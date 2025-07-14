from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import importlib
import os
import types
import sys
from src.services.service import ServiceABC

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MenuNode(ABC):
    """Abstract base class for all menu nodes with optimized initialization and request handling"""
    __slots__ = ('node_id', 'config', 'validation_error', 'next_nodes', 'engine', 'msisdn', 
                 '_service_class', '_service', 'request_timeout')

    # Shared requests Session for connection pooling and Keep-Alive
    _session = requests.Session()
    _retry_strategy = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    _adapter = HTTPAdapter(
        max_retries=_retry_strategy,
        pool_connections=10,
        pool_maxsize=10
    )
    _session.mount("http://", _adapter)
    _session.mount("https://", _adapter)
    _session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Python-Requests/2.32.3",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive"
    })

    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.validation_error = ""
        self.next_nodes: Dict[str, str] = {}
        self.engine: Optional['MenuEngine'] = None
        self.msisdn: Optional[str] = None
        self._service_class = self._resolve_service_class(config)
        self._service = None  # Lazy-loaded
        self.request_timeout = None if isinstance(config, str) else config.get("request_timeout", 5.0)

    def _resolve_service_class(self, config: Dict[str, Any]) -> Optional[type]:
        """Resolve service class without instantiation for lazy loading"""
        path = config if isinstance(config, str) else config.get('validation_url', '') or config.get('action_url', '')
        if path and not path.startswith("http"):
            try:
                module_path, class_name = path.rsplit(".", 1)
                # Try to import the module first
                try:
                    module = importlib.import_module(module_path)
                    logger.info(f"Successfully imported existing module: {module_path}")
                except ImportError:
                    # Module doesn't exist, create it physically and dynamically
                    logger.info(f"Module {module_path} not found, creating in project directory...")
                    should_extend_service_abc = self._should_extend_service_abc(class_name, path)
                    self._create_physical_files(module_path, class_name, should_extend_service_abc)
                    module = self._create_dynamic_module(module_path)
                
                # Try to get the class from the module
                try:
                    klass = getattr(module, class_name)
                    logger.info(f"Found existing class {class_name} in module {module_path}")
                except AttributeError:
                    # Class doesn't exist, create it physically and dynamically
                    logger.info(f"Class {class_name} not found in module {module_path}, creating in project directory...")
                    should_extend_service_abc = self._should_extend_service_abc(class_name, path)
                    self._create_physical_files(module_path, class_name, should_extend_service_abc)
                    klass = self._create_dynamic_service_class(module, class_name, path)
                
                # Validate the class (if it extends ServiceABC)
                if hasattr(klass, '__bases__') and any(base.__name__ == 'ServiceABC' for base in klass.__mro__):
                    if not isinstance(klass, type) or not issubclass(klass, ServiceABC):
                        logger.error(f"Invalid service class {class_name} at {path}")
                        return None
                
                logger.info(f"Resolved service {class_name} for node {self.node_id}")
                return klass
                
            except (ValueError, ImportError, AttributeError) as e:
                logger.error(f"Failed to resolve service {path} for node {self.node_id}: {str(e)}")
                print(f'FAILED loading {path} in the node {type(self).__name__}')
                raise TypeError(f"Failed to resolve service {path} for node {self.node_id}: {str(e)}")
        
        return None

    def _create_dynamic_module(self, module_path: str):
        """Create a dynamic module at the specified path - IN MEMORY ONLY"""
        # Create the module object in memory
        module = types.ModuleType(module_path)
        module.__file__ = f"<dynamic:{module_path}>"  # Virtual file path
        module.__loader__ = None
        module.__package__ = '.'.join(module_path.split('.')[:-1]) if '.' in module_path else None
        
        # Add to sys.modules dictionary (Python's module cache in memory)
        sys.modules[module_path] = module
        
        # Create parent modules if they don't exist (also in memory only)
        parts = module_path.split('.')
        for i in range(len(parts) - 1):
            parent_path = '.'.join(parts[:i+1])
            if parent_path not in sys.modules:
                parent_module = types.ModuleType(parent_path)
                parent_module.__file__ = f"<dynamic:{parent_path}>"
                parent_module.__loader__ = None
                parent_module.__package__ = '.'.join(parts[:i]) if i > 0 else None
                sys.modules[parent_path] = parent_module
        
        logger.info(f"Created dynamic module IN MEMORY: {module_path}")
        return module

    def _create_dynamic_service_class(self, module, class_name: str, full_path: str):
        """Create a dynamic service class in the given module - IN MEMORY AND ON DISK"""
        should_extend_service_abc = self._should_extend_service_abc(class_name, full_path)
        
        if should_extend_service_abc:
            class_dict = {
                '__module__': module.__name__,
                '__qualname__': class_name,
                'getUrl': lambda self, *args, **kwargs: f"{self.baseurl}api/{class_name.lower()}",
                'getPayload': lambda self, *args, **kwargs: {
                    "service": class_name,
                    "timestamp": __import__('time').time(),
                    "source": "dynamic_service"
                },
                'parseResponse': lambda self, response_data: response_data,
            }
            try:
                from src.services.ServiceABC import ServiceABC
                dynamic_class = type(class_name, (ServiceABC,), class_dict)
            except ImportError:
                logger.warning(f"ServiceABC not available, creating basic class for {class_name}")
                dynamic_class = type(class_name, (object,), class_dict)
        else:
            class_dict = {
                '__module__': module.__name__,
                '__qualname__': class_name,
                '__init__': lambda self: None,
                'process': lambda self, *args, **kwargs: f"Processing in {class_name}",
                'execute': lambda self, *args, **kwargs: f"Executing {class_name}",
                'validate': lambda self, data: True,
                'handle': lambda self, request: {"status": "handled", "handler": class_name},
            }
            dynamic_class = type(class_name, (object,), class_dict)
        
        setattr(module, class_name, dynamic_class)
        logger.info(f"Created dynamic class IN MEMORY: {class_name} in module {module.__name__}")
        return dynamic_class

    def _should_extend_service_abc(self, class_name: str, full_path: str) -> bool:
        """Determine if a class should extend ServiceABC based on naming conventions"""
        return (
            'service' in class_name.lower() or 
            'service' in full_path.lower() or
            class_name.endswith('Service')
        )

    def _create_physical_files(self, module_path: str, class_name: str, should_extend_service_abc: bool = True):
        """Create actual .py files on disk in the current project directory"""
        # Get current working directory (your VS Code project root)
        project_root = os.getcwd()
        print(f"Creating files in project directory: {project_root}")
        
        # Convert module path to file path
        file_path = os.path.join(project_root, module_path.replace('.', os.sep) + '.py')
        dir_path = os.path.dirname(file_path)
        
        # Create directory structure for the module
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"Created directory: {dir_path}")
        
        # Create __init__.py files for proper Python package structure
        parts = module_path.split('.')
        for i in range(len(parts)):
            init_dir = os.path.join(project_root, *parts[:i+1])
            os.makedirs(init_dir, exist_ok=True)  # Ensure directory exists
            init_path = os.path.join(init_dir, '__init__.py')
            if not os.path.exists(init_path):
                with open(init_path, 'w') as f:
                    f.write('# Auto-generated __init__.py\n')
                print(f"Created: {init_path}")
        
        # Only create the file if it doesn't already exist
        if not os.path.exists(file_path):
            # Generate the class code
            if should_extend_service_abc:
                class_code = f'''"""
    Auto-generated service class: {class_name}
    Generated at: {os.path.abspath(file_path)}
"""
from typing import Dict, Any
from abc import ABC, abstractmethod

try:
    from src.services.ServiceABC import ServiceABC
except ImportError:
    # Fallback: create a basic ABC if ServiceABC not found
    class ServiceABC(ABC):
        def __init__(self):
            self.baseurl = "http://localhost:8080/"
            self.validation_error = ""
        
        @abstractmethod
        def getUrl(self, *args, **kwargs) -> str:
            pass
        
        @abstractmethod
        def getPayload(self, *args, **kwargs) -> Dict:
            pass
        
        @abstractmethod
        def parseResponse(self, response_data: Any) -> Any:
            pass

class {class_name}(ServiceABC):
    """Auto-generated service class"""
    
    def __init__(self):
        super().__init__()
    
    def getUrl(self, *args, **kwargs) -> str:
        """Return the URL for the API request."""
        return f"{{self.baseurl}}api/{class_name.lower()}"
    
    def getPayload(self, *args, **kwargs) -> Dict:
        """Create the JSON payload for the API request."""
        return {{
            "service": "{class_name}",
            "timestamp": __import__('time').time(),
            "source": "auto_generated"
        }}
    
    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the API request."""
        return response_data
'''
            else:
                class_code = f'''"""
    Auto-generated class: {class_name}
    Generated at: {os.path.abspath(file_path)}
"""
from typing import Any, Dict

class {class_name}:
    """Auto-generated class"""
    
    def __init__(self):
        pass
    
    def process(self, *args, **kwargs) -> str:
        """Process method for {class_name}"""
        return f"Processing in {class_name}"
    
    def execute(self, *args, **kwargs) -> str:
        """Execute method for {class_name}"""
        return f"Executing {class_name}"
    
    def validate(self, data: Any) -> bool:
        """Validate method for {class_name}"""
        return True
    
    def handle(self, request: Dict) -> Dict:
        """Handle method for {class_name}"""
        return {{"status": "handled", "handler": "{class_name}"}}
'''
            
            # Write the file
            with open(file_path, 'w') as f:
                f.write(class_code)
            
            print(f"✓ Created physical file: {file_path}")
        else:
            print(f"File already exists: {file_path}")
        
        return file_path

    @property
    def service(self) -> Optional[ServiceABC]:
        """Lazy service initialization"""
        if self._service is None and self._service_class:
            self._service = self._service_class()
        return self._service

    def reset_state(self, msisdn: str):
        """Reset all stateful properties for a new session"""
        self.msisdn = msisdn
        self.validation_error = ""
        self._service = None  # Reset service instance for lazy loading

    def add_transition(self, condition: str, target_node_id: str):
        """Add transition to another node"""
        self.next_nodes[condition] = target_node_id

    def set_engine(self, engine: 'MenuEngine'):
        """Set reference to engine for node transitions"""
        self.engine = engine

    def make_post_request(self, payload: Dict) -> Any:
        """Delegate HTTP POST request to the service instance with optimized settings"""
        if not self.service:
            logger.error(f"No service configured for node {self.node_id}")
            return None
        format_context = {**self.bundle_details, **self.inputs, 'msisdn': self.msisdn}
        payload = payload|  {           
                                **self.inputs,
                                **{k: v.format(**format_context) if isinstance(v, str) else v 
                                for k, v in self.config.get("params", {}).items()}
        }
        try:
            return self.service.doPost(payload, msisdn=self.msisdn)
        except requests.RequestException as e:
            logger.error(f"POST request failed for node {self.node_id}: {str(e)}")
            self.validation_error = f"Request failed: {str(e)}"
            return None

    @abstractmethod
    def getNext(self) -> str:
        """Get the next prompt or response based on the node's state"""
        pass

    def getPrevious(self) -> str:
        """Return the prompt of the previous node or a fallback message."""
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            previous_node = self.engine.nodes.get(previous_node_id)
            if previous_node:
                return previous_node.getNext()
        return "No previous menu\nPress 0 to exit"

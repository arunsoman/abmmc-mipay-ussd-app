from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import importlib
from src.menu.graph.nodes.global_share import service_config
from src.services.service import ServiceABC


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from src.services.ValidationApi import Validate


class MenuNode(ABC):
    """Abstract base class for all menu nodes with renderer logic and optimized HTTP request handling."""
    service : ServiceABC
    # Shared requests Session for connection pooling and Keep-Alive
    _session = requests.Session()
    
    # Configure retries for transient failures
    _retry_strategy = Retry(
        total=3,
        backoff_factor=0.1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    _adapter = HTTPAdapter(
        max_retries=_retry_strategy,
        pool_connections=10,  # Max connections to keep in pool
        pool_maxsize=10       # Max concurrent connections
    )
    _session.mount("http://", _adapter)
    _session.mount("https://", _adapter)
    
    # Configure default headers with compression
    _session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "Python-Requests/2.32.3",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",  # Enable compression
        "Connection": "keep-alive"          # Explicitly enable Keep-Alive
    })

    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.validation_error = ""
        self.next_nodes: Dict[str, str] = {}  # Key: condition, Value: node_id
        self.engine: Optional['MenuEngine'] = None
        self.msisdn = config.get("msisdn", "")
        self.service = {}
        # Initialize service
        self.service = None


        
        path = self.config.get('validation_url', '') or self.config.get('action_url', '')
        if path and not path.startswith("http"):
            logger.info(f"Loading service from path: {path}")
            try:
                # Split path to get module and class
                if '.' not in path:
                    raise ValueError(f"Invalid service path {path}: must include module and class name (e.g., module.class)")
                module_path, class_name = path.rsplit(".", 1)
                logger.debug(f"Module path: {module_path}, Class name: {class_name}")
                module = importlib.import_module(module_path)
                klass = getattr(module, class_name)
                # Check if klass is a class
                if not isinstance(klass, type):
                    raise ValueError(f"Expected a class at {path}, got {type(klass).__name__} instead")
                # Check if klass inherits from ServiceABC
                if not issubclass(klass, ServiceABC):
                    raise ValueError(f"Service class {class_name} at {path} must inherit from ServiceABC")
                self.service = klass()  # Instantiate the service class
                logger.info(f"Service {class_name} loaded successfully for node {node_id}")
            except (ValueError, ImportError, AttributeError) as e:
                logger.error(f"Failed to load service from path {path} for node {node_id}: {str(e)}")
                raise ValueError(f"Invalid service configuration for node {node_id}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error loading service from path {path} for node {node_id}: {str(e)}")
                raise ValueError(f"Unexpected error in service configuration for node {node_id}: {str(e)}")
        else:
            logger.info(f"No valid service path provided for node {node_id}, proceeding without service")




        # Configurable timeout from node config, default to 5 seconds
        self.request_timeout = config.get("request_timeout", 5.0)


    def add_transition(self, condition: str, target_node_id: str):
        """Add transition to another node."""
        self.next_nodes[condition] = target_node_id
    
    def set_engine(self, engine: 'MenuEngine'):
        """Set reference to engine for node transitions."""
        self.engine = engine
    
    def make_post_request(self, payLoad: Dict) -> Any:
        """Delegate HTTP POST request to the service instance."""
        return self.service.doPost(payLoad=payLoad) 
    
    def parseResponse(self, response_data: Any) -> Any:
       return self.service.parseResponse(response_data)
    
    @abstractmethod
    def getNext(self) -> str:
        """Get the next prompt or response based on the node's state."""
        pass
    
    @abstractmethod
    def getPrevious(self) -> str:
        """Get the prompt of the previous node or a fallback message."""
        pass
    
    @abstractmethod
    def handleUserInput(self, user_input: str) -> str:
        """Process user input, update state, and return the next prompt or response."""
        pass
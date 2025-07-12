from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import importlib
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
        self.msisdn = config.get("msisdn", "")
        self._service_class = self._resolve_service_class(config)
        self._service = None  # Lazy-loaded
        self.request_timeout = config.get("request_timeout", 5.0)

    def _resolve_service_class(self, config: Dict[str, Any]) -> Optional[type]:
        """Resolve service class without instantiation for lazy loading"""
        path = config.get('validation_url', '') or config.get('action_url', '')
        if path and not path.startswith("http"):
            try:
                module_path, class_name = path.rsplit(".", 1)
                module = importlib.import_module(module_path)
                klass = getattr(module, class_name)
                if not isinstance(klass, type) or not issubclass(klass, ServiceABC):
                    logger.error(f"Invalid service class {class_name} at {path}")
                    return None
                logger.info(f"Resolved service {class_name} for node {self.node_id}")
                return klass
            except (ValueError, ImportError, AttributeError) as e:
                logger.error(f"Failed to resolve service {path} for node {self.node_id}: {str(e)}")
                return None
        return None

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

    @abstractmethod
    def getPrevious(self) -> str:
        """Get the prompt of the previous node or a fallback message"""
        pass

    @abstractmethod
    def handleUserInput(self, user_input: str) -> str:
        """Process user input, update state, and return the next prompt or response"""
        pass
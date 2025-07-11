from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
from src.menu.graph.nodes.global_share import service_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MenuNode(ABC):
    """Abstract base class for all menu nodes with renderer logic and optimized HTTP request handling."""
    
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
        # Configurable timeout from node config, default to 5 seconds
        self.request_timeout = config.get("request_timeout", 5.0)

    def add_transition(self, condition: str, target_node_id: str):
        """Add transition to another node."""
        self.next_nodes[condition] = target_node_id
    
    def set_engine(self, engine: 'MenuEngine'):
        """Set reference to engine for node transitions."""
        self.engine = engine
    
    def make_post_request(
        self,
        url: str,
        payload: Dict[str, Any],
        extra_headers: Optional[Dict[str, str]] = None,
        stream: bool = False
    ) -> Any:
        """
        Centralized method to make POST requests with optimized performance.
        
        Args:
            url: The target URL for the POST request.
            payload: The JSON payload to send.
            extra_headers: Additional headers to include (e.g., Authorization).
            stream: Whether to stream the response (for large responses).
        
        Returns:
            Parsed response data as defined by the subclass's parseResponse method,
            or None if the request fails.
        """
        headers = {}
        if self.msisdn in service_config and "auth_token" in service_config[self.msisdn]:
            headers["Authorization"] = f"Bearer {service_config[self.msisdn]['auth_token']}"
        if extra_headers:
            headers.update(extra_headers)
        
        logger.debug(f"Making POST request to {url} with payload {payload}")
        try:
            response = self._session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.request_timeout,
                stream=stream
            )
            response.raise_for_status()
            response_data = response.json() if not stream else response.iter_content(chunk_size=8192)
            logger.debug(f"Received response from {url}: {response_data if not stream else 'streamed'}")
            return self.parseResponse(response_data)
        except requests.RequestException as e:
            self.validation_error = f"Request failed: {str(e)}"
            logger.error(f"Request to {url} failed: {str(e)}")
            return None
    
    def parseResponse(self, response_data: Any) -> Any:
        """
        Default implementation for parsing response data. Subclasses should override
        for specific response handling. Returns None for nodes that don't make network calls.
        
        Args:
            response_data: The raw response data (JSON or streamed content).
        
        Returns:
            None for nodes that don't handle network responses.
        """
        return None
    
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
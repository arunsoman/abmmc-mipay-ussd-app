from abc import ABC, abstractmethod
from typing import Any, Dict
import  requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .TokenManager import TokenManager

class ServiceTransactionRecord:
    """Python equivalent of Java ServiceTransactionRecord with slots."""
    __slots__ = ('initiator', 'service_provider', 'service_receiver', 'context')

    def __init__(self, initiator: str, service_provider: str, 
                 service_receiver: str, context: Dict[str, Any]):
        self.initiator = initiator
        self.service_provider = service_provider
        self.service_receiver = service_receiver
        self.context = context
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "initiator": self.initiator,
            "serviceProvider": self.service_provider,
            "serviceReceiver": self.service_receiver,
            "context": self.context
        }
    
class ServiceABC(ABC):
    _session = requests.Session()
    _request_timeout = 20
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
    

    def doPost (self, payLoad: Dict, msisdn: str)->Any:
        

        headers = dict(ServiceABC._session.headers)|{"Authorization" : f"Bearer {TokenManager.get_token(msisdn)}"}

        
        response = self._session.post(
                self.getUrl(),
                json=payLoad|self.getPayload(),
                headers=headers,
                timeout=ServiceABC._request_timeout,
                
            )
        return  self.parseResponse(response.json())

    """Abstract base class for API services."""
    def __init__(self):
        self.baseurl = "http://localhost:8080/"  # Placeholder base URL
        self.validation_error = ""
        

    @abstractmethod
    def getUrl(self, *args, **kwargs) -> str:
        """Return the URL for the API request."""
        pass

    @abstractmethod
    def getPayload(self, *args, **kwargs) -> Dict:
        """Create the JSON payload for the API request."""
        pass

    @abstractmethod
    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the API request."""
        pass 
"""
    Auto-generated service class: BalanceAPI
    Generated at: C:\Users\arun\Documents\ussdgw\src\services\CkeckBalanceAPI.py
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

class BalanceAPI(ServiceABC):
    """Auto-generated service class"""
    
    def __init__(self):
        super().__init__()
    
    def getUrl(self, *args, **kwargs) -> str:
        """Return the URL for the API request."""
        return f"{self.baseurl}api/balanceapi"
    
    def getPayload(self, *args, **kwargs) -> Dict:
        """Create the JSON payload for the API request."""
        return {
            "service": "BalanceAPI",
            "timestamp": __import__('time').time(),
            "source": "auto_generated"
        }
    
    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the API request."""
        return response_data

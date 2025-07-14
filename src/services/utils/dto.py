import json
from typing import Dict, Any, Optional, List
from threading import Lock

class ServiceTransactionRecord:
    """Python equivalent of Java ServiceTransactionRecord with slots and object pooling."""
    __slots__ = ('initiator', 'service_provider', 'service_receiver', 'context', '_in_use')
    
    def __init__(self, initiator: str, service_provider: str, 
                 service_receiver: str, context: Dict[str, Any]):
        self.initiator = initiator
        self.service_provider = service_provider
        self.service_receiver = service_receiver
        self.context = context
        self._in_use = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initiator": self.initiator,
            "serviceProvider": self.service_provider,
            "serviceReceiver": self.service_receiver,
            "context": self.context
        }




class BaseResponse:
    """Python equivalent of Java BaseResponse<T> with slots for memory efficiency."""
    __slots__ = ('response_code', 'error', 'data')

    def __init__(self, response_code: int = 0, error: Optional[str] = None, data: Any = None):
        self.response_code = response_code
        self.error = error
        self.data = data
    
    def __repr__(self):
        return f"BaseResponse(response_code={self.response_code}, error={self.error}, data={self.data})"
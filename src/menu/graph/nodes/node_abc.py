from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class MenuNode(ABC):
    """Abstract base class for all menu nodes with renderer logic."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.validation_error = ""
        self.next_nodes: Dict[str, str] = {}  # Key: condition, Value: node_id
        self.engine: Optional['MenuEngine'] 
        self.msisdn = config.get("msisdn", "")

    def add_transition(self, condition: str, target_node_id: str):
        """Add transition to another node."""
        self.next_nodes[condition] = target_node_id
    
    def set_engine(self, engine: 'MenuEngine'):
        """Set reference to engine for node transitions."""
        self.engine = engine
    
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
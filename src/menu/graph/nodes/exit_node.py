from typing import Any, Dict
from src.menu.graph.menu_state_management import MenuSessionManager
from src.menu.graph.nodes.node_abc import MenuNode

class ExitNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)

    """Node to terminate the session."""
    def getNext(self) -> str:
        MenuSessionManager.store_token(self.msisdn, "")
        return self.config.get("prompt", "Session ended")
    
    def getPrevious(self) -> str:
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            previous_node = self.engine.nodes.get(previous_node_id)
            if previous_node:
                return previous_node.getNext()
        return "No previous menu"
    
    def handleUserInput(self, user_input: str) -> str:
        MenuSessionManager.store_token(self.msisdn, "") 
        if self.engine:
            self.engine.session_active = False
        return "Session ended"

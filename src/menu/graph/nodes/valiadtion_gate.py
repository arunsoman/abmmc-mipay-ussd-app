from typing import Dict, Any
from src.menu.graph.nodes.node_abc import MenuNode
from src.menu.graph.nodes.global_share import service_config

class ValidationGateNode(MenuNode):
    """Root node for PIN authentication before accessing services."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.max_attempts = config.get("max_attempts", 3)
        self.current_attempts = 0
        self.valid_pin = config.get("valid_pin", "123456")
        self.validation_url = config.get("validation_url")
        self.prompt = config.get("prompt", "Enter your PIN:\n")
        self.service = None  # Mock or actual AuthService

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the POST request."""
        if response_data and isinstance(response_data, dict):
            if response_data.get("status"):
                return {
                    "status": response_data.get("status"),
                    "auth_token": response_data.get("auth_token", "mock_token")
                }
            self.validation_error = f"Validation failed: {response_data.get('error', 'Invalid PIN')}"
        else:
            self.validation_error = "Validation failed: Invalid response"
        return None

    def getNext(self) -> str:
        """Return the PIN prompt with validation error if any."""
        error_msg = f"\n{self.validation_error}" if self.validation_error else ""
        return f"{self.prompt}{error_msg}"

    def getPrevious(self) -> str:
        """No previous node for root; return fallback message."""
        return "No previous menu\nPress 0 to exit"

    def handleUserInput(self, user_input: str) -> str:
        """Validate PIN and transition to success or failure node."""
        self.current_attempts += 1
        self.validation_error = ""

        if self.validation_url:
            payload = {"password": user_input, "phone": self.msisdn}
            response_data = self.make_post_request(self.validation_url, payload)
            if response_data:
                service_config[self.msisdn] = {
                    "msisdn": self.msisdn,
                    "auth_token": response_data.get("auth_token")
                }
                target_node_id = self.next_nodes.get("success")
                if target_node_id and self.engine:
                    self.engine.navigation_stack.append(self.node_id)
                    self.engine.set_current_node(target_node_id)
                    return self.engine.get_current_prompt()
                return self.getNext()
            else:
                self.validation_error = self.validation_error or "Validation failed: Unknown error"
        else:
            if user_input == self.valid_pin:
                service_config[self.msisdn] = {
                    "msisdn": self.msisdn,
                    "auth_token": "mock_token"
                }
                target_node_id = self.next_nodes.get("success")
                if target_node_id and self.engine:
                    self.engine.navigation_stack.append(self.node_id)
                    self.engine.set_current_node(target_node_id)
                    return self.engine.get_current_prompt()
            else:
                self.validation_error = "Invalid PIN"

        if self.current_attempts >= self.max_attempts:
            target_node_id = self.next_nodes.get("failure", "exit_node")
            if target_node_id and self.engine:
                self.engine.navigation_stack.append(self.node_id)
                self.engine.set_current_node(target_node_id)
                return self.engine.get_current_prompt()

        return self.getNext()
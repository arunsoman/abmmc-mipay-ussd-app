from typing import Dict, Any
import requests
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
            try:
                payload = {"password": user_input, "phone": self.msisdn}
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Python-Requests/2.32.3"
                }
                response = requests.post(self.validation_url, json=payload, headers=headers, timeout=5)
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get("status"):
                        token = response.headers.get("Authorization")
                        service_config[self.msisdn] = {
                            "msisdn": self.msisdn,
                            "auth_token": token
                        }
                        target_node_id = self.next_nodes.get("success")
                        if target_node_id and self.engine:
                            self.engine.navigation_stack.append(self.node_id)
                            self.engine.set_current_node(target_node_id)
                            return self.engine.get_current_prompt()
                    else:
                        self.validation_error = f"Validation failed: {response_data.get('error', 'Invalid PIN')}"
                else:
                    self.validation_error = f"Validation failed: Server returned {response.status_code}"
            except requests.RequestException as e:
                self.validation_error = f"Validation error: {str(e)}"
        else:
            # Mock validation
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
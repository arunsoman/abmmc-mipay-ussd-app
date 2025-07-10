from typing import Dict, Any
import requests
from src.menu.graph.nodes.node_abc import MenuNode
from src.menu.graph.nodes.global_share import service_config

class Msisdn_Node(MenuNode):
    """Node to send a POST request with cached data and display the response."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.prompt = config.get("prompt", "Response: {response}\nPress 9 to go back, 0 to exit")
        self.cache_params = config.get("cache_params", {})
        self.action_url = config.get("action_url")
        self.valid_keys = {"9", "0"}
        self.state = "initial"  # initial -> complete
        self.response_data = None

    def getNext(self) -> str:
        """Generate the prompt with the server response or error."""
        if self.state == "initial":
            # Build payload from cache
            cached_data = service_config.get(self.msisdn, {})
            payload = {display_name: cached_data.get(cache_key, "N/A") 
                       for cache_key, display_name in self.cache_params.items()}
            try:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Python-Requests/2.32.3"
                }
                if self.msisdn in service_config and "auth_token" in service_config[self.msisdn]:
                    headers["Authorization"] = f"Bearer {service_config[self.msisdn]['auth_token']}"
                response = requests.post(self.action_url, json=payload, headers=headers, timeout=5)
                response.raise_for_status()
                self.response_data = response.json()
                self.state = "complete"
                formatted_response = self.prompt.format(response=str(self.response_data))
            except (requests.RequestException, KeyError, ValueError) as e:
                self.validation_error = f"Request failed: {str(e)}"
                self.state = "complete"
                formatted_response = self.validation_error
            error_msg = f"\n{self.validation_error}" if self.validation_error else ""
            return f"{formatted_response}{error_msg}"
        elif self.state == "complete":
            formatted_response = self.prompt.format(response=str(self.response_data)) if self.response_data else self.validation_error
            error_msg = f"\n{self.validation_error}" if self.validation_error else ""
            return f"{formatted_response}{error_msg}"
        return "Service unavailable"

    def getPrevious(self) -> str:
        """Return the prompt of the previous node or a fallback message."""
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            previous_node = self.engine.nodes.get(previous_node_id)
            if previous_node:
                return previous_node.getNext()
        return "No previous menu\nPress 0 to exit"

    def handleUserInput(self, user_input: str) -> str:
        """Process user input and transition to the selected node."""
        self.validation_error = ""

        if user_input in self.valid_keys:
            if user_input == "9":
                if self.engine and self.engine.navigation_stack:
                    target_node_id = self.engine.navigation_stack.pop()
                    self.engine.set_current_node(target_node_id)
                    self.state = "initial"
                    self.response_data = None
                    return self.engine.get_current_prompt()
                return "No previous menu\nPress 0 to exit"
            elif user_input == "0":
                if self.engine:
                    self.engine.set_current_node("exit_node")
                    self.state = "initial"
                    self.response_data = None
                    return self.engine.get_current_prompt()
                return "Session ended"
        else:
            self.validation_error = f"Invalid selection. Choose from {', '.join(sorted(self.valid_keys))}"

        return self.getNext()
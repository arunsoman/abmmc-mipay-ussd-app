from typing import Dict, Any, Optional
import re
from src.menu.graph.nodes.node_abc import MenuNode
from src.menu.graph.nodes.global_share import service_config

class SingleInputActionNode(MenuNode):
    """Node for actions requiring a single user input, e.g., balance check."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.state = "input"  # input -> confirm -> complete
        self.input: Any = None  # Store single input
        self.input_key = config.get("input_key")
        self.prompt = config.get("prompt", "")
        self.validation = config.get("validation", {})
        self.confirmation_prompt = config.get("confirmation_prompt", "")
        self.action_url = config.get("action_url")
        self.params = config.get("params", {})
        self.success_prompt = config.get("success_prompt", "Action completed\nStatus: {status}\nPress 9 to go back, 0 to exit")

    def parseResponse(self, response_data: Any) -> Any:
        """Parse the JSON response from the POST request."""
        if response_data and isinstance(response_data, dict):
            if response_data.get("status"):
                return response_data
            self.validation_error = f"Action failed: {response_data.get('error', 'Unknown error')}"
        else:
            self.validation_error = "Action failed: Invalid response"
        return None

    def getNext(self) -> str:
        """Generate the next prompt based on the current state."""
        if self.state == "input":
            error_msg = f"\n{self.validation_error}" if self.validation_error else ""
            return f"{self.prompt}{error_msg}"
        elif self.state == "confirm":
            prompt = self.confirmation_prompt
            prompt = prompt.replace(f"{{{self.input_key}}}", str(self.input))
            return f"{prompt}\n"
        elif self.state == "complete":
            return f"{self.success_prompt}\nPress 9 to go back, 0 to exit"
        return "Service unavailable"

    def getPrevious(self) -> str:
        """Return the prompt of the previous node or a fallback message."""
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            previous_node = self.engine.nodes.get(previous_node_id)
            if previous_node:
                return previous_node.getNext()
        return "No previous menu\nPress 9 to go back, 0 to exit"

    def validate(self, user_input: str) -> str:
        """Validate user input based on the current state."""
        self.validation_error = ""
        
        if self.state == "input":
            if self.validation.get("type") == "numeric":
                try:
                    value = float(user_input)
                    if "min" in self.validation and value < self.validation["min"]:
                        self.validation_error = f"Value must be at least {self.validation['min']}"
                        return ""
                    if "max" in self.validation and value > self.validation["max"]:
                        self.validation_error = f"Value must not exceed {self.validation['max']}"
                        return ""
                    self.input = value
                    return "valid"
                except ValueError:
                    self.validation_error = "Invalid numeric input"
                    return ""
            elif "regex" in self.validation:
                if re.match(self.validation["regex"], user_input):
                    self.input = user_input
                    return "valid"
                self.validation_error = "Invalid input format"
                return ""
            elif "options" in self.validation:
                try:
                    choice = int(user_input)
                    options = self.validation.get("options", [])
                    if 1 <= choice <= len(options):
                        self.input = options[choice - 1]
                        return "valid"
                    self.validation_error = f"Invalid selection. Choose 1-{len(options)}"
                    return ""
                except ValueError:
                    self.validation_error = "Invalid selection"
                    return ""
            else:
                self.input = user_input
                return "valid"
        
        elif self.state == "confirm":
            if user_input in ["1", "2"]:
                return user_input
            self.validation_error = "Please select 1 or 2"
            return ""
        
        elif self.state == "complete":
            if user_input in ["9", "0"] or user_input in self.next_nodes:
                return user_input
            self.validation_error = "Invalid option. Press 9 to go back, 0 to exit"
            return "0"  # Default to exit on invalid input
        
        return ""

    def handleUserInput(self, user_input: str) -> str:
        """Process user input, update state, and return the next prompt."""
        validation_result = self.validate(user_input)
        
        if self.state == "input" and validation_result == "valid":
            self.state = "confirm"
            return self.getNext()
        
        elif self.state == "confirm":
            if validation_result == "1":
                self.state = "complete"
                if self.action_url:
                    payload = {
                        "msisdn": self.msisdn,
                        self.input_key: self.input,
                        **self.params
                    }
                    for key, value in payload.items():
                        if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                            param_key = value[1:-1]
                            payload[key] = self.input if param_key == self.input_key else value
                    
                    response_data = self.make_post_request(self.action_url, payload)
                    if response_data:
                        self.success_prompt = self.success_prompt.format(**response_data)
                        return f"{self.success_prompt}\nPress 9 to go back, 0 to exit"
                    else:
                        self.state = "complete"
                        return f"{self.validation_error}\nPress 9 to go back, 0 to exit"
                return f"{self.success_prompt}\nPress 9 to go back, 0 to exit"
            elif validation_result == "2":
                if self.engine:
                    self.engine.set_current_node("exit_node")
                    return self.engine.get_current_prompt()
                return "Session ended"
        
        elif self.state == "complete":
            if validation_result == "9":
                if self.engine and self.engine.navigation_stack:
                    target_node_id = self.engine.navigation_stack.pop()
                    self.engine.set_current_node(target_node_id)
                    self.state = "input"
                    self.input = None
                    return self.engine.get_current_prompt()
                return "No previous menu\nPress 9 to go back, 0 to exit"
            elif validation_result == "0" or validation_result == "":
                if self.engine:
                    self.engine.set_current_node("exit_node")
                    self.state = "input"
                    self.input = None
                    return self.engine.get_current_prompt()
                return "Session ended"
            elif validation_result in self.next_nodes:
                target_node_id = self.next_nodes[validation_result]
                if self.engine and self.engine.current_node_id:
                    self.engine.navigation_stack.append(self.engine.current_node_id)
                    self.engine.set_current_node(target_node_id)
                    self.state = "input"
                    self.input = None
                    return self.engine.get_current_prompt()
        
        return self.getNext()
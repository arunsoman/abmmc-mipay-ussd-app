from typing import Dict, Any, List
from src.menu.graph.nodes.node_abc import MenuNode
import re
import requests
from src.menu.graph.nodes.global_share import service_config

class MultiInputActionNode(MenuNode):
    """Node for multi-step input collection, e.g., wallet-to-wallet transfer."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.state = "input"  # input -> confirm -> complete
        self.current_step = 0
        self.inputs: Dict[str, Any] = {}  # Store inputs by input_key
        self.steps: List[Dict[str, Any]] = config.get("steps", [])
        self.confirmation_prompt = config.get("confirmation_prompt", "")
        self.action_url = config.get("action_url")
        self.params = config.get("params", {})
        self.success_prompt = config.get("success_prompt", "Action completed\nStatus: {status}\nPress 9 to go back, 0 to exit")

    def getNext(self) -> str:
        """Generate the next prompt based on the current state."""
        if self.state == "input" and self.current_step < len(self.steps):
            step_config = self.steps[self.current_step]
            prompt = step_config["prompt"]
            error_msg = f"\n{self.validation_error}" if self.validation_error else ""
            return f"{prompt}{error_msg}"
        elif self.state == "confirm":
            prompt = self.confirmation_prompt
            for key, value in self.inputs.items():
                if isinstance(value, dict):
                    prompt = prompt.replace(f"{{{key}}}", str(value.get("name", value)))
                else:
                    prompt = prompt.replace(f"{{{key}}}", str(value))
            return f"{prompt}\n1: OK, 2: Cancel"
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
        """Validate user input based on the current state and step."""
        self.validation_error = ""
        
        if self.state == "input" and self.current_step < len(self.steps):
            step_config = self.steps[self.current_step]
            validation = step_config.get("validation", {})
            input_key = step_config["input_key"]
            
            if validation.get("type") == "numeric":
                try:
                    value = float(user_input)
                    if "min" in validation and value < validation["min"]:
                        self.validation_error = f"Value must be at least {validation['min']}"
                        return ""
                    if "max" in validation and value > validation["max"]:
                        self.validation_error = f"Value must not exceed {validation['max']}"
                        return ""
                    self.inputs[input_key] = value
                    return "valid"
                except ValueError:
                    self.validation_error = "Invalid numeric input"
                    return ""
            elif "regex" in validation:
                if re.match(validation["regex"], user_input):
                    self.inputs[input_key] = user_input
                    # For change_pin, ensure confirm_pin matches new_pin
                    if self.node_id == "change_pin" and input_key == "confirm_pin":
                        if self.inputs.get("new_pin") != user_input:
                            self.validation_error = "Confirmation PIN does not match new PIN"
                            return ""
                    return "valid"
                self.validation_error = "Invalid input format"
                return ""
            elif "options" in validation:
                try:
                    choice = int(user_input) - 1
                    options = validation.get("options", [])
                    if 0 <= choice < len(options):
                        self.inputs[input_key] = options[choice]
                        return "valid"
                    self.validation_error = f"Invalid selection. Choose 1-{len(options)}"
                    return ""
                except ValueError:
                    self.validation_error = "Invalid selection"
                    return ""
            else:
                self.inputs[input_key] = user_input
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
        print(f"DEBUG: state={self.state}, current_step={self.current_step}, input={user_input}")  # Debug
        validation_result = self.validate(user_input)
        
        if self.state == "input" and validation_result == "valid":
            self.current_step += 1
            if self.current_step >= len(self.steps):
                self.state = "confirm"
            return self.getNext()
        
        elif self.state == "confirm":
            if validation_result == "1":
                self.state = "complete"
                if self.action_url:
                    payload = {
                        "msisdn": self.msisdn,
                        **{k: v["id"] if isinstance(v, dict) else v for k, v in self.inputs.items()},
                        **self.params
                    }
                    for key, value in payload.items():
                        if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                            param_key = value[1:-1]
                            payload[key] = self.inputs.get(param_key, value)
                    
                    try:
                        headers = {
                            "Content-Type": "application/json",
                            "User-Agent": "Python-Requests/2.32.3"
                        }
                        if self.msisdn in service_config:
                            headers["Authorization"] = f"Bearer {service_config[self.msisdn].get('auth_token')}"
                        response = requests.post(self.action_url, json=payload, headers=headers, timeout=5)
                        response_data = response.json()
                        if response_data.get("status"):
                            self.success_prompt = self.success_prompt.format(**response_data)
                            return f"{self.success_prompt}\nPress 9 to go back, 0 to exit"
                        else:
                            self.validation_error = f"Action failed: {response_data.get('error', 'Unknown error')}"
                            self.state = "complete"
                            return f"{self.validation_error}\nPress 9 to go back, 0 to exit"
                    except requests.RequestException as e:
                        self.validation_error = f"Action failed: {str(e)}"
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
                    self.current_step = 0
                    self.inputs = {}
                    return self.engine.get_current_prompt()
                return "No previous menu\nPress 9 to go back, 0 to exit"
            elif validation_result == "0":
                if self.engine:
                    self.engine.set_current_node("exit_node")
                    self.state = "input"
                    self.current_step = 0
                    self.inputs = {}
                    return self.engine.get_current_prompt()
                return "Session ended"
            elif validation_result in self.next_nodes:
                target_node_id = self.next_nodes[validation_result]
                if self.engine and self.engine.current_node_id:
                    self.engine.navigation_stack.append(self.engine.current_node_id)
                    self.engine.set_current_node(target_node_id)
                    self.state = "input"
                    self.current_step = 0
                    self.inputs = {}
                    return self.engine.get_current_prompt()
        
        return self.getNext()   
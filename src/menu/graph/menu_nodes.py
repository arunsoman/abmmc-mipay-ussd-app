from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import re
import requests
import json
import os
from jsonschema import validate, ValidationError
from src.services.service_registery import ServiceRegistry
from src.services.banking_service import BankingService
from src.services.services import AuthService
from src.menu.graph.schemas.schema_utils import SCHEMA_CACHE, schema_utils_SCHEMA_REGISTRY
from src.menu.graph.nodes.exit_node import ExitNode
from src.menu.graph.nodes.main_menu import MenuNavigationNode
from src.menu.graph.nodes.multiInpu_action_node import MultiInputActionNode
from src.menu.graph.nodes.single_input_action_node import SingleInputActionNode
from src.menu.graph.nodes.valiadtion_gate import ValidationGateNode


# Schema registry: Maps node types to schema file paths


#
def load_schema(node_type: str) -> Dict[str, Any]:
    """Load a JSON schema from file and cache it."""
    if node_type not in schema_utils_SCHEMA_REGISTRY:
        raise ValueError(f"No schema defined for node type: {node_type}")
    
    if node_type not in SCHEMA_CACHE:
        schema_path = os.path.join(os.path.dirname(__file__),  schema_utils_SCHEMA_REGISTRY[node_type])
        try:
            with open(schema_path, 'r') as f:
                SCHEMA_CACHE[node_type] = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema {schema_path}: {str(e)}")
    
    return SCHEMA_CACHE[node_type]

def validate_node_config(node_id: str, node_config: Dict[str, Any]):
    """Validate a node configuration against its schema."""
    node_type = node_config.get("type")
    if not node_type:
        raise ValueError(f"Node {node_id} is missing 'type' in configuration")
    
    schema = load_schema(node_type)
    try:
        validate(instance=node_config, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Validation error for node {node_id}: {str(e)}")

service_config = {}

class MenuNode(ABC):
    """Abstract base class for all menu nodes with renderer logic."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.validation_error = ""
        self.next_nodes: Dict[str, str] = {}  # Key: condition, Value: node_id
        self.engine: Optional['MenuEngine'] = None
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

class MultiInputActionNode(MenuNode):
    """Node for multi-step input collection with renderer logic."""
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
            if "{bundle_options}" in prompt and "dynamic_options" in step_config:
                bundle_type = self.inputs.get("bundle_type")
                if bundle_type:
                    options = step_config["dynamic_options"]["bundle_type"].get(bundle_type, [])
                    bundle_options = "\n".join([f"{i+1}. {opt['name']} - {opt['price']} AFN" for i, opt in enumerate(options)])
                    prompt = prompt.replace("{bundle_options}", bundle_options)
            error_msg = f"\n{self.validation_error}" if self.validation_error else ""
            return f"{prompt}{error_msg}"
        elif self.state == "confirm":
            prompt = self.confirmation_prompt
            for key, value in self.inputs.items():
                if isinstance(value, dict):
                    prompt = prompt.replace(f"{{{key}}}", str(value.get("name", value)))
                    prompt = prompt.replace(f"{{{key}_price}}", str(value.get("price", "")))
                else:
                    prompt = prompt.replace(f"{{{key}}}", str(value))
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
                    return "valid"
                self.validation_error = "Invalid input format"
                return ""
            elif "options" in validation:
                try:
                    choice = int(user_input)
                    options = validation.get("options", [])
                    if step_config.get("dynamic_options") and input_key == "bundle_id":
                        bundle_type = self.inputs.get("bundle_type")
                        if bundle_type:
                            options = step_config["dynamic_options"]["bundle_type"].get(bundle_type, [])
                    if 1 <= choice <= len(options):
                        self.inputs[input_key] = options[choice - 1]
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
        validation_result = self.validate(user_input)
        
        if self.state == "input" and validation_result == "valid":
            step_config = self.steps[self.current_step]
            input_key = step_config["input_key"]
            
            if self.action_url:
                payload = {
                    "msisdn": self.msisdn,
                    input_key: self.inputs[input_key] if not isinstance(self.inputs[input_key], dict) else self.inputs[input_key]["id"],
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
                    if not response_data.get("success"):
                        self.validation_error = f"Step {self.current_step + 1} failed: {response_data.get('error', 'Unknown error')}"
                        return self.getNext()
                except requests.RequestException as e:
                    self.validation_error = f"Step {self.current_step + 1} failed: {str(e)}"
                    return self.getNext()
                
            self.current_step += 1
            if self.current_step >= len(self.steps):
                self.state = "confirm"
            return self.getNext()
        
        elif self.state == "confirm":
            if validation_result == "1":
                self.state = "complete"
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
            elif validation_result == "0" or validation_result == "":
                if self.engine:
                    self.engine.set_current_node("exit_node")
                    self.state = "input"
                    self.current_step = 0
                    self.inputs = {}
                    return self.engine.get_current_prompt()
                return "Session ended"
            elif validation_result in self.next_nodes:
                target_node_id = self.next_nodes[validation_result]
                if self.engine:
                    self.engine.navigation_stack.append(self.engine.current_node_id)
                    self.engine.set_current_node(target_node_id)
                    self.state = "input"
                    self.current_step = 0
                    self.inputs = {}
                    return self.engine.get_current_prompt()
        
        return self.getNext()

class MenuEngine:
    """Engine to manage nodes and handle user interactions."""
    def __init__(self):
        self.nodes: Dict[str, MenuNode] = {}
        self.current_node: Optional[MenuNode] = None
        self.current_node_id: Optional[str] = None
        self.session_active = True
        self.navigation_stack: List[str] = []
        
    def add_node(self, node: MenuNode):
        self.nodes[node.node_id] = node
        node.set_engine(self)
    
    def set_current_node(self, node_id: str):
        if node_id in self.nodes:
            self.current_node = self.nodes[node_id]
            self.current_node_id = node_id
        else:
            raise ValueError(f"Node {node_id} not found")
    
    def process_user_input(self, user_input: str) -> str:
        if not self.current_node or not self.session_active:
            return "Session ended"
        return self.current_node.handleUserInput(user_input)
    
    def get_current_prompt(self) -> str:
        if self.current_node:
            return self.current_node.getNext()
        return "Session ended"

def load_config_from_source(source: str) -> Dict[str, Any]:
    """Load configuration from various sources (Python module, JSON file, or URL)."""
    import importlib.util
    import requests
    
    if source.endswith(".py"):
        spec = importlib.util.spec_from_file_location("config_module", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "config", {})
    
    elif source.endswith(".json"):
        with open(source, 'r') as f:
            return json.load(f)
    
    elif source.startswith(("http://", "https://")):
        try:
            response = requests.get(source, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to load config from URL {source}: {str(e)}")
    
    raise ValueError(f"Unsupported config source: {source}")

def load_Menu_engine(msisdn: str, config: Dict[str, Any] = None, config_source: str = None) -> MenuEngine:
    """Load menu engine with configuration, validating against schemas."""
    if config_source and not config:
        config = load_config_from_source(config_source)
    
    if not config:
        raise ValueError("No configuration provided")
    
    engine = MenuEngine()
    for node_id, node_config in config.items():
        try:
            validate_node_config(node_id, node_config)
        except ValueError as e:
            print(f"Skipping node {node_id}: {str(e)}")
            continue
        
        node_config = node_config.copy()
        node_config.update({"msisdn": msisdn})
        
        node_type = node_config.get("type")
        node: MenuNode
        if node_type == "multi_input_action":
            node = MultiInputActionNode(node_id, node_config)
        elif node_type == "exit":
            node = ExitNode(node_id, node_config)
        elif node_type == "single_input_action":
            node = SingleInputActionNode(node_id, node_config)
        elif node_type == "menu_navigation":
            node = MenuNavigationNode(node_id, node_config)
        elif node_type == "validation_gate":
            node = ValidationGateNode(node_id, node_config)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
            
        engine.add_node(node)
    
    for node_id, node_config in config.items():
        if node_id not in engine.nodes:
            continue
        
        node = engine.nodes[node_id]
        
        if "on_success" in node_config:
            target = node_config["on_success"].get("target_menu")
            if target:
                node.add_transition("success", target)
        
        if "on_failure" in node_config:
            target = node_config["on_failure"].get("target_menu")
            if target:
                node.add_transition("failure", target)
        
        if "options" in node_config:
            for option in node_config["options"]:
                target = option.get("target_menu")
                if target:
                    node.add_transition(option["key"], target)
        
        if "transitions" in node_config:
            for key, target in node_config["transitions"].items():
                node.add_transition(key, target)
    
    if "root_validation_gate" in engine.nodes:
        engine.set_current_node("root_validation_gate")
    elif engine.nodes:
        first_node_id = next(iter(engine.nodes.keys()))
        engine.set_current_node(first_node_id)
    
    return engine

if __name__ == "__main__":
    from src.menu.graph.demo_menu_config import config
    def interactive_console():
        engine = load_Menu_engine("1000", config)
       
        
        while engine.session_active:
            user_input = input("> ")
            print(engine.process_user_input(user_input))

    interactive_console()
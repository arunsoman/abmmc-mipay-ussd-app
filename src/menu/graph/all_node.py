from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, cast, List
import re
import requests
from src.menu.graph.demo_menu_config import config
from src.services.service_registery import ServiceRegistry
from src.services.banking_service import BankingService
from src.services.services import AuthService, BundleService, TopupService, BillPaymentService

service_config = {}

class MenuNode(ABC):
    """Base class for all Menu nodes."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.validation_error = ""
        self.next_nodes: Dict[str, str] = {}  # Key: condition, Value: node_id
        self.engine: Optional['MenuEngine'] = None
        self.msisdn = config.get("msisdn", "")
        self.key: Optional[str] = None
        self.auth_key: Optional[str] = None
        
    def add_transition(self, condition: str, target_node_id: str):
        """Add transition to another node."""
        self.next_nodes[condition] = target_node_id
    
    def set_engine(self, engine: 'MenuEngine'):
        """Set reference to engine for node transitions."""
        self.engine = engine
    
    def get_prompt(self) -> str:
        """Get current node's prompt with validation error if any."""
        error_msg = f"\n{self.validation_error}" if self.validation_error else ""
        return f"{self.config.get('prompt', '')}{error_msg}"
    
    @abstractmethod
    def validate(self, user_input: str) -> str:
        """Validate input and return next node condition or empty string to stay."""
        pass
    
    @abstractmethod
    def processInput(self, user_input: str) -> str:
        """Process input with custom logic and return response."""
        pass

class MultiInputActionNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.state = "input"  # input -> confirm -> complete
        self.current_step = 0
        self.inputs: Dict[str, Any] = {}
        self.steps: List[Dict[str, Any]] = config.get("steps", [])
        self.confirmation_prompt = config.get("confirmation_prompt", "")
        self.action_url = config.get("action_url")
        self.params = config.get("params", {})
        self.success_prompt = config.get("success_prompt", "Action completed\nReceipt: {receipt_number}")

    def get_prompt(self) -> str:
        if self.state == "input" and self.current_step < len(self.steps):
            error_msg = f"\n{self.validation_error}" if self.validation_error else ""
            return f"{self.steps[self.current_step]['prompt']}{error_msg}"
        elif self.state == "confirm":
            prompt = self.confirmation_prompt
            for key, value in self.inputs.items():
                prompt = prompt.replace(f"{{{key}}}", str(value))
            return f"{prompt}\n"
        elif self.state == "complete":
            return self.success_prompt
        return "Service unavailable"

    def validate(self, user_input: str) -> str:
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
            else:
                self.inputs[input_key] = user_input
                return "valid"
        
        elif self.state == "confirm":
            if user_input in ["1", "2"]:
                return user_input
            self.validation_error = "Please select 1 or 2"
            return ""
        
        elif self.state == "complete":
            if user_input in self.next_nodes:
                return user_input
            self.validation_error = "Invalid option"
            return ""
        
        return ""

    def processInput(self, user_input: str) -> str:
        validation_result = self.validate(user_input)
        
        if self.state == "input" and validation_result == "valid":
            self.current_step += 1
            if self.current_step >= len(self.steps):
                self.state = "confirm"
                # Track the previous menu before showing confirmation
                if self.engine and self.engine.current_node_id != self.node_id:
                    self.engine.navigation_stack.append(self.engine.current_node_id)
                self.engine.current_node_id = self.node_id
            return self.get_prompt()
        
        elif self.state == "confirm":
            if validation_result == "1":
                if self.action_url:
                    # Prepare payload with msisdn, inputs, and params
                    payload = {"msisdn": self.msisdn, **self.inputs, **self.params}
                    # Replace placeholders in params (e.g., <phone_number>)
                    for key, value in payload.items():
                        if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                            input_key = value[1:-1]
                            payload[key] = self.inputs.get(input_key, value)
                    try:
                        response = requests.post(self.action_url, json=payload, timeout=5)
                        response_data = response.json()
                        if response_data.get("success"):
                            self.state = "complete"
                            return self.success_prompt.format(**response_data)
                        else:
                            return f"Action failed: {response_data.get('error', 'Unknown error')}\nPress 9 to go back"
                    except Exception as e:
                        return f"Action failed: {str(e)}\nPress 9 to go back"
                else:
                    # For nodes like others_bundle with null action_url
                    if "*" in self.next_nodes:
                        target_node_id = self.next_nodes["*"]
                        if self.engine:
                            self.engine.navigation_stack.append(self.engine.current_node_id)
                            self.engine.set_current_node(target_node_id)
                            return self.engine.current_node.get_prompt()
                        return "Service unavailable"
                    return "No action defined\nPress 9 to go back"
            elif validation_result == "2":
                # Return to previous menu
                if self.engine and self.engine.navigation_stack:
                    target_node_id = self.engine.navigation_stack.pop()
                    self.engine.set_current_node(target_node_id)
                    self.state = "input"
                    self.current_step = 0
                    self.inputs = {}
                    return self.engine.current_node.get_prompt()
                return "No previous menu\nPress 9 to go back"
        
        elif self.state == "complete" and validation_result in self.next_nodes:
            target_node_id = self.next_nodes[validation_result]
            if self.engine:
                self.engine.navigation_stack.append(self.engine.current_node_id)
                self.engine.set_current_node(target_node_id)
                self.state = "input"
                self.current_step = 0
                self.inputs = {}
                return self.engine.current_node.get_prompt()
        
        return self.get_prompt()

class ValidationGateNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.max_attempts = config.get("max_attempts", 3)
        self.current_attempts = 0
        self.valid_pin = config.get("valid_pin", "123456")
        self.service = cast(AuthService, ServiceRegistry.get_service("auth"))

    def validate(self, user_input: str) -> str:
        self.current_attempts += 1
        self.validation_error = ""
        
        token = self.service.validate_pin(self.msisdn, user_input)
        if self.msisdn and token:
            service_config[self.msisdn] = {
                "msisdn": self.msisdn,
                "auth_token": token
            }
            return "success"
        
        if self.current_attempts >= self.max_attempts:
            return "failure"
        
        self.validation_error = "Invalid PIN. Enter PIN."
        return ""

    def processInput(self, user_input: str) -> str:
        validation_result = self.validate(user_input)
        
        if validation_result:
            target_node_id = self.next_nodes.get(validation_result)
            if target_node_id and self.engine:
                self.engine.navigation_stack.append(self.engine.current_node_id)
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        return self.get_prompt()

class TransferNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.banking_service = cast(BankingService, ServiceRegistry.get_service('banking'))
        self.transfer_state = "recipient"  # recipient -> amount -> pin -> confirm
        self.recipient_number = ""
        self.amount = ""
        self.max_amount = config.get("max_amount", 10000)
        self.min_amount = config.get("min_amount", 1)
    
    def get_prompt(self) -> str:
        if self.transfer_state == "recipient":
            return "Enter recipient phone number:"
        elif self.transfer_state == "amount":
            return f"Enter amount (Min: {self.min_amount}, Max: {self.max_amount} AFN):"
        elif self.transfer_state == "pin":
            return "Enter your PIN:"
        elif self.transfer_state == "confirm":
            return f"Transfer {self.amount} AFN to {self.recipient_number}? 1: OK, 2: Cancel"
        return "Transfer service unavailable"
    
    def validate_phone(self, phone: str) -> bool:
        return len(phone) >= 10 and phone.isdigit()
    
    def validate_amount(self, amount: str) -> bool:
        try:
            amt = float(amount)
            return self.min_amount <= amt <= self.max_amount
        except ValueError:
            return False
    
    def validate(self, user_input: str) -> str:
        # This method is required by the abstract base class
        return ""
    
    def processInput(self, user_input: str) -> str:
        if self.transfer_state == "recipient":
            if self.validate_phone(user_input):
                self.recipient_number = user_input
                self.transfer_state = "amount"
                if self.engine:
                    self.engine.navigation_stack.append(self.engine.current_node_id)
                return self.get_prompt()
            return "Invalid phone number. " + self.get_prompt()
        
        elif self.transfer_state == "amount":
            if self.validate_amount(user_input):
                self.amount = user_input
                self.transfer_state = "pin"
                return self.get_prompt()
            return f"Invalid amount. Must be between {self.min_amount}-{self.max_amount} AFN. " + self.get_prompt()
        
        elif self.transfer_state == "pin":
            if self.msisdn and self.banking_service.validate_pin(self.msisdn, user_input):
                self.transfer_state = "confirm"
                return self.get_prompt()
            return "Invalid PIN. " + self.get_prompt()
        
        elif self.transfer_state == "confirm":
            if user_input == "1" and self.msisdn and self.recipient_number and self.amount and self.key:
                result = self.banking_service.transfer_funds(
                    from_msisdn=self.msisdn,
                    to_msisdn=self.recipient_number,
                    pin=self.key,
                    amount=float(self.amount)
                )
                if result.get("success"):
                    if self.engine:
                        self.engine.navigation_stack.append(self.engine.current_node_id)
                    return f"Transfer successful! Transaction ID: {result.get('transaction_id')}\nPress 0 to go back"
                else:
                    return f"Transfer failed: {result.get('error')}\nPress 0 to go back"
            elif user_input == "2":
                if self.engine and self.engine.navigation_stack:
                    target_node_id = self.engine.navigation_stack.pop()
                    self.engine.set_current_node(target_node_id)
                    self.transfer_state = "recipient"
                    return self.engine.current_node.get_prompt()
                return "No previous menu\nPress 0 to go back"
            return "Invalid choice. " + self.get_prompt()
        
        return self.get_prompt()

class TopupNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.telecom_service = cast(TopupService, ServiceRegistry.get_service('telecom'))
        self.topup_state = "phone"  # phone -> amount -> pin -> confirm
        self.target_number = ""
        self.amount = ""
        self.topup_amounts: List[int] = config.get("amounts", [10, 20, 50, 100, 200])
    
    def get_prompt(self) -> str:
        if self.topup_state == "phone":
            return "Enter phone number to top up:"
        elif self.topup_state == "amount":
            prompt = "Select amount:\n"
            for i, amount in enumerate(self.topup_amounts, 1):
                prompt += f"{i}. {amount} AFN\n"
            return prompt
        elif self.topup_state == "pin":
            return "Enter your PIN:"
        elif self.topup_state == "confirm":
            return f"Top up {self.amount} AFN to {self.target_number}? 1: OK, 2: Cancel"
        return "Top up service unavailable"
    
    def validate(self, user_input: str) -> str:
        # This method is required by the abstract base class
        return ""
    
    def processInput(self, user_input: str) -> str:
        if self.topup_state == "phone":
            if len(user_input) >= 10 and user_input.isdigit():
                self.target_number = user_input
                self.topup_state = "amount"
                if self.engine:
                    self.engine.navigation_stack.append(self.engine.current_node_id)
                return self.get_prompt()
            return "Invalid phone number. " + self.get_prompt()
        
        elif self.topup_state == "amount":
            try:
                choice = int(user_input)
                if 1 <= choice <= len(self.topup_amounts):
                    self.amount = str(self.topup_amounts[choice - 1])
                    self.topup_state = "pin"
                    return self.get_prompt()
            except ValueError:
                pass
            return "Invalid selection. " + self.get_prompt()
        
        elif self.topup_state == "confirm":
            if user_input == "1" and self.msisdn and self.target_number:
                result = self.telecom_service.topup_phone(
                    self.msisdn,
                    self.target_number,
                    float(self.amount)
                )
                if result.get("success"):
                    if self.engine:
                        self.engine.navigation_stack.append(self.engine.current_node_id)
                    return f"Top up successful! Reference: {result.get('reference')}\nPress 0 to go back"
                else:
                    return f"Top up failed: {result.get('error')}\nPress 0 to go back"
            elif user_input == "2":
                if self.engine and self.engine.navigation_stack:
                    target_node_id = self.engine.navigation_stack.pop()
                    self.engine.set_current_node(target_node_id)
                    self.topup_state = "phone"
                    return self.engine.current_node.get_prompt()
                return "No previous menu\nPress 0 to go back"
            return "Invalid choice. " + self.get_prompt()
        
        return self.get_prompt()

class BundlePurchaseNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.bundle_service = cast(BundleService, ServiceRegistry.get_service('bundle'))
        self.purchase_state = "type"  # type -> bundle -> pin -> confirm
        self.bundle_type = ""
        self.selected_bundle: Dict[str, Any] = {}
        self.bundle_types: Dict[str, Any] = config.get("bundle_types", {
            "1": {"name": "Data", "bundles": [
                {"id": "data_1gb", "name": "1GB - 7 days", "price": 50},
                {"id": "data_3gb", "name": "3GB - 30 days", "price": 150},
                {"id": "data_10gb", "name": "10GB - 30 days", "price": 400}
            ]},
            "2": {"name": "Voice", "bundles": [
                {"id": "voice_100min", "name": "100 minutes", "price": 30},
                {"id": "voice_500min", "name": "500 minutes", "price": 120},
                {"id": "voice_unlimited", "name": "Unlimited - 30 days", "price": 300}
            ]},
            "3": {"name": "SMS", "bundles": [
                {"id": "sms_100", "name": "100 SMS", "price": 10},
                {"id": "sms_500", "name": "500 SMS", "price": 40},
                {"id": "sms_1000", "name": "1000 SMS", "price": 70}
            ]}
        })
    
    def get_prompt(self) -> str:
        if self.purchase_state == "type":
            prompt = "Select bundle type:\n"
            for key, bundle_type in self.bundle_types.items():
                prompt += f"{key}. {bundle_type['name']}\n"
            return prompt
        elif self.purchase_state == "bundle":
            bundles = self.bundle_types[self.bundle_type]["bundles"]
            prompt = f"Select {self.bundle_types[self.bundle_type]['name']} bundle:\n"
            for i, bundle in enumerate(bundles, 1):
                prompt += f"{i}. {bundle['name']} - {bundle['price']} AFN\n"
            return prompt
        elif self.purchase_state == "pin":
            return "Enter your PIN:"
        elif self.purchase_state == "confirm":
            return f"Purchase {self.selected_bundle['name']} for {self.selected_bundle['price']} AFN? 1: OK, 2: Cancel"
        return "Bundle purchase service unavailable"
    
    def validate(self, user_input: str) -> str:
        # This method is required by the abstract base class
        return ""
    
    def processInput(self, user_input: str) -> str:
        if self.purchase_state == "type":
            if user_input in self.bundle_types:
                self.bundle_type = user_input
                self.purchase_state = "bundle"
                if self.engine:
                    self.engine.navigation_stack.append(self.engine.current_node_id)
                return self.get_prompt()
            return "Invalid selection. " + self.get_prompt()
        
        elif self.purchase_state == "bundle":
            try:
                choice = int(user_input)
                bundles = self.bundle_types[self.bundle_type]["bundles"]
                if 1 <= choice <= len(bundles):
                    self.selected_bundle = bundles[choice - 1]
                    self.purchase_state = "pin"
                    return self.get_prompt()
            except ValueError:
                pass
            return "Invalid selection. " + self.get_prompt()
        
        elif self.purchase_state == "confirm":
            if user_input == "1" and self.msisdn and self.selected_bundle:
                result = self.bundle_service.purchase_bundle(
                    self.msisdn,
                    self.selected_bundle['id'],
                    self.selected_bundle['price']
                )
                if result:
                    if self.engine:
                        self.engine.navigation_stack.append(self.engine.current_node_id)
                    return f"Bundle activated! Reference: {result.get('reference')}\nPress 0 to go back"
                else:
                    return f"Purchase failed: {result.get('error')}\nPress 0 to go back"
            elif user_input == "2":
                if self.engine and self.engine.navigation_stack:
                    target_node_id = self.engine.navigation_stack.pop()
                    self.engine.set_current_node(target_node_id)
                    self.purchase_state = "type"
                    return self.engine.current_node.get_prompt()
                return "No previous menu\nPress 0 to go back"
            return "Invalid choice. " + self.get_prompt()
        
        return self.get_prompt()

class MenuNavigationNode(MenuNode):
    def validate(self, user_input: str) -> str:
        self.validation_error = ""
        
        options = self.config.get("options", [])
        for option in options:
            if user_input == option["key"]:
                return option["key"]
        
        if user_input == "0" and "back" in self.next_nodes:
            return "back"
        if user_input == "#" and "exit" in self.next_nodes:
            return "exit"
            
        valid_options = [opt["key"] for opt in options]
        self.validation_error = f"Invalid option. Valid: {', '.join(valid_options)}"
        return ""
    
    def processInput(self, user_input: str) -> str:
        validation_result = self.validate(user_input)
        
        if validation_result:
            target_node_id = self.next_nodes.get(validation_result)
            if target_node_id and self.engine:
                self.engine.navigation_stack.append(self.engine.current_node_id)
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        return self.get_prompt()

class SingleInputActionNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
    
    def validate(self, user_input: str) -> str:
        self.validation_error = ""
        
        transitions = self.config.get("transitions", {})
        if user_input in transitions:
            return user_input
            
        return ""
    
    def processInput(self, user_input: str) -> str:
        validation_result = self.validate(user_input)
        
        if validation_result:
            transitions = self.config.get("transitions", {})
            target_node_id = transitions.get(validation_result)
            if target_node_id and self.engine:
                self.engine.navigation_stack.append(self.engine.current_node_id)
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        return self.get_prompt()

class ExitNode(MenuNode):
    def validate(self, user_input: str) -> str:
        return "terminate"
    
    def processInput(self, user_input: str) -> str:
        if self.engine:
            self.engine.session_active = False
        return "Session ended"

class BalanceCheckNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.banking_service = cast(BankingService, ServiceRegistry.get_service('banking'))
    
    def get_prompt(self) -> str:
        balance = self.banking_service.get_balance(self.msisdn) if self.msisdn else 0.0
        return f"Your balance: {balance} AFN\nPress 0 to go back"

    def validate(self, user_input: str) -> str:
        self.validation_error = ""
        if user_input == "0" and "back" in self.next_nodes:
            return "back"
        self.validation_error = "Invalid option. Press 0 to go back"
        return ""

    def processInput(self, user_input: str) -> str:
        validation_result = self.validate(user_input)
        
        if validation_result:
            target_node_id = self.next_nodes.get(validation_result)
            if target_node_id and self.engine:
                self.engine.navigation_stack.append(self.engine.current_node_id)
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        return self.get_prompt()

class MenuEngine:
    def __init__(self):
        self.nodes: Dict[str, MenuNode] = {}
        self.current_node: Optional[MenuNode] = None
        self.current_node_id: Optional[str] = None
        self.session_active = True
        self.navigation_stack: List[str] = []  # Stack to track navigation history
        
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
            
        return self.current_node.processInput(user_input)
    
    def get_current_prompt(self) -> str:
        if self.current_node:
            return self.current_node.get_prompt()
        return "Session ended"

def load_Menu_engine(msisdn: str, config: Dict[str, Any]) -> MenuEngine:
    engine = MenuEngine()
    for node_id, node_config in config.items():
        node_config = node_config.copy()
        node_config.update({"msisdn": msisdn})
        
        node_type = node_config.get("type")
        if not node_type:
            print(f"Node {node_id} is missing 'type' in configuration")
            continue
        
        node: MenuNode
        if node_type == "validation_gate":
            node = ValidationGateNode(node_id, node_config)
        elif node_type == "menu_navigation":
            node = MenuNavigationNode(node_id, node_config)
        elif node_type == "single_input_action":
            node = SingleInputActionNode(node_id, node_config)
        elif node_type == "multi_input_action":
            node = MultiInputActionNode(node_id, node_config)
        elif node_type == "exit":
            node = ExitNode(node_id, node_config)
        elif node_type == "balance_check":
            node = BalanceCheckNode(node_id, node_config)
        elif node_type == "transfer":
            node = TransferNode(node_id, node_config)
        elif node_type == "topup":
            node = TopupNode(node_id, node_config)
        elif node_type == "bundle_purchase":
            node = BundlePurchaseNode(node_id, node_config)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
            
        engine.add_node(node)
    
    # Set up transitions
    for node_id, node_config in config.items():
        if node_id not in engine.nodes:
            print(f"Node {node_id} not found in engine")
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
    
    # Set starting node
    if "root_validation_gate" in engine.nodes:
        engine.set_current_node("root_validation_gate")
    elif engine.nodes:
        # If no root_validation_gate, set to first available node
        first_node_id = next(iter(engine.nodes.keys()))
        engine.set_current_node(first_node_id)
    
    return engine

if __name__ == "__main__":
    from src.menu.graph.demo_menu_config import config
    
    def interactive_console():
        engine = load_Menu_engine("1000", config)
        
        print("="*50)
        print("Menu Interactive Console")
        print("="*50)
        print("PIN: 123456 (3 attempts)")
        print
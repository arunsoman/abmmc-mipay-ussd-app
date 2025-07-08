from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, cast
from src.menu.graph.demo_menu_config import config
from src.services.service_registery import ServiceRegistry
from src.services.banking_service import BankingService
from src.services.services import AuthService,  BundleService, TopupService, BillPaymentService


class MenuNode(ABC):
    """Base class for all Menu nodes."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.config = config
        self.validation_error = ""
        self.next_nodes = {}  # Key: condition, Value: node_id
        self.engine = None 
        self.msisdn = config.get("msisdn", None)
        self.key = None
        self.auth_key = None
        
    def add_transition(self, condition: str, target_node_id: str):
        """Add transition to another node."""
        self.next_nodes[condition] = target_node_id
    
    def set_engine(self, engine):
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

class ValidationGateNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.max_attempts = config.get("max_attempts", 3)
        self.current_attempts = 0
        self.valid_pin = config.get("valid_pin", "123456")
        self.service = cast(AuthService ,ServiceRegistry.get_service("auth") )


    def validate(self, user_input: str) -> str:
        self.current_attempts += 1
        self.validation_error = ""
        
        if self.msisdn and  self.service.validate_pin(self.msisdn, user_input):
            return "success"
        
        if self.current_attempts >= self.max_attempts:
            return "failure"
        
        self.validation_error = f"Enter PIN. "
        return ""  # Stay in current node
    
    def processInput(self, user_input: str) -> str:
        """Custom validation gate logic."""
        validation_result = self.validate(user_input)
        
        if validation_result == "success":
            # Move to success node
            target_node_id = self.next_nodes.get("success")
            if target_node_id and self.engine:
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        elif validation_result == "failure":
            # Move to failure node
            target_node_id = self.next_nodes.get("failure")
            if target_node_id and self.engine:
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        # Stay in current node - return prompt with validation error
        return self.get_prompt()

class TransferNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.banking_service = cast(BankingService,  ServiceRegistry.get_service('banking'))
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
            return f"Transfer {self.amount} AFN to {self.recipient_number}?\n1. Confirm\n2. Cancel"
        return "Transfer service unavailable"
    
    def validate_phone(self, phone: str) -> bool:
        return len(phone) >= 10 and phone.isdigit()
    
    def validate_amount(self, amount: str) -> bool:
        try:
            amt = float(amount)
            return self.min_amount <= amt <= self.max_amount
        except ValueError:
            return False
    
    def processInput(self, user_input: str) -> str:
        if self.transfer_state == "recipient":
            if self.validate_phone(user_input):
                self.recipient_number = user_input
                self.transfer_state = "amount"
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
            if user_input == "1" and self.msisdn and self.recipient_number \
            and self.amount and self.key:
                result = self.banking_service.transfer_funds(
                    from_msisdn=self.msisdn,
                    to_msisdn=self.recipient_number,
                    pin=self.key,
                    amount= float(self.amount)
                )
                if result.get("success"):
                    return f"Transfer successful! Transaction ID: {result.get('transaction_id')}\nPress 0 to go back"
                else:
                    return f"Transfer failed: {result.get('error')}\nPress 0 to go back"
            elif user_input == "2":
                return "Transfer cancelled.\nPress 0 to go back"
            return "Invalid choice. " + self.get_prompt()
        
        return self.get_prompt()


class TopupNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.telecom_service = cast( TopupService ,ServiceRegistry.get_service('telecom'))
        self.topup_state = "phone"  # phone -> amount -> pin -> confirm
        self.target_number = ""
        self.amount = ""
        self.topup_amounts = config.get("amounts", [10, 20, 50, 100, 200])
        
    
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
            return f"Top up {self.amount} AFN to {self.target_number}?\n1. Confirm\n2. Cancel"
        return "Top up service unavailable"
    
    def processInput(self, user_input: str) -> str:
        if self.topup_state == "phone":
            if len(user_input) >= 10 and user_input.isdigit():
                self.target_number = user_input
                self.topup_state = "amount"
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
            if user_input == "1" and self.msisdn and self.target_number :
                result = self.telecom_service.topup_phone(
                    self.msisdn,
                    self.target_number,
                    float(self.amount)
                )
                if result.get("success"):
                    return f"Top up successful! Reference: {result.get('reference')}\nPress 0 to go back"
                else:
                    return f"Top up failed: {result.get('error')}\nPress 0 to go back"
            elif user_input == "2":
                return "Top up cancelled.\nPress 0 to go back"
            return "Invalid choice. " + self.get_prompt()
        
        return self.get_prompt()


# class BillPaymentNode(MenuNode):
#     def __init__(self, node_id: str, config: Dict[str, Any]):
#         super().__init__(node_id, config)
#         self.billing_service = cast( ,ServiceRegistry.get_service('billing'))
#         self.payment_state = "provider"  # provider -> account -> amount -> pin -> confirm
#         self.provider = ""
#         self.account_number = ""
#         self.amount = ""
#         self.providers = config.get("providers", ["Electricity", "Water", "Internet", "Gas"])
    
#     def get_prompt(self) -> str:
#         if self.payment_state == "provider":
#             prompt = "Select bill provider:\n"
#             for i, provider in enumerate(self.providers, 1):
#                 prompt += f"{i}. {provider}\n"
#             return prompt
#         elif self.payment_state == "account":
#             return f"Enter your {self.provider} account number:"
#         elif self.payment_state == "amount":
#             return "Enter payment amount (AFN):"
#         elif self.payment_state == "pin":
#             return "Enter your PIN:"
#         elif self.payment_state == "confirm":
#             return f"Pay {self.amount} AFN for {self.provider} account {self.account_number}?\n1. Confirm\n2. Cancel"
#         return "Bill payment service unavailable"
    
#     def processInput(self, user_input: str) -> str:
#         if self.payment_state == "provider":
#             try:
#                 choice = int(user_input)
#                 if 1 <= choice <= len(self.providers):
#                     self.provider = self.providers[choice - 1]
#                     self.payment_state = "account"
#                     return self.get_prompt()
#             except ValueError:
#                 pass
#             return "Invalid selection. " + self.get_prompt()
        
#         elif self.payment_state == "account":
#             if len(user_input) >= 5 and user_input.isalnum():
#                 self.account_number = user_input
#                 self.payment_state = "amount"
#                 return self.get_prompt()
#             return "Invalid account number. " + self.get_prompt()
        
#         elif self.payment_state == "amount":
#             try:
#                 amount = float(user_input)
#                 if amount > 0:
#                     self.amount = user_input
#                     self.payment_state = "pin"
#                     return self.get_prompt()
#             except ValueError:
#                 pass
#             return "Invalid amount. " + self.get_prompt()
        
#         elif self.payment_state == "pin":
#             if self.billing_service.validate_pin(self.msisdn, user_input):
#                 self.payment_state = "confirm"
#                 return self.get_prompt()
#             return "Invalid PIN. " + self.get_prompt()
        
#         elif self.payment_state == "confirm":
#             if user_input == "1":
#                 result = self.billing_service.pay_bill(
#                     self.msisdn,
#                     self.provider,
#                     self.account_number,
#                     float(self.amount)
#                 )
#                 if result.get("success"):
#                     return f"Payment successful! Receipt: {result.get('receipt_number')}\nPress 0 to go back"
#                 else:
#                     return f"Payment failed: {result.get('error')}\nPress 0 to go back"
#             elif user_input == "2":
#                 return "Payment cancelled.\nPress 0 to go back"
#             return "Invalid choice. " + self.get_prompt()
        
#         return self.get_prompt()


class BundlePurchaseNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.bundle_service = cast(BundleService ,ServiceRegistry.get_service('bundle'))
        self.purchase_state = "type"  # type -> bundle -> pin -> confirm
        self.bundle_type = ""
        self.selected_bundle = {}
        
        self.bundle_types = config.get("bundle_types", {
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
            return f"Purchase {self.selected_bundle['name']} for {self.selected_bundle['price']} AFN?\n1. Confirm\n2. Cancel"
        return "Bundle purchase service unavailable"
    
    def processInput(self, user_input: str) -> str:
        if self.purchase_state == "type":
            if user_input in self.bundle_types:
                self.bundle_type = user_input
                self.purchase_state = "bundle"
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
        
        # elif self.purchase_state == "pin":
        #     if self.bundle_service.validate_pin(self.msisdn, user_input):
        #         self.purchase_state = "confirm"
        #         return self.get_prompt()
        #     return "Invalid PIN. " + self.get_prompt()
        
        elif self.purchase_state == "confirm":
            if user_input == "1" and self.msisdn and self.selected_bundle:
                result = self.bundle_service.purchase_bundle(
                    self.msisdn,
                    self.selected_bundle['id'],
                    self.selected_bundle['price']
                )
                if result:
                    return f"Bundle activated! Reference: {result.get('reference')}\nPress 0 to go back"
                else:
                    return f"Purchase failed: {result.get('error')}\nPress 0 to go back"
            elif user_input == "2":
                return "Purchase cancelled.\nPress 0 to go back"
            return "Invalid choice. " + self.get_prompt()
        
        return self.get_prompt()
    
class MenuNavigationNode(MenuNode):
    def validate(self, user_input: str) -> str:
        self.validation_error = ""
        
        # Check if input matches any option
        options = self.config.get("options", [])
        for option in options:
            if user_input == option["key"]:
                return option["key"]
        
        # Check for back/exit options
        if user_input == "0" and "back" in self.next_nodes:
            return "back"
        if user_input == "#" and "exit" in self.next_nodes:
            return "exit"
            
        valid_options = [opt["key"] for opt in options]
        self.validation_error = f"Invalid option. Valid: {', '.join(valid_options)}"
        return ""
    
    def processInput(self, user_input: str) -> str:
        """Custom menu navigation logic."""
        validation_result = self.validate(user_input)
        
        if validation_result:
            # Move to target node
            target_node_id = self.next_nodes.get(validation_result)
            if target_node_id and self.engine:
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        # Stay in current node - return prompt with validation error
        return self.get_prompt()

class SingleInputActionNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        
    
    def validate(self, user_input: str) -> str:
        self.validation_error = ""
        
        # Check transitions from config
        transitions = self.config.get("transitions", {})
        if user_input in transitions:
            return user_input
            
        return ""
    
    def processInput(self, user_input: str) -> str:
        """Custom single action logic."""
        validation_result = self.validate(user_input)
        
        if validation_result:
            # Get target from transitions
            transitions = self.config.get("transitions", {})
            target_node_id = transitions.get(validation_result)
            if target_node_id and self.engine:
                self.engine.set_current_node(target_node_id)
                return self.engine.current_node.get_prompt()
        
        # Stay in current node - return prompt
        return self.get_prompt()

class ExitNode(MenuNode):
    def validate(self, user_input: str) -> str:
        return "terminate"
    
    def processInput(self, user_input: str) -> str:
        """Terminate session."""
        if self.engine:
            self.engine.session_active = False
        return "Session ended"
    
class BalanceCheckNode(MenuNode):
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.banking_service = cast(BundleService ,ServiceRegistry.get_service('banking'))
        

    
    def get_prompt(self) -> str:
        balance = self.banking_service.get_balance(self.msisdn) if self.msisdn else 0.0
        return f"Your balance: {balance} AFN\nPress 0 to go back"

class MenuEngine:
    """Central engine managing Menu flow."""
    def __init__(self):
        self.nodes = {}
        self.current_node = None
        self.session_active = True
        
    def add_node(self, node: MenuNode):
        """Add node to engine."""
        self.nodes[node.node_id] = node
        node.set_engine(self)  # Set engine reference
        
    def set_current_node(self, node_id: str):
        """Set current active node."""
        if node_id in self.nodes:
            self.current_node = self.nodes[node_id]
        else:
            raise ValueError(f"Node {node_id} not found")
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and return response."""
        if not self.current_node or not self.session_active:
            return "Session ended"
            
        return self.current_node.processInput(user_input)
    
    def get_current_prompt(self) -> str:
        """Get current node's prompt."""
        if self.current_node:
            return self.current_node.config.get("prompt", "")
        return "Session ended"

def load_Menu_engine(msisdn :str, config: Dict[str, Any]) -> MenuEngine:
    """Load Menu engine from configuration."""
    engine = MenuEngine()
    # Step 1: Create all nodes
    for node_id, node_config in config.items():
        node_config.update({"msisdn": msisdn})  
        try:
            node_type = node_config.get("type")
        except AttributeError:
            print(f"Node {node_id} is missing 'type' in configuration")
            continue
        
        if node_type == "validation_gate":
            node = ValidationGateNode(node_id, node_config)
        elif node_type == "menu_navigation":
            node = MenuNavigationNode(node_id, node_config)
        elif node_type == "single_input_action":
            node = SingleInputActionNode(node_id, node_config)
        elif node_type == "exit":
            node = ExitNode(node_id, node_config)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
            
        engine.add_node(node)
    
    # Step 2: Setup transitions
    for node_id, node_config in config.items():
        try:
            node = engine.nodes[node_id]
        except KeyError:
            print(f"Node {node_id} not found in engine")
            continue
        
        # Handle success transitions
        if "on_success" in node_config:
            target = node_config["on_success"].get("target_menu")
            if target:
                node.add_transition("success", target)
        
        # Handle failure transitions
        if "on_failure" in node_config:
            target = node_config["on_failure"].get("target_menu")
            if target:
                node.add_transition("failure", target)
        
        # Handle menu options
        if "options" in node_config:
            for option in node_config["options"]:
                target = option.get("target_menu")
                if target:
                    node.add_transition(option["key"], target)
    
    # Step 3: Set root node
    if "root_validation_gate" in engine.nodes:
        engine.set_current_node("root_validation_gate")
    
    return engine


if __name__ == "__main__":
    from src.menu.graph.demo_menu_config import config
    def interactive_console():
        """Interactive Menu console for testing."""
        
        
        # Setup transitions for single input actions
        # 
        engine = load_Menu_engine("1000",config)
        
        print("="*50)
        print("Menu Interactive Console")
        print("="*50)
        print("PIN: 123456 (3 attempts)")
        print("Type 'quit' to exit console")
        print("="*50)
        
        # Initial prompt
        print(f"\n{engine.get_current_prompt()}")
        
        while engine.session_active:
            try:
                user_input = input("\nEnter input: ").strip()
                
                if user_input.lower() == 'quit':
                    print("Exiting console...")
                    break
                
                response = engine.process_user_input(user_input)
                print(f"\n{response}")
                
                if not engine.session_active:
                    print("Session ended. Type 'quit' to exit console.")
                    break
                    
            except KeyboardInterrupt:
                print("\nExiting console...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    # Test the engine
    engine = load_Menu_engine("10000", config)
    
    print(engine.get_current_prompt())  # "Enter PIN:"
    print(engine.process_user_input("wrong"))  # Invalid PIN message
    print(engine.process_user_input("123456"))  # Success -> main menu
    print(engine.process_user_input("1"))  # -> my_money_menu
    print(engine.process_user_input("1.1"))  # -> balance_check
    print(engine.process_user_input("0"))  # -> back to my_money_menu
    interactive_console()

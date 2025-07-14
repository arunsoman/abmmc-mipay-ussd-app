from typing import Dict, Any, Optional, List
from src.menu.graph.nodes.node_abc import MenuNode
from src.menu.graph.schemas.schema_utils import validate_node_config, get_validated_config
from src.menu.graph.nodes.multiInpu_action_node import MultiInputActionNode
from src.menu.graph.nodes.valiadtion_gate import ValidationGateNode
from src.menu.graph.nodes.main_menu import MenuNavigationNode
from src.menu.graph.nodes.single_input_action_node import SingleInputActionNode
from src.menu.graph.nodes.exit_node import ExitNode
from src.menu.graph.nodes.msisdn_node import Msisdn_Node
import json
import argparse

class MenuEngine:
    """Engine to manage nodes and handle user interactions."""
    def __init__(self):
        self.nodes: Dict[str, MenuNode] = {}
        self.current_node: Optional[MenuNode] = None
        self.current_node_id: Optional[str] = None
        self.session_active: bool = True
        self.navigation_stack: List[str] = []
        self.config: Dict[str, Any] = {}

    def add_node(self, node: MenuNode) -> None:
        """Add a node to the engine's node dictionary."""
        if not isinstance(node.node_id, str):
            raise TypeError(f"node_id must be a string, got {type(node.node_id).__name__}: {node.node_id}")
        self.nodes[node.node_id] = node
        node.set_engine(self)
        print(f"Added node {node.node_id} to engine")

    def update_node(self, node_id: str, attributes: Dict[str, Any]) -> None:
        """Update attributes of a node identified by node_id."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found in nodes")
        node = self.nodes[node_id]
        for key, value in attributes.items():
            if key == "config":
                if not isinstance(value, dict):
                    raise TypeError(f"Config must be a dict, got {type(value).__name__}")
                node.config = value
            elif hasattr(node, key):
                setattr(node, key, value)
            else:
                raise AttributeError(f"Node has no attribute {key}")
        self.nodes[node_id] = node

    def set_current_node(self, node_id: str) -> None:
        """Set the current node in the USSD session."""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found in nodes: {list(self.nodes.keys())}")
        self.current_node = self.nodes[node_id]
        self.current_node_id = node_id
        print(f"Set current node to: {node_id}")

    def process_user_input(self, user_input: str) -> str:
        """Process user input and return the next prompt."""
        if not self.current_node or not self.session_active:
            return "Session ended"
        # TODO  intercept 0 to exit 0 to back
        if user_input == '0' or user_input == '9':
            if user_input == "0":
                self.navigation_stack.pop()
                self.set_current_node()
                self.current_node.getPrevious()
        val = self.current_node.handleUserInput(user_input)
        return val

    def get_current_prompt(self) -> str:
        """Get the prompt of the current node."""
        if self.current_node:
            return self.current_node.getNext() +"\n9 press go back \n0 perss exit."
        return "Session ended"

def load_Menu_engine(msisdn: str, config: Dict[str, Any]) -> MenuEngine:
    """Load menu engine with configuration, setting validation_gate as root."""
    config = get_validated_config("", config)
    engine = MenuEngine()
    engine.config = config

    for node_id, node_config in config.items():
        if node_id == "bundle_mapping":
            continue
        node_config = node_config.copy()
        node_config.update({"msisdn": msisdn})
        node_type = node_config.get("type")
        node: MenuNode
        if node_type == "multi_input_action":
            node = MultiInputActionNode(node_id=node_id, config=node_config)
        elif node_type == "exit":
            node = ExitNode(node_id=node_id, config=node_config)
        elif node_type == "single_input_action":
            node = SingleInputActionNode(node_id=node_id, config=node_config)
        elif node_type == "menu_navigation":
            node = MenuNavigationNode(node_id=node_id, config=node_config)
        elif node_type == "validation_gate":
            node = ValidationGateNode(node_id=node_id, config=node_config)
        elif node_type == "cache_post":
            node = Msisdn_Node(node_id=node_id, config=node_config)
        else:
            print(f"Skipping unknown node type {node_type} for {node_id}")
            continue

        node.msisdn=msisdn
        # Set engine and service MSISDN
        node.set_engine(engine)
        if isinstance(node, (SingleInputActionNode, MultiInputActionNode)):
            node.initialize_bundle_details()
        engine.add_node(node)

    for node_id, node_config in config.items():
        if node_id not in engine.nodes or node_id == "bundle_mapping":
            continue
        node = engine.nodes[node_id]
        if "transitions" in node_config:
            for key, target in node_config["transitions"].items():
                node.add_transition(key, target)
        if node_config.get("type") == "validation_gate":
            if "on_success" in node_config and isinstance(node_config["on_success"], dict) and "target_menu" in node_config["on_success"]:
                node.add_transition("success", node_config["on_success"]["target_menu"])
            if "on_failure" in node_config and isinstance(node_config["on_failure"], dict) and "target_menu" in node_config["on_failure"]:
                node.add_transition("failure", node_config["on_failure"]["target_menu"])

    if "root_validation_gate" in engine.nodes:
        engine.set_current_node("root_validation_gate")
    elif engine.nodes:
        first_node_id = next(iter(engine.nodes.keys()))
        engine.set_current_node(first_node_id)
        print(f"Warning: root_validation_gate not found, set {first_node_id} as root")
    else:
        raise ValueError("No valid nodes found in configuration")

    return engine

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Run USSD menu engine with a JSON config file")
#     parser.add_argument("config_file", type=str, help="Path to the JSON configuration file")
#     parser.add_argument("--msisdn", type=str, default="1234567890", help="MSISDN for the session (default: 1234567890)")
#     args = parser.parse_args()

#     try:
#         with open(args.config_file, 'r') as f:
#             config = json.load(f)
#     except FileNotFoundError:
#         print(f"Error: Config file {args.config_file} not found")
#         exit(1)
#     except json.JSONDecodeError:
#         print(f"Error: Invalid JSON in {args.config_file}")
#         exit(1)

#     engine = load_Menu_engine(args.msisdn, config)
#     print(engine.get_current_prompt())

#     while engine.session_active:
#         user_input = input("> ")
#         print(engine.process_user_input(user_input))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run USSD menu engine with a JSON config file")
    parser.add_argument("config_file", type=str, help="Path to the JSON configuration file")
    parser.add_argument("--msisdn", type=str, default="1234567890", help="MSISDN for the session (default: 1234567890)")
    args = {
        "config_file":r'C:\Users\arun\Documents\ussdgw\config\demo_menu_config.json',
        "msisdn":"555555555555"
    }

    try:
        with open(args['config_file'], 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file {args['config_file']} not found")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {args['config_file']}")
        exit(1)

    engine = load_Menu_engine(args['msisdn'], config)
    print(engine.get_current_prompt())
    while engine.session_active:
        user_input = input("> ")
        print(engine.current_node.handleUserInput(user_input))
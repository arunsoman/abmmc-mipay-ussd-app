from typing import Dict, Any, Optional, List
from src.menu.graph.nodes.node_abc import MenuNode
from src.menu.graph.schemas.schema_utils import validate_node_config
from src.menu.graph.nodes.multiInpu_action_node import MultiInputActionNode
from src.menu.graph.nodes.valiadtion_gate import ValidationGateNode
from src.menu.graph.nodes.main_menu import MenuNavigationNode
from src.menu.graph.nodes.single_input_action_node import SingleInputActionNode
from src.menu.graph.nodes.exit_node import ExitNode
from src.menu.graph.schemas.schema_utils import load_schema
import json

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
        if spec is not None and spec.loader is not None:
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

def load_Menu_engine(msisdn: str, config: Dict[str, Any], config_source: str) -> MenuEngine:
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
        
        if "transitions" in node_config:
            for key, target in node_config["transitions"].items():
                node.add_transition(key, target)
        
        # Add on_success and on_failure transitions for validation_gate nodes
        if node_config.get("type") == "validation_gate":
            if "on_success" in node_config and isinstance(node_config["on_success"], dict) and "target_menu" in node_config["on_success"]:
                node.add_transition("success", node_config["on_success"]["target_menu"])
            if "on_failure" in node_config and isinstance(node_config["on_failure"], dict) and "target_menu" in node_config["on_failure"]:
                node.add_transition("failure", node_config["on_failure"]["target_menu"])
    
    if engine.nodes:
        first_node_id = next(iter(engine.nodes.keys()))
        engine.set_current_node(first_node_id)
    
    return engine

if __name__ == "__main__":
    from src.menu.graph.demo_menu_config import config as demo_config
    def interactive_console():
        engine = load_Menu_engine("1000", demo_config, "")
        print(engine.get_current_prompt())
        
        while engine.session_active:
            user_input = input("> ")
            print(engine.process_user_input(user_input))
    
    interactive_console()
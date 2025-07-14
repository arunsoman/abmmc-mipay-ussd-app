import copy
from typing import Dict, Any, Optional
from .menu_engine import load_Menu_engine, MenuEngine
from .single_input_action_node import SingleInputActionNode
from .multiInpu_action_node import MultiInputActionNode
import json

class EngineCache:
    """Manages in-memory static engine cache for low-latency session creation"""
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.static_engine: MenuEngine
        self.config: Dict[str, Any]
        self._build_static_engine()

    def _build_static_engine(self):
        """Preload and assemble static engine at server startup"""
        print("Load engine without MSISDN to serve as a template", end=" ")
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        self.static_engine = load_Menu_engine(msisdn="", config=self.config)
        print("... Done")

    def get_session_engine(self, msisdn: str, session_manager=None) -> MenuEngine:
        """Create session-specific engine from static template"""
        session_engine = copy.deepcopy(self.static_engine)
        for node in session_engine.nodes.values():
            node.msisdn = msisdn
            node.reset_state(msisdn)
            if node.service:
                node.service.setMsisdn(msisdn)
            if isinstance(node, (SingleInputActionNode, MultiInputActionNode)):
                node.initialize_bundle_details()
        if "root_validation_gate" in session_engine.nodes:
            session_engine.set_current_node("root_validation_gate")
        else:
            first_node_id = next(iter(session_engine.nodes.keys()))
            session_engine.set_current_node(first_node_id)
            print(f"Warning: root_validation_gate not found, set {first_node_id} as root")
        return session_engine

# Singleton instance
engine_cache = EngineCache("config/demo_menu_config.json")
import copy
from typing import Dict, Any
from .menu_engine import load_Menu_engine

class EngineCache:
    """Manages in-memory static engine cache for low-latency session creation"""
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.static_engine = None
        self._build_static_engine()

    def _build_static_engine(self):
        """Preload and assemble static engine at server startup"""
        # Load engine without MSISDN to serve as a template
        self.static_engine = load_Menu_engine(msisdn="", config=None, config_source=self.config_path)

    def get_session_engine(self, msisdn: str):
        """Create session-specific engine from static template"""
        # Create a shallow copy of the static engine
        session_engine = copy.copy(self.static_engine)
        # Update MSISDN for the engine and its nodes
        session_engine.msisdn = msisdn
        for node in session_engine.nodes.values():
            node.msisdn = msisdn
            node.reset_state(msisdn)  # Reset node-specific state
        # Ensure the engine starts at the first node
        session_engine.set_current_node(next(iter(session_engine.nodes.keys())))
        return session_engine

# Singleton instance
engine_cache = EngineCache("config/demo_menu_config.json")
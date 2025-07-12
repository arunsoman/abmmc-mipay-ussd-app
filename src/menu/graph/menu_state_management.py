import threading
from typing import Dict, Optional
from cachetools import TTLCache
from .nodes.menu_engine import MenuEngine
from .nodes.engine_cache import engine_cache

class MenuSessionManager:
    """Optimized session manager for USSD menu engines with token storage"""
    __tokens = TTLCache(maxsize=40_000_00, ttl=30*60)
    __tokens_lock = threading.Lock()

    
    def __init__(self, session_timeout_seconds: int = 300, max_sessions: int = 10000):
        """Initialize with TTL cache and thread-safe lock"""
        self.sessions = TTLCache(maxsize=max_sessions, ttl=session_timeout_seconds)
        self.lock = threading.Lock()
        self.session_timeout = session_timeout_seconds
        self.config_mapping: Dict[str, Dict] = {}

    def set_config_mapping(self, config_mapping: Dict[str, Dict]):
        """Set configuration mapping for service codes"""
        with self.lock:
            self.config_mapping = config_mapping

    def get_or_create_session(self, msisdn: str, service_code: str = "", config: Optional[Dict] = None) -> MenuEngine|None:
        """Get or create a session-specific MenuEngine with minimal overhead"""
        session_key = f"{msisdn}:{service_code}"
        with self.lock:
            if session_key in self.sessions:
                return self.sessions[session_key]

            menu_config = config or self.config_mapping.get(service_code, None)
            if not menu_config:
                raise ValueError(f"No config found for service code: {service_code}")

            engine = engine_cache.get_session_engine(msisdn, self)
            self.sessions[session_key] = engine
            return engine

    @staticmethod
    def store_token( msisdn: str, auth_token: str):
        """Store authentication token for the session"""
        session_key = msisdn
        with MenuSessionManager.__tokens_lock:
            MenuSessionManager.__tokens[session_key] = auth_token

    @staticmethod
    def get_token( msisdn: str, service_code: str= '') -> Optional[str]:
        """Retrieve authentication token for the session"""
        session_key = f"{msisdn}:{service_code}"
        with MenuSessionManager.__tokens_lock:
            return MenuSessionManager.__tokens.get(session_key)

    def get_session(self, msisdn: str, service_code: str = "") -> Optional[MenuEngine]:
        """Retrieve an existing session or return None"""
        session_key = f"{msisdn}:{service_code}"
        with self.lock:
            return self.sessions.get(session_key)

    def end_session(self, msisdn: str, service_code: str = ""):
        """End a session and remove it from cache"""
        session_key = f"{msisdn}:{service_code}"
        with self.lock:
            self.sessions.pop(session_key, None)

    def update_activity(self, msisdn: str, service_code: str = ""):
        """Update session activity to refresh TTL"""
        session_key = f"{msisdn}:{service_code}"
        with self.lock:
            if session_key in self.sessions:
                _ = self.sessions[session_key]
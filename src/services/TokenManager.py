from typing import Optional
from cachetools import TTLCache
import threading

class TokenManager:
    """Manages authentication tokens for USSD sessions."""
    __tokens = TTLCache(maxsize=40_000_00, ttl=3*60)
    __tokens_lock = threading.Lock()

    @staticmethod
    def store_token(msisdn: str, auth_token: str):
        """Store authentication token for the session."""
        session_key = msisdn
        with TokenManager.__tokens_lock:
            TokenManager.__tokens[session_key] = auth_token

    @staticmethod
    def get_token(msisdn: str, service_code: str = '') -> Optional[str]:
        """Retrieve authentication token for the session."""
        session_key = f"{msisdn}:{service_code}"
        with TokenManager.__tokens_lock:
            return TokenManager.__tokens.get(session_key)
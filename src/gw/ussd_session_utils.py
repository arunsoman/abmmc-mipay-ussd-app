import time
from threading import Lock
from typing import Any, Dict, Optional

class USSDSession:
    """Represents a USSD session for a specific MSISDN following AWCC specs."""
    
    def __init__(self, msisdn: str, session_id: str, service_code: str):
        """
        Initialize a USSD session according to AWCC specifications:
        - msisdn: Subscriber's phone number
        - session_id: Unique session identifier
        - service_code: USSD service code (e.g., *222#)
        """
        self.msisdn = msisdn
        self.session_id = session_id
        self.service_code = service_code
        self.start_time = time.time()
        self.last_activity = self.start_time
        self.current_state = None  # Current state in the USSD flow
        self.user_data = {}  # Stores collected user responses
        self.session_data = {}  # Additional session metadata
        self.is_new_session = True
        self.encoding = "gsm-7"  # Default encoding per AWCC
        self.language = "en"  # Default language
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()
        
    def is_expired(self, timeout=120) -> bool:
        """Check if session has expired (AWCC timeout typically 120 seconds)"""
        return (time.time() - self.last_activity) > timeout
        
    def store_response(self, key: str, value: str):
        """Store user response with validation tracking"""
        self.user_data[key] = {
            "value": value,
            "timestamp": time.time(),
            "validated": False
        }
        
    def validate_response(self, key: str):
        """Mark response as validated"""
        if key in self.user_data:
            self.user_data[key]["validated"] = True
            
    def get_response(self, key: str) -> Optional[str]:
        """Get stored response value"""
        return self.user_data.get(key, {}).get("value")

class USSDSessionManager:
    """Manages USSD sessions with thread safety and AWCC compliance."""
    
    def __init__(self, session_timeout=300000000):
        self.sessions: Dict[str, USSDSession] = {}
        self.lock = Lock()
        self.session_timeout = session_timeout  # AWCC standard timeout
        
    def create_session(
        self,
        msisdn: str,
        session_id: str,
        service_code: str,
        initial_state: Any
    ) -> USSDSession:
        """Create a new USSD session per AWCC specifications"""
        with self.lock:
            # Terminate any existing session for this MSISDN
            if msisdn in self.sessions:
                del self.sessions[msisdn]
            
            # Create new session
            session = USSDSession(msisdn, session_id, service_code)
            session.current_state = initial_state
            self.sessions[msisdn] = session
            return session
        
    def get_session(self, msisdn: str) -> Optional[USSDSession]:
        with self.lock:
            session = self.sessions.get(msisdn)
            if session and session.is_expired(self.session_timeout):
                del self.sessions[msisdn]
                return None
            return session
        
    def update_session_state(
        self,
        session: USSDSession,
        new_state: Any,
        user_input: Optional[str] = None,
        response_key: Optional[str] = None
    ):
        """Update session state with AWCC-compliant activity tracking"""
        with self.lock:
            session.update_activity()
            session.current_state = new_state
            session.is_new_session = False
            
            if user_input and response_key:
                session.store_response(response_key, user_input)
    
    def end_session(self, session: USSDSession):
        """Properly terminate a USSD session per AWCC specs"""
        with self.lock:
            if session.msisdn in self.sessions:
                del self.sessions[session.msisdn]
                
    def cleanup_sessions(self, msisdn: str):
        """Clean up expired session for a given MSISDN"""
        with self.lock:
            session = self.sessions.get(msisdn)
            if session and session.is_expired(self.session_timeout):
                del self.sessions[msisdn]
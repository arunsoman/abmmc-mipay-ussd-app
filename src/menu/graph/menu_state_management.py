from typing import Dict, Any, Optional
import threading
import time
from datetime import datetime, timedelta
from src.menu.graph.all_node import MenuEngine, load_Menu_engine

class MenuSessionManager:
    def __init__(self, session_timeout_minutes: int = 500000):
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.sessions = {}  # msisdn -> {'engine': MenuEngine, 'config': Dict, 'last_activity': datetime}
        self.lock = threading.Lock()
        self.cleanup_thread = None
        self.running = True
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self.cleanup_thread.start()
        print("Session cleanup thread started")

    def _cleanup_expired_sessions(self):
        while self.running:
            try:
                with self.lock:
                    current_time = datetime.now()
                    expired_msisdns = [
                        msisdn for msisdn, session_data in self.sessions.items()
                        if current_time - session_data['last_activity'] > self.session_timeout
                    ]
                    for msisdn in expired_msisdns:
                        self.sessions[msisdn]['engine'] = None
                        del self.sessions[msisdn]
                        print(f"Session expired for MSISDN: {msisdn}")
                time.sleep(30)
            except Exception as e:
                print(f"Error in cleanup thread: {e}")

    def get_or_create_session(self, msisdn: str, config: Optional[Dict] = None) -> MenuEngine:
        with self.lock:
            current_time = datetime.now()
            if msisdn in self.sessions:
                session_data = self.sessions[msisdn]
                session_data['last_activity'] = current_time
                return session_data['engine']
            else:
                if config is None:
                    raise ValueError("Config required for new session")
                engine = load_Menu_engine(msisdn, config)
                self.sessions[msisdn] = {
                    'engine': engine,
                    'config': config,
                    'last_activity': current_time
                }
                print(f"New session created for MSISDN: {msisdn}")
                return engine

    def process_user_input(self, msisdn: str, user_input: str) -> Dict[str, Any]:
        engine = self.get_or_create_session(msisdn)
        with self.lock:
            if msisdn in self.sessions:
                self.sessions[msisdn]['last_activity'] = datetime.now()
        response = engine.process_user_input(user_input)
        if not engine.session_active:
            print(f"Session ended for MSISDN: {msisdn}")
            self.end_session(msisdn)
            return {'text': "Session ended. Thank you for using our service.", 'end_session': True}
        return {'text': response, 'end_session': not engine.session_active or response == "0"}

    def get_initial_prompt(self, msisdn: str) -> str:
        engine = self.get_or_create_session(msisdn)
        return engine.get_current_prompt()

    def end_session(self, msisdn: str):
        with self.lock:
            if msisdn in self.sessions:
                del self.sessions[msisdn]
                print(f"Session ended for MSISDN: {msisdn}")

    def get_active_sessions(self) -> Dict[str, datetime]:
        with self.lock:
            return {msisdn: data['last_activity'] for msisdn, data in self.sessions.items()}

    def shutdown(self):
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join()
        with self.lock:
            self.sessions.clear()
        print("Session manager shutdown complete")
from typing import Dict, Any, Optional
from .node_abc import MenuNode
import logging
import requests
from src.menu.graph.menu_state_management import MenuSessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationGateNode(MenuNode):
    """Node for PIN validation with cached prompt and token handling"""
    __slots__ = ('max_attempts', 'current_attempts', 'valid_pin', 'validation_url', 'prompt', 'cached_prompt', 'on_success', 'on_failure')

    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.max_attempts = config.get("max_attempts", 3)
        self.current_attempts = 0
        self.valid_pin = config.get("valid_pin", "123456")
        self.validation_url = config.get("validation_url")
        self.prompt = config.get("prompt", "Enter your PIN:\n")
        self.cached_prompt = self.prompt
        self.on_success = config.get("on_success", {})
        self.on_failure = config.get("on_failure", {})

    def reset_state(self, msisdn: str):
        """Reset node state for a new session"""
        super().reset_state(msisdn)
        self.current_attempts = 0
        self.validation_error = ""
        self.cached_prompt = self.prompt

    def getNext(self) -> str:
        """Return cached prompt with validation error if present"""
        error_msg = f"\n{self.validation_error}" if self.validation_error else ""
        return self.cached_prompt + error_msg

    def getPrevious(self) -> str:
        """Return cached prompt as fallback"""
        return self.cached_prompt

    def handleUserInput(self, user_input: str) -> str:
        """Validate PIN, store token, and transition to next node"""
        self.current_attempts += 1

        # Validate PIN
        if self.validation_url:
            payload = {"password": user_input, "username": self.msisdn}
            logger.info(f"Using validation service: {self.validation_url}")
            response = self.make_post_request(payload)
            logger.info(f"Service response: {response}")
            if response and self.engine and response.get("auth_token", None):
                MenuSessionManager.store_token(self.msisdn,  response.get("auth_token", None))
                target_node = self.on_success.get("target_menu", "main_menu")
                self.engine.set_current_node(target_node)
                return self.engine.get_current_prompt()
            else:
                self.validation_error = "Some error"

        # Check max attempts
        if self.current_attempts >= self.max_attempts and self.engine:
            target_node = self.on_failure.get("target_menu", "exit_node")
            self.engine.set_current_node(target_node)
            self.engine.session_active = False
            return self.engine.get_current_prompt()

        return self.getNext()
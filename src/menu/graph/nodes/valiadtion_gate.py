from typing import Dict, Any, Optional
from .node_abc import MenuNode
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationGateNode(MenuNode):
    """Node for PIN validation with cached prompt and efficient input handling"""
    __slots__ = ('max_attempts', 'current_attempts', 'valid_pin', 'validation_url', 'prompt', 'cached_prompt', 'on_success', 'on_failure')

    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.max_attempts = config.get("max_attempts", 3)
        self.current_attempts = 0
        self.valid_pin = config.get("valid_pin")
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
        """Validate PIN via service or local check and transition to next node"""
        self.current_attempts += 1
        logger.info(f"Validating input for {self.msisdn} at node {self.node_id}, attempt {self.current_attempts}")

        if self.validation_url:
            logger.info(f"Using validation service: {self.validation_url}")
            payload = {"msisdn": self.msisdn, "pin": user_input}
            response = self.make_post_request(payload)
            logger.info(f"Service response: {response}")
            if response and response.get("valid", False):
                target_node = self.on_success.get("target_menu", "main_menu")
                logger.info(f"Validation successful, transitioning to {target_node}")
                self.engine.set_current_node(target_node)
                return self.engine.get_current_prompt()
            else:
                self.validation_error = "Invalid PIN"
                logger.warning(f"Validation failed: {self.validation_error}")
        elif self.valid_pin and user_input == self.valid_pin:
            target_node = self.on_success.get("target_menu", "main_menu")
            logger.info(f"Local validation successful, transitioning to {target_node}")
            self.engine.set_current_node(target_node)
            return self.engine.get_current_prompt()
        else:
            self.validation_error = "Invalid PIN"
            logger.warning(f"Local validation failed: {self.validation_error}")

        if self.current_attempts >= self.max_attempts:
            target_node = self.on_failure.get("target_menu", "exit_node")
            logger.info(f"Max attempts reached, transitioning to {target_node}")
            self.engine.set_current_node(target_node)
            self.engine.session_active = False
            return self.engine.get_current_prompt()

        return self.getNext()
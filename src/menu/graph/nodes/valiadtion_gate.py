from typing import Dict, Any, Optional, cast
from src.menu.graph.nodes.node_abc import MenuNode
import logging
import requests
from src.services.ValidationApi import Validate
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
    
    def getPrevious(self) -> str:
        return super().getPrevious()
    
    def getNext(self) -> str:
        if self.validation_error:
            return self.validation_error
        return self.config.get("prompt", "")

    def handleUserInput(self, user_input: str) -> str:
        self.validation_error = ""
        self.current_attempts += 1
        if self.validation_url:
            try:
                payload = {"password": user_input, "username": self.msisdn}
                cast(Validate, self.service).setMsisdn(self.msisdn)
                response = self.service.doPost(payload, self.msisdn)
                logger.info(f"Validation response for PIN {user_input}: {response}")
                if response:
                    target_node_id = self.next_nodes.get("success")
                    if target_node_id and self.engine:
                        self.engine.navigation_stack.append(self.node_id)
                        self.engine.set_current_node(target_node_id)
                        return self.engine.get_current_prompt()
                    self.validation_error = "Invalid success node configuration"
                else:
                    self.validation_error = response.get("error", "Invalid PIN") if isinstance(response, dict) else "Invalid PIN"
            except requests.RequestException as e:
                self.validation_error = f"Validation error: {str(e)}"
        else:
            self.validation_error = "Validation URL not configured"
        
        if self.current_attempts >= self.max_attempts:
            target_node_id = self.next_nodes.get("failure", "exit_node")
            if target_node_id and self.engine:
                self.engine.navigation_stack.append(self.node_id)
                self.engine.set_current_node(target_node_id)
                return self.engine.get_current_prompt()
        return self.getNext()
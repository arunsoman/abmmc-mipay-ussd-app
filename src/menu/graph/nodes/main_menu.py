from typing import Any
from src.menu.graph.nodes.node_abc import MenuNode
from .global_share import service_config
from typing import Dict, Any
from src.menu.graph.nodes.node_abc import MenuNode
from .global_share import service_config
import logging

logger = logging.getLogger(__name__)

class MenuNavigationNode(MenuNode):
    def __init__(self, node_id: str, config: dict):
        super().__init__(node_id, config)
        self.prompt = config.get("prompt", "Select an option:\n")
        self.options = config.get("options", [])
        self.max_invalid_attempts = config.get("max_invalid_attempts", 3)
        self.invalid_attempts = 0
        self.validation_error = ""
        # Log configuration details
        logger.info(f"Initialized MenuNavigationNode {node_id} with prompt: {self.prompt}")
        logger.info(f"Options: {self.options}")
        logger.info(f"Max invalid attempts: {self.max_invalid_attempts}")
        logger.info(f"Transitions: {self.next_nodes}")

    def getNext(self) -> str:
        if self.validation_error:
            logger.warning(f"Validation error for node {self.node_id}: {self.validation_error}")
            return self.validation_error
        if not self.options:
            logger.error(f"No options defined for node {self.node_id}")
            return self.prompt + "No options available\n"
        prompt = self.prompt
        for option in self.options:
            if not isinstance(option, dict) or "key" not in option or "label" not in option:
                logger.error(f"Invalid option format in node {self.node_id}: {option}")
                continue
            prompt += f"{option['key']}. {option['label']}\n"
        logger.debug(f"Generated prompt for node {self.node_id}: {prompt}")
        return prompt

    def getPrevious(self) -> str:
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            if previous_node_id in self.engine.nodes:
                logger.info(f"Returning prompt for previous node {previous_node_id} from {self.node_id}")
                return self.engine.nodes[previous_node_id].getNext()
        logger.warning(f"No previous node for {self.node_id}")
        return "No previous node available"

    def handleUserInput(self, user_input: str) -> str:
        self.validation_error = ""
        if user_input in self.next_nodes:
            target_node_id = self.next_nodes[user_input]
            if self.engine:
                self.engine.navigation_stack.append(self.node_id)
                self.engine.set_current_node(target_node_id)
                logger.info(f"Transition from {self.node_id} to {target_node_id} via transition {user_input}")
                return self.engine.get_current_prompt()
        for option in self.options:
            if user_input == option["key"]:
                target_node_id = option["target_menu"]
                if self.engine:
                    self.engine.navigation_stack.append(self.node_id)
                    self.engine.set_current_node(target_node_id)
                    service_config.setdefault(self.msisdn, {})["selected_menu_option"] = user_input
                    logger.info(f"Transition from {self.node_id} to {target_node_id} via option {user_input}")
                    return self.engine.get_current_prompt()
        self.invalid_attempts += 1
        if self.invalid_attempts >= self.max_invalid_attempts:
            if "invalid" in self.next_nodes:
                self.engine.set_current_node(self.next_nodes["invalid"])
                logger.info(f"Max invalid attempts reached for {self.node_id}, transitioning to {self.next_nodes['invalid']}")
                return self.engine.get_current_prompt()
            logger.error(f"Max invalid attempts reached for {self.node_id}, ending session")
            return "Max invalid attempts reached. Session ended."
        self.validation_error = "Invalid selection, please try again."
        logger.warning(f"Invalid input {user_input} for {self.node_id}, attempts: {self.invalid_attempts}")
        return self.getNext()
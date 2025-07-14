from typing import Any, Dict, List
from src.menu.graph.nodes.node_abc import MenuNode
from .global_share import service_config
import logging
import re

logger = logging.getLogger(__name__)

class MultiInputActionNode(MenuNode):
    def __init__(self, node_id: str, config: dict):
        super().__init__(node_id, config)
        self.steps: List[Dict[str, Any]] = config.get("steps", [])
        self.input_keys: List[str] = [step["input_key"] for step in self.steps]
        self.prompts: List[str] = [step["prompt"] for step in self.steps]
        self.validations: Dict[str, Dict[str, Any]] = {step["input_key"]: step.get("validation", {}) for step in self.steps}
        self.confirmation_prompt: str = config.get("confirmation_prompt", "")
        self.state = "input" if self.steps else "complete"
        self.inputs: Dict[str, str] = {}
        self.current_input_index = 0
        self.validation_error = ""
        self.bundle_mapping_key = config.get("bundle_mapping_key")
        self.bundle_details: Dict[str, Any] = {}
        logger.info(f"Initialized MultiInputActionNode {node_id} with {len(self.steps)} steps, confirmation_prompt: {self.confirmation_prompt}")

    def initialize_bundle_details(self) -> None:
        if not self.bundle_mapping_key or not self.engine:
            self.bundle_details = {}
            logger.warning(f"No bundle_mapping_key or engine for node {self.node_id}")
            return
        selected_option = service_config.get(self.msisdn, {}).get("selected_bundle_option")
        bundle_mapping = self.engine.config.get("bundle_mapping", {}).get(self.bundle_mapping_key, {})
        if not selected_option or selected_option not in bundle_mapping:
            self.validation_error = "Error: Invalid bundle selection"
            self.bundle_details = {}
            logger.error(f"Invalid bundle selection for node {self.node_id}: selected_option={selected_option}")
        else:
            self.bundle_details = bundle_mapping.get(selected_option, {})
            logger.info(f"Bundle details for node {self.node_id}: {self.bundle_details}")

    def getNext(self) -> str:
        if self.validation_error:
            logger.warning(f"Validation error for node {self.node_id}: {self.validation_error}")
            return self.validation_error
        if self.state == "input" and self.current_input_index < len(self.steps):
            prompt = self.prompts[self.current_input_index]
            try:
                formatted_prompt = prompt.format(**self.bundle_details, **self.inputs)
                logger.debug(f"Generated prompt for node {self.node_id}, step {self.current_input_index}: {formatted_prompt}")
                return formatted_prompt
            except KeyError as e:
                logger.error(f"Prompt formatting error for node {self.node_id}: {str(e)}")
                return "Invalid prompt configuration"
        elif self.state == "confirm" and self.confirmation_prompt:
            try:
                formatted_prompt = self.confirmation_prompt.format(**self.bundle_details, **self.inputs)
                logger.debug(f"Generated confirmation prompt for node {self.node_id}: {formatted_prompt}")
                return formatted_prompt
            except KeyError as e:
                logger.error(f"Confirmation prompt formatting error for node {self.node_id}: {str(e)}")
                return "Invalid confirmation prompt configuration"
        elif self.state == "complete":
            prompt = self.validation_error or self.config.get("success_prompt", "").format(**self.bundle_details, **self.inputs)
            logger.debug(f"Generated success prompt for node {self.node_id}: {prompt}")
            return prompt
        logger.warning(f"Invalid state for node {self.node_id}: {self.state}")
        return "No prompt available"

    def getPrevious(self) -> str:
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            if previous_node_id in self.engine.nodes:
                logger.info(f"Returning prompt for previous node {previous_node_id} from {self.node_id}")
                return self.engine.nodes[previous_node_id].getNext()
        logger.warning(f"No previous node for {self.node_id}")
        return "No previous node available"

    def validateInput(self, user_input: str, input_key: str) -> bool:
        validation = self.validations.get(input_key, {})
        if "regex" in validation:
            result = bool(re.match(validation["regex"], user_input))
            logger.debug(f"Input validation for node {self.node_id}, key {input_key}, input: {user_input}, result: {result}")
            return result
        logger.debug(f"No regex validation for node {self.node_id}, key {input_key}, input: {user_input}")
        return True

    def parseResponse(self, response_data: Any) -> Any:
        if response_data and isinstance(response_data, dict):
            if response_data.get("status"):
                result = {**{"receipt_number": "N/A", "error_message": "Unknown error"}, **response_data}
                logger.info(f"Parsed response for node {self.node_id}: {result}")
                return result
            error_message = response_data.get("error", "Unknown error")
            if "error_prompt" in self.config:
                try:
                    error_message = self.config["error_prompt"].format(error_message=error_message, **self.bundle_details, **self.inputs)
                except KeyError:
                    logger.warning(f"Error prompt formatting failed for node {self.node_id}, using default: {error_message}")
            self.validation_error = error_message
            logger.error(f"Response error for node {self.node_id}: {self.validation_error}")
        else:
            error_message = "Invalid response"
            if "error_prompt" in self.config:
                try:
                    error_message = self.config["error_prompt"].format(error_message=error_message, **self.bundle_details, **self.inputs)
                except KeyError:
                    logger.warning(f"Error prompt formatting failed for node {self.node_id}, using default: {error_message}")
            self.validation_error = error_message
            logger.error(f"Invalid response for node {self.node_id}: {response_data}")
        return None

    def handleUserInput(self, user_input: str) -> str:
        logger.debug(f"Handling user input for node {self.node_id}: {user_input}, state: {self.state}, index: {self.current_input_index}")
        self.validation_error = ""
        if self.state == "input" and self.current_input_index < len(self.steps):
            current_key = self.input_keys[self.current_input_index]
            if self.validateInput(user_input, current_key):
                self.inputs[current_key] = user_input
                if current_key == "confirm_pin" and self.inputs.get("new_pin") != user_input:
                    self.validation_error = "New PIN and confirmation do not match"
                    logger.warning(f"Validation failed for node {self.node_id}: {self.validation_error}")
                    return self.getNext()
                self.current_input_index += 1
                if self.current_input_index >= len(self.steps):
                    if self.confirmation_prompt:
                        self.state = "confirm"
                        logger.info(f"Transition to confirm state for node {self.node_id}")
                    else:
                        self.state = "complete"
                        logger.info(f"Transition to complete state for node {self.node_id}")
                        return self._execute_action()
                return self.getNext()
            else:
                self.validation_error = self.validations.get(current_key, {}).get("validation_error", "Invalid input")
                logger.warning(f"Invalid input for node {self.node_id}, key {current_key}: {user_input}, error: {self.validation_error}")
                return self.getNext()
        elif self.state == "confirm":
            if user_input == "1":  # OK
                self.state = "complete"
                logger.info(f"Confirmed action for node {self.node_id}")
                return self._execute_action()
            elif user_input == "2":  # Cancel
                self.state = "input"
                self.current_input_index = 0
                self.inputs = {}
                logger.info(f"Cancelled action for node {self.node_id}, resetting to input state")
                return self.getNext()
            else:
                self.validation_error = "Invalid selection, please enter 1 (OK) or 2 (Cancel)"
                logger.warning(f"Invalid confirmation input for node {self.node_id}: {user_input}")
                return self.getNext()
        logger.warning(f"Invalid state for input handling in node {self.node_id}: {self.state}")
        return self.getNext()

    def _execute_action(self) -> str:
        format_context = {**self.bundle_details, **self.inputs, 'msisdn': self.msisdn}
        payload = {           
            **self.inputs,
            **{k: v.format(**format_context) if isinstance(v, str) else v 
            for k, v in self.config.get("params", {}).items()}
        }   
        logger.debug(f"Sending payload for node {self.node_id}: {payload}")
        response = self.make_post_request(payload)
        response_data = self.parseResponse(response)
        if response_data:
            prompt = self.config.get("success_prompt", "").format(**response_data, **self.bundle_details, **self.inputs)
            logger.info(f"Success prompt for node {self.node_id}: {prompt}")
            return prompt
        logger.warning(f"Validation error after response for node {self.node_id}: {self.validation_error}")
        return self.validation_error
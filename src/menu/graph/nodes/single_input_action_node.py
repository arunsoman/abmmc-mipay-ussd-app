from typing import Any, Dict
from src.menu.graph.nodes.node_abc import MenuNode
from .global_share import service_config

class SingleInputActionNode(MenuNode):
    def __init__(self, node_id: str, config: dict):
        super().__init__(node_id, config)
        self.input_key = config.get("input_key")
        self.validation = config.get("validation", {})
        self.state = "input"
        self.input = ""
        self.validation_error = ""
        self.bundle_mapping_key = config.get("bundle_mapping_key")
        self.bundle_details: Dict[str, Any] = {}

    def initialize_bundle_details(self) -> None:
        if not self.bundle_mapping_key or not self.engine:
            self.bundle_details = {}
            print(f" 000 -No bundle_mapping_key or engine for node {self.node_id}")
            return
        selected_option = service_config.get(self.msisdn, {}).get("selected_bundle_option")
        if not selected_option:
            self.validation_error = "Error: No bundle option selected"
            print(f"------XXXXX--------- No selected_bundle_option for msisdn {self.msisdn} in node {self.node_id}")
            return
        bundle_mapping = self.engine.config.get("bundle_mapping", {}).get(self.bundle_mapping_key, {})
        if selected_option not in bundle_mapping:
            self.validation_error = f"Error: Invalid bundle option {selected_option} for {self.bundle_mapping_key}"
            print(f"--------- Invalid bundle option \
                {selected_option} for {self.bundle_mapping_key} in node {self.node_id},\
                    available: {list(bundle_mapping.keys())}")
            self.bundle_details = {}
        else:
            self.bundle_details = bundle_mapping.get(selected_option, {})
            print(f"Bundle details for node {self.node_id}: {self.bundle_details}")
            """Initialize bundle details after engine is set."""
            if not self.bundle_mapping_key or not self.engine:
                self.bundle_details = {}
                return
            selected_option = service_config.get(self.msisdn, {}).get("selected_bundle_option")
            bundle_mapping = self.engine.config.get("bundle_mapping", {}).get(self.bundle_mapping_key, {})
            if not selected_option or selected_option not in bundle_mapping:
                self.validation_error = "Error: Invalid bundle selection"
                self.bundle_details = {}
            else:
                self.bundle_details = bundle_mapping.get(selected_option, {})

    def getNext(self) -> str:
        if self.validation_error:
            return self.validation_error
        if self.state == "input":
            return self.config.get("prompt", "").format(**self.bundle_details)
        elif self.state == "complete":
            return self.validation_error or self.config.get("success_prompt", "").format(**self.bundle_details)
        return ""

    def getPrevious(self) -> str:
        """Get the prompt of the previous node or a fallback message."""
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            if previous_node_id in self.engine.nodes:
                return self.engine.nodes[previous_node_id].getNext()
        return "No previous node available"

    def validateInput(self, user_input: str) -> bool:
        if "regex" in self.validation:
            import re
            return bool(re.match(self.validation["regex"], user_input))
        return True

    def parseResponse(self, response_data: Any) -> Any:
        if response_data and isinstance(response_data, dict):
            if response_data.get("status"):
                return {**{"receipt_number": "N/A", "error_message": "Unknown error"}, **response_data}
            self.validation_error = self.config.get("error_prompt", "Action failed: {error_message}").format(
                error_message=response_data.get("error", "Invalid response"), **self.bundle_details
            )
        else:
            self.validation_error = self.config.get("error_prompt", "Action failed: Invalid response").format(
                error_message="Invalid response", **self.bundle_details
            )
        return None

    def handleUserInput(self, user_input: str) -> str:
        self.validation_error = ""
        if self.state == "input":
            if self.validateInput(user_input):
                self.input = user_input
                self.state = "complete"
                payload = {
                    "msisdn": self.msisdn,
                    self.input_key: user_input,
                    **{k: v.format(**self.bundle_details) if isinstance(v, str) else v for k, v in self.config.get("params", {}).items()}
                }
                response = self.make_post_request(payload)
                response_data = self.parseResponse(response)
                if response_data:
                    return self.config.get("success_prompt", "").format(**response_data, **self.bundle_details)
                return self.validation_error
            else:
                self.validation_error = self.config.get("validation_error", "Invalid input")
        return self.getNext()
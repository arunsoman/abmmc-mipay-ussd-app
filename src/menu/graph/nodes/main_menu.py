from typing import Dict, Any
from src.menu.graph.nodes.node_abc import MenuNode

class MenuNavigationNode(MenuNode):
    """Node for main menu or sub-menu navigation, linking to other nodes."""
    def __init__(self, node_id: str, config: Dict[str, Any]):
        super().__init__(node_id, config)
        self.prompt = config.get("prompt", "Select an option:\n")
        self.options = config.get("options", [])
        self.valid_keys = {option["key"] for option in self.options} | {"9", "0"}

    def getNext(self) -> str:
        """Generate the menu prompt with options and validation error if any."""
        options_text = "\n".join([f"{opt['key']}. {opt['label']}" for opt in self.options])
        navigation_text = "\n9. Back\n0. Exit"
        error_msg = f"\n{self.validation_error}" if self.validation_error else ""
        return f"{self.prompt}\n{options_text}{navigation_text}{error_msg}"

    def getPrevious(self) -> str:
        """Return the prompt of the previous node or a fallback message."""
        if self.engine and self.engine.navigation_stack:
            previous_node_id = self.engine.navigation_stack[-1]
            previous_node = self.engine.nodes.get(previous_node_id)
            if previous_node:
                return previous_node.getNext()
        return "No previous menu\nPress 0 to exit"

    def handleUserInput(self, user_input: str) -> str:
        """Process user input and transition to the selected node."""
        self.validation_error = ""

        if user_input in self.valid_keys:
            if user_input == "9":
                if self.engine and self.engine.navigation_stack:
                    target_node_id = self.engine.navigation_stack.pop()
                    self.engine.set_current_node(target_node_id)
                    return self.engine.get_current_prompt()
                return "No previous menu\nPress 0 to exit"
            elif user_input == "0":
                if self.engine:
                    self.engine.set_current_node("exit_node")
                    return self.engine.get_current_prompt()
                return "Session ended"
            else:
                target_node_id = next((opt["target_menu"] for opt in self.options if opt["key"] == user_input), None)
                if target_node_id and self.engine:
                    self.engine.navigation_stack.append(self.node_id)
                    self.engine.set_current_node(target_node_id)
                    return self.engine.get_current_prompt()
        else:
            self.validation_error = f"Invalid selection. Choose from {', '.join(sorted(self.valid_keys))}"

        return self.getNext()
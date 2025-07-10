from typing import Dict, Any, Optional, List
import re
import requests
import json
import os
from jsonschema import validate, ValidationError

# Schema registry
schema_utils_SCHEMA_REGISTRY = {
    "multi_input_action": "schemas/multi_input_action.json",
    "exit": "schemas/exit.json",
    "single_input_action": "schemas/SingleInputActionNode.json",
    "menu_navigation": "schemas/MenuNavigationNode.json",
    "validation_gate": "schemas/ValidationGateNode.json",
}

# Cache for loaded schemas
SCHEMA_CACHE = {}

def load_schema(node_type: str) -> Dict[str, Any]:
    """Load a JSON schema from file and cache it."""
    if node_type not in schema_utils_SCHEMA_REGISTRY:
        raise ValueError(f"No schema defined for node type: {node_type}")
    
    if node_type not in SCHEMA_CACHE:
        schema_path = os.path.join(os.path.dirname(__file__), '..', schema_utils_SCHEMA_REGISTRY[node_type])
        try:
            with open(schema_path, 'r') as f:
                SCHEMA_CACHE[node_type] = json.load(f)
        except FileNotFoundError:
            pass
            # raise FileNotFoundError(f"Schema file not found: {schema_path}")
        # except json.JSONDecodeError as e:
            # raise ValueError(f"Invalid JSON in schema {schema_path}: {str(e)}")
    
    return SCHEMA_CACHE[node_type]

def validate_node_config(node_id: str, node_config: Dict[str, Any]):
    """Validate a node configuration against its schema."""
    node_type = node_config.get("type")
    if not node_type:
        raise ValueError(f"Node {node_id} is missing 'type' in configuration")
    
    schema = load_schema(node_type)
    try:
        validate(instance=node_config, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Validation error for node {node_id}: {str(e)}")

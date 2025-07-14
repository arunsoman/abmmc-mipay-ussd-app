from typing import Dict, Any, Optional, List
import threading
import re
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
    "cache_post":"schemas/msisdn_menu.json"
}

# Cache for loaded schemas
SCHEMA_CACHE = {}
from functools import lru_cache

@lru_cache(maxsize=128)
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
            pass  # Consider logging or re-raising here
    
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
    

def load_config_from_source(source: str) -> Dict[str, Any]:
    """Load configuration from various sources (Python module, JSON file, or URL)."""
    import importlib.util
    import requests
    
    if source.endswith(".py"):
        spec = importlib.util.spec_from_file_location("config_module", source)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, "config", {})
    
    elif source.endswith(".json"):
        with open(source, 'r') as f:
            return json.load(f)
    
    elif source.startswith(("http://", "https://")):
        try:
            response = requests.get(source, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Failed to load config from URL {source}: {str(e)}")
    
    raise ValueError(f"Unsupported config source: {source}")


# Global cache for validated configuration
CONFIG_CACHE = {}
CONFIG_CACHE_LOCK = threading.Lock()  # Thread-safe lock for cache access

def get_validated_config(config_source: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Retrieve or validate and cache the configuration."""
    global CONFIG_CACHE
    with CONFIG_CACHE_LOCK:
        # Check if config is already cached for the given source
        if config_source in CONFIG_CACHE:
            return CONFIG_CACHE[config_source]
        
        # Load and validate configuration if not cached
        if config_source and not config:
            config = load_config_from_source(config_source)
        
        if not config:
            raise ValueError("No configuration provided")
        
        # Validate all nodes in the configuration
        # for node_id, node_config in config.items():
        #     try:
        #         validate_node_config(node_id, node_config)
        #     except ValueError as e:
        #         print(f"Skipping node {node_id}: {str(e)}")
        #         continue
        
        # Cache the validated configuration
        CONFIG_CACHE[config_source] = config
        return config
import os 
import yaml 
from pathlib import Path 
from typing import Any, Dict, List, Optional 

# Function to load a YAML file and return its content as a dictionary.
def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file) 
    
# Function to return the environment variable value
def get_active_environment(config: Dict[str, Any]) -> str:
    return config.get("environment")

# Function to get the environment configuration.
def get_environment_config(config: Dict[str, Any]) -> Dict[str, Any]:
    env = get_active_environment(config)
    if env not in config:
        raise ValueError(f"Environment '{env}' not found in the configuration.")
    return config[env] 

# Function to extract the endpoints from the configuration.
def get_endpoints(config: Dict[str, Any]) -> List[str]:
    env_config = get_environment_config(config)
    endpoints = env_config.get('endpoints', [])
    if not isinstance(endpoints, list):
        raise ValueError("Endpoints should be a list.")
    return endpoints 


"""YAML loading utilities."""

from typing import Any, Dict
from pathlib import Path
import yaml


def load_yaml(file_path: Path) -> Dict[str, Any]:
    """
    Load and parse a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Parsed YAML content as dictionary
        
    Raises:
        yaml.YAMLError: If YAML is invalid
        FileNotFoundError: If file doesn't exist
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) 
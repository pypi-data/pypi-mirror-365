"""Schema loading and parsing functionality."""

from typing import Any, Dict, Optional, Union, List
from pathlib import Path
import yaml


class SchemaError(Exception):
    """Raised when there's an error loading or parsing a schema."""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.file_path = file_path


def load_schema(schema_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a YAML schema file.
    
    Args:
        schema_path: Path to the YAML schema file
        
    Returns:
        Parsed schema dictionary
        
    Raises:
        SchemaError: If file cannot be loaded or parsed
    """
    try:
        schema_path = Path(schema_path)
        
        if not schema_path.exists():
            raise SchemaError(
                f"Schema file not found: {schema_path}",
                str(schema_path)
            )
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = yaml.safe_load(f)
        
        if not isinstance(schema, dict):
            raise SchemaError(
                f"Schema must be a dictionary, got {type(schema).__name__}",
                str(schema_path)
            )
        
        # Process rule bundles if present
        if "rules" in schema:
            schema["rules"] = _process_rule_bundles(schema["rules"], schema_path)
        
        return schema
        
    except yaml.YAMLError as e:
        raise SchemaError(
            f"Invalid YAML in schema file: {str(e)}",
            str(schema_path)
        )
    except Exception as e:
        raise SchemaError(
            f"Error loading schema file: {str(e)}",
            str(schema_path)
        )


def _process_rule_bundles(rules: List[Dict[str, Any]], base_path: Path) -> List[Dict[str, Any]]:
    """
    Process rule bundles by expanding include statements.
    
    Args:
        rules: List of rule dictionaries
        base_path: Path to the base schema file
        
    Returns:
        Expanded list of rules with bundles included
    """
    expanded_rules = []
    
    for rule in rules:
        # Check if this is an include statement
        if "include" in rule:
            include_path = rule["include"]
            bundle_rules = _load_rule_bundle(include_path, base_path)
            expanded_rules.extend(bundle_rules)
        else:
            expanded_rules.append(rule)
    
    return expanded_rules


def _load_rule_bundle(include_path: str, base_path: Path) -> List[Dict[str, Any]]:
    """
    Load rules from a bundle file.
    
    Args:
        include_path: Path to the bundle file (relative to base_path)
        base_path: Path to the base schema file
        
    Returns:
        List of rules from the bundle
        
    Raises:
        SchemaError: If bundle file cannot be loaded
    """
    try:
        # Resolve relative path
        bundle_path = base_path.parent / include_path
        
        if not bundle_path.exists():
            raise SchemaError(
                f"Rule bundle file not found: {bundle_path}",
                str(bundle_path)
            )
        
        # Load the bundle file
        with open(bundle_path, 'r', encoding='utf-8') as f:
            bundle_schema = yaml.safe_load(f)
        
        if not isinstance(bundle_schema, dict):
            raise SchemaError(
                f"Rule bundle must be a dictionary, got {type(bundle_schema).__name__}",
                str(bundle_path)
            )
        
        # Extract rules from bundle
        bundle_rules = bundle_schema.get("rules", [])
        
        # Recursively process any includes in the bundle
        if bundle_rules:
            bundle_rules = _process_rule_bundles(bundle_rules, bundle_path)
        
        return bundle_rules
        
    except yaml.YAMLError as e:
        raise SchemaError(
            f"Invalid YAML in rule bundle file: {str(e)}",
            str(bundle_path)
        )
    except Exception as e:
        raise SchemaError(
            f"Error loading rule bundle file: {str(e)}",
            str(bundle_path)
        ) 
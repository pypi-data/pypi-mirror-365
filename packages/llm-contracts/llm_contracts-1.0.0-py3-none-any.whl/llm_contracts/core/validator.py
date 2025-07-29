"""Core validation functionality."""

from typing import Any, Dict, List, Optional, Union
import json
from pathlib import Path

from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate as json_validate

from .schema import SchemaError, load_schema
from .rules import RuleError, validate_rules


class ValidationError(Exception):
    """Raised when validation fails."""
    
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str]):
        self.is_valid = is_valid
        self.errors = errors
    
    def __bool__(self) -> bool:
        return self.is_valid


def validate_output(
    output: Union[str, Dict[str, Any]], 
    schema_path: Union[str, Path]
) -> ValidationResult:
    """
    Validate LLM output against a schema and rules.
    
    Args:
        output: The LLM output to validate (JSON string, dict, or text)
        schema_path: Path to the YAML schema file
        
    Returns:
        ValidationResult with validation status and any errors
        
    Raises:
        ValidationError: If validation fails and strict mode is enabled
        SchemaError: If schema file cannot be loaded
        RuleError: If rule validation fails
    """
    try:
        # Load schema from file
        schema = load_schema(schema_path)
        
        # Parse output if it's a string
        if isinstance(output, str):
            try:
                parsed_output = json.loads(output)
            except json.JSONDecodeError:
                # Treat as plain text
                parsed_output = output
        else:
            parsed_output = output
        
        errors: List[str] = []
        
        # Validate schema if present
        if "schema" in schema:
            schema_errors = _validate_schema(parsed_output, schema["schema"])
            errors.extend(schema_errors)
        
        # Validate rules if present
        if "rules" in schema:
            rule_errors = validate_rules(parsed_output, schema["rules"])
            errors.extend(rule_errors)
        
        is_valid = len(errors) == 0
        
        # Check if strict mode is enabled
        strict = schema.get("strict", False)
        if strict and not is_valid:
            raise ValidationError(
                f"Validation failed with {len(errors)} errors", 
                errors
            )
        
        return ValidationResult(is_valid, errors)
        
    except (SchemaError, RuleError) as e:
        raise ValidationError(f"Validation setup failed: {str(e)}")


def _validate_schema(
    data: Any, 
    schema: Dict[str, Any]
) -> List[str]:
    """
    Validate data against JSON schema.
    
    Args:
        data: Data to validate
        schema: JSON schema definition
        
    Returns:
        List of validation error messages
    """
    errors: List[str] = []
    
    try:
        json_validate(instance=data, schema=schema)
    except JSONSchemaValidationError as e:
        errors.append(f"Schema validation failed: {e.message}")
    except Exception as e:
        errors.append(f"Unexpected validation error: {str(e)}")
    
    return errors 
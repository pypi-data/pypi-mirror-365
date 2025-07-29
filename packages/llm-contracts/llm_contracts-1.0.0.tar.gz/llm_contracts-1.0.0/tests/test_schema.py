"""Tests for the schema module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

from llm_contracts.core.schema import load_schema, SchemaError
from llm_contracts.core.validator import validate_output, ValidationResult


class TestSchemaLoading:
    """Test schema loading functionality."""
    
    def test_load_schema_valid_yaml(self):
        """Test loading valid YAML schema."""
        schema_content = {
            "schema": {
                "name": {"type": "str"},
                "age": {"type": "int"}
            },
            "rules": [
                {"keyword_must_include": "quality"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            loaded_schema = load_schema(schema_path)
            
            assert "schema" in loaded_schema
            assert "rules" in loaded_schema
            assert loaded_schema["schema"]["name"]["type"] == "str"
            assert loaded_schema["schema"]["age"]["type"] == "int"
            assert len(loaded_schema["rules"]) == 1
        finally:
            Path(schema_path).unlink()
    
    def test_load_schema_invalid_yaml(self):
        """Test loading invalid YAML schema."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            schema_path = f.name
        
        try:
            with pytest.raises(SchemaError):
                load_schema(schema_path)
        finally:
            Path(schema_path).unlink()
    
    def test_load_schema_nonexistent_file(self):
        """Test loading nonexistent schema file."""
        with pytest.raises(SchemaError):
            load_schema("nonexistent.yaml")
    
    def test_load_schema_empty_file(self):
        """Test loading empty schema file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            schema_path = f.name
        
        try:
            with pytest.raises(SchemaError):
                loaded_schema = load_schema(schema_path)
        finally:
            Path(schema_path).unlink()
    
    def test_load_schema_with_comments(self):
        """Test loading schema with YAML comments."""
        schema_content = """
        # User profile schema
        schema:
          name:
            type: str
            # Required field
            required: true
          age:
            type: int
            # Age range
            min: 0
            max: 120
        
        # Validation rules
        rules:
          - keyword_must_include: "quality"
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(schema_content)
            schema_path = f.name
        
        try:
            loaded_schema = load_schema(schema_path)
            
            assert "schema" in loaded_schema
            assert "rules" in loaded_schema
            assert loaded_schema["schema"]["name"]["required"] is True
            assert loaded_schema["schema"]["age"]["min"] == 0
            assert loaded_schema["schema"]["age"]["max"] == 120
        finally:
            Path(schema_path).unlink()
    
    def test_load_schema_rule_bundles(self):
        """Test loading schema with rule bundles."""
        # Create a rule bundle file
        bundle_content = {
            "rules": [
                {"keyword_must_not_include": ["cheap", "defective"]},
                {"no_placeholder_text": r"\[YOUR_TEXT_HERE\]"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(bundle_content, f)
            bundle_path = f.name
        
        # Create main schema that includes the bundle
        schema_content = {
            "schema": {
                "name": {"type": "str"}
            },
            "rules": [
                {"include": Path(bundle_path).name},
                {"keyword_must_include": "quality"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            loaded_schema = load_schema(schema_path)
            
            assert "schema" in loaded_schema
            assert "rules" in loaded_schema
            # Should have expanded the bundle rules
            assert len(loaded_schema["rules"]) >= 3  # Bundle rules + quality rule
        finally:
            Path(schema_path).unlink()
            Path(bundle_path).unlink()


class TestSchemaValidation:
    """Test schema validation functionality."""
    
    def test_validate_schema_success(self):
        """Test successful schema validation."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        data = {"name": "John Doe", "age": 30}
        
        try:
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            assert len(result.errors) == 0
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_missing_required_field(self):
        """Test schema validation with missing required field."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        data = {"name": "John Doe"}  # Missing age
        
        try:
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_wrong_type(self):
        """Test schema validation with wrong field type."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        data = {"name": "John Doe", "age": "thirty"}  # age should be int
        
        try:
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_string_pattern(self):
        """Test schema validation with string pattern."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "pattern": r"^[A-Z][a-z]+ [A-Z][a-z]+$"
                    }
                },
                "required": ["name"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid name
            data = {"name": "John Doe"}
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Invalid name
            data = {"name": "john doe"}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_numeric_constraints(self):
        """Test schema validation with numeric constraints."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "age": {
                        "type": "integer",
                        "minimum": 18,
                        "maximum": 65
                    },
                    "price": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1000.0
                    }
                },
                "required": ["age", "price"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid data
            data = {"age": 25, "price": 99.99}
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Invalid age
            data = {"age": 16, "price": 99.99}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            
            # Invalid price
            data = {"age": 25, "price": -10.0}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_list_constraints(self):
        """Test schema validation with list constraints."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 5,
                        "items": {"type": "string"}
                    }
                },
                "required": ["tags"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid list
            data = {"tags": ["python", "testing"]}
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Empty list (below min)
            data = {"tags": []}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            
            # Too many items
            data = {"tags": ["a", "b", "c", "d", "e", "f"]}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_nested_objects(self):
        """Test schema validation with nested objects."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "address": {
                        "type": "object",
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                            "zip_code": {
                                "type": "string",
                                "pattern": r"^\d{5}$"
                            }
                        },
                        "required": ["street", "city"]
                    }
                },
                "required": ["address"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid nested object
            data = {
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "zip_code": "12345"
                }
            }
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Invalid nested object (missing required field)
            data = {
                "address": {
                    "street": "123 Main St",
                    "zip_code": "12345"
                }
            }
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            
            # Invalid nested object (wrong zip code format)
            data = {
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "zip_code": "123"
                }
            }
            result = validate_output(data, schema_path)
            assert result.is_valid is False
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_enum_values(self):
        """Test schema validation with enum values."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive", "pending"]
                    }
                },
                "required": ["status"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid enum value
            data = {"status": "active"}
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Invalid enum value
            data = {"status": "unknown"}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_string_length_constraints(self):
        """Test schema validation with string length constraints."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 50
                    },
                    "description": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 500
                    }
                },
                "required": ["name", "description"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid string lengths
            data = {"name": "John", "description": "This is a valid description with sufficient length."}
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Name too short
            data = {"name": "J", "description": "This is a valid description."}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            
            # Description too short
            data = {"name": "John", "description": "Short"}
            result = validate_output(data, schema_path)
            assert result.is_valid is False
        finally:
            Path(schema_path).unlink()


class TestSchemaErrorHandling:
    """Test schema error handling."""
    
    def test_validate_schema_invalid_schema_structure(self):
        """Test validation with invalid schema structure."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "invalid_type"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        data = {"name": "John Doe"}
        
        try:
            # Should handle invalid type gracefully
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_missing_schema_section(self):
        """Test validation with missing schema section."""
        schema_content = {
            "rules": [
                {"keyword_must_include": "quality"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        data = {"name": "John Doe"}
        
        try:
            # Should not fail if no schema section, but should fail on rules
            result = validate_output(data, schema_path)
            assert result.is_valid is False  # Should fail on missing keyword
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_empty_data(self):
        """Test validation with empty data."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        data = {}
        
        try:
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()
    
    def test_validate_schema_none_data(self):
        """Test validation with None data."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        data = None
        
        try:
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()


class TestSchemaIntegration:
    """Test schema integration with other components."""
    
    def test_schema_with_rules_integration(self):
        """Test schema validation combined with rules."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name", "description"]
            },
            "rules": [
                {"keyword_must_include": "quality"},
                {"word_count_min": 5}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid data
            data = {
                "name": "Product",
                "description": "This is a quality product with great features."
            }
            
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Invalid data (missing keyword)
            data = {
                "name": "Product",
                "description": "This is a product with features."
            }
            
            result = validate_output(data, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()
    
    def test_schema_file_loading_integration(self):
        """Test complete integration of schema loading and validation."""
        schema_content = {
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "price": {
                        "type": "number",
                        "minimum": 0.0
                    },
                    "category": {
                        "type": "string",
                        "enum": ["electronics", "clothing", "books"]
                    }
                },
                "required": ["title", "price", "category"]
            },
            "rules": [
                {"keyword_must_include": "quality"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(schema_content, f)
            schema_path = f.name
        
        try:
            # Valid data
            data = {
                "title": "Quality Product",
                "price": 99.99,
                "category": "electronics"
            }
            
            result = validate_output(data, schema_path)
            assert result.is_valid is True
            
            # Invalid data
            invalid_data = {
                "title": "Product",
                "price": -10.0,  # Invalid price
                "category": "invalid"  # Invalid category
            }
            
            result = validate_output(invalid_data, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink() 
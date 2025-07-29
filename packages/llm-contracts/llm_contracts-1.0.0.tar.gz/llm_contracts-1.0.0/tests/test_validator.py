"""Tests for the validator module."""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest

from llm_contracts.core.validator import validate_output, ValidationError, ValidationResult


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating ValidationResult instances."""
        result = ValidationResult(True, [])
        assert result.is_valid is True
        assert result.errors == []
        
        result = ValidationResult(False, ["Error 1", "Error 2"])
        assert result.is_valid is False
        assert result.errors == ["Error 1", "Error 2"]
    
    def test_validation_result_bool(self):
        """Test ValidationResult boolean conversion."""
        result = ValidationResult(True, [])
        assert bool(result) is True
        
        result = ValidationResult(False, ["Error"])
        assert bool(result) is False


class TestValidateOutput:
    """Test validate_output function."""
    
    def test_validate_json_success(self):
        """Test successful JSON validation."""
        schema = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
        
        output = {"name": "John Doe", "age": 30}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            result = validate_output(output, schema_path)
            assert result.is_valid is True
            assert result.errors == []
        finally:
            Path(schema_path).unlink()
    
    def test_validate_json_failure(self):
        """Test failed JSON validation."""
        schema = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                },
                "required": ["name", "age"]
            }
        }
        
        output = {"name": "John Doe"}  # Missing age
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            result = validate_output(output, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()
    
    def test_validate_rules_success(self):
        """Test successful rule validation."""
        schema = {
            "rules": [
                {"keyword_must_include": "hello"},
                {"word_count_min": 3}
            ]
        }
        
        output = "Hello world, this is a test"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            result = validate_output(output, schema_path)
            assert result.is_valid is True
            assert result.errors == []
        finally:
            Path(schema_path).unlink()
    
    def test_validate_rules_failure(self):
        """Test failed rule validation."""
        schema = {
            "rules": [
                {"keyword_must_include": "missing"},
                {"word_count_min": 10}
            ]
        }
        
        output = "Short text"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            result = validate_output(output, schema_path)
            assert result.is_valid is False
            assert len(result.errors) >= 2
        finally:
            Path(schema_path).unlink()
    
    def test_validate_string_json(self):
        """Test validation with JSON string input."""
        schema = {
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        }
        
        output = '{"name": "John Doe"}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            result = validate_output(output, schema_path)
            assert result.is_valid is True
        finally:
            Path(schema_path).unlink()
    
    def test_validate_string_text(self):
        """Test validation with plain text string input."""
        schema = {
            "rules": [
                {"keyword_must_include": "test"}
            ]
        }
        
        output = "This is a test message"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            result = validate_output(output, schema_path)
            assert result.is_valid is True
        finally:
            Path(schema_path).unlink()
    
    def test_strict_mode(self):
        """Test strict mode raises ValidationError."""
        schema = {
            "strict": True,
            "rules": [
                {"keyword_must_include": "missing"}
            ]
        }
        
        output = "This text doesn't have the required keyword"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            with pytest.raises(ValidationError):
                validate_output(output, schema_path)
        finally:
            Path(schema_path).unlink()
    
    def test_invalid_schema_file(self):
        """Test handling of invalid schema file."""
        with pytest.raises(ValidationError):
            validate_output({}, "nonexistent.yaml")
    
    def test_empty_schema(self):
        """Test validation with empty schema."""
        schema = {}
        output = {"name": "John"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            result = validate_output(output, schema_path)
            assert result.is_valid is True
        finally:
            Path(schema_path).unlink()
    
    def test_section_must_start_with(self):
        """Test section_must_start_with rule."""
        schema = {
            "rules": [
                {"section_must_start_with": "^# Introduction"}
            ]
        }
        
        valid_content = "# Introduction to AI\nThis is a valid section."
        invalid_content = "This doesn't start with a heading."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            # Test valid content
            result = validate_output(valid_content, schema_path)
            assert result.is_valid is True
            
            # Test invalid content
            result = validate_output(invalid_content, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink()
    
    def test_list_item_pattern(self):
        """Test list_item_pattern rule."""
        schema = {
            "rules": [
                {"list_item_pattern": "^\\d+\\. [A-Z].*"}
            ]
        }
        
        valid_content = """
        1. First item starts with capital
        2. Second item also starts with capital
        """
        
        invalid_content = """
        1. first item doesn't start with capital
        2. second item also doesn't start with capital
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(schema, f)
            schema_path = f.name
        
        try:
            # Test valid content
            result = validate_output(valid_content, schema_path)
            assert result.is_valid is True
            
            # Test invalid content
            result = validate_output(invalid_content, schema_path)
            assert result.is_valid is False
            assert len(result.errors) > 0
        finally:
            Path(schema_path).unlink() 
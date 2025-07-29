"""Tests for the CLI module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import click
from click.testing import CliRunner

from llm_contracts.cli.main import main


class TestCLI:
    """Test CLI functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_basic_validation_success(self):
        """Test successful validation via CLI."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe", "age": 30}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file
            ])
            
            assert result.exit_code == 0
            assert "✅ Validation passed!" in result.output
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_basic_validation_failure(self):
        """Test failed validation via CLI."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe"}, f)  # Missing age
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file
            ])
            
            assert result.exit_code == 0
            assert "❌ Validation failed!" in result.output
            assert "Errors:" in result.output
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_text_output_format(self):
        """Test text output format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe", "age": 30}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file,
                '--output-format', 'text'
            ])
            
            assert result.exit_code == 0
            assert "Validating" in result.output
            assert "Validation passed!" in result.output or "Validation failed!" in result.output
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_json_output_format(self):
        """Test JSON output format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe", "age": 30}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file,
                '--output-format', 'json'
            ])
            
            assert result.exit_code == 0
            output_data = json.loads(result.output)
            assert "valid" in output_data
            assert "output_file" in output_data
            assert "schema_file" in output_data
            assert "errors" in output_data
            assert "error_count" in output_data
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_strict_mode_success(self):
        """Test strict mode with successful validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe", "age": 30}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file,
                '--strict'
            ])
            
            assert result.exit_code == 0
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_strict_mode_failure(self):
        """Test strict mode with failed validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe"}, f)  # Missing age
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
strict: true
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file,
                '--strict'
            ])
            
            assert result.exit_code == 1
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_html_report_generation(self):
        """Test HTML report generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe", "age": 30}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            html_report = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file,
                '--html-report', html_report
            ])
            
            assert result.exit_code == 0
            assert "📄 HTML report generated" in result.output
            assert Path(html_report).exists()
            
            # Check HTML content
            with open(html_report, 'r') as f:
                html_content = f.read()
                assert "<!DOCTYPE html>" in html_content
                assert "llm-contracts Validation Report" in html_content
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
            Path(html_report).unlink()
    
    def test_markdown_report_generation(self):
        """Test Markdown report generation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe", "age": 30}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            md_report = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file,
                '--md-report', md_report
            ])
            
            assert result.exit_code == 0
            assert "📝 Markdown report generated" in result.output
            assert Path(md_report).exists()
            
            # Check Markdown content
            with open(md_report, 'r') as f:
                md_content = f.read()
                assert "llm-contracts Validation Report" in md_content
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
            Path(md_report).unlink()
    
    def test_text_file_input(self):
        """Test validation of text file input."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test message with quality content.")
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
rules:
  - keyword_must_include: "quality"
  - word_count_min: 5
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file
            ])
            
            assert result.exit_code == 0
            assert "Validation passed!" in result.output or "Validation failed!" in result.output
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_invalid_schema_file(self):
        """Test handling of invalid schema file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe"}, f)
            output_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', 'nonexistent.yaml'
            ])
            
            assert result.exit_code == 2  # Click's default for missing required argument
            assert "does not exist" in result.output
        finally:
            Path(output_file).unlink()
    
    def test_invalid_output_file(self):
        """Test handling of invalid output file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                'nonexistent.json',
                '--schema', schema_file
            ])
            
            assert result.exit_code == 2  # Click's default for missing required argument
        finally:
            Path(schema_file).unlink()
    
    def test_malformed_json_input(self):
        """Test handling of malformed JSON input."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"name": "John Doe", "age": 30,}')  # Invalid JSON
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file
            ])
            
            # Should fall back to text mode
            assert result.exit_code == 0
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe"}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
schema:
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
  required: [name, age]
rules:
  - keyword_must_include: "missing"
            """)
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file
            ])
            
            assert result.exit_code == 0
            assert "❌ Validation failed!" in result.output
            assert "Errors:" in result.output
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_unexpected_error_handling(self):
        """Test handling of unexpected errors."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John Doe"}, f)
            output_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid yaml content")
            schema_file = f.name
        
        try:
            result = self.runner.invoke(main, [
                output_file,
                '--schema', schema_file
            ])
            
            assert result.exit_code == 1
            assert "Validation error" in result.output
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink() 
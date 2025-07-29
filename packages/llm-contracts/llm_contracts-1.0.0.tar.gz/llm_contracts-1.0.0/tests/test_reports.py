"""Tests for the reports module."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from llm_contracts.core.validator import ValidationResult
from llm_contracts.reports.html_generator import generate_html_report
from llm_contracts.reports.markdown_generator import generate_markdown_report


class TestHTMLReportGenerator:
    """Test HTML report generation."""
    
    def test_generate_html_report_single_result(self):
        """Test generating HTML report for single validation result."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_file = f.name
        
        try:
            generate_html_report(result, output_file)
            
            assert Path(output_file).exists()
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "<!DOCTYPE html>" in content
                assert "llm-contracts Validation Report" in content
                assert "✅" in content  # Pass indicator
        finally:
            Path(output_file).unlink()
    
    def test_generate_html_report_with_errors(self):
        """Test generating HTML report with validation errors."""
        result = ValidationResult(False, [
            "Must include keyword: 'quality'",
            "Word count (5) below minimum (10)"
        ])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_file = f.name
        
        try:
            generate_html_report(result, output_file)
            
            assert Path(output_file).exists()
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "❌" in content  # Fail indicator
                assert "Must include keyword: 'quality'" in content
                assert "Word count (5) below minimum (10)" in content
        finally:
            Path(output_file).unlink()
    
    def test_generate_html_report_multiple_results(self):
        """Test generating HTML report for multiple validation results."""
        results = [
            ValidationResult(True, []),
            ValidationResult(False, ["Error 1"]),
            ValidationResult(True, [])
        ]
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_file = f.name
        
        try:
            generate_html_report(results, output_file)
            
            assert Path(output_file).exists()
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "2 Passed" in content
                assert "1 Failed" in content
                assert "66.7% Success Rate" in content
        finally:
            Path(output_file).unlink()
    
    def test_generate_html_report_with_schema(self):
        """Test generating HTML report with schema reference."""
        result = ValidationResult(False, ["Field 'age' is required"])
        
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
            output_file = f.name
        
        try:
            generate_html_report(result, output_file, schema_file)
            
            assert Path(output_file).exists()
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "llm-contracts Validation Report" in content
                assert "Field 'age' is required" in content
        finally:
            Path(output_file).unlink()
            Path(schema_file).unlink()
    
    def test_generate_html_report_nonexistent_schema(self):
        """Test generating HTML report with nonexistent schema file."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_file = f.name
        
        try:
            # Should not raise an error
            generate_html_report(result, output_file, "nonexistent.yaml")
            
            assert Path(output_file).exists()
        finally:
            Path(output_file).unlink()
    
    def test_html_report_css_styling(self):
        """Test that HTML report includes proper CSS styling."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_file = f.name
        
        try:
            generate_html_report(result, output_file)
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "<style>" in content
                assert "font-family" in content
                assert "background" in content
                assert ".pass" in content
                assert ".fail" in content
        finally:
            Path(output_file).unlink()
    
    def test_html_report_responsive_design(self):
        """Test that HTML report includes responsive design elements."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            output_file = f.name
        
        try:
            generate_html_report(result, output_file)
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "viewport" in content
                assert "width=device-width" in content
                assert "max-width" in content
        finally:
            Path(output_file).unlink()


class TestMarkdownReportGenerator:
    """Test Markdown report generation."""
    
    def test_generate_markdown_report_single_result(self):
        """Test generating Markdown report for single validation result."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            output_file = f.name
        
        try:
            generate_markdown_report(result, output_file, "schema.yaml", {})
            
            assert Path(output_file).exists()
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "# llm-contracts Validation Report" in content
                assert "## Summary" in content
                assert "✅ PASSED" in content
        finally:
            Path(output_file).unlink()
    
    def test_generate_markdown_report_with_errors(self):
        """Test generating Markdown report with validation errors."""
        result = ValidationResult(False, [
            "Must include keyword: 'quality'",
            "Word count (5) below minimum (10)"
        ])
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            output_file = f.name
        
        try:
            generate_markdown_report(result, output_file, "schema.yaml", {})
            
            assert Path(output_file).exists()
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "❌ FAILED" in content
                assert "Must include keyword: 'quality'" in content
                assert "Word count (5) below minimum (10)" in content
        finally:
            Path(output_file).unlink()
    
    def test_generate_markdown_report_with_schema(self):
        """Test generating Markdown report with schema reference."""
        result = ValidationResult(False, ["Field 'age' is required"])
        schema_content = {
            "schema": {
                "name": {"type": "str"},
                "age": {"type": "int", "required": True}
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            output_file = f.name
        
        try:
            generate_markdown_report(result, output_file, "schema.yaml", schema_content)
            
            assert Path(output_file).exists()
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "## Schema Reference" in content
        finally:
            Path(output_file).unlink()
    
    def test_markdown_report_formatting(self):
        """Test that Markdown report has proper formatting."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            output_file = f.name
        
        try:
            generate_markdown_report(result, output_file, "schema.yaml", {})
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "**" in content   # Bold text
                assert "`" in content    # Code formatting
        finally:
            Path(output_file).unlink()
    
    def test_markdown_report_timestamp(self):
        """Test that Markdown report includes timestamp."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            output_file = f.name
        
        try:
            generate_markdown_report(result, output_file, "schema.yaml", {})
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "**Generated**:" in content
        finally:
            Path(output_file).unlink()
    
    def test_markdown_report_error_categorization(self):
        """Test that Markdown report categorizes errors properly."""
        result = ValidationResult(False, [
            "Must include keyword: 'quality'",
            "Word count (5) below minimum (10)",
            "Field 'age' is required"
        ])
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            output_file = f.name
        
        try:
            generate_markdown_report(result, output_file, "schema.yaml", {})
            
            with open(output_file, 'r') as f:
                content = f.read()
                assert "Must include keyword: 'quality'" in content
                assert "Word count (5) below minimum (10)" in content
                assert "Field 'age' is required" in content
        finally:
            Path(output_file).unlink()


class TestReportIntegration:
    """Test integration between different report types."""
    
    def test_html_and_markdown_consistency(self):
        """Test that HTML and Markdown reports are consistent."""
        result = ValidationResult(False, ["Test error message"])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            html_file = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            md_file = f.name
        
        try:
            # Generate both reports
            generate_html_report(result, html_file)
            generate_markdown_report(result, md_file, "schema.yaml", {})
            
            # Check both files exist
            assert Path(html_file).exists()
            assert Path(md_file).exists()
            
            # Check content consistency
            with open(html_file, 'r') as f:
                html_content = f.read()
            
            with open(md_file, 'r') as f:
                md_content = f.read()
            
            # Both should contain the error message
            assert "Test error message" in html_content
            assert "Test error message" in md_content
            
            # Both should indicate failure
            assert "❌" in html_content
            assert "❌ FAILED" in md_content
        finally:
            Path(html_file).unlink()
            Path(md_file).unlink()
    
    def test_report_file_permissions(self):
        """Test that report files are created with proper permissions."""
        result = ValidationResult(True, [])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            html_file = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            md_file = f.name
        
        try:
            generate_html_report(result, html_file)
            generate_markdown_report(result, md_file, "schema.yaml", {})
            
            # Check files are readable
            assert Path(html_file).is_file()
            assert Path(md_file).is_file()
            
            # Check files are not empty
            assert Path(html_file).stat().st_size > 0
            assert Path(md_file).stat().st_size > 0
        finally:
            Path(html_file).unlink()
            Path(md_file).unlink()
    
    def test_report_encoding(self):
        """Test that reports are generated with proper UTF-8 encoding."""
        result = ValidationResult(False, ["Special characters: éñüß"])
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            html_file = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as f:
            md_file = f.name
        
        try:
            generate_html_report(result, html_file)
            generate_markdown_report(result, md_file, "schema.yaml", {})
            
            # Check UTF-8 encoding
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            assert "éñüß" in html_content
            assert "éñüß" in md_content
        finally:
            Path(html_file).unlink()
            Path(md_file).unlink() 
"""Main contracts API for llm-contracts."""

from typing import Any, Dict, Union, Optional
from pathlib import Path

from .core.validator import validate_output, ValidationResult, ValidationError
from .reports.html_generator import generate_html_report
from .reports.markdown_generator import generate_markdown_report


class Contracts:
    """Main contracts API for LLM output validation and linting."""
    
    def validate(
        self, 
        data: Union[str, Dict[str, Any]], 
        schema_path: Union[str, Path],
        custom_validator: Optional[callable] = None
    ) -> ValidationResult:
        """
        Validate LLM output against a schema.
        
        Args:
            data: Data to validate (JSON string, dict, or text)
            schema_path: Path to YAML schema file
            custom_validator: Optional custom validation function
            
        Returns:
            ValidationResult with validation status and errors
            
        Example:
            >>> from llm_contracts import contracts
            >>> result = contracts.validate(data, 'schema.yaml')
            >>> print(f"Valid: {result.is_valid}")
        """
        # For now, ignore custom_validator until we implement it
        return validate_output(data, schema_path)
    
    def lint(
        self,
        data: Union[str, Dict[str, Any]],
        schema_path: Union[str, Path],
        custom_validator: Optional[callable] = None
    ) -> ValidationResult:
        """
        Lint LLM output for content quality and style issues.
        
        Args:
            data: Data to lint (JSON string, dict, or text)
            schema_path: Path to YAML schema file with linting rules
            custom_validator: Optional custom validation function
            
        Returns:
            ValidationResult with linting status and issues
            
        Example:
            >>> from llm_contracts import contracts
            >>> result = contracts.lint(content, 'style_rules.yaml')
            >>> print(f"Lint passed: {result.is_valid}")
        """
        # For now, ignore custom_validator until we implement it
        return validate_output(data, schema_path)
    
    def generate_report(
        self,
        result: ValidationResult,
        output_path: str,
        schema_path: str,
        format: str = "html",
        schema_content: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Generate validation report in specified format.
        
        Args:
            result: Validation result from validate() or lint()
            output_path: Path for the report file
            schema_path: Path to schema file for reference
            format: Report format ("html" or "markdown")
            schema_content: Optional schema content for rule references
            
        Example:
            >>> from llm_contracts import contracts
            >>> result = contracts.validate(data, 'schema.yaml')
            >>> contracts.generate_report(result, 'report.html', 'schema.yaml', 'html')
        """
        if format.lower() == "html":
            generate_html_report(result, output_path, schema_path)
        elif format.lower() in ["md", "markdown"]:
            generate_markdown_report(result, output_path, schema_path, schema_content)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'html' or 'markdown'")
    
    def validate_and_report(
        self,
        data: Union[str, Dict[str, Any]],
        schema_path: Union[str, Path],
        report_path: Optional[str] = None,
        report_format: str = "html",
        custom_validator: Optional[callable] = None
    ) -> ValidationResult:
        """
        Validate data and optionally generate a report.
        
        Args:
            data: Data to validate
            schema_path: Path to schema file
            report_path: Optional path for report file
            report_format: Report format ("html" or "markdown")
            custom_validator: Optional custom validation function
            
        Returns:
            ValidationResult
            
        Example:
            >>> from llm_contracts import contracts
            >>> result = contracts.validate_and_report(
            ...     data, 'schema.yaml', 'report.html', 'html'
            ... )
        """
        result = self.validate(data, schema_path)
        
        if report_path:
            self.generate_report(result, report_path, str(schema_path), report_format)
        
        return result


# Create singleton instance
contracts = Contracts()

# Export main functions for backward compatibility
__all__ = [
    "contracts",
    "validate_output",  # Backward compatibility
    "generate_html_report",  # Backward compatibility
    "generate_markdown_report",  # Backward compatibility
    "ValidationResult",
    "ValidationError"
] 
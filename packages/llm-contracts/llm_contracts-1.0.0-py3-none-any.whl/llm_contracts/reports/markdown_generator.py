"""Markdown report generation for llm-contracts."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.validator import ValidationResult


def generate_markdown_report(
    result: ValidationResult,
    output_path: str,
    schema_path: str,
    schema_content: Optional[Dict[str, Any]] = None
) -> None:
    """
    Generate a Markdown validation report.
    
    Args:
        result: Validation result from validate_output
        output_path: Path for the Markdown output file
        schema_path: Path to the schema file for reference
        schema_content: Optional schema content for rule references
    """
    markdown_content = _generate_markdown_content(result, schema_path, schema_content)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)


def _generate_markdown_content(
    result: ValidationResult,
    schema_path: str,
    schema_content: Optional[Dict[str, Any]] = None
) -> str:
    """Generate the Markdown content for the report."""
    
    # Header
    content = [
        "# llm-contracts Validation Report",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Schema**: `{schema_path}`",
        "",
    ]
    
    # Summary
    error_count = len(result.errors)
    success_rate = 100.0 if result.is_valid else 0.0
    
    content.extend([
        "## Summary",
        "",
        f"- **Status**: {'✅ PASSED' if result.is_valid else '❌ FAILED'}",
        f"- **Errors**: {error_count}",
        f"- **Success Rate**: {success_rate:.1f}%",
        "",
    ])
    
    # Test Results
    content.extend([
        "## Test Results",
        "",
    ])
    
    if result.is_valid:
        content.extend([
        "### ✅ Validation Passed",
        "",
        "All validation checks passed successfully!",
        "",
        ])
    else:
        content.extend([
        "### ❌ Validation Failed",
        "",
        f"Found {error_count} validation error(s):",
        "",
        ])
        
        # Group errors by type
        error_groups = _group_errors_by_type(result.errors)
        
        for error_type, errors in error_groups.items():
            content.append(f"#### {error_type}")
            content.append("")
            
            for error in errors:
                content.append(f"- {error}")
            
            content.append("")
    
    # Schema Reference (if available)
    if schema_content:
        content.extend([
        "## Schema Reference",
        "",
        "### Rules Applied",
        "",
        ])
        
        if "rules" in schema_content:
            for i, rule in enumerate(schema_content["rules"], 1):
                content.append(f"**Rule {i}**:")
                content.append("```yaml")
                content.append(f"{rule}")
                content.append("```")
                content.append("")
    
    return "\n".join(content)


def _group_errors_by_type(errors: List[str]) -> Dict[str, List[str]]:
    """Group errors by their type for better organization."""
    groups = {
        "Schema Validation": [],
        "Keyword Rules": [],
        "Content Rules": [],
        "Other": []
    }
    
    for error in errors:
        error_lower = error.lower()
        
        if "schema validation failed" in error_lower:
            groups["Schema Validation"].append(error)
        elif "keyword" in error_lower:
            groups["Keyword Rules"].append(error)
        elif any(rule_type in error_lower for rule_type in [
            "word count", "placeholder", "phrase", "section", "list"
        ]):
            groups["Content Rules"].append(error)
        else:
            groups["Other"].append(error)
    
    # Remove empty groups
    return {k: v for k, v in groups.items() if v} 
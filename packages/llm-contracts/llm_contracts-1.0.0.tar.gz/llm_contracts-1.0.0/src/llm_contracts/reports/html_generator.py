"""HTML report generator for validation results."""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.validator import ValidationResult


def generate_html_report(
    results: Union[ValidationResult, List[ValidationResult]], 
    output_file: str,
    schema_path: Optional[str] = None
) -> None:
    """
    Generate an HTML report for validation results.
    
    Args:
        results: Single ValidationResult or list of ValidationResult objects
        output_file: Path to output HTML file
        schema_path: Optional path to schema file for highlighting
    """
    if isinstance(results, ValidationResult):
        results = [results]
    
    html_content = _generate_html_content(results, schema_path)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _generate_html_content(
    results: List[ValidationResult], 
    schema_path: Optional[str] = None
) -> str:
    """Generate the complete HTML content."""
    
    # Load schema content if provided
    schema_content = None
    if schema_path and Path(schema_path).exists():
        with open(schema_path, 'r') as f:
            schema_content = yaml.safe_load(f)
    
    # Calculate summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.is_valid)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Generate CSS
    css = _generate_css()
    
    # Generate report sections
    header = _generate_header(total_tests, passed_tests, failed_tests, success_rate)
    test_results = _generate_test_results(results, schema_content)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>llm-contracts Validation Report</title>
    <style>
        {css}
    </style>
</head>
<body>
    <div class="container">
        {header}
        {test_results}
    </div>
</body>
</html>"""


def _generate_css() -> str:
    """Generate minimalist custom CSS."""
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8fafc;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .header h1 {
            color: #1f2937;
            margin-bottom: 1rem;
            font-size: 2rem;
        }
        
        .summary {
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
        }
        
        .summary-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
        }
        
        .pass { color: #059669; }
        .fail { color: #dc2626; }
        .warning { color: #d97706; }
        
        .test-results {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .test-item {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #e5e7eb;
        }
        
        .test-item.pass {
            border-left-color: #059669;
        }
        
        .test-item.fail {
            border-left-color: #dc2626;
        }
        
        .test-item h3 {
            margin-bottom: 0.5rem;
            color: #1f2937;
        }
        
        .errors {
            margin-top: 1rem;
        }
        
        .error-detail {
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .error-detail h4 {
            color: #dc2626;
            margin-bottom: 0.5rem;
        }
        
        .schema-reference {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 1rem;
            margin-top: 1rem;
        }
        
        .schema-reference h5 {
            color: #374151;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .schema-reference pre {
            background: #1f2937;
            color: #f9fafb;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.875rem;
            line-height: 1.4;
        }
        
        .timestamp {
            color: #6b7280;
            font-size: 0.875rem;
            margin-top: 1rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .summary {
                flex-direction: column;
                gap: 1rem;
            }
        }
    """


def _generate_header(
    total_tests: int, 
    passed_tests: int, 
    failed_tests: int, 
    success_rate: float
) -> str:
    """Generate the report header."""
    return f"""
        <div class="header">
            <h1>llm-contracts Validation Report</h1>
            <div class="summary">
                <div class="summary-item">
                    <span class="pass">✅</span>
                    <span>{passed_tests} Passed</span>
                </div>
                <div class="summary-item">
                    <span class="fail">❌</span>
                    <span>{failed_tests} Failed</span>
                </div>
                <div class="summary-item">
                    <span class="warning">📊</span>
                    <span>{success_rate:.1f}% Success Rate</span>
                </div>
            </div>
            <div class="timestamp">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
    """


def _generate_test_results(
    results: List[ValidationResult], 
    schema_content: Optional[Dict[str, Any]] = None
) -> str:
    """Generate the test results section."""
    html_parts = ['<div class="test-results">']
    
    for i, result in enumerate(results):
        status_class = "pass" if result.is_valid else "fail"
        status_icon = "✅" if result.is_valid else "❌"
        
        html_parts.append(f'''
            <div class="test-item {status_class}">
                <h3>{status_icon} Test {i + 1}</h3>
        ''')
        
        if result.is_valid:
            html_parts.append('<p>All validations passed successfully.</p>')
        else:
            html_parts.append('<div class="errors">')
            for error in result.errors:
                html_parts.append(f'''
                    <div class="error-detail">
                        <h4>Validation Error</h4>
                        <p>{error}</p>
                        {_generate_schema_reference(error, schema_content)}
                    </div>
                ''')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    return ''.join(html_parts)


def _generate_schema_reference(
    error: str, 
    schema_content: Optional[Dict[str, Any]] = None
) -> str:
    """Generate schema reference for an error."""
    if not schema_content:
        return ""
    
    # Try to find relevant schema section based on error message
    relevant_section = _find_relevant_schema_section(error, schema_content)
    
    if relevant_section:
        return f'''
            <div class="schema-reference">
                <h5>Relevant Schema Section:</h5>
                <pre><code>{relevant_section}</code></pre>
            </div>
        '''
    
    return ""


def _find_relevant_schema_section(error: str, schema_content: Dict[str, Any]) -> Optional[str]:
    """Find the relevant schema section for an error."""
    error_lower = error.lower()
    
    # Handle schema validation errors
    if "schema validation failed" in error_lower:
        # Try to find the specific field that failed
        for key, value in schema_content.get("schema", {}).get("properties", {}).items():
            if key in error_lower:
                return yaml.dump({key: value}, default_flow_style=False)
    
    # Handle keyword errors
    elif "must include keyword" in error_lower or "must not include keyword" in error_lower:
        # Extract the keyword from the error message
        import re
        keyword_match = re.search(r"'([^']+)'", error)
        if keyword_match:
            keyword = keyword_match.group(1)
            # Find the specific rule that contains this keyword
            if "rules" in schema_content:
                for rule in schema_content["rules"]:
                    for rule_type, rule_value in rule.items():
                        if rule_type in ["keyword_must_include", "keyword_must_not_include"]:
                            if isinstance(rule_value, list) and keyword in rule_value:
                                return yaml.dump({rule_type: rule_value}, default_flow_style=False)
                            elif isinstance(rule_value, str) and keyword == rule_value:
                                return yaml.dump({rule_type: rule_value}, default_flow_style=False)
    
    # Handle placeholder text errors
    elif "placeholder text" in error_lower:
        # Find the specific placeholder rule
        if "rules" in schema_content:
            for rule in schema_content["rules"]:
                for rule_type, rule_value in rule.items():
                    if rule_type == "no_placeholder_text":
                        return yaml.dump({rule_type: rule_value}, default_flow_style=False)
    
    # Handle word count errors
    elif "word count" in error_lower:
        if "rules" in schema_content:
            for rule in schema_content["rules"]:
                for rule_type, rule_value in rule.items():
                    if rule_type in ["word_count_min", "word_count_max"]:
                        return yaml.dump({rule_type: rule_value}, default_flow_style=False)
    
    # Handle phrase proximity errors
    elif "must be within" in error_lower:
        if "rules" in schema_content:
            for rule in schema_content["rules"]:
                for rule_type, rule_value in rule.items():
                    if rule_type == "phrase_proximity":
                        return yaml.dump({rule_type: rule_value}, default_flow_style=False)
    
    return None 
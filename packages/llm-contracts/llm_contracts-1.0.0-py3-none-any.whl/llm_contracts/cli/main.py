"""Command-line interface for llm-contracts."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from ..core.validator import validate_output, ValidationError


@click.command()
@click.argument("output_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--schema", 
    "-s", 
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to YAML schema file"
)
@click.option(
    "--output-format",
    "-f",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format for results"
)
@click.option(
    "--strict",
    is_flag=True,
    help="Exit with error code 1 if validation fails"
)
@click.option(
    "--html-report",
    type=click.Path(path_type=Path),
    help="Generate HTML report file"
)
@click.option(
    "--md-report",
    type=click.Path(path_type=Path),
    help="Generate Markdown report file"
)
def main(
    output_file: Path,
    schema: Path,
    output_format: str,
    strict: bool,
    html_report: Optional[Path] = None,
    md_report: Optional[Path] = None
) -> None:
    """
    Validate LLM output against a schema.
    
    OUTPUT_FILE: Path to the file containing LLM output to validate
    """
    try:
        # Read output file
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as JSON, fallback to text
        try:
            output_data = json.loads(content)
        except json.JSONDecodeError:
            output_data = content
        
        # Validate output
        result = validate_output(output_data, schema)
        
        # Output results
        if output_format == "json":
            _output_json(result, output_file, schema)
        else:
            _output_text(result, output_file, schema)
        
        # Generate HTML report if requested
        if html_report:
            from ..reports.html_generator import generate_html_report
            generate_html_report(result, str(html_report), str(schema))
            click.echo(f"📄 HTML report generated: {html_report}")
        
        # Generate Markdown report if requested
        if md_report:
            from ..reports.markdown_generator import generate_markdown_report
            from ..core.schema import load_schema
            schema_content = load_schema(schema)
            generate_markdown_report(result, str(md_report), str(schema), schema_content)
            click.echo(f"📝 Markdown report generated: {md_report}")
        
        # Exit with error code if validation failed and strict mode is enabled
        if strict and not result.is_valid:
            sys.exit(1)
            
    except ValidationError as e:
        click.echo(f"Validation error: {e.message}", err=True)
        if e.errors:
            for error in e.errors:
                click.echo(f"  - {error}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        sys.exit(1)


def _output_text(
    result: "ValidationResult", 
    output_file: Path, 
    schema_file: Path
) -> None:
    """Output validation results in text format."""
    click.echo(f"Validating {output_file} against {schema_file}")
    click.echo()
    
    if result.is_valid:
        click.echo("✅ Validation passed!")
    else:
        click.echo("❌ Validation failed!")
        click.echo()
        click.echo("Errors:")
        for error in result.errors:
            click.echo(f"  - {error}")


def _output_json(
    result: "ValidationResult", 
    output_file: Path, 
    schema_file: Path
) -> None:
    """Output validation results in JSON format."""
    output_data = {
        "valid": result.is_valid,
        "output_file": str(output_file),
        "schema_file": str(schema_file),
        "errors": result.errors,
        "error_count": len(result.errors)
    }
    
    click.echo(json.dumps(output_data, indent=2))


if __name__ == "__main__":
    main() 
"""LLM Output Validation, Linting, and Assertion Layer."""

from importlib import metadata

try:
    __version__ = metadata.version("llm-contracts")
except metadata.PackageNotFoundError:
    __version__ = "unknown"

from .core.validator import validate_output, ValidationError, ValidationResult
from .core.schema import SchemaError
from .core.rules import RuleError
from .reports.html_generator import generate_html_report
from .reports.markdown_generator import generate_markdown_report
from .contracts import contracts

__all__ = [
    "contracts",  # New branded API
    "validate_output",  # Backward compatibility
    "ValidationError", 
    "ValidationResult",
    "SchemaError",
    "RuleError",
    "generate_html_report",
    "generate_markdown_report",
    "__version__",
] 
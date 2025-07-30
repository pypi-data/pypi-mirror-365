"""Security validation for AI Forge template system."""

import re
from pathlib import Path
from typing import Any

from ..exceptions import TemplateSecurityError


def validate_template_path(path: Path, base_path: Path) -> None:
    """Validate that template path is safe and within base directory.

    Args:
        path: Path to validate
        base_path: Base directory that path must be within

    Raises:
        TemplateSecurityError: If path is unsafe or outside base directory
    """
    try:
        # Resolve to absolute paths to prevent path traversal
        resolved_path = path.resolve()
        resolved_base = base_path.resolve()

        # Check if path is within base directory
        if not str(resolved_path).startswith(str(resolved_base)):
            raise TemplateSecurityError(
                f"Template path '{path}' is outside base directory '{base_path}'"
            )

        # Check for suspicious path components
        path_parts = path.parts
        dangerous_parts = {"..", ".", "~"}
        if any(part in dangerous_parts for part in path_parts):
            raise TemplateSecurityError(
                f"Template path '{path}' contains dangerous path components"
            )

    except (OSError, ValueError) as e:
        raise TemplateSecurityError(f"Invalid template path '{path}': {e}")


def validate_template_content(content: str, file_path: Path) -> None:
    """Validate template content for security risks.

    Args:
        content: Template file content to validate
        file_path: Path of the template file being validated

    Raises:
        TemplateSecurityError: If content contains security risks
    """
    # List of dangerous patterns to check for
    dangerous_patterns = [
        # Python code execution
        r"exec\s*\(",
        r"eval\s*\(",
        r"__import__\s*\(",
        r"compile\s*\(",
        # File system operations that could be dangerous (Python specific)
        r"(?<![\w_])open\s*\(",  # open() not preceded by word chars
        r"(?<![\w_])file\s*\(",  # file() not preceded by word chars
        # Subprocess/shell execution
        r"subprocess\.",
        r"os\.system",
        r"os\.popen",
        r"os\.spawn",
        # Network operations
        r"urllib\.",
        r"requests\.",
        r"socket\.",
        # Jinja2 specific dangerous patterns
        r"\{\{.*?__.*?\}\}",  # Double underscore attributes
        r"\{\%.*?import.*?\%\}",  # Import statements in templates
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            raise TemplateSecurityError(
                f"Template '{file_path}' contains potentially dangerous content: "
                f"pattern '{pattern}' detected"
            )


def validate_template_variables(variables: dict[str, Any]) -> None:
    """Validate template variables for security.

    Args:
        variables: Template variables to validate

    Raises:
        TemplateSecurityError: If variables contain security risks
    """
    # Check for dangerous variable names
    dangerous_names = {
        "__builtins__",
        "__globals__",
        "__locals__",
        "__import__",
        "exec",
        "eval",
        "compile",
        "open",
        "file",
    }

    for var_name in variables:
        if var_name in dangerous_names:
            raise TemplateSecurityError(
                f"Variable name '{var_name}' is not allowed for security reasons"
            )

        # Check for variables starting with underscore (potential private access)
        if var_name.startswith("_"):
            raise TemplateSecurityError(
                f"Variable name '{var_name}' starting with underscore is not allowed"
            )

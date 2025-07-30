"""Variable validation rules for the starter template."""

import re
from typing import Any

try:
    from ai_forge.exceptions import TemplateValidationError
except ImportError:
    # Fallback for testing
    class TemplateValidationError(Exception):  # type: ignore[no-redef]
        pass


def validate_project_name(value: str) -> str:
    """Validate and sanitize project name.

    Args:
        value: Raw project name value

    Returns:
        Sanitized project name

    Raises:
        TemplateValidationError: If project name is invalid
    """
    if not value or not value.strip():
        raise TemplateValidationError("Project name cannot be empty")

    # Remove leading/trailing whitespace
    name = value.strip()

    # Check length constraints
    if len(name) < 2:
        raise TemplateValidationError("Project name must be at least 2 characters long")

    if len(name) > 100:
        raise TemplateValidationError("Project name must be 100 characters or less")

    # Check for valid characters (allow letters, numbers, spaces, hyphens, underscores)
    if not re.match(r"^[a-zA-Z0-9\s\-_\.]+$", name):
        raise TemplateValidationError(
            "Project name can only contain letters, numbers, spaces, "
            "hyphens, underscores, and dots"
        )

    # Check that it doesn't start or end with special characters
    if re.search(r"^[-_.\s]|[-_.\s]$", name):
        raise TemplateValidationError(
            "Project name cannot start or end with special characters"
        )

    # Check for dangerous patterns
    dangerous_patterns = [
        r"\.\.",  # Path traversal
        r'[<>:"/\\|?*]',  # Windows forbidden characters
        r"^\.",  # Hidden files pattern
        r"^CON$|^PRN$|^AUX$|^NUL$",  # Windows reserved names
        r"^COM[1-9]$|^LPT[1-9]$",  # Windows reserved names
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            raise TemplateValidationError(
                f"Project name contains invalid pattern: {pattern}"
            )

    return name


def validate_description(value: str) -> str:
    """Validate and sanitize project description.

    Args:
        value: Raw description value

    Returns:
        Sanitized description

    Raises:
        TemplateValidationError: If description is invalid
    """
    if not value or not value.strip():
        raise TemplateValidationError("Description cannot be empty")

    # Remove leading/trailing whitespace
    description = value.strip()

    # Check length constraints
    if len(description) < 5:
        raise TemplateValidationError("Description must be at least 5 characters long")

    if len(description) > 500:
        raise TemplateValidationError("Description must be 500 characters or less")

    # Check for potentially dangerous content
    dangerous_patterns = [
        r"<script",  # HTML script tags
        r"javascript:",  # JavaScript URLs
        r"data:",  # Data URLs
        r"vbscript:",  # VBScript URLs
        r"onload=",  # Event handlers
        r"onerror=",  # Event handlers
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, description, re.IGNORECASE):
            raise TemplateValidationError(
                f"Description contains potentially dangerous content: {pattern}"
            )

    return description


def validate_author(value: str) -> str:
    """Validate and sanitize author name.

    Args:
        value: Raw author value

    Returns:
        Sanitized author name

    Raises:
        TemplateValidationError: If author is invalid
    """
    if not value or not value.strip():
        raise TemplateValidationError("Author cannot be empty")

    # Remove leading/trailing whitespace
    author = value.strip()

    # Check length constraints
    if len(author) < 2:
        raise TemplateValidationError("Author name must be at least 2 characters long")

    if len(author) > 100:
        raise TemplateValidationError("Author name must be 100 characters or less")

    # Allow letters, numbers, spaces, hyphens, apostrophes, dots
    if not re.match(r"^[a-zA-Z0-9\s\-'\.]+$", author):
        raise TemplateValidationError(
            "Author name can only contain letters, numbers, spaces, "
            "hyphens, apostrophes, and dots"
        )

    # Check for dangerous patterns
    dangerous_patterns = [
        r"\.\.",  # Path traversal
        r'[<>:"/\\|?*]',  # Forbidden characters
        r"^\.",  # Starting with dot
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, author):
            raise TemplateValidationError(
                f"Author name contains invalid pattern: {pattern}"
            )

    return author


def validate_editor(value: str) -> str:
    """Validate and sanitize editor name.

    Args:
        value: Raw editor value

    Returns:
        Sanitized editor name

    Raises:
        TemplateValidationError: If editor is invalid
    """
    if not value or not value.strip():
        return "vscode"  # Default fallback

    editor = value.strip().lower()

    # List of supported editors
    supported_editors = {
        "vscode",
        "code",
        "visual-studio-code",
        "vim",
        "nvim",
        "neovim",
        "emacs",
        "sublime",
        "sublime-text",
        "atom",
        "intellij",
        "idea",
        "pycharm",
        "webstorm",
        "goland",
        "clion",
        "eclipse",
        "netbeans",
        "nano",
        "gedit",
        "notepad++",
        "kate",
    }

    # Normalize common variations
    editor_mapping = {
        "vs-code": "vscode",
        "visual-studio-code": "vscode",
        "code": "vscode",
        "nvim": "neovim",
        "sublime-text": "sublime",
        "notepad-plus-plus": "notepad++",
        "idea": "intellij",
    }

    editor = editor_mapping.get(editor, editor)

    if editor not in supported_editors:
        raise TemplateValidationError(
            f"Unsupported editor: {value}. "
            f"Supported editors: {', '.join(sorted(supported_editors))}"
        )

    return editor


def validate_claude_permissions(value: list[str]) -> list[str]:
    """Validate Claude Code permissions list.

    Args:
        value: List of permission names

    Returns:
        Validated permissions list

    Raises:
        TemplateValidationError: If permissions are invalid
    """
    if not isinstance(value, list):
        raise TemplateValidationError("Claude permissions must be a list")

    if not value:
        raise TemplateValidationError(
            "At least one Claude permission must be specified"
        )

    # Define allowed and dangerous permissions
    safe_permissions = {"Edit", "Write", "Read", "Grep", "Glob", "LS"}
    dangerous_permissions = {
        "Execute",
        "Network",
        "SystemAccess",
        "FileSystem",
        "Shell",
    }
    all_permissions = safe_permissions | dangerous_permissions

    validated_permissions = []

    for permission in value:
        if not isinstance(permission, str):
            raise TemplateValidationError(
                f"Permission must be a string, got {type(permission).__name__}"
            )

        permission = permission.strip()

        if not permission:
            raise TemplateValidationError("Permission name cannot be empty")

        # Check if permission is recognized
        if permission not in all_permissions:
            raise TemplateValidationError(
                f"Unknown permission: {permission}. "
                f"Valid permissions: {', '.join(sorted(all_permissions))}"
            )

        # Warn about dangerous permissions (but don't reject - let user decide)
        if permission in dangerous_permissions:
            # For starter template, we reject dangerous permissions
            raise TemplateValidationError(
                f"Permission '{permission}' is not allowed in starter template "
                f"for security. Safe permissions: {', '.join(sorted(safe_permissions))}"
            )

        if permission not in validated_permissions:
            validated_permissions.append(permission)

    # Ensure minimum required permissions
    required_permissions = {"Read"}
    for req_perm in required_permissions:
        if req_perm not in validated_permissions:
            validated_permissions.append(req_perm)

    return validated_permissions


def validate_boolean(value: Any, field_name: str) -> bool:
    """Validate boolean value.

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Returns:
        Boolean value

    Raises:
        TemplateValidationError: If value is not a valid boolean
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.strip().lower()
        if value in ("true", "yes", "1", "on", "enable", "enabled"):
            return True
        elif value in ("false", "no", "0", "off", "disable", "disabled"):
            return False

    raise TemplateValidationError(
        f"{field_name} must be a boolean value (true/false), got: {value}"
    )


# Main validation function
def validate_variables(variables: dict[str, Any]) -> dict[str, Any]:
    """Validate all template variables.

    Args:
        variables: Dictionary of template variables

    Returns:
        Dictionary of validated and sanitized variables

    Raises:
        TemplateValidationError: If any variable is invalid
    """
    validated: dict[str, Any] = {}

    # Validate required variables
    validated["project_name"] = validate_project_name(variables["project_name"])
    validated["description"] = validate_description(variables["description"])
    validated["author"] = validate_author(variables["author"])

    # Validate optional variables with defaults
    validated["editor"] = validate_editor(variables.get("editor", "vscode"))
    validated["git_enabled"] = validate_boolean(
        variables.get("git_enabled", True), "git_enabled"
    )
    validated["format_on_save"] = validate_boolean(
        variables.get("format_on_save", True), "format_on_save"
    )
    validated["claude_permissions"] = validate_claude_permissions(
        variables.get("claude_permissions", ["Edit", "Write", "Read"])
    )

    # Add date if not provided (will be handled by template rendering)
    validated["date"] = variables.get("date", "{{ now.strftime('%Y-%m-%d') }}")

    return validated

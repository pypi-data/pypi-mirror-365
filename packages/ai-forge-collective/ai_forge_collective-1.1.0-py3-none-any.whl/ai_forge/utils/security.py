"""Security validation utilities."""

import re
from pathlib import Path

from ai_forge.exceptions import FileSystemError


def validate_path_security(file_path: str, allow_hidden: bool = False) -> str:
    """Validate path to prevent directory traversal attacks.

    Args:
        file_path: The file path to validate
        allow_hidden: Whether to allow hidden files/directories

    Returns:
        The validated path string

    Raises:
        ValueError: If path contains dangerous patterns
    """
    if not file_path:
        raise ValueError("Path cannot be empty")

    # Normalize path and check for directory traversal
    normalized_path = Path(file_path).as_posix()

    # Prevent absolute paths (Unix and Windows style)
    if Path(normalized_path).is_absolute() or (
        len(file_path) > 1 and file_path[1] == ":" and file_path[0].isalpha()
    ):
        raise ValueError("Absolute paths are not allowed")

    # Prevent directory traversal patterns
    path_parts = normalized_path.split("/")
    if ".." in path_parts or any(part.startswith("..") for part in path_parts):
        raise ValueError("Path traversal patterns (..) are not allowed")

    # Handle hidden files
    hidden_check = (
        not allow_hidden
        and normalized_path.startswith(".")
        and "/" not in normalized_path
    )
    if hidden_check:
        # Allow common hidden files
        allowed_hidden = {".gitignore", ".env.example", ".claude", ".ai-forge.yaml"}
        if normalized_path not in allowed_hidden:
            raise ValueError("Hidden system files are not allowed")

    return normalized_path


def validate_path_within_project(file_path: Path, project_root: Path) -> None:
    """Validate that file path is safe and within project directory.

    Args:
        file_path: Path to validate
        project_root: Project root directory that path must be within

    Raises:
        FileSystemError: If path is unsafe or outside project directory
    """
    try:
        # Resolve to absolute paths to prevent path traversal
        resolved_path = file_path.resolve()
        resolved_root = project_root.resolve()

        # Check if path is within project directory
        if not str(resolved_path).startswith(str(resolved_root)):
            raise FileSystemError(
                f"File path '{file_path}' is outside project "
                f"directory '{project_root}'",
                path=str(file_path),
                operation="path_validation",
            )

        # Additional checks for common dangerous patterns
        path_str = str(resolved_path)

        # Block access to system directories
        dangerous_paths = ["/etc", "/usr", "/bin", "/var", "/sys", "/proc", "/dev"]
        for dangerous in dangerous_paths:
            if path_str.startswith(dangerous):
                raise FileSystemError(
                    f"Access to system directory '{dangerous}' is not allowed",
                    path=str(file_path),
                    operation="path_validation",
                )

    except (OSError, ValueError) as e:
        raise FileSystemError(
            f"Invalid file path: {file_path}",
            path=str(file_path),
            operation="path_validation",
        ) from e


def validate_project_name(name: str) -> str:
    """Validate project name format.

    Args:
        name: The project name to validate

    Returns:
        The validated project name

    Raises:
        ValueError: If name contains invalid characters
    """
    if not name:
        raise ValueError("Project name cannot be empty")

    # Allow alphanumeric, hyphens, and underscores only
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise ValueError(
            "Project name must contain only alphanumeric characters, "
            "hyphens, and underscores"
        )

    return name


def validate_template_content(content: str, max_size: int = 1024 * 1024) -> str:
    """Validate template content for security issues.

    Args:
        content: Template content to validate
        max_size: Maximum allowed size in bytes

    Returns:
        The validated content

    Raises:
        ValueError: If content contains security issues
    """
    if len(content.encode("utf-8")) > max_size:
        raise ValueError(f"Template content exceeds maximum size of {max_size} bytes")

    # Check for potentially dangerous patterns in templates
    dangerous_patterns = [
        r"{{.*__import__.*}}",  # Python imports
        r"{{.*eval\s*\(.*}}",  # Eval functions
        r"{{.*exec\s*\(.*}}",  # Exec functions
        r"{{.*subprocess.*}}",  # Process execution
        r"{{.*os\.system.*}}",  # System calls
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            raise ValueError(
                f"Template contains potentially dangerous pattern: {pattern}"
            )

    return content


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove dangerous characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove control characters
    filename = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)

    # Ensure filename is not empty and doesn't start with dot
    if not filename or filename.startswith("."):
        filename = "safe_" + filename

    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[: 255 - len(ext)] + ext

    return filename


def is_safe_command(command: str) -> bool:
    """Check if a command is safe to execute.

    Args:
        command: Command string to validate

    Returns:
        True if command appears safe, False otherwise
    """
    # List of dangerous command patterns
    dangerous_patterns = [
        r"rm\s+-rf\s+/",  # Recursive delete of root
        r"curl.*\|.*sh",  # Pipe to shell
        r"wget.*\|.*sh",  # Pipe to shell
        r"eval\s*\(",  # Eval functions
        r"exec\s*\(",  # Exec functions
        r">[>\s]*/dev/sd[a-z]",  # Writing to disk devices
        r"dd\s+if=.*of=",  # Disk imaging
        r"mkfs\.",  # Format filesystem
        r"fdisk",  # Disk partitioning
        r"mount\s+",  # Mount filesystems
        r"umount\s+",  # Unmount filesystems
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False

    return True


def validate_hook_command(command: str) -> str:
    """Validate a hook command for security.

    Args:
        command: Hook command to validate

    Returns:
        The validated command

    Raises:
        ValueError: If command contains security issues
    """
    if not command.strip():
        raise ValueError("Hook command cannot be empty")

    if not is_safe_command(command):
        raise ValueError(
            f"Hook command contains potentially dangerous patterns: {command}"
        )

    return command.strip()

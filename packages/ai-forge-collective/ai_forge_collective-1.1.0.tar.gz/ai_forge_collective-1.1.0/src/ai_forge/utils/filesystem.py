"""Filesystem utility functions for AI Forge.

This module provides secure file system operations with path validation,
permission checking, and safe file handling capabilities.
"""

import os
import shutil
import stat
from pathlib import Path
from typing import Optional

from ..exceptions import FileSystemError, ValidationError


def normalize_path(path: Path | str) -> Path:
    """Normalize a file path to prevent path traversal attacks.

    Args:
        path: Path to normalize

    Returns:
        Normalized Path object

    Raises:
        ValidationError: If path is invalid
    """
    try:
        if isinstance(path, str):
            path = Path(path)

        # Resolve to absolute path and normalize
        normalized = path.resolve()

        # Check for suspicious path components (after resolution)
        # Note: ~ is handled by resolve(), so we check the resolved path
        path_parts = normalized.parts
        dangerous_parts = {"..", "."}
        if any(part in dangerous_parts for part in path_parts):
            raise ValidationError(
                f"Path '{path}' contains dangerous path components",
                field_name="path",
                invalid_value=str(path),
            )

        return normalized

    except (OSError, ValueError) as e:
        raise ValidationError(
            f"Invalid path '{path}': {e}", field_name="path", invalid_value=str(path)
        ) from e


def is_safe_path(file_path: Path, base_path: Path) -> bool:
    """Check if file path is safe and within base directory.

    Args:
        file_path: Path to check
        base_path: Base directory that path should be within

    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Normalize both paths
        normalized_file = normalize_path(file_path)
        normalized_base = normalize_path(base_path)

        # Check if file path is within base directory
        return str(normalized_file).startswith(str(normalized_base))

    except (ValidationError, OSError):
        return False


def ensure_directory(dir_path: Path, mode: int = 0o755) -> None:
    """Ensure directory exists with proper permissions.

    Args:
        dir_path: Directory path to create
        mode: Directory permissions mode

    Raises:
        FileSystemError: If directory creation fails
    """
    try:
        dir_path.mkdir(parents=True, exist_ok=True, mode=mode)

        # Verify permissions were set correctly
        if dir_path.exists():
            current_mode = dir_path.stat().st_mode & 0o777
            if current_mode != mode:
                dir_path.chmod(mode)

    except OSError as e:
        raise FileSystemError(
            f"Cannot create directory '{dir_path}': {e}",
            path=str(dir_path),
            operation="create_directory",
        ) from e


def validate_file_permissions(
    file_path: Path, required_mode: Optional[int] = None
) -> None:
    """Validate file permissions are appropriate.

    Args:
        file_path: File path to check
        required_mode: Optional required permission mode

    Raises:
        FileSystemError: If file permissions are inappropriate
        ValidationError: If file doesn't exist
    """
    if not file_path.exists():
        raise ValidationError(
            f"File '{file_path}' does not exist",
            field_name="file_path",
            invalid_value=str(file_path),
        )

    try:
        file_stat = file_path.stat()
        current_mode = file_stat.st_mode

        # Check if file is world-writable (security risk)
        if current_mode & stat.S_IWOTH:
            raise FileSystemError(
                f"File '{file_path}' is world-writable (security risk)",
                path=str(file_path),
                operation="permission_check",
            )

        # Check if required mode is set
        if required_mode is not None:
            actual_mode = current_mode & 0o777
            if actual_mode != required_mode:
                raise FileSystemError(
                    f"File '{file_path}' has incorrect permissions: "
                    f"expected {oct(required_mode)}, got {oct(actual_mode)}",
                    path=str(file_path),
                    operation="permission_check",
                )

    except OSError as e:
        raise FileSystemError(
            f"Cannot check permissions for '{file_path}': {e}",
            path=str(file_path),
            operation="permission_check",
        ) from e


def safe_file_read(
    file_path: Path, base_path: Path, max_size: int = 10 * 1024 * 1024
) -> str:
    """Safely read file content with security checks.

    Args:
        file_path: File to read
        base_path: Base directory for path validation
        max_size: Maximum file size to read (default: 10MB)

    Returns:
        File content as string

    Raises:
        FileSystemError: If file reading fails or security checks fail
        ValidationError: If file is too large or path is invalid
    """
    # Validate path is safe
    if not is_safe_path(file_path, base_path):
        raise ValidationError(
            f"File path '{file_path}' is outside base directory '{base_path}'",
            field_name="file_path",
            invalid_value=str(file_path),
        )

    try:
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > max_size:
            raise ValidationError(
                f"File '{file_path}' is too large: {file_size} bytes (max: {max_size})",
                field_name="file_size",
                invalid_value=str(file_size),
            )

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except OSError as e:
        raise FileSystemError(
            f"Cannot read file '{file_path}': {e}",
            path=str(file_path),
            operation="read_file",
        ) from e


def safe_file_copy(
    source_path: Path,
    dest_path: Path,
    base_path: Path,
    preserve_permissions: bool = True,
) -> None:
    """Safely copy file with security validation.

    Args:
        source_path: Source file to copy
        dest_path: Destination path
        base_path: Base directory for path validation
        preserve_permissions: Whether to preserve source file permissions

    Raises:
        FileSystemError: If file copying fails
        ValidationError: If paths are invalid
    """
    # Validate both paths are safe
    if not is_safe_path(source_path, base_path):
        raise ValidationError(
            f"Source path '{source_path}' is outside base directory '{base_path}'",
            field_name="source_path",
            invalid_value=str(source_path),
        )

    if not is_safe_path(dest_path, base_path):
        raise ValidationError(
            f"Destination path '{dest_path}' is outside base directory '{base_path}'",
            field_name="dest_path",
            invalid_value=str(dest_path),
        )

    try:
        # Ensure destination directory exists
        ensure_directory(dest_path.parent)

        # Copy file
        shutil.copy2(source_path, dest_path)

        # Set safe permissions if not preserving
        if not preserve_permissions:
            # Remove world permissions, keep owner and group read/write
            dest_path.chmod(0o644)

    except (OSError, shutil.Error) as e:
        raise FileSystemError(
            f"Cannot copy file from '{source_path}' to '{dest_path}': {e}",
            path=str(dest_path),
            operation="copy_file",
        ) from e


def get_config_dir() -> Path:
    """Get the AI Forge configuration directory following XDG Base Directory
    specification.

    Returns:
        Path to the AI Forge config directory
    """
    # Use XDG_CONFIG_HOME if set, otherwise default to ~/.config
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        base_config = Path(config_home)
    else:
        base_config = Path.home() / ".config"

    return base_config / "ai-forge"


def get_user_templates_dir() -> Path:
    """Get the user templates directory within the config directory.

    Returns:
        Path to the user templates directory
    """
    return get_config_dir() / "templates"


def ensure_config_dir() -> Path:
    """Ensure the AI Forge config directory exists and return it.

    Returns:
        Path to the AI Forge config directory

    Raises:
        FileSystemError: If directory creation fails
    """
    config_dir = get_config_dir()
    ensure_directory(config_dir)
    return config_dir


def ensure_user_templates_dir() -> Path:
    """Ensure the user templates directory exists and return it.

    Returns:
        Path to the user templates directory

    Raises:
        FileSystemError: If directory creation fails
    """
    templates_dir = get_user_templates_dir()
    ensure_directory(templates_dir)
    return templates_dir

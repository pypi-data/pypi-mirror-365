"""File validation rules for the starter template."""

import json
import re
import stat
from pathlib import Path
from typing import Any

try:
    from ai_forge.exceptions import TemplateValidationError
except ImportError:
    # Fallback for testing
    class TemplateValidationError(Exception):  # type: ignore[no-redef]
        pass


def validate_claude_md_content(content: str, variables: dict[str, Any]) -> None:
    """Validate generated CLAUDE.md content.

    Args:
        content: Generated CLAUDE.md content
        variables: Template variables used for generation

    Raises:
        TemplateValidationError: If content is invalid
    """
    if not content or not content.strip():
        raise TemplateValidationError("CLAUDE.md content cannot be empty")

    # Check minimum required sections
    required_sections = [
        f"# {variables['project_name']}",
        "## Project Overview",
        "## Development Guidelines",
        "## Claude Code Configuration",
    ]

    for section in required_sections:
        if section not in content:
            raise TemplateValidationError(
                f"CLAUDE.md missing required section: {section}"
            )

    # Check that variables are properly substituted
    if "{{" in content or "}}" in content:
        raise TemplateValidationError(
            "CLAUDE.md contains unsubstituted template variables"
        )

    # Check for minimum content length
    if len(content.strip()) < 100:
        raise TemplateValidationError(
            "CLAUDE.md content is too short (minimum 100 characters)"
        )

    # Check that project name appears in content
    if variables["project_name"] not in content:
        raise TemplateValidationError("CLAUDE.md must contain the project name")

    # Check that description appears in content
    if variables["description"] not in content:
        raise TemplateValidationError("CLAUDE.md must contain the project description")


def validate_settings_json_content(content: str, variables: dict[str, Any]) -> None:
    """Validate generated settings.json content.

    Args:
        content: Generated settings.json content
        variables: Template variables used for generation

    Raises:
        TemplateValidationError: If content is invalid
    """
    if not content or not content.strip():
        raise TemplateValidationError("settings.json content cannot be empty")

    # Parse JSON to validate syntax
    try:
        settings = json.loads(content)
    except json.JSONDecodeError as e:
        raise TemplateValidationError(f"settings.json is not valid JSON: {e}")

    # Check required top-level sections
    required_sections = [
        "project",
        "claude",
        "editor",
        "development",
        "hooks",
        "security",
        "paths",
        "metadata",
    ]

    for section in required_sections:
        if section not in settings:
            raise TemplateValidationError(
                f"settings.json missing required section: {section}"
            )

    # Validate project section
    project = settings["project"]
    if project["name"] != variables["project_name"]:
        raise TemplateValidationError(
            "settings.json project name doesn't match template variable"
        )

    if project["description"] != variables["description"]:
        raise TemplateValidationError(
            "settings.json description doesn't match template variable"
        )

    if project["author"] != variables["author"]:
        raise TemplateValidationError(
            "settings.json author doesn't match template variable"
        )

    # Validate Claude permissions
    claude = settings["claude"]
    if "permissions" not in claude:
        raise TemplateValidationError(
            "settings.json missing Claude permissions section"
        )

    permissions = claude["permissions"]
    if "allowed" not in permissions or "denied" not in permissions:
        raise TemplateValidationError(
            "settings.json missing allowed or denied permissions"
        )

    # Check that dangerous permissions are denied
    dangerous_permissions = ["Execute", "Network", "SystemAccess", "FileSystem"]
    for perm in dangerous_permissions:
        if perm not in permissions["denied"]:
            raise TemplateValidationError(
                f"Dangerous permission '{perm}' must be in denied list"
            )
        if perm in permissions["allowed"]:
            raise TemplateValidationError(
                f"Dangerous permission '{perm}' cannot be in allowed list"
            )

    # Validate that at least Read permission is allowed
    if "Read" not in permissions["allowed"]:
        raise TemplateValidationError("Read permission must be in allowed list")

    # Validate editor configuration
    editor = settings["editor"]
    if editor["primary"] != variables["editor"]:
        raise TemplateValidationError(
            "settings.json editor doesn't match template variable"
        )

    # Validate hooks configuration
    hooks = settings["hooks"]
    format_hook = hooks.get("format_on_save", {})
    if format_hook.get("enabled") != variables["format_on_save"]:
        raise TemplateValidationError(
            "settings.json format_on_save doesn't match template variable"
        )


def validate_format_script_content(content: str, variables: dict[str, Any]) -> None:
    """Validate generated format-on-save.sh content.

    Args:
        content: Generated script content
        variables: Template variables used for generation

    Raises:
        TemplateValidationError: If content is invalid
    """
    if not content or not content.strip():
        raise TemplateValidationError("format-on-save.sh content cannot be empty")

    # Check that it starts with shebang
    lines = content.split("\n")
    if not lines[0].startswith("#!"):
        raise TemplateValidationError("format-on-save.sh must start with shebang")

    # Check for required security features
    security_features = [
        "set -euo pipefail",  # Strict error handling
        "readonly ",  # Read-only variables
        "timeout",  # Timeout protection
        "cleanup()",  # Cleanup function
        "trap cleanup EXIT",  # Error handling
    ]

    for feature in security_features:
        if feature not in content:
            raise TemplateValidationError(
                f"format-on-save.sh missing security feature: {feature}"
            )

    # Check that variables are properly substituted
    if "{{" in content or "}}" in content:
        raise TemplateValidationError(
            "format-on-save.sh contains unsubstituted template variables"
        )

    # Check that project name appears in content
    if variables["project_name"] not in content:
        raise TemplateValidationError("format-on-save.sh must contain the project name")

    # Check for dangerous string patterns (should not exist)
    dangerous_strings = [
        "rm -rf",
        "sudo ",
        "curl ",
        "wget ",
        "> /dev/",
        "| sh",
        "| bash",
        "$(curl",
        "$(wget",
    ]

    for pattern in dangerous_strings:
        if pattern in content:
            raise TemplateValidationError(
                f"format-on-save.sh contains dangerous pattern: {pattern}"
            )

    # Check for dangerous regex patterns
    dangerous_regexes = [
        r"\beval\s+[^']",  # eval as shell command (not 'yq eval')
        r"\bexec\s+[^']",  # exec as shell command
    ]

    for pattern in dangerous_regexes:
        if re.search(pattern, content):
            raise TemplateValidationError(
                f"format-on-save.sh contains dangerous pattern: {pattern}"
            )

    # Check minimum content length
    if len(content.strip()) < 500:
        raise TemplateValidationError(
            "format-on-save.sh content is too short (minimum 500 characters)"
        )


def validate_generated_file_permissions(file_path: Path) -> None:
    """Validate file permissions of generated files.

    Args:
        file_path: Path to the generated file

    Raises:
        TemplateValidationError: If file permissions are incorrect
    """
    if not file_path.exists():
        raise TemplateValidationError(f"Generated file does not exist: {file_path}")

    # Get file stats
    file_stat = file_path.stat()

    # Check that file is not world-writable
    if file_stat.st_mode & stat.S_IWOTH:
        raise TemplateValidationError(
            f"File {file_path} is world-writable (security risk)"
        )

    # For shell scripts, check that they are executable
    if file_path.suffix == ".sh" or file_path.name.endswith(".sh"):
        if not (file_stat.st_mode & stat.S_IXUSR):
            raise TemplateValidationError(f"Shell script {file_path} is not executable")

    # For configuration files, check that they are not executable
    config_extensions = {".json", ".yaml", ".yml", ".md", ".txt"}
    if file_path.suffix in config_extensions:
        if file_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            raise TemplateValidationError(
                f"Configuration file {file_path} should not be executable"
            )


def validate_generated_file_structure(
    output_path: Path, variables: dict[str, Any]
) -> None:
    """Validate the structure of generated files.

    Args:
        output_path: Path where files were generated
        variables: Template variables used for generation

    Raises:
        TemplateValidationError: If file structure is invalid
    """
    expected_files = [
        "CLAUDE.md",
        ".claude/settings.json",
        ".claude/hooks/format-on-save.sh",
    ]

    # Check that all expected files exist
    for file_path in expected_files:
        full_path = output_path / file_path
        if not full_path.exists():
            raise TemplateValidationError(f"Expected file not generated: {file_path}")

        # Validate file permissions
        validate_generated_file_permissions(full_path)

    # Check that .claude directory has correct permissions
    claude_dir = output_path / ".claude"
    if not claude_dir.is_dir():
        raise TemplateValidationError(".claude directory not created")

    # Check that hooks directory exists and has correct permissions
    hooks_dir = claude_dir / "hooks"
    if not hooks_dir.is_dir():
        raise TemplateValidationError(".claude/hooks directory not created")

    # Validate individual file contents
    claude_md_path = output_path / "CLAUDE.md"
    with open(claude_md_path, "r", encoding="utf-8") as f:
        validate_claude_md_content(f.read(), variables)

    settings_path = output_path / ".claude/settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        validate_settings_json_content(f.read(), variables)

    script_path = output_path / ".claude/hooks/format-on-save.sh"
    with open(script_path, "r", encoding="utf-8") as f:
        validate_format_script_content(f.read(), variables)


def validate_cross_platform_compatibility(output_path: Path) -> None:
    """Validate that generated files are cross-platform compatible.

    Args:
        output_path: Path where files were generated

    Raises:
        TemplateValidationError: If files have platform-specific issues
    """
    # Check for Windows-incompatible file names
    script_path = output_path / ".claude/hooks/format-on-save.sh"

    if script_path.exists():
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check line endings (should be LF for shell scripts)
        if "\r\n" in content:
            raise TemplateValidationError(
                "Shell script contains Windows line endings (should be LF)"
            )

        # Check for Windows-specific paths
        windows_patterns = [
            "C:\\",
            "D:\\",
            "Program Files",
            "\\Users\\",
            "\\Windows\\",
        ]

        for pattern in windows_patterns:
            if pattern in content:
                raise TemplateValidationError(
                    f"Shell script contains Windows-specific path: {pattern}"
                )

    # Check all text files for consistent encoding
    text_files = [
        "CLAUDE.md",
        ".claude/settings.json",
        ".claude/hooks/format-on-save.sh",
    ]

    for file_path in text_files:
        full_path = output_path / file_path
        if full_path.exists():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError:
                raise TemplateValidationError(f"File {file_path} is not valid UTF-8")

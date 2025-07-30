"""Base file generator class for AI Forge file generation engine."""

import json
import stat
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import jinja2
import yaml

from ..exceptions import FileSystemError, TemplateRenderError, ValidationError
from ..templates.security import validate_template_content, validate_template_variables


class FileGenerator(ABC):
    """Abstract base class for all file generators in AI Forge.

    This class provides the common interface and functionality for generating
    configuration files, scripts, and documentation with proper security
    validation and formatting.
    """

    def __init__(self) -> None:
        """Initialize file generator with secure Jinja2 environment."""
        # Configure Jinja2 environment with security settings
        self.env = jinja2.Environment(
            # Disable dangerous features for security
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
            # Prevent access to private attributes
            finalize=self._finalize_value,
        )

        # Remove dangerous globals
        self.env.globals.clear()

        # Add only safe built-ins
        self.env.globals.update(
            {
                "range": range,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "enumerate": enumerate,
                "zip": zip,
            }
        )

    def _finalize_value(self, value: Any) -> Any:
        """Finalize template values with security checks.

        Args:
            value: Value to finalize

        Returns:
            Finalized value

        Raises:
            ValidationError: If value contains security risks
        """
        # Convert None to empty string for safety
        if value is None:
            return ""

        # Block access to private attributes
        if isinstance(value, str) and value.startswith("_"):
            raise ValidationError("Access to private attributes is not allowed")

        return value

    def validate_path(self, file_path: Path, project_root: Path) -> None:
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
                    f"File path '{file_path}' is outside project directory "
                    f"'{project_root}'",
                    path=str(file_path),
                    operation="path_validation",
                )

            # Check for suspicious path components
            path_parts = file_path.parts
            dangerous_parts = {"..", ".", "~"}
            if any(part in dangerous_parts for part in path_parts):
                raise FileSystemError(
                    f"File path '{file_path}' contains dangerous path components",
                    path=str(file_path),
                    operation="path_validation",
                )

        except (OSError, ValueError) as e:
            raise FileSystemError(
                f"Invalid file path '{file_path}': {e}",
                path=str(file_path),
                operation="path_validation",
            ) from e

    def render_template(self, template_content: str, context: dict[str, Any]) -> str:
        """Render template content with context variables.

        Args:
            template_content: Template string to render
            context: Template variables for rendering

        Returns:
            Rendered content

        Raises:
            TemplateRenderError: If template rendering fails
            ValidationError: If context variables are invalid
        """
        # Validate context variables
        validate_template_variables(context)

        # Validate template content
        validate_template_content(template_content, Path("<string>"))

        try:
            template = self.env.from_string(template_content)
            return template.render(**context)
        except jinja2.TemplateError as e:
            raise TemplateRenderError(f"Template rendering failed: {e}") from e

    def write_file(
        self,
        file_path: Path,
        content: str,
        project_root: Path,
        executable: bool = False,
    ) -> None:
        """Write content to file with security validation.

        Args:
            file_path: Path where to write the file
            content: Content to write
            project_root: Project root directory for path validation
            executable: Whether to make file executable

        Raises:
            FileSystemError: If file writing fails
        """
        # Validate path security
        self.validate_path(file_path, project_root)

        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Set executable permissions if requested
            if executable:
                # Add execute permission for owner
                current_mode = file_path.stat().st_mode
                new_mode = current_mode | stat.S_IXUSR
                file_path.chmod(new_mode)

        except OSError as e:
            raise FileSystemError(
                f"Cannot write file '{file_path}': {e}",
                path=str(file_path),
                operation="write_file",
            ) from e

    def write_json_file(
        self, file_path: Path, data: dict[str, Any], project_root: Path, indent: int = 2
    ) -> None:
        """Write data to JSON file with validation.

        Args:
            file_path: Path where to write the JSON file
            data: Data to serialize as JSON
            project_root: Project root directory for path validation
            indent: JSON indentation level

        Raises:
            FileSystemError: If file writing fails
            ValidationError: If data cannot be serialized as JSON
        """
        try:
            # Validate JSON serialization
            content = json.dumps(
                data, indent=indent, ensure_ascii=False, sort_keys=True
            )
        except (TypeError, ValueError) as e:
            raise ValidationError(
                f"Cannot serialize data as JSON: {e}",
                field_name="json_data",
                invalid_value=str(data),
            ) from e

        self.write_file(file_path, content, project_root)

    def write_yaml_file(
        self, file_path: Path, data: dict[str, Any], project_root: Path
    ) -> None:
        """Write data to YAML file with validation.

        Args:
            file_path: Path where to write the YAML file
            data: Data to serialize as YAML
            project_root: Project root directory for path validation

        Raises:
            FileSystemError: If file writing fails
            ValidationError: If data cannot be serialized as YAML
        """
        try:
            # Validate YAML serialization
            content = yaml.dump(
                data,
                default_flow_style=False,
                sort_keys=True,
                allow_unicode=True,
                indent=2,
            )
        except yaml.YAMLError as e:
            raise ValidationError(
                f"Cannot serialize data as YAML: {e}",
                field_name="yaml_data",
                invalid_value=str(data),
            ) from e

        self.write_file(file_path, content, project_root)

    @abstractmethod
    def generate(
        self, output_path: Path, context: dict[str, Any], project_root: Path
    ) -> list[Path]:
        """Generate files based on context and write to output path.

        Args:
            output_path: Directory where to generate files
            context: Generation context and variables
            project_root: Project root directory for path validation

        Returns:
            List of generated file paths

        Raises:
            FileSystemError: If file generation fails
            TemplateRenderError: If template rendering fails
            ValidationError: If context is invalid
        """
        pass

    @abstractmethod
    def get_required_context_keys(self) -> list[str]:
        """Get list of required context keys for generation.

        Returns:
            List of required context key names
        """
        pass

    @abstractmethod
    def get_optional_context_keys(self) -> dict[str, Any]:
        """Get dictionary of optional context keys with default values.

        Returns:
            Dictionary mapping optional key names to default values
        """
        pass

    def validate_context(self, context: dict[str, Any]) -> None:
        """Validate that context contains all required keys.

        Args:
            context: Context to validate

        Raises:
            ValidationError: If required keys are missing
        """
        required_keys = self.get_required_context_keys()
        missing_keys = [key for key in required_keys if key not in context]

        if missing_keys:
            raise ValidationError(
                f"Missing required context keys: {', '.join(missing_keys)}",
                field_name="context",
                invalid_value=str(context),
            )

    def merge_context_defaults(self, context: dict[str, Any]) -> dict[str, Any]:
        """Merge context with default values for optional keys.

        Args:
            context: Input context

        Returns:
            Context merged with defaults
        """
        defaults = self.get_optional_context_keys()
        merged = defaults.copy()
        merged.update(context)
        return merged

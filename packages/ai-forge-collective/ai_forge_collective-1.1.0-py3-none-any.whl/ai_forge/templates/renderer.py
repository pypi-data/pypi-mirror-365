"""Template renderer for AI Forge template system."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

import jinja2

from ..exceptions import TemplateRenderError, TemplateSecurityError
from .security import validate_template_content, validate_template_variables

if TYPE_CHECKING:
    from .base import Template


class TemplateRenderer:
    """Renders templates using Jinja2 with security validation."""

    def __init__(self) -> None:
        """Initialize template renderer."""
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
        """
        # Convert None to empty string for safety
        if value is None:
            return ""

        # Block access to private attributes
        if isinstance(value, str) and value.startswith("_"):
            raise TemplateSecurityError("Access to private attributes is not allowed")

        return value

    def render_template(
        self,
        template: "Template",
        output_path: Path,
        context: dict[str, Any],
    ) -> None:
        """Render template to output directory.

        Args:
            template: Template to render
            output_path: Target directory for rendered files
            context: Template variables for rendering

        Raises:
            TemplateRenderError: If template rendering fails
        """
        # Validate context variables
        validate_template_variables(context)

        # Merge with default values
        full_context = template.get_variable_defaults().copy()
        full_context.update(context)

        # Check required variables
        required_vars = template.get_required_variables()
        missing_vars = [var for var in required_vars if var not in full_context]
        if missing_vars:
            raise TemplateRenderError(
                f"Missing required template variables: {', '.join(missing_vars)}",
                template_name=template.name,
                template_path=str(template.path),
            )

        # Create output directory
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise TemplateRenderError(
                f"Cannot create output directory: {e}",
                template_name=template.name,
                template_path=str(output_path),
            ) from e

        # Get template files from manifest
        from .manifest import TemplateManifest

        # Get manifest object (either from template or create temporary one)
        if hasattr(template, "_manifest"):
            manifest = template._manifest  # type: ignore[attr-defined]
        else:
            manifest = TemplateManifest(template.manifest_data)

        template_files = manifest.get_file_mapping()

        # Render all files using the mapping (source -> destination)
        self._render_file_mapping(template, template_files, output_path, full_context)

    def _render_file_mapping(
        self,
        template: "Template",
        file_mapping: dict[str, str],
        output_path: Path,
        context: dict[str, Any],
    ) -> None:
        """Render files from source -> destination mapping.

        Args:
            template: Template being rendered
            file_mapping: Dictionary mapping source files to destination paths
            output_path: Target directory for rendered files
            context: Template variables for rendering
        """
        for source_file, dest_file in file_mapping.items():
            source_path = template.path / source_file
            dest_path = output_path / dest_file

            self._render_single_file(template, source_path, dest_path, context)

    def _render_single_file(
        self,
        template: "Template",
        source_path: Path,
        dest_path: Path,
        context: dict[str, Any],
    ) -> None:
        """Render a single template file.

        Args:
            template: Template being rendered
            source_path: Source template file path
            dest_path: Destination file path
            context: Template variables for rendering
        """
        try:
            # Read template file
            with open(source_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        except OSError as e:
            raise TemplateRenderError(
                f"Cannot read template file '{source_path}': {e}",
                template_name=template.name,
                template_path=str(source_path),
            ) from e

        # Validate template content for security
        validate_template_content(template_content, source_path)

        try:
            # Render template
            jinja_template = self.env.from_string(template_content)
            rendered_content = jinja_template.render(**context)
        except jinja2.TemplateError as e:
            raise TemplateRenderError(
                f"Template rendering failed for '{source_path}': {e}",
                template_name=template.name,
                template_path=str(source_path),
            ) from e

        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Write rendered file
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(rendered_content)

            # Set appropriate file permissions
            self._set_file_permissions(dest_path)
        except OSError as e:
            raise TemplateRenderError(
                f"Cannot write rendered file '{dest_path}': {e}",
                template_name=template.name,
                template_path=str(dest_path),
            ) from e

    def _set_file_permissions(self, file_path: Path) -> None:
        """Set appropriate file permissions based on file type.

        Args:
            file_path: Path to the file to set permissions for
        """
        import stat

        # Shell scripts should be executable
        if file_path.suffix == ".sh" or file_path.name.endswith(".sh"):
            # Make executable for owner, readable for owner and group
            file_path.chmod(stat.S_IRWXU | stat.S_IRGRP)
        else:
            # Regular files: readable and writable for owner, readable for group
            file_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)

    def render_string(self, template_string: str, context: dict[str, Any]) -> str:
        """Render a template string with context.

        Args:
            template_string: Template string to render
            context: Template variables for rendering

        Returns:
            Rendered string

        Raises:
            TemplateRenderError: If rendering fails
        """
        # Validate context variables
        validate_template_variables(context)

        # Validate template content
        validate_template_content(template_string, Path("<string>"))

        try:
            template = self.env.from_string(template_string)
            return template.render(**context)
        except jinja2.TemplateError as e:
            raise TemplateRenderError(f"Template string rendering failed: {e}") from e

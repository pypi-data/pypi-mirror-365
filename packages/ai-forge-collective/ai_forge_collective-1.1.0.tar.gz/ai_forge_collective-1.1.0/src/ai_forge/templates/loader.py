"""Template loader for AI Forge template system."""

from pathlib import Path
from typing import Any

import yaml

from ..exceptions import TemplateError, TemplateValidationError
from .base import Template
from .manifest import TemplateManifest
from .security import validate_template_path


class FileSystemTemplate(Template):
    """Template implementation that loads from filesystem."""

    def __init__(self, path: Path, manifest_data: dict[str, Any]) -> None:
        """Initialize filesystem template.

        Args:
            path: Path to the template directory
            manifest_data: Parsed template manifest data
        """
        super().__init__(path, manifest_data)
        self._manifest = TemplateManifest(manifest_data)

    def validate(self) -> bool:
        """Validate template structure and security.

        Returns:
            True if template is valid and safe to use

        Raises:
            TemplateValidationError: If template validation fails
        """
        # Validate manifest
        self._manifest.validate()

        # Check that template directory exists
        if not self.path.exists():
            raise TemplateValidationError(
                f"Template directory does not exist: {self.path}",
                template_path=str(self.path),
            )

        if not self.path.is_dir():
            raise TemplateValidationError(
                f"Template path is not a directory: {self.path}",
                template_path=str(self.path),
            )

        # Validate all template files exist and are secure
        template_files = self._manifest.get_template_files()
        for file_path in template_files:
            full_path = self.path / file_path

            # Security validation
            validate_template_path(full_path, self.path)

            # Check file exists
            if not full_path.exists():
                raise TemplateValidationError(
                    f"Template file does not exist: {file_path}",
                    template_path=str(full_path),
                )

        return True

    def render(self, output_path: Path, context: dict[str, Any]) -> None:
        """Render template to output directory.

        Args:
            output_path: Target directory for rendered template
            context: Template variables for rendering

        Raises:
            TemplateRenderError: If template rendering fails
        """
        # This will be implemented in the renderer module
        from .renderer import TemplateRenderer

        renderer = TemplateRenderer()
        renderer.render_template(self, output_path, context)


class FileSystemLoader:
    """Loads templates from the filesystem."""

    def __init__(self, base_path: Path) -> None:
        """Initialize filesystem loader.

        Args:
            base_path: Base directory to search for templates
        """
        self.base_path = base_path.resolve()

    def load_template(self, template_name: str) -> FileSystemTemplate:
        """Load a template by name.

        Args:
            template_name: Name of the template to load

        Returns:
            Loaded template instance

        Raises:
            TemplateError: If template cannot be loaded
        """
        template_path = self.base_path / template_name

        # Security validation
        validate_template_path(template_path, self.base_path)

        if not template_path.exists():
            raise TemplateError(
                f"Template not found: {template_name}",
                template_name=template_name,
                template_path=str(template_path),
            )

        if not template_path.is_dir():
            raise TemplateError(
                f"Template path is not a directory: {template_name}",
                template_name=template_name,
                template_path=str(template_path),
            )

        # Load manifest
        manifest_path = template_path / "template.yaml"
        if not manifest_path.exists():
            raise TemplateError(
                f"Template manifest not found: {template_name}/template.yaml",
                template_name=template_name,
                template_path=str(manifest_path),
            )

        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise TemplateError(
                f"Invalid YAML in template manifest: {e}",
                template_name=template_name,
                template_path=str(manifest_path),
            ) from e
        except OSError as e:
            raise TemplateError(
                f"Cannot read template manifest: {e}",
                template_name=template_name,
                template_path=str(manifest_path),
            ) from e

        if not isinstance(manifest_data, dict):
            raise TemplateError(
                "Template manifest must be a YAML object",
                template_name=template_name,
                template_path=str(manifest_path),
            )

        # Create and validate template
        template = FileSystemTemplate(template_path, manifest_data)
        template.validate()

        return template

    def list_templates(self) -> list[str]:
        """List all available templates.

        Returns:
            List of template names
        """
        if not self.base_path.exists():
            return []

        templates = []
        for item in self.base_path.iterdir():
            if item.is_dir():
                manifest_path = item / "template.yaml"
                if manifest_path.exists():
                    templates.append(item.name)

        return sorted(templates)

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists.

        Args:
            template_name: Name of the template to check

        Returns:
            True if template exists and has valid manifest
        """
        try:
            template_path = self.base_path / template_name
            validate_template_path(template_path, self.base_path)

            if not template_path.is_dir():
                return False

            manifest_path = template_path / "template.yaml"
            return manifest_path.exists()
        except Exception:
            return False


class MultiPathLoader:
    """Loads templates from multiple filesystem paths."""

    def __init__(self, search_paths: list[Path]) -> None:
        """Initialize multi-path loader.

        Args:
            search_paths: List of directories to search for templates
                (in priority order)
        """
        self.search_paths = [path.resolve() for path in search_paths]
        self._loaders = [FileSystemLoader(path) for path in self.search_paths]

    def load_template(self, template_name: str) -> FileSystemTemplate:
        """Load a template by name from the first path that contains it.

        Args:
            template_name: Name of the template to load

        Returns:
            Loaded template instance

        Raises:
            TemplateError: If template cannot be found in any search path
        """
        for loader in self._loaders:
            if loader.template_exists(template_name):
                return loader.load_template(template_name)

        # Template not found in any path
        search_path_strs = [str(path) for path in self.search_paths]
        raise TemplateError(
            f"Template not found: {template_name}",
            template_name=template_name,
            details={"searched_paths": search_path_strs},
        )

    def list_templates(self) -> list[str]:
        """List all available templates from all search paths.

        Returns:
            List of unique template names (with user templates taking priority)
        """
        all_templates = set()
        for loader in self._loaders:
            all_templates.update(loader.list_templates())
        return sorted(all_templates)

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists in any search path.

        Args:
            template_name: Name of the template to check

        Returns:
            True if template exists in any search path
        """
        return any(loader.template_exists(template_name) for loader in self._loaders)

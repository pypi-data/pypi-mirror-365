"""Base template class for AI Forge template system."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Template(ABC):
    """Abstract base class for all templates in AI Forge.

    This class defines the interface that all templates must implement
    for loading, validation, and rendering.
    """

    def __init__(self, path: Path, manifest_data: dict[str, Any]) -> None:
        """Initialize template with path and manifest data.

        Args:
            path: Path to the template directory
            manifest_data: Parsed template manifest data
        """
        self.path = path
        self.manifest_data = manifest_data
        self.name = manifest_data.get("name", path.name)
        self.description = manifest_data.get("description", "")
        self.version = manifest_data.get("version", "1.0.0")
        self.language = manifest_data.get("language", "")

    @abstractmethod
    def validate(self) -> bool:
        """Validate template structure and security.

        Returns:
            True if template is valid and safe to use

        Raises:
            TemplateValidationError: If template validation fails
        """
        pass

    @abstractmethod
    def render(self, output_path: Path, context: dict[str, Any]) -> None:
        """Render template to output directory.

        Args:
            output_path: Target directory for rendered template
            context: Template variables for rendering

        Raises:
            TemplateRenderError: If template rendering fails
        """
        pass

    def get_required_variables(self) -> list[str]:
        """Get list of required template variables.

        Returns:
            List of variable names required for template rendering
        """
        return self.manifest_data.get("variables", {}).get("required", [])

    def get_optional_variables(self) -> list[str]:
        """Get list of optional template variables.

        Returns:
            List of optional variable names with defaults
        """
        return list(self.manifest_data.get("variables", {}).get("optional", {}).keys())

    def get_variable_defaults(self) -> dict[str, Any]:
        """Get default values for optional variables.

        Returns:
            Dictionary mapping variable names to default values
        """
        return self.manifest_data.get("variables", {}).get("optional", {})

"""Configuration schema models using Pydantic for AI Forge."""

import re
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FileConfig(BaseModel):
    """Configuration for files to be generated.

    Validates file paths to prevent directory traversal attacks and ensures
    files are created within safe boundaries.
    """

    path: str = Field(..., description="Relative path where file will be created")
    content: str = Field(..., description="Template content for the file")

    @field_validator("path")
    @classmethod
    def validate_path_security(cls, value: str) -> str:
        """Validate path to prevent directory traversal attacks.

        Args:
            value: The file path to validate

        Returns:
            The validated path string

        Raises:
            ValueError: If path contains dangerous patterns
        """
        if not value:
            raise ValueError("Path cannot be empty")

        # Normalize path and check for directory traversal
        normalized_path = Path(value).as_posix()

        # Prevent absolute paths (Unix and Windows style)
        if Path(normalized_path).is_absolute() or (
            len(value) > 1 and value[1] == ":" and value[0].isalpha()
        ):
            raise ValueError("Absolute paths are not allowed")

        # Prevent directory traversal patterns
        path_parts = normalized_path.split("/")
        if ".." in path_parts or any(part.startswith("..") for part in path_parts):
            raise ValueError("Path traversal patterns (..) are not allowed")

        # Prevent hidden system files
        if normalized_path.startswith(".") and "/" not in normalized_path:
            if normalized_path not in {".gitignore", ".env.example", ".claude"}:
                raise ValueError("Hidden system files are not allowed")

        return normalized_path


class TemplateConfig(BaseModel):
    """Configuration for AI Forge templates.

    Contains template metadata and validation for semantic versioning.
    """

    name: str = Field(
        ..., description="Template name (alphanumeric, hyphens, underscores)"
    )
    description: str = Field(..., description="Human-readable template description")
    version: str = Field(..., description="Semantic version (x.y.z format)")

    @field_validator("name")
    @classmethod
    def validate_template_name(cls, value: str) -> str:
        """Validate template name format.

        Args:
            value: The template name to validate

        Returns:
            The validated template name

        Raises:
            ValueError: If name contains invalid characters
        """
        if not value:
            raise ValueError("Template name cannot be empty")

        # Allow alphanumeric, hyphens, and underscores only
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValueError(
                "Template name must contain only alphanumeric characters, "
                "hyphens, and underscores"
            )

        return value

    @field_validator("version")
    @classmethod
    def validate_semantic_version(cls, value: str) -> str:
        """Validate semantic version format (x.y.z).

        Args:
            value: The version string to validate

        Returns:
            The validated version string

        Raises:
            ValueError: If version is not in semantic version format
        """
        if not value:
            raise ValueError("Version cannot be empty")

        # Validate semantic version pattern (x.y.z where x, y, z are integers)
        if not re.match(r"^\d+\.\d+\.\d+$", value):
            raise ValueError("Version must be in semantic version format (x.y.z)")

        return value


class AIForgeConfig(BaseModel):
    """Main AI Forge configuration.

    Root configuration object that contains project settings and references
    to templates and files to be generated.
    """

    project_name: str = Field(
        ..., description="Project name (alphanumeric, hyphens, underscores)"
    )
    template_name: Optional[str] = Field(
        None, description="Name of the template to use"
    )
    files: list[FileConfig] = Field(
        default_factory=list, description="List of files to generate"
    )

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        """Validate project name format.

        Args:
            value: The project name to validate

        Returns:
            The validated project name

        Raises:
            ValueError: If name contains invalid characters
        """
        if not value:
            raise ValueError("Project name cannot be empty")

        # Allow alphanumeric, hyphens, and underscores only
        if not re.match(r"^[a-zA-Z0-9_-]+$", value):
            raise ValueError(
                "Project name must contain only alphanumeric characters, "
                "hyphens, and underscores"
            )

        return value

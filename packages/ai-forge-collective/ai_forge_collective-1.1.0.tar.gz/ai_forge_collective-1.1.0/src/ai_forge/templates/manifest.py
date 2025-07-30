"""Template manifest handling for AI Forge template system."""

from typing import Any

from ..exceptions import TemplateValidationError


class TemplateManifest:
    """Handles parsing and validation of template manifest files."""

    # Required fields in template manifest
    REQUIRED_FIELDS = {"name", "description", "version", "language"}

    # Optional fields with their expected types
    OPTIONAL_FIELDS = {
        "files": (list, dict),
        "variables": dict,
        "dependencies": list,
        "tags": list,
        "author": str,
        "license": str,
        "min_ai_forge_version": str,
    }

    def __init__(self, manifest_data: dict[str, Any]) -> None:
        """Initialize template manifest.

        Args:
            manifest_data: Raw manifest data from template.yaml
        """
        self.data = manifest_data
        self._validate_structure()

    def _validate_structure(self) -> None:
        """Validate the basic structure of the manifest.

        Raises:
            TemplateValidationError: If manifest structure is invalid
        """
        if not isinstance(self.data, dict):
            raise TemplateValidationError("Template manifest must be a dictionary")

        # Check required fields
        missing_fields = self.REQUIRED_FIELDS - set(self.data.keys())
        if missing_fields:
            raise TemplateValidationError(
                f"Template manifest missing required fields: "
                f"{', '.join(missing_fields)}"
            )

        # Validate field types
        for field, value in self.data.items():
            if field in self.REQUIRED_FIELDS:
                if not isinstance(value, str):
                    raise TemplateValidationError(
                        f"Required field '{field}' must be a string, "
                        f"got {type(value).__name__}"
                    )
                if not value.strip():
                    raise TemplateValidationError(
                        f"Required field '{field}' cannot be empty"
                    )

            elif field in self.OPTIONAL_FIELDS:
                expected_types = self.OPTIONAL_FIELDS[field]
                if not isinstance(expected_types, tuple):
                    expected_types = (expected_types,)

                if not isinstance(value, expected_types):
                    type_names = " or ".join(t.__name__ for t in expected_types)
                    raise TemplateValidationError(
                        f"Field '{field}' must be {type_names}, "
                        f"got {type(value).__name__}"
                    )

    def validate(self) -> None:
        """Perform comprehensive validation of the manifest.

        Raises:
            TemplateValidationError: If manifest validation fails
        """
        self._validate_structure()
        self._validate_variables()
        self._validate_files()
        self._validate_dependencies()

    def _validate_variables(self) -> None:
        """Validate the variables section of the manifest.

        Raises:
            TemplateValidationError: If variables section is invalid
        """
        variables = self.data.get("variables", {})
        if not isinstance(variables, dict):
            raise TemplateValidationError("Variables section must be a dictionary")

        # Validate required variables
        required = variables.get("required", [])
        if not isinstance(required, list):
            raise TemplateValidationError("Required variables must be a list")

        for var in required:
            if not isinstance(var, str):
                raise TemplateValidationError(
                    f"Required variable name must be a string, got {type(var).__name__}"
                )
            if not var.strip():
                raise TemplateValidationError("Required variable name cannot be empty")

        # Validate optional variables
        optional = variables.get("optional", {})
        if not isinstance(optional, dict):
            raise TemplateValidationError("Optional variables must be a dictionary")

        for var_name, default_value in optional.items():
            if not isinstance(var_name, str):
                raise TemplateValidationError(
                    f"Optional variable name must be a string, "
                    f"got {type(var_name).__name__}"
                )
            if not var_name.strip():
                raise TemplateValidationError("Optional variable name cannot be empty")

    def _validate_files(self) -> None:
        """Validate the files section of the manifest.

        Raises:
            TemplateValidationError: If files section is invalid
        """
        files = self.data.get("files", [])

        if isinstance(files, list):
            for file_path in files:
                if not isinstance(file_path, str):
                    raise TemplateValidationError(
                        f"File path must be a string, got {type(file_path).__name__}"
                    )
                if not file_path.strip():
                    raise TemplateValidationError("File path cannot be empty")

                # Check for dangerous path patterns
                if ".." in file_path or file_path.startswith("/"):
                    raise TemplateValidationError(
                        f"File path '{file_path}' contains dangerous patterns"
                    )

        elif isinstance(files, dict):
            for source, dest in files.items():
                if not isinstance(source, str) or not isinstance(dest, str):
                    raise TemplateValidationError(
                        "File mapping keys and values must be strings"
                    )
                if not source.strip() or not dest.strip():
                    raise TemplateValidationError("File mapping paths cannot be empty")

                # Check for dangerous path patterns
                for path in [source, dest]:
                    if ".." in path or path.startswith("/"):
                        raise TemplateValidationError(
                            f"File path '{path}' contains dangerous patterns"
                        )
        else:
            raise TemplateValidationError("Files section must be a list or dictionary")

    def _validate_dependencies(self) -> None:
        """Validate the dependencies section of the manifest.

        Raises:
            TemplateValidationError: If dependencies section is invalid
        """
        dependencies = self.data.get("dependencies", [])
        if not isinstance(dependencies, list):
            raise TemplateValidationError("Dependencies must be a list")

        for dep in dependencies:
            if not isinstance(dep, str):
                raise TemplateValidationError(
                    f"Dependency must be a string, got {type(dep).__name__}"
                )
            if not dep.strip():
                raise TemplateValidationError("Dependency cannot be empty")

    # Getter methods for template properties

    def get_name(self) -> str:
        """Get template name."""
        return self.data["name"]

    def get_description(self) -> str:
        """Get template description."""
        return self.data["description"]

    def get_version(self) -> str:
        """Get template version."""
        return self.data["version"]

    def get_language(self) -> str:
        """Get template language."""
        return self.data["language"]

    def get_template_files(self) -> list[str]:
        """Get list of template files to process.

        Returns:
            List of file paths relative to template directory
        """
        files = self.data.get("files", [])

        if isinstance(files, list):
            return files
        elif isinstance(files, dict):
            return list(files.keys())
        else:
            return []

    def get_file_mapping(self) -> dict[str, str]:
        """Get file mapping from source to destination.

        Returns:
            Dictionary mapping source files to destination paths
        """
        files = self.data.get("files", [])

        if isinstance(files, dict):
            return files
        elif isinstance(files, list):
            # Create identity mapping for list format
            return {f: f for f in files}
        else:
            return {}

    def get_required_variables(self) -> list[str]:
        """Get list of required template variables."""
        return self.data.get("variables", {}).get("required", [])

    def get_optional_variables(self) -> dict[str, Any]:
        """Get dictionary of optional variables with defaults."""
        return self.data.get("variables", {}).get("optional", {})

    def get_dependencies(self) -> list[str]:
        """Get list of template dependencies."""
        return self.data.get("dependencies", [])

    def get_tags(self) -> list[str]:
        """Get list of template tags."""
        return self.data.get("tags", [])

    def get_author(self) -> str:
        """Get template author."""
        return self.data.get("author", "")

    def get_license(self) -> str:
        """Get template license."""
        return self.data.get("license", "")

    def get_min_ai_forge_version(self) -> str:
        """Get minimum AI Forge version required."""
        return self.data.get("min_ai_forge_version", "")

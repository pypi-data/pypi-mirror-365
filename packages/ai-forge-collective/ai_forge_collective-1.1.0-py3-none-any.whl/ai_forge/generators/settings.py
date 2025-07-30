"""Generator for settings.json configuration files."""

from pathlib import Path
from typing import Any

from .base import FileGenerator


class SettingsGenerator(FileGenerator):
    """Generator for settings.json configuration files.

    Creates settings.json files with project-specific configurations,
    tool settings, and development environment preferences.
    """

    def get_required_context_keys(self) -> list[str]:
        """Get list of required context keys for settings.json generation.

        Returns:
            List of required context key names
        """
        return [
            "project_name",
            "language",
        ]

    def get_optional_context_keys(self) -> dict[str, Any]:
        """Get dictionary of optional context keys with default values.

        Returns:
            Dictionary mapping optional key names to default values
        """
        return {
            "python_version": "3.12",
            "package_manager": "uv",
            "testing_framework": "pytest",
            "linting_tools": ["ruff", "mypy"],
            "formatter": "ruff",
            "type_checker": "mypy",
            "editor_config": {
                "tab_size": 4,
                "insert_final_newline": True,
                "trim_trailing_whitespace": True,
                "charset": "utf-8",
            },
            "test_config": {
                "test_paths": ["tests/"],
                "coverage_threshold": 90,
                "fail_under": 90,
            },
            "lint_config": {
                "line_length": 88,
                "target_version": "py312",
                "select": ["E", "W", "F", "I", "N", "B", "C4", "UP"],
                "ignore": ["E203", "W503"],
            },
            "mypy_config": {
                "python_version": "3.12",
                "strict": True,
                "warn_return_any": True,
                "warn_unused_configs": True,
                "disallow_untyped_defs": True,
            },
            "environment": {"development": True, "debug": False, "log_level": "INFO"},
            "paths": {
                "src": "src/",
                "tests": "tests/",
                "docs": "docs/",
                "config": "config/",
            },
            "custom_settings": {},
        }

    def _build_settings_data(self, context: dict[str, Any]) -> dict[str, Any]:
        """Build the complete settings data structure.

        Args:
            context: Generation context

        Returns:
            Complete settings dictionary
        """
        settings = {
            "project": {
                "name": context["project_name"],
                "language": context["language"],
                "version": "1.0.0",
            },
            "development": {
                "python_version": context["python_version"],
                "package_manager": context["package_manager"],
                "testing_framework": context["testing_framework"],
                "linting_tools": context["linting_tools"],
                "formatter": context["formatter"],
                "type_checker": context["type_checker"],
            },
            "editor": context["editor_config"],
            "testing": context["test_config"],
            "linting": context["lint_config"],
            "type_checking": context["mypy_config"],
            "environment": context["environment"],
            "paths": context["paths"],
        }

        # Add custom settings if provided
        if context["custom_settings"]:
            settings.update(context["custom_settings"])

        # Add Python-specific settings if language is Python
        if context["language"].lower() == "python":
            settings["python"] = {
                "interpreter": f"python{context['python_version']}",
                "venv_path": ".venv",
                "requirements_files": ["requirements.txt", "requirements-dev.txt"],
                "import_sorting": {
                    "tool": "ruff",
                    "profile": "black",
                    "multi_line_output": 3,
                },
                "docstring_style": "google",
            }

        return settings

    def _add_tool_specific_config(
        self, settings: dict[str, Any], context: dict[str, Any]
    ) -> None:
        """Add tool-specific configuration sections.

        Args:
            settings: Settings dictionary to modify
            context: Generation context
        """
        # Add pytest configuration
        if context["testing_framework"] == "pytest":
            settings["pytest"] = {
                "testpaths": context["test_config"]["test_paths"],
                "python_files": ["test_*.py", "*_test.py"],
                "python_classes": ["Test*"],
                "python_functions": ["test_*"],
                "addopts": [
                    "--strict-markers",
                    "--strict-config",
                    f"--cov={context['paths']['src']}",
                    f"--cov-fail-under={context['test_config']['fail_under']}",
                    "--cov-report=term-missing",
                    "--cov-report=html",
                ],
                "markers": [
                    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
                    "integration: marks tests as integration tests",
                    "unit: marks tests as unit tests",
                ],
            }

        # Add ruff configuration
        if "ruff" in context["linting_tools"]:
            settings["ruff"] = {
                "line-length": context["lint_config"]["line_length"],
                "target-version": context["lint_config"]["target_version"],
                "select": context["lint_config"]["select"],
                "ignore": context["lint_config"]["ignore"],
                "fixable": ["ALL"],
                "unfixable": [],
                "exclude": [
                    ".bzr",
                    ".direnv",
                    ".eggs",
                    ".git",
                    ".hg",
                    ".mypy_cache",
                    ".nox",
                    ".pants.d",
                    ".pytype",
                    ".ruff_cache",
                    ".svn",
                    ".tox",
                    ".venv",
                    "__pypackages__",
                    "_build",
                    "buck-out",
                    "build",
                    "dist",
                    "node_modules",
                    "venv",
                ],
            }

        # Add mypy configuration
        if context["type_checker"] == "mypy":
            settings["mypy"] = context["mypy_config"].copy()
            settings["mypy"]["files"] = [context["paths"]["src"]]
            settings["mypy"]["exclude"] = ["build/", "dist/", ".venv/", ".mypy_cache/"]

    def generate(
        self, output_path: Path, context: dict[str, Any], project_root: Path
    ) -> list[Path]:
        """Generate settings.json file based on context.

        Args:
            output_path: Directory where to generate the file
            context: Generation context and variables
            project_root: Project root directory for path validation

        Returns:
            List containing the generated settings.json file path

        Raises:
            FileSystemError: If file generation fails
            ValidationError: If context is invalid
        """
        # Validate context
        self.validate_context(context)

        # Merge with defaults
        full_context = self.merge_context_defaults(context)

        # Build settings data
        settings_data = self._build_settings_data(full_context)

        # Add tool-specific configuration
        self._add_tool_specific_config(settings_data, full_context)

        # Write JSON file
        settings_path = output_path / "settings.json"
        self.write_json_file(settings_path, settings_data, project_root, indent=2)

        return [settings_path]

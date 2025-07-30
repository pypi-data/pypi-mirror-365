"""Configuration loading and saving utilities for AI Forge."""

from pathlib import Path
from typing import Any, Union

import yaml

from ..exceptions import AIForgeError
from .config import AIForgeConfig, TemplateConfig


class ConfigLoadError(AIForgeError):
    """Error loading configuration from file."""


class ConfigSaveError(AIForgeError):
    """Error saving configuration to file."""


class ConfigLoader:
    """Utility class for loading and saving AI Forge configurations.

    Provides methods to load configurations from YAML files and save them
    back with proper error handling and validation.
    """

    @staticmethod
    def load_config(file_path: Union[str, Path]) -> AIForgeConfig:
        """Load AI Forge configuration from YAML file.

        Args:
            file_path: Path to the YAML configuration file

        Returns:
            Validated AIForgeConfig instance

        Raises:
            ConfigLoadError: If file cannot be read or parsed
            ValidationError: If configuration data is invalid
        """
        path = Path(file_path)

        try:
            if not path.exists():
                raise ConfigLoadError(f"Configuration file not found: {path}")

            if not path.is_file():
                raise ConfigLoadError(f"Path is not a file: {path}")

            with path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            if data is None:
                data = {}

            return AIForgeConfig.model_validate(data)

        except yaml.YAMLError as e:
            raise ConfigLoadError(f"Invalid YAML in {path}: {e}") from e
        except OSError as e:
            raise ConfigLoadError(f"Cannot read file {path}: {e}") from e

    @staticmethod
    def load_template_config(file_path: Union[str, Path]) -> TemplateConfig:
        """Load template configuration from YAML file.

        Args:
            file_path: Path to the YAML template configuration file

        Returns:
            Validated TemplateConfig instance

        Raises:
            ConfigLoadError: If file cannot be read or parsed
            ValidationError: If configuration data is invalid
        """
        path = Path(file_path)

        try:
            if not path.exists():
                raise ConfigLoadError(f"Template configuration file not found: {path}")

            if not path.is_file():
                raise ConfigLoadError(f"Path is not a file: {path}")

            with path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            if data is None:
                raise ConfigLoadError(f"Empty template configuration: {path}")

            return TemplateConfig.model_validate(data)

        except yaml.YAMLError as e:
            raise ConfigLoadError(f"Invalid YAML in {path}: {e}") from e
        except OSError as e:
            raise ConfigLoadError(f"Cannot read file {path}: {e}") from e

    @staticmethod
    def save_config(
        config: AIForgeConfig, file_path: Union[str, Path], create_dirs: bool = True
    ) -> None:
        """Save AI Forge configuration to YAML file.

        Args:
            config: The configuration to save
            file_path: Path where to save the configuration
            create_dirs: Whether to create parent directories if they don't exist

        Raises:
            ConfigSaveError: If file cannot be written
        """
        path = Path(file_path)

        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict and clean up None values
            data = config.model_dump(exclude_none=True)

            with path.open("w", encoding="utf-8") as file:
                yaml.safe_dump(
                    data, file, default_flow_style=False, indent=2, sort_keys=False
                )

        except OSError as e:
            raise ConfigSaveError(f"Cannot write file {path}: {e}") from e

    @staticmethod
    def save_template_config(
        config: TemplateConfig, file_path: Union[str, Path], create_dirs: bool = True
    ) -> None:
        """Save template configuration to YAML file.

        Args:
            config: The template configuration to save
            file_path: Path where to save the configuration
            create_dirs: Whether to create parent directories if they don't exist

        Raises:
            ConfigSaveError: If file cannot be written
        """
        path = Path(file_path)

        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict and clean up None values
            data = config.model_dump(exclude_none=True)

            with path.open("w", encoding="utf-8") as file:
                yaml.safe_dump(
                    data, file, default_flow_style=False, indent=2, sort_keys=False
                )

        except OSError as e:
            raise ConfigSaveError(f"Cannot write file {path}: {e}") from e

    @staticmethod
    def load_yaml_data(file_path: Union[str, Path]) -> dict[str, Any]:
        """Load raw YAML data from file.

        Args:
            file_path: Path to the YAML file

        Returns:
            Raw dictionary data from YAML file

        Raises:
            ConfigLoadError: If file cannot be read or parsed
        """
        path = Path(file_path)

        try:
            if not path.exists():
                raise ConfigLoadError(f"File not found: {path}")

            if not path.is_file():
                raise ConfigLoadError(f"Path is not a file: {path}")

            with path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            return data if data is not None else {}

        except yaml.YAMLError as e:
            raise ConfigLoadError(f"Invalid YAML in {path}: {e}") from e
        except OSError as e:
            raise ConfigLoadError(f"Cannot read file {path}: {e}") from e

    @staticmethod
    def create_default_config(project_name: str) -> AIForgeConfig:
        """Create a default AI Forge configuration.

        Args:
            project_name: Name of the project

        Returns:
            Default AIForgeConfig instance
        """
        return AIForgeConfig(
            project_name=project_name, template_name="starter", files=[]
        )

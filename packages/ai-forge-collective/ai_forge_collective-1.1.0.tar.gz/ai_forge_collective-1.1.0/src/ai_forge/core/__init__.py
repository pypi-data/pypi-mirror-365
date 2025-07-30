"""Core AI Forge modules for configuration management (MVP only)."""

from .config import AIForgeConfig, FileConfig, TemplateConfig
from .loader import ConfigLoader, ConfigLoadError, ConfigSaveError

__all__ = [
    "AIForgeConfig",
    "FileConfig",
    "TemplateConfig",
    "ConfigLoader",
    "ConfigLoadError",
    "ConfigSaveError",
    # Detection system moved to p2/language-detection branch
]

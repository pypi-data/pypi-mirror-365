"""File generation engine for AI Forge.

This module provides specialized file generators that create configuration files,
scripts, and documentation with proper formatting and security validation.
"""

from .base import FileGenerator
from .claude_md import ClaudeMdGenerator
from .hooks import HooksGenerator
from .mcp import McpGenerator
from .settings import SettingsGenerator

__all__ = [
    "FileGenerator",
    "ClaudeMdGenerator",
    "HooksGenerator",
    "McpGenerator",
    "SettingsGenerator",
]

"""Template system for AI Forge.

This module provides a secure, Jinja2-based template system for generating
project files and configurations.
"""

from .base import Template
from .loader import FileSystemLoader, FileSystemTemplate
from .manifest import TemplateManifest
from .renderer import TemplateRenderer

__all__ = [
    "Template",
    "FileSystemLoader",
    "FileSystemTemplate",
    "TemplateManifest",
    "TemplateRenderer",
]

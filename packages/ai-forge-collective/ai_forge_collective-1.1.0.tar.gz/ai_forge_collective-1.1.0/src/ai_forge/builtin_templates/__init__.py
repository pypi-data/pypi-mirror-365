"""Built-in templates for AI Forge."""

from pathlib import Path


def get_template_path() -> Path:
    """Get the path to builtin templates directory.

    Returns:
        Path to the builtin templates directory
    """
    return Path(__file__).parent

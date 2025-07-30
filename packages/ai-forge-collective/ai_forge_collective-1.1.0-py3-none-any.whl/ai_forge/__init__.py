"""AI Forge - Claude Collective Builder.

A Python CLI tool that transforms Claude Code from a powerful but low-level tool
into a productivity multiplier through intelligent, templated configurations.
"""

import logging
import sys

from .core import (
    AIForgeConfig,
    ConfigLoader,
    ConfigLoadError,
    ConfigSaveError,
    FileConfig,
    TemplateConfig,
)

__version__ = "1.1.0"

__all__ = [
    "AIForgeConfig",
    "ConfigLoadError",
    "ConfigLoader",
    "ConfigSaveError",
    "FileConfig",
    "TemplateConfig",
    "__version__",
]


# Configure logging for the application
def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration for AI Forge."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main() -> None:
    """Main entry point for the AI Forge CLI."""
    from ai_forge.cli.main import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()

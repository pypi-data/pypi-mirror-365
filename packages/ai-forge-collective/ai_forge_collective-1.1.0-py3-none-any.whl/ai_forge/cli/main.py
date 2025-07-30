"""Main CLI entry point for AI Forge."""

import logging

import click

from ai_forge import __version__, setup_logging
from ai_forge.cli.console import console


@click.group(name="ai-forge")
@click.version_option(version=__version__, prog_name="AI Forge")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """AI Forge - Claude Collective Builder.

    Transform Claude Code into a productivity multiplier through intelligent,
    templated configurations.
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Set up logging level based on verbose flag
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    # Configure global console with verbose setting
    console.set_verbose(verbose)

    # Store global options in context
    ctx.obj["verbose"] = verbose
    ctx.obj["console"] = console

    logger = logging.getLogger(__name__)
    if verbose:
        logger.debug("Verbose mode enabled")


# Import and register commands - placed after cli function to avoid circular imports
def _register_commands() -> None:
    """Register CLI commands (MVP: init only)."""
    from ai_forge.cli.commands.init import init

    cli.add_command(init)
    # Phase 2 commands moved to separate branches:
    # - template command -> p2/templates branch
    # - validate command -> p2/templates branch


# Register commands
_register_commands()


def main() -> None:
    """Entry point for the AI Forge CLI."""
    cli()


if __name__ == "__main__":
    main()

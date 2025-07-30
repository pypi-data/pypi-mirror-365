"""Init command implementation."""

from datetime import datetime
from pathlib import Path

import click

from ai_forge.builtin_templates import get_template_path
from ai_forge.cli.console import console
from ai_forge.cli.errors import handle_errors
from ai_forge.exceptions import FileSystemError, ValidationError
from ai_forge.templates.loader import FileSystemLoader


@click.command()
@click.option(
    "--force", is_flag=True, help="Overwrite existing template files if they exist"
)
@click.pass_context
@handle_errors
def init(ctx: click.Context, force: bool) -> None:
    """Initialize a new AI Forge project with the universal starter template."""

    # Check if template files already exist and handle --force flag
    template_files = [
        "CLAUDE.md",
        ".claude/settings.json",
        ".claude/hooks/format-on-save.sh",
    ]
    existing_files = [f for f in template_files if Path(f).exists()]

    if existing_files and not force:
        file_list = ", ".join(existing_files)
        raise FileSystemError(
            f"Template files already exist: {file_list}. Use --force to overwrite.",
            path=str(existing_files[0]),
            operation="create template files",
            error_code="files_exist",
        )

    # Load the starter template
    template_path = get_template_path()
    loader = FileSystemLoader(template_path)

    try:
        template = loader.load_template("starter")
    except Exception as e:
        raise ValidationError(
            f"Failed to load starter template: {e}",
            field_name="template",
            invalid_value="starter",
            error_code="template_load_failed",
        ) from e

    # Create template context
    project_name = Path.cwd().name
    now = datetime.now()
    context = {
        "project_name": project_name,
        "description": "Project initialized with AI Forge",
        "author": "AI Forge User",  # Could be made configurable in the future
        "date": now.strftime("%Y-%m-%d"),
        "now": now,  # For template default values
    }

    # Render template to current directory
    try:
        template.render(Path.cwd(), context)
        console.success("Initialized project with AI Forge starter template")
        console.info("Generated files:")
        for file_path in template_files:
            if Path(file_path).exists():
                console.info(f"  ✓ {file_path}")
    except Exception as e:
        raise FileSystemError(
            f"Failed to render template: {e}",
            path=str(Path.cwd()),
            operation="render template",
            error_code="template_render_failed",
        ) from e

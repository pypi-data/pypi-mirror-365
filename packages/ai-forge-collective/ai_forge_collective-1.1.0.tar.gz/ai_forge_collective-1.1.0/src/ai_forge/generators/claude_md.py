"""Generator for CLAUDE.md configuration files."""

from pathlib import Path
from typing import Any

from .base import FileGenerator


class ClaudeMdGenerator(FileGenerator):
    """Generator for CLAUDE.md project configuration files.

    Creates CLAUDE.md files with project instructions, guidelines,
    and configuration for Claude Code development workflows.
    """

    def get_required_context_keys(self) -> list[str]:
        """Get list of required context keys for CLAUDE.md generation.

        Returns:
            List of required context key names
        """
        return [
            "project_name",
            "project_description",
            "language",
        ]

    def get_optional_context_keys(self) -> dict[str, Any]:
        """Get dictionary of optional context keys with default values.

        Returns:
            Dictionary mapping optional key names to default values
        """
        return {
            "project_type": "application",
            "development_workflow": "standard",
            "testing_framework": "pytest",
            "linting_tools": ["ruff", "mypy"],
            "package_manager": "uv",
            "python_version": "3.12+",
            "security_requirements": True,
            "documentation_style": "google",
            "team_size": "small",
            "additional_guidelines": [],
            "custom_instructions": "",
            "agent_roles": {
                "project-manager": "Track tasks and status against specifications",
                "python-engineer": "Python code implementation and dependency "
                "management",
                "debugger": "Error resolution and testing failures",
                "code-reviewer": "Code quality validation before merging",
                "research-assistant": "External documentation and best practice "
                "research",
            },
        }

    def _get_claude_md_template(self) -> str:
        """Get the CLAUDE.md template content.

        Returns:
            Template string for CLAUDE.md file
        """
        return """# {{ project_name }}

{{ project_description }}

## Product Vision

This {{ project_type }} is built using {{ language }} with focus on:
- **Developer Experience**: Clean, maintainable, and well-tested code
- **Security**: Input validation, safe defaults, and secure coding practices
- **Performance**: Optimized for production use with efficient algorithms
- **Extensibility**: Modular design allowing for future enhancements

## Project Status

**Current Phase**: Active Development
- Following {{ development_workflow }} development workflow
- Using {{ testing_framework }} for testing with comprehensive coverage
- Code quality maintained with {{ linting_tools | join(', ') }}
- Dependencies managed via {{ package_manager }}

## Architecture

### Technical Stack
- **Language**: {{ language }} {{ python_version }}
- **Package Manager**: {{ package_manager }}
- **Testing**: {{ testing_framework }}
- **Linting**: {{ linting_tools | join(', ') }}
- **Documentation**: {{ documentation_style }}-style docstrings

{% if security_requirements %}
### Security Requirements
- Input validation on all user-provided data
- Path traversal protection for file operations
- Safe defaults in all configurations
- No arbitrary code execution from user input
- Comprehensive error handling with specific exceptions
{% endif %}

## Development Guidelines

### Agent System Usage
{% for role, description in agent_roles.items() %}
- **{{ role }}**: {{ description }}
{% endfor %}

### Technical Standards
- **{{ language }} {{ python_version }}**: Use modern typing (dict not Dict, list not List)
- **Dependencies**: {{ package_manager }} for all package management 
  (never pip/pipenv/poetry)
- **Code Quality**: {{ linting_tools | join(' for linting/formatting, ') }}
- **Testing**: {{ testing_framework }} with coverage reporting, unit tests for 
  all functions
{% if security_requirements %}
- **Security**: Input validation, safe defaults, principle of least privilege
{% endif %}

### Development Workflow
1. **Task-Driven**: All work tracked with clear acceptance criteria
{% if security_requirements %}
2. **Security-First**: Validate all inputs, use safe defaults, sandbox execution
{% endif %}
3. **Test Coverage**: Unit tests required for all public APIs
4. **Documentation**: Inline docs for complex logic only, self-documenting code preferred

## Code Quality Standards

### Requirements
- Type hints on all functions and methods
- Comprehensive error handling with specific exceptions
- Logging instead of print statements for production code
- Context managers for resource management
- Pathlib for all file operations

### Testing Requirements
- Unit tests for all public APIs
- Integration tests for main workflows
{% if security_requirements %}
- Security tests for input validation
{% endif %}
- Coverage > 90% for core modules

### Documentation Standards
- {{ documentation_style.title() }}-style docstrings for public APIs
- Clear variable and function names
- Inline comments only for complex business logic
- Architecture decision records for major changes

{% if additional_guidelines %}
## Additional Guidelines

{% for guideline in additional_guidelines %}
- {{ guideline }}
{% endfor %}
{% endif %}

{% if custom_instructions %}
## Custom Instructions

{{ custom_instructions }}
{% endif %}

## Important Constraints

- NEVER create files unless absolutely necessary for the goal
- ALWAYS prefer editing existing files over creating new ones
- NEVER proactively create documentation files unless explicitly requested
- Follow conventional commits format for all changes
- Use {{ package_manager }} for all {{ language }} package management operations

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User."""

    def generate(
        self, output_path: Path, context: dict[str, Any], project_root: Path
    ) -> list[Path]:
        """Generate CLAUDE.md file based on context.

        Args:
            output_path: Directory where to generate the file
            context: Generation context and variables
            project_root: Project root directory for path validation

        Returns:
            List containing the generated CLAUDE.md file path

        Raises:
            FileSystemError: If file generation fails
            TemplateRenderError: If template rendering fails
            ValidationError: If context is invalid
        """
        # Validate context
        self.validate_context(context)

        # Merge with defaults
        full_context = self.merge_context_defaults(context)

        # Get template and render
        template_content = self._get_claude_md_template()
        rendered_content = self.render_template(template_content, full_context)

        # Write file
        claude_md_path = output_path / "CLAUDE.md"
        self.write_file(claude_md_path, rendered_content, project_root)

        return [claude_md_path]

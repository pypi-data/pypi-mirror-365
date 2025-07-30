"""Generator for shell script hooks and automation scripts."""

from pathlib import Path
from typing import Any

from .base import FileGenerator


class HooksGenerator(FileGenerator):
    """Generator for shell script hooks and automation scripts.

    Creates various hook scripts for development workflow automation,
    including pre-commit hooks, test runners, and deployment scripts.
    """

    def get_required_context_keys(self) -> list[str]:
        """Get list of required context keys for hooks generation.

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
            "package_manager": "uv",
            "testing_framework": "pytest",
            "linting_tools": ["ruff", "mypy"],
            "formatter": "ruff",
            "type_checker": "mypy",
            "hooks_enabled": {
                "pre_commit": True,
                "post_commit": False,
                "pre_push": True,
                "test_runner": True,
                "format_check": True,
                "lint_check": True,
                "type_check": True,
                "security_check": False,
            },
            "test_command": "pytest",
            "coverage_threshold": 90,
            "python_version": "3.12",
            "shell": "bash",
            "git_hooks_path": ".git/hooks",
            "scripts_path": "scripts",
            "fail_fast": True,
            "verbose": False,
        }

    def _get_shebang(self, shell: str) -> str:
        """Get appropriate shebang for shell script.

        Args:
            shell: Shell type (bash, sh, zsh)

        Returns:
            Shebang line for the shell
        """
        shebang_map = {"bash": "#!/bin/bash", "sh": "#!/bin/sh", "zsh": "#!/bin/zsh"}
        return shebang_map.get(shell, "#!/bin/bash")

    def _get_pre_commit_hook_template(self) -> str:
        """Get template for pre-commit hook script.

        Returns:
            Pre-commit hook template string
        """
        return """{{ shebang }}
#
# Pre-commit hook for {{ project_name }}
# Runs linting, type checking, and formatting checks before commit
#

set -e{% if fail_fast %} -o pipefail{% endif %}

{% if verbose %}
echo "Running pre-commit checks for {{ project_name }}..."
{% endif %}

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Check if {{ package_manager }} is available
if ! command -v {{ package_manager }} &> /dev/null; then
    echo "Error: {{ package_manager }} is not installed or not in PATH"
    exit 1
fi

{% if hooks_enabled.format_check %}
# Run formatter check
{% if verbose %}
echo "Checking code formatting with {{ formatter }}..."
{% endif %}
{% if formatter == "ruff" %}
if ! {{ package_manager }} run {{ formatter }} check --diff .; then
    echo "Code formatting issues found. Run '{{ package_manager }} run {{ formatter }} format .' to fix."
    exit 1
fi
{% else %}
if ! {{ package_manager }} run {{ formatter }} --check .; then
    echo "Code formatting issues found. Run '{{ package_manager }} run {{ formatter }} .' to fix."
    exit 1
fi
{% endif %}
{% endif %}

{% if hooks_enabled.lint_check %}
# Run linting
{% if verbose %}
echo "Running linting checks..."
{% endif %}
{% for tool in linting_tools %}
{% if tool != formatter %}
if ! {{ package_manager }} run {{ tool }} .; then
    echo "Linting issues found with {{ tool }}"
    exit 1
fi
{% endif %}
{% endfor %}
{% endif %}

{% if hooks_enabled.type_check %}
# Run type checking
{% if verbose %}
echo "Running type checks with {{ type_checker }}..."
{% endif %}
if ! {{ package_manager }} run {{ type_checker }} .; then
    echo "Type checking failed"
    exit 1
fi
{% endif %}

{% if hooks_enabled.security_check %}
# Run security checks
{% if verbose %}
echo "Running security checks..."
{% endif %}
if command -v bandit &> /dev/null; then
    if ! {{ package_manager }} run bandit -r src/; then
        echo "Security issues found"
        exit 1
    fi
fi
{% endif %}

{% if verbose %}
echo "All pre-commit checks passed!"
{% endif %}
"""

    def _get_pre_push_hook_template(self) -> str:
        """Get template for pre-push hook script.

        Returns:
            Pre-push hook template string
        """
        return """{{ shebang }}
#
# Pre-push hook for {{ project_name }}
# Runs full test suite before pushing
#

set -e{% if fail_fast %} -o pipefail{% endif %}

{% if verbose %}
echo "Running pre-push checks for {{ project_name }}..."
{% endif %}

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Check if {{ package_manager }} is available
if ! command -v {{ package_manager }} &> /dev/null; then
    echo "Error: {{ package_manager }} is not installed or not in PATH"
    exit 1
fi

{% if hooks_enabled.test_runner %}
# Run full test suite
{% if verbose %}
echo "Running test suite..."
{% endif %}
if ! {{ package_manager }} run {{ test_command }} --cov-fail-under={{ coverage_threshold }}; then
    echo "Tests failed or coverage below {{ coverage_threshold }}%"
    exit 1
fi
{% endif %}

{% if verbose %}
echo "All pre-push checks passed!"
{% endif %}
"""

    def _get_test_runner_template(self) -> str:
        """Get template for test runner script.

        Returns:
            Test runner script template string
        """
        return """{{ shebang }}
#
# Test runner script for {{ project_name }}
# Provides various testing options and configurations
#

set -e{% if fail_fast %} -o pipefail{% endif %}

# Default options
COVERAGE="{{ coverage_threshold }}"
VERBOSE=""
FAST=""
INTEGRATION=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-v"
            shift
            ;;
        -f|--fast)
            FAST="-m 'not slow'"
            shift
            ;;
        -i|--integration)
            INTEGRATION="-m integration"
            shift
            ;;
        -c|--coverage)
            COVERAGE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -v, --verbose      Run tests in verbose mode"
            echo "  -f, --fast         Skip slow tests"
            echo "  -i, --integration  Run only integration tests"
            echo "  -c, --coverage N   Set coverage threshold to N%"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Check if {{ package_manager }} is available
if ! command -v {{ package_manager }} &> /dev/null; then
    echo "Error: {{ package_manager }} is not installed or not in PATH"
    exit 1
fi

# Run tests
echo "Running tests for {{ project_name }}..."
{{ package_manager }} run {{ test_command }} \\
    --cov=src/ \\
    --cov-report=term-missing \\
    --cov-report=html \\
    --cov-fail-under="$COVERAGE" \\
    $VERBOSE \\
    $FAST \\
    $INTEGRATION

echo "Tests completed successfully!"
"""

    def _get_format_script_template(self) -> str:
        """Get template for code formatting script.

        Returns:
            Format script template string
        """
        return """{{ shebang }}
#
# Code formatting script for {{ project_name }}
# Formats all code using {{ formatter }}
#

set -e{% if fail_fast %} -o pipefail{% endif %}

# Parse command line arguments
CHECK_ONLY=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_ONLY="--check"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --check    Only check formatting, don't modify files"
            echo "  -h, --help Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Check if {{ package_manager }} is available
if ! command -v {{ package_manager }} &> /dev/null; then
    echo "Error: {{ package_manager }} is not installed or not in PATH"
    exit 1
fi

{% if check_only %}
if [[ -n "$CHECK_ONLY" ]]; then
    echo "Checking code formatting..."
{% if formatter == "ruff" %}
    {{ package_manager }} run {{ formatter }} check --diff .
{% else %}
    {{ package_manager }} run {{ formatter }} --check .
{% endif %}
else
{% endif %}
    echo "Formatting code with {{ formatter }}..."
{% if formatter == "ruff" %}
    {{ package_manager }} run {{ formatter }} format .
{% else %}
    {{ package_manager }} run {{ formatter }} .
{% endif %}
    echo "Code formatting completed!"
{% if check_only %}
fi
{% endif %}
"""

    def generate(
        self, output_path: Path, context: dict[str, Any], project_root: Path
    ) -> list[Path]:
        """Generate hook scripts based on context.

        Args:
            output_path: Directory where to generate the files
            context: Generation context and variables
            project_root: Project root directory for path validation

        Returns:
            List of generated script file paths

        Raises:
            FileSystemError: If file generation fails
            TemplateRenderError: If template rendering fails
            ValidationError: If context is invalid
        """
        # Validate context
        self.validate_context(context)

        # Merge with defaults
        full_context = self.merge_context_defaults(context)

        # Add shebang to context
        full_context["shebang"] = self._get_shebang(full_context["shell"])

        generated_files = []

        # Create scripts directory
        scripts_dir = output_path / full_context["scripts_path"]

        # Generate pre-commit hook
        if full_context["hooks_enabled"]["pre_commit"]:
            template = self._get_pre_commit_hook_template()
            content = self.render_template(template, full_context)
            hook_path = scripts_dir / "pre-commit"
            self.write_file(hook_path, content, project_root, executable=True)
            generated_files.append(hook_path)

        # Generate pre-push hook
        if full_context["hooks_enabled"]["pre_push"]:
            template = self._get_pre_push_hook_template()
            content = self.render_template(template, full_context)
            hook_path = scripts_dir / "pre-push"
            self.write_file(hook_path, content, project_root, executable=True)
            generated_files.append(hook_path)

        # Generate test runner script
        if full_context["hooks_enabled"]["test_runner"]:
            template = self._get_test_runner_template()
            content = self.render_template(template, full_context)
            script_path = scripts_dir / "test"
            self.write_file(script_path, content, project_root, executable=True)
            generated_files.append(script_path)

        # Generate format script
        if full_context["hooks_enabled"]["format_check"]:
            template = self._get_format_script_template()
            content = self.render_template(template, full_context)
            script_path = scripts_dir / "format"
            self.write_file(script_path, content, project_root, executable=True)
            generated_files.append(script_path)

        return generated_files

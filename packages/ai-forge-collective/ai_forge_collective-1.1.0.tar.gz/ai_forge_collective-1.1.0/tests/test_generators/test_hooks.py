"""Tests for the HooksGenerator class."""

import stat
import tempfile
from pathlib import Path

import pytest

from ai_forge.exceptions import ValidationError
from ai_forge.generators.hooks import HooksGenerator


class TestHooksGenerator:
    """Test cases for HooksGenerator."""

    def test_get_required_context_keys(self):
        """Test required context keys."""
        generator = HooksGenerator()
        required = generator.get_required_context_keys()

        assert "project_name" in required
        assert "language" in required

    def test_get_optional_context_keys(self):
        """Test optional context keys and defaults."""
        generator = HooksGenerator()
        optional = generator.get_optional_context_keys()

        assert "package_manager" in optional
        assert optional["package_manager"] == "uv"
        assert "testing_framework" in optional
        assert optional["testing_framework"] == "pytest"
        assert "hooks_enabled" in optional
        assert optional["hooks_enabled"]["pre_commit"] is True
        assert optional["hooks_enabled"]["pre_push"] is True
        assert optional["shell"] == "bash"
        assert optional["scripts_path"] == "scripts"

    def test_get_shebang(self):
        """Test shebang generation for different shells."""
        generator = HooksGenerator()

        assert generator._get_shebang("bash") == "#!/bin/bash"
        assert generator._get_shebang("sh") == "#!/bin/sh"
        assert generator._get_shebang("zsh") == "#!/bin/zsh"
        assert generator._get_shebang("unknown") == "#!/bin/bash"  # Default

    def test_generate_all_hooks_enabled(self):
        """Test generation with all hooks enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Test Project",
                "language": "Python",
                "hooks_enabled": {
                    "pre_commit": True,
                    "pre_push": True,
                    "test_runner": True,
                    "format_check": True,
                },
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Should generate 4 scripts
            assert len(files) == 4

            # Check that scripts directory was created
            scripts_dir = temp_path / "scripts"
            assert scripts_dir.exists()
            assert scripts_dir.is_dir()

            # Check individual files
            file_names = [f.name for f in files]
            assert "pre-commit" in file_names
            assert "pre-push" in file_names
            assert "test" in file_names
            assert "format" in file_names

    def test_generate_selective_hooks(self):
        """Test generation with only some hooks enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Selective Project",
                "language": "Python",
                "hooks_enabled": {
                    "pre_commit": True,
                    "pre_push": False,
                    "test_runner": True,
                    "format_check": False,
                },
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Should generate only 2 scripts
            assert len(files) == 2

            file_names = [f.name for f in files]
            assert "pre-commit" in file_names
            assert "test" in file_names
            assert "pre-push" not in file_names
            assert "format" not in file_names

    def test_pre_commit_hook_content(self):
        """Test pre-commit hook script content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "PreCommit Test",
                "language": "Python",
                "package_manager": "uv",
                "formatter": "ruff",
                "type_checker": "mypy",
                "linting_tools": ["ruff", "mypy"],
                "hooks_enabled": {"pre_commit": True},
                "verbose": True,
                "fail_fast": True,
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            pre_commit_file = next(f for f in files if f.name == "pre-commit")
            content = pre_commit_file.read_text()

            # Check shebang
            assert content.startswith("#!/bin/bash")

            # Check project name in comments
            assert "PreCommit Test" in content

            # Check that it uses the correct package manager
            assert "uv run" in content

            # Check formatter commands
            assert "ruff check --diff" in content

            # Check type checking
            assert "mypy ." in content

            # Check verbose mode
            assert "echo" in content  # Verbose output

            # Check fail fast option
            assert "set -e -o pipefail" in content

    def test_pre_push_hook_content(self):
        """Test pre-push hook script content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "PrePush Test",
                "language": "Python",
                "test_command": "pytest",
                "coverage_threshold": 85,
                "hooks_enabled": {"pre_push": True},
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            pre_push_file = next(f for f in files if f.name == "pre-push")
            content = pre_push_file.read_text()

            # Check test command
            assert "pytest --cov-fail-under=85" in content

            # Check project name
            assert "PrePush Test" in content

    def test_test_runner_script_content(self):
        """Test test runner script content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "TestRunner Test",
                "language": "Python",
                "test_command": "pytest",
                "coverage_threshold": 95,
                "hooks_enabled": {"test_runner": True},
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            test_file = next(f for f in files if f.name == "test")
            content = test_file.read_text()

            # Check help message
            assert "--help" in content
            assert "Usage:" in content

            # Check coverage threshold variable
            assert 'COVERAGE="95"' in content

            # Check command line argument parsing
            assert "--verbose" in content
            assert "--fast" in content
            assert "--integration" in content

            # Check pytest execution
            assert "pytest" in content
            assert "--cov=" in content

    def test_format_script_content(self):
        """Test format script content."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Format Test",
                "language": "Python",
                "formatter": "ruff",
                "hooks_enabled": {"format_check": True},
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            format_file = next(f for f in files if f.name == "format")
            content = format_file.read_text()

            # Check formatter commands
            assert "ruff check --diff" in content  # Check mode
            assert "ruff format" in content  # Format mode

            # Check command line argument handling
            assert "--check" in content

    def test_script_executable_permissions(self):
        """Test that generated scripts have executable permissions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Permissions Test",
                "language": "Python",
                "hooks_enabled": {"pre_commit": True},
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            for script_file in files:
                # Check that file has execute permission for owner
                file_mode = script_file.stat().st_mode
                assert file_mode & stat.S_IXUSR, (
                    f"Script {script_file.name} is not executable"
                )

    def test_custom_shell_configuration(self):
        """Test generation with custom shell configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Shell Test",
                "language": "Python",
                "shell": "zsh",
                "hooks_enabled": {"pre_commit": True},
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            script_content = files[0].read_text()
            assert script_content.startswith("#!/bin/zsh")

    def test_custom_scripts_path(self):
        """Test generation with custom scripts path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Custom Path Test",
                "language": "Python",
                "scripts_path": "bin",
                "hooks_enabled": {"pre_commit": True},
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Check that scripts were created in custom directory
            assert all(f.parent.name == "bin" for f in files)

    def test_generate_missing_required_context(self):
        """Test generation with missing required context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Incomplete Project"
                # Missing language
            }

            generator = HooksGenerator()
            with pytest.raises(ValidationError, match="Missing required context keys"):
                generator.generate(temp_path, context, temp_path)

    def test_no_hooks_enabled(self):
        """Test generation when no hooks are enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "No Hooks Test",
                "language": "Python",
                "hooks_enabled": {
                    "pre_commit": False,
                    "pre_push": False,
                    "test_runner": False,
                    "format_check": False,
                },
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Should generate no files
            assert len(files) == 0

    def test_script_syntax_validity(self):
        """Test that generated scripts have valid shell syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Syntax Test",
                "language": "Python",
                "hooks_enabled": {"pre_commit": True, "test_runner": True},
            }

            generator = HooksGenerator()
            files = generator.generate(temp_path, context, temp_path)

            for script_file in files:
                content = script_file.read_text()

                # Basic shell syntax checks
                assert content.startswith("#!/")  # Has shebang
                assert "set -e" in content  # Has error handling

                # No template syntax left behind
                assert "{{" not in content
                assert "}}" not in content
                assert "{%" not in content
                assert "%}" not in content

    def test_different_package_managers(self):
        """Test script generation for different package managers."""
        package_managers = ["uv", "poetry", "pip", "pipenv"]

        for package_manager in package_managers:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                context = {
                    "project_name": f"{package_manager.title()} Test",
                    "language": "Python",
                    "package_manager": package_manager,
                    "hooks_enabled": {"pre_commit": True},
                }

                generator = HooksGenerator()
                files = generator.generate(temp_path, context, temp_path)

                content = files[0].read_text()
                assert f"{package_manager} run" in content or package_manager in content

"""Tests for the ClaudeMdGenerator class."""

import tempfile
from pathlib import Path

import pytest

from ai_forge.exceptions import ValidationError
from ai_forge.generators.claude_md import ClaudeMdGenerator


class TestClaudeMdGenerator:
    """Test cases for ClaudeMdGenerator."""

    def test_get_required_context_keys(self):
        """Test required context keys."""
        generator = ClaudeMdGenerator()
        required = generator.get_required_context_keys()

        assert "project_name" in required
        assert "project_description" in required
        assert "language" in required

    def test_get_optional_context_keys(self):
        """Test optional context keys and defaults."""
        generator = ClaudeMdGenerator()
        optional = generator.get_optional_context_keys()

        assert "project_type" in optional
        assert optional["project_type"] == "application"
        assert optional["package_manager"] == "uv"
        assert optional["python_version"] == "3.12+"
        assert optional["security_requirements"] is True
        assert "agent_roles" in optional
        assert isinstance(optional["agent_roles"], dict)

    def test_generate_success(self):
        """Test successful CLAUDE.md generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Test Project",
                "project_description": "A test project for AI Forge",
                "language": "Python",
            }

            generator = ClaudeMdGenerator()
            files = generator.generate(temp_path, context, temp_path)

            assert len(files) == 1
            claude_md_path = files[0]
            assert claude_md_path.name == "CLAUDE.md"
            assert claude_md_path.exists()

            content = claude_md_path.read_text()
            assert "# Test Project" in content
            assert "A test project for AI Forge" in content
            assert "Python 3.12+" in content
            assert "uv for all package management" in content

    def test_generate_with_custom_context(self):
        """Test generation with custom context values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Custom Project",
                "project_description": "Custom description",
                "language": "Python",
                "project_type": "library",
                "package_manager": "poetry",
                "python_version": "3.11+",
                "security_requirements": False,
                "testing_framework": "unittest",
                "linting_tools": ["flake8", "pylint"],
                "additional_guidelines": [
                    "Use dependency injection",
                    "Follow SOLID principles",
                ],
                "custom_instructions": "This is a custom instruction block.",
            }

            generator = ClaudeMdGenerator()
            files = generator.generate(temp_path, context, temp_path)

            content = files[0].read_text()
            assert "# Custom Project" in content
            assert "library" in content
            assert "poetry for all package management" in content
            assert "Python 3.11+" in content
            assert "unittest" in content
            assert "flake8" in content
            assert "pylint" in content
            assert "Use dependency injection" in content
            assert "Follow SOLID principles" in content
            assert "This is a custom instruction block." in content

    def test_generate_security_requirements_disabled(self):
        """Test generation with security requirements disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "No Security Project",
                "project_description": "Project without security requirements",
                "language": "Python",
                "security_requirements": False,
            }

            generator = ClaudeMdGenerator()
            files = generator.generate(temp_path, context, temp_path)

            content = files[0].read_text()
            # Security section should not be present
            assert "### Security Requirements" not in content
            assert "Input validation on all user-provided data" not in content

    def test_generate_agent_roles_customization(self):
        """Test generation with custom agent roles."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Custom Agents Project",
                "project_description": "Project with custom agent roles",
                "language": "Python",
                "agent_roles": {
                    "custom-agent": "Custom agent description",
                    "another-agent": "Another custom agent",
                },
            }

            generator = ClaudeMdGenerator()
            files = generator.generate(temp_path, context, temp_path)

            content = files[0].read_text()
            assert "**custom-agent**: Custom agent description" in content
            assert "**another-agent**: Another custom agent" in content

    def test_generate_missing_required_context(self):
        """Test generation with missing required context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Incomplete Project"
                # Missing project_description and language
            }

            generator = ClaudeMdGenerator()
            with pytest.raises(ValidationError, match="Missing required context keys"):
                generator.generate(temp_path, context, temp_path)

    def test_template_rendering_edge_cases(self):
        """Test template rendering with edge case values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Edge Case Project",
                "project_description": "Testing edge cases",
                "language": "Python",
                "linting_tools": [],  # Empty list
                "additional_guidelines": [],  # Empty list
                "custom_instructions": "",  # Empty string
                "agent_roles": {},  # Empty dict
            }

            generator = ClaudeMdGenerator()
            files = generator.generate(temp_path, context, temp_path)

            content = files[0].read_text()
            assert "# Edge Case Project" in content
            # Should handle empty collections gracefully
            assert content  # File should still be generated

    def test_file_path_security(self):
        """Test that file generation respects path security."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Try to write outside project root
            malicious_path = temp_path / ".." / "malicious"
            context = {
                "project_name": "Security Test",
                "project_description": "Testing path security",
                "language": "Python",
            }

            generator = ClaudeMdGenerator()
            with pytest.raises(Exception):  # Should raise security-related exception
                generator.generate(malicious_path, context, temp_path)

    def test_content_quality(self):
        """Test that generated content meets quality standards."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Quality Test Project",
                "project_description": "Testing content quality standards",
                "language": "Python",
            }

            generator = ClaudeMdGenerator()
            files = generator.generate(temp_path, context, temp_path)

            content = files[0].read_text()

            # Check for essential sections
            assert "# Quality Test Project" in content
            assert "## Product Vision" in content
            assert "## Project Status" in content
            assert "## Architecture" in content
            assert "## Development Guidelines" in content
            assert "## Code Quality Standards" in content
            assert "## Important Constraints" in content
            assert "# important-instruction-reminders" in content

            # Check that variables are properly substituted (no {{ }} left)
            assert "{{" not in content
            assert "}}" not in content

    def test_markdown_syntax_validity(self):
        """Test that generated Markdown has valid syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Markdown Test",
                "project_description": "Testing Markdown syntax",
                "language": "Python",
            }

            generator = ClaudeMdGenerator()
            files = generator.generate(temp_path, context, temp_path)

            content = files[0].read_text()

            # Basic Markdown syntax checks
            lines = content.split("\n")

            # Check headers are properly formatted
            header_lines = [line for line in lines if line.startswith("#")]
            for header in header_lines:
                assert header.startswith("#")
                assert " " in header  # Should have space after #

            # Check no malformed template syntax
            assert "{{" not in content
            assert "}}" not in content
            assert "{%" not in content
            assert "%}" not in content

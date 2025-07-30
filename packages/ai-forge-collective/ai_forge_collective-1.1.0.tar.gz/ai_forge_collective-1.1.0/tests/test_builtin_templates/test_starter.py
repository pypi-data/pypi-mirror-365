"""Comprehensive tests for the starter template."""

import json
import stat
import tempfile
from pathlib import Path

import pytest
import yaml

from ai_forge.exceptions import TemplateValidationError
from ai_forge.templates import FileSystemLoader, TemplateRenderer


class TestStarterTemplateValidation:
    """Test validation functions for starter template variables and files."""

    def test_validate_project_name_valid(self) -> None:
        """Test valid project name validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_project_name,
        )

        valid_names = [
            "my-project",
            "My Project",
            "project_name",
            "Project.Name",
            "test123",
            "a-very-long-project-name-with-many-words",
        ]

        for name in valid_names:
            result = validate_project_name(name)
            assert result == name.strip()

    def test_validate_project_name_invalid(self) -> None:
        """Test invalid project name validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_project_name,
        )

        invalid_names = [
            "",  # Empty
            "   ",  # Whitespace only
            "a",  # Too short
            "a" * 101,  # Too long
            "../traversal",  # Path traversal
            "project<script>",  # HTML
            "CON",  # Windows reserved
            ".hidden",  # Starts with dot
            "-project",  # Starts with special char
            "project-",  # Ends with special char
        ]

        for name in invalid_names:
            with pytest.raises(TemplateValidationError):
                validate_project_name(name)

    def test_validate_description_valid(self) -> None:
        """Test valid description validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_description,
        )

        valid_descriptions = [
            "A simple project",
            "This is a longer description with multiple words and punctuation!",
            "Description with numbers 123 and symbols @#$%",
        ]

        for desc in valid_descriptions:
            result = validate_description(desc)
            assert result == desc.strip()

    def test_validate_description_invalid(self) -> None:
        """Test invalid description validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_description,
        )

        invalid_descriptions = [
            "",  # Empty
            "   ",  # Whitespace only
            "abc",  # Too short
            "a" * 501,  # Too long
            "<script>alert('xss')</script>",  # XSS attempt
            "javascript:alert('xss')",  # JavaScript URL
            "data:text/html,<script>",  # Data URL
        ]

        for desc in invalid_descriptions:
            with pytest.raises(TemplateValidationError):
                validate_description(desc)

    def test_validate_author_valid(self) -> None:
        """Test valid author validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_author,
        )

        valid_authors = [
            "John Doe",
            "Jane Smith-Jones",
            "O'Connor",
            "Dr. Smith",
            "user123",
        ]

        for author in valid_authors:
            result = validate_author(author)
            assert result == author.strip()

    def test_validate_author_invalid(self) -> None:
        """Test invalid author validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_author,
        )

        invalid_authors = [
            "",  # Empty
            "a",  # Too short
            "a" * 101,  # Too long
            "../admin",  # Path traversal
            "user<script>",  # HTML
        ]

        for author in invalid_authors:
            with pytest.raises(TemplateValidationError):
                validate_author(author)

    def test_validate_editor_valid(self) -> None:
        """Test valid editor validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_editor,
        )

        test_cases = [
            ("vscode", "vscode"),
            ("code", "vscode"),  # Normalized
            ("vim", "vim"),
            ("emacs", "emacs"),
            ("sublime-text", "sublime"),  # Normalized
            ("", "vscode"),  # Default fallback
        ]

        for input_editor, expected in test_cases:
            result = validate_editor(input_editor)
            assert result == expected

    def test_validate_editor_invalid(self) -> None:
        """Test invalid editor validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_editor,
        )

        with pytest.raises(TemplateValidationError):
            validate_editor("nonexistent-editor")

    def test_validate_claude_permissions_valid(self) -> None:
        """Test valid Claude permissions validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_claude_permissions,
        )

        valid_permissions = [
            ["Read", "Write", "Edit"],
            ["Read"],  # Minimum
            ["Edit", "Write", "Read", "Grep"],  # All safe permissions
        ]

        for perms in valid_permissions:
            result = validate_claude_permissions(perms)
            assert "Read" in result  # Always required
            assert all(
                p in ["Edit", "Write", "Read", "Grep", "Glob", "LS"] for p in result
            )

    def test_validate_claude_permissions_invalid(self) -> None:
        """Test invalid Claude permissions validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_claude_permissions,
        )

        invalid_permissions = [
            [],  # Empty
            ["Execute"],  # Dangerous
            ["Network"],  # Dangerous
            ["Read", "Execute"],  # Mix of safe and dangerous
            "not-a-list",  # Wrong type
            [123],  # Wrong item type
        ]

        for perms in invalid_permissions:
            with pytest.raises(TemplateValidationError):
                validate_claude_permissions(perms)  # type: ignore

    def test_validate_boolean_values(self) -> None:
        """Test boolean validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_boolean,
        )

        true_values = [True, "true", "True", "yes", "1", "on", "enable", "enabled"]
        false_values = [
            False,
            "false",
            "False",
            "no",
            "0",
            "off",
            "disable",
            "disabled",
        ]

        for val in true_values:
            assert validate_boolean(val, "test") is True

        for val in false_values:
            assert validate_boolean(val, "test") is False

        # Test invalid values
        with pytest.raises(TemplateValidationError):
            validate_boolean("maybe", "test")

    def test_validate_variables_complete(self) -> None:
        """Test complete variable validation."""
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_variables,
        )

        valid_variables = {
            "project_name": "Test Project",
            "description": "A test project for validation",
            "author": "Test Author",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": "true",
            "claude_permissions": ["Read", "Write", "Edit"],
        }

        result = validate_variables(valid_variables)

        assert result["project_name"] == "Test Project"
        assert result["description"] == "A test project for validation"
        assert result["author"] == "Test Author"
        assert result["editor"] == "vscode"
        assert result["git_enabled"] is True
        assert result["format_on_save"] is True
        assert "Read" in result["claude_permissions"]


class TestStarterTemplateGeneration:
    """Test starter template file generation and content validation."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_path = (
            Path(__file__).parent.parent.parent
            / "src"
            / "ai_forge"
            / "builtin_templates"
            / "starter"
        )
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_template_manifest_structure(self) -> None:
        """Test that the template manifest has correct structure."""
        manifest_path = self.template_path / "template.yaml"
        assert manifest_path.exists(), "Template manifest not found"

        with open(manifest_path, "r") as f:
            manifest = yaml.safe_load(f)

        # Check required fields
        required_fields = ["name", "description", "version", "language"]
        for field in required_fields:
            assert field in manifest, f"Missing required field: {field}"

        assert manifest["name"] == "starter"
        assert manifest["language"] == "universal"

        # Check variables structure
        assert "variables" in manifest
        variables = manifest["variables"]
        assert "required" in variables
        assert "optional" in variables

        required_vars = variables["required"]
        assert "project_name" in required_vars
        assert "description" in required_vars
        assert "author" in required_vars

    def test_template_files_exist(self) -> None:
        """Test that all template files exist."""
        files_dir = self.template_path / "files"
        assert files_dir.exists(), "Template files directory not found"

        expected_files = [
            "CLAUDE.md.j2",
            "settings.json.j2",
            "format-on-save.sh.j2",
        ]

        for file_name in expected_files:
            file_path = files_dir / file_name
            assert file_path.exists(), f"Template file not found: {file_name}"

            # Check that files are not empty
            content = file_path.read_text()
            assert len(content.strip()) > 0, f"Template file is empty: {file_name}"

    def test_validation_module_exists(self) -> None:
        """Test that validation module exists and is importable."""
        validation_dir = self.template_path / "validation"
        assert validation_dir.exists(), "Validation directory not found"

        validation_files = ["__init__.py", "variables.py", "files.py"]
        for file_name in validation_files:
            file_path = validation_dir / file_name
            assert file_path.exists(), f"Validation file not found: {file_name}"

    def test_template_rendering_success(self) -> None:
        """Test successful template rendering with valid variables."""

        # Load template using the loader
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")

        # Test variables
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Render template
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Check that files were generated
        expected_files = [
            "CLAUDE.md",
            ".claude/settings.json",
            ".claude/hooks/format-on-save.sh",
        ]

        for file_path in expected_files:
            full_path = self.output_dir / file_path
            assert full_path.exists(), f"Generated file not found: {file_path}"

    def test_claude_md_content(self) -> None:
        """Test generated CLAUDE.md content."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Check CLAUDE.md content
        claude_md_path = self.output_dir / "CLAUDE.md"
        content = claude_md_path.read_text()

        # Validate content using validation function
        from ai_forge.builtin_templates.starter.validation.files import (
            validate_claude_md_content,
        )

        validate_claude_md_content(content, context)

        # Additional content checks
        assert "# Test Project" in content
        assert "A test project for AI Forge" in content
        assert "Test Author" in content
        assert "2024-01-15" in content
        assert "- Edit" in content
        assert "- Write" in content
        assert "- Read" in content

    def test_settings_json_content(self) -> None:
        """Test generated settings.json content."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Check settings.json content
        settings_path = self.output_dir / ".claude/settings.json"
        content = settings_path.read_text()

        # Validate JSON syntax
        settings = json.loads(content)

        # Validate content using validation function
        from ai_forge.builtin_templates.starter.validation.files import (
            validate_settings_json_content,
        )

        validate_settings_json_content(content, context)

        # Additional validation
        assert settings["project"]["name"] == "Test Project"
        assert settings["project"]["author"] == "Test Author"
        assert settings["editor"]["primary"] == "vscode"
        assert settings["hooks"]["format_on_save"]["enabled"] is True

        # Security checks
        permissions = settings["claude"]["permissions"]
        assert "Execute" in permissions["denied"]
        assert "Network" in permissions["denied"]
        assert "Read" in permissions["allowed"]

    def test_format_script_content(self) -> None:
        """Test generated format-on-save.sh content."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Check script content
        script_path = self.output_dir / ".claude/hooks/format-on-save.sh"
        content = script_path.read_text()

        # Validate content using validation function
        from ai_forge.builtin_templates.starter.validation.files import (
            validate_format_script_content,
        )

        validate_format_script_content(content, context)

        # Additional checks
        assert content.startswith("#!/bin/bash")
        assert "Test Project" in content
        assert "set -euo pipefail" in content
        assert "readonly" in content
        assert "cleanup()" in content

        # Security checks - ensure no dangerous patterns
        dangerous_patterns = ["rm -rf", "sudo ", "| sh", "curl ", "wget "]
        for pattern in dangerous_patterns:
            assert pattern not in content, f"Dangerous pattern found: {pattern}"

    def test_file_permissions(self) -> None:
        """Test that generated files have correct permissions."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Check file permissions
        from ai_forge.builtin_templates.starter.validation.files import (
            validate_generated_file_permissions,
        )

        # Shell script should be executable
        script_path = self.output_dir / ".claude/hooks/format-on-save.sh"
        validate_generated_file_permissions(script_path)
        script_stat = script_path.stat()
        assert script_stat.st_mode & stat.S_IXUSR, "Script should be executable"

        # Config files should not be executable
        for config_file in ["CLAUDE.md", ".claude/settings.json"]:
            config_path = self.output_dir / config_file
            validate_generated_file_permissions(config_path)
            config_stat = config_path.stat()
            assert not (config_stat.st_mode & stat.S_IXUSR), (
                f"{config_file} should not be executable"
            )

        # No files should be world-writable
        for file_path in [
            self.output_dir / "CLAUDE.md",
            self.output_dir / ".claude/settings.json",
            self.output_dir / ".claude/hooks/format-on-save.sh",
        ]:
            file_stat = file_path.stat()
            assert not (file_stat.st_mode & stat.S_IWOTH), (
                f"{file_path} should not be world-writable"
            )

    def test_directory_structure(self) -> None:
        """Test that correct directory structure is created."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Validate directory structure
        from ai_forge.builtin_templates.starter.validation.files import (
            validate_generated_file_structure,
        )

        validate_generated_file_structure(self.output_dir, context)

        # Check specific directories exist
        assert (self.output_dir / ".claude").is_dir()
        assert (self.output_dir / ".claude/hooks").is_dir()


class TestStarterTemplateCrossPlatform:
    """Test cross-platform compatibility of starter template."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_path = (
            Path(__file__).parent.parent.parent
            / "src"
            / "ai_forge"
            / "builtin_templates"
            / "starter"
        )
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_cross_platform_compatibility(self) -> None:
        """Test that generated files are cross-platform compatible."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Validate cross-platform compatibility
        from ai_forge.builtin_templates.starter.validation.files import (
            validate_cross_platform_compatibility,
        )

        validate_cross_platform_compatibility(self.output_dir)

    def test_line_endings_consistency(self) -> None:
        """Test that generated files have consistent line endings."""
        context = {
            "project_name": "Test Project",
            "description": "A test project for AI Forge",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Check shell script has Unix line endings
        script_path = self.output_dir / ".claude/hooks/format-on-save.sh"
        content = script_path.read_text()
        assert "\r\n" not in content, (
            "Shell script should not have Windows line endings"
        )

    def test_utf8_encoding(self) -> None:
        """Test that all generated files are UTF-8 encoded."""
        context = {
            "project_name": "Test Project with Üñíçödé",
            "description": "A test project with special characters: áéíóú",
            "author": "Test Authör",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Load and render template
        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Check that files can be read as UTF-8
        text_files = [
            "CLAUDE.md",
            ".claude/settings.json",
            ".claude/hooks/format-on-save.sh",
        ]

        for file_path in text_files:
            full_path = self.output_dir / file_path
            try:
                content = full_path.read_text(encoding="utf-8")
                assert len(content) > 0
            except UnicodeDecodeError:
                pytest.fail(f"File {file_path} is not valid UTF-8")


class TestStarterTemplateEdgeCases:
    """Test edge cases and error conditions for starter template."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_path = (
            Path(__file__).parent.parent.parent
            / "src"
            / "ai_forge"
            / "builtin_templates"
            / "starter"
        )
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_missing_required_variables(self) -> None:
        """Test template rendering with missing required variables."""
        # Missing project_name
        context = {
            "description": "A test project",
            "author": "Test Author",
        }

        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()

        with pytest.raises(Exception):  # Should fail due to missing required variable
            renderer.render_template(template, self.output_dir, context)

    def test_special_characters_in_variables(self) -> None:
        """Test template with special characters in variables."""
        context = {
            "project_name": "Test-Project_Name.v2",
            "description": "A project with special chars: @#$%^&*()",
            "author": "O'Connor-Smith",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Should validate and render successfully
        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_variables,
        )

        validated = validate_variables(context)

        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, validated)

        # Verify files were created
        assert (self.output_dir / "CLAUDE.md").exists()
        assert (self.output_dir / ".claude/settings.json").exists()

    def test_boolean_string_conversion(self) -> None:
        """Test boolean values provided as strings."""
        context = {
            "project_name": "Test Project",
            "description": "A test project",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": "true",  # String instead of boolean
            "format_on_save": "false",  # String instead of boolean
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_variables,
        )

        validated = validate_variables(context)

        # Should convert strings to booleans
        assert validated["git_enabled"] is True
        assert validated["format_on_save"] is False

    def test_empty_output_directory(self) -> None:
        """Test rendering to an empty output directory."""
        context = {
            "project_name": "Test Project",
            "description": "A test project",
            "author": "Test Author",
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        # Create a completely empty directory
        empty_dir = Path(self.temp_dir) / "empty"
        empty_dir.mkdir()

        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, empty_dir, context)

        # Should create directory structure and files
        assert (empty_dir / ".claude").is_dir()
        assert (empty_dir / ".claude/hooks").is_dir()
        assert (empty_dir / "CLAUDE.md").exists()

    def test_maximum_length_variables(self) -> None:
        """Test template with maximum length variables."""
        context = {
            "project_name": "a" * 100,  # Maximum allowed length
            "description": "b" * 500,  # Maximum allowed length
            "author": "c" * 100,  # Maximum allowed length
            "date": "2024-01-15",
            "editor": "vscode",
            "git_enabled": True,
            "format_on_save": True,
            "claude_permissions": ["Edit", "Write", "Read"],
        }

        from ai_forge.builtin_templates.starter.validation.variables import (
            validate_variables,
        )

        validated = validate_variables(context)

        loader = FileSystemLoader(self.template_path.parent)
        template = loader.load_template("starter")
        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, validated)

        # Should render successfully
        assert (self.output_dir / "CLAUDE.md").exists()

        # Verify content contains long strings
        claude_content = (self.output_dir / "CLAUDE.md").read_text()
        assert "a" * 100 in claude_content
        assert "b" * 500 in claude_content

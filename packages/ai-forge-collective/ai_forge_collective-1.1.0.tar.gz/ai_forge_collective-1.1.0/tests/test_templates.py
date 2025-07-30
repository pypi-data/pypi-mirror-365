"""Comprehensive tests for AI Forge template system."""

import tempfile
from pathlib import Path

import pytest
import yaml

from ai_forge.exceptions import (
    TemplateError,
    TemplateRenderError,
    TemplateSecurityError,
    TemplateValidationError,
)
from ai_forge.templates import (
    FileSystemLoader,
    TemplateManifest,
    TemplateRenderer,
)
from ai_forge.templates.loader import FileSystemTemplate
from ai_forge.templates.security import (
    validate_template_content,
    validate_template_path,
    validate_template_variables,
)


class TestTemplateManifest:
    """Test TemplateManifest class."""

    def test_valid_manifest(self) -> None:
        """Test valid manifest parsing."""
        manifest_data = {
            "name": "test-template",
            "description": "A test template",
            "version": "1.0.0",
            "language": "python",
            "files": ["main.py", "requirements.txt"],
            "variables": {
                "required": ["project_name"],
                "optional": {"author": "Anonymous"},
            },
        }

        manifest = TemplateManifest(manifest_data)
        manifest.validate()

        assert manifest.get_name() == "test-template"
        assert manifest.get_description() == "A test template"
        assert manifest.get_version() == "1.0.0"
        assert manifest.get_language() == "python"
        assert manifest.get_template_files() == ["main.py", "requirements.txt"]
        assert manifest.get_required_variables() == ["project_name"]
        assert manifest.get_optional_variables() == {"author": "Anonymous"}

    def test_missing_required_fields(self) -> None:
        """Test manifest with missing required fields."""
        manifest_data = {
            "name": "test-template",
            "description": "A test template",
            # Missing version and language
        }

        with pytest.raises(TemplateValidationError, match="missing required fields"):
            TemplateManifest(manifest_data).validate()

    def test_invalid_field_types(self) -> None:
        """Test manifest with invalid field types."""
        manifest_data = {
            "name": "test-template",
            "description": "A test template",
            "version": 1.0,  # Should be string
            "language": "python",
            "files": "not-a-list",  # Should be list or dict
        }

        with pytest.raises(TemplateValidationError, match="must be a string"):
            TemplateManifest(manifest_data).validate()

    def test_dangerous_file_paths(self) -> None:
        """Test manifest with dangerous file paths."""
        manifest_data = {
            "name": "test-template",
            "description": "A test template",
            "version": "1.0.0",
            "language": "python",
            "files": ["../../../etc/passwd"],  # Path traversal
        }

        with pytest.raises(TemplateValidationError, match="dangerous patterns"):
            TemplateManifest(manifest_data).validate()

    def test_file_mapping_format(self) -> None:
        """Test manifest with file mapping format."""
        manifest_data = {
            "name": "test-template",
            "description": "A test template",
            "version": "1.0.0",
            "language": "python",
            "files": {"src/main.py.j2": "main.py", "src/config.yaml.j2": "config.yaml"},
        }

        manifest = TemplateManifest(manifest_data)
        manifest.validate()

        file_mapping = manifest.get_file_mapping()
        assert file_mapping == {
            "src/main.py.j2": "main.py",
            "src/config.yaml.j2": "config.yaml",
        }


class TestTemplateSecurity:
    """Test template security validation."""

    def test_valid_template_path(self) -> None:
        """Test valid template path validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            valid_path = base_path / "templates" / "python"
            valid_path.mkdir(parents=True)

            # Should not raise exception
            validate_template_path(valid_path, base_path)

    def test_path_traversal_attack(self) -> None:
        """Test path traversal attack prevention."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            dangerous_path = base_path / ".." / ".." / "etc" / "passwd"

            with pytest.raises(TemplateSecurityError, match="outside base directory"):
                validate_template_path(dangerous_path, base_path)

    def test_dangerous_template_content(self) -> None:
        """Test dangerous template content detection."""
        dangerous_contents = [
            "{{ exec('rm -rf /') }}",
            "{% import os %}",
            "{{ __import__('subprocess').call(['rm', '-rf', '/']) }}",
            "{{ open('/etc/passwd').read() }}",
        ]

        for content in dangerous_contents:
            with pytest.raises(TemplateSecurityError, match="dangerous content"):
                validate_template_content(content, Path("test.j2"))

    def test_safe_template_content(self) -> None:
        """Test safe template content passes validation."""
        safe_content = """
        # {{ project_name }}
        
        def main():
            print("Hello, {{ name }}!")
            return {{ version }}
        
        if __name__ == "__main__":
            main()
        """

        # Should not raise exception
        validate_template_content(safe_content, Path("main.py.j2"))

    def test_dangerous_variable_names(self) -> None:
        """Test dangerous variable name detection."""
        dangerous_vars = {
            "__builtins__": "bad",
            "_private": "also bad",
            "exec": "very bad",
        }

        with pytest.raises(TemplateSecurityError):
            validate_template_variables(dangerous_vars)

    def test_safe_variable_names(self) -> None:
        """Test safe variable names pass validation."""
        safe_vars = {
            "project_name": "my-project",
            "author": "John Doe",
            "version": "1.0.0",
        }

        # Should not raise exception
        validate_template_variables(safe_vars)


class TestFileSystemLoader:
    """Test FileSystemLoader class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "templates"
        self.template_dir.mkdir()

        # Create a valid test template
        self.test_template_dir = self.template_dir / "python-basic"
        self.test_template_dir.mkdir()

        # Create template manifest
        manifest_data = {
            "name": "python-basic",
            "description": "Basic Python project template",
            "version": "1.0.0",
            "language": "python",
            "files": ["main.py.j2", "requirements.txt.j2"],
            "variables": {
                "required": ["project_name"],
                "optional": {"author": "Anonymous"},
            },
        }

        with open(self.test_template_dir / "template.yaml", "w") as f:
            yaml.dump(manifest_data, f)

        # Create template files
        with open(self.test_template_dir / "main.py.j2", "w") as f:
            f.write("# {{ project_name }}\n\nprint('Hello from {{ project_name }}!')")

        with open(self.test_template_dir / "requirements.txt.j2", "w") as f:
            f.write("# Requirements for {{ project_name }}\n")

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_load_valid_template(self) -> None:
        """Test loading a valid template."""
        loader = FileSystemLoader(self.template_dir)
        template = loader.load_template("python-basic")

        assert isinstance(template, FileSystemTemplate)
        assert template.name == "python-basic"
        assert template.description == "Basic Python project template"
        assert template.language == "python"

    def test_load_nonexistent_template(self) -> None:
        """Test loading a template that doesn't exist."""
        loader = FileSystemLoader(self.template_dir)

        with pytest.raises(TemplateError, match="Template not found"):
            loader.load_template("nonexistent")

    def test_list_templates(self) -> None:
        """Test listing available templates."""
        loader = FileSystemLoader(self.template_dir)
        templates = loader.list_templates()

        assert "python-basic" in templates

    def test_template_exists(self) -> None:
        """Test checking if template exists."""
        loader = FileSystemLoader(self.template_dir)

        assert loader.template_exists("python-basic") is True
        assert loader.template_exists("nonexistent") is False

    def test_load_template_without_manifest(self) -> None:
        """Test loading template without manifest file."""
        # Create template directory without manifest
        bad_template_dir = self.template_dir / "bad-template"
        bad_template_dir.mkdir()

        loader = FileSystemLoader(self.template_dir)

        with pytest.raises(TemplateError, match="Template manifest not found"):
            loader.load_template("bad-template")

    def test_load_template_with_invalid_yaml(self) -> None:
        """Test loading template with invalid YAML manifest."""
        # Create template with invalid YAML
        bad_template_dir = self.template_dir / "invalid-yaml"
        bad_template_dir.mkdir()

        with open(bad_template_dir / "template.yaml", "w") as f:
            f.write("invalid: yaml: content: [")

        loader = FileSystemLoader(self.template_dir)

        with pytest.raises(TemplateError, match="Invalid YAML"):
            loader.load_template("invalid-yaml")


class TestTemplateRenderer:
    """Test TemplateRenderer class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "templates"
        self.output_dir = Path(self.temp_dir) / "output"
        self.template_dir.mkdir()
        self.output_dir.mkdir()

        # Create test template
        test_template_dir = self.template_dir / "test-template"
        test_template_dir.mkdir()

        manifest_data = {
            "name": "test-template",
            "description": "Test template",
            "version": "1.0.0",
            "language": "python",
            "files": ["main.py.j2", "config.yaml.j2"],
            "variables": {
                "required": ["project_name"],
                "optional": {"author": "Anonymous"},
            },
        }

        with open(test_template_dir / "template.yaml", "w") as f:
            yaml.dump(manifest_data, f)

        with open(test_template_dir / "main.py.j2", "w") as f:
            f.write("# {{ project_name }}\n# Author: {{ author }}\n\nprint('Hello!')")

        with open(test_template_dir / "config.yaml.j2", "w") as f:
            f.write("project: {{ project_name }}\nauthor: {{ author }}")

        # Load template
        loader = FileSystemLoader(self.template_dir)
        self.template = loader.load_template("test-template")
        self.renderer = TemplateRenderer()

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_render_template_success(self) -> None:
        """Test successful template rendering."""
        context = {"project_name": "my-project", "author": "John Doe"}

        self.renderer.render_template(self.template, self.output_dir, context)

        # Check that files were created
        main_file = self.output_dir / "main.py.j2"
        config_file = self.output_dir / "config.yaml.j2"

        assert main_file.exists()
        assert config_file.exists()

        # Check file contents
        main_content = main_file.read_text()
        assert "# my-project" in main_content
        assert "# Author: John Doe" in main_content

        config_content = config_file.read_text()
        assert "project: my-project" in config_content
        assert "author: John Doe" in config_content

    def test_render_missing_required_variables(self) -> None:
        """Test rendering with missing required variables."""
        context = {
            "author": "John Doe"
            # Missing required project_name
        }

        with pytest.raises(
            TemplateRenderError, match="Missing required template variables"
        ):
            self.renderer.render_template(self.template, self.output_dir, context)

    def test_render_with_defaults(self) -> None:
        """Test rendering with default variable values."""
        context = {
            "project_name": "my-project"
            # Using default for author
        }

        self.renderer.render_template(self.template, self.output_dir, context)

        main_file = self.output_dir / "main.py.j2"
        main_content = main_file.read_text()
        assert "# Author: Anonymous" in main_content  # Default value

    def test_render_string(self) -> None:
        """Test rendering template strings."""
        template_string = "Hello, {{ name }}!"
        context = {"name": "World"}

        result = self.renderer.render_string(template_string, context)
        assert result == "Hello, World!"

    def test_render_string_with_dangerous_content(self) -> None:
        """Test that dangerous content in strings is rejected."""
        dangerous_template = "{{ exec('rm -rf /') }}"
        context = {}

        with pytest.raises(TemplateSecurityError):
            self.renderer.render_string(dangerous_template, context)

    def test_render_with_dangerous_variables(self) -> None:
        """Test that dangerous variables are rejected."""
        context = {"project_name": "my-project", "__builtins__": "dangerous"}

        with pytest.raises(TemplateSecurityError):
            self.renderer.render_template(self.template, self.output_dir, context)


class TestTemplateIntegration:
    """Integration tests for the complete template system."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = Path(self.temp_dir) / "templates"
        self.output_dir = Path(self.temp_dir) / "output"
        self.template_dir.mkdir()
        self.output_dir.mkdir()

    def teardown_method(self) -> None:
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_complete_template_workflow(self) -> None:
        """Test complete workflow from loading to rendering."""
        # Create template structure
        python_template_dir = self.template_dir / "python-project"
        python_template_dir.mkdir()

        # Create subdirectory for template files
        src_dir = python_template_dir / "src"
        src_dir.mkdir()

        # Template manifest
        manifest_data = {
            "name": "python-project",
            "description": "Complete Python project template",
            "version": "1.0.0",
            "language": "python",
            "files": {
                "src/main.py.j2": "src/main.py",
                "pyproject.toml.j2": "pyproject.toml",
                "README.md.j2": "README.md",
            },
            "variables": {
                "required": ["project_name", "description"],
                "optional": {
                    "author": "Anonymous",
                    "version": "0.1.0",
                    "python_version": "3.12",
                },
            },
        }

        with open(python_template_dir / "template.yaml", "w") as f:
            yaml.dump(manifest_data, f)

        # Template files
        with open(src_dir / "main.py.j2", "w") as f:
            f.write(
                '"""{{ description }}"""\n\n'
                "def main():\n"
                '    print("{{ project_name }} v{{ version }}")\n\n'
                'if __name__ == "__main__":\n'
                "    main()"
            )

        with open(python_template_dir / "pyproject.toml.j2", "w") as f:
            f.write(
                "[project]\n"
                'name = "{{ project_name }}"\n'
                'version = "{{ version }}"\n'
                'description = "{{ description }}"\n'
                'requires-python = ">={{ python_version }}"'
            )

        with open(python_template_dir / "README.md.j2", "w") as f:
            f.write(
                "# {{ project_name }}\n\n{{ description }}\n\n## Author\n\n{{ author }}"
            )

        # Load and render template
        loader = FileSystemLoader(self.template_dir)
        template = loader.load_template("python-project")

        context = {
            "project_name": "awesome-tool",
            "description": "An awesome Python tool",
            "author": "Jane Developer",
            "version": "1.2.3",
        }

        renderer = TemplateRenderer()
        renderer.render_template(template, self.output_dir, context)

        # Verify output structure
        assert (self.output_dir / "src" / "main.py").exists()
        assert (self.output_dir / "pyproject.toml").exists()
        assert (self.output_dir / "README.md").exists()

        # Verify content
        main_content = (self.output_dir / "src" / "main.py").read_text()
        assert '"An awesome Python tool"' in main_content
        assert 'print("awesome-tool v1.2.3")' in main_content

        pyproject_content = (self.output_dir / "pyproject.toml").read_text()
        assert 'name = "awesome-tool"' in pyproject_content
        assert 'version = "1.2.3"' in pyproject_content
        assert 'requires-python = ">=3.12"' in pyproject_content  # Default value

        readme_content = (self.output_dir / "README.md").read_text()
        assert "# awesome-tool" in readme_content
        assert "Jane Developer" in readme_content

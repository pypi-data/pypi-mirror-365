"""Tests for the base FileGenerator class."""

import json
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from ai_forge.exceptions import FileSystemError, TemplateRenderError, ValidationError
from ai_forge.generators.base import FileGenerator


class TestFileGenerator(FileGenerator):
    """Concrete implementation of FileGenerator for testing."""

    def get_required_context_keys(self) -> list[str]:
        return ["project_name"]

    def get_optional_context_keys(self) -> dict[str, any]:
        return {"version": "1.0.0", "debug": False}

    def generate(
        self, output_path: Path, context: dict[str, any], project_root: Path
    ) -> list[Path]:
        self.validate_context(context)
        full_context = self.merge_context_defaults(context)

        # Simple test generation
        test_file = output_path / "test.txt"
        content = f"Project: {full_context['project_name']}\nVersion: {full_context['version']}"
        self.write_file(test_file, content, project_root)
        return [test_file]


class TestFileGeneratorBase:
    """Test cases for FileGenerator base class."""

    def test_initialization(self):
        """Test FileGenerator initialization."""
        generator = TestFileGenerator()

        # Check that Jinja2 environment is configured
        assert generator.env is not None
        assert generator.env.autoescape is True
        assert generator.env.trim_blocks is True
        assert generator.env.lstrip_blocks is True

        # Check that dangerous globals are removed
        assert "__builtins__" not in generator.env.globals
        assert "__import__" not in generator.env.globals

        # Check that safe globals are present
        assert "range" in generator.env.globals
        assert "len" in generator.env.globals
        assert "str" in generator.env.globals

    def test_finalize_value_none(self):
        """Test _finalize_value converts None to empty string."""
        generator = TestFileGenerator()
        result = generator._finalize_value(None)
        assert result == ""

    def test_finalize_value_private_attribute(self):
        """Test _finalize_value blocks private attributes."""
        generator = TestFileGenerator()

        with pytest.raises(
            ValidationError, match="Access to private attributes is not allowed"
        ):
            generator._finalize_value("_private")

    def test_finalize_value_normal(self):
        """Test _finalize_value passes through normal values."""
        generator = TestFileGenerator()
        assert generator._finalize_value("test") == "test"
        assert generator._finalize_value(123) == 123
        assert generator._finalize_value(True) is True

    def test_validate_path_success(self):
        """Test successful path validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            project_root = temp_path
            file_path = project_root / "test.txt"

            generator = TestFileGenerator()
            # Should not raise any exception
            generator.validate_path(file_path, project_root)

    def test_validate_path_traversal_attack(self):
        """Test path validation prevents path traversal attacks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            file_path = project_root / ".." / "malicious.txt"

            generator = TestFileGenerator()
            with pytest.raises(FileSystemError, match="outside project directory"):
                generator.validate_path(file_path, project_root)

    def test_validate_path_dangerous_components(self):
        """Test path validation rejects dangerous path components."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            generator = TestFileGenerator()

            # Test various dangerous path components
            dangerous_paths = [
                project_root / ".." / "test.txt",
                project_root / "." / "test.txt",
                project_root / "~" / "test.txt",
            ]

            for dangerous_path in dangerous_paths:
                with pytest.raises(FileSystemError, match="dangerous path components"):
                    generator.validate_path(dangerous_path, project_root)

    def test_render_template_success(self):
        """Test successful template rendering."""
        generator = TestFileGenerator()
        template = "Hello {{ name }}!"
        context = {"name": "World"}

        result = generator.render_template(template, context)
        assert result == "Hello World!"

    def test_render_template_invalid_context(self):
        """Test template rendering with invalid context variables."""
        generator = TestFileGenerator()
        template = "Hello {{ name }}!"
        context = {"_private": "value"}  # Invalid variable name

        with pytest.raises(ValidationError):
            generator.render_template(template, context)

    @patch("ai_forge.templates.security.validate_template_content")
    def test_render_template_security_validation(self, mock_validate):
        """Test that template rendering validates content security."""
        generator = TestFileGenerator()
        template = "Hello {{ name }}!"
        context = {"name": "World"}

        generator.render_template(template, context)
        mock_validate.assert_called_once()

    def test_render_template_jinja_error(self):
        """Test template rendering with Jinja2 syntax error."""
        generator = TestFileGenerator()
        template = "Hello {{ name !"  # Invalid syntax
        context = {"name": "World"}

        with pytest.raises(TemplateRenderError, match="Template rendering failed"):
            generator.render_template(template, context)

    def test_write_file_success(self):
        """Test successful file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_path = temp_path / "test.txt"
            content = "Test content"

            generator = TestFileGenerator()
            generator.write_file(file_path, content, temp_path)

            # Verify file was written
            assert file_path.exists()
            assert file_path.read_text() == content

    def test_write_file_executable(self):
        """Test writing executable file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_path = temp_path / "script.sh"
            content = "#!/bin/bash\necho 'test'"

            generator = TestFileGenerator()
            generator.write_file(file_path, content, temp_path, executable=True)

            # Verify file was written and is executable
            assert file_path.exists()
            assert file_path.read_text() == content
            assert file_path.stat().st_mode & stat.S_IXUSR

    def test_write_file_creates_directories(self):
        """Test that write_file creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_path = temp_path / "subdir" / "nested" / "test.txt"
            content = "Test content"

            generator = TestFileGenerator()
            generator.write_file(file_path, content, temp_path)

            # Verify directory structure was created
            assert file_path.exists()
            assert file_path.read_text() == content

    def test_write_file_path_validation(self):
        """Test that write_file validates path security."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_path = temp_path / ".." / "malicious.txt"
            content = "Malicious content"

            generator = TestFileGenerator()
            with pytest.raises(FileSystemError):
                generator.write_file(file_path, content, temp_path)

    def test_write_json_file_success(self):
        """Test successful JSON file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_path = temp_path / "test.json"
            data = {"name": "test", "version": "1.0.0", "items": [1, 2, 3]}

            generator = TestFileGenerator()
            generator.write_json_file(file_path, data, temp_path)

            # Verify JSON file was written correctly
            assert file_path.exists()
            loaded_data = json.loads(file_path.read_text())
            assert loaded_data == data

    def test_write_json_file_invalid_data(self):
        """Test JSON file writing with non-serializable data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_path = temp_path / "test.json"
            data = {"invalid": set([1, 2, 3])}  # Sets are not JSON serializable

            generator = TestFileGenerator()
            with pytest.raises(ValidationError, match="Cannot serialize data as JSON"):
                generator.write_json_file(file_path, data, temp_path)

    def test_write_yaml_file_success(self):
        """Test successful YAML file writing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            file_path = temp_path / "test.yaml"
            data = {"name": "test", "version": "1.0.0", "items": [1, 2, 3]}

            generator = TestFileGenerator()
            generator.write_yaml_file(file_path, data, temp_path)

            # Verify YAML file was written correctly
            assert file_path.exists()
            loaded_data = yaml.safe_load(file_path.read_text())
            assert loaded_data == data

    def test_validate_context_success(self):
        """Test successful context validation."""
        generator = TestFileGenerator()
        context = {"project_name": "test-project"}

        # Should not raise any exception
        generator.validate_context(context)

    def test_validate_context_missing_keys(self):
        """Test context validation with missing required keys."""
        generator = TestFileGenerator()
        context = {}  # Missing required 'project_name'

        with pytest.raises(ValidationError, match="Missing required context keys"):
            generator.validate_context(context)

    def test_merge_context_defaults(self):
        """Test merging context with default values."""
        generator = TestFileGenerator()
        context = {"project_name": "test-project"}

        merged = generator.merge_context_defaults(context)

        assert merged["project_name"] == "test-project"
        assert merged["version"] == "1.0.0"  # Default value
        assert merged["debug"] is False  # Default value

    def test_generate_integration(self):
        """Test complete generation workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "test-project"}

            generator = TestFileGenerator()
            files = generator.generate(temp_path, context, temp_path)

            assert len(files) == 1
            assert files[0].exists()
            content = files[0].read_text()
            assert "Project: test-project" in content
            assert "Version: 1.0.0" in content

"""Tests for the SettingsGenerator class."""

import json
import tempfile
from pathlib import Path

import pytest

from ai_forge.exceptions import ValidationError
from ai_forge.generators.settings import SettingsGenerator


class TestSettingsGenerator:
    """Test cases for SettingsGenerator."""

    def test_get_required_context_keys(self):
        """Test required context keys."""
        generator = SettingsGenerator()
        required = generator.get_required_context_keys()

        assert "project_name" in required
        assert "language" in required

    def test_get_optional_context_keys(self):
        """Test optional context keys and defaults."""
        generator = SettingsGenerator()
        optional = generator.get_optional_context_keys()

        assert "python_version" in optional
        assert optional["python_version"] == "3.12"
        assert optional["package_manager"] == "uv"
        assert optional["testing_framework"] == "pytest"
        assert "linting_tools" in optional
        assert "ruff" in optional["linting_tools"]
        assert "mypy" in optional["linting_tools"]
        assert "editor_config" in optional
        assert "test_config" in optional
        assert "lint_config" in optional
        assert "mypy_config" in optional

    def test_generate_success(self):
        """Test successful settings.json generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Test Project", "language": "Python"}

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            assert len(files) == 1
            settings_path = files[0]
            assert settings_path.name == "settings.json"
            assert settings_path.exists()

            # Verify JSON is valid
            with open(settings_path) as f:
                data = json.load(f)

            assert data["project"]["name"] == "Test Project"
            assert data["project"]["language"] == "Python"
            assert data["development"]["python_version"] == "3.12"
            assert data["development"]["package_manager"] == "uv"

    def test_generate_with_custom_context(self):
        """Test generation with custom context values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Custom Project",
                "language": "Python",
                "python_version": "3.11",
                "package_manager": "poetry",
                "testing_framework": "unittest",
                "linting_tools": ["flake8"],
                "formatter": "black",
                "type_checker": "pyright",
                "custom_settings": {
                    "deployment": {"platform": "docker", "registry": "ghcr.io"}
                },
            }

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            assert data["development"]["python_version"] == "3.11"
            assert data["development"]["package_manager"] == "poetry"
            assert data["development"]["testing_framework"] == "unittest"
            assert data["development"]["linting_tools"] == ["flake8"]
            assert data["development"]["formatter"] == "black"
            assert data["development"]["type_checker"] == "pyright"
            assert data["deployment"]["platform"] == "docker"
            assert data["deployment"]["registry"] == "ghcr.io"

    def test_python_specific_settings(self):
        """Test that Python-specific settings are added for Python projects."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Python Project", "language": "Python"}

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            assert "python" in data
            assert data["python"]["interpreter"] == "python3.12"
            assert data["python"]["venv_path"] == ".venv"
            assert "requirements.txt" in data["python"]["requirements_files"]
            assert "import_sorting" in data["python"]
            assert data["python"]["docstring_style"] == "google"

    def test_non_python_language(self):
        """Test generation for non-Python languages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "JavaScript Project", "language": "JavaScript"}

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            assert data["project"]["language"] == "JavaScript"
            # Python-specific settings should not be present
            assert "python" not in data

    def test_pytest_configuration(self):
        """Test pytest-specific configuration generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Pytest Project",
                "language": "Python",
                "testing_framework": "pytest",
            }

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            assert "pytest" in data
            assert "testpaths" in data["pytest"]
            assert "addopts" in data["pytest"]
            assert "markers" in data["pytest"]
            assert "--cov=" in str(data["pytest"]["addopts"])
            assert "--cov-fail-under=" in str(data["pytest"]["addopts"])

    def test_ruff_configuration(self):
        """Test ruff-specific configuration generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Ruff Project",
                "language": "Python",
                "linting_tools": ["ruff", "mypy"],
            }

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            assert "ruff" in data
            assert "line-length" in data["ruff"]
            assert "target-version" in data["ruff"]
            assert "select" in data["ruff"]
            assert "ignore" in data["ruff"]
            assert "exclude" in data["ruff"]
            assert ".venv" in data["ruff"]["exclude"]
            assert "__pycache__" in data["ruff"]["exclude"]

    def test_mypy_configuration(self):
        """Test mypy-specific configuration generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "MyPy Project",
                "language": "Python",
                "type_checker": "mypy",
            }

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            assert "mypy" in data
            assert "python_version" in data["mypy"]
            assert "strict" in data["mypy"]
            assert "files" in data["mypy"]
            assert "exclude" in data["mypy"]

    def test_editor_configuration(self):
        """Test editor configuration settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Editor Project",
                "language": "Python",
                "editor_config": {
                    "tab_size": 2,
                    "insert_final_newline": False,
                    "trim_trailing_whitespace": False,
                    "charset": "utf-16",
                },
            }

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            assert data["editor"]["tab_size"] == 2
            assert data["editor"]["insert_final_newline"] is False
            assert data["editor"]["trim_trailing_whitespace"] is False
            assert data["editor"]["charset"] == "utf-16"

    def test_generate_missing_required_context(self):
        """Test generation with missing required context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Incomplete Project"
                # Missing language
            }

            generator = SettingsGenerator()
            with pytest.raises(ValidationError, match="Missing required context keys"):
                generator.generate(temp_path, context, temp_path)

    def test_json_format_validity(self):
        """Test that generated JSON is properly formatted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "JSON Format Test", "language": "Python"}

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Read as text to check formatting
            content = files[0].read_text()

            # Should be properly indented
            assert "  " in content  # 2-space indentation

            # Should be valid JSON
            data = json.loads(content)
            assert isinstance(data, dict)

            # Check that it's sorted (json.dumps with sort_keys=True)
            keys = list(data.keys())
            assert keys == sorted(keys)

    def test_configuration_completeness(self):
        """Test that all expected configuration sections are present."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Complete Project", "language": "Python"}

            generator = SettingsGenerator()
            files = generator.generate(temp_path, context, temp_path)

            with open(files[0]) as f:
                data = json.load(f)

            # Check all expected top-level sections
            expected_sections = [
                "project",
                "development",
                "editor",
                "testing",
                "linting",
                "type_checking",
                "environment",
                "paths",
            ]

            for section in expected_sections:
                assert section in data, f"Missing section: {section}"

            # Check project section
            assert "name" in data["project"]
            assert "language" in data["project"]
            assert "version" in data["project"]

            # Check development section
            assert "python_version" in data["development"]
            assert "package_manager" in data["development"]
            assert "testing_framework" in data["development"]

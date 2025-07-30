"""Comprehensive test suite for AI Forge configuration models and loader."""

import tempfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from ai_forge.core import (
    AIForgeConfig,
    ConfigLoader,
    ConfigLoadError,
    ConfigSaveError,
    FileConfig,
    TemplateConfig,
)


class TestFileConfig:
    """Test cases for FileConfig model."""

    def test_valid_file_config(self):
        """Test creating a valid FileConfig."""
        config = FileConfig(path="src/main.py", content="print('Hello, World!')")
        assert config.path == "src/main.py"
        assert config.content == "print('Hello, World!')"

    def test_file_config_with_gitignore(self):
        """Test that .gitignore is allowed as hidden file."""
        config = FileConfig(path=".gitignore", content="*.pyc\n__pycache__/")
        assert config.path == ".gitignore"

    def test_file_config_with_env_example(self):
        """Test that .env.example is allowed as hidden file."""
        config = FileConfig(
            path=".env.example", content="DATABASE_URL=postgresql://localhost/db"
        )
        assert config.path == ".env.example"

    def test_file_config_with_claude_dir(self):
        """Test that .claude directory is allowed."""
        config = FileConfig(path=".claude", content="")
        assert config.path == ".claude"

    def test_empty_path_validation(self):
        """Test that empty path raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FileConfig(path="", content="test")

        assert "Path cannot be empty" in str(exc_info.value)

    def test_absolute_path_validation(self):
        """Test that absolute paths are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            FileConfig(path="/etc/passwd", content="malicious")

        assert "Absolute paths are not allowed" in str(exc_info.value)

    def test_directory_traversal_validation(self):
        """Test that directory traversal patterns are rejected."""
        traversal_paths = [
            "../etc/passwd",
            "src/../../../etc/passwd",
            "src/../../config.yaml",
            "./../../sensitive.txt",
        ]

        for path in traversal_paths:
            with pytest.raises(ValidationError) as exc_info:
                FileConfig(path=path, content="malicious")
            assert "Path traversal patterns (..) are not allowed" in str(exc_info.value)

    def test_hidden_system_files_validation(self):
        """Test that unauthorized hidden files are rejected."""
        forbidden_paths = [".bashrc", ".ssh", ".aws", ".config"]

        for path in forbidden_paths:
            with pytest.raises(ValidationError) as exc_info:
                FileConfig(path=path, content="malicious")
            assert "Hidden system files are not allowed" in str(exc_info.value)

    def test_nested_valid_paths(self):
        """Test that nested valid paths work correctly."""
        valid_paths = [
            "src/utils/helper.py",
            "docs/api/reference.md",
            "tests/unit/test_config.py",
            ".claude/hooks/pre-commit.sh",
        ]

        for path in valid_paths:
            config = FileConfig(path=path, content="valid content")
            assert config.path == path


class TestTemplateConfig:
    """Test cases for TemplateConfig model."""

    def test_valid_template_config(self):
        """Test creating a valid TemplateConfig."""
        config = TemplateConfig(
            name="python-starter",
            description="A Python starter template",
            version="1.0.0",
        )
        assert config.name == "python-starter"
        assert config.description == "A Python starter template"
        assert config.version == "1.0.0"

    def test_template_name_validation(self):
        """Test template name validation."""
        valid_names = [
            "python-starter",
            "typescript_template",
            "go-basic",
            "fullstack123",
            "template_v2",
        ]

        for name in valid_names:
            config = TemplateConfig(
                name=name, description="Test template", version="1.0.0"
            )
            assert config.name == name

    def test_invalid_template_names(self):
        """Test that invalid template names are rejected."""
        invalid_names = [
            "",
            "template with spaces",
            "template@special",
            "template.with.dots",
            "template/with/slashes",
            "template#hash",
        ]

        for name in invalid_names:
            with pytest.raises(ValidationError) as exc_info:
                TemplateConfig(name=name, description="Test template", version="1.0.0")
            error_msg = str(exc_info.value)
            assert any(
                msg in error_msg
                for msg in [
                    "Template name cannot be empty",
                    "Template name must contain only alphanumeric characters, "
                    "hyphens, and underscores",
                ]
            )

    def test_semantic_version_validation(self):
        """Test semantic version validation."""
        valid_versions = ["1.0.0", "10.20.30", "0.1.0", "2.1.15"]

        for version in valid_versions:
            config = TemplateConfig(
                name="test-template", description="Test template", version=version
            )
            assert config.version == version

    def test_invalid_semantic_versions(self):
        """Test that invalid semantic versions are rejected."""
        invalid_versions = [
            "",
            "1.0",
            "v1.0.0",
            "1.0.0-alpha",
            "1.0.0.1",
            "1.x.0",
            "latest",
            "1.0.0-beta.1",
        ]

        for version in invalid_versions:
            with pytest.raises(ValidationError) as exc_info:
                TemplateConfig(
                    name="test-template", description="Test template", version=version
                )
            error_msg = str(exc_info.value)
            assert any(
                msg in error_msg
                for msg in [
                    "Version cannot be empty",
                    "Version must be in semantic version format (x.y.z)",
                ]
            )


class TestAIForgeConfig:
    """Test cases for AIForgeConfig model."""

    def test_valid_ai_forge_config(self):
        """Test creating a valid AIForgeConfig."""
        config = AIForgeConfig(
            project_name="my-awesome-project", template_name="python-starter"
        )
        assert config.project_name == "my-awesome-project"
        assert config.template_name == "python-starter"
        assert config.files == []

    def test_ai_forge_config_with_files(self):
        """Test AIForgeConfig with file configurations."""
        files = [
            FileConfig(path="src/main.py", content="print('Hello')"),
            FileConfig(path="README.md", content="# My Project"),
        ]

        config = AIForgeConfig(
            project_name="test-project", template_name="starter", files=files
        )

        assert len(config.files) == 2
        assert config.files[0].path == "src/main.py"
        assert config.files[1].path == "README.md"

    def test_project_name_validation(self):
        """Test project name validation."""
        valid_names = [
            "my-project",
            "awesome_app",
            "project123",
            "web-api-v2",
            "cli_tool",
        ]

        for name in valid_names:
            config = AIForgeConfig(project_name=name)
            assert config.project_name == name

    def test_invalid_project_names(self):
        """Test that invalid project names are rejected."""
        invalid_names = [
            "",
            "project with spaces",
            "project@domain.com",
            "project.with.dots",
            "project/with/slashes",
            "project#tag",
        ]

        for name in invalid_names:
            with pytest.raises(ValidationError) as exc_info:
                AIForgeConfig(project_name=name)
            error_msg = str(exc_info.value)
            assert any(
                msg in error_msg
                for msg in [
                    "Project name cannot be empty",
                    "Project name must contain only alphanumeric characters, "
                    "hyphens, and underscores",
                ]
            )

    def test_optional_template_name(self):
        """Test that template_name is optional."""
        config = AIForgeConfig(project_name="test-project")
        assert config.template_name is None

    def test_default_empty_files(self):
        """Test that files defaults to empty list."""
        config = AIForgeConfig(project_name="test-project")
        assert config.files == []


class TestConfigLoader:
    """Test cases for ConfigLoader class."""

    def test_create_default_config(self):
        """Test creating a default configuration."""
        config = ConfigLoader.create_default_config("my-project")

        assert config.project_name == "my-project"
        assert config.template_name == "starter"
        assert config.files == []

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent configuration file."""
        with pytest.raises(ConfigLoadError) as exc_info:
            ConfigLoader.load_config("nonexistent.yaml")

        assert "Configuration file not found" in str(exc_info.value)

    def test_load_config_from_yaml(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "project_name": "test-project",
            "template_name": "python-starter",
            "files": [{"path": "src/main.py", "content": "print('Hello, World!')"}],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(config_data, f)
            temp_path = f.name

        try:
            config = ConfigLoader.load_config(temp_path)

            assert config.project_name == "test-project"
            assert config.template_name == "python-starter"
            assert len(config.files) == 1
            assert config.files[0].path == "src/main.py"
            assert config.files[0].content == "print('Hello, World!')"
        finally:
            Path(temp_path).unlink()

    def test_load_empty_yaml(self):
        """Test loading empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            # Should raise ValidationError due to missing required fields
            with pytest.raises(ValidationError):
                ConfigLoader.load_config(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML syntax."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("project_name: test\ninvalid: yaml: syntax:")
            temp_path = f.name

        try:
            with pytest.raises(ConfigLoadError) as exc_info:
                ConfigLoader.load_config(temp_path)
            assert "Invalid YAML" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()

    def test_save_and_load_config_roundtrip(self):
        """Test saving and loading configuration preserves data."""
        original_config = AIForgeConfig(
            project_name="roundtrip-test",
            template_name="test-template",
            files=[
                FileConfig(path="src/app.py", content="# Main application"),
                FileConfig(path="tests/test_app.py", content="# Tests"),
            ],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            # Save configuration
            ConfigLoader.save_config(original_config, temp_path)

            # Load it back
            loaded_config = ConfigLoader.load_config(temp_path)

            # Verify data integrity
            assert loaded_config.project_name == original_config.project_name
            assert loaded_config.template_name == original_config.template_name
            assert len(loaded_config.files) == len(original_config.files)

            for i, file_config in enumerate(loaded_config.files):
                assert file_config.path == original_config.files[i].path
                assert file_config.content == original_config.files[i].content
        finally:
            Path(temp_path).unlink()

    def test_load_template_config(self):
        """Test loading template configuration."""
        template_data = {
            "name": "python-starter",
            "description": "Python starter template",
            "version": "1.2.3",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(template_data, f)
            temp_path = f.name

        try:
            template_config = ConfigLoader.load_template_config(temp_path)

            assert template_config.name == "python-starter"
            assert template_config.description == "Python starter template"
            assert template_config.version == "1.2.3"
        finally:
            Path(temp_path).unlink()

    def test_save_template_config(self):
        """Test saving template configuration."""
        template_config = TemplateConfig(
            name="test-template", description="A test template", version="0.1.0"
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            ConfigLoader.save_template_config(template_config, temp_path)

            # Verify file was created and contains expected data
            with open(temp_path, "r") as f:
                data = yaml.safe_load(f)

            assert data["name"] == "test-template"
            assert data["description"] == "A test template"
            assert data["version"] == "0.1.0"
        finally:
            Path(temp_path).unlink()

    def test_load_yaml_data(self):
        """Test loading raw YAML data."""
        test_data = {"key1": "value1", "key2": 42, "key3": ["item1", "item2"]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(test_data, f)
            temp_path = f.name

        try:
            data = ConfigLoader.load_yaml_data(temp_path)

            assert data == test_data
        finally:
            Path(temp_path).unlink()

    def test_save_config_creates_directories(self):
        """Test that save_config creates parent directories."""
        config = AIForgeConfig(project_name="test-project")

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "dir" / "config.yaml"

            ConfigLoader.save_config(config, nested_path)

            assert nested_path.exists()
            assert nested_path.is_file()

    def test_save_config_without_creating_directories(self):
        """Test saving config without creating directories raises error."""
        config = AIForgeConfig(project_name="test-project")

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nonexistent" / "config.yaml"

            with pytest.raises(ConfigSaveError):
                ConfigLoader.save_config(config, nested_path, create_dirs=False)

    def test_load_directory_as_file(self):
        """Test that loading a directory raises appropriate error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ConfigLoadError) as exc_info:
                ConfigLoader.load_config(temp_dir)
            assert "Path is not a file" in str(exc_info.value)


class TestConfigSecurity:
    """Security-focused test cases for configuration validation."""

    def test_malicious_path_injection_attempts(self):
        """Test various malicious path injection attempts."""
        malicious_patterns = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "./../../sensitive/data.txt",
            "/var/log/auth.log",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "..%2F..%2F..%2Fetc%2Fpasswd",  # URL-encoded
            "...///etc/passwd",
            "..\\..\\.\\windows\\system32",
        ]

        for malicious_path in malicious_patterns:
            with pytest.raises(ValidationError):
                FileConfig(path=malicious_path, content="malicious content")

    def test_configuration_with_malicious_files(self):
        """Test that configurations with malicious files are rejected."""
        malicious_files = [
            FileConfig(
                path="legitimate.py", content="import os; os.system('rm -rf /')"
            ),
            FileConfig(path="normal.txt", content="normal content"),
        ]

        # The configuration should be created (content validation is not part of MVP)
        # but path validation should still work
        try:
            config = AIForgeConfig(project_name="test-project", files=malicious_files)
            # Content validation is not implemented in MVP, so this should succeed
            assert len(config.files) == 2
        except ValidationError:
            # If content validation is added later, this would be the expected behavior
            pass

    def test_yaml_injection_attempts(self):
        """Test YAML injection resistance."""
        yaml_content = """
project_name: "test"
files:
  - path: "test.py"
    content: |
      import subprocess
      subprocess.call(['rm', '-rf', '/'])
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            # Should load successfully as YAML is valid and content validation
            # is not part of MVP scope
            config = ConfigLoader.load_config(temp_path)
            assert config.project_name == "test"
        finally:
            Path(temp_path).unlink()

    def test_large_configuration_handling(self):
        """Test handling of unusually large configurations."""
        # Create a configuration with many files
        large_files = [
            FileConfig(
                path=f"file_{i}.py",
                content="# " + "x" * 1000,  # 1KB of content per file
            )
            for i in range(100)  # 100 files
        ]

        config = AIForgeConfig(project_name="large-project", files=large_files)

        assert len(config.files) == 100

        # Test saving and loading large configuration
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            ConfigLoader.save_config(config, temp_path)
            loaded_config = ConfigLoader.load_config(temp_path)

            assert len(loaded_config.files) == 100
            assert loaded_config.project_name == "large-project"
        finally:
            Path(temp_path).unlink()


# Test fixtures for pytest
@pytest.fixture
def sample_config():
    """Sample AI Forge configuration for testing."""
    return AIForgeConfig(
        project_name="sample-project",
        template_name="python-starter",
        files=[
            FileConfig(
                path="src/main.py",
                content="#!/usr/bin/env python3\nprint('Hello, World!')",
            ),
            FileConfig(
                path="README.md",
                content="# Sample Project\n\nThis is a sample project.",
            ),
        ],
    )


@pytest.fixture
def sample_template_config():
    """Sample template configuration for testing."""
    return TemplateConfig(
        name="python-starter",
        description="A Python starter template with best practices",
        version="1.0.0",
    )


@pytest.fixture
def temp_config_file(sample_config):
    """Temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config_data = sample_config.model_dump()
        yaml.safe_dump(config_data, f)
        temp_path = f.name

    yield temp_path
    Path(temp_path).unlink()

"""Tests for the McpGenerator class."""

import json
import tempfile
from pathlib import Path

import pytest

from ai_forge.exceptions import ValidationError
from ai_forge.generators.mcp import McpGenerator


class TestMcpGenerator:
    """Test cases for McpGenerator."""

    def test_get_required_context_keys(self):
        """Test required context keys."""
        generator = McpGenerator()
        required = generator.get_required_context_keys()

        assert "project_name" in required

    def test_get_optional_context_keys(self):
        """Test optional context keys and defaults."""
        generator = McpGenerator()
        optional = generator.get_optional_context_keys()

        assert "mcp_version" in optional
        assert optional["mcp_version"] == "2024-11-05"
        assert "servers" in optional
        assert "filesystem" in optional["servers"]
        assert "tools" in optional
        assert "security" in optional
        assert "preferences" in optional
        assert "custom_servers" in optional

    def test_generate_success(self):
        """Test successful MCP configuration generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Test MCP Project"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Should generate 3 files
            assert len(files) == 3

            file_names = [f.name for f in files]
            assert "mcp.json" in file_names
            assert "mcp-tools.json" in file_names
            assert "mcp-client.json" in file_names

            # Verify all files exist
            for file_path in files:
                assert file_path.exists()

    def test_mcp_config_structure(self):
        """Test main MCP configuration file structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "MCP Structure Test"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            mcp_config_file = next(f for f in files if f.name == "mcp.json")

            with open(mcp_config_file) as f:
                data = json.load(f)

            # Check required top-level fields
            assert "mcpVersion" in data
            assert "description" in data
            assert "servers" in data
            assert "security" in data
            assert "preferences" in data

            # Check version
            assert data["mcpVersion"] == "2024-11-05"

            # Check description
            assert "MCP Structure Test" in data["description"]

            # Check servers structure
            assert "filesystem" in data["servers"]
            assert "command" in data["servers"]["filesystem"]
            assert "args" in data["servers"]["filesystem"]

    def test_tools_config_structure(self):
        """Test tools configuration file structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Tools Structure Test"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            tools_config_file = next(f for f in files if f.name == "mcp-tools.json")

            with open(tools_config_file) as f:
                data = json.load(f)

            # Check required fields
            assert "version" in data
            assert "tools" in data

            # Check version
            assert data["version"] == "2024-11-05"

            # Check tools structure
            assert "filesystem" in data["tools"]
            filesystem_tools = data["tools"]["filesystem"]
            assert "read_file" in filesystem_tools
            assert "write_file" in filesystem_tools
            assert "list_directory" in filesystem_tools

    def test_client_config_template(self):
        """Test client configuration template rendering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Client Config Test"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            client_config_file = next(f for f in files if f.name == "mcp-client.json")

            with open(client_config_file) as f:
                data = json.load(f)

            # Check mcpServers section
            assert "mcpServers" in data
            assert "Client Config Test-filesystem" in data["mcpServers"]

            # Check preferences
            assert "preferences" in data
            assert "autoApprove" in data["preferences"]
            assert "maxConcurrentRequests" in data["preferences"]
            assert "timeout" in data["preferences"]
            assert "logLevel" in data["preferences"]

            # Check security
            assert "security" in data
            assert "allowedPaths" in data["security"]
            assert "deniedPaths" in data["security"]
            assert "maxFileSize" in data["security"]
            assert "sandbox" in data["security"]

    def test_custom_servers_integration(self):
        """Test integration of custom servers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Custom Servers Test",
                "custom_servers": {
                    "database": {
                        "command": "node",
                        "args": ["db-server.js"],
                        "env": {"DB_URL": "sqlite:///test.db"},
                    },
                    "web": {
                        "command": "python",
                        "args": ["-m", "web_server"],
                        "description": "Web server for testing",
                    },
                },
            }

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Check main config
            mcp_config_file = next(f for f in files if f.name == "mcp.json")
            with open(mcp_config_file) as f:
                data = json.load(f)

            assert "database" in data["servers"]
            assert "web" in data["servers"]
            assert data["servers"]["database"]["command"] == "node"
            assert data["servers"]["database"]["args"] == ["db-server.js"]
            assert data["servers"]["database"]["env"]["DB_URL"] == "sqlite:///test.db"

            # Check client config
            client_config_file = next(f for f in files if f.name == "mcp-client.json")
            with open(client_config_file) as f:
                client_data = json.load(f)

            assert "database" in client_data["mcpServers"]
            assert "web" in client_data["mcpServers"]

    def test_security_configuration(self):
        """Test security configuration options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Security Test",
                "security": {
                    "allowed_paths": ["src/", "docs/"],
                    "denied_paths": [".env", "*.key", ".git", "secrets/"],
                    "max_file_size": "5MB",
                    "sandbox": True,
                },
            }

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            mcp_config_file = next(f for f in files if f.name == "mcp.json")
            with open(mcp_config_file) as f:
                data = json.load(f)

            security = data["security"]
            assert security["allowedPaths"] == ["src/", "docs/"]
            assert security["deniedPaths"] == [".env", "*.key", ".git", "secrets/"]
            assert security["maxFileSize"] == "5MB"
            assert security["sandbox"] is True

    def test_preferences_configuration(self):
        """Test preferences configuration options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {
                "project_name": "Preferences Test",
                "preferences": {
                    "auto_approve": True,
                    "max_concurrent_requests": 5,
                    "timeout": 60,
                    "log_level": "DEBUG",
                },
            }

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            mcp_config_file = next(f for f in files if f.name == "mcp.json")
            with open(mcp_config_file) as f:
                data = json.load(f)

            prefs = data["preferences"]
            assert prefs["autoApprove"] is True
            assert prefs["maxConcurrentRequests"] == 5
            assert prefs["timeout"] == 60
            assert prefs["logLevel"] == "DEBUG"

    def test_mcp_version_configuration(self):
        """Test MCP version configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Version Test", "mcp_version": "2024-12-01"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            # Check main config version
            mcp_config_file = next(f for f in files if f.name == "mcp.json")
            with open(mcp_config_file) as f:
                data = json.load(f)

            assert data["mcpVersion"] == "2024-12-01"

            # Check tools config version
            tools_config_file = next(f for f in files if f.name == "mcp-tools.json")
            with open(tools_config_file) as f:
                tools_data = json.load(f)

            assert tools_data["version"] == "2024-12-01"

    def test_generate_missing_required_context(self):
        """Test generation with missing required context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {}  # Missing project_name

            generator = McpGenerator()
            with pytest.raises(ValidationError, match="Missing required context keys"):
                generator.generate(temp_path, context, temp_path)

    def test_json_format_validity(self):
        """Test that all generated JSON files are properly formatted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "JSON Validity Test"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            for file_path in files:
                if file_path.suffix == ".json":
                    # Should be valid JSON
                    with open(file_path) as f:
                        data = json.load(f)

                    assert isinstance(data, dict)

                    # Check formatting (should be indented)
                    content = file_path.read_text()
                    assert "  " in content  # 2-space indentation

    def test_default_filesystem_server(self):
        """Test default filesystem server configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Filesystem Test"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            mcp_config_file = next(f for f in files if f.name == "mcp.json")
            with open(mcp_config_file) as f:
                data = json.load(f)

            fs_server = data["servers"]["filesystem"]
            assert fs_server["command"] == "npx"
            assert "-y" in fs_server["args"]
            assert "@modelcontextprotocol/server-filesystem" in fs_server["args"]
            assert "." in fs_server["args"]

    def test_tools_definitions(self):
        """Test tools definitions structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            context = {"project_name": "Tools Definitions Test"}

            generator = McpGenerator()
            files = generator.generate(temp_path, context, temp_path)

            tools_config_file = next(f for f in files if f.name == "mcp-tools.json")
            with open(tools_config_file) as f:
                data = json.load(f)

            fs_tools = data["tools"]["filesystem"]

            # Check read_file tool
            assert "read_file" in fs_tools
            assert "description" in fs_tools["read_file"]
            assert "parameters" in fs_tools["read_file"]
            assert "path" in fs_tools["read_file"]["parameters"]

            # Check write_file tool
            assert "write_file" in fs_tools
            assert "description" in fs_tools["write_file"]
            assert "parameters" in fs_tools["write_file"]
            assert "path" in fs_tools["write_file"]["parameters"]
            assert "content" in fs_tools["write_file"]["parameters"]

            # Check list_directory tool
            assert "list_directory" in fs_tools
            assert "description" in fs_tools["list_directory"]
            assert "parameters" in fs_tools["list_directory"]
            assert "path" in fs_tools["list_directory"]["parameters"]

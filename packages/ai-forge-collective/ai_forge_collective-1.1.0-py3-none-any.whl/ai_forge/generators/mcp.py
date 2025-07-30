"""Generator for MCP (Model Context Protocol) configuration files."""

from pathlib import Path
from typing import Any

from .base import FileGenerator


class McpGenerator(FileGenerator):
    """Generator for MCP (Model Context Protocol) configuration files.

    Creates MCP configuration files for Claude Code integration,
    including server configurations and tool definitions.
    """

    def get_required_context_keys(self) -> list[str]:
        """Get list of required context keys for MCP configuration generation.

        Returns:
            List of required context key names
        """
        return [
            "project_name",
        ]

    def get_optional_context_keys(self) -> dict[str, Any]:
        """Get dictionary of optional context keys with default values.

        Returns:
            Dictionary mapping optional key names to default values
        """
        return {
            "mcp_version": "2024-11-05",
            "servers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
                    "description": "Filesystem access for project files",
                }
            },
            "tools": {
                "filesystem": {
                    "read_file": {
                        "description": "Read file contents",
                        "parameters": {"path": "File path to read"},
                    },
                    "write_file": {
                        "description": "Write content to file",
                        "parameters": {
                            "path": "File path to write",
                            "content": "Content to write",
                        },
                    },
                    "list_directory": {
                        "description": "List directory contents",
                        "parameters": {"path": "Directory path to list"},
                    },
                }
            },
            "security": {
                "allowed_paths": ["."],
                "denied_paths": [
                    ".git",
                    ".env",
                    "*.key",
                    "*.pem",
                    "node_modules",
                    ".venv",
                    "__pycache__",
                ],
                "max_file_size": "10MB",
                "sandbox": True,
            },
            "preferences": {
                "auto_approve": False,
                "max_concurrent_requests": 10,
                "timeout": 30,
                "log_level": "INFO",
            },
            "custom_servers": {},
        }

    def _build_mcp_config(self, context: dict[str, Any]) -> dict[str, Any]:
        """Build the complete MCP configuration.

        Args:
            context: Generation context

        Returns:
            Complete MCP configuration dictionary
        """
        config = {
            "mcpVersion": context["mcp_version"],
            "description": f"MCP configuration for {context['project_name']}",
            "servers": {},
        }

        # Add default servers
        for server_name, server_config in context["servers"].items():
            config["servers"][server_name] = {
                "command": server_config["command"],
                "args": server_config["args"],
            }

            # Add optional fields
            if "env" in server_config:
                config["servers"][server_name]["env"] = server_config["env"]
            if "description" in server_config:
                config["servers"][server_name]["description"] = server_config[
                    "description"
                ]

        # Add custom servers
        if context["custom_servers"]:
            config["servers"].update(context["custom_servers"])

        # Add security configuration
        if context["security"]:
            config["security"] = {
                "allowedPaths": context["security"]["allowed_paths"],
                "deniedPaths": context["security"]["denied_paths"],
                "maxFileSize": context["security"]["max_file_size"],
                "sandbox": context["security"]["sandbox"],
            }

        # Add preferences
        if context["preferences"]:
            config["preferences"] = {
                "autoApprove": context["preferences"]["auto_approve"],
                "maxConcurrentRequests": context["preferences"][
                    "max_concurrent_requests"
                ],
                "timeout": context["preferences"]["timeout"],
                "logLevel": context["preferences"]["log_level"],
            }

        return config

    def _build_tools_config(self, context: dict[str, Any]) -> dict[str, Any]:
        """Build tools configuration for MCP.

        Args:
            context: Generation context

        Returns:
            Tools configuration dictionary
        """
        return {"version": context["mcp_version"], "tools": context["tools"]}

    def _get_mcp_client_config_template(self) -> str:
        """Get template for MCP client configuration.

        Returns:
            MCP client config template string
        """
        return """{
  "mcpServers": {
    "{{ project_name }}-filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {
        "PROJECT_ROOT": "."
      }
    }{% if custom_servers %},
    {% for name, config in custom_servers.items() %}"{{ name }}": {
      "command": "{{ config.command }}",
      "args": {{ config.args | tojson }}{% if config.env %},
      "env": {{ config.env | tojson }}{% endif %}
    }{% if not loop.last %},{% endif %}
    {% endfor %}{% endif %}
  },
  "preferences": {
    "autoApprove": {{ preferences.auto_approve | tojson }},
    "maxConcurrentRequests": {{ preferences.max_concurrent_requests }},
    "timeout": {{ preferences.timeout }},
    "logLevel": "{{ preferences.log_level }}"
  }{% if security %},
  "security": {
    "allowedPaths": {{ security.allowed_paths | tojson }},
    "deniedPaths": {{ security.denied_paths | tojson }},
    "maxFileSize": "{{ security.max_file_size }}",
    "sandbox": {{ security.sandbox | tojson }}
  }{% endif %}
}"""

    def generate(
        self, output_path: Path, context: dict[str, Any], project_root: Path
    ) -> list[Path]:
        """Generate MCP configuration files based on context.

        Args:
            output_path: Directory where to generate the files
            context: Generation context and variables
            project_root: Project root directory for path validation

        Returns:
            List of generated MCP configuration file paths

        Raises:
            FileSystemError: If file generation fails
            TemplateRenderError: If template rendering fails
            ValidationError: If context is invalid
        """
        # Validate context
        self.validate_context(context)

        # Merge with defaults
        full_context = self.merge_context_defaults(context)

        generated_files = []

        # Generate main MCP configuration
        mcp_config = self._build_mcp_config(full_context)
        mcp_config_path = output_path / "mcp.json"
        self.write_json_file(mcp_config_path, mcp_config, project_root, indent=2)
        generated_files.append(mcp_config_path)

        # Generate tools configuration
        tools_config = self._build_tools_config(full_context)
        tools_config_path = output_path / "mcp-tools.json"
        self.write_json_file(tools_config_path, tools_config, project_root, indent=2)
        generated_files.append(tools_config_path)

        # Generate client configuration template
        client_template = self._get_mcp_client_config_template()
        client_content = self.render_template(client_template, full_context)
        client_config_path = output_path / "mcp-client.json"
        self.write_file(client_config_path, client_content, project_root)
        generated_files.append(client_config_path)

        return generated_files

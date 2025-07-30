# Starter Template

A universal starter template for AI Forge that provides basic Claude Code configuration and development workflow setup for any project type.

## Overview

This template creates a minimal but secure Claude Code setup that works across all programming languages and project types. It provides:

- Basic Claude Code configuration with safe permissions
- Project documentation template  
- Cross-platform format-on-save hook
- Language-agnostic development workflow

## Generated Files

- `CLAUDE.md` - Project-specific Claude Code instructions
- `.claude/settings.json` - Claude Code configuration with minimal permissions
- `.claude/hooks/format-on-save.sh` - Cross-platform formatting hook

## Required Variables

- `project_name` - Name of the project
- `description` - Brief description of the project
- `author` - Project author/maintainer

## Optional Variables

- `date` - Creation date (defaults to current date)
- `editor` - Primary editor (defaults to "vscode")
- `git_enabled` - Enable git integration (defaults to true)
- `format_on_save` - Enable format-on-save hook (defaults to true)
- `claude_permissions` - List of allowed Claude permissions (defaults to ["Edit", "Write", "Read"])

## Security Features

- Minimal Claude Code permissions (Edit, Write, Read only)
- Safe hook implementation with error handling
- No hardcoded paths or platform assumptions
- Input validation and sanitization

## Cross-Platform Compatibility

This template is designed to work on:
- Linux
- macOS  
- Windows (with WSL or Git Bash)

The generated scripts use portable shell commands and handle platform differences gracefully.

## Usage

```bash
ai-forge init starter --project-name "My Project" --description "A new project" --author "Your Name"
```

## Customization

After generation, you can customize:
- Add more specific Claude permissions in `.claude/settings.json`
- Modify the format-on-save hook for your specific tools
- Extend `CLAUDE.md` with project-specific instructions
- Add additional hooks to `.claude/hooks/`
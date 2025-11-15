# OpenCode CLI Configuration

This directory contains configuration files and examples for [OpenCode CLI](https://opencode.ai), an AI-assisted development tool that helps you code faster and smarter.

## Quick Start

The main configuration file is `opencode.json`. This file defines how OpenCode behaves in your development workflow, including which AI models to use, custom commands, and specialized agents.

### What's Inside

- **`opencode.json`** - Your main OpenCode configuration
- **`sample-configs/`** - Example configurations for different scenarios
  - `sample-docker-mcp.json` - Docker-based MCP server setup
  - `sample-npx-mcp.json` - NPX-based MCP server (Snyk example)
- **`AGENTS.md`** - Technical documentation for AI assistants

## Key Features

### 🎯 Tiered AI Models

This configuration uses a smart tiered approach:

- **Fast Model** (`xai/grok-2-mini`) - Quick fixes, formatting, simple queries
- **Balanced Model** (`claude-sonnet-4-5`) - General development, complex tasks
- Multiple provider options via GitHub Copilot (GPT-4o, GPT-5, Claude, Gemini, Grok)

### 🤖 Specialized Agents

Pre-configured agents for different workflows:

| Agent | Purpose | Can Modify Code? |
|-------|---------|------------------|
| **quick** | Fast fixes, formatting, simple tasks | ✅ Yes |
| **reviewer** | Code review, analysis, security checks | ❌ No (read-only) |
| **docs** | Documentation writing | ✅ Yes (docs only) |

### ⚡ Custom Commands

Ready-to-use commands for common tasks:

```bash
# Quick fixes using fast model
opencode quick-fix "fix the typo in main.js"

# Deep code analysis
opencode analyze "review the authentication system"

# Code review (read-only, no changes)
opencode review "check security in auth.js"

# Generate/update documentation
opencode document "API endpoints in routes/"

# Intelligent refactoring
opencode refactor "optimize database queries"
```

## Configuration Highlights

### Models & Providers

```json
{
  "model": "anthropic/claude-sonnet-4-5-20250929",
  "small_model": "xai/grok-2-mini"
}
```

Access to multiple AI models through GitHub Copilot, including GPT-5, Claude Sonnet 4.5, Gemini 2.5 Pro, and more.

### MCP Servers

Model Context Protocol (MCP) servers extend OpenCode with additional capabilities:

```json
{
  "mcp": {
    "github": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "enabled": true
    }
  }
}
```

**Add Your Own MCP Servers**:
- See `sample-configs/` for Docker and NPX examples
- Popular options: Snyk security scanning, custom tool integrations
- Set environment variables for authentication (e.g., `SNYK_TOKEN`)

### Auto-Loaded Instructions

OpenCode automatically reads project context from:
- `AGENTS.md` - AI assistant guidelines
- `.cursor/rules/*.md` - Project-specific rules
- `README.md` - Project documentation

This ensures the AI understands your project's conventions and requirements.

## Customization

### Adding a New Agent

Edit the `agent` section in `opencode.json`:

```json
{
  "agent": {
    "your-agent": {
      "description": "What this agent does",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-5-20250929",
      "temperature": 0.1,
      "tools": {
        "write": true,
        "edit": true,
        "read": true
      }
    }
  }
}
```

### Creating Custom Commands

Add to the `command` section:

```json
{
  "command": {
    "my-command": {
      "template": "Do something with: $ARGUMENTS",
      "description": "What this command does",
      "agent": "quick"  // Optional: use a specific agent
    }
  }
}
```

Then use it: `opencode my-command "your input here"`

### Adding MCP Servers

**Example: Docker-based server**
```json
{
  "mcp": {
    "my-server": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "my-server:latest"],
      "enabled": true,
      "environment": {
        "API_KEY": "${MY_API_KEY}"
      },
      "timeout": 10000
    }
  },
  "tools": {
    "my-server": true  // Enable the tool
  }
}
```

**Example: NPX-based server**
```json
{
  "mcp": {
    "my-npm-tool": {
      "type": "local",
      "command": ["npx", "-y", "@company/mcp-server"],
      "enabled": true,
      "environment": {
        "TOKEN": "${MY_TOKEN}"
      }
    }
  }
}
```

## Environment Variables

Some integrations require authentication tokens. Set these in your shell:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN = "your-token-here"
$env:SNYK_TOKEN = "your-snyk-token"

# Linux/Mac
export GITHUB_TOKEN="your-token-here"
export SNYK_TOKEN="your-snyk-token"
```

Reference them in config using `${VARIABLE_NAME}` syntax.

## Tips & Best Practices

### ✅ Do's
- Use the `quick` agent for simple, fast tasks
- Use the `reviewer` agent when you want analysis without modifications
- Keep temperature low (0.1-0.2) for code generation
- Use higher temperature (0.3-0.5) for creative tasks like documentation
- Test MCP servers individually before combining them

### ❌ Don'ts
- Don't give write permissions to review/analysis agents
- Don't set timeouts too low for remote MCP servers
- Don't forget to enable tools in the `tools` section after adding MCP servers
- Don't hardcode secrets - always use environment variables

## Troubleshooting

**OpenCode not using the right model?**
- Check the `model` and `small_model` settings
- Verify your agent assignments in custom commands

**MCP server not working?**
- Ensure environment variables are set: `echo $env:VARIABLE_NAME` (PowerShell)
- Check Docker/NPX is installed and accessible
- Verify the tool is enabled in the `tools` section
- Increase timeout if the server is slow to respond

**Custom command not found?**
- Verify JSON syntax is valid (use a JSON validator)
- Check that the command is defined in the `command` section
- Restart OpenCode after configuration changes

## Learn More

- [OpenCode Documentation](https://opencode.ai) - Official docs and guides
- [Model Context Protocol](https://modelcontextprotocol.io) - Learn about MCP
- `AGENTS.md` - Detailed technical documentation for AI assistants

## Contributing

Found a useful configuration? Create a pull request to share it with others:
1. Add your config to `sample-configs/`
2. Document it in this README
3. Submit a PR

---

*This configuration is optimized for efficient AI-assisted development with cost-effective model selection and specialized agents for different workflows.*

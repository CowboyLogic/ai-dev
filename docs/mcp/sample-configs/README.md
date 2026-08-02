# MCP Sample Configurations

This directory contains example configuration files for integrating Model Context Protocol (MCP) servers with AI development tools.

## Available Samples

### Docker Desktop GitHub MCP
**File:** [`docker-desktop-github-mcp.json`](docker-desktop-github-mcp.json)

Configuration for running GitHub MCP server through Docker Desktop integration.

**Features:**
- GitHub repository access
- Issue and PR management
- Code search capabilities

### Docker MCP Server
**File:** [`sample-docker-mcp.json`](sample-docker-mcp.json)

General Docker-based MCP server configuration template.

**Use Cases:**
- Running MCP servers in containers
- Isolated server environments
- Cross-platform compatibility

### NPX MCP Server
**File:** [`sample-npx-mcp.json`](sample-npx-mcp.json)

Configuration for running MCP servers via NPX (Node Package Runner).

**Use Cases:**
- JavaScript/TypeScript MCP servers
- Quick server deployment
- No installation required

## Usage

1. **Choose a sample** - Select the configuration that matches your use case
2. **Copy to your project** - Copy the JSON file to your tool's config directory
3. **Customize** - Update server URLs, credentials, and options
4. **Test** - Verify the server connection works

## Integration Guides

For detailed integration instructions, see:

- **[MCP Configuration Guide](../configuration.md)** - Comprehensive setup guide
- **[MCP Overview](../overview.md)** - Concepts and architecture
- **[OpenCode MCP Integration](../../tools/opencode/configuration.md#7-mcp-server-configuration)** - OpenCode-specific setup

## Configuration Format

All sample files follow this structure with top-level `mcp` key:

```json
{
  "mcp": {
    "server-name": {
      "type": "local",
      "command": ["docker", "run", "..."],
      "enabled": true,
      "environment": {
        "ENV_VAR": "value"
      },
      "timeout": 10000
    }
  },
  "tools": {
    "server-name": true
  }
}
```

## Environment Variables

Many MCP servers require API keys or credentials. Store these securely:

- Use environment variables for sensitive data
- Never commit credentials to version control
- Reference env vars in config: `"GITHUB_TOKEN": "${GITHUB_TOKEN}"`

## Next Steps

- Review **[MCP Overview](../overview.md)** for concepts
- Follow **[Configuration Guide](../configuration.md)** for setup
- Explore **[OpenCode Integration](../../tools/opencode/index.md)** for usage examples

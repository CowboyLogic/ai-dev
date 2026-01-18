# Model Context Protocol (MCP) Servers

This section provides working examples and configurations for integrating MCP servers into your AI development workflow.

## What is MCP?

Model Context Protocol (MCP) extends AI assistants with custom tools, data sources, and specialized functions through standardized server integrations.

**Learn more:** [Official MCP Documentation](https://modelcontextprotocol.io) | [MCP Specification](https://spec.modelcontextprotocol.io)

This guide focuses on **practical implementation examples** from this repository.

## Available Sample Configurations

Sample MCP server configurations are available in [`sample-configs/`](sample-configs/README.md):

### Docker-Based MCP Servers

Example: Running MCP servers in Docker containers for isolation and portability.

**File:** `docker-desktop-github-mcp.json`

### NPX-Based MCP Servers

Example: Running MCP servers via NPX for quick, npm-package based integrations.

**File:** `sample-npx-mcp.json`

### Standard Docker MCP

Example: Basic Docker MCP server configuration.

**File:** `sample-docker-mcp.json`

## Integration with OpenCode

MCP servers can be configured in OpenCode's `opencode.json`:

```json
{
  "mcp": {
    "server-name": {
      "type": "local",  // or "remote"
      "command": ["docker", "run", "--rm", "-i", "server-image"],
      "enabled": true,
      "environment": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  },
  "tools": {
    "server-name": true  // Enable the tool
  }
}
```

See [OpenCode Configuration](../tools/opencode/configuration.md) for detailed setup instructions.

## Common Use Cases

This repository includes examples for:

- **Security Scanning** - Snyk integration (see `sample-npx-mcp.json`)
- **Code Analysis** - Custom analysis tools
- **Deployment & Infrastructure** - CI/CD and cloud provider integrations
- **Data Access** - Database and API connections

For comprehensive MCP capabilities, see the [official MCP tools documentation](https://modelcontextprotocol.io/docs/tools).

## Environment Variables

Most MCP servers require authentication tokens or API keys. Set these as environment variables:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN = "your-token"
$env:SNYK_TOKEN = "your-token"

# Linux/Mac
export GITHUB_TOKEN="your-token"
export SNYK_TOKEN="your-token"
```

Reference them in configuration files using `${VARIABLE_NAME}` syntax.

## Next Steps

- **Quick Start:** Explore [sample configurations](sample-configs/README.md) for copy-paste examples
- **Integration:** Review [OpenCode MCP setup](../tools/opencode/configuration.md) for tool-specific configuration
- **Deep Dive:** Read the [official MCP documentation](https://modelcontextprotocol.io) for protocol details and advanced features

> [!NOTE] Expanding Content
> This section is actively being developed with more examples, tutorials, and best practices.

# Model Context Protocol (MCP) Servers

This section documents lessons learned and useful configurations when working with MCP servers in their various forms.

## What is MCP?

Model Context Protocol (MCP) is a standardized way to extend AI assistants with additional capabilities through server integrations. MCP servers can provide:

- **Tool Access** - Custom tools and APIs
- **Data Sources** - Database connections, file systems, external services
- **Specialized Functions** - Code analysis, security scanning, deployment tools

## Available Sample Configurations

Sample MCP server configurations are available in [`../reference/mcp/sample-configs/`](../reference/mcp/sample-configs/README.md):

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

### Security Scanning
- Snyk integration for vulnerability detection
- Custom security audit tools

### Code Analysis
- AST parsing and analysis
- Code quality metrics
- Complexity analysis

### Deployment & Infrastructure  
- CI/CD integrations
- Cloud provider APIs (AWS, Azure, GCP)
- Kubernetes management

### Data Access
- Database connections
- API integrations
- File system access

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

- Explore [sample configurations](../reference/mcp/sample-configs/README.md)
- Review [OpenCode MCP integration](../tools/opencode/configuration.md#7-mcp-server-configuration)
- Check the [official MCP documentation](https://modelcontextprotocol.io)

> [!NOTE] Expanding Content
> This section is actively being developed with more examples, tutorials, and best practices.
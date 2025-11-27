# MCP Server Configuration Guide

This guide covers how to configure and use Model Context Protocol (MCP) servers with various AI development tools.

## Sample Configurations

All sample configuration files are located in [`../reference/mcp/sample-configs/`](../reference/mcp/sample-configs/README.md).

## Docker-Based MCP Servers

Docker-based MCP servers run in isolated containers, providing portability and consistent environments.

### Basic Docker Configuration

**Example:** `docker-desktop-github-mcp.json`

```json
{
  "mcp": {
    "my-docker-service": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "my-mcp-server:latest"],
      "enabled": true,
      "environment": {
        "API_KEY": "${MY_API_KEY}",
        "CONFIG_PATH": "/config"
      },
      "timeout": 10000
    }
  },
  "tools": {
    "my-docker-service": true
  }
}
```

### Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `type` | Server type | `"local"` or `"remote"` |
| `command` | Command to execute | `["docker", "run", ...]` |
| `enabled` | Whether server is active | `true` / `false` |
| `environment` | Environment variables | `{"KEY": "${VALUE}"}` |
| `timeout` | Connection timeout (ms) | `10000` |

### Best Practices

✅ **Do:**
- Use `--rm` flag to clean up containers
- Use `-i` for interactive mode
- Set appropriate timeouts
- Use environment variables for secrets
- Tag your images with versions

❌ **Don't:**
- Hardcode secrets in configuration
- Use overly short timeouts
- Forget to enable the tool in `tools` section
- Run containers in detached mode for MCP

## NPX-Based MCP Servers

NPX-based MCP servers run Node.js packages directly, useful for npm-published MCP tools.

### Basic NPX Configuration

**Example:** `sample-npx-mcp.json`

```json
{
  "mcp": {
    "snyk": {
      "type": "local",
      "command": ["npx", "-y", "@snyk/mcp-server"],
      "enabled": true,
      "environment": {
        "SNYK_TOKEN": "${SNYK_TOKEN}"
      }
    }
  },
  "tools": {
    "snyk": true
  }
}
```

### Common NPX MCP Servers

| Package | Purpose | Required Env Vars |
|---------|---------|-------------------|
| `@snyk/mcp-server` | Security vulnerability scanning | `SNYK_TOKEN` |
| `@modelcontextprotocol/server-*` | Official MCP servers | Varies |

### Best Practices

✅ **Do:**
- Use `-y` flag to auto-install
- Specify package versions when needed
- Test packages individually first
- Check package trust and maintenance

❌ **Don't:**
- Install untrusted packages
- Forget required environment variables
- Use outdated or unmaintained packages

## Remote MCP Servers

Remote MCP servers connect to hosted services via HTTP/WebSocket.

### Basic Remote Configuration

```json
{
  "mcp": {
    "github": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  },
  "tools": {
    "github": true
  }
}
```

### Configuration Options

| Option | Description | Example |
|--------|-------------|---------|
| `type` | Must be "remote" | `"remote"` |
| `url` | Server endpoint | `"https://..."` |
| `headers` | HTTP headers | `{"Authorization": "..."}` |
| `timeout` | Connection timeout | `30000` |

## Environment Variables

### Setting Environment Variables

**Windows PowerShell:**
```powershell
# Temporary (current session)
$env:GITHUB_TOKEN = "ghp_your_token_here"
$env:SNYK_TOKEN = "your_snyk_token"

# Permanent (user profile)
[System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'ghp_your_token_here', 'User')
```

**Linux/Mac:**
```bash
# Temporary (current session)
export GITHUB_TOKEN="ghp_your_token_here"
export SNYK_TOKEN="your_snyk_token"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### Referencing in Configuration

Use `${VARIABLE_NAME}` syntax in configuration files:

```json
{
  "environment": {
    "API_KEY": "${MY_API_KEY}",
    "API_SECRET": "${MY_API_SECRET}"
  }
}
```

### Security Best Practices

🔒 **Security:**
- Never commit tokens to version control
- Use `.gitignore` for config files with secrets
- Rotate tokens regularly
- Use minimal permission scopes
- Consider using secret management tools (e.g., Azure Key Vault, AWS Secrets Manager)

## Troubleshooting

### MCP Server Not Responding

**Symptom:** Server times out or doesn't respond

**Solutions:**
1. Increase timeout value: `"timeout": 30000`
2. Check Docker/NPX is installed and in PATH
3. Verify environment variables are set
4. Check network connectivity for remote servers
5. Review server logs for errors

### Tool Not Available

**Symptom:** AI assistant says tool is not available

**Solutions:**
1. Verify tool is enabled in `tools` section
2. Check MCP server is `enabled: true`
3. Restart the AI tool after configuration changes
4. Validate JSON syntax

### Authentication Failures

**Symptom:** "401 Unauthorized" or similar errors

**Solutions:**
1. Verify environment variables are set correctly:
   ```powershell
   echo $env:GITHUB_TOKEN  # PowerShell
   echo $GITHUB_TOKEN       # Bash
   ```
2. Check token hasn't expired
3. Verify token has required permissions
4. Ensure proper syntax: `${VARIABLE}` not `$VARIABLE`

### Docker Container Issues

**Symptom:** Docker command fails

**Solutions:**
1. Ensure Docker Desktop is running
2. Pull the image first: `docker pull image-name`
3. Test container independently: `docker run image-name`
4. Check container logs: `docker logs container-id`
5. Verify port mappings if needed

## Integration Examples

### OpenCode Integration

Add to `opencode.json` or `.opencode.json`:

```json
{
  "mcp": {
    "github": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "enabled": true
    },
    "snyk": {
      "type": "local",
      "command": ["npx", "-y", "@snyk/mcp-server"],
      "enabled": true,
      "environment": {
        "SNYK_TOKEN": "${SNYK_TOKEN}"
      }
    }
  },
  "tools": {
    "github": true,
    "snyk": true
  }
}
```

See [OpenCode Configuration Guide](../tools/opencode/configuration.md) for more details.

### Multiple Servers

You can configure multiple MCP servers simultaneously:

```json
{
  "mcp": {
    "github": { /* ... */ },
    "snyk": { /* ... */ },
    "custom-tool": { /* ... */ }
  },
  "tools": {
    "github": true,
    "snyk": true,
    "custom-tool": true
  }
}
```

Each server runs independently and provides its own set of capabilities.

## Sample Files Reference

All sample configuration files are available at [`../reference/mcp/sample-configs/`](../reference/mcp/sample-configs/README.md):

- **`docker-desktop-github-mcp.json`** - Docker Desktop with GitHub MCP integration
- **`sample-docker-mcp.json`** - Basic Docker MCP server example
- **`sample-npx-mcp.json`** - NPX-based MCP server example

## Next Steps

- Review [sample configurations](../reference/mcp/sample-configs/README.md)
- Explore [OpenCode MCP integration](../tools/opencode/configuration.md)
- Read [MCP Overview](overview.md) for concepts and use cases
- Visit [official MCP documentation](https://modelcontextprotocol.io) for protocol details

---

**Need help?** Check the troubleshooting section above or consult the official MCP documentation.

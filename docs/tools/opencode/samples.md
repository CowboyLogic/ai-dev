# Sample MCP Server Configurations

This page provides detailed examples of Model Context Protocol (MCP) server configurations for OpenCode CLI.

## What are MCP Servers?

Model Context Protocol (MCP) servers extend OpenCode with additional capabilities by providing tools, resources, and context that AI models can use during development.

**Common Use Cases:**
- Security scanning (e.g., Snyk)
- Code analysis tools
- API integrations (e.g., GitHub, Jira)
- Custom development tools
- Database access
- Cloud service integrations

## Sample Configurations

### Docker-Based MCP Server

Located at: `docs/mcp/sample-configs/sample-docker-mcp.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  
  // Sample configuration for a local container-based MCP server using Docker
  "mcp": {
    "docker-mcp-sample": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "my-mcp-server:latest"],
      "enabled": true,
      "environment": {
        "API_KEY": "${MY_API_KEY}",
        "DEBUG": "true"
      },
      "timeout": 10000
    }
  },

  // Minimal other config for completeness
  "model": "anthropic/claude-3-5-sonnet-20241022",
  "tools": {
    "docker-mcp-sample": true
  }
}
```

**Key Points:**

**Server Configuration:**
- **`type: "local"`** - Runs as a local process
- **`command`** - Array format: `["docker", "run", "--rm", "-i", "image:tag"]`
- **`--rm`** - Automatically remove container when stopped
- **`-i`** - Interactive mode for communication
- **`enabled: true`** - Server is active

**Environment Variables:**
- Use `${VARIABLE_NAME}` to reference shell environment variables
- Set in your shell before running OpenCode
- Common pattern for API keys and secrets

**Timeout:**
- Value in milliseconds (10000 = 10 seconds)
- Adjust based on server startup time
- Docker servers may need longer timeouts

**Tool Enablement:**
- Must add `"docker-mcp-sample": true` to `tools` section
- This activates the MCP server's capabilities
- Without this, the server won't be available to the AI

**Setting Up:**

1. **Build your Docker image:**
   ```bash
   docker build -t my-mcp-server:latest .
   ```

2. **Set environment variables:**
   ```powershell
   # PowerShell
   $env:MY_API_KEY = "your-api-key-here"
   ```

3. **Test the server manually:**
   ```bash
   docker run --rm -i my-mcp-server:latest
   ```

4. **Add to OpenCode config**

5. **Enable the tool in `tools` section**

**Common Docker MCP Use Cases:**
- Custom code analysis tools
- Database query tools
- API testing frameworks
- Security scanning services
- Build system integrations

### NPX-Based MCP Server (Snyk)

Located at: `docs/mcp/sample-configs/sample-npx-mcp.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  
  // Sample configuration for a local MCP server using npx, similar to Snyk MCP server
  "mcp": {
    "snyk": {
      "type": "local",
      "command": ["npx", "-y", "@snyk/mcp-server"],
      "enabled": true,
      "environment": {
        "SNYK_TOKEN": "${SNYK_TOKEN}"
      },
      "timeout": 15000
    }
  },

  // Minimal other config for completeness
  "model": "anthropic/claude-3-5-sonnet-20241022",
  "tools": {
    "snyk": true
  }
}
```

**Key Points:**

**NPX Configuration:**
- **`npx -y`** - Automatically install package if not present
- **`@snyk/mcp-server`** - NPM package name
- Works with any npm package that provides MCP server

**Environment Variables:**
- Snyk requires `SNYK_TOKEN` for authentication
- Obtain from [Snyk dashboard](https://app.snyk.io)
- Set before running OpenCode

**Timeout:**
- 15000ms (15 seconds) allows time for npm installation
- First run may take longer as package downloads
- Subsequent runs are faster

**Setting Up Snyk MCP:**

1. **Create Snyk account:**
   - Visit [snyk.io](https://snyk.io)
   - Create free or paid account

2. **Get API token:**
   - Go to Account Settings
   - Copy API token

3. **Set environment variable:**
   ```powershell
   # PowerShell
   $env:SNYK_TOKEN = "your-snyk-token-here"
   ```
   
   ```bash
   # Linux/Mac
   export SNYK_TOKEN="your-snyk-token-here"
   ```

4. **Add configuration to `opencode.json`**

5. **Enable tool:**
   ```json
   {
     "tools": {
       "snyk": true
     }
   }
   ```

6. **Use in commands:**
   ```bash
   opencode "scan for security vulnerabilities"
   ```

**What Snyk MCP Provides:**
- Vulnerability scanning
- License compliance checking
- Dependency analysis
- Security recommendations
- Fix suggestions

**Other NPX MCP Servers:**

You can use this pattern for any npm-based MCP server:

```json
{
  "my-npm-tool": {
    "type": "local",
    "command": ["npx", "-y", "@company/mcp-tool"],
    "enabled": true,
    "environment": {
      "TOOL_API_KEY": "${TOOL_API_KEY}"
    },
    "timeout": 15000
  }
}
```

### Docker Desktop MCP Toolbox GitHub Server

Located at: `docs/mcp/sample-configs/docker-desktop-github-mcp.json`

For users with Docker Desktop's MCP Toolbox installed, you can use the GitHub MCP server:

```json
{
  "$schema": "https://opencode.ai/config.json",
  
  // Configuration for Docker Desktop MCP Toolbox GitHub MCP server
  // This assumes you have the Docker Desktop MCP Toolbox installed
  // Replace 'docker/desktop-mcp-toolbox-github:latest' with the actual image name if different
  "mcp": {
    "docker-desktop-github": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "docker/desktop-mcp-toolbox-github:latest"],
      "enabled": true,
      "environment": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      },
      "timeout": 30000
    }
  },

  // Enable the GitHub MCP tools
  "tools": {
    "docker-desktop-github": true
  }
}
```

**Key Points:**

**Docker Desktop Integration:**
- Requires Docker Desktop with MCP Toolbox extension
- Provides local GitHub operations without remote API calls
- May offer additional Docker-specific GitHub workflows

**Environment Variables:**
- `GITHUB_TOKEN` - Required for GitHub API access
- Obtain from GitHub Settings > Developer settings > Personal access tokens

**Timeout:**
- 30000ms (30 seconds) to allow for Docker container startup
- May need adjustment based on your system's Docker performance

**Setup Requirements:**

1. **Install Docker Desktop MCP Toolbox:**
   - Ensure Docker Desktop is installed and running
   - Install the MCP Toolbox extension from Docker Desktop

2. **Verify the image:**
   ```bash
   docker images | grep mcp-toolbox
   ```

3. **Set GitHub token:**
   ```powershell
   # PowerShell
   $env:GITHUB_TOKEN = "your-github-token-here"
   ```

4. **Test the container:**
   ```bash
   docker run --rm -i docker/desktop-mcp-toolbox-github:latest --help
   ```

5. **Add to OpenCode configuration**

**Features Provided:**
- Local GitHub repository operations
- Issue and pull request management
- Code search and analysis
- Integration with Docker workflows

## Additional MCP Server Examples

### GitHub MCP Server (Remote)

Already included in main `opencode.json`:

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
  }
}
```

**Features:**
- Access GitHub APIs
- Repository operations
- Issue and PR management
- Code search across GitHub

**Setup:**
1. Create GitHub Personal Access Token
2. Set `GITHUB_TOKEN` environment variable
3. Enable in tools section

### Custom HTTP MCP Server

For your own remote MCP server:

```json
{
  "mcp": {
    "my-api": {
      "type": "remote",
      "url": "https://api.example.com/mcp/",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer ${MY_API_TOKEN}",
        "X-Custom-Header": "value"
      },
      "timeout": 5000
    }
  },
  "tools": {
    "my-api": true
  }
}
```

**Use Cases:**
- Internal company APIs
- Custom development tools
- Third-party integrations
- Microservice access

### Database MCP Server

Example for database access:

```json
{
  "mcp": {
    "postgres": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", 
                  "-e", "POSTGRES_PASSWORD=${DB_PASSWORD}",
                  "postgres-mcp:latest"],
      "enabled": true,
      "environment": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "myapp",
        "DB_USER": "admin",
        "DB_PASSWORD": "${DB_PASSWORD}"
      },
      "timeout": 20000
    }
  },
  "tools": {
    "postgres": true
  }
}
```

**Capabilities:**
- Query database
- Generate migrations
- Analyze schema
- Optimize queries

**Security Warning:**
- Use read-only credentials when possible
- Restrict to development databases
- Never expose production credentials

## Configuration Patterns

### Multi-Server Setup

Combine multiple MCP servers:

```json
{
  "mcp": {
    "github": { /* remote GitHub MCP */ },
    "snyk": { /* local security scanning */ },
    "postgres": { /* local database access */ },
    "custom-api": { /* remote custom API */ }
  },
  "tools": {
    "github": true,
    "snyk": true,
    "postgres": true,
    "custom-api": true
  }
}
```

**Benefits:**
- Comprehensive toolset
- Different tools for different tasks
- Flexible workflow

**Considerations:**
- More servers = more API calls = higher cost
- Enable only what you need
- Consider disabling servers per project

### Conditional Server Activation

Enable servers per project with `.opencode.json`:

```json
{
  "mcp": {
    "snyk": {
      "enabled": true
    },
    "postgres": {
      "enabled": false
    }
  }
}
```

### Environment-Specific Configuration

**Development:**
```json
{
  "mcp": {
    "dev-tools": {
      "environment": {
        "ENV": "development",
        "DEBUG": "true"
      }
    }
  }
}
```

**Production:**
```json
{
  "mcp": {
    "prod-tools": {
      "environment": {
        "ENV": "production",
        "DEBUG": "false"
      }
    }
  }
}
```

## Troubleshooting MCP Servers

### Server Not Responding

**Check 1: Environment Variables**
```powershell
# PowerShell - verify variable is set
echo $env:SNYK_TOKEN
```

```bash
# Linux/Mac
echo $SNYK_TOKEN
```

**Check 2: Command Availability**
```bash
# Docker
docker --version

# NPX
npx --version
```

**Check 3: Tool Enablement**
Verify in `tools` section:
```json
{
  "tools": {
    "your-server-name": true
  }
}
```

**Check 4: Timeout**
Increase if server is slow to start:
```json
{
  "timeout": 30000  // 30 seconds
}
```

### Authentication Failures

1. **Verify token format** - Check for extra spaces or quotes
2. **Check token permissions** - Ensure token has required scopes
3. **Test token manually** - Use curl or Postman
4. **Regenerate token** - Token may have expired

### Docker-Specific Issues

**Container not starting:**
```bash
# Test image manually
docker run --rm -i your-image:latest

# Check logs
docker logs container-id
```

**Port conflicts:**
```bash
# Check what's using port
netstat -ano | findstr :8080  # Windows
lsof -i :8080  # Linux/Mac
```

### NPX-Specific Issues

**Package not installing:**
```bash
# Install manually first
npm install -g @snyk/mcp-server

# Then use without -y flag
```

**Version conflicts:**
```bash
# Specify version
npx @snyk/mcp-server@1.2.3
```

## Best Practices

### Security

✅ **Do:**
- Use environment variables for all secrets
- Restrict permissions to minimum necessary
- Use read-only access when possible
- Rotate tokens regularly

❌ **Don't:**
- Hardcode API keys in config
- Commit secrets to version control
- Use production credentials in development
- Share tokens across projects unnecessarily

### Performance

✅ **Do:**
- Set appropriate timeouts
- Enable only needed servers
- Use local servers when possible
- Cache results when available

❌ **Don't:**
- Set timeouts too low
- Enable all servers by default
- Use remote servers for local-only operations
- Make unnecessary API calls

### Maintenance

✅ **Do:**
- Document custom MCP servers
- Version control configuration
- Test servers after updates
- Monitor API usage and costs

❌ **Don't:**
- Leave unused servers enabled
- Ignore deprecation warnings
- Skip testing after changes
- Forget to update documentation

## Creating Custom MCP Servers

### Basic Structure

MCP servers communicate via stdin/stdout using JSON-RPC.

**Minimum Implementation:**
1. Accept JSON-RPC requests on stdin
2. Return JSON-RPC responses on stdout
3. Implement required MCP protocol methods
4. Handle tools/resources/prompts as needed

**Example (Python):**
```python
import sys
import json

def handle_request(request):
    # Process MCP request
    # Return MCP response
    pass

for line in sys.stdin:
    request = json.loads(line)
    response = handle_request(request)
    print(json.dumps(response))
    sys.stdout.flush()
```

### Resources

- **[MCP Specification](https://modelcontextprotocol.io)** - Protocol details
- **[MCP SDK](https://github.com/modelcontextprotocol/sdk)** - Official SDKs
- **Example Servers** - Reference implementations

## Modular Agent Configuration

The `agent-subagent-config/` directory provides an alternative to traditional agent configuration, where specialized agents are defined in individual markdown files.

### Overview

Instead of defining all agents in `opencode.json`, each agent is a separate markdown file with YAML frontmatter:

**Traditional Approach:**
```json
{
  "agent": {
    "security": {
      "description": "Security audits",
      "mode": "subagent",
      "model": "github-copilot/claude-sonnet-4",
      "temperature": 0.1
    },
    "database": { /* ... */ },
    "devops": { /* ... */ }
    // Many more agents...
  }
}
```

**Modular Approach:**

`agent/security.md`:
```markdown
---
description: Security audits, vulnerability scanning, and best practices
mode: subagent
model: github-copilot/claude-sonnet-4
temperature: 0.1
tools:
  bash: true
---

# Agent Purpose
The Security agent focuses on identifying vulnerabilities...
```

### Available Agents

The modular configuration includes **13 specialized agents**:

- **`@api`** - REST/GraphQL API design, OpenAPI specs
- **`@architect`** - System architecture and design decisions
- **`@cloud`** - AWS/Azure/GCP, Infrastructure as Code
- **`@data`** - Data analysis, ETL pipelines
- **`@database`** - Schema design, query optimization
- **`@devops`** - CI/CD, Docker, Kubernetes
- **`@documentation`** - Technical docs, API documentation
- **`@performance`** - Performance profiling and optimization
- **`@research`** - Technical discovery and analysis
- **`@reviewer`** - Code review and best practices
- **`@security`** - Security audits and vulnerability scanning
- **`@testing`** - Unit tests, integration tests
- **`@uxui`** - UI/UX design and accessibility

### Usage Examples

```bash
# API design
opencode @api "Design REST API for user management"

# Security audit
opencode @security "Review authentication system for vulnerabilities"

# Database optimization
opencode @database "Optimize query performance in user_stats"

# Cloud infrastructure
opencode @cloud "Create Terraform module for ECS deployment"

# DevOps automation
opencode @devops "Set up GitHub Actions for CI/CD"
```

### Benefits

- **Modularity** - Add agents by adding markdown files
- **Maintainability** - Each agent is self-contained
- **Documentation** - Agent purpose documented inline
- **Reusability** - Share individual agents across projects
- **Scalability** - Manage complex multi-agent workflows

### Getting Started

1. Copy `docs/tools/opencode/agent-subagent-config/` to your project
2. Review available agents in `agent/` directory
3. Add/remove agent files as needed
4. Use `@agentname` to invoke specific agents

See the [Configuration Guide](configuration.md) for comprehensive documentation on the modular agent pattern.

## Next Steps

- **[Configuration Guide](configuration.md)** - Detailed config documentation
- **[OpenCode Overview](index.md)** - Feature overview
- **[Getting Started](../../index.md)** - General guide

---

**Ready to add MCP servers?** Start with the Snyk example, then explore Docker-based servers for custom tools.

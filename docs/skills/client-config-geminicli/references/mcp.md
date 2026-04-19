# MCP Servers Reference

MCP servers are configured in `settings.json` under `mcpServers`.

## Transports

### stdio (local process)
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      },
      "cwd": "/optional/working/directory"
    }
  }
}
```

### SSE (HTTP Server-Sent Events)
```json
{
  "mcpServers": {
    "remote-server": {
      "url": "https://my-server.example.com/sse",
      "headers": {
        "Authorization": "Bearer ${MY_TOKEN}"
      }
    }
  }
}
```

### HTTP streaming
```json
{
  "mcpServers": {
    "http-server": {
      "httpUrl": "https://my-server.example.com/mcp",
      "headers": {
        "X-API-Key": "${API_KEY}"
      }
    }
  }
}
```

## Field reference

| Field | Transport | Description |
|-------|-----------|-------------|
| `command` | stdio | Executable to run |
| `args` | stdio | Arguments array |
| `env` | stdio | Environment variables (supports `${VAR}` interpolation) |
| `cwd` | stdio | Working directory for the process |
| `url` | SSE | SSE endpoint URL |
| `httpUrl` | HTTP | HTTP streaming endpoint URL |
| `headers` | SSE/HTTP | HTTP headers (auth tokens, etc.) |
| `trust` | all | Trust level: `"full"` bypasses tool approval prompts |
| `tools` | all | Tool inclusion/exclusion (see below) |

## Tool filtering

```json
{
  "mcpServers": {
    "my-server": {
      "command": "...",
      "tools": {
        "include": ["tool_a", "tool_b"],
        "exclude": ["dangerous_tool"]
      }
    }
  }
}
```

## CLI commands

| Command | Description |
|---------|-------------|
| `/mcp` | List all configured MCP servers and status |
| `/mcp reload` | Reload server list and reconnect |

## Docker transport example

```json
{
  "mcpServers": {
    "postgres": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "DATABASE_URL",
        "mcp/postgres"
      ],
      "env": {
        "DATABASE_URL": "${DATABASE_URL}"
      }
    }
  }
}
```

## Common servers

| Server | Command |
|--------|---------|
| GitHub | `npx -y @modelcontextprotocol/server-github` |
| Filesystem | `npx -y @modelcontextprotocol/server-filesystem /path` |
| Postgres | `npx -y @modelcontextprotocol/server-postgres` |
| Slack | `npx -y @modelcontextprotocol/server-slack` |
| Google Drive | `npx -y @modelcontextprotocol/server-gdrive` |

# MCP Servers Reference

## Structure in opencode.json

```json
{
  "mcp": {
    "server-name": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "environment": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_TOKEN}"
      },
      "enabled": true,
      "timeout": 5000
    }
  }
}
```

---

## Transport types

### `local` (stdio — most common)

Starts a local process, communicates over stdin/stdout.

```json
{
  "type": "local",
  "command": ["node", "path/to/server.js"],
  "environment": { "API_KEY": "{env:MY_API_KEY}" },
  "enabled": true,
  "timeout": 5000
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"local"` |
| `command` | Yes | Array — executable + arguments |
| `environment` | No | Environment variables object |
| `enabled` | No | `true` (default) — set `false` to disable without removing |
| `timeout` | No | Milliseconds before timeout (default: 5000) |

### `remote` (HTTP / SSE)

```json
{
  "type": "remote",
  "url": "https://mcp.example.com/mcp",
  "headers": {
    "Authorization": "Bearer {env:API_TOKEN}"
  },
  "oauth": false,
  "enabled": true,
  "timeout": 5000
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"remote"` |
| `url` | Yes | Remote server endpoint |
| `headers` | No | HTTP headers object |
| `oauth` | No | OAuth config object, `false` to disable, omit for auto |
| `enabled` | No | `true` (default) |
| `timeout` | No | Milliseconds before timeout (default: 5000) |

---

## OAuth configuration (remote servers)

**Automatic** (omit `oauth` field — opencode handles it):
```json
{ "type": "remote", "url": "https://mcp.example.com/mcp" }
```

**Pre-registered credentials**:
```json
{
  "oauth": {
    "clientId": "{env:MCP_CLIENT_ID}",
    "clientSecret": "{env:MCP_CLIENT_SECRET}",
    "scope": "tools:read tools:execute"
  }
}
```

**Disabled** (API-key auth instead):
```json
{
  "oauth": false,
  "headers": { "Authorization": "Bearer {env:API_KEY}" }
}
```

---

## Common MCP servers

### GitHub
```json
"github": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
  "environment": { "GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_TOKEN}" }
}
```

### Filesystem
```json
"filesystem": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
}
```

### Memory
```json
"memory": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-memory"]
}
```

### PostgreSQL
```json
"postgres": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"]
}
```

### Brave Search
```json
"brave-search": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-brave-search"],
  "environment": { "BRAVE_API_KEY": "{env:BRAVE_API_KEY}" }
}
```

---

## CLI commands

```bash
opencode mcp list                   # show all servers and auth status
opencode mcp auth <server-name>     # authenticate with OAuth
opencode mcp logout <server-name>   # remove stored credentials
opencode mcp debug <server-name>    # troubleshoot connection issues
```

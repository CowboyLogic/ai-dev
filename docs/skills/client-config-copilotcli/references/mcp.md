# MCP Servers Reference

## Config file location

```
~/.copilot/mcp-config.json
```

(Or `$COPILOT_HOME/mcp-config.json`)

## Structure

```json
{
  "mcpServers": {
    "server-name": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      },
      "tools": ["*"]
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
  "command": "node",
  "args": ["path/to/server.js"],
  "env": { "API_KEY": "..." },
  "tools": ["*"]
}
```

### `http` (Streamable HTTP)

```json
{
  "type": "http",
  "url": "https://mcp.example.com/mcp",
  "headers": { "Authorization": "Bearer YOUR_TOKEN" },
  "tools": ["*"]
}
```

### `sse` (Server-Sent Events — legacy, deprecated but supported)

```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse",
  "headers": { "Authorization": "Bearer YOUR_TOKEN" },
  "tools": ["*"]
}
```

---

## Fields reference

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `local` \| `http` \| `sse` |
| `tools` | Yes | Array of allowed tool names, or `["*"]` for all |
| `command` | local only | Executable to run |
| `args` | local only | Arguments array |
| `env` | local only | Environment variables object |
| `url` | http/sse only | Remote server URL |
| `headers` | http/sse only | HTTP headers (for auth etc.) |

---

## Common MCP servers

### GitHub
```json
"github": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..." },
  "tools": ["*"]
}
```

### Filesystem
```json
"filesystem": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
  "tools": ["*"]
}
```

### Memory
```json
"memory": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"],
  "tools": ["*"]
}
```

### PostgreSQL
```json
"postgres": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"],
  "tools": ["*"]
}
```

---

## Adding servers

### Via interactive CLI (recommended)
```
/mcp add
```
Launches a guided form — enter server name, type, command/URL, and any env vars.

### Via direct editing
Edit `~/.copilot/mcp-config.json` directly. Useful for sharing configs or adding multiple servers at once.

---

## Management commands (inside sessions)

| Command | Purpose |
|---------|---------|
| `/mcp show` | List all configured servers |
| `/mcp show SERVER-NAME` | Show status and tools for one server |
| `/mcp edit SERVER-NAME` | Modify server config |
| `/mcp delete SERVER-NAME` | Remove server |
| `/mcp disable SERVER-NAME` | Disable without removing |
| `/mcp enable SERVER-NAME` | Re-enable disabled server |

---

## Tool permissions for MCP

In CLI flags, reference MCP tools with:

```bash
--allow-tool='SERVER_NAME'              # allow all tools from server
--allow-tool='SERVER_NAME(tool_name)'   # allow specific tool
--deny-tool='SERVER_NAME(tool_name)'    # block specific tool
```

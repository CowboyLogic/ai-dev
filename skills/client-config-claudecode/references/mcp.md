# MCP Servers Reference

## File locations

| Scope | File |
|-------|------|
| User (all projects) | `~/.claude.json` → `mcpServers` key |
| Project (shared) | `.mcp.json` in project root |
| Managed | `managed-mcp.json` in system dir |

Note: MCP servers are NOT configured in `settings.json` directly — they live in `~/.claude.json` (user scope) or `.mcp.json` (project scope).

---

## ~/.claude.json mcpServers structure

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

---

## Transport types

### stdio (most common — local process)
```json
{
  "type": "stdio",
  "command": "node",
  "args": ["path/to/server.js"],
  "env": { "API_KEY": "..." }
}
```

### SSE (Server-Sent Events — remote HTTP)
```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse",
  "headers": { "Authorization": "Bearer ${MY_TOKEN}" }
}
```

### HTTP (streamable HTTP)
```json
{
  "type": "http",
  "url": "https://mcp.example.com/mcp",
  "headers": { "Authorization": "Bearer ${MY_TOKEN}" }
}
```

---

## Common MCP servers

### Filesystem
```json
"filesystem": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
}
```

### GitHub
```json
"github": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..." }
}
```

### Memory
```json
"memory": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"]
}
```

### PostgreSQL
```json
"postgres": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"]
}
```

### Brave Search
```json
"brave-search": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-brave-search"],
  "env": { "BRAVE_API_KEY": "..." }
}
```

---

## MCP settings in settings.json

These control MCP behavior but servers themselves are in `~/.claude.json`:

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["memory", "github"],
  "disabledMcpjsonServers": ["filesystem"],
  "allowedMcpServers": [{ "serverName": "github" }],
  "deniedMcpServers": [{ "serverName": "filesystem" }],
  "allowManagedMcpServersOnly": true
}
```

| Setting | Effect |
|---------|--------|
| `enableAllProjectMcpServers` | Auto-approve all project `.mcp.json` servers |
| `enabledMcpjsonServers` | Approve specific servers from `.mcp.json` |
| `disabledMcpjsonServers` | Block specific servers from `.mcp.json` |
| `allowedMcpServers` | (managed) Allowlist all scopes |
| `deniedMcpServers` | (managed) Block all scopes |
| `allowManagedMcpServersOnly` | (managed) Only managed servers allowed |

---

## MCP permission rules (in settings.json permissions)

```json
{
  "permissions": {
    "allow": ["mcp__github__*"],
    "deny": ["mcp__filesystem__write*"],
    "ask": ["mcp__puppeteer__*"]
  }
}
```

Pattern: `mcp__<server-name>__<tool-name>`

---

## Add a new MCP server

To add a server at user scope, edit `~/.claude.json` (not settings.json):

```bash
# View current MCP config
cat ~/.claude.json | python3 -m json.tool
```

Then add your server to the `mcpServers` object. Claude Code will pick it up on next session start.

## Verify MCP servers are loaded

Inside Claude Code, type `/mcp` to see all configured servers and their status.

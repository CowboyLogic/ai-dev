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
`"streamable-http"` is accepted as an alias for `"http"` (matches the MCP spec name; configs copied from server docs work as-is). A JSON entry with a `url` but no `type` is an error — Claude Code otherwise reads it as stdio and skips the server.

### WebSocket (persistent bidirectional — servers that push events unprompted)
```json
{
  "type": "ws",
  "url": "wss://mcp.example.com/socket",
  "headers": { "Authorization": "Bearer ${MY_TOKEN}" }
}
```
Only configurable via `.mcp.json` or `claude mcp add-json` (no `--transport ws` flag). Accepts the same `url`, `headers`, `headersHelper`, `timeout`, and `alwaysLoad` fields as `http`. Header-only auth (no OAuth support).

**Other per-server fields** (any transport): `headersHelper` (script to generate dynamic auth headers), `alwaysLoad` (skip lazy tool-search deferral for this server), `oauth: {clientId, callbackPort}` (pre-configured OAuth credentials, via `claude mcp add-json ... --client-secret`).

Stdio servers receive `CLAUDE_PROJECT_DIR` (project root) in their spawned environment — same value hooks get. Reference it in `command`/`args` with `${CLAUDE_PROJECT_DIR:-.}` (needs a default outside plugin-provided configs).

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
  "allowManagedMcpServersOnly": true,
  "disableClaudeAiConnectors": true,
  "allowAllClaudeAiMcps": true
}
```

| Setting | Effect |
|---------|--------|
| `enableAllProjectMcpServers` | Auto-approve all project `.mcp.json` servers |
| `enabledMcpjsonServers` | Approve specific servers from `.mcp.json` |
| `disabledMcpjsonServers` | Block specific servers from `.mcp.json` |
| `allowedMcpServers` | (managed) Allowlist all scopes |
| `deniedMcpServers` | (managed) Block all scopes; block a claude.ai connector by `serverName`/`serverUrl` |
| `allowManagedMcpServersOnly` | (managed) Only managed servers allowed |
| `disableClaudeAiConnectors` | Disable claude.ai connectors entirely. Any-source-true: a `true` in any scope wins over a `false` elsewhere. `--mcp-config` servers unaffected |
| `allowAllClaudeAiMcps` | (managed) Load claude.ai connectors alongside a deployed `managed-mcp.json`, which otherwise suppresses them |

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

Pattern: `mcp__<server-name>__<tool-name>`. Plugin-bundled servers use `mcp__plugin_<plugin-name>_<server-name>__<tool>`.

**Tools that force a prompt regardless of allow rules / permission mode:**
- Server marks a tool `_meta["anthropic/requiresUserInteraction"]: true` — always prompts (even `acceptEdits`/`auto`/`bypassPermissions`); denied outright in `dontAsk`.
- Org sets a claude.ai connector tool to `ask` (via admin console) — same forced-prompt behavior. Org can also set a tool to `blocked`, which filters it out before Claude ever sees it.

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

# V1 MCP Servers Reference

> [!NOTE]
> This file covers the **V1** shape (servers directly under `mcp`, `enabled`, numeric `timeout`, camelCase OAuth
> fields). Native V2 nests servers under `mcp.servers`, uses `disabled`, a `{startup, catalog, execution}` timeout
> object, and snake_case OAuth fields. See [v2/mcp.md](v2/mcp.md).

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
| `cwd` | No | Working directory for the server process (relative paths resolve from the workspace) |
| `environment` | No | Environment variables object |
| `enabled` | No | `true` (default) — set `false` to disable without removing |
| `timeout` | No | Milliseconds for fetching tools from the server (default: 5000) |

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

| OAuth field | Description |
|-------------|-------------|
| `clientId` | Client ID; omit to attempt dynamic client registration (RFC 7591) |
| `clientSecret` | Client secret, if required |
| `scope` | Scopes to request |
| `callbackPort` | Local callback port (default `19876`); ignored if `redirectUri` is set (schema field) |
| `redirectUri` | Redirect URI (default `http://127.0.0.1:19876/mcp/oauth/callback`) (schema field) |

Tokens from a successful OAuth flow are stored in `~/.local/share/opencode/mcp-auth.json`.

---

## Enabling / disabling MCP tools

MCP tools are registered as `<server-name>_<tool-name>`. The docs manage them through the (deprecated but still
honored) `tools` map, glob patterns supported. The V1 schema also accepts arbitrary `permission` keys, so
`"permission": { "my-mcp_*": "deny" }` is the likely non-deprecated equivalent, but the V1 docs do not show it —
verify before relying on it.

```json
{
  "mcp": {
    "my-mcp-foo": { "type": "local", "command": ["bun", "x", "my-mcp-command-foo"] }
  },
  "tools": { "my-mcp*": false }
}
```

Disable every tool from a server with a glob: `"tools": { "my-mcp*": false }`.

**Per-agent**: disable globally, then re-enable for one agent:

```json
{
  "tools": { "my-mcp*": false },
  "agent": { "my-agent": { "tools": { "my-mcp*": true } } }
}
```

Glob syntax: `*` matches zero-or-more chars, `?` matches exactly one, all other chars are literal.

A global default for MCP request timeouts can be set with `experimental.mcp_timeout` (ms).

Organizations can ship MCP servers disabled via remote `.well-known/opencode` config; enable one locally by
redeclaring it with `"enabled": true`.

---

## Documented example servers

### Sentry (remote, OAuth)

```json
"sentry": {
  "type": "remote",
  "url": "https://mcp.sentry.dev/mcp",
  "oauth": {}
}
```

Then `opencode mcp auth sentry` to complete the OAuth flow.

### Context7 (remote, optional API key)

```json
"context7": {
  "type": "remote",
  "url": "https://mcp.context7.com/mcp",
  "headers": { "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}" }
}
```

`headers` is optional — omit for the free tier, add for higher rate limits.

### Grep by Vercel (remote — search code on GitHub)

```json
"gh_grep": {
  "type": "remote",
  "url": "https://mcp.grep.app"
}
```

---

## CLI commands

```bash
opencode mcp list                   # show all servers and auth status
opencode mcp auth <server-name>     # authenticate with OAuth
opencode mcp auth list              # view auth status for all OAuth-capable servers
opencode mcp logout <server-name>   # remove stored credentials
opencode mcp debug <server-name>    # troubleshoot connection issues
```

# MCP Servers Reference

MCP servers are configured in `settings.json` under `mcpServers`. At least one of `command`, `url`, or `httpUrl` is required per server; if multiple are given, precedence is `httpUrl` > `url` > `command`.

Discovered tools are prefixed `mcp_<serverAlias>_<toolName>` to avoid name collisions. Avoid underscores in server aliases (use `my-server`, not `my_server`) — the policy engine parses FQNs on the first underscore after `mcp_`, so an underscore in the alias breaks security-policy matching.

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
      "cwd": "/optional/working/directory",
      "timeout": 15000
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
| `env` | stdio | Environment variables. Supports `$VAR`, `${VAR}` (all platforms), and `%VAR%` (Windows only) |
| `cwd` | stdio | Working directory for the process |
| `url` | SSE | SSE endpoint URL |
| `httpUrl` | HTTP | HTTP streaming endpoint URL |
| `headers` | SSE/HTTP | HTTP headers (auth tokens, etc.) |
| `timeout` | all | Request timeout in ms (default: 600000 = 10 min) |
| `trust` | all | `true` bypasses all tool-call confirmations for this server (default `false`) |
| `description` | all | Shown for display purposes |
| `includeTools` | all | Allowlist — only these tool names are exposed |
| `excludeTools` | all | Blocklist — takes precedence over `includeTools` if a tool is in both |
| `targetAudience` | OAuth (service account) | OAuth Client ID allowlisted on the IAP-protected app |
| `targetServiceAccount` | OAuth (service account) | Email of the GCP service account to impersonate |
| `authProviderType` | OAuth | `dynamic_discovery` (default), `google_credentials`, or `service_account_impersonation` |

## Global MCP settings (`mcp`)

A separate top-level `mcp` object controls discovery/execution rules across **all** servers (distinct from the per-server `mcpServers` object above):

```json
{
  "mcp": {
    "serverCommand": "global-mcp-launcher",
    "allowed": ["my-trusted-server"],
    "excluded": ["experimental-server"]
  }
}
```

| Field | Description |
|-------|-------------|
| `mcp.serverCommand` | Global command to start an MCP server |
| `mcp.allowed` | If set, only servers in this list (matching `mcpServers` keys) connect |
| `mcp.excluded` | Servers in this list never connect |

## Tool filtering

```json
{
  "mcpServers": {
    "my-server": {
      "command": "...",
      "includeTools": ["tool_a", "tool_b"],
      "excludeTools": ["dangerous_tool"]
    }
  }
}
```

## Environment variable security

The CLI sanitizes the environment passed to MCP server processes:

- **Auto-redacted** from the inherited host environment: core project keys (`GEMINI_API_KEY`, `GOOGLE_API_KEY`, …) and anything matching `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*KEY*`, `*AUTH*`, `*CREDENTIAL*`, plus certificate/private-key patterns.
- **Explicit overrides**: a variable listed in a server's `env` block is trusted and exempt from redaction — prefer `"MY_KEY": "$MY_KEY"` expansion over hardcoding secrets.

## OAuth for remote servers

SSE/HTTP servers can require OAuth 2.0. Omit OAuth config to let the CLI auto-discover it (detects 401s, discovers endpoints, performs dynamic client registration, handles the browser flow). Tokens are stored in `~/.gemini/mcp-oauth-tokens.json`, auto-refreshed, and validated per connection.

```json
{
  "mcpServers": {
    "oauthServer": {
      "url": "https://api.example.com/sse",
      "oauth": {
        "enabled": true,
        "clientId": "...",
        "clientSecret": "...",
        "scopes": ["read", "write"]
      }
    }
  }
}
```

OAuth config fields: `enabled`, `clientId`, `clientSecret`, `authorizationUrl`/`tokenUrl` (auto-discovered if omitted), `scopes`, `redirectUri` (default: random `localhost` port), `tokenParamName`, `audiences`.

Requires local browser access and a receivable redirect — doesn't work headless, over SSH without X11 forwarding, or in browser-less containers.

**Google Cloud auth shortcuts** (via `authProviderType`):
- `google_credentials` — uses Application Default Credentials; requires `oauth.scopes`.
- `service_account_impersonation` — impersonates a service account for IAP-protected (e.g. Cloud Run) services; requires `targetAudience` + `targetServiceAccount`.

Manage OAuth: `/mcp auth` (list servers needing auth), `/mcp auth <serverName>` (authenticate/re-authenticate).

## Resources

Some MCP servers expose contextual resources in addition to tools. Reference them like local files with `@server://resource/path`; the CLI calls `resources/read` and injects the content. `/mcp` shows a Resources section per connected server.

## CLI commands

| Command | Description |
|---------|-------------|
| `/mcp` | List all configured MCP servers, tools, resources, and status |
| `/mcp reload` | Reload server list and reconnect |
| `/mcp auth [serverName]` | Manage OAuth authentication |

## Example configurations

**Docker transport:**
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

**HTTP with custom headers:**
```json
{
  "mcpServers": {
    "httpServerWithAuth": {
      "httpUrl": "http://localhost:3000/mcp",
      "headers": { "Authorization": "Bearer ${API_TOKEN}" },
      "timeout": 5000
    }
  }
}
```

## Common servers

| Server | Command |
|--------|---------|
| GitHub | `npx -y @github/github-mcp-server` |
| Filesystem | `npx -y @modelcontextprotocol/server-filesystem /path` |
| Postgres | `npx -y @modelcontextprotocol/server-postgres` |
| Slack | `npx -y @modelcontextprotocol/server-slack` |
| Google Drive | `npx -y @modelcontextprotocol/server-gdrive` |

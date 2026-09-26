# V2 MCP Servers Reference

Source: <https://opencode.ai/v2/docs/mcp-servers/>.

## Structure

Servers live under `mcp.servers` — V2 does **not** place server names directly under `mcp`.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "timeout": { "startup": 45000, "catalog": 30000, "execution": 600000 },
    "servers": {
      "my-server": {
        "type": "local",
        "command": ["npx", "-y", "example-mcp-server"],
      },
    },
  },
}
```

Servers connect automatically. Use `"disabled": true` (not `enabled`) to keep one configured without connecting.
A higher-precedence config that defines the same server name **replaces the whole object** — repeat every required
field in an override, or use a different name.

## Local (stdio)

```jsonc
"everything": {
  "type": "local",
  "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
  "cwd": ".",
  "environment": { "LOG_LEVEL": "info", "MCP_API_KEY": "{env:MCP_API_KEY}" },
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"local"` |
| `command` | Yes | Executable plus arguments |
| `cwd` | No | Process directory; relative paths resolve from the workspace (also the default) |
| `environment` | No | String env vars added to the inherited environment. Use `{env:NAME}`; `$NAME` is not expanded |
| `disabled` | No | `true` prevents connection (default `false`) |
| `codemode` | No | `false` exposes tools directly instead of through Code Mode (default `true`) |
| `timeout` | No | Per-server `{startup, catalog, execution}` overrides |
| `protocol` | No | `legacy` (default), `auto`, or `2026-07-28` |

## Remote (Streamable HTTP)

```jsonc
"context7": {
  "type": "remote",
  "url": "https://mcp.context7.com/mcp",
  "oauth": false,
  "headers": { "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}" },
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"remote"` |
| `url` | Yes | Absolute Streamable HTTP endpoint |
| `headers` | No | String HTTP headers |
| `oauth` | No | OAuth settings object, or `false` to disable OAuth |
| `disabled` | No | `true` prevents connection |
| `codemode` | No | `false` to skip Code Mode |
| `timeout` | No | Per-server timeout overrides |
| `protocol` | No | `legacy` \| `auto` \| `2026-07-28` |

## OAuth

OAuth is **on by default** for remote servers unless `oauth: false`. OpenCode discovers the authorization server,
uses PKCE, refreshes tokens, and tries dynamic client registration. For dynamic registration, configure only the URL:

```jsonc
"sentry": { "type": "remote", "url": "https://mcp.sentry.dev/mcp" }
```

Pre-registered clients use **snake_case** fields (V1 used camelCase):

```jsonc
"company-tools": {
  "type": "remote",
  "url": "https://mcp.example.com/mcp",
  "oauth": {
    "client_id": "{env:MCP_CLIENT_ID}",
    "client_secret": "{env:MCP_CLIENT_SECRET}",
    "scope": "tools:read tools:execute",
    "callback_port": 19876,
    "redirect_uri": "http://127.0.0.1:19876/callback",
  },
}
```

| Field | Description |
|-------|-------------|
| `client_id` | Pre-registered client ID; omit to attempt dynamic registration |
| `client_secret` | Secret for a pre-registered client |
| `scope` | Space-delimited scopes |
| `callback_port` | Local callback port 1–65535 (default: an available ephemeral port) |
| `redirect_uri` | Pre-registered loopback URI reaching the local callback listener |
| `auth_server_metadata_url` | OAuth/OIDC metadata URL when the server doesn't publish protected-resource metadata |

Use `oauth: false` only when the server authenticates purely with a header credential.

## Timeouts

Positive integer milliseconds. Defaults under `mcp.timeout`; a server's `timeout` object overrides matching keys.

| Timeout | Default | Applies to |
|---------|---------|------------|
| `startup` | 30 s | Transport connection and initialization |
| `catalog` | 30 s | Listing tools, prompts, resources, templates |
| `execution` | 12 h | Tool calls, prompt retrieval, resource reads |

V1 `timeout: <ms>` maps to `timeout: { catalog, execution }`; V1 `experimental.mcp_timeout` maps to the
`mcp.timeout.catalog`/`execution` defaults.

## Protocol

| Value | Behavior |
|-------|----------|
| `legacy` | Default; classic `initialize`, revisions up to 2025-11-25 |
| `auto` | Probes `server/discover` for 2026-07-28, falls back to legacy |
| `2026-07-28` | Requires the new revision; fails against older servers |

## Tool names and permissions

Tools are named `<server>_<tool>`; characters other than letters, digits, `_`, and `-` become `_`.
MCP prompts become commands `/<server>:<prompt>`. Hide or gate tools with permissions (V2 has no `tools` map):

```jsonc
{ "permissions": [{ "action": "context7_*", "resource": "*", "effect": "deny" }] }
```

## CLI and TUI

```bash
opencode mcp add context7 --url https://mcp.context7.com/mcp                  # writes project config
opencode mcp add context7 --global --url https://mcp.context7.com/mcp         # writes global config
opencode mcp add everything -- npx -y @modelcontextprotocol/server-everything # local server
opencode mcp add everything --env LOG_LEVEL=debug -- npx -y @modelcontextprotocol/server-everything
opencode mcp add context7 --url https://mcp.context7.com/mcp --header CONTEXT7_API_KEY=secret
opencode mcp list
opencode mcp auth sentry
opencode mcp logout sentry
```

In the TUI, `/mcps` views, connects, disconnects, or authenticates servers. To remove a server, delete its entry
from the config where it was added.

# V2 MCP Servers Reference

Source: <https://opencode.ai/v2/docs/mcp-servers/> (2.2.5).

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
signs in with PKCE, and refreshes tokens; credentials are stored outside project configuration. Most servers need only
the URL:

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
| `client_id` | Pre-registered client ID; takes priority over CIMD and DCR |
| `client_secret` | Secret for a confidential client, sent in the token request body; omit for public clients |
| `scope` | Space-delimited scopes; defaults to the scope the server names when it rejects an unauthenticated request |
| `callback_port` | Local callback port 1–65535 (default: the `redirect_uri` port, then an available ephemeral port) |
| `redirect_uri` | Pre-registered loopback URI reaching the local callback listener; setting it disables CIMD |
| `auth_server_metadata_url` | OAuth/OIDC metadata URL when the server doesn't publish protected-resource metadata |

Use `oauth: false` only when the server authenticates purely with a header credential.

### Client registration

OpenCode identifies itself with the first method that applies (2.2.5 docs):

| Method | Used when |
|--------|-----------|
| Pre-registered client | `oauth.client_id` is configured |
| Client ID Metadata Document (CIMD) | The authorization server supports CIMD and public clients (`client_id_metadata_document_supported` and token auth method `none`), and `oauth.redirect_uri` is not set; OpenCode sends its metadata document URL as the `client_id` |
| Dynamic client registration (DCR) | Neither applies; OpenCode registers a client and reuses it on later sign-ins |

CIMD allows loopback redirects without a port (`http://127.0.0.1/callback`, `http://localhost/callback`), so
`callback_port` works with CIMD; a custom `redirect_uri` does not, and OpenCode falls back to DCR. If the server
supports neither CIMD nor DCR, configure a pre-registered client.

## Timeouts

Positive integer milliseconds. Defaults under `mcp.timeout` apply to servers defined in configuration files; a
server's `timeout` object overrides matching keys.

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

Command text fills a prompt's arguments in order; separate them with spaces and quote values that contain spaces
(`/context_7:find_docs react "server components"`).

## Resources, instructions, and input requests

- **Resources:** agents read MCP resources through the built-in `list_mcp_resources` and `read_mcp_resource` tools. The
  permission actions are `opencode_list_mcp_resources` (resource = server name) and `opencode_read_mcp_resource`
  (resource = `<server>:<uri>`), for example `{ "action": "opencode_read_mcp_resource", "resource": "docs:*", "effect": "allow" }`.
- **Server instructions:** instructions a server returns during initialization are added to the system prompt inside
  `<mcp_instructions>`. They are omitted when the agent's permissions deny every one of the server's tools, or deny
  `execute` for a Code Mode server. Changed entries are sent as updates, not the full list (2.1.3).
- **Input requests:** servers can ask for input during a call (MCP elicitation). OpenCode shows a form, or a link for
  URL requests; dismissing the form cancels the request. Forms appear instead of the call waiting until it times out
  (2.1.4 release notes).
- **Code Mode:** by default agents reach a server's tools through `execute` under the server's namespace; set
  `codemode: false` to list them directly. Denying `execute` removes Code Mode and the tools reached only through it.

## CLI and TUI

```bash
opencode mcp add context7 --url https://mcp.context7.com/mcp                  # writes project config
opencode mcp add context7 --global --url https://mcp.context7.com/mcp         # writes global config
opencode mcp add everything -- npx -y @modelcontextprotocol/server-everything # local server
opencode mcp add everything --env LOG_LEVEL=debug -- npx -y @modelcontextprotocol/server-everything
opencode mcp add context7 --url https://mcp.context7.com/mcp --header CONTEXT7_API_KEY=secret
opencode mcp list
opencode mcp auth sentry
opencode mcp auth                                                             # pick from OAuth-capable servers
opencode mcp logout sentry
```

In the TUI, `/mcps` views, connects, disconnects, or authenticates servers. Disconnecting there does not change
configuration; edit configuration for OAuth client settings, timeouts, working directories, or to keep a server
disconnected. To remove a server, delete its entry from the config where it was added. Quote `{env:NAME}` header values
in the shell (`--header 'CONTEXT7_API_KEY={env:CONTEXT7_API_KEY}'`) so they are written literally.

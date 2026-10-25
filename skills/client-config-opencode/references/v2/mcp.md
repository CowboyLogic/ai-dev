# V2 MCP Servers Reference

Source: <https://opencode.ai/v2/docs/mcp-servers/> (checked against the 2.1.4 tag; CLI flags checked on the 2.1.4 binary).

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
signs in with PKCE, and refreshes tokens; credentials are stored outside project configuration. Most servers need
only the URL:

```jsonc
"sentry": { "type": "remote", "url": "https://mcp.sentry.dev/mcp" }
```

### Client registration (2.1.x docs)

OpenCode identifies itself with the first method that applies:

| Method | Used when |
|--------|-----------|
| Pre-registered client | `oauth.client_id` is configured |
| Client ID Metadata Document (CIMD) | The authorization server advertises `client_id_metadata_document_supported` and public-client support, and `oauth.redirect_uri` is **not** set. OpenCode sends its metadata document URL (`https://opencode.ai/oauth/opencode/client.json`) as the `client_id` and skips registration |
| Dynamic client registration (DCR) | Neither of the above applies; the registered client is reused on later sign-ins |

`callback_port` works with CIMD (loopback redirects `http://127.0.0.1/callback` and `http://localhost/callback` allow
any port); a custom `redirect_uri` does not, so OpenCode falls back to DCR. If the server supports neither CIMD nor
DCR, configure a pre-registered client.

### Pre-registered clients

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
MCP prompts become commands `/<server>:<prompt>`; command text fills the prompt's arguments in order, space-separated
with quotes around values containing spaces (`/context_7:find_docs react "server components"`). Hide or gate tools
with permissions (V2 has no `tools` map):

```jsonc
{ "permissions": [{ "action": "context7_*", "resource": "*", "effect": "deny" }] }
```

By default agents reach MCP tools through `execute` (Code Mode) under the server's normalized name; set
`codemode: false` on a server to list its tools directly. Denying `execute` removes every tool reached only through
Code Mode.

## Resources, server instructions, and input requests

- **Resources:** agents use the built-in `list_mcp_resources` and `read_mcp_resource` tools. Their permission actions
  are `opencode_list_mcp_resources` (resource: the server name) and `opencode_read_mcp_resource` (resource:
  `<server>:<uri>`), e.g. `{ "action": "opencode_read_mcp_resource", "resource": "docs:*", "effect": "allow" }`.
- **Server instructions:** instructions a server returns at initialization are added to the system prompt inside
  `<mcp_instructions>`. They are omitted when the agent's permissions deny every tool of that server, or deny
  `execute` for a Code Mode server.
- **Input requests (elicitation):** OpenCode shows a server's input request as a form (or a link for URL requests);
  dismissing the form cancels it. Before 2.1.4 the call waited until it timed out (2.1.4 release notes); desktop and
  web show the forms from 2.1.4 too.

## CLI and TUI

```bash
opencode mcp add context7 --url https://mcp.context7.com/mcp                  # writes project config
opencode mcp add context7 --global --url https://mcp.context7.com/mcp         # writes global config
opencode mcp add everything -- npx -y @modelcontextprotocol/server-everything # local server
opencode mcp add everything --env LOG_LEVEL=debug -- npx -y @modelcontextprotocol/server-everything
opencode mcp add context7 --url https://mcp.context7.com/mcp --header 'CONTEXT7_API_KEY={env:CONTEXT7_API_KEY}'
opencode mcp list
opencode mcp auth sentry
opencode mcp auth                 # no name: pick from the OAuth-capable servers
opencode mcp logout sentry
```

`--header` and `--env` take `name=value` and repeat (`opencode mcp add --help` on 2.1.4). Quote `{env:NAME}` so the
shell writes it literally instead of embedding a secret in the config.

In the TUI, `/mcps` views, connects, disconnects, or authenticates servers; disconnecting there does not change
configuration (edit `disabled` to keep a server disconnected). To remove a server, delete its entry from the config
where it was added.

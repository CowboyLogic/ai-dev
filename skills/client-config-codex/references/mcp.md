# MCP Servers Reference

Codex connects to Model Context Protocol servers over STDIO (a local process) or streamable HTTP (a
URL). The Codex CLI, the ChatGPT desktop app, and the IDE extension share one MCP configuration for the
same Codex host. Hosted plugin tools in ChatGPT web can have different capabilities.

## Config locations

| Scope | File | Notes |
|-------|------|-------|
| User | `~/.codex/config.toml` | Default; `$CODEX_HOME/config.toml` when `CODEX_HOME` is set |
| Project | `.codex/config.toml` | Trusted projects only |
| Plugin | Plugin manifest | Bundled servers; user config controls only on/off state and tool policy |

Define each server as a `[mcp_servers.<server-name>]` table. Use `codex mcp add` for the basics and edit
the TOML for anything finer.

```toml
[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
env_vars = ["LOCAL_TOKEN"]

[mcp_servers.context7.env]
MY_ENV_VAR = "MY_ENV_VALUE"
```

## STDIO servers

| Key | Required | Description |
|-----|----------|-------------|
| `command` | Yes | Command that starts the server |
| `args` | No | Argument array |
| `env` | No | Environment variables to set for the server (non-secret values) |
| `env_vars` | No | Names of variables to allow and forward from Codex's environment |
| `cwd` | No | Working directory for the server |
| `experimental_environment` | No | `remote` starts the server through a remote executor when one is available |

`env_vars` entries are plain names or objects with a source:

```toml
env_vars = ["LOCAL_TOKEN", { name = "REMOTE_TOKEN", source = "remote" }]
```

String entries and `source = "local"` read Codex's local environment. `source = "remote"` reads the
remote executor environment and requires remote MCP stdio.

## Streamable HTTP servers

| Key | Required | Description |
|-----|----------|-------------|
| `url` | Yes | Server address |
| `bearer_token_env_var` | No | Name of the env var holding a bearer token sent in `Authorization` |
| `http_headers` | No | Map of header name to static value |
| `env_http_headers` | No | Map of header name to env var name; values come from the environment |
| `http_headers_helper` | No | Local command that prints a JSON object of header names and string values |
| `auth` | No | `oauth` (default) uses stored MCP OAuth credentials; `chatgpt` uses the current ChatGPT session for the trusted first-party ChatGPT origin, with stored OAuth as fallback |

Credential order: configured bearer tokens and authorization headers come first, then `auth`. If no
credential source resolves, Codex connects without authentication; run `codex mcp login NAME`
separately to start OAuth.

`http_headers_helper` works for HTTP connections from the local environment only, not stdio servers or
remote execution. Codex caches helper headers. After a same-origin POST returns `401` or `403`, it
refreshes once and retries only if the values changed. Explicit bearer tokens and OAuth credentials beat
a helper-provided `Authorization` header, and an OAuth `403` for insufficient scope does not trigger a
refresh.

```toml
[mcp_servers.figma]
url = "https://mcp.figma.com/mcp"
bearer_token_env_var = "FIGMA_OAUTH_TOKEN"
http_headers = { "X-Figma-Region" = "us-east-1" }
```

Prefer `env_http_headers` for any header that carries a secret:

```toml
[mcp_servers.example.env_http_headers]
Authorization = "EXAMPLE_AUTH_HEADER"
```

## Behavior, timeouts, and tool policy

| Key | Description |
|-----|-------------|
| `enabled` | `false` disables a server without deleting it |
| `required` | `true` fails startup if this enabled server cannot initialize |
| `startup_timeout_sec` | Seconds to wait for startup (default `10`) |
| `tool_timeout_sec` | Seconds to wait for a tool run (default `60`) |
| `enabled_tools` | Tool allow list |
| `disabled_tools` | Tool deny list, applied after `enabled_tools` |
| `default_tools_approval_mode` | `auto`, `prompt`, `writes`, or `approve`; `writes` prompts for tools not marked read-only |
| `tools.<tool>.approval_mode` | Per-tool override of the approval mode |
| `tools.<tool>.output_token_limit` | Positive token budget for that tool's output, before the standard 20% serialization allowance |

Top-level `mcp_optional_startup_grace_ms` (default `1000`) is how long Codex waits for optional
servers when building the initial tool catalog; `0` waits for each `startup_timeout_sec`.

```toml
[mcp_servers.chrome_devtools]
url = "http://localhost:3000/mcp"
enabled_tools = ["open", "screenshot"]
disabled_tools = ["screenshot"]     # applied after enabled_tools
default_tools_approval_mode = "prompt"
startup_timeout_sec = 20
tool_timeout_sec = 45
enabled = true

[mcp_servers.chrome_devtools.tools.open]
approval_mode = "approve"
output_token_limit = 30000
```

## CLI commands

| Command | Purpose |
|---------|---------|
| `codex mcp list [--json]` | Configured servers with status and auth |
| `codex mcp get NAME [--json]` | One server's configuration |
| `codex mcp add NAME -- COMMAND...` | Add a stdio server |
| `codex mcp add NAME --url URL` | Add a streamable HTTP server |
| `codex mcp remove NAME` | Remove a server |
| `codex mcp login NAME` | Start OAuth for a streamable HTTP server |
| `codex mcp logout NAME` | Drop stored OAuth credentials |

There is no `enable` or `disable` subcommand; set `enabled = false` in the TOML instead. OAuth actions
work only with streamable HTTP servers that support OAuth.

| `codex mcp add` option | Purpose |
|------------------------|---------|
| `--env KEY=VALUE` | Environment variable for the launched server; stdio only |
| `--url URL` | Streamable HTTP server address |
| `--bearer-token-env-var ENV_VAR` | Env var to read for a bearer token; HTTP only |
| `--oauth-client-id ID` | Pre-registered OAuth client ID |
| `--oauth-client-secret SECRET` | Client secret for a pre-registered client (see Safety notes) |
| `--oauth-client-registration auto\|cimd\|dcr` | Registration strategy for the immediate login only |
| `--oauth-resource RESOURCE` | OAuth `resource` parameter for login |

```bash
codex mcp add context7 -- npx -y @upstash/context7-mcp
codex mcp add example-http --url https://mcp.example.com/mcp --bearer-token-env-var EXAMPLE_TOKEN
codex mcp add example --url https://mcp.example.com --oauth-client-id my-client
```

| `codex mcp login` option | Purpose |
|--------------------------|---------|
| `--scopes SCOPE,SCOPE` | Comma-separated scopes to request |
| `--no-browser` | Print the authorization URL and accept the callback URL without opening a browser |
| `--oauth-client-registration auto\|cimd\|dcr` | Registration strategy for this login only |

In the TUI, `/mcp` lists active servers and tools; `/mcp verbose` adds server diagnostics. Any other
argument prints usage.

## OAuth

Codex supports OAuth Client ID Metadata Documents (CIMD) and Dynamic Client Registration (DCR).
`auto` (the default) picks CIMD when the authorization server advertises
`client_id_metadata_document_supported: true`, lists `none` in `token_endpoint_auth_methods_supported`,
and the callback is a supported loopback URL; otherwise it uses DCR when available. A configured client
ID always wins and skips registration. The `--oauth-client-registration` choice is never stored in
`config.toml`. If the server advertises `scopes_supported`, Codex prefers them over scopes configured in
`config.toml`.

A pre-registered client is saved with its callback in `config.toml`:

```toml
[mcp_servers.example]
url = "https://mcp.example.com"

[mcp_servers.example.oauth]
client_id = "my-client"
callback_url = "http://127.0.0.1/callback"
```

`codex mcp add` prints the exact `OAuth callback URL` to register with the provider; register that value.

| Setting | Scope | Purpose |
|---------|-------|---------|
| `mcp_oauth_callback_url` | Global | Custom callback path or remote ingress URL, for example `"https://devbox.example.internal/callback"` |
| `mcp_oauth_callback_port` | Global | Fixed listener port, for example `5555` |
| `mcp_servers.<name>.oauth.callback_port` | Per server | Overrides the global port |
| `mcp_servers.<name>.oauth.client_id`, `.callback_url` | Per server | Pre-registered client |

Callback rules that matter when editing:

- The authorization server must advertise `authorization_response_iss_parameter_supported: true` and a
  metadata `issuer` for Codex to reuse a stable callback. Otherwise Codex appends a server-specific
  callback ID, such as `http://127.0.0.1/callback/XuuuHAzzHOni`, derived from the server URL.
- A saved `callback_url` that lacks the correct callback ID is ignored on servers without issuer
  support; Codex then uses `mcp_oauth_callback_url`, or `http://127.0.0.1/callback`, plus the ID. The
  stored value is not modified.
- Portless `http://127.0.0.1` callbacks get the active listener port inserted at authorization time.
  This does not apply to `localhost`, IPv6, HTTPS, or callbacks that already include a port.
- A port inside `callback_url` does not configure the listener. For a direct loopback callback, use a
  portless URL or set the same port in both places. A proxied callback may use a different external
  port. Local callback URLs bind locally; non-local ones bind to `0.0.0.0`.
- A mismatched `iss`, or a missing `iss` when issuer support is advertised, rejects the response with no
  code exchange and no callback fallback.

## Plugin-provided servers

Installed plugins can bundle MCP servers in their manifest. Codex launches them from the plugin, so
user config never sets their transport command. Control them under `plugins.<plugin>.mcp_servers.<server>`:

```toml
[plugins."sample@test".mcp_servers.sample]
enabled = true
default_tools_approval_mode = "prompt"
enabled_tools = ["read", "search"]

[plugins."sample@test".mcp_servers.sample.tools.search]
approval_mode = "approve"
```

Plugin HTTP servers can declare OAuth in the plugin's `.mcp.json` with camelCase keys `clientId`,
`callbackUrl`, and `callbackPort`; `callbackPort` overrides `mcp_oauth_callback_port`, and with
neither set Codex picks an ephemeral port. Callback selection follows the same rules as other servers.

```json
{ "mcpServers": { "sample": { "type": "http", "url": "https://mcp.example.com/mcp",
  "oauth": { "clientId": "my-client", "callbackUrl": "http://127.0.0.1/callback/registered" } } } }
```

## Safety notes

- Reference secrets by env var name only: `bearer_token_env_var`, `env_http_headers`, and `env_vars`.
  Never write a token into `http_headers`, `env`, or `--env KEY=VALUE`. Inspect existing configs for
  literal `Authorization` values and flag them instead of copying them.
- `codex mcp list` prints an Env column, and `--json` output for `list` and `get` includes `env` and
  `http_headers` fields. Treat that output as sensitive; do not paste it into chats or commits.
- `--oauth-client-secret` puts the secret on the command line and into shell history. Ask the user to
  run that step themselves or supply it another way; never generate it in a command.
- Project `.codex/config.toml` servers load only in trusted projects. Review a repo's MCP entries
  before trusting it, because a stdio `command` runs on the developer machine.
- Narrow blast radius with `enabled_tools`, `disabled_tools`, and `default_tools_approval_mode = "prompt"`.
- `codex mcp add` and `remove` edit `config.toml`. Run them only when the user asked for the change,
  and confirm the target before removing.

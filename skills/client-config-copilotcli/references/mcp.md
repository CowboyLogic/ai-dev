# MCP and LSP Servers Reference

## MCP config locations and priority

| Source | Location | Priority |
|--------|----------|----------|
| Session-only | `--additional-mcp-config=JSON` or `=@file.json` | Highest |
| Plugins | Plugin MCP configs | |
| Workspace | `.mcp.json` (any dir from cwd up to the repo root) and `.github/mcp.json` | |
| User | `~/.copilot/mcp-config.json` (or `$COPILOT_HOME/mcp-config.json`) | Lowest |
| Built-in | `github-mcp-server`, `playwright`, `fetch`, `time` | Always available |

Same-name servers: the higher-priority source wins. Within workspace files, files closer to cwd
win, and `.mcp.json` beats `.github/mcp.json` in the same directory. VS Code's
`.vscode/mcp.json` is **not** read (see [Migrating](#migrating-from-vscodemcpjson)).

Workspace servers load only in trusted directories. In `-p` they load if the directory is already
trusted, otherwise only with `GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP=true`.

## Structure

```json
{
  "mcpServers": {
    "playwright": {
      "type": "local",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {},
      "tools": ["*"]
    },
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" },
      "tools": ["*"]
    }
  }
}
```

Project files (`.mcp.json`, `.github/mcp.json`) may also use a bare top-level format where each key
is a server name:

```json
{ "playwright": { "type": "local", "command": "npx", "args": ["@playwright/mcp@latest"] } }
```

**Credentials**: `env` supports `$VAR`, `${VAR}`, and `${VAR:-default}` expansion, and `headers`
support variable expansion. Keep secrets in your shell profile, not in the file. `PATH` is
inherited automatically.

---

## Transport types

| `type` | Description | Required fields |
|--------|-------------|-----------------|
| `local` / `stdio` | Local process over stdin/stdout (default `local`; `stdio` is the portable name) | `command`, `args` |
| `http` | Streamable HTTP (`"streamable-http"` accepted as alias) | `url` |
| `sse` | Legacy Server-Sent Events — deprecated in the MCP spec, still supported | `url` |

### Local server fields

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes | Command to start the server |
| `args` | Yes | Argument array |
| `tools` | Yes | `["*"]` or a list of tool names |
| `type` | No | `"local"` (default) or `"stdio"` |
| `env` | No | Environment variables (expansion supported) |
| `cwd` | No | Working directory |
| `timeout` | No | Tool discovery / call timeout in ms (default `30000`) |
| `deferTools` | No | `"auto"` (default) or `"never"` (always visible under tool search) |
| `disableToolCache` | No | `true` skips the tool snapshot cache for this server |
| `slowConnectionThresholdMs` | No | Warn after this many ms connecting (default `10000`; warning only; positive integer ≤ `2147483647`) |

`timeout` sets the real connection budget (floored at `60000` ms); `slowConnectionThresholdMs` only
controls when the slow-connection warning prints.

### Remote server fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"http"` or `"sse"` |
| `url` | Yes | Server URL |
| `tools` | Yes | Tools to enable |
| `headers` | No | HTTP headers (expansion supported) |
| `oauthClientId` | No | Static OAuth client ID (skips dynamic registration) |
| `oauthScopes` | No | Non-empty array of scopes to request; requires `oauthClientId`. A scope in the server's `WWW-Authenticate` challenge still wins; otherwise this overrides discovered `scopes_supported` |
| `oauthPublicClient` | No | Default `true`; `false` for confidential clients |
| `oauthGrantType` | No | `"authorization_code"` (default) or `"client_credentials"` (headless) |
| `oidc` | No | `true` injects GitHub OIDC tokens (`GITHUB_COPILOT_OIDC_MCP_TOKEN[_SUFFIX]` in `env`, or Bearer header for remote) |
| `timeout`, `deferTools`, `slowConnectionThresholdMs` | No | As for local servers |

Optional `filterMapping` controls output processing: `none`, `markdown`, or `hidden_characters`
(default).

Headless OAuth (`client_credentials`) also needs `oauthPublicClient: false` and a `client_secret`
stored in the system keychain (set via the `/mcp` UI).

Entra-protected remote servers authenticate through the OS broker on Windows; on Linux and macOS the
CLI tries to mint a token silently from the Entra account signed in via `/login`, and falls back to
the browser flow (`--device-code` bypasses the broker). Signing in with Entra also surfaces a hosted
WorkIQ server in `/mcp`, disabled by default (`/mcp enable WorkIQ`).

---

## Adding servers

### Interactive

```text
/mcp add
```

Opens a form (Tab between fields, Ctrl+S to save; takes effect immediately). Enter `env` as
`KEY=VALUE` pairs or JSON.

### Terminal

```bash
# Local (stdio) — command after --
copilot mcp add context7 -- npx -y @upstash/context7-mcp
copilot mcp add github --env GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_PAT -- \
  docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server

# Remote
copilot mcp add --transport http notion https://mcp.notion.com/mcp
copilot mcp add --transport http --header "Authorization: Bearer YOUR-TOKEN" stripe https://mcp.stripe.com
```

| Option | Description |
|--------|-------------|
| `--transport` | `stdio` (default), `http`, `sse` |
| `--env KEY=VALUE` | Env var (repeatable) |
| `--header "H: V"` | Header for remote servers (repeatable) |
| `--tools` | `"*"` (default), comma-separated list, or `""` for none |
| `--timeout MS` | Default `30000` |
| `--json` | Print the added config as JSON |
| `--show-secrets` | Print full env/header values (avoid in shared logs) |

`copilot mcp add` writes to `~/.copilot/mcp-config.json`.

### Registry search (experimental)

`/mcp search [QUERY]` browses the GitHub MCP Registry (or the org-configured registry) and
pre-fills the add form. Requires `--experimental` or `/experimental on`.

---

## Management

### In a session

| Command | Purpose |
|---------|---------|
| `/mcp` or `/mcp config` | Plugins dashboard pinned to MCP servers |
| `/mcp list` (`ls`) | Plain-text list with status |
| `/mcp show [NAME]` | Details and tools |
| `/mcp edit NAME` | Edit (refuses workspace `.mcp.json` servers — edit the file) |
| `/mcp delete NAME` | Remove |
| `/mcp disable NAME` / `/mcp enable NAME` | Persisted toggle |
| `/mcp auth NAME` | Re-run OAuth (for `needs-auth` status) |
| `/mcp reload` | Reload configuration |

### In the terminal

| Command | Purpose |
|---------|---------|
| `copilot mcp list [--json]` | All servers by source (built-in, user, workspace, plugin) |
| `copilot mcp get NAME [--json]` | Type, status, tools |
| `copilot mcp enable NAME` / `disable NAME` | Persisted toggle |
| `copilot mcp remove NAME` | Remove from user config (workspace servers: edit the file) |

Disabled servers show `(disabled)` in `list` output (`"enabled": false` with `--json`).

Settings: `disabledMcpServers` (configured but not started), `enabledMcpServers` (turn on built-ins
that are off by default). Flags: `--disable-builtin-mcps`, `--disable-mcp-server=NAME`,
`--enable-mcp-server=NAME` (session only).

---

## Naming, tools, and permissions

- Server names may contain any printable characters except control characters and `}`.
- Tool names sent to the model are `serverName-toolName`, sanitized to `[A-Za-z0-9_-]`, capped at
  64 characters.
- Every MCP tool call requires permission. Pre-approve with `--allow-tool='SERVER'` or
  `--allow-tool='SERVER(tool_name)'`; block with `--deny-tool='SERVER(tool_name)'`.
- Local stdio servers that spawn inside the sandbox show `connected (sandboxed)`; toggling
  `/sandbox` restarts only local servers. Remote servers aren't locally sandboxed, though the
  sandbox network policy can restrict the CLI's connections to them.
- Stdio servers must write logs to **stderr**; non-JSON stdout lines are dropped (a line over 1 MB
  skips that check and is forwarded as is).
- Trust levels by source: built-in High; repository `.github/mcp.json` and workspace `.mcp.json`
  Medium (review recommended); user `~/.copilot/mcp-config.json` user-defined; remote servers Low
  (always review).
- To pull a server package from a private npm registry, put `--registry` and the registry URL before
  the package name in `args`, for example `"command": "npx"` with
  `"args": ["--registry", "https://npm.pkg.github.com", "@my-org/internal-mcp-server"]`.
  `--registry` and the other npm options (`--userconfig`,
  `--globalconfig`, `--prefix`, `--cache`, `--node-options`, `--workspace`, `-w`) are treated as
  value-consuming arguments when the server's identity fingerprint is computed, so allowlist checks
  still work with them ahead of the package name.
- Tool snapshots are cached; disable per server with `disableToolCache` or globally with
  `COPILOT_MCP_TOOL_CACHE=false`.
- Per the v1.0.89–v1.0.93 release notes (not in the docs reference): `server/tool` and
  `server/*` tool filters match MCP tool names that contain a slash, and MCP server configuration
  changes apply between turns without restarting the session. v1.0.90 added `--mcp-github-auth` to
  scope GitHub account auth to approved MCP server origins.

## Governance

- Enterprise registry/allowlist policies apply automatically; blocked servers show
  `MCP server "NAME" was blocked by your enterprise "ENTERPRISE"`. Fail-closed if the policy can't
  be verified. Built-in servers are exempt. The CLI fingerprints each non-default server from its
  command, arguments, and remote URL and sends the fingerprints to the enterprise evaluate endpoint;
  the check also runs when the `MCP_ENTERPRISE_ALLOWLIST` experimental feature flag is enabled.
- Managed settings may set `allowedMcpServers` / `deniedMcpServers` entries matching exactly one of
  `serverUrl` (wildcards allowed), `serverCommand` (exact command + args array), or `serverName`.
  Deny always wins; an empty `allowedMcpServers` array blocks all non-default servers.
  `serverName` allowlist entries are case-sensitive, have no wildcards, and are limited to letters,
  numbers, `_`, `.`, `/`, and `-` (so registry names such as `microsoft/playwright-mcp` work);
  denylist entries accept any non-empty string. Users choose server names, so use `serverUrl` or
  `serverCommand` when you need to enforce a server's identity.

## Migrating from `.vscode/mcp.json`

```bash
jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json
```

---

## LSP servers

Language servers give the agent definitions, references, and renames.

| Scope | File |
|-------|------|
| User | `~/.copilot/lsp-config.json` |
| Project | `.github/lsp.json` |

```json
{
  "lspServers": {
    "typescript": {
      "command": "typescript-language-server",
      "args": ["--stdio"],
      "fileExtensions": { ".ts": "typescript", ".tsx": "typescriptreact", ".js": "javascript" }
    }
  }
}
```

Server names: alphanumerics, underscores, hyphens.

| Field | Required | Description |
|-------|----------|-------------|
| `command` | No | Command that starts the server. At least one of `command`, `bash`, or `powershell` is required |
| `bash` | No | Bash script run instead of `command`, for pipes or environment setup. Not used on Windows if `powershell` is also set |
| `powershell` | No | PowerShell script run instead of `command`; used on Windows when set |
| `args` | No | Arguments for `command`; ignored when the server starts from `bash` or `powershell` |
| `cwd` | No | Working directory to launch from (default: the project root) |
| `fileExtensions` | Yes | Map of extension to language ID |
| `env` | No | Env vars (`${VAR}`, `${VAR:-default}`) |
| `rootUri` | No | Root relative to the Git root (default `"."`) |
| `initializationOptions` | No | Sent in the LSP `initialize` request |
| `requestTimeoutMs` | No | Request timeout (default 90 seconds) |
| `initializationTimeoutMs` | No | Startup handshake timeout (default 60 seconds); raise it if a server needs longer for initial project analysis |
| `spawnTimeoutMs` | No | Timeout for spawning the server process, in milliseconds (no default documented) |
| `warmupTimeoutMs` | No | Timeout for the server's warmup phase, in milliseconds (no default documented) |

Manage with `/lsp` (`show`, `test NAME`, `reload`, `logs`, `help`) or `copilot lsp list [--json]`.

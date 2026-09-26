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
| `slowConnectionThresholdMs` | No | Warn after this many ms connecting (default `10000`; warning only) |

### Remote server fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"http"` or `"sse"` |
| `url` | Yes | Server URL |
| `tools` | Yes | Tools to enable |
| `headers` | No | HTTP headers (expansion supported) |
| `oauthClientId` | No | Static OAuth client ID (skips dynamic registration) |
| `oauthPublicClient` | No | Default `true`; `false` for confidential clients |
| `oauthGrantType` | No | `"authorization_code"` (default) or `"client_credentials"` (headless) |
| `oidc` | No | `true` injects GitHub OIDC tokens (`GITHUB_COPILOT_OIDC_MCP_TOKEN[_SUFFIX]` in `env`, or Bearer header for remote) |
| `timeout`, `deferTools`, `slowConnectionThresholdMs` | No | As for local servers |

Optional `filterMapping` controls output processing: `none`, `markdown`, or `hidden_characters`
(default).

Headless OAuth (`client_credentials`) also needs `oauthPublicClient: false` and a `client_secret`
stored in the system keychain (set via the `/mcp` UI).

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
- Local stdio servers can run sandboxed and show `connected (sandboxed)`.
- Stdio servers must write logs to **stderr**; non-JSON stdout lines are dropped.
- Tool snapshots are cached; disable per server with `disableToolCache` or globally with
  `COPILOT_MCP_TOOL_CACHE=false`.

## Governance

- Enterprise registry/allowlist policies apply automatically; blocked servers show
  `MCP server "NAME" was blocked by your enterprise "ENTERPRISE"`. Fail-closed if the policy can't
  be verified. Built-in servers are exempt.
- Managed settings may set `allowedMcpServers` / `deniedMcpServers` entries matching exactly one of
  `serverUrl` (wildcards allowed), `serverCommand` (exact command + args array), or `serverName`.
  Deny always wins; an empty `allowedMcpServers` array blocks all non-default servers.

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
| `command` | Yes | Command that starts the server |
| `args` | No | Arguments |
| `fileExtensions` | Yes | Map of extension to language ID |
| `env` | No | Env vars (`${VAR}`, `${VAR:-default}`) |
| `rootUri` | No | Root relative to the Git root (default `"."`) |
| `initializationOptions` | No | Sent in the LSP `initialize` request |
| `requestTimeoutMs` | No | Request timeout (default 90 seconds) |

Manage with `/lsp` (`show`, `test NAME`, `reload`, `logs`, `help`) or `copilot lsp list [--json]`.

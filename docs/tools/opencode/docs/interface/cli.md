# OpenCode — CLI Reference

> Source: <https://opencode.ai/docs/cli/>  
> Last updated: April 10, 2026

The OpenCode CLI starts the [TUI](tui.md) by default when run without arguments.

```bash
opencode
```

---

## Global Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--help` | `-h` | Display help |
| `--version` | `-v` | Print version number |
| `--print-logs` | | Print logs to stderr |
| `--log-level` | | Log level: `DEBUG`, `INFO`, `WARN`, `ERROR` |

---

## `opencode` (TUI)

```bash
opencode [project]
```

| Flag | Short | Description |
|------|-------|-------------|
| `--continue` | `-c` | Continue the last session |
| `--session` | `-s` | Session ID to continue |
| `--fork` | | Fork the session when continuing |
| `--prompt` | | Initial prompt to use |
| `--model` | `-m` | Model in `provider/model` format |
| `--agent` | | Agent to use |
| `--port` | | Port to listen on |
| `--hostname` | | Hostname to listen on |

---

## Commands

### `opencode run`

Run OpenCode non-interactively with a prompt:

```bash
opencode run "Explain how closures work in JavaScript"
```

Attach to a running `opencode serve` instance:

```bash
opencode serve                          # start headless server
opencode run --attach http://localhost:4096 "Explain async/await"
```

| Flag | Short | Description |
|------|-------|-------------|
| `--command` | | The command to run |
| `--continue` | `-c` | Continue the last session |
| `--session` | `-s` | Session ID to continue |
| `--fork` | | Fork session when continuing |
| `--share` | | Share the session |
| `--model` | `-m` | Model in `provider/model` format |
| `--agent` | | Agent to use |
| `--file` | `-f` | File(s) to attach to message |
| `--format` | | Output format: `default` or `json` |
| `--title` | | Session title |
| `--attach` | | Attach to running server URL |
| `--port` | | Local server port (random default) |

---

### `opencode serve`

Start a headless HTTP server for API access:

```bash
opencode serve
```

Set `OPENCODE_SERVER_PASSWORD` to enable HTTP basic auth (default username: `opencode`).

| Flag | Description |
|------|-------------|
| `--port` | Port to listen on |
| `--hostname` | Hostname to listen on |
| `--mdns` | Enable mDNS discovery |
| `--cors` | Additional CORS origins |

---

### `opencode web`

Start a headless server with a web interface:

```bash
opencode web
```

| Flag | Description |
|------|-------------|
| `--port` | Port to listen on |
| `--hostname` | Hostname to listen on |
| `--mdns` | Enable mDNS discovery |
| `--cors` | Additional CORS origins |

---

### `opencode attach`

Attach a TUI to an already-running backend server:

```bash
opencode attach http://10.20.30.40:4096
```

| Flag | Short | Description |
|------|-------|-------------|
| `--dir` | | Working directory to start TUI in |
| `--session` | `-s` | Session ID to continue |

---

### `opencode agent`

Manage agents.

```bash
opencode agent create    # create a new agent interactively
opencode agent list      # list all available agents
```

---

### `opencode auth`

Manage provider credentials.

```bash
opencode auth login      # add / update API keys (stored in ~/.local/share/opencode/auth.json)
opencode auth list       # list authenticated providers
opencode auth ls         # alias for list
opencode auth logout     # remove provider credentials
```

---

### `opencode models`

List all available models from configured providers:

```bash
opencode models              # all models
opencode models anthropic    # filter by provider
```

| Flag | Description |
|------|-------------|
| `--refresh` | Refresh the model cache from models.dev |
| `--verbose` | Show metadata including costs |

---

### `opencode mcp`

Manage MCP servers.

```bash
opencode mcp add                  # add MCP server interactively
opencode mcp list                 # list configured servers and status
opencode mcp ls                   # alias for list
opencode mcp auth <name>          # authenticate with OAuth server
opencode mcp auth list            # list OAuth servers and their status
opencode mcp logout <name>        # remove OAuth credentials
opencode mcp debug <name>         # debug OAuth connection issues
```

---

### `opencode session`

```bash
opencode session list             # list all sessions
opencode session list -n 10       # last 10 sessions
opencode session list --format json
```

---

### `opencode stats`

Show token usage and cost statistics:

```bash
opencode stats
```

| Flag | Description |
|------|-------------|
| `--days N` | Last N days (default: all time) |
| `--tools N` | Number of tools to show |
| `--models N` | Show top N models by usage |
| `--project` | Filter by project |

---

### `opencode export`

Export session data as JSON:

```bash
opencode export [sessionID]
```

---

### `opencode import`

Import session data from a file or share URL:

```bash
opencode import session.json
opencode import https://opncd.ai/s/abc123
```

---

### `opencode github`

Manage the GitHub Actions agent.

```bash
opencode github install    # set up GitHub Actions workflow
opencode github run        # run the agent (used in CI)
```

---

### `opencode acp`

Start an ACP (Agent Client Protocol) server via stdin/stdout:

```bash
opencode acp
```

| Flag | Description |
|------|-------------|
| `--cwd` | Working directory |
| `--port` | Port to listen on |
| `--hostname` | Hostname to listen on |

---

### `opencode upgrade`

Update OpenCode:

```bash
opencode upgrade           # latest version
opencode upgrade v0.1.48   # specific version
```

| Flag | Short | Description |
|------|-------|-------------|
| `--method` | `-m` | Installation method: `curl`, `npm`, `pnpm`, `bun`, `brew` |

---

### `opencode uninstall`

```bash
opencode uninstall
```

| Flag | Short | Description |
|------|-------|-------------|
| `--keep-config` | `-c` | Keep configuration files |
| `--keep-data` | `-d` | Keep session data and snapshots |
| `--dry-run` | | Preview what would be removed |
| `--force` | `-f` | Skip confirmation prompts |

---

## Environment Variables

| Variable | Type | Description |
|----------|------|-------------|
| `OPENCODE_AUTO_SHARE` | boolean | Automatically share sessions |
| `OPENCODE_GIT_BASH_PATH` | string | Path to Git Bash on Windows |
| `OPENCODE_CONFIG` | string | Path to config file |
| `OPENCODE_TUI_CONFIG` | string | Path to TUI config file |
| `OPENCODE_CONFIG_DIR` | string | Path to config directory |
| `OPENCODE_CONFIG_CONTENT` | string | Inline JSON config |
| `OPENCODE_DISABLE_AUTOUPDATE` | boolean | Disable auto-update checks |
| `OPENCODE_DISABLE_TERMINAL_TITLE` | boolean | Disable automatic terminal title updates |
| `OPENCODE_PERMISSION` | string | Inline JSON permissions config |
| `OPENCODE_DISABLE_DEFAULT_PLUGINS` | boolean | Disable default plugins |
| `OPENCODE_DISABLE_LSP_DOWNLOAD` | boolean | Disable auto LSP server downloads |
| `OPENCODE_ENABLE_EXA` | boolean | Enable Exa web search tools |
| `OPENCODE_ENABLE_EXPERIMENTAL_MODELS` | boolean | Enable experimental models |
| `OPENCODE_DISABLE_AUTOCOMPACT` | boolean | Disable automatic context compaction |
| `OPENCODE_DISABLE_CLAUDE_CODE` | boolean | Disable `.claude` support |
| `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT` | boolean | Disable `~/.claude/CLAUDE.md` |
| `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` | boolean | Disable `.claude/skills` |
| `OPENCODE_DISABLE_MOUSE` | boolean | Disable mouse capture in TUI |
| `OPENCODE_SERVER_PASSWORD` | string | Enable basic auth for `serve`/`web` |
| `OPENCODE_SERVER_USERNAME` | string | Override basic auth username (default `opencode`) |
| `OPENCODE_MODELS_URL` | string | Custom URL for fetching models config |

### Experimental

| Variable | Type | Description |
|----------|------|-------------|
| `OPENCODE_EXPERIMENTAL` | boolean | Enable all experimental features |
| `OPENCODE_EXPERIMENTAL_LSP_TOOL` | boolean | Enable experimental LSP tool |
| `OPENCODE_EXPERIMENTAL_BASH_DEFAULT_TIMEOUT_MS` | number | Default bash timeout in ms |
| `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX` | number | Max output tokens |
| `OPENCODE_EXPERIMENTAL_FILEWATCHER` | boolean | Enable file watcher for entire dir |
| `OPENCODE_EXPERIMENTAL_OXFMT` | boolean | Enable oxfmt formatter |
| `OPENCODE_EXPERIMENTAL_EXA` | boolean | Enable experimental Exa features |
| `OPENCODE_EXPERIMENTAL_LSP_TY` | boolean | Enable TY LSP for Python files |
| `OPENCODE_EXPERIMENTAL_MARKDOWN` | boolean | Enable experimental markdown features |
| `OPENCODE_EXPERIMENTAL_PLAN_MODE` | boolean | Enable plan mode |

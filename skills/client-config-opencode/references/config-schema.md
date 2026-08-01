# Full Config Schema Reference

Schema: `https://opencode.ai/config.json`
TUI schema: `https://opencode.ai/tui.json`

## Table of Contents
- [Core fields](#core-fields)
- [Server](#server)
- [Commands](#commands)
- [Instructions](#instructions)
- [Formatters](#formatters)
- [Compaction](#compaction)
- [Skills & Plugins](#skills--plugins)
- [File watcher](#file-watcher)
- [Config precedence order](#config-precedence-order)
- [Managed / enterprise](#managed--enterprise)
- [Annotated full example](#annotated-full-example)

---

## Core fields

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `$schema` | string | Enable editor validation | `"https://opencode.ai/config.json"` |
| `model` | string | Default model (`provider/model`) | `"anthropic/claude-sonnet-4-5"` |
| `small_model` | string | Lightweight task model | `"anthropic/claude-haiku-4-5"` |
| `default_agent` | string | Default primary agent (must be `primary` mode; falls back to `build` with a warning if invalid). Applies across TUI, `opencode run`, desktop app, GitHub Action | `"build"` |
| `subagent_depth` | integer | Max subagent nesting depth (default `1`: primary can launch subagents, they can't launch more; `0` blocks all subagent launches) | `2` |
| `share` | enum | `"manual"` (default) \| `"auto"` \| `"disabled"` | `"manual"` |
| `autoupdate` | bool \| `"notify"` | Auto-update behavior (only applies if not installed via a package manager) | `"notify"` |
| `snapshot` | boolean | Track filesystem changes for undo/revert (default `true`); disable on large repos to avoid slow indexing | `true` |
| `logLevel` | enum | `"DEBUG"` \| `"INFO"` \| `"WARN"` \| `"ERROR"` | `"INFO"` |
| `username` | string | Custom display name | `"alice"` |
| `shell` | string | Default shell for the interactive terminal and agent bash tool calls; absolute path or short name. Auto-detected per-OS if unset | `"pwsh"` |
| `tools` | object (string → bool) | Enable/disable tools (built-in, custom, or `<mcp-server>_<tool>`) by name or glob | `{ "write": false, "bash": false }` |
| `disabled_providers` | array | Provider IDs to disable (even if creds/env vars present); takes priority over `enabled_providers` | `["amazon-bedrock"]` |
| `enabled_providers` | array | Restrict to only these providers | `["anthropic", "openai"]` |
| `attachment` | object | `attachment.image` — `auto_resize`, `max_width`/`max_height` (default 2000px), `max_base64_bytes` (default 5242880) | `{ "image": { "auto_resize": true } }` |
| `references` | object | Named git or local directory references (`{repository, branch?, description?, hidden?}` or `{path, description?, hidden?}`) | — |
| `experimental` | object | Unstable, may change/be removed. Keys: `policies` (allow/deny provider access, see below), `mcp_timeout`, `batch_tool`, `openTelemetry`, `primary_tools`, `continue_loop_on_deny`, `disable_paste_summary` | `{ "policies": [...] }` |
| `enterprise` | object | Enterprise config — `{"url": "https://your-enterprise"}` | — |
| `reference` | object | **Deprecated** — use `references` instead | — |
| `mode` | object | **Deprecated** — use `agent` instead | — |
| `autoshare` | boolean | **Deprecated** — use `share` instead | — |
| `layout` | string | **Deprecated** — always stretch layout | — |

### Policies (experimental)

Allow/deny opencode actions on configured resources; currently scoped to provider access.

```json
{ "experimental": { "policies": [ { "effect": "deny", "action": "provider.use", "resource": "openai" } ] } }
```
---

## Server

Controls `opencode serve` / `opencode web`:

```json
{
  "port": 4096,
  "hostname": "0.0.0.0",
  "mdns": true,
  "mdnsDomain": "opencode.local",
  "cors": ["https://my-app.example.com"]
}
```

| Key | Description |
|-----|-------------|
| `port` | Listening port (default: 4096) |
| `hostname` | Listening address (default: `localhost`) |
| `mdns` | Enable mDNS service discovery |
| `mdnsDomain` | Custom mDNS domain (default: `opencode.local`) |
| `cors` | Additional allowed CORS origins |

---

## Commands

Define custom slash commands. Also loadable as markdown files in `~/.config/opencode/commands/` or `.opencode/commands/`.

```json
{
  "command": {
    "review": {
      "description": "Review the current diff for issues",
      "template": "Review this diff for bugs, security issues, and style: {file:.git/COMMIT_EDITMSG}",
      "agent": "build",
      "model": "anthropic/claude-opus-4-5"
    },
    "standup": {
      "description": "Generate a standup summary",
      "template": "Summarize my recent git commits into a standup update: {env:GIT_LOG}",
      "subtask": true
    }
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `template` | Yes | Command prompt — supports `{env:VAR}` and `{file:path}` |
| `description` | No | Shown in command picker |
| `agent` | No | Agent to use for this command |
| `model` | No | Model override |
| `subtask` | No | Run as a subtask (boolean) |

### Prompt template syntax

| Syntax | Description |
|--------|-------------|
| `{env:VAR_NAME}` | Inject environment variable value |
| `{file:path}` | Inject file contents |
| `$ARGUMENTS` | All arguments passed after the command name |
| `$1`, `$2`, ... | Positional argument references |
| `` !`command` `` | Inject shell command output |
| `@filename` | Include file content by name |

---

## Instructions

Load additional system instructions from files:

```json
{
  "instructions": [
    "~/.config/opencode/base-instructions.md",
    "{file:./CONVENTIONS.md}",
    ".opencode/project-rules.md"
  ]
}
```

Supports `~` expansion and relative paths. Files are concatenated into the system prompt.

---

## Formatters

Configure code formatters run after file edits:

```json
{
  "formatter": {
    "prettier": {
      "command": ["npx", "prettier", "--write"],
      "extensions": [".ts", ".tsx", ".js", ".json", ".css"]
    },
    "black": {
      "command": ["black"],
      "extensions": [".py"]
    },
    "builtin": {
      "disabled": true
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `command` | Formatter executable + args (file path appended automatically) |
| `extensions` | File extensions to format |
| `environment` | Additional env vars |
| `disabled` | Disable a formatter (including `builtin`) |

Built-in formatters (auto-detected when installed): `air`, `biome`, `cargofmt`, `clang-format`, `cljfmt`, `dart`, `dfmt`, `gleam`, `gofmt`, `htmlbeautifier`, `ktlint`, `mix`, `nixfmt`, `ocamlformat`, `ormolu`, `oxfmt` (experimental), `pint`, `prettier`, `rubocop`, `ruff`, `rustfmt`, `shfmt`, `standardrb`, `terraform`, `uv`, `zig`.

---

## LSP

Configure Language Server Protocol servers:

```json
{
  "lsp": {
    "typescript": {
      "command": ["typescript-language-server", "--stdio"],
      "extensions": [".ts", ".tsx"],
      "initialization": { "preferences": {} }
    },
    "python": {
      "command": ["pylsp"],
      "extensions": [".py"],
      "disabled": false
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `command` | LSP server command array |
| `extensions` | File extensions to activate LSP for |
| `env` | Environment variables |
| `initialization` | LSP initialization options object |
| `disabled` | Disable this LSP server |

---

## Tool output

Control truncation of tool output sent to the model:

```json
{
  "tool_output": {
    "max_lines": 500,
    "max_bytes": 51200
  }
}
```

| Field | Description |
|-------|-------------|
| `max_lines` | Maximum lines per tool output |
| `max_bytes` | Maximum bytes per tool output |

---

## Compaction

Control how context is managed when it fills up:

```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 8000,
    "tail_turns": 5,
    "preserve_recent_tokens": 2000
  }
}
```

| Field | Description |
|-------|-------------|
| `auto` | Automatically compact when context is full (default: `true`) |
| `prune` | Remove old **tool outputs** to save tokens (default: `false`) |
| `reserved` | Token buffer reserved during compaction, to avoid overflow |
| `tail_turns` | Recent user turns (plus their assistant/tool responses) to keep verbatim during compaction (default: `2`) |
| `preserve_recent_tokens` | Max tokens from recent turns to preserve verbatim after compaction |

---

## Skills & Plugins

```json
{
  "skills": {
    "paths": ["~/.config/opencode/skills", ".opencode/skills"],
    "urls": ["https://example.com/my-skills"]
  },
  "plugin": [
    "@opencode/plugin-example",
    ["@opencode/plugin-with-options", { "option": "value" }]
  ]
}
```

Plugins are NPM packages or local paths. Skills are directories with markdown files.

---

## File watcher

```json
{
  "watcher": {
    "ignore": ["node_modules/**", "*.log", ".git/**"]
  }
}
```

Glob patterns for files opencode should not watch for changes.

---

## Config precedence order

Configs are **merged**, not replaced — later sources override earlier ones only for conflicting keys. Load order (lowest to highest priority):

1. Remote config (`.well-known/opencode` — org defaults, fetched on provider auth)
2. Global config (`~/.config/opencode/opencode.json`)
3. Custom config (`OPENCODE_CONFIG` env var path)
4. Project config (`opencode.json` in project root, or nearest parent Git dir)
5. `.opencode/` directories (agents, commands, plugins — also `OPENCODE_CONFIG_DIR`)
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var, raw JSON)
7. Managed config files (system dirs below — admin-controlled)
8. macOS managed preferences (`.mobileconfig` via MDM) — highest, not user-overridable

`.opencode`/`~/.config/opencode` subdirectories use plural names (`agents/`, `commands/`, `modes/`, `plugins/`, `skills/`, `tools/`, `themes/`); singular forms still work for backwards compatibility.

## Managed / enterprise

### System-level config locations (admin-managed, not user-editable)

| Platform | Location |
|----------|----------|
| macOS | `/Library/Application Support/opencode/` |
| Linux | `/etc/opencode/` |
| Windows | `%ProgramData%\opencode\` |

### macOS MDM

Read from managed preference domain `ai.opencode.managed` via `.mobileconfig` profiles (Jamf, Kandji, FleetDM). Highest priority — user cannot override.

### Remote config

Deploy organization defaults via `.well-known/opencode` endpoint on your domain — lowest priority, overridden by everything else.

---

## Annotated full example

```jsonc
{
  "$schema": "https://opencode.ai/config.json",

  // Models
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "default_agent": "build",

  // Provider management
  "enabled_providers": ["anthropic", "openai"],

  // Behavior
  "share": "manual",
  "autoupdate": "notify",
  "snapshot": true,
  "logLevel": "INFO",

  // Permissions (global defaults)
  "permission": {
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "list": "allow",
    "edit": "ask",
    "bash": "ask",
    "webfetch": "ask"
  },

  // MCP servers
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "environment": { "GITHUB_PERSONAL_ACCESS_TOKEN": "{env:GITHUB_TOKEN}" }
    }
  },

  // Custom commands
  "command": {
    "review": {
      "description": "Review staged changes",
      "template": "Review this diff for issues: {file:.git/MERGE_MSG}"
    }
  },

  // Additional instructions
  "instructions": [".opencode/project-rules.md"],

  // Server (for opencode web)
  "port": 4096,
  "mdns": false
}
```

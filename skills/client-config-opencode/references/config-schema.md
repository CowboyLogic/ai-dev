# V1 Config Schema Reference

> [!NOTE]
> This file covers the **V1** `opencode.json` shape (singular keys: `permission`, `agent`, `provider`, `command`,
> `plugin`). For native V2 (`permissions`, `agents`, `providers`, `commands`, `plugins`, `mcp.servers`), use
> [v2/config-schema.md](v2/config-schema.md). V2 still reads everything below.

Schema: `https://opencode.ai/config.json` (V1 shape, `additionalProperties: false`)
TUI schema: `https://opencode.ai/tui.json`

## Table of Contents

- [Core fields](#core-fields)
- [Server](#server)
- [Commands](#commands)
- [Instructions](#instructions)
- [Formatters](#formatters)
- [LSP](#lsp)
- [Tool output](#tool-output)
- [Compaction](#compaction)
- [Skills and plugins](#skills-and-plugins)
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
| `small_model` | string | Model for lightweight tasks like title generation; defaults to a cheaper model from your provider if available, else the main model | `"anthropic/claude-haiku-4-5"` |
| `default_agent` | string | Default primary agent (must be `primary` mode; falls back to `build` with a warning if invalid). Applies across TUI, `opencode run`, desktop app, GitHub Action | `"build"` |
| `subagent_depth` | integer | Max subagent nesting depth (default `1`: primary can launch subagents, they can't launch more; `0` blocks all subagent launches) | `2` |
| `share` | enum | `"manual"` (default) \| `"auto"` \| `"disabled"` | `"manual"` |
| `autoupdate` | bool \| `"notify"` | Auto-update behavior (only works if not installed via a package manager such as Homebrew) | `"notify"` |
| `snapshot` | boolean | Track filesystem changes for undo/revert (default `true`); disable on large repos to avoid slow indexing | `true` |
| `logLevel` | enum | `"DEBUG"` \| `"INFO"` \| `"WARN"` \| `"ERROR"` | `"INFO"` |
| `username` | string | Custom display name instead of the system username | `"alice"` |
| `shell` | string | Shell for the interactive terminal and compatible agent tool calls; absolute path or short name. Auto-detected per OS if unset | `"pwsh"` |
| `permission` | object \| string | Tool permissions — see [permissions.md](permissions.md) | `{ "edit": "ask" }` |
| `tools` | object (string → bool) | **Deprecated since v1.1.1** (merged into `permission`, still honored). Enable/disable tools by name or glob | `{ "write": false }` |
| `disabled_providers` | array | Provider IDs never loaded, even with creds/env vars; wins over `enabled_providers` | `["amazon-bedrock"]` |
| `enabled_providers` | array | Allowlist — only these providers load | `["anthropic", "openai"]` |
| `attachment` | object | `attachment.image` — `auto_resize` (default on), `max_width`/`max_height` (default 2000), `max_base64_bytes` (default 5242880) | `{ "image": { "auto_resize": true } }` |
| `references` | object | Named Git or local directory references (string shorthand, `{repository, branch?, description?, hidden?}`, or `{path, description?, hidden?}`) | — |
| `experimental` | object | Unstable. Keys: `policies`, `mcp_timeout`, `batch_tool`, `openTelemetry`, `primary_tools`, `continue_loop_on_deny`, `disable_paste_summary` | `{ "policies": [...] }` |
| `enterprise` | object | `{ "url": "https://your-enterprise" }` | — |
| `reference` | object | **Deprecated** — use `references` | — |
| `mode` | object | **Deprecated** — use `agent` | — |
| `autoshare` | boolean | **Deprecated** — use `share` | — |
| `layout` | string | **Deprecated** — always stretch layout | — |

Legacy `theme`, `keybinds`, and `tui` keys in `opencode.json` are deprecated and auto-migrated to `tui.json` when
possible.

### Policies (experimental)

Allow/deny actions on resources. V1 supports one action, `provider.use`. Last matching statement wins; no match =
allowed; a global-config policy beats a project policy for the same provider. Prefer policies over
`enabled_providers`/`disabled_providers`.

```json
{
  "experimental": {
    "policies": [
      { "effect": "deny", "action": "provider.use", "resource": "*" },
      { "effect": "allow", "action": "provider.use", "resource": "anthropic" }
    ]
  }
}
```

---

## Server

Controls `opencode serve` / `opencode web`. These keys live under a **`server` object**, not at the top level.

```json
{
  "server": {
    "port": 4096,
    "hostname": "0.0.0.0",
    "mdns": true,
    "mdnsDomain": "myproject.local",
    "cors": ["http://localhost:5173"]
  }
}
```

| Key | Description |
|-----|-------------|
| `port` | Port to listen on |
| `hostname` | Hostname to listen on (defaults to `0.0.0.0` when `mdns` is on and no hostname is set) |
| `mdns` | Enable mDNS service discovery |
| `mdnsDomain` | Custom mDNS domain (default: `opencode.local`) |
| `cors` | Additional allowed origins — full origins (scheme + host + optional port) |

---

## Commands

Custom slash commands. Also loadable as Markdown in `~/.config/opencode/commands/` or `.opencode/commands/`
(filename = command name; frontmatter = options; body = template).

```json
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-haiku-4-5"
    },
    "component": {
      "template": "Create a new React component named $ARGUMENTS with TypeScript support.",
      "description": "Create a new component",
      "subtask": true
    }
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `template` | Yes | Prompt sent to the LLM |
| `description` | No | Shown in the TUI command list |
| `agent` | No | Agent to run it; if that agent is a subagent, the command triggers a subagent invocation by default |
| `model` | No | Model override |
| `variant` | No | Model variant (schema field) |
| `subtask` | No | `true` forces a subagent invocation even for a primary agent; `false` disables the default subagent behavior |

A custom command with the same name as a built-in (`/init`, `/undo`, `/redo`, `/share`, `/help`) overrides it.

### Prompt template syntax

| Syntax | Description |
|--------|-------------|
| `$ARGUMENTS` | All arguments passed after the command name |
| `$1`, `$2`, … | Positional arguments |
| `` !`command` `` | Inject shell command output (runs in the project root) |
| `@filename` | Include file content |

---

## Instructions

Additional instruction files, globs, or remote URLs (fetched with a 5-second timeout):

```json
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md",
    "https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"
  ]
}
```

`AGENTS.md` files are loaded automatically (project files found by traversing up from cwd, plus
`~/.config/opencode/AGENTS.md`). Claude Code fallbacks: `CLAUDE.md` (if no `AGENTS.md`) and `~/.claude/CLAUDE.md`
(if no global `AGENTS.md`). Disable with `OPENCODE_DISABLE_CLAUDE_CODE=1`, `OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1`,
or `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`.

---

## Formatters

**Disabled unless configured.** `true` enables all built-ins; an object enables built-ins plus overrides; `false`
disables formatters enabled by another config.

```json
{
  "formatter": {
    "prettier": { "disabled": true },
    "custom-prettier": {
      "command": ["npx", "prettier", "--write", "$FILE"],
      "environment": { "NODE_ENV": "development" },
      "extensions": [".js", ".ts", ".jsx", ".tsx"]
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `command` | Command array; `$FILE` is replaced with the file path. Required for custom formatters |
| `extensions` | File extensions to format |
| `environment` | Additional env vars |
| `disabled` | Disable a formatter |

Built-ins (run when their requirement is met): `air`, `biome`, `cargofmt`, `clang-format`, `cljfmt`, `dart`, `dfmt`,
`gleam`, `gofmt`, `htmlbeautifier`, `ktlint`, `mix`, `nixfmt`, `ocamlformat`, `ormolu`, `oxfmt` (experimental),
`pint`, `prettier`, `rubocop`, `ruff`, `rustfmt`, `shfmt`, `standardrb`, `terraform`, `uv`, `zig`.

---

## LSP

**Disabled unless configured.** `true` enables built-ins; an object enables built-ins plus overrides.

```json
{
  "lsp": {
    "typescript": { "disabled": true },
    "custom-lsp": {
      "command": ["custom-lsp-server", "--stdio"],
      "extensions": [".custom"],
      "initialization": { "preferences": {} }
    }
  }
}
```

| Field | Description |
|-------|-------------|
| `command` | LSP server command array (required unless the entry only disables a server) |
| `extensions` | File extensions to activate for |
| `env` | Environment variables |
| `initialization` | LSP `initialize` options |
| `disabled` | Disable this server |

The docs note LSP is not always a net positive; running lint/typecheck commands documented in `AGENTS.md` is often
better.

---

## Tool output

Truncation thresholds; overflow is written to the truncation directory and a preview is returned.

```json
{ "tool_output": { "max_lines": 2000, "max_bytes": 51200 } }
```

Defaults: `max_lines` 2000, `max_bytes` 51200.

---

## Compaction

```json
{ "compaction": { "auto": true, "prune": false, "reserved": 10000 } }
```

| Field | Description |
|-------|-------------|
| `auto` | Compact automatically when context is full (default `true`) |
| `prune` | Remove old tool outputs to save tokens (default `false`) |
| `reserved` | Token buffer kept free during compaction |
| `tail_turns` | Max recent user turns (plus their responses) kept verbatim; by default retention is limited only by the token budget (schema-only field) |
| `preserve_recent_tokens` | Max tokens from recent turns preserved verbatim (schema-only field) |

---

## Skills and plugins

```json
{
  "skills": {
    "paths": ["./team-skills"],
    "urls": ["https://example.com/.well-known/skills/"]
  },
  "plugin": [
    "opencode-helicone-session",
    ["./plugin/local.ts", { "enabled": true }]
  ]
}
```

Skills are auto-discovered from `.opencode/skills/<name>/SKILL.md`, `~/.config/opencode/skills/`, and the
Claude/agents-compatible `.claude/skills/` and `.agents/skills/` (project and global). V1 `SKILL.md` frontmatter
requires `name` (1–64 chars, `^[a-z0-9]+(-[a-z0-9]+)*$`, matching the directory) and `description` (1–1024 chars).

Plugins: npm packages (installed with Bun at startup, cached in `~/.cache/opencode/node_modules/`), or local
`.js`/`.ts` files in `.opencode/plugins/` and `~/.config/opencode/plugins/` (auto-loaded). An entry may be a string
or a `[name, options]` pair.

---

## File watcher

```json
{ "watcher": { "ignore": ["node_modules/**", "dist/**", ".git/**"] } }
```

---

## Config precedence order

Configs are **merged** — later sources override earlier ones only for conflicting keys. Load order (low → high):

1. Remote config (`.well-known/opencode` — org defaults, fetched when you authenticate with a supporting provider)
2. Global config (`~/.config/opencode/opencode.json`)
3. Custom config (`OPENCODE_CONFIG` env var path)
4. Project config (`opencode.json` in cwd, else the nearest one up to the Git root)
5. `.opencode/` directories (agents, commands, plugins); `OPENCODE_CONFIG_DIR` loads after these
6. Inline config (`OPENCODE_CONFIG_CONTENT` env var)
7. Managed config files (system dirs below)
8. macOS managed preferences (`.mobileconfig` via MDM) — highest, not user-overridable

`.opencode` / `~/.config/opencode` subdirectories use plural names (`agents/`, `commands/`, `modes/`, `plugins/`,
`skills/`, `tools/`, `themes/`); singular forms still work.

## Managed / enterprise

### System-level config (admin-managed)

Drop `opencode.json` or `opencode.jsonc` in:

| Platform | Location |
|----------|----------|
| macOS | `/Library/Application Support/opencode/` |
| Linux | `/etc/opencode/` |
| Windows | `%ProgramData%\opencode` |

### macOS MDM

Preference domain `ai.opencode.managed`, read from `/Library/Managed Preferences/<user>/ai.opencode.managed.plist`
or `/Library/Managed Preferences/ai.opencode.managed.plist`. Plist keys map directly to `opencode.json` fields.
Verify with `opencode debug config`.

---

## Variable substitution

- `{env:VAR}` — environment variable (empty string if unset)
- `{file:path}` — file contents; path relative to the config file, or absolute (`/`, `~`)

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
  "formatter": true,

  // Permissions (global defaults)
  "permission": {
    "edit": "ask",
    "bash": { "*": "ask", "git status *": "allow" },
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
      "template": "Review this diff for issues:\n!`git diff --cached`"
    }
  },

  // Additional instructions
  "instructions": [".opencode/project-rules.md"],

  // Server (for opencode serve / web)
  "server": { "port": 4096, "mdns": false }
}
```

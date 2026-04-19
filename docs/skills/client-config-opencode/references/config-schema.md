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
- [Managed / enterprise](#managed--enterprise)
- [Annotated full example](#annotated-full-example)

---

## Core fields

| Key | Type | Description | Example |
|-----|------|-------------|---------|
| `$schema` | string | Enable editor validation | `"https://opencode.ai/config.json"` |
| `model` | string | Default model (`provider/model`) | `"anthropic/claude-sonnet-4-5"` |
| `small_model` | string | Lightweight task model | `"anthropic/claude-haiku-4-5"` |
| `default_agent` | string | Default primary agent | `"build"` |
| `share` | enum | `"manual"` \| `"auto"` \| `"disabled"` | `"manual"` |
| `autoupdate` | bool \| `"notify"` | Auto-update behavior | `"notify"` |
| `snapshot` | boolean | Track filesystem changes | `true` |
| `logLevel` | enum | `"DEBUG"` \| `"INFO"` \| `"WARN"` \| `"ERROR"` | `"INFO"` |
| `username` | string | Custom display name | `"alice"` |
| `disabled_providers` | array | Provider IDs to disable | `["bedrock"]` |
| `enabled_providers` | array | Restrict to only these providers | `["anthropic", "openai"]` |

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

---

## Compaction

Control how context is managed when it fills up:

```json
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 8000
  }
}
```

| Field | Description |
|-------|-------------|
| `auto` | Automatically compact when context is near limit |
| `prune` | Remove older messages during compaction |
| `reserved` | Tokens reserved for response generation |

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

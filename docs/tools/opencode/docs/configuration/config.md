# OpenCode — Configuration

> Source: <https://opencode.ai/docs/config/>  
> Last updated: April 10, 2026

---

## Format

OpenCode supports JSON and JSONC (JSON with Comments). Reference the schema for editor autocomplete:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "autoupdate": true,
  "server": {
    "port": 4096
  }
}
```

---

## Locations and Precedence

Config sources are merged (not replaced). Later sources override earlier ones for conflicting keys.

| Priority | Source | Location |
|----------|--------|----------|
| 1 (lowest) | Remote | `.well-known/opencode` endpoint (org defaults) |
| 2 | Global | `~/.config/opencode/opencode.json` |
| 3 | Custom | `OPENCODE_CONFIG` env var |
| 4 | Project | `opencode.json` in project root |
| 5 | Directory | `.opencode/` subdirectories |
| 6 | Inline | `OPENCODE_CONFIG_CONTENT` env var |
| 7 (highest) | Managed | `/Library/Application Support/opencode/` (macOS) |

TUI-specific settings go in `tui.json` (or `tui.jsonc`) alongside `opencode.json`. Schema: `https://opencode.ai/tui.json`.

### Global config
`~/.config/opencode/opencode.json` — user-wide preferences.

### Per-project config
`opencode.json` in project root. Safe to commit to Git.

### Custom path
```bash
export OPENCODE_CONFIG=/path/to/my/custom-config.json
```

### Custom directory
```bash
export OPENCODE_CONFIG_DIR=/path/to/my/config-directory
```

### Managed settings (enterprise)

| OS | Path |
|----|------|
| macOS | `/Library/Application Support/opencode/` |
| Linux | `/etc/opencode/` |
| Windows | `%ProgramData%\opencode` |

macOS also supports MDM-deployed `.mobileconfig` via the `ai.opencode.managed` preference domain.

---

## Schema Reference

### Models

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "small_model": "anthropic/claude-haiku-4-5",
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,
        "chunkTimeout": 30000,
        "setCacheKey": true
      }
    }
  }
}
```

- `model` — default model in `provider/model-id` format
- `small_model` — lightweight model for tasks like title generation
- `provider.options.timeout` — request timeout in ms (default 300000)
- `provider.options.chunkTimeout` — stream chunk timeout in ms

### TUI

```jsonc
// tui.json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight",
  "scroll_speed": 3,
  "scroll_acceleration": { "enabled": true },
  "diff_style": "auto",
  "mouse": true
}
```

### Server

```jsonc
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

### Tools

```jsonc
{
  "tools": {
    "write": false,
    "bash": false
  }
}
```

### Agents

```jsonc
{
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "model": "anthropic/claude-sonnet-4-5",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": {
        "write": false,
        "edit": false
      }
    }
  }
}
```

### Default agent

```jsonc
{
  "default_agent": "plan"
}
```

Must be a primary agent (`"build"`, `"plan"`, or a custom primary agent).

### Sharing

```jsonc
{
  "share": "manual"   // "manual" | "auto" | "disabled"
}
```

### Commands

```jsonc
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report.\nFocus on the failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-haiku-4-5"
    }
  }
}
```

### Keybinds

```jsonc
// tui.json
{
  "keybinds": {}
}
```

See [keybinds.md](../interface/keybinds.md) for available actions.

### Themes

```jsonc
// tui.json
{
  "theme": "tokyonight"
}
```

### Snapshot

```jsonc
{
  "snapshot": false   // disable undo/redo snapshots (not recommended)
}
```

### Autoupdate

```jsonc
{
  "autoupdate": false    // true | false | "notify"
}
```

### Formatters

```jsonc
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

### Permissions

```jsonc
{
  "permission": {
    "edit": "ask",
    "bash": "ask"
  }
}
```

### Compaction

```jsonc
{
  "compaction": {
    "auto": true,
    "prune": true,
    "reserved": 10000
  }
}
```

### Watcher

```jsonc
{
  "watcher": {
    "ignore": ["node_modules/**", "dist/**", ".git/**"]
  }
}
```

### MCP servers

```jsonc
{
  "mcp": {}
}
```

See [mcp-servers.md](../features/mcp-servers.md).

### Plugins

```jsonc
{
  "plugin": ["opencode-helicone-session", "@my-org/custom-plugin"]
}
```

### Instructions

```jsonc
{
  "instructions": ["CONTRIBUTING.md", "docs/guidelines.md", ".cursor/rules/*.md"]
}
```

Accepts file paths, glob patterns, and remote URLs.

### Disabled / Enabled providers

```jsonc
{
  "disabled_providers": ["openai", "gemini"],
  "enabled_providers": ["anthropic", "openai"]
}
```

`disabled_providers` takes priority over `enabled_providers`.

---

## Variable Substitution

### Environment variables

```jsonc
{
  "model": "{env:OPENCODE_MODEL}",
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```

### File contents

```jsonc
{
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{file:~/.secrets/openai-key}"
      }
    }
  }
}
```

File paths can be relative to the config file or absolute (starting with `/` or `~`).

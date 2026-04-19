# Settings Schema Reference

Schema file: `~/.gemini/settings.json` (user) or `.gemini/settings.json` (project)

## Table of Contents
- [general](#general)
- [ui](#ui)
- [model](#model)
- [tools](#tools)
- [security](#security)
- [context](#context)
- [mcpServers](#mcpservers)
- [advanced](#advanced)
- [Annotated example](#annotated-example)

---

## general

| Field | Type | Description |
|-------|------|-------------|
| `vimMode` | boolean | Enable vim keybindings in the input editor |
| `approvalMode` | enum | Tool approval behavior (see below) |
| `preferredEditor` | string | Editor for `/edit` command (e.g. `"vim"`, `"code"`) |
| `autoUpdate` | boolean | Automatically install CLI updates |
| `notifications` | boolean | Enable desktop notifications |
| `checkpointing` | boolean | Enable session checkpointing for rewind |
| `planMode` | object | Plan mode defaults (`{ "enabled": boolean }`) |
| `sessionCleanup` | object | Session retention policy |

**Approval modes:**

| Mode | Behavior |
|------|----------|
| `"default"` | Ask before file edits and shell commands |
| `"auto_edit"` | Auto-approve file edits, ask for shell |
| `"plan"` | Always enter plan mode first |
| `"yolo"` | Auto-approve everything (no prompts) |

---

## ui

| Field | Type | Description |
|-------|------|-------------|
| `theme` | string | Theme name or path to `.json` file |
| `autoTheme` | boolean | Switch theme based on terminal background |
| `showBanner` | boolean | Show startup banner |
| `showTips` | boolean | Show usage tips |
| `showFooter` | boolean | Show footer with context count |
| `windowTitle` | string | Custom terminal window title |
| `showThinking` | boolean | Display inline thinking steps |
| `screenReader` | boolean | Enable screen reader accessibility mode |
| `customThemes` | object | Define custom themes (see below) |

**Built-in themes:**

Dark: `ANSI`, `Atom One`, `Ayu`, `Default`, `Dracula`, `GitHub`, `Holiday`, `Shades Of Purple`, `Solarized Dark`, `Tokyo Night`

Light: `ANSI Light`, `Ayu Light`, `Default Light`, `GitHub Light`, `Google Code`, `Solarized Light`, `Xcode`

**Custom theme structure:**
```json
{
  "ui": {
    "customThemes": {
      "my-theme": {
        "name": "my-theme",
        "type": "custom",
        "background": { "primary": "#1e1e2e" },
        "text": { "primary": "#cdd6f4", "secondary": "#a6adc8", "link": "#89b4fa" },
        "status": { "success": "#a6e3a1", "warning": "#f9e2af", "error": "#f38ba8" },
        "border": { "default": "#585b70" },
        "ui": { "comment": "#6c7086" }
      }
    },
    "theme": "my-theme"
  }
}
```

---

## model

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Default model (e.g. `"gemini-2.5-pro"`, `"gemini-2.5-flash"`) |
| `maxSessionTurns` | number | Max conversation turns before stopping |
| `contextCompression` | object | Compression threshold settings |
| `loopDetection` | object | Loop detection configuration |
| `summarizeToolOutput` | boolean | Summarize verbose tool output |

**Override model per-session:** `GEMINI_MODEL` env var or `--model` CLI flag.

---

## tools

| Field | Type | Description |
|-------|------|-------------|
| `sandbox` | string / object | Sandbox mode: `"none"`, `"docker"`, `"podman"`, or config object |
| `sandboxNetworkAccess` | boolean | Allow network inside sandbox |
| `shell` | object | Shell configuration (see below) |
| `discoveryCommand` | string | Command to discover additional tools |
| `allowedTools` | array | Allowlist of tool names |
| `excludeTools` | array | Blocklist of tool names |
| `truncationThreshold` | number | Max chars for tool output before truncation |

**Shell config object:**
```json
{
  "tools": {
    "shell": {
      "interactive": true,
      "pager": "less",
      "colorOutput": true
    }
  }
}
```

**Sandbox config object (Docker):**
```json
{
  "tools": {
    "sandbox": {
      "type": "docker",
      "image": "node:20",
      "networkAccess": false,
      "trustedPaths": ["/home/user/projects"]
    }
  }
}
```

---

## security

| Field | Type | Description |
|-------|------|-------------|
| `folderTrust.enabled` | boolean | Require explicit folder trust before loading project config |
| `redactedEnvVars` | array | Env var names to mask from logs/context |
| `allowedExtensions` | array | Extension IDs allowed to load |
| `blockedExtensions` | array | Extension IDs prevented from loading |
| `authType` | string | Force auth method: `"gemini"`, `"google"`, `"vertex"` |
| `conseca` | object | Context-aware security checker config |

**Trusted folders** are stored in `~/.gemini/trustedFolders.json` (managed by CLI — use `/permissions` to modify).

---

## context

| Field | Type | Description |
|-------|------|-------------|
| `fileName` | array | Context file names to scan for (`["GEMINI.md", "AGENTS.md"]`) |
| `respectGitignore` | boolean | Skip gitignored files in context loading |
| `respectGeminiignore` | boolean | Skip `.geminiignore`-listed files |
| `fuzzySearch` | boolean | Enable fuzzy file matching |
| `recursiveSearch` | boolean | Search subdirectories for context files |
| `includeDirectories` | array | Additional directories to include in context |

---

## mcpServers

See `references/mcp.md` for full MCP configuration.

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@scope/mcp-server"],
      "env": { "API_KEY": "${MY_API_KEY}" }
    }
  }
}
```

---

## advanced

| Field | Type | Description |
|-------|------|-------------|
| `nodeMemoryAutoConfig` | boolean | Auto-configure Node.js `--max-old-space-size` |
| `dnsOrder` | string | DNS resolution order (`"ipv4first"`, `"verbatim"`) |
| `excludedEnvVars` | array | Env vars excluded from context (default: `["DEBUG", "DEBUG_MODE"]`) |
| `bugReportCommand` | string | Command to run for `/bugreport` |

---

## Annotated example

```jsonc
{
  // Model selection
  "model": {
    "name": "gemini-2.5-pro",
    "maxSessionTurns": 100
  },

  // UI
  "ui": {
    "theme": "Tokyo Night",
    "showBanner": false
  },

  // Tool behavior
  "general": {
    "approvalMode": "auto_edit",
    "checkpointing": true,
    "autoUpdate": true
  },

  // Context files
  "context": {
    "fileName": ["GEMINI.md", "AGENTS.md"],
    "respectGitignore": true
  },

  // Security
  "security": {
    "folderTrust": { "enabled": true },
    "redactedEnvVars": ["OPENAI_API_KEY", "STRIPE_SECRET"]
  },

  // MCP servers
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    }
  },

  // Advanced
  "advanced": {
    "nodeMemoryAutoConfig": true
  }
}
```

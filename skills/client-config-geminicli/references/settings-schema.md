# Settings Schema Reference

Schema file: `~/.gemini/settings.json` (user) or `.gemini/settings.json` (project)

## Table of Contents
- [Settings Schema Reference](#settings-schema-reference)
  - [Table of Contents](#table-of-contents)
  - [general](#general)
  - [ui](#ui)
  - [output](#output)
  - [model](#model)
  - [tools](#tools)
  - [security](#security)
  - [context](#context)
  - [mcpServers](#mcpservers)
  - [advanced](#advanced)
  - [Annotated example](#annotated-example)
  - [agents](#agents)
  - [experimental](#experimental)
  - [skills](#skills)
  - [hooksConfig](#hooksconfig)
  - [ide](#ide)
  - [billing](#billing)

---

## general

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `general.vimMode` | boolean | `false` | Enable vim keybindings in the input editor |
| `general.defaultApprovalMode` | enum | `"default"` | Tool approval behavior (see below) — YOLO mode can only be enabled via CLI flag, not here |
| `general.preferredEditor` | string | — | Editor for `/edit` command (e.g. `"vim"`, `"code"`) |
| `general.enableAutoUpdate` | boolean | `true` | Automatically install CLI updates |
| `general.enableNotifications` | boolean | — | Enable desktop notifications |
| `general.notificationMethod` | string | `"auto"` | How to send terminal notifications |
| `general.checkpointing` | boolean | — | Enable session checkpointing for rewind |
| `general.plan.enabled` | boolean | `true` | Enable Plan Mode (read-only safety) |
| `general.plan.directory` | string | system tmp | Directory for planning artifacts |
| `general.plan.modelRouting` | boolean | `true` | Switch Pro/Flash based on Plan Mode status |
| `general.sessionRetention.enabled` | boolean | `true` | Enable automatic session cleanup |
| `general.sessionRetention.maxAge` | string | `"30d"` | Delete chats older than this (e.g. `"7d"`, `"24h"`) |
| `general.topicUpdateNarration` | boolean | `true` | Topic & Update model for reduced chattiness |
| `general.retryFetchErrors` | boolean | `true` | Retry on fetch failed errors |
| `general.maxAttempts` | number | `10` | Max chat model attempts (cannot exceed 10) |
| `general.debugKeystrokeLogging` | boolean | `false` | Enable keystroke debug logging |

**Approval modes (settable in config):**

| Mode | Behavior |
|------|----------|
| `"default"` | Ask before file edits and shell commands |
| `"auto_edit"` | Auto-approve file edits, ask for shell |
| `"plan"` | Always enter plan mode first |

> [!NOTE]
> YOLO mode (auto-approve all) is **CLI-only** — use `--yolo` or `--approval-mode=yolo` flag. It cannot be set in `settings.json`. Use `security.disableYoloMode: true` to prevent its use.

---

## ui

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ui.theme` | string | — | Theme name or path to `.json` file |
| `ui.autoThemeSwitching` | boolean | `true` | Switch theme based on terminal background |
| `ui.terminalBackgroundPollingInterval` | number | `60` | Seconds between background color polls |
| `ui.hideBanner` | boolean | `false` | Hide the startup banner |
| `ui.hideTips` | boolean | `false` | Hide usage tips |
| `ui.hideFooter` | boolean | `false` | Hide the footer |
| `ui.hideWindowTitle` | boolean | `false` | Hide the terminal window title bar |
| `ui.dynamicWindowTitle` | boolean | `true` | Update title with status icons (◇ Ready, ✋ Action, ✦ Working) |
| `ui.showStatusInTitle` | boolean | `false` | Show model thoughts in window title during work |
| `ui.inlineThinkingMode` | enum | `"off"` | Display model thinking inline: `"off"` or `"full"` |
| `ui.accessibility.screenReader` | boolean | `false` | Render plain-text output for screen readers |
| `ui.compactToolOutput` | boolean | `true` | Compact format for directory listings and file reads |
| `ui.hideContextSummary` | boolean | `false` | Hide context summary (GEMINI.md, MCP servers) above input |
| `ui.escapePastedAtSymbols` | boolean | `false` | Escape `@` in pasted text to prevent path expansion |
| `ui.showShortcutsHint` | boolean | `true` | Show "? for shortcuts" hint |
| `ui.showMemoryUsage` | boolean | `false` | Show memory usage in UI |
| `ui.showLineNumbers` | boolean | `true` | Show line numbers in chat |
| `ui.showCitations` | boolean | `false` | Show citations for generated text |
| `ui.showModelInfoInChat` | boolean | `false` | Show model name per turn in chat |
| `ui.showUserIdentity` | boolean | `true` | Show signed-in user identity (email) |
| `ui.showHomeDirectoryWarning` | boolean | `true` | Warn when running in home directory |
| `ui.showCompatibilityWarnings` | boolean | `true` | Show terminal/OS compatibility warnings |
| `ui.loadingPhrases` | enum | `"off"` | What to show while model works: `"tips"`, `"witty"`, `"all"`, `"off"` |
| `ui.errorVerbosity` | enum | `"low"` | Recoverable error display: `"low"` or `"full"` |
| `ui.useAlternateBuffer` | boolean | `false` | Use alternate screen buffer (preserves shell history) |
| `ui.incrementalRendering` | boolean | `true` | Reduce flickering (requires `useAlternateBuffer`) |
| `ui.useBackgroundColor` | boolean | `true` | Use background colors in UI |
| `ui.showSpinner` | boolean | `true` | Show spinner during operations |
| `ui.footer.hideCWD` | boolean | `false` | Hide current directory in footer |
| `ui.footer.hideSandboxStatus` | boolean | `false` | Hide sandbox status indicator in footer |
| `ui.footer.hideModelInfo` | boolean | `false` | Hide model name and context usage in footer |
| `ui.footer.hideContextPercentage` | boolean | `true` | Hide context window usage percentage |
| `ui.customThemes` | object | — | Define custom themes (see below) |

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

## output

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `output.format` | enum | `"text"` | CLI output format: `"text"` or `"json"` |

---

## model

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model.name` | string | — | Default model (e.g. `"gemini-2.5-pro"`, `"gemini-2.5-flash"`) |
| `model.maxSessionTurns` | number | `-1` | Max conversation turns (-1 = unlimited) |
| `model.compressionThreshold` | number | `0.5` | Fraction of context usage that triggers compression |
| `model.disableLoopDetection` | boolean | `false` | Disable infinite loop detection |
| `model.skipNextSpeakerCheck` | boolean | `true` | Skip next speaker validation check |

**Override model per-session:** `GEMINI_MODEL` env var or `--model` CLI flag.

---

## tools

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tools.sandbox` | string / object | — | Sandbox mode: `"none"`, `"docker"`, `"podman"`, or config object |
| `tools.sandboxNetworkAccess` | boolean | `false` | Allow network inside sandbox |
| `tools.sandboxAllowedPaths` | array | `[]` | Additional paths sandbox is allowed to access |
| `tools.shell.enableInteractiveShell` | boolean | `true` | Use node-pty for interactive shell (with child_process fallback) |
| `tools.shell.showColor` | boolean | `true` | Show color in shell output |
| `tools.useRipgrep` | boolean | `true` | Use ripgrep for faster file content search |
| `tools.discoveryCommand` | string | — | Command to discover additional tools |
| `tools.allowedTools` | array | — | Allowlist of tool names |
| `tools.excludeTools` | array | — | Blocklist of tool names |
| `tools.truncateToolOutputThreshold` | number | `40000` | Max chars for tool output before truncation (0 = disable) |
| `tools.disableLLMCorrection` | boolean | `true` | Disable LLM-based error correction for edit tools |

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

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `security.folderTrust.enabled` | boolean | `true` | Require explicit folder trust before loading project config |
| `security.environmentVariableRedaction.enabled` | boolean | `false` | Redact env vars that may contain secrets |
| `security.toolSandboxing` | boolean | `false` | Tool-level sandboxing (isolates individual tools) |
| `security.enableConseca` | boolean | `false` | Context-aware LLM security checker |
| `security.disableYoloMode` | boolean | `false` | Prevent YOLO mode even if `--yolo` flag is passed |
| `security.disableAlwaysAllow` | boolean | `false` | Disable "Always allow" option in confirmation dialogs |
| `security.enablePermanentToolApproval` | boolean | `false` | Enable "Allow for all future sessions" option |
| `security.autoAddToPolicyByDefault` | boolean | `false` | Make "Allow for all future sessions" the default for low-risk tools |
| `security.blockGitExtensions` | boolean | `false` | Block installing extensions from Git |
| `security.allowedExtensions` | array | `[]` | Regex patterns for allowed extensions (overrides `blockGitExtensions`) |
| `security.authType` | string | — | Force auth method: `"gemini"`, `"google"`, `"vertex"` |

**Trusted folders** are stored in `~/.gemini/trustedFolders.json` (managed by CLI — use `/permissions` to modify).

---

## context

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `context.fileName` | array | `["GEMINI.md"]` | Context file names to scan for |
| `context.discoveryMaxDirs` | number | `200` | Max directories to search for memory files |
| `context.loadMemoryFromIncludeDirectories` | boolean | `false` | When true, `/memory reload` scans include directories |
| `context.fileFiltering.respectGitIgnore` | boolean | `true` | Skip gitignored files |
| `context.fileFiltering.respectGeminiIgnore` | boolean | `true` | Skip `.geminiignore`-listed files |
| `context.fileFiltering.enableRecursiveFileSearch` | boolean | `true` | Search subdirectories for `@` completions |
| `context.fileFiltering.enableFuzzySearch` | boolean | `true` | Enable fuzzy file matching for `@` references |
| `context.fileFiltering.customIgnoreFilePaths` | array | `[]` | Additional ignore file paths (take precedence over `.geminiignore`) |

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

## agents

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `agents.browser.confirmSensitiveActions` | boolean | `false` | Require manual confirmation for sensitive browser actions |
| `agents.browser.blockFileUploads` | boolean | `false` | Hard-block file upload requests from browser agent |

---

## advanced

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `advanced.autoConfigureMemory` | boolean | `true` | Auto-configure Node.js `--max-old-space-size` (user settings only — workspace override ignored) |

---

## experimental

All experimental features default to `false` unless noted.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `experimental.voiceMode` | boolean | `false` | Enable voice dictation and commands (`/voice`, `/voice model`) |
| `experimental.voice.activationMode` | string | `"push-to-talk"` | How to trigger recording with Space key |
| `experimental.voice.backend` | string | `"gemini-live"` | Voice transcription backend |
| `experimental.voice.whisperModel` | string | `"ggml-base.en.bin"` | Whisper model for local transcription |
| `experimental.voice.stopGracePeriodMs` | number | `1000` | Ms to wait for final transcription after stopping |
| `experimental.gemma` | boolean | `false` | Enable access to Gemma 4 models |
| `experimental.gemmaModelRouter.enabled` | boolean | `false` | Route requests to local Gemma via LiteRT-LM shim |
| `experimental.gemmaModelRouter.autoStartServer` | boolean | `false` | Auto-start LiteRT-LM server on CLI start |
| `experimental.memoryV2` | boolean | `true` | Prompt-driven memory editing (four tiers). `false` = legacy `save_memory` tool |
| `experimental.autoMemory` | boolean | `false` | Extract reusable skills from past sessions; review via `/memory inbox` |
| `experimental.generalistProfile` | boolean | `false` | Use generalist agent profile for general coding tasks |
| `experimental.contextManagement` | boolean | `false` | Enable context management logic |
| `experimental.worktrees` | boolean | `false` | Automated Git worktree management for parallel work |
| `experimental.modelSteering` | boolean | `false` | Enable model steering hints during tool execution |
| `experimental.directWebFetch` | boolean | `false` | Web fetch bypassing LLM summarization |
| `experimental.useOSC52Paste` | boolean | `false` | OSC 52 paste (more robust for remote terminals) |
| `experimental.useOSC52Copy` | boolean | `false` | OSC 52 copy |

---

## skills

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `skills.enabled` | boolean | `true` | Enable Agent Skills |

---

## hooksConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `hooksConfig.enabled` | boolean | `true` | Master toggle — when false, no hooks execute |
| `hooksConfig.notifications` | boolean | `true` | Show visual indicators when hooks are executing |

---

## ide

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ide.enabled` | boolean | `false` | Enable IDE integration mode |

---

## billing

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `billing.overageStrategy` | enum | `"ask"` | How to handle quota exhaustion when AI credits available: `"ask"`, `"always"`, `"never"` |

---

## Annotated example

```jsonc
{
  // Model selection
  "model": {
    "name": "gemini-2.5-pro",
    "maxSessionTurns": -1
  },

  // UI
  "ui": {
    "theme": "Tokyo Night",
    "hideBanner": false,
    "inlineThinkingMode": "off"
  },

  // Tool behavior
  "general": {
    "defaultApprovalMode": "auto_edit",
    "checkpointing": true,
    "enableAutoUpdate": true,
    "topicUpdateNarration": true
  },

  // Context files
  "context": {
    "fileName": ["GEMINI.md", "AGENTS.md"],
    "fileFiltering": {
      "respectGitIgnore": true,
      "respectGeminiIgnore": true
    }
  },

  // Security
  "security": {
    "folderTrust": { "enabled": true },
    "environmentVariableRedaction": { "enabled": true }
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
    "autoConfigureMemory": true
  },

  // Experimental
  "experimental": {
    "memoryV2": true
  }
}
```

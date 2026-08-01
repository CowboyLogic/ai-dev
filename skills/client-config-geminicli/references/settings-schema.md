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
  - [mcp (global MCP settings)](#mcp-global-mcp-settings)
  - [security](#security)
  - [context](#context)
  - [mcpServers](#mcpservers)
  - [agents](#agents)
  - [privacy](#privacy)
  - [advanced](#advanced)
  - [experimental](#experimental)
  - [contextManagement](#contextmanagement)
  - [admin (enterprise lockdown)](#admin-enterprise-lockdown)
  - [skills](#skills)
  - [hooksConfig](#hooksconfig)
  - [ide](#ide)
  - [Annotated example](#annotated-example)

---

## general

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `general.vimMode` | boolean | `false` | Enable vim keybindings in the input editor |
| `general.defaultApprovalMode` | enum | `"default"` | Tool approval behavior (see below) — YOLO mode can only be enabled via CLI flag, not here |
| `general.preferredEditor` | enum | — | Editor for `/edit`: `vscode`, `vscodium`, `windsurf`, `cursor`, `zed`, `antigravity`, `sublimetext`, `lapce`, `nova`, `bbedit`, `vim`, `neovim`, `emacs`, `hx`, `emacsclient`, `micro`. Unset falls back to `$VISUAL`/`$EDITOR` |
| `general.openEditorInNewWindow` | boolean | `false` | Open VS Code-family editors in a new window |
| `general.devtools` | boolean | `false` | Enable DevTools inspector on launch |
| `general.enableAutoUpdate` | boolean | `true` | Automatically install CLI updates |
| `general.enableAutoUpdateNotification` | boolean | `true` | Enable update notification prompts |
| `general.enableNotifications` | boolean | `false` | Enable terminal run-event notifications |
| `general.notificationMethod` | enum | `"auto"` | How to send terminal notifications: `auto`, `osc9`, `osc777`, `bell` |
| `general.checkpointing.enabled` | boolean | `false` | Enable session checkpointing for recovery |
| `general.plan.enabled` | boolean | `true` | Enable Plan Mode (read-only safety) |
| `general.plan.directory` | string | system tmp | Directory for planning artifacts (custom dir needs a Plan Mode write policy) |
| `general.plan.modelRouting` | boolean | `true` | Switch Pro/Flash based on Plan Mode status |
| `general.sessionRetention.enabled` | boolean | `true` | Enable automatic session cleanup |
| `general.sessionRetention.maxAge` | string | `"30d"` | Delete chats older than this (e.g. `"7d"`, `"24h"`, `"1w"`) |
| `general.sessionRetention.maxCount` | number | — | Alternative: max sessions to keep (most recent) |
| `general.sessionRetention.minRetention` | string | `"1d"` | Minimum retention period (safety floor) |
| `general.topicUpdateNarration` | boolean | `true` | Topic & Update model for reduced chattiness |
| `general.retryFetchErrors` | boolean | `true` | Retry on fetch failed errors |
| `general.maxAttempts` | number | `10` | Max chat model attempts (cannot exceed 10) |
| `general.debugKeystrokeLogging` | boolean | `false` | Enable keystroke debug logging |
| `general.logRagSnippets` | boolean | `false` | Log full code-customization (RAG) retrieved snippets for debugging |

Also present at the settings.json root (not under a category): `policyPaths` (array, `[]`) and `adminPolicyPaths` (array, `[]`) — additional policy files/directories to load.

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
| `ui.customWittyPhrases` | array | `[]` | Custom phrases cycled through during loading (replaces defaults) |
| `ui.debugRainbow` | boolean | `false` | Debug rainbow rendering (rendering/perf bug diagnosis only) |
| `ui.footer.items` | array | — | Item IDs to display in the footer, rendered in order |
| `ui.footer.showLabels` | boolean | `true` | Show descriptive headers above footer items (e.g. `/model`) |
| `ui.collapseDrawerDuringApproval` | boolean | `true` | Collapse the UI drawer while a tool awaits confirmation |
| `ui.renderProcess` | boolean | `true` | Enable Ink render process for the UI |
| `ui.terminalBuffer` | boolean | `false` | Use the new terminal buffer architecture for rendering |
| `ui.accessibility.enableLoadingPhrases` | boolean | `true` | Deprecated — use `ui.loadingPhrases` instead |

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
        "background": { "primary": "#1e1e2e", "diff": { "added": "#2b3312", "removed": "#341212" } },
        "text": { "primary": "#cdd6f4", "secondary": "#a6adc8", "link": "#89b4fa", "accent": "#f5c2e7", "response": "#cdd6f4" },
        "status": { "success": "#a6e3a1", "warning": "#f9e2af", "error": "#f38ba8" },
        "border": { "default": "#585b70", "focused": "#89b4fa" },
        "ui": { "comment": "#6c7086", "symbol": "#94e2d5", "gradient": ["#cc241d", "#d65d0e", "#d79921"] }
      }
    },
    "theme": "my-theme"
  }
}
```

`name` and `type: "custom"` are required; all color sub-properties are optional but `background.primary`, `text.primary`/`secondary`, and the accent/status colors are recommended. Values accept hex codes or CSS color names.

`ui.theme` can also point to a path to a theme JSON file (same structure) — for safety, the CLI only loads theme files located within the home directory.

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
| `model.summarizeToolOutput` | object | — | Per-tool token budgets for summarizing tool output, e.g. `{"run_shell_command": {"tokenBudget": 2000}}`. Only `run_shell_command` supports this currently |
| `model.compressionThreshold` | number | `0.5` | Fraction of context usage that triggers compression |
| `model.disableLoopDetection` | boolean | `false` | Disable infinite loop detection |
| `model.skipNextSpeakerCheck` | boolean | `true` | Skip next speaker validation check |

**Override model per-session:** `GEMINI_MODEL` env var or `--model` CLI flag.

> `modelConfigs` (aliases/overrides/model routing chains/fallback policy) is a large internal registry for advanced model-tier customization — see the full configuration reference if you need to override generation params (temperature, thinking budget) per alias or define custom fallback chains. Most users never touch this.

---

## tools

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tools.sandbox` | string | — | Legacy full-process sandbox: boolean-like enable/disable, a sandbox profile path, or a command (`"docker"`, `"podman"`, `"lxc"`, `"windows-native"`) |
| `tools.sandboxAllowedPaths` | array | `[]` | Additional paths the sandbox may access |
| `tools.sandboxNetworkAccess` | boolean | `false` | Allow network inside sandbox |
| `tools.shell.enableInteractiveShell` | boolean | `true` | Use node-pty for interactive shell (child_process fallback) |
| `tools.shell.backgroundCompletionBehavior` | enum | `"silent"` | On background command finish: `silent`, `inject` (return output to agent), `notify` (brief chat message) |
| `tools.shell.pager` | string | `"cat"` | Pager command for shell output |
| `tools.shell.showColor` | boolean | `true` | Show color in shell output |
| `tools.shell.inactivityTimeout` | number | `300` | Max seconds without shell output before timeout |
| `tools.shell.enableShellOutputEfficiency` | boolean | `true` | Enable shell output efficiency optimizations |
| `tools.core` | array | — | Allowlist restricting the set of built-in tools |
| `tools.allowed` | array | — | Tool names that bypass the confirmation dialog (e.g. `["run_shell_command(git)"]`) |
| `tools.confirmationRequired` | array | — | Tool names that always require confirmation — takes precedence over `allowed`/`core` |
| `tools.exclude` | array | — | Tool names to exclude from discovery |
| `tools.discoveryCommand` | string | — | Command to discover additional tools |
| `tools.callCommand` | string | — | Custom shell command to invoke discovered tools (reads JSON args on stdin, emits JSON on stdout) |
| `tools.useRipgrep` | boolean | `true` | Use ripgrep for faster file content search |
| `tools.truncateToolOutputThreshold` | number | `40000` | Max chars for tool output before truncation (0 or negative = disable) |
| `tools.disableLLMCorrection` | boolean | `true` | Disable LLM-based error correction for edit tools |

> Field names changed from older docs: use `tools.allowed` / `tools.exclude`, not `allowedTools` / `excludeTools`.

---

## mcp (global MCP settings)

Distinct from the per-server `mcpServers` object below — these control discovery/execution rules for *all* servers.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mcp.serverCommand` | string | — | Global command to start an MCP server |
| `mcp.allowed` | array | — | Only connect to servers in this list (matches `mcpServers` keys) |
| `mcp.excluded` | array | — | Never connect to servers in this list |

---

## security

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `security.folderTrust.enabled` | boolean | `true` | Require explicit folder trust before loading project config |
| `security.environmentVariableRedaction.enabled` | boolean | `false` | Redact env vars that may contain secrets |
| `security.environmentVariableRedaction.allowed` | array | `[]` | Env vars always allowed (bypass redaction) |
| `security.environmentVariableRedaction.blocked` | array | `[]` | Env vars always redacted |
| `security.toolSandboxing` | boolean | `false` | Tool-level sandboxing (isolates individual tools) |
| `security.enableConseca` | boolean | `false` | Context-aware LLM security checker |
| `security.disableYoloMode` | boolean | `false` | Prevent YOLO mode even if `--yolo` flag is passed |
| `security.disableAlwaysAllow` | boolean | `false` | Disable "Always allow" option in confirmation dialogs |
| `security.enablePermanentToolApproval` | boolean | `false` | Enable "Allow for all future sessions" option |
| `security.autoAddToPolicyByDefault` | boolean | `false` | Make "Allow for all future sessions" the default for low-risk tools |
| `security.blockGitExtensions` | boolean | `false` | Block installing extensions from Git |
| `security.allowedExtensions` | array | `[]` | Regex patterns for allowed extensions (overrides `blockGitExtensions`) |
| `security.auth.selectedType` | string | — | Currently selected authentication type |
| `security.auth.enforcedType` | string | — | Required auth type — mismatch prompts re-auth |
| `security.auth.useExternal` | boolean | — | Use an external authentication flow |

> `security.authType` from older docs no longer exists — use `security.auth.selectedType` / `security.auth.enforcedType`.

**Trusted folders** are stored in `~/.gemini/trustedFolders.json` (managed by CLI — use `/permissions` to modify).

---

## context

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `context.fileName` | string \| array | `["GEMINI.md"]` | Context file name(s) to scan for |
| `context.importFormat` | string | — | Format to use when importing memory |
| `context.includeDirectoryTree` | boolean | `true` | Include the cwd directory tree in the initial model request |
| `context.discoveryMaxDirs` | number | `200` | Max directories to search for memory files |
| `context.memoryBoundaryMarkers` | array | `[".git"]` | Names marking the boundary for GEMINI.md upward discovery; empty array disables parent traversal |
| `context.includeDirectories` | array | `[]` | Additional directories included in workspace context (missing dirs skipped with a warning) |
| `context.loadMemoryFromIncludeDirectories` | boolean | `false` | When true, `/memory reload` also scans include directories |
| `context.fileFiltering.respectGitIgnore` | boolean | `true` | Skip gitignored files |
| `context.fileFiltering.respectGeminiIgnore` | boolean | `true` | Skip `.geminiignore`-listed files |
| `context.fileFiltering.enableFileWatcher` | boolean | `false` | Enable file watcher updates for `@` suggestions (experimental) |
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
| `agents.overrides` | object | `{}` | Per-agent overrides — disable an agent, set a custom model config or run config |
| `agents.browser.sessionMode` | enum | `"persistent"` | `persistent`, `isolated`, or `existing` |
| `agents.browser.headless` | boolean | `false` | Run browser in headless mode |
| `agents.browser.profilePath` | string | — | Browser profile directory for session persistence |
| `agents.browser.visualModel` | string | — | Model for the visual agent's `analyze_screenshot` tool (enables the tool when set) |
| `agents.browser.allowedDomains` | array | `["github.com", "*.google.com", "localhost"]` | Allowed domains for the browser agent |
| `agents.browser.disableUserInput` | boolean | `true` | Disable user input on the browser window during automation |
| `agents.browser.maxActionsPerTask` | number | `100` | Hard cap on tool calls per browser task |
| `agents.browser.confirmSensitiveActions` | boolean | `false` | Require manual confirmation for sensitive browser actions (e.g. `fill_form`, `evaluate_script`) |
| `agents.browser.blockFileUploads` | boolean | `false` | Hard-block file upload requests from browser agent |

---

## privacy

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `privacy.usageStatisticsEnabled` | boolean | `true` | Enable collection of usage statistics |

---

## advanced

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `advanced.autoConfigureMemory` | boolean | `true` | Auto-configure Node.js `--max-old-space-size` (user settings only — workspace override ignored) |
| `advanced.dnsResolutionOrder` | string | — | DNS resolution order |
| `advanced.excludedEnvVars` | array | `["DEBUG", "DEBUG_MODE"]` | Env vars excluded from project context |
| `advanced.ignoreLocalEnv` | boolean | `false` | Ignore generic `.env` files in the project directory |
| `advanced.bugCommand` | object | — | Configuration for the bug report command |

**Billing:** `billing.overageStrategy` (enum, `"ask"`) — `ask`/`always`/`never` when AI credits are available. `billing.vertexAi.requestType` (`dedicated`/`shared`) and `billing.vertexAi.sharedRequestType` (`priority`/`flex`) set Vertex AI request headers.

---

## experimental

All experimental features default to `false` unless noted.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `experimental.voiceMode` | boolean | `false` | Enable voice dictation and commands (`/voice`, `/voice model`) |
| `experimental.voice.activationMode` | enum | `"push-to-talk"` | `push-to-talk` or `toggle` |
| `experimental.voice.backend` | enum | `"gemini-live"` | `gemini-live` (sends audio to Google Cloud) or `whisper` (local) |
| `experimental.voice.whisperModel` | enum | `"ggml-base.en.bin"` | Whisper model for local transcription |
| `experimental.voice.stopGracePeriodMs` | number | `4000` | Ms to wait for final transcription after stopping |
| `experimental.gemma` | boolean | `true` | Enable access to Gemma 4 models via Gemini API |
| `experimental.gemmaModelRouter.enabled` | boolean | `false` | Route requests to local Gemma via LiteRT-LM shim |
| `experimental.gemmaModelRouter.autoStartServer` | boolean | `false` | Auto-start LiteRT-LM server on CLI start |
| `experimental.gemmaModelRouter.binaryPath` | string | `""` | Custom path to LiteRT-LM binary (default `~/.gemini/bin/litert/`) |
| `experimental.gemmaModelRouter.classifier.host` | string | `"http://localhost:9379"` | Classifier host |
| `experimental.gemmaModelRouter.classifier.model` | string | `"gemma3-1b-gpu-custom"` | Classifier model |
| `experimental.autoMemory` | boolean | `false` | Auto-extract memory patches/skills from past sessions as `.patch` files under `<projectMemoryDir>/.inbox/<kind>/`; nothing applied until reviewed via `/memory inbox` |
| `experimental.enableAgents` | boolean | `true` | Enable local and remote subagents |
| `experimental.generalistProfile` | boolean | `false` | Generalist agent profile for general coding tasks |
| `experimental.powerUserProfile` | boolean | `false` | Less cache-friendly variant of the generalist profile |
| `experimental.contextManagement` | boolean | `false` | Enable context management logic (see `contextManagement` section) |
| `experimental.worktrees` | boolean | `false` | Automated Git worktree management for parallel work |
| `experimental.modelSteering` | boolean | `false` | Model steering hints during tool execution |
| `experimental.directWebFetch` | boolean | `false` | Web fetch bypassing LLM summarization |
| `experimental.dynamicModelConfiguration` | boolean | `false` | Enable dynamic model config (definitions/resolutions/chains) via settings |
| `experimental.extensionManagement` | boolean | `true` | Enable extension management features |
| `experimental.extensionConfig` | boolean | `true` | Enable requesting/fetching extension settings |
| `experimental.extensionRegistry` | boolean | `false` | Enable extension registry explore UI |
| `experimental.extensionRegistryURI` | string | `"https://geminicli.com/extensions.json"` | Extension registry URI (web URL or local path) |
| `experimental.extensionReloading` | boolean | `false` | Enable extension load/unload within a running session |
| `experimental.taskTracker` | boolean | `false` | Enable task tracker tools |
| `experimental.stressTestProfile` | boolean | `false` | Lower token limits for testing garbage collection/distillation |
| `experimental.useOSC52Paste` | boolean | `false` | OSC 52 paste (more robust for remote terminals) |
| `experimental.useOSC52Copy` | boolean | `false` | OSC 52 copy |
| `experimental.topicUpdateNarration` | boolean | `false` | Deprecated — use `general.topicUpdateNarration` |

> `experimental.memoryV2` no longer appears in upstream docs. Prompt-driven memory editing (just tell the agent to remember something) is the current default; there is no legacy-tool toggle documented.

---

## contextManagement

Tunables for the automatic history/tool-output compression pipeline (all `number`, all require restart):

| Field | Default | Description |
|-------|---------|-------------|
| `contextManagement.historyWindow.maxTokens` | `150000` | Tokens allowed before compression triggers |
| `contextManagement.historyWindow.retainedTokens` | `40000` | Tokens always retained |
| `contextManagement.messageLimits.normalMaxTokens` | `2500` | Target budget for a normal turn |
| `contextManagement.messageLimits.retainedMaxTokens` | `12000` | Max tokens a single turn can consume before truncation |
| `contextManagement.messageLimits.normalizationHeadRatio` | `0.25` | Ratio of tokens retained from the start of a truncated message |
| `contextManagement.tools.distillation.maxOutputTokens` | `10000` | Max tokens shown when truncating large tool outputs |
| `contextManagement.tools.distillation.summarizationThresholdTokens` | `20000` | Threshold above which truncated tool output is LLM-summarized |
| `contextManagement.tools.outputMasking.protectionThresholdTokens` | `50000` | Min tokens protected from masking (most recent outputs) |
| `contextManagement.tools.outputMasking.minPrunableThresholdTokens` | `30000` | Min prunable tokens to trigger a masking pass |
| `contextManagement.tools.outputMasking.protectLatestTurn` | `true` (boolean) | Never mask the absolute latest turn |

---

## admin (enterprise lockdown)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `admin.secureModeEnabled` | boolean | `false` | Disallow YOLO mode and "Always allow" |
| `admin.extensions.enabled` | boolean | `true` | If `false`, disallow installing/using extensions |
| `admin.mcp.enabled` | boolean | `true` | If `false`, disallow MCP servers |
| `admin.mcp.config` | object | `{}` | Admin-configured MCP servers (allowlist) |
| `admin.mcp.requiredConfig` | object | `{}` | Admin-required MCP servers, always injected |
| `admin.skills.enabled` | boolean | `true` | If `false`, disallow agent skills |

---

## skills

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `skills.enabled` | boolean | `true` | Enable Agent Skills |
| `skills.disabled` | array | `[]` | List of disabled skill names |

---

## hooksConfig

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `hooksConfig.enabled` | boolean | `true` | Master toggle — when false, no hooks execute |
| `hooksConfig.disabled` | array | `[]` | Hook names (commands) disabled even if configured |
| `hooksConfig.notifications` | boolean | `true` | Show visual indicators when hooks are executing |

See `references/hooks.md` for the `hooks` object itself.

---

## ide

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `ide.enabled` | boolean | `false` | Enable IDE integration mode |
| `ide.hasSeenNudge` | boolean | `false` | Whether the user has seen the IDE integration nudge |

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
    "autoMemory": true
  }
}
```

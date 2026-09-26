# settings.json Full Schema Reference

Schema URL: `https://json.schemastore.org/claude-code-settings.json`

Upstream: `https://code.claude.com/docs/en/settings-reference.md` (every key, with scope/type/default) and `https://code.claude.com/docs/en/settings.md` (files and precedence).

**Scope labels used below** (from the upstream "Scope" field): *Any file* = user, project, local, managed, `--settings`. *User or managed* = ignored in project/local settings (a repository can't set it for you). *Managed* = read only from managed sources. *Global config* = `~/.claude.json`, not `settings.json`.

## Table of Contents

- [Settings files and precedence](#settings-files-and-precedence)
- [Model & Performance](#model--performance)
- [Auto Mode](#auto-mode)
- [UI & Display](#ui--display)
- [Memory, Context & Session](#memory-context--session)
- [Environment & Integration](#environment--integration)
- [Plugins & Skills](#plugins--skills)
- [Subagents & Sessions](#subagents--sessions)
- [Sandbox](#sandbox)
- [Attribution & Git](#attribution--git)
- [Worktree settings](#worktree-settings)
- [Misc / Enterprise](#misc--enterprise)
- [Deprecated and removed keys](#deprecated-and-removed-keys)
- [Global config (~/.claude.json only)](#global-config-claudejson-only)

---

## Settings files and precedence

| Scope | File |
| --- | --- |
| User | `~/.claude/settings.json` (or `$CLAUDE_CONFIG_DIR/settings.json`) |
| Shared project | `.claude/settings.json` |
| Project local | `.claude/settings.local.json` (loaded from the git repo root; Claude Code adds it to global git excludes when it creates it) |
| Managed | `managed-settings.json` + optional `managed-settings.d/*.json` in the system dir, MDM (macOS `com.anthropic.claudecode` profile, Windows `HKLM\SOFTWARE\Policies\ClaudeCode`), or server-managed settings from the claude.ai console |

Managed system dirs: macOS `/Library/Application Support/ClaudeCode/`, Linux/WSL `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\` (the legacy `C:\ProgramData\ClaudeCode\` path is not read).

**Precedence (highest first)**: managed → command-line args (incl. `--settings`) → local project → shared project → user. Environment variables are not a level; each env-var/key pair has its own rule (e.g. exported `ANTHROPIC_MODEL` beats `model` from any file).

**Lists merge** across files (e.g. `permissions.allow`), except: `fallbackModel` (highest file wins whole chain), `modelPicker` (whole value from highest of managed/`--settings`/user), managed `availableModels` (applied as-is), and `modelSettings` (resolved per model).

**Exceptions to managed precedence** (a stricter value from a lower scope wins): `disableClaudeAiConnectors: true`, `enableArtifact: false` / `disableArtifact: true`, `isolatePeerMachines: true`, project/local `remoteControlAtStartup: false`, a stricter project/local `crossSessionInbound`, `false` for `useAutoModeDuringPlan`/`syncClaudeAiSkills`/`syncClaudeAiPlugins` (not from `.claude/settings.json`), and the lowest `maxEffortLevel` from any scope.

**Within the managed tier** (default `managedSourcesBehavior: "first-wins"`): remote (server-managed / Claude apps gateway) → MDM (plist/HKLM) → managed files (`managed-settings.d/*.json` merged with `managed-settings.json`) → HKCU (Windows, only if nothing above delivers a policy key).

---

## Model & Performance

| Key | Description | Example |
| --- | --- | --- |
| `model` | Model every new session starts with (`--model` and `ANTHROPIC_MODEL` override it) | `"claude-sonnet-5"` |
| `effortLevel` | Default effort for models with no saved level: `"low"` \| `"medium"` \| `"high"` \| `"xhigh"`. Since v2.1.251 `/effort` saves per-model levels under `modelSettings` instead of writing this key; in user settings Opus 5.5 and later models ignore it | `"high"` |
| `modelSettings` | Per-model `effortLevel` and/or `maxEffortLevel` (v2.1.251+) | `{"claude-sonnet-4-6": {"effortLevel": "high"}}` |
| `maxEffortLevel` | Cap effort: `"low"`\|`"medium"`\|`"high"`\|`"xhigh"`\|`"max"` (`"max"` = no cap). Lowest cap across scopes wins. A cap below `xhigh` disables ultracode (v2.1.267+) | `"medium"` |
| `ultracode` | Start sessions with ultracode on (runs at `xhigh`). Read from settings but never written by Claude Code; `/effort ultracode` is per-session | `true` |
| `alwaysThinkingEnabled` | Extended thinking by default (unset = on for supporting models) | `true` |
| `showThinkingSummaries` | Show thinking block summaries (default `false`) | `true` |
| `availableModels` | Restrict model picker options; managed list is applied as-is | `["sonnet", "haiku"]` |
| `enforceAvailableModels` | Extend `availableModels` to the Default option when the default isn't allowlisted (default `false`) | `true` |
| `modelOverrides` | Map Anthropic model IDs to provider IDs (Bedrock ARNs etc.) | `{"claude-opus-4-6": "arn:aws:bedrock:..."}` |
| `modelPicker` | *(User or managed)* Custom `/model` picker rows: `{options: [{model, label?, description?}], replaceBuiltInOptions?}` (v2.1.242+) | see upstream |
| `modelPricing` | *(Managed only)* Contracted rates for cost display: `{multiplier?, overrides?}` (v2.1.242+) | see upstream |
| `outputStyle` | Built-in or custom output style name | `"Explanatory"` |
| `agent` | Run main thread as named subagent | `"code-reviewer"` |
| `advisorModel` | Model for the advisor tool: `"fable"`\|`"opus"`\|`"sonnet"` or a full ID (unset = advisor off) | `"opus"` |
| `fallbackModel` | Ordered fallback chain when primary is overloaded/unavailable; `"default"` expands to the default model. At most 3 distinct models kept; doesn't merge across files | `["claude-sonnet-5", "claude-haiku-4-5"]` |
| `switchModelsOnFlag` | Default `true`. Auto-switch to fallback when a safety classifier flags a request | `false` |
| `fastMode` | Turn on fast mode where available; `/fast` writes this | `true` |
| `fastModePerSessionOptIn` | Fast mode resets each session (default `false`) | `true` |
| `promptCacheTtl` | Prompt-cache lifetime for the main conversation: `"5m"` \| `"1h"` (v2.1.242+) | `"1h"` |
| `subagentPromptCacheTtl` | Same, for subagents, workflows, and background helpers (v2.1.242+) | `"5m"` |

---

## Auto Mode

```json
{
  "autoMode": {
    "environment": [
      "Organization: Acme Corp. Primary use: software development",
      "Source control: github.com/acme-corp",
      "Trusted internal domains: *.internal.acme.com"
    ],
    "allow": ["$defaults", "Deploying to staging is allowed: isolated from prod"],
    "soft_deny": ["$defaults", "Never run DB migrations outside migrations CLI"],
    "hard_deny": ["$defaults"],
    "classifyAllShell": false
  },
  "disableAutoMode": "disable",
  "useAutoModeDuringPlan": false,
  "skipAutoPermissionPrompt": true
}
```

**Important**: `autoMode` holds `environment`, `allow`, `soft_deny`, and `hard_deny` arrays of prose rules. Leaving `"$defaults"` out of an array **replaces** the built-in rules for that array; including it keeps them at that position. When several readable files set the same array, entries are concatenated. `autoMode` is *User or managed* (also `--settings`) — ignored in project/local settings.

- `autoMode.classifyAllShell` (default `false`): send every Bash/PowerShell command through the classifier; by default only allow rules that could run arbitrary code (`Bash(*)`, `Bash(python *)` etc.) are suspended in auto mode.
- `disableAutoMode: "disable"` — remove auto mode from the `Shift+Tab` cycle; also accepted as `permissions.disableAutoMode`.
- `useAutoModeDuringPlan` (default `true`, *User, local, or managed*): classifier reviews shell commands in plan mode.
- `skipAutoPermissionPrompt` (*User or managed*): skip the one-time auto mode notice.

Inspect your config:

```bash
claude auto-mode defaults   # built-in rules
claude auto-mode config     # effective config (yours + defaults)
claude auto-mode critique   # AI review of your custom rules
```

---

## UI & Display

| Key | Description | Example |
| --- | --- | --- |
| `language` | Response language (not validated) | `"japanese"` |
| `theme` | `"auto"`\|`"dark"` (default)\|`"light"`\|`"dark-daltonized"`\|`"light-daltonized"`\|`"dark-ansi"`\|`"light-ansi"`\|`"custom:<slug>"`\|`"custom:<plugin-name>:<slug>"` | `"dark"` |
| `viewMode` | Starting transcript view: `"default"`\|`"verbose"`\|`"focus"` (focus needs fullscreen renderer) | `"focus"` |
| `tui` | Renderer: `"fullscreen"`\|`"default"` (unset = Claude Code picks) | `"fullscreen"` |
| `verbose` | Full tool output (default `false`) | `true` |
| `axScreenReader` | Screen-reader friendly flat output; forces classic renderer | `true` |
| `editorMode` | `"normal"` (default) \| `"vim"` | `"vim"` |
| `vimInsertModeRemaps` | *(User or managed)* Two-key INSERT sequences → `"<Esc>"` | `{"jj": "<Esc>"}` |
| `prefersReducedMotion` | Reduce UI animations (default `false`) | `true` |
| `spinnerTipsEnabled` | Show tips in spinner (default `true`) | `false` |
| `spinnerTipsOverride` | `{tips, tipsFile, label, excludeDefault}`; objects/`tipsFile`/`label`/`excludeDefault` only honored from user/`--settings`/managed | `{"excludeDefault": true, "tips": ["Use tool X"]}` |
| `spinnerVerbs` | `{mode: "append"\|"replace", verbs: [...]}` | `{"mode": "append", "verbs": ["Pondering"]}` |
| `statusLine` | `{type: "command", command, padding?, refreshInterval? (seconds, min 1), hideVimModeIndicator?}` | `{"type": "command", "command": "~/.claude/statusline.sh"}` |
| `subagentStatusLine` | `{type: "command", command}` — rewrite subagent task rows (JSON on stdin, `{"id","content"}` lines out) | `{"type": "command", "command": "~/.claude/subagent-rows.sh"}` |
| `showClearContextOnPlanAccept` | Show clear-context option on plan accept (default `false`) | `true` |
| `showTurnDuration` | Turn duration after responses (default `true`) | `false` |
| `timeFormat` | `"auto"` (default)\|`"12-hour"`\|`"24-hour"`\|`"24-hour-utc"` or a strftime pattern (v2.1.257+) | `"24-hour"` |
| `timeZone` | IANA zone for displayed times; ignored with `"24-hour-utc"` (v2.1.257+) | `"Europe/Dublin"` |
| `terminalProgressBarEnabled` | Terminal progress bar (default `true`) | `false` |
| `terminalTitleFromRename` | Use `/rename` name as tab title (default `true`) | `false` |
| `autoScrollEnabled` | Follow new output in fullscreen (default `true`) | `false` |
| `wheelScrollAccelerationEnabled` | Accelerate mouse-wheel scroll in fullscreen (default `true`) | `false` |
| `syntaxHighlightingDisabled` | Disable syntax highlighting (default `false`) | `true` |
| `emojiCompletionEnabled` | `:shortcode:` emoji autocomplete (default `true`) | `false` |
| `promptSuggestionEnabled` | Grayed-out prompt suggestions (default `true`) | `false` |
| `spellcheck` | *(User or managed)* `{enabled, checker: "aspell"\|"hunspell"\|"ispell"\|"auto", language, color}` (v2.1.235+) | `{"enabled": true}` |
| `teammateMode` | Agent-team display: `"in-process"` (default)\|`"auto"`\|`"tmux"`\|`"iterm2"` | `"auto"` |
| `respondToBashCommands` | Claude responds after an input-box `!` command (default `true`) | `false` |
| `askUserQuestionTimeout` | *(User or managed)* `"60s"`\|`"5m"`\|`"10m"`\|`"never"` (default) | `"5m"` |
| `dialogExpiry` | *(User or managed)* Deadline for dialogs forwarded to remote clients: `"60s"`\|`"5m"` (default)\|`"10m"`\|`"never"` | `"10m"` |
| `autoContinueAtUsageLimit` | *(User or managed)* Continue automatically after a claude.ai usage-limit reset (default `true`, v2.1.234+) | `false` |
| `footerLinksRegexes` | *(User or managed)* Footer badges: `[{type: "regex", pattern, url, label?}]` with `{name}` named-capture substitution | `[{"type": "regex", "pattern": "\\b(?<key>PROJ-\\d+)\\b", "url": "https://issues.example.com/browse/{key}", "label": "{key}"}]` |
| `companyAnnouncements` | Startup messages (cycled randomly) | `["Welcome! See docs.acme.com"]` |

---

## Memory, Context & Session

| Key | Description | Example |
| --- | --- | --- |
| `autoMemoryEnabled` | Auto memory read/write (default `true`) | `false` |
| `autoMemoryDirectory` | Absolute or `~/` path (default `~/.claude/projects/<project>/memory/`) | `"~/my-memory-dir"` |
| `autoCompactEnabled` | Auto-compact near context limit (default `true`) | `false` |
| `autoCompactWindow` | Tokens before auto-compact, `100000`–`1000000`, capped at model window | `400000` |
| `bashOutputMaxChars` | Inline Bash/PowerShell output limit, clamped `4000`–`128000` (default 30,000; v2.1.261+) | `60000` |
| `claudeMdExcludes` | Globs/absolute paths of CLAUDE.md files to skip (not managed memory) | `["**/vendor/**/CLAUDE.md"]` |
| `fileCheckpointingEnabled` | Snapshot files so `/rewind` can restore them (default `true`) | `false` |
| `plansDirectory` | Plan file dir, relative to project root (default `~/.claude/plans`) | `"./plans"` |
| `cleanupPeriodDays` | Delete session transcripts/app data older than N days (default `30`, min `1`) | `20` |
| `desktopSessionCleanupPeriodDays` | *(User or managed)* Age limit for Desktop/Cowork transcripts (default `0` = none; v2.1.248+) | `60` |
| `respectGitignore` | `@` file picker respects .gitignore (default `true`) | `false` |
| `includeGitInstructions` | Built-in git workflow in system prompt (default `true`) | `false` |
| `skillListingBudgetFraction` | Fraction of context for skill listing, `>0`–`1` (default `0.01`) | `0.02` |
| `skillListingMaxDescChars` | Per-skill description cap in listing (default `1536`) | `2048` |
| `skillOverrides` | Per-skill visibility `"on"`\|`"name-only"`\|`"user-invocable-only"`\|`"off"`; `/skills` writes it to `.claude/settings.local.json` | `{"deploy": "off"}` |
| `disableWorkflows` | Disable dynamic workflows (default `false`) | `true` |
| `enableWorkflows` | Personal on/off for dynamic workflows (unset = on, except Pro plan) | `true` |
| `workflowKeywordTriggerEnabled` | Typing `ultracode` triggers a workflow (default `true`) | `false` |
| `workflowSizeGuideline` | `"unrestricted"`\|`"small"`\|`"medium"`\|`"large"` (default `"medium"`, or `"small"` on Pro with v2.1.271+) | `"small"` |
| `autoUpdatesChannel` | `"latest"` (default) \| `"stable"` (~1 week old, skips major regressions) | `"stable"` |
| `minimumVersion` | Floor for auto-updates | `"2.1.100"` |
| `feedbackSurveyRate` | Survey probability `0`–`1` | `0` |
| `feedbackDrafts` | *(User or managed)* Claude-drafted feedback: `"notify"` (default)\|`"quiet"`\|`"off"` | `"off"` |

---

## Environment & Integration

```json
{
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "NODE_ENV": "development"
  }
}
```

| Key | Description | Example |
| --- | --- | --- |
| `env` | Env vars applied every session (string values) | `{"FOO": "bar"}` |
| `apiKeyHelper` | Shell command that outputs the auth value | `"/bin/gen_key.sh"` |
| `awsAuthRefresh` | Command that refreshes AWS credentials | `"aws sso login --profile myprofile"` |
| `awsCredentialExport` | Command that outputs AWS credentials JSON | `"/bin/gen_aws.sh"` |
| `gcpAuthRefresh` | Command that refreshes GCP ADC | `"gcloud auth application-default login"` |
| `otelHeadersHelper` | Script for dynamic OpenTelemetry headers | `"/bin/gen_otel.sh"` |
| `forceLoginMethod` | `"claudeai"` \| `"console"` \| `"gateway"` (`"gateway"` only from an on-machine managed source) | `"claudeai"` |
| `forceLoginOrgUUID` | UUID string or array; only managed sources enforce it | `"uuid-here"` |
| `forceLoginGatewayUrl` | *(Managed only, on-machine)* Pre-fill/lock the `/login` Cloud gateway URL | `"https://claude-gateway.example.com"` |
| `gatewayInternalNetworks` | *(Managed only, on-machine)* Up to four public IPv4 CIDRs where `/login` accepts a gateway (v2.1.268+) | `["203.0.113.0/24"]` |
| `fileSuggestion` | Custom `@` autocomplete: `{type: "command", command}` | `{"type": "command", "command": "~/.claude/suggest.sh"}` |
| `defaultShell` | `"bash"` (default) \| `"powershell"` | `"powershell"` |
| `voice` | `{enabled, mode: "hold"\|"tap", autoSubmit}`; `mode` defaults to `"hold"`; `autoSubmit` applies in hold mode only. `/voice` writes it | `{"enabled": true, "mode": "tap"}` |
| `skipWebFetchPreflight` | Skip the WebFetch domain safety check | `true` |
| `sshConfigs` | *(User or managed)* Desktop SSH connections `{id, name, sshHost, sshPort?, sshIdentityFile?}` | `[{"id": "dev-vm", "name": "Dev VM", "sshHost": "user@dev.example.com"}]` |
| `prUrlTemplate` | PR badge URL with `{host}`, `{owner}`, `{repo}`, `{number}`, `{url}` | `"https://reviews.example.com/{owner}/{repo}/pull/{number}"` |
| `processWrapper` | *(User or managed)* Launcher prefix for background processes | `"/opt/corp/launcher --profile claude"` |
| `disableClaudeAiConnectors` | Disable claude.ai MCP connectors (see `references/mcp.md`) | `true` |
| `remote.defaultEnvironmentId` | Default cloud environment (`env_...` or `ccpool_...`) | `"env_0123abcd"` |
| `remoteControlAtStartup` | Auto-connect Remote Control at session start | `false` |
| `disableRemoteControl` | Disable Remote Control entirely (default `false`) | `true` |
| `agentPushNotifEnabled` | Proactive push notifications via Remote Control (default `false`) | `true` |
| `inputNeededNotifEnabled` | Push when a prompt/question needs input (default `false`) | `true` |
| `preferredNotifChannel` | `"auto"` (default)\|`"terminal_bell"`\|`"iterm2"`\|`"iterm2_with_bell"`\|`"kitty"`\|`"ghostty"`\|`"notifications_disabled"` | `"terminal_bell"` |

---

## Plugins & Skills

Plugins extend Claude Code with skills, agents, hooks, and MCP servers. Manage via `/plugin`.

```json
{
  "enabledPlugins": {
    "formatter@acme-tools": true,
    "experimental@personal": false
  },
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": { "source": "github", "repo": "acme-corp/claude-plugins" },
      "autoUpdate": true
    }
  }
}
```

| Key | Description | Example |
| --- | --- | --- |
| `enabledPlugins` | `"plugin@marketplace": bool` (unset = plugin's `defaultEnabled`) | `{"formatter@acme-tools": true}` |
| `extraKnownMarketplaces` | Marketplace name → `{source, autoUpdate?}`; repo entries honored only after workspace trust | see above |
| `pluginConfigs` | *(User or managed)* Non-sensitive `userConfig` answers, keyed by plugin ID; Claude Code writes it | — |
| `syncClaudeAiSkills` | *(User, local, managed)* `false` stops syncing claude.ai skills to `~/.claude/skills/synced/` (`true` = unset) | `false` |
| `syncClaudeAiPlugins` | *(User, local, managed)* `false` stops syncing claude.ai plugins to `~/.claude/plugins/synced/` (v2.1.273+) | `false` |
| `disableBundledSkills` | Hide bundled skills/workflows from the model | `true` |
| `disableSkillShellExecution` | Disable inline `!` shell in skills | `true` |
| `pluginTrustMessage` | *(Managed only)* Extra text on plugin trust dialog | `"Vetted by IT"` |
| `allowedChannelPlugins` | *(Managed only)* Channel plugin allowlist: `{marketplace, plugin}` or `"plugin@marketplace"` | `["telegram@claude-plugins-official"]` |
| `channelsEnabled` | *(Managed only)* Allow channels on Team/Enterprise | `true` |
| `strictKnownMarketplaces` | *(Managed only)* Marketplace source allowlist; `[]` = full lockdown (incl. official) | `[{"source": "github", "repo": "acme/plugins"}]` |
| `blockedMarketplaces` | *(Managed only)* Marketplace source denylist | `[{"source": "github", "repo": "untrusted/plugins"}]` |
| `pluginSuggestionMarketplaces` | *(Managed only)* Marketplaces allowed to surface plugin suggestions | `["acme-corp-plugins"]` |
| `strictPluginOnlyCustomization` | *(Managed only)* `true` or subset of `["skills", "agents", "hooks", "mcp"]` — only plugins/managed may supply those | `["skills", "hooks"]` |
| `disableCommandPluginSources` | *(Managed only)* Block `command` plugin sources and marketplace `headersHelper` commands (unset follows `allowManagedHooksOnly`) | `true` |
| `disableSideloadFlags` | *(Managed only)* Reject `--plugin-dir`, `--plugin-url`, `--agents`, `--mcp-config` | `true` |

---

## Subagents & Sessions

Subagent Markdown files define specialized assistants. Locations by priority (highest first):

| Location | Scope |
| --- | --- |
| Managed settings | Organization-wide |
| `--agents` CLI flag (JSON) | Current session |
| `.claude/agents/` | Current project |
| `~/.claude/agents/` | All your projects |
| Plugin `agents/` directory | Where plugin is enabled |

See `https://code.claude.com/docs/en/sub-agents.md` for the file format.

| Key | Description | Example |
| --- | --- | --- |
| `disableAgentView` | Turn off background agents/agent view | `true` |
| `crossSessionInbound` | Messages from your other sessions: `"accept"`\|`"hold"`\|`"refuse"` (v2.1.224+) | `"hold"` |
| `isolatePeerMachines` | Require approval before `SendMessage` reaches sessions on other machines; `true` from any scope wins | `true` |

---

## Sandbox

> [!NOTE]
> OS-level isolation for Bash, PowerShell, and Monitor commands and their children. macOS, Linux, WSL2 only.

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "failIfUnavailable": false,
    "excludedCommands": ["docker *"],
    "allowUnsandboxedCommands": true,
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyWrite": ["/etc", "/usr/local/bin"],
      "denyRead": ["~/.aws/credentials"],
      "allowRead": ["."]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"],
      "deniedDomains": ["sensitive.internal.com"],
      "allowUnixSockets": ["/var/run/docker.sock"],
      "allowAllUnixSockets": false,
      "allowLocalBinding": true,
      "httpProxyPort": 8080,
      "socksProxyPort": 8081
    }
  }
}
```

**Defaults**: `enabled` `false`, `autoAllowBashIfSandboxed` `true`, `allowUnsandboxedCommands` `true`, `failIfUnavailable` `false`.

**Path prefixes**: `/` = absolute, `~/` = home-relative, `./` or no prefix = project/user-relative.

**Additional sandbox keys:**

| Key | Description | Example |
| --- | --- | --- |
| `network.allowMachLookup` | *(macOS)* XPC/Mach service names; trailing `*` prefix match, `"*"` = all | `["com.apple.coresimulator.*"]` |
| `network.allowManagedDomainsOnly` | *(Managed only)* Only managed `allowedDomains` apply | `true` |
| `network.strictAllowlist` | *(User or managed)* Deny (not prompt) sandboxed commands outside the allowlist | `true` |
| `network.tlsTerminate` | *(User or managed)* Terminate TLS in the proxy; `{}` or `{caCertPath, caKeyPath}`. Needed for `mask` credentials | `{}` |
| `filesystem.allowManagedReadPathsOnly` | *(Managed only)* Only managed `filesystem.allowRead` applies | `true` |
| `filesystem.disabled` | *(User or managed)* Skip filesystem isolation, keep network isolation | `true` |
| `ignoreViolations` | Command-substring → violation substrings to silence (still blocked, just not reported) | `{"*": ["/etc/hosts"]}` |
| `ripgrep` | *(User or managed)* Custom `rg` for the sandbox: `{command, args?}` | `{"command": "/opt/bin/rg"}` |
| `credentials.files` | `[{path, mode: "deny"\|"mask", ...}]`; `mask` entries dropped from project/local files | `[{"path": "~/.aws/credentials", "mode": "deny"}]` |
| `credentials.envVars` | `[{name, mode: "deny"\|"mask", ...}]`; `mask` needs `network.tlsTerminate` | `[{"name": "GITHUB_TOKEN", "mode": "deny"}]` |
| `credentials.allowPlaintextInject` | *(User or managed)* Allow `mask` substitution over plain HTTP (default `false`) | `true` |
| `credentials.awsPairs` | *(User or managed)* Pair non-standard AWS var names for SigV4 re-signing: `{accessKeyIdVar, secretAccessKeyVar, sessionTokenVar?}` (v2.1.224+) | — |
| `credentials.sigv4` | *(User or managed)* `{streaming, presigned, sigv4a}` each `"deny"` (default) \| `"passthrough"` (v2.1.224+) | `{"streaming": "passthrough"}` |
| `allowAppleEvents` | *(macOS, user or managed)* Allow Apple Events (`open`/`osascript`). **Removes code-execution isolation** | `true` |
| `enableWeakerNestedSandbox` | *(Linux/WSL2)* Weaker sandbox for unprivileged Docker. **Reduces security** | `true` |
| `enableWeakerNetworkIsolation` | *(macOS)* Allow system TLS trust service. **Reduces security** | `true` |
| `bwrapPath` / `socatPath` | *(Managed only, Linux/WSL2)* Absolute path to `bwrap`/`socat` | `"/opt/admin/bwrap"` |

---

## Attribution & Git

```json
{
  "attribution": {
    "commit": "Co-Authored-By: Claude <noreply@anthropic.com>",
    "pr": "",
    "sessionUrl": false
  },
  "includeGitInstructions": true
}
```

- `attribution.commit` — default `Co-Authored-By: <active model name> <noreply@anthropic.com>`; `""` hides it.
- `attribution.pr` — default `🤖 Generated with [Claude Code](https://claude.com/claude-code)`; `""` hides it.
- `attribution.sessionUrl` — default `true`; add the claude.ai session link (cloud/Remote Control sessions).
- `"attribution": false` hides all attribution — requires v2.1.281+; earlier versions reject it **and skip the whole settings file**.

---

## Worktree settings

```json
{
  "worktree": {
    "baseRef": "fresh",
    "symlinkDirectories": ["node_modules", ".cache"],
    "sparsePaths": ["packages/my-app", "shared/utils"],
    "bgIsolation": "worktree"
  }
}
```

| Key | Description | Example |
| --- | --- | --- |
| `worktree.baseRef` | `"fresh"` (default, `origin/<default-branch>`) or `"head"` (local `HEAD`, includes unpushed commits) | `"head"` |
| `worktree.symlinkDirectories` | Dirs (repo-relative) symlinked into each worktree | `["node_modules"]` |
| `worktree.sparsePaths` | Sparse-checkout dirs (unset = whole tree) | `["packages/my-app"]` |
| `worktree.bgIsolation` | Background sessions: `"worktree"` (default) or `"none"` | `"none"` |

---

## Misc / Enterprise

| Key | Description | Example |
| --- | --- | --- |
| `disableDeepLinkRegistration` | `"disable"` prevents `claude-cli://` handler registration | `"disable"` |
| `allowedHttpHookUrls` | Allowlist for HTTP hook URLs (merges across files) | `["https://hooks.example.com/*"]` |
| `httpHookAllowedEnvVars` | Env vars HTTP hooks may interpolate into headers | `["MY_TOKEN"]` |
| `allowManagedHooksOnly` | *(Managed only)* Only managed + force-enabled plugin hooks run; also narrows `statusLine`/`fileSuggestion`/`subagentStatusLine` | `true` |
| `allowManagedPermissionRulesOnly` | *(Managed only)* Only managed permission rules apply | `true` |
| `forceRemoteSettingsRefresh` | *(Managed only)* Block startup until remote managed settings are fetched | `true` |
| `wslInheritsWindowsSettings` | *(Managed only, Windows source)* WSL reads the Windows policy chain | `true` |
| `managedSourcesBehavior` | *(Managed only)* `"first-wins"` (default) or `"merge"` across admin sources | `"merge"` |
| `parentSettingsBehavior` | *(Managed only)* `"first-wins"` (default) or `"merge"` for embedder-supplied managed settings | `"merge"` |
| `policyHelper` | *(Managed only; plist/HKLM/managed file)* `{path, timeoutMs (default 10000, min 1000), refreshIntervalMs (0 or ≥60000)}` | `{"path": "/usr/local/bin/claude-policy"}` |
| `requiredMinimumVersion` / `requiredMaximumVersion` | *(Managed only)* Hard version floor/ceiling; invalid value ignored | `"2.1.150"` |
| `claudeMd` | *(Managed only)* Org-managed CLAUDE.md text | `"Always run make lint before committing."` |
| `enableArtifact` | `false` turns the Artifact tool off from any file; nothing turns it back on | `false` |
| `disableBrowserExternalNavigation` | *(Managed only)* Block external browsing in desktop Browser pane | `true` |
| `browserExternalPageTools` | *(Managed only)* `"disabled"` stops tools on external pages | `"disabled"` |
| `disableMobileSimulatorTools` | *(Managed only)* Block iOS Simulator pane tools | `true` |
| `disableDesktopLocalSessions` | *(Managed only)* Turn off on-device Desktop Code sessions | `true` |
| `sshHostAllowlist` | *(Managed only, Desktop only)* SSH host patterns; `[]` disables SSH sessions | `["*.example.com"]` |
| `allowAllClaudeAiMcps` / `managedMcpServers` | *(Managed only)* See `references/mcp.md` | — |

---

## Deprecated and removed keys

| Key | Status | Use instead |
| --- | --- | --- |
| `voiceEnabled` | Deprecated since v2.1.92, still read | `voice.enabled` |
| `includeCoAuthoredBy` | Deprecated since v2.0.62; ignored once `attribution.commit`/`pr` is set | `attribution` |
| `disableArtifact` | Deprecated; `true` still = `enableArtifact: false`, `false` ignored | `enableArtifact` |
| `keybindingFlavor` | Deprecated since v2.1.261, no effect (still accepted) | — |
| `taskOutputMaxChars` | Removed in v2.1.277 with the `TaskOutput` tool | — |
| `permissionExplainerEnabled` | *(Global config)* Removed in v2.1.257 | — |
| `teammateDefaultModel` | *(Global config)* Removed in v2.1.234 | — |

---

## Global config (~/.claude.json only)

These go in `~/.claude.json`, NOT in `settings.json`. `~/.claude.json` also holds sign-in state, MCP servers (user/local scope), and per-project trust.

> [!NOTE]
> `theme`, `verbose`, `showTurnDuration`, `terminalProgressBarEnabled`, `teammateMode`, `agentPushNotifEnabled`, `inputNeededNotifEnabled`, `preferredNotifChannel`, `remoteControlAtStartup`, and `respectGitignore` are `settings.json` keys; Claude Code still reads a value left in `~/.claude.json` by older versions when no settings file sets it.

| Key | Description | Example |
| --- | --- | --- |
| `autoConnectIde` | Auto-connect to running IDE from external terminal (default `false`) | `true` |
| `autoInstallIdeExtension` | Auto-install IDE extension (default `true`) | `false` |
| `copyOnSelect` | Copy mouse selections in fullscreen/agent view (default `true`) | `false` |
| `diffTool` | `"auto"` (default, IDE diff viewer) or `"terminal"` | `"terminal"` |
| `externalEditorContext` | Prepend Claude's last response as comments in `Ctrl+G` editor (default `false`) | `true` |

---

## Complete annotated example

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "autoUpdatesChannel": "latest",
  "model": "claude-sonnet-5",
  "effortLevel": "high",
  "language": "english",
  "permissions": {
    "defaultMode": "default",
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "WebSearch"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./secrets/**)"
    ]
  },
  "hooks": {
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "echo 'Claude finished' | wall 2>/dev/null || true",
          "async": true
        }]
      }
    ]
  },
  "env": {
    "NODE_ENV": "development"
  }
}
```

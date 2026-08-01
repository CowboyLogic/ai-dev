# settings.json Full Schema Reference

Schema URL: `https://json.schemastore.org/claude-code-settings.json`

## Table of Contents

- [Model & Performance](#model--performance)
- [Auto Mode](#auto-mode)
- [UI & Display](#ui--display)
- [Session & Behavior](#session--behavior)
- [Environment & Integration](#environment--integration)
- [Plugins](#plugins)
- [Subagents](#subagents)
- [Sandbox](#sandbox)
- [Attribution & Git](#attribution--git)
- [Worktree settings](#worktree-settings)
- [Misc / Enterprise](#misc--enterprise)
- [Global config (~/.claude.json only)](#global-config-claudejson-only)

---

## Model & Performance

| Key | Description | Example |
| --- | --- | --- |
| `model` | Override default model | `"claude-sonnet-4-6"` |
| `effortLevel` | Persist effort level | `"low"` \| `"medium"` \| `"high"` \| `"xhigh"` |
| `alwaysThinkingEnabled` | Enable extended thinking by default | `true` |
| `showThinkingSummaries` | Show thinking block summaries | `true` |
| `availableModels` | Restrict model picker options | `["sonnet", "haiku"]` |
| `modelOverrides` | Map model IDs to provider-specific IDs (Bedrock ARNs etc.) | `{"claude-opus-4-6": "arn:aws:bedrock:..."}` |
| `outputStyle` | Output style for system prompt adjustment | `"Explanatory"` |
| `agent` | Run main thread as named subagent | `"code-reviewer"` |
| `advisorModel` | Model for the server-side advisor tool (`/advisor`) | `"opus"` |
| `fallbackModel` | Ordered fallback chain tried when primary model is overloaded/unavailable (max 3, doesn't merge across scopes — highest-precedence file wins whole chain) | `["claude-sonnet-5", "claude-haiku-4-5"]` |
| `switchModelsOnFlag` | Default `true`. Auto-switch to fallback model when a safety classifier flags a request, instead of pausing to choose | `false` |

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
    "allow": ["Deploying to staging is allowed: isolated from prod"],
    "soft_deny": ["Never run DB migrations outside migrations CLI"]
  },
  "disableAutoMode": "disable",
  "useAutoModeDuringPlan": false
}
```

**Important**: Setting `allow` or `soft_deny` **replaces** the entire default list for that field (include the literal string `"$defaults"` in the array to inherit the built-ins at that position instead). Run `claude auto-mode defaults` first to see defaults, then copy and edit. `autoMode` is read from user settings, `--settings`, and managed settings only — ignored in project/local settings.

`autoMode.classifyAllShell` (default `false`): when `true`, suspends every Bash/PowerShell allow rule while auto mode is active so *all* shell commands route through the classifier, not just ones matching arbitrary-code-execution patterns.

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
| `language` | Response language | `"japanese"`, `"spanish"`, `"french"` |
| `viewMode` | Default transcript view | `"default"` \| `"verbose"` \| `"focus"` |
| `tui` | Terminal UI renderer | `"fullscreen"` \| `"default"` |
| `prefersReducedMotion` | Reduce UI animations | `true` |
| `spinnerTipsEnabled` | Show tips in spinner | `false` |
| `spinnerTipsOverride` | Custom spinner tips | `{"excludeDefault": true, "tips": ["Use tool X"]}` |
| `spinnerVerbs` | Custom action verbs | `{"mode": "append", "verbs": ["Pondering"]}` |
| `statusLine` | Custom status line | `{"type": "command", "command": "~/.claude/statusline.sh"}` |
| `showClearContextOnPlanAccept` | Show clear-context on plan accept | `true` |
| `awaySummaryEnabled` | Session recap on return | `true` |
| `autoScrollEnabled` | Follow new output in fullscreen mode (default: `true`) | `false` |
| `editorMode` | Input keybindings (`"normal"` or `"vim"`) | `"vim"` |
| `showTurnDuration` | Show turn duration after responses (default: `true`) | `false` |
| `terminalProgressBarEnabled` | Terminal progress bar in ConEmu/Ghostty/iTerm2 (default: `true`) | `false` |
| `teammateMode` | Agent team display: `"auto"`, `"in-process"`, `"tmux"`, `"iterm2"` (default: `"in-process"`) | `"auto"` |
| `theme` | Color theme (default: `"dark"`): `"auto"`\|`"dark"`\|`"light"`\|`"dark-daltonized"`\|`"light-daltonized"`\|`"dark-ansi"`\|`"light-ansi"`\|`"custom:<slug>"` | `"dark"` |
| `verbose` | Show full tool output instead of truncated summaries (default: `false`) | `true` |
| `syntaxHighlightingDisabled` | Disable syntax highlighting in diffs/code blocks/previews | `true` |
| `wheelScrollAccelerationEnabled` | Accelerate mouse-wheel scroll speed in fullscreen mode (default: `true`) | `false` |
| `emojiCompletionEnabled` | `:shortcode:` emoji autocomplete in prompt input (default: `true`) | `false` |
| `vimInsertModeRemaps` | Map two-key INSERT-mode sequences to Escape in vim editor mode. Only `"<Esc>"` target supported | `{"jj": "<Esc>"}` |
| `respondToBashCommands` | Whether Claude responds after an input-box `!` shell command (default: `true`); `false` adds output to context silently | `false` |
| `askUserQuestionTimeout` | Idle time before an unanswered `AskUserQuestion` auto-continues (default: `"never"`) | `"5m"` |
| `footerLinksRegexes` | Extra clickable footer badges when a regex matches turn output: `{pattern, url, label}` with named-capture `{name}` substitution. User/`--settings`/managed only | `[{"pattern": "\\b(?<key>PROJ-\\d+)\\b", "url": "https://issues.example.com/{key}"}]` |

---

## Session & Behavior

| Key | Description | Example |
| --- | --- | --- |
| `cleanupPeriodDays` | Delete session files older than N days (default: 30, min: 1) | `20` |
| `autoUpdatesChannel` | Update channel | `"stable"` \| `"latest"` |
| `minimumVersion` | Floor for auto-updates | `"2.1.100"` |
| `plansDirectory` | Where plan files are stored | `"./plans"` |
| `autoMemoryDirectory` | Custom auto-memory storage dir | `"~/my-memory-dir"` |
| `respectGitignore` | `@` file picker respects .gitignore | `true` (default) |
| `fastModePerSessionOptIn` | Fast mode resets each session | `true` |
| `feedbackSurveyRate` | Survey probability 0–1 (0 = disable) | `0` |
| `includeGitInstructions` | Include built-in git workflow in system prompt | `true` (default) |
| `companyAnnouncements` | Messages shown at startup (cycled randomly) | `["Welcome! See docs.acme.com"]` |
| `autoMemoryEnabled` | Enable auto memory read/write (default: `true`); toggle with `/memory` | `false` |
| `autoCompactEnabled` | Auto-compact conversation near context limit (default: `true`) | `false` |
| `fastMode` | Turn on fast mode for sessions where available; `/fast` writes this | `true` |
| `fileCheckpointingEnabled` | Snapshot files before each edit so `/rewind` can restore them (default: `true`) | `false` |
| `requiredMinimumVersion` | (Managed only) Hard floor — Claude Code exits at startup if older. Fails open (invalid value stripped, not enforced) | `"2.1.150"` |
| `requiredMaximumVersion` | (Managed only) Hard ceiling — Claude Code exits at startup if newer. Fails open | `"2.1.150"` |
| `disableWorkflows` | Disable dynamic workflows and bundled workflow commands (default: `false`) | `true` |
| `workflowKeywordTriggerEnabled` | Whether typing `ultracode` in a prompt triggers a dynamic workflow (default: `true`) | `false` |
| `workflowSizeGuideline` | Agent-count guidance Claude aims for in workflows it writes (default: `"medium"`) | `"small"` \| `"unrestricted"` \| `"large"` |
| `ultracode` | Turn on ultracode for current session. Not read from settings.json — set via `/effort ultracode` or `--effort ultracode` | `true` |
| `skillListingBudgetFraction` | Fraction of context window reserved for the skill listing (default: `0.01`) | `0.02` |
| `skillListingMaxDescChars` | Per-skill char cap on description+when_to_use text in the listing (default: `1536`) | `2048` |
| `skillOverrides` | Per-skill visibility: `"on"`\|`"name-only"`\|`"user-invocable-only"`\|`"off"`, keyed by skill name | `{"legacy-context": "name-only", "deploy": "off"}` |
| `disableBundledSkills` | Disable bundled skills/workflows (built-ins like `/init` stay typable but hidden from model) | `true` |

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
| `env` | Env vars applied every session | `{"FOO": "bar"}` |
| `apiKeyHelper` | Script to generate auth value (X-Api-Key) | `"/bin/gen_key.sh"` |
| `awsAuthRefresh` | Script that refreshes AWS credentials | `"aws sso login --profile myprofile"` |
| `awsCredentialExport` | Script that outputs AWS credentials JSON | `"/bin/gen_aws.sh"` |
| `otelHeadersHelper` | Script for dynamic OpenTelemetry headers | `"/bin/gen_otel.sh"` |
| `forceLoginMethod` | Restrict login to claude.ai or console | `"claudeai"` \| `"console"` |
| `forceLoginOrgUUID` | Require specific org UUID(s); accepts string or array | `"uuid-here"` |
| `fileSuggestion` | Custom `@` autocomplete script | `{"type": "command", "command": "~/.claude/suggest.sh"}` |
| `defaultShell` | Default shell for `!` commands | `"bash"` \| `"powershell"` |
| `voice` | Voice dictation: `enabled`, `mode` (`"hold"`/`"tap"`), `autoSubmit` | `{"enabled": true, "mode": "tap"}` |
| `voiceEnabled` | **Deprecated**: use `voice.enabled` instead | `true` |
| `skipWebFetchPreflight` | Skip Anthropic domain safety check before WebFetch (Bedrock/Vertex/air-gapped envs) | `true` |
| `sshConfigs` | Pre-configure SSH connections for Desktop env dropdown (user scope only) | `[{"id": "dev-vm", "name": "Dev VM", "sshHost": "user@dev.example.com"}]` |
| `prUrlTemplate` | Custom PR badge URL. Substitutes `{host}`, `{owner}`, `{repo}`, `{number}`, `{url}` | `"https://reviews.example.com/{owner}/{repo}/pull/{number}"` |
| `gcpAuthRefresh` | Script that refreshes GCP Application Default Credentials | `"gcloud auth application-default login"` |
| `processWrapper` | Corporate launcher command placed in front of background processes Claude Code starts. From managed/`--settings`/user only | `"/opt/corp/launcher --profile claude"` |
| `disableClaudeAiConnectors` | Disable claude.ai MCP connectors (see `references/mcp.md`) | `true` |
| `remote.defaultEnvironmentId` | Default cloud environment for `claude --cloud`/ultraplan sessions | `"env_0123abcd"` |
| `remoteControlAtStartup` | Auto-connect Remote Control at session start instead of waiting for `/remote-control` | `false` |
| `disableRemoteControl` | Disable Remote Control entirely (blocks flag, auto-start, in-session toggle) | `true` |
| `forceLoginGatewayUrl` | Pre-fill/lock gateway URL on the `/login` Cloud gateway screen. Managed tier only | `"https://claude-gateway.example.com"` |
| `agentPushNotifEnabled` | Default `false`. Allow Claude to send proactive push notifications via Remote Control | `true` |
| `inputNeededNotifEnabled` | Default `false`. Push notification when a permission prompt/question needs input | `true` |
| `preferredNotifChannel` | Notification method (default: `"auto"`): `"terminal_bell"`\|`"iterm2"`\|`"iterm2_with_bell"`\|`"kitty"`\|`"ghostty"`\|`"notifications_disabled"` | `"terminal_bell"` |

---

## Plugins

Plugins extend Claude Code with skills, agents, hooks, and MCP servers. Manage via `/plugin` command.

```json
{
  "enabledPlugins": {
    "formatter@acme-tools": true,
    "deployer@acme-tools": true,
    "experimental@personal": false
  },
  "extraKnownMarketplaces": {
    "acme-tools": {
      "source": { "source": "github", "repo": "acme-corp/claude-plugins" }
    }
  }
}
```

| Key | Description | Example |
| --- | --- | --- |
| `enabledPlugins` | Enable/disable plugins by `"name@marketplace"` key | `{"formatter@acme-tools": true}` |
| `extraKnownMarketplaces` | Register team marketplaces; members are prompted to install on folder trust | see above |
| `pluginTrustMessage` | *(Managed only)* Custom message on plugin trust dialog | `"Vetted by IT"` |
| `allowedChannelPlugins` | *(Managed only)* Allowlist of channel plugins that may push messages | `[{"marketplace": "claude-plugins-official", "plugin": "telegram"}]` |
| `channelsEnabled` | *(Managed only)* Allow channels for Team/Enterprise users | `true` |
| `strictKnownMarketplaces` | *(Managed only)* Allowlist of marketplace sources; empty array = lockdown | `[{"source": "github", "repo": "acme/plugins"}]` |
| `blockedMarketplaces` | *(Managed only)* Denylist of marketplace sources | `[{"source": "github", "repo": "untrusted/plugins"}]` |
| `pluginSuggestionMarketplaces` | *(Managed only)* Marketplace names allowed to surface contextual plugin-install suggestions | `["acme-corp-plugins"]` |
| `strictPluginOnlyCustomization` | *(Managed only)* Block skills/agents/hooks/MCP servers from user+project sources — only plugins or managed settings. `true` locks all four; an array locks only those named | `["skills", "hooks"]` |
| `disableSideloadFlags` | *(Managed only)* Reject `--plugin-dir`, `--plugin-url`, `--agents`, `--mcp-config` CLI flags at startup (closes a `strictKnownMarketplaces` bypass) | `true` |

---

## Subagents

Subagent Markdown files define specialized AI assistants with custom prompts and tool restrictions.

| Scope | Location |
| --- | --- |
| User (all projects) | `~/.claude/agents/` |
| Project (shared) | `.claude/agents/` |

See [sub-agents documentation](/en/sub-agents) for file format details.

---

## Sandbox

> OS-level isolation for bash commands. macOS, Linux, WSL2 only.

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

**Path prefixes**: `/` = absolute, `~/` = home-relative, `./` or no prefix = project/user-relative.

**Additional sandbox keys:**

| Key | Description | Example |
| --- | --- | --- |
| `network.allowMachLookup` | *(macOS only)* XPC/Mach service names the sandbox may look up. Supports trailing `*`. Required for iOS Simulator, Playwright | `["com.apple.coresimulator.*"]` |
| `network.allowManagedDomainsOnly` | *(Managed only)* Only `allowedDomains` from managed settings apply; others ignored | `true` |
| `network.strictAllowlist` | Deny (not prompt) sandboxed commands outside the allowlist. Sandboxed commands only — in-process `WebFetch` unaffected. User/managed/`--settings` only | `true` |
| `network.tlsTerminate` | Experimental: terminate TLS inside the sandbox proxy so it can read HTTPS contents; required for `credentials.envVars` `mask` mode. `{}` = ephemeral CA, or set `caCertPath`/`caKeyPath` | `{}` |
| `filesystem.allowManagedReadPathsOnly` | *(Managed only)* Only `filesystem.allowRead` from managed settings applies | `true` |
| `filesystem.disabled` | Skip filesystem isolation while keeping network isolation (unrestricted host FS access, network still confined to `allowedDomains`). User/managed/`--settings` only | `true` |
| `allowUnsandboxedCommands` | Default `true`. Allow the `dangerouslyDisableSandbox` escape hatch; `false` forces every command sandboxed or excluded | `false` |
| `failIfUnavailable` | Exit at startup if `sandbox.enabled` but sandbox can't start (default `false` = warn and run unsandboxed) | `true` |
| `credentials.files` | Credential paths sandboxed commands can't read (same effect as `filesystem.denyRead`, kept separate for grouping): `{path, mode: "deny"}` | `[{"path": "~/.aws/credentials", "mode": "deny"}]` |
| `credentials.envVars` | Env vars to protect from sandboxed commands: `{name, mode}`. `deny` strips it; `mask` substitutes a per-session sentinel (requires `network.tlsTerminate`, user/managed/`--settings` only) | `[{"name": "GITHUB_TOKEN", "mode": "deny"}]` |
| `credentials.allowPlaintextInject` | Allow `mask` substitution over plain HTTP, not just TLS (default `false`, cleartext risk) | `true` |
| `allowAppleEvents` | *(macOS only)* Allow sandboxed commands to send Apple Events — needed for `open`/`osascript`. **Removes code-execution isolation**; user/managed/`--settings` only | `true` |
| `enableWeakerNestedSandbox` | *(Linux/WSL2)* Weaker sandbox for unprivileged Docker. **Reduces security** | `true` |
| `enableWeakerNetworkIsolation` | *(macOS only)* Allow system TLS trust service for `gh`/`gcloud`/`terraform` with MITM proxy. **Reduces security** | `true` |
| `bwrapPath` / `socatPath` | *(Managed only, Linux/WSL2)* Override auto-detected path to `bwrap`/`socat` binaries | `"/opt/admin/bwrap"` |

---

## Attribution & Git

```json
{
  "attribution": {
    "commit": "🤖 Generated with Claude Code",
    "pr": ""
  },
  "includeGitInstructions": true
}
```

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
| `worktree.baseRef` | Which ref new worktrees branch from: `"fresh"` (default, `origin/<default-branch>`) or `"head"` (current local `HEAD`, includes unpushed commits) | `"head"` |
| `worktree.bgIsolation` | Isolation for background sessions: `"worktree"` (default, blocks Edit/Write in main checkout until `EnterWorktree`) or `"none"` | `"none"` |

---

## Misc / Enterprise

| Key | Description | Example |
| --- | --- | --- |
| `disableSkillShellExecution` | Disable `!` shell blocks in skills | `true` |
| `disableDeepLinkRegistration` | Prevent `claude-cli://` protocol handler registration | `"disable"` |
| `allowedHttpHookUrls` | Allowlist for HTTP hook URLs | `["https://hooks.example.com/*"]` |
| `httpHookAllowedEnvVars` | Env vars HTTP hooks may use in headers | `["MY_TOKEN"]` |
| `allowManagedHooksOnly` | *(Managed only)* Block all user/project/plugin hooks; only managed + force-enabled plugin hooks load | `true` |
| `allowManagedPermissionRulesOnly` | *(Managed only)* Only managed `allow`/`ask`/`deny` rules apply; user/project rules ignored | `true` |
| `forceRemoteSettingsRefresh` | *(Managed only)* Block startup until remote managed settings are freshly fetched; exit if fetch fails | `true` |
| `wslInheritsWindowsSettings` | *(Windows managed only)* Claude Code on WSL also reads Windows policy chain | `true` |
| `disableAgentView` | Turn off background agents/agent view (`claude agents`, `--bg`, `/background`) | `true` |
| `disableArtifact` / `enableArtifact` | Disable, or explicitly enable, the Artifact tool (publishes session output as a private claude.ai page) | `true` |
| `disableBrowserExternalNavigation` | *(Managed only)* Block external browsing in desktop app's Browser pane (localhost previews unaffected) | `true` |
| `browserExternalPageTools` | *(Managed only)* Set `"disabled"` to stop Claude using tools on external pages in the desktop Browser pane | `"disabled"` |
| `disableMobileSimulatorTools` | *(Managed only)* Block Claude's tools for the desktop app's iOS Simulator pane | `true` |
| `claudeMd` | *(Managed only)* CLAUDE.md-style instructions injected as org-managed memory | `"Always run make lint before committing."` |
| `claudeMdExcludes` | Glob/absolute paths of CLAUDE.md files to skip loading (user/project/local memory only, not managed) | `["**/vendor/**/CLAUDE.md"]` |
| `parentSettingsBehavior` | *(Managed only)* `"first-wins"` (default) or `"merge"` — how SDK/IDE-embedder-supplied managed settings combine with an admin-deployed managed tier | `"merge"` |
| `policyHelper` | Admin-deployed executable that computes managed settings dynamically at startup. MDM/system `managed-settings.json` only | `{"path": "/usr/local/bin/claude-policy"}` |
| `enforceAvailableModels` | Extend the `availableModels` allowlist to the Default model option when the resolved default isn't itself allowlisted | `true` |
| `allowAllClaudeAiMcps` | *(Managed only)* Load claude.ai connectors alongside a deployed `managed-mcp.json` (see `references/mcp.md`) | `true` |

---

## Global config (~/.claude.json only)

These go in `~/.claude.json`, NOT in `settings.json`. Adding them to `settings.json` will trigger a schema validation error.

> [!NOTE]
> (v2.1.119+) `autoScrollEnabled`, `editorMode`, `showTurnDuration`, `terminalProgressBarEnabled`, and `teammateMode` moved to `settings.json`. Earlier versions store them in `~/.claude.json`.

| Key | Description | Example |
| --- | --- | --- |
| `autoConnectIde` | Auto-connect to running IDE when starting from external terminal | `true` |
| `autoInstallIdeExtension` | Auto-install Claude Code IDE extension when running inside VS Code/JetBrains | `false` |
| `externalEditorContext` | Prepend Claude's last response as `#`-commented context when opening external editor (`Ctrl+G`) | `true` |
| `diffTool` | Where to show file diffs when an IDE is connected: `"auto"` (IDE diff viewer) or `"terminal"` | `"terminal"` |
| `permissionExplainerEnabled` | Show model-generated command explanation on `Ctrl+E` at a Bash/PowerShell permission prompt (default: `true`) | `false` |
| `teammateDefaultModel` | Default model for agent-team teammates when the spawn prompt doesn't specify one; `null` inherits lead's `/model` | `"sonnet"` |

---

## Complete annotated example

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "autoUpdatesChannel": "latest",
  "model": "claude-sonnet-4-6",
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

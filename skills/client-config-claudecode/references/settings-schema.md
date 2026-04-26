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

**Important**: Setting `allow` or `soft_deny` **replaces** the entire default list for that field. Run `claude auto-mode defaults` first to see defaults, then copy and edit.

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
| `teammateMode` | Agent team display: `"auto"`, `"in-process"`, `"tmux"` | `"in-process"` |

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
| `filesystem.allowManagedReadPathsOnly` | *(Managed only)* Only `filesystem.allowRead` from managed settings applies | `true` |
| `enableWeakerNestedSandbox` | *(Linux/WSL2)* Weaker sandbox for unprivileged Docker. **Reduces security** | `true` |
| `enableWeakerNetworkIsolation` | *(macOS only)* Allow system TLS trust service for `gh`/`gcloud`/`terraform` with MITM proxy. **Reduces security** | `true` |

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
    "symlinkDirectories": ["node_modules", ".cache"],
    "sparsePaths": ["packages/my-app", "shared/utils"]
  }
}
```

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

---

## Global config (~/.claude.json only)

These go in `~/.claude.json`, NOT in `settings.json`. Adding them to `settings.json` will trigger a schema validation error.

> **Note (v2.1.119+):** `autoScrollEnabled`, `editorMode`, `showTurnDuration`, `terminalProgressBarEnabled`, and `teammateMode` moved to `settings.json`. Earlier versions store them in `~/.claude.json`.

| Key | Description | Example |
| --- | --- | --- |
| `autoConnectIde` | Auto-connect to running IDE when starting from external terminal | `true` |
| `autoInstallIdeExtension` | Auto-install Claude Code IDE extension when running inside VS Code/JetBrains | `false` |
| `externalEditorContext` | Prepend Claude's last response as `#`-commented context when opening external editor (`Ctrl+G`) | `true` |

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

# Copilot CLI Core Configuration Reference

Covers the configuration directory, `settings.json` (user, repository, local), `config.json`,
repository model allowlists, managed settings, environment variables, authentication, BYOK
providers, and model selection.

Permissions (flags, patterns, `permissions-config.json`, sandbox) are in `permissions.md`.
CLI commands, options, and slash commands are in `cli-commands.md`.

## Configuration directory (`~/.copilot`)

Default `~/.copilot` (`$HOME/.copilot`; Windows `$HOME\.copilot`). Override the whole path with
`COPILOT_HOME`. The `--config-dir` option is deprecated — use `COPILOT_HOME`.

| Path | Type | Purpose | Edit by hand? |
|------|------|---------|---------------|
| `settings.json` | File | Personal settings (JSONC) | Yes, or `/settings` |
| `config.json` | File | App state: auth, installed plugins, `trustedFolders` | Only `trustedFolders` |
| `copilot-instructions.md` | File | Personal custom instructions | Yes |
| `instructions/` | Dir | Personal `*.instructions.md` files | Yes |
| `mcp-config.json` | File | User-level MCP servers | Yes, or `/mcp` |
| `lsp-config.json` | File | User-level LSP servers | Yes, or `/lsp` |
| `providers.json` | File | BYOK provider and model registry | Yes |
| `agents/` | Dir | Personal custom agents (`*.agent.md`) | Yes |
| `skills/` | Dir | Personal skills (`<name>/SKILL.md`) | Yes |
| `hooks/` | Dir | User-level hook files (`*.json`) | Yes |
| `extensions/` | Dir | Personal extensions | Yes |
| `permissions-config.json` | File | Saved tool/directory approvals per location | With caution |
| `installed-plugins/` | Dir | Plugin files — manage with `copilot plugin` | No |
| `plugin-data/` | Dir | Persistent plugin data | No |
| `session-state/` | Dir | Session history (`events.jsonl`) — enables `--resume`/`--continue` | No |
| `command-history-state/` | Dir | Prompt history for `Ctrl+R` | No |
| `session-store.db` | File | SQLite cross-session index (rebuild with `/chronicle reindex`) | No |
| `logs/` | Dir | `process-{timestamp}-{pid}.log` per session — safe to delete | No |
| `ide/` | Dir | IDE integration lock files | No |
| `mcp-oauth-config/` | Dir | MCP OAuth fallback storage when no keychain | No |
| `mcp-secrets/` | Dir | MCP secret placeholder fallback storage | No |

Items are created on demand (for example, `installed-plugins/` appears after the first install).

The cache directory is **not** affected by `COPILOT_HOME`: macOS `~/Library/Caches/copilot`,
Linux `$XDG_CACHE_HOME/copilot` or `~/.cache/copilot`, Windows `%LOCALAPPDATA%/copilot`.
Override with `COPILOT_CACHE_HOME`.

Run `copilot help config` for a quick terminal reference.

---

## Settings precedence

Later overrides earlier:

1. Built-in defaults
2. MDM managed settings
3. User settings — `~/.copilot/settings.json`
4. Repository settings — `.github/copilot/settings.json` (committed)
5. Local settings — `.github/copilot/settings.local.json` (add to `.gitignore`)
6. Environment variables
7. Command-line flags

Exceptions: an MDM `permissions.disableBypassPermissionsMode` of `"disable"` always wins, and
managed `sandbox` values set a floor users cannot relax.

The CLI also reads `.claude/settings.json` and `.claude/settings.local.json` in the repository for
the shared cross-tool subset (such as `companyAnnouncements`, `disableAllHooks`,
`enabledPlugins`, `extraKnownMarketplaces`, and `hooks`).

---

## settings.json (user)

**Location**: `~/.copilot/settings.json` (or `$COPILOT_HOME/settings.json`). JSON with comments
(JSONC) is supported.

- Edit directly, or use `/settings` (alias `/config`) in a session: `/settings KEY VALUE`,
  `/settings show KEY`, `/settings KEY` (shows valid values). Nested keys use dots:
  `/settings footer.showBranch off`. Booleans accept `on`/`off` or `true`/`false`.
- List/structured settings and security-sensitive settings can't be set inline — press
  `Ctrl+E` in the `/settings` editor to open the file.
- Invalid values or unknown top-level keys are ignored and listed in the **Problems** tab of
  `/settings`. `$schema` is tolerated.
- User settings previously lived in `config.json`; they are migrated to `settings.json`
  automatically on startup.
- If `settings.json` is a symlink (dotfiles), `/settings` writes follow the symlink.
- A few settings (for example, `experimental` and proxy settings) need a restart.

```json
{
  "model": "auto",
  "effortLevel": "medium",
  "theme": "dim",
  "autoUpdate": true,
  "continueOnAutoMode": true,
  "allowedUrls": ["*.github.com"],
  "disabledSkills": ["legacy-skill"],
  "footer": { "showBranch": true }
}
```

### User setting keys

| Key | Type / values | Default | Purpose |
|-----|---------------|---------|---------|
| `allowedUrls` | `string[]` | `[]` | URLs/domains allowed without prompting; supports `*.github.com` |
| `askUser` | boolean | `true` | Allow clarifying questions (`--no-ask-user` disables) |
| `autoUpdate` | boolean | `true` | Auto-download CLI updates and update first-party plugins |
| `autoUpdatesChannel` | `"stable"` \| `"prerelease"` | `"stable"` | Update channel |
| `banner` | `"always"` \| `"once"` \| `"never"` | `"once"` | Startup banner frequency |
| `bashEnv` | boolean | `false` | `BASH_ENV` support |
| `beep` / `beepOnSchedule` | boolean | `true` | Audible beep on attention / scheduled run finished |
| `builtInAgents.rubberDuck` | boolean | `true` | Enable rubber-duck subagent |
| `builtInAgents.rubberDuckAutoInvoke` | boolean | `false` | Extra proactive rubber-duck nudges |
| `colorMode` | theme values | `"github"` | **Deprecated** alias for `theme` |
| `commandHistoryMaxSize` | number (1–1000) | `50` | Retained prompt history |
| `compactPaste` | boolean | `true` | Collapse pastes over 10 lines |
| `companyAnnouncements` | `string[]` | `[]` | Random startup messages |
| `continueOnAutoMode` | boolean | `false` | Switch to auto mode on eligible rate limits (not global limits or BYOK) |
| `copyOnSelect` | boolean | `true` macOS, else `false` | Copy mouse selection to clipboard |
| `customAgents.defaultLocalOnly` | boolean | `false` | Only local custom agents (no org/enterprise agents) |
| `deniedUrls` | `string[]` | `[]` | Always-denied URLs; deny beats allow |
| `disableAllHooks` | boolean | `false` | Disable repository and user hooks |
| `disabledMcpServers` | `string[]` | `[]` | Configured but not started |
| `disabledSkills` | `string[]` | `[]` | Discovered but not loaded |
| `dynamicRetrieval` | `{ skills?: boolean }` | unset | `skills: false` disables embeddings retrieval for skills |
| `editorMode` | `"normal"` \| `"vim"` | `"normal"` | Composer mode (`/vim` toggles) |
| `effortLevel` | `"low"` \| `"medium"` \| `"high"` \| `"xhigh"` | `"medium"` | Reasoning effort |
| `enabledMcpServers` | `string[]` | `[]` | Enable built-in MCP servers that are off by default |
| `enabledPlugins` | `Record<string, boolean>` | `{}` | Declarative plugin auto-install |
| `experimental` | boolean | `false` | Experimental features (`--experimental`, `/experimental`) |
| `extraKnownMarketplaces` | `Record<string, {...}>` | `{}` | Extra plugin marketplaces; `source` required (`"directory"`, `"git"`, `"github"`); optional `autoUpdate: true` |
| `footer` | object | — | Status-line items: `showModelEffort`, `showDirectory`, `showBranch`, `showContextWindow`, `showQuota`, `showAgent`, `showAiUsed`, `showCodeChanges`, `showUsername`, `showSandbox`, `showYolo`, `showCustom` (managed by `/statusline`) |
| `hooks` | object | — | Inline hooks keyed by event (same schema as hook files) |
| `ide.autoConnect` / `ide.openDiffOnEdit` | boolean | `true` | IDE auto-connect / show edit diffs in IDE |
| `includeCoAuthoredBy` | boolean | `true` | `Co-authored-by` trailer on agent commits |
| `keepAlive` | `"on"` \| `"off"` \| `"busy"` | `"off"` | Prevent system sleep |
| `logLevel` | `"none"` \| `"error"` \| `"warning"` \| `"info"` \| `"debug"` \| `"all"` \| `"default"` | `"default"` | Log verbosity |
| `mergeStrategy` | `"rebase"` \| `"merge"` | — | Strategy for `/pr fix conflicts` |
| `model` | string | varies | Default model; `"auto"` lets Copilot choose |
| `mouse` | boolean | `true` | Mouse support |
| `permissions.disableBypassPermissionsMode` | `"disable"` \| `"allow-auto-only"` | — | Block allow-all flags (see `permissions.md`) |
| `pinnedPrompts` | boolean | `true` | Pin current prompt while scrolling |
| `powershellFlags` | `string[]` | `["-NoProfile", "-NoLogo"]` | Windows only |
| `proxyUrl` / `proxyKerberosServicePrincipal` | string | unset | HTTP(S) proxy; `HTTP_PROXY`/`HTTPS_PROXY` override |
| `remote` | `"on"` \| `"off"` | `"on"` | Session sync and remote control |
| `remoteExport` | boolean | `true` | Export sessions remotely when sync is available |
| `renderHexColors` / `renderMarkdown` | boolean | `true` | Terminal rendering |
| `respectGitignore` | boolean | `true` | Hide gitignored files from `@` picker |
| `sandbox.*` | object | — | Local sandbox settings (see `permissions.md`) |
| `screenReader` | boolean | `false` | Screen reader optimizations |
| `scrollbar` | boolean | `true` | Scrollbar in scrollable views |
| `shellShortcut` | boolean | `true` | Lone `$` + `Enter` opens a shell (user/managed scope only) |
| `showTimestamps` / `showTipsOnStartup` | boolean | `true` | UI toggles |
| `sidebar` | boolean | `true` | Current-session sidebar |
| `skillDirectories` | `string[]` | `[]` | Extra skill search directories |
| `statusLine` | object | — | Custom status line: `type: "command"`, `command`, optional `padding`, `refreshInterval` (seconds) |
| `stayInAutopilot` | boolean | `true` | Stay in autopilot after a task completes |
| `storeTokenPlaintext` | boolean | `false` | Allow plaintext token in `config.json` when no keychain |
| `stream` | boolean | `true` | Streaming responses |
| `streamerMode` | boolean | `false` | Hide model names, quota, timestamps for screen sharing |
| `subagents.agents` | object | `{}` | Per-agent `model`, `modelPolicy`, `effortLevel`, `contextTier` (see `agents-plugins.md`) |
| `subagents.disabledSubagents` | `string[]` | `[]` | Agents that can't be dispatched (not `rubber-duck`) |
| `subagents.maxConcurrency` / `subagents.maxDepth` | number | plan-based / `6` | Usage-based billing only; capped at `32` / `256` |
| `tabs.enabled` / `tabs.hide` / `tabs.sort` | boolean / `string[]` | `true` / `[]` / `[]` | Home tab bar (`copilot`, `agents`, `issues`, `pull-requests`, `gists`) |
| `taskbarPresence` | boolean | `true` | Windows taskbar presence |
| `terminalProgress` | boolean | `true` | OSC 9;4 progress indicators |
| `theme` | `"default"` \| `"github"` \| `"dim"` \| `"high-contrast"` \| `"colorblind"` | `"github"` | Color palette |
| `toolSearch` | boolean | model-dependent | `false` opts out of deferred tool loading |
| `transcriptView` | `"default"` \| `"concise"` | `"default"` | Timeline grouping |
| `updateTerminalTitle` | boolean | `true` | Show intent in terminal title |
| `worktreeBaseRef` | `"head"` \| `"defaultBranch"` | `"head"` | Base for `/worktree` and `--worktree` |

`trustedFolders` is **not** a `settings.json` key — it lives in `config.json`.

---

## Repository and local settings

**Repository**: `.github/copilot/settings.json` (committed). **Local**:
`.github/copilot/settings.local.json` (gitignored; same schema, overrides repository).

Only these keys are honored at repository/local level — anything else is silently ignored:

| Key | Merge behavior |
|-----|----------------|
| `companyAnnouncements` | Replaced — repository wins |
| `contextTier` (`"default"` \| `"long_context"`) | Replaced — repository wins |
| `deniedUrls` | Union — repository can add, never remove |
| `disableAllHooks` | Repository wins |
| `disabledMcpServers` | Union |
| `disabledSkills` | Union |
| `effortLevel` | Replaced — repository wins |
| `enabledPlugins` | Merged — repository overrides same key |
| `extraKnownMarketplaces` | Merged — repository overrides same key (`autoUpdate` accepted but ignored) |
| `hooks` | Merged — repository overrides same key |
| `includeCoAuthoredBy` | Replaced — repository wins |
| `mergeStrategy` | Replaced — repository wins |
| `model` | Replaced — repository wins |
| `respectGitignore` | Tighten-only — repository can enable, never disable |

- `model`, `effortLevel`, and `contextTier` overrides only apply when the directory is trusted.
- A plugin enabled only via repository `enabledPlugins` is scoped to that repository.
- Repository `enabledPlugins` and `extraKnownMarketplaces` are also read by Copilot cloud agent.
- Set repo values in-session with `/settings --repo KEY VALUE` or `/settings --local KEY VALUE`.

### Repository model allowlist (`.github/allowed_models.txt`)

Plain text, one rule per line, resolved from the repository root:

```text
# .github/allowed_models.txt
fallback: gpt-5.4
gpt-5.4
claude-sonnet-*
```

- Lines are exact model IDs or globs; `#` starts a comment; `*` allows all (the default with no file).
- `fallback: MODEL-ID` is required exactly once, must be an exact ID, and must match an allowed rule.
- Negated patterns (`!pattern`) aren't supported. Re-evaluated on `/cd`.
- Governs built-in models only — BYOK models are never filtered.

---

## config.json

**Location**: `~/.copilot/config.json` (or `$COPILOT_HOME/config.json`). Automatically managed
application state (auth data, installed plugin metadata, `loggedInUsers`, `installedPlugins`,
`firstLaunchAt`, `staff`). Put user preferences in `settings.json`, not here.

### trustedFolders (array)

The one field you edit by hand. Controls where Copilot can read, modify, and execute files.

```json
{
  "trustedFolders": [
    "/home/user/projects/my-app",
    "C:\\Users\\user\\projects"
  ]
}
```

- At startup you're asked to trust the launch directory for this session only, or for this and
  future sessions (the latter writes to `trustedFolders`).
- Scoping is heuristic — GitHub does not guarantee files outside trusted directories are protected.
  Only trust directories whose contents you control.
- Trust gates project-level MCP servers, hooks, skills, and plugins, plus repository `model`,
  `effortLevel`, and `contextTier` overrides.

---

## Managed settings (administrators)

Loaded at startup as a policy baseline; server-managed settings fill keys MDM leaves unset.
Long-running sessions re-apply managed settings hourly.

| Platform | Source |
|----------|--------|
| macOS | MDM plist `com.github.copilot`, or `/Library/Application Support/GitHubCopilot/managed-settings.json` |
| Windows | Registry `HKLM\SOFTWARE\Policies\GitHubCopilot`, or `%ProgramFiles%\GitHubCopilot\managed-settings.json` |
| Linux | `/etc/github-copilot/managed-settings.json` |

On POSIX, file-based managed settings are rejected if they are symlinks, not owned by root, or
world-writable.

Supported keys: `allowedMcpServers`, `deniedMcpServers`, `enabledPlugins`,
`extraKnownMarketplaces`, `forceLoginOrgs`, `forceRemoteSettingsRefresh`, `model`, `permissions`
(including `disableBypassPermissionsMode` and `deny`/`ask`/`allow` rules), `policyHelper`,
`remoteControl`, `sandbox`, `shellShortcut`, `strictKnownMarketplaces`, `telemetry`. See
`permissions.md` for managed permission rules and `mcp.md` for the MCP allow/deny list.

---

## Environment variables

| Variable | Purpose |
|----------|---------|
| `COPILOT_HOME` | Config/state directory (default `$HOME/.copilot`) |
| `COPILOT_CACHE_HOME` | Cache directory override |
| `COPILOT_ALLOW_ALL` | Truthy (`true`, `1`, `yes`, `on`, `y`) = `--allow-all`. Exactly `true` also trusts the working directory (loads its skills, plugins, MCP servers, and hooks) |
| `COPILOT_AUTO_UPDATE` | `false` disables CLI and first-party plugin auto-updates |
| `COPILOT_MODEL` | Model to use |
| `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN` | Auth tokens, in that precedence order |
| `COPILOT_GH_HOST` | GitHub hostname for Copilot CLI only; overrides `GH_HOST` |
| `GH_HOST` | GitHub hostname for `gh` and Copilot CLI (default `github.com`) |
| `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | Extra instruction directories (comma-separated) |
| `COPILOT_SKILLS_DIRS` | Extra skill directories (comma-separated) |
| `COPILOT_EDITOR` | Editor (checked after `$VISUAL` and `$EDITOR`; default `vi`) |
| `COPILOT_MCP_TOOL_CACHE` | `false` disables MCP tool snapshot caching |
| `COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES` | Max tool output returned directly to the model (default `20480`) |
| `COPILOT_PLAN_THEN_AUTOPILOT` | Truthy = `--plan --mode autopilot` |
| `COPILOT_SUBAGENT_MAX_CONCURRENT` / `COPILOT_SUBAGENT_MAX_DEPTH` | Subagent limits (defaults `32` / `4` per this table; see note) |
| `COPILOT_TASK_WAIT_TIMEOUT_SECONDS` | How long `-p` waits for background work (default `600`) |
| `COPILOT_ENABLE_HTTP2` | `1`/`true` opts into HTTP/2 |
| `COPILOT_ENABLE_INTERRUPTED_SESSION_RESTORE` | `1` enables restoring crashed sessions |
| `COPILOT_PROMPT_FRAME` | `1`/`0` toggles the prompt frame |
| `COPILOT_STRIP_REASONING_ON_RESUME` | `0`/`false` keeps BYOK reasoning tokens on resume |
| `COPILOT_CHILD_OOM_SCORE_ADJ` | Linux OOM bias for child processes (default `300`; `off` disables) |
| `COPILOT_WEB_FETCH_ALLOW_LOCALHOST` | `1` lets `web_fetch` reach `localhost` |
| `COPILOT_HOOK_ALLOW_LOCALHOST` | `1` allows `http://localhost` HTTP hooks |
| `COPILOT_OFFLINE` | `true` = no GitHub contact, no telemetry (BYOK only) |
| `COPILOT_PROVIDER_*` / `COPILOT_PROVIDERS_CONFIG` | BYOK (see below) |
| `GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP` | `true` loads workspace MCP servers in `-p` in untrusted dirs |
| `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS` | `true` loads repository hooks in `-p` |
| `GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS` | `true` loads project extensions in `-p` |
| `PLUGINS_DASHBOARD` | `false` disables the plugins dashboard and `copilot plugin` commands |
| `PLAIN_DIFF` | `true` disables rich diffs |
| `USE_BUILTIN_RIPGREP` | `false` uses system ripgrep |
| `USE_TGREP` | `true`/`false` forces tgrep / ripgrep |

> [!NOTE]
> The upstream docs disagree on subagent defaults: the environment-variable table lists
> `COPILOT_SUBAGENT_MAX_DEPTH` default `4` (range 1–128) and max concurrent `32` (range 1–256),
> while the subagent-limits table and `subagents.*` settings list depth default `6` (cap `256`)
> and plan-based concurrency (cap `32`). Treat the settings values as authoritative for
> `settings.json`.

---

## Auth

### Credential resolution order

1. `COPILOT_GITHUB_TOKEN`
2. `GH_TOKEN`
3. `GITHUB_TOKEN`
4. OAuth token from the system keychain
5. GitHub CLI fallback (`gh auth token`)

An environment variable silently overrides a stored OAuth token. Exception: in Codespaces the
auto-injected `GITHUB_TOKEN` does not beat an account signed in with `/login`.

### Supported token types

| Type | Prefix | Supported |
|------|--------|-----------|
| OAuth token (browser or device flow) | `gho_` | Yes |
| Fine-grained PAT | `github_pat_` | Yes — user-owned, with **Copilot Requests** account permission |
| GitHub App user-to-server | `ghu_` | Yes (env var only) |
| Classic PAT | `ghp_` | No |

### Credential storage

Keychain service name `copilot-cli`: macOS Keychain Access, Windows Credential Manager, Linux
libsecret (GNOME Keyring / KWallet). With no keychain, the CLI prompts to store the token in
plaintext in `~/.copilot/config.json` (`storeTokenPlaintext` setting).

### Auth commands

```bash
copilot login                          # browser flow locally, device code when remote/CI
copilot login --host https://example.ghe.com   # GHE Cloud with data residency
copilot login --device-code            # force device code flow
copilot login --web-flow               # force browser flow
copilot login --with-token < token.txt # read token from stdin
```

In a session: `/login`, `/logout` (removes local token, doesn't revoke), `/user list`,
`/user switch`, `/user show`.

---

## BYOK (Bring Your Own Key)

Use your own provider instead of GitHub-hosted models. GitHub auth becomes optional, but without
it `/delegate`, the GitHub MCP server, and GitHub code search are unavailable. Run
`copilot help providers` for more examples.

Models must support **tool calling** and **streaming**; 128k+ context recommended.

### BYOK environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `COPILOT_PROVIDER_BASE_URL` | Yes | API endpoint base URL |
| `COPILOT_MODEL` | Yes | Model identifier (or `--model`) |
| `COPILOT_PROVIDER_TYPE` | No | `openai` (default) \| `azure` \| `anthropic` |
| `COPILOT_PROVIDER_API_KEY` | No | API key (not needed for local Ollama) |
| `COPILOT_PROVIDER_API_KEY_COMMAND` | No | Command printing a fresh key before each request; beats `COPILOT_PROVIDER_API_KEY` |
| `COPILOT_PROVIDER_BEARER_TOKEN` | No | Bearer token when not using an API key |
| `COPILOT_PROVIDER_HEADERS` | No | Custom headers (referenced by the docs; format not documented) |
| `COPILOT_PROVIDER_WIRE_API` | No | API protocol used with the provider |
| `COPILOT_PROVIDER_AZURE_API_VERSION` | Azure | Azure OpenAI API version |
| `COPILOT_PROVIDER_MODEL_ID` | No | Well-known model name (capabilities, token limits) |
| `COPILOT_PROVIDER_WIRE_MODEL` | No | Model name sent to the API (Azure: deployment name) |
| `COPILOT_PROVIDER_MAX_PROMPT_TOKENS` | No | Max prompt tokens per request |
| `COPILOT_PROVIDER_MAX_OUTPUT_TOKENS` | No | Max output tokens |
| `COPILOT_OFFLINE` | No | `true` = no GitHub contact or telemetry; only air-gapped if the provider is local |

### providers.json

`~/.copilot/providers.json` (override with `COPILOT_PROVIDERS_CONFIG`) is a JSON object with
`providers` and `models` keys. When it declares any provider or model it takes precedence over the
`COPILOT_PROVIDER_*` variables. The upstream docs don't publish the entry schema — run
`copilot help providers` before writing one.

### Provider examples

#### Ollama (local, no key)

```bash
export COPILOT_PROVIDER_BASE_URL=http://localhost:11434
export COPILOT_MODEL=llama3.2
```

#### OpenAI

```bash
export COPILOT_PROVIDER_BASE_URL=https://api.openai.com/v1
export COPILOT_PROVIDER_API_KEY=YOUR-OPENAI-API-KEY
export COPILOT_MODEL=gpt-4o
```

#### Azure OpenAI

```bash
export COPILOT_PROVIDER_BASE_URL=https://YOUR-RESOURCE-NAME.openai.azure.com
export COPILOT_PROVIDER_TYPE=azure
export COPILOT_PROVIDER_API_KEY=YOUR-AZURE-API-KEY
export COPILOT_PROVIDER_AZURE_API_VERSION=YOUR-AZURE-API-VERSION
export COPILOT_PROVIDER_MODEL_ID=YOUR-MODEL-NAME
export COPILOT_PROVIDER_WIRE_MODEL=YOUR-DEPLOYMENT-NAME
export COPILOT_MODEL=YOUR-DEPLOYMENT-NAME
```

#### Anthropic

```bash
export COPILOT_PROVIDER_TYPE=anthropic
export COPILOT_PROVIDER_BASE_URL=https://api.anthropic.com
export COPILOT_PROVIDER_API_KEY=YOUR-ANTHROPIC-API-KEY
export COPILOT_MODEL=claude-opus-4-5
```

---

## Model usage

- Select with `/model` (alias `/models`), `--model=MODEL`, `COPILOT_MODEL`, or the `model` setting.
  `auto` lets Copilot choose.
- `/model` scope flags: `--session`/`-s` (default, current session only), `--global` (saved default),
  `--repo`/`--local` (pins in repository settings).
- Reasoning effort: `--effort`/`--reasoning-effort` (`low`, `medium`, `high`, `xhigh`, `max`;
  `max` is Anthropic-only) or the `effortLevel` setting.
- Context tier: `--context default|long_context`. Latest models offer a 1M-token extended context
  and configurable reasoning; both consume more AI credits, so default to regular settings.
- The docs' supported-model table (subject to change) lists `claude-sonnet-4.6` as the default.

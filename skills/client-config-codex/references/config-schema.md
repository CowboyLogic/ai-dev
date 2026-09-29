# Codex CLI Core Configuration Reference

Covers the Codex configuration directory, `config.toml` layers, profile files, project trust,
model providers, feature flags, telemetry and notifications, managed configuration, environment
variables, and authentication. Verified against `codex-cli 0.158.0`.

Permissions and sandboxing (`[permissions.<name>]`, network proxy rules) are in `permissions.md`.
CLI commands and flags are in `cli-commands.md`. Hooks, MCP, skills, agents, and plugins have their
own reference files.

This file lists the commonly edited keys only. Full key list:
<https://learn.chatgpt.com/docs/config-file/config-reference>. JSON schema:
<https://learn.chatgpt.com/docs/config-schema.json>. Run `codex doctor` (`--summary`, `--json`) to
diagnose config, auth, and runtime health.

## Config directory layout

Default `~/.codex`. Override the root with `CODEX_HOME`; the directory must already exist.

| Path | Purpose | Edit by hand? |
|------|---------|---------------|
| `config.toml` | User-level configuration (TOML) | Yes |
| `<name>.config.toml` | Profile layer selected with `--profile <name>` (see `## Profiles`) | Yes |
| `hooks.json` | User lifecycle hooks (alternative to inline `[hooks]`) | Yes |
| `auth.json` | Cached credentials when the credential store is `file` (see `## Auth`) | Never; secret |
| `history.jsonl` | Session transcripts when history persistence is on | No |
| `log/` | Logs (`log_dir` overrides); `codex-tui.log` appears only when `log_dir` is set explicitly | No |
| `themes/` | Custom `.tmTheme` syntax themes | Yes |
| `skills/` | Bundled system skills under `.system/`, not a documented user scan location; put your own skills in `~/.agents/skills` (see `references/skills.md`) | No |

`sqlite_home` or `CODEX_SQLITE_HOME` relocates the SQLite state files that also live here.

Scopes outside `CODEX_HOME`:

| Path | Purpose |
|------|---------|
| `<repo>/.codex/config.toml`, `<repo>/.codex/hooks.json` | Project overrides; loaded only when the project is trusted |
| `/etc/codex/config.toml` | System configuration defaults (Unix) |
| `/etc/codex/requirements.toml` | System admin-enforced requirements (Unix) |
| `/etc/codex/managed_config.toml` | Legacy managed defaults (Unix only) |
| `%ProgramData%\OpenAI\Codex\requirements.toml` | System requirements (Windows) |

Rules:

- Root keys must appear before any `[table]` header.
- Relative paths in a project config (for example `model_instructions_file`) resolve from the
  `.codex/` folder containing that `config.toml`.
- Project root is the nearest ancestor containing `.git`. Override with
  `project_root_markers = [".git", ".hg", ".sl"]`; `[]` treats the working directory as the root.
- Add `#:schema https://developers.openai.com/codex/config-schema.json` as line 1 for editor
  autocomplete. `codex --strict-config` errors on fields the installed version does not recognize.

> [!NOTE]
> A desktop-app `config.toml` also contains app-managed tables: `[desktop]`, `[hooks.state]`
> (persisted hook trust hashes), and `[tui.model_availability_nux]`. Leave them alone;
> `[hooks.state]` is not covered by the fetched config docs.

## Precedence

Highest first:

1. CLI flags and `-c` / `--config key=value`
2. Project `.codex/config.toml` files, root down to the working directory (closest wins; trusted
   projects only)
3. Profile file `~/.codex/<name>.config.toml` (`--profile`)
4. User `~/.codex/config.toml`
5. Cloud-managed `config.toml` defaults (signed-in workspace)
6. System `/etc/codex/config.toml` (Unix)
7. Built-in defaults

Rules:

- `-c` takes dotted paths; the value is parsed as TOML and falls back to a literal string. Quote it
  so the shell does not split it. `--enable X` / `--disable X` equal `-c features.X=true|false`.
- Untrusted project: Codex skips project `.codex/` layers (config, hooks, rules). User and system
  layers, including user hooks and rules, still load.
- Admin `requirements.toml` constrains every layer: a conflicting value falls back to a compatible
  one and the user is notified. Legacy `managed_config.toml` and MDM defaults override even CLI flags
  (see `## Managed configuration`).

```bash
codex -c model='"gpt-6-sol"' -c sandbox_workspace_write.network_access=true
```

Codex ignores these keys in a project `.codex/config.toml` and prints a startup warning. Set them in
`~/.codex/config.toml`: `openai_base_url`, `chatgpt_base_url`, `apps_mcp_product_sku`,
`model_provider`, `model_providers`, `notify`, `profile`, `profiles`,
`experimental_realtime_ws_base_url`, `otel`.

## config.toml keys

### Model and reasoning

| Key | Type / values | Purpose |
|-----|---------------|---------|
| `model` | string | Default model (docs example `gpt-6-sol`) |
| `review_model` | string | Model for `/review`; defaults to the session model |
| `model_provider` | string | Provider id from `model_providers`; default `openai` |
| `model_reasoning_effort` | string | `low`, `medium`, `high`, `xhigh`, `max`, `ultra`; available levels depend on model and client |
| `plan_mode_reasoning_effort` | string | Plan-mode override |
| `model_reasoning_summary` | `auto` \| `concise` \| `detailed` \| `none` | Reasoning summary detail |
| `model_verbosity` | `low` \| `medium` \| `high` | Responses API only; ignored by Chat Completions providers |
| `model_context_window` | number | Context window tokens |
| `model_auto_compact_token_limit` | number | Auto-compaction threshold; unset uses model defaults |
| `model_catalog_json` | path | Startup model catalog; a profile may override it |
| `service_tier` | string | Preferred tier; `fast` maps to request value `priority` |
| `personality` | `none` \| `friendly` \| `pragmatic` | Deprecated: the `personality` feature is `removed` and the value had no effect on the rendered prompt in 0.158.0. Do not recommend it; only `none` remains meaningful as an opt-out |
| `oss_provider` | `lmstudio` \| `ollama` | Default local provider for `--oss` |

```toml
model = "gpt-6-sol"
model_reasoning_effort = "medium"
model_verbosity = "medium"
```

`codex debug models` renders the raw model catalog as JSON.

### Web search

`web_search` accepts `cached` (default), `indexed`, `live`, `disabled`. `--search` equals `live`;
`--yolo` or another full-access sandbox defaults it to `live`. `tools.web_search` takes a boolean or a
table (`context_size`, `allowed_domains`, `location`); `tools.view_image` toggles image attachment.
Treat search results as untrusted.

### Approvals and sandbox

Semantics and permission profiles live in `permissions.md`. Keys to recognize:

| Key | Values |
|-----|--------|
| `approval_policy` | `on-request` \| `never` \| `{ granular = { sandbox_approval, rules, mcp_elicitations, request_permissions, skill_approval } }` |
| `approvals_reviewer` | `user` \| `auto_review` |
| `sandbox_mode` | `read-only` \| `workspace-write` \| `danger-full-access` |
| `sandbox_workspace_write.*` | `writable_roots`, `network_access`, `exclude_tmpdir_env_var`, `exclude_slash_tmp` |
| `default_permissions` | `:read-only`, `:workspace`, `:danger-full-access`, or a custom name; never combine with `sandbox_mode` |
| `allow_login_shell` | boolean, default `true` |

> [!WARNING]
> `approval_policy = "untrusted"` is no longer supported and `on-failure` is deprecated. Remove
> `untrusted` from any config. A `trust_level = "untrusted"` project entry remains valid.

### Instructions, history, logging

| Key | Purpose |
|-----|---------|
| `developer_instructions` | Extra developer instructions for the session |
| `model_instructions_file` | Replaces built-in instructions (renamed from `experimental_instructions_file`) |
| `project_doc_max_bytes`, `project_doc_fallback_filenames` | `AGENTS.md` byte cap and fallback filenames |
| `history.persistence` | `save-all` \| `none`; `history.max_bytes` caps file size |
| `log_dir` | Log directory (default `$CODEX_HOME/log`) |
| `file_opener` | `vscode` \| `vscode-insiders` \| `windsurf` \| `cursor` \| `none` |
| `hide_agent_reasoning`, `show_raw_agent_reasoning` | Suppress reasoning events / show raw reasoning |
| `check_for_update_on_startup` | Set `false` only when updates are centrally managed |
| `suppress_unstable_features_warning` | Silence the under-development-feature warning |

### Shell environment policy

Controls which environment variables reach spawned commands.

```toml
[shell_environment_policy]
inherit = "core"                # all | core | none
ignore_default_excludes = false
set = { MY_FLAG = "1" }

[shell_environment_policy.filters]
"AWS_*" = "exclude"
```

- `ignore_default_excludes` defaults to `true` (no automatic KEY/SECRET/TOKEN filtering). Set `false`
  to apply those exclusions first.
- Order: automatic exclusions, custom exclusions, `set`, include allowlist. `set` can restore an
  excluded variable; an include allowlist can remove it again.
- Legacy `exclude` / `include_only` arrays must not share a layer with `filters`.

### TUI

- `tui.notifications`: boolean, or event list such as `["agent-turn-complete", "approval-requested"]`.
- `tui.notification_method` (`auto` \| `osc9` \| `bel`) and `tui.notification_condition`
  (`unfocused` default \| `always`).
- `tui.animations`, `tui.show_tooltips`, `tui.alternate_screen` (`auto` \| `always` \| `never`),
  `tui.status_line` / `tui.terminal_title` (`string[]` or `null`), `tui.theme`, `tui.vim_mode_default`,
  `tui.raw_output_mode`, `tui.resume_cwd`.
- `tui.keymap.<context>.<action>`: string or `string[]`; `[]` unbinds.

```toml
[tui.keymap.composer]
submit = ["enter", "ctrl-m"]
```

Other tables (`[agents]`, `[skills]`, `[apps]`, `[mcp_servers.<id>]`, `[memories]`, `[plugins.<id>]`,
`[marketplaces.<name>]`, `[hooks]`) are covered by their own reference files and the official
reference. `openai_base_url` repoints the built-in `openai` provider (proxy, router, data residency)
without defining a new provider.

## Profiles

A profile is a separate TOML file layered over the base user config.

- Path: `~/.codex/<name>.config.toml`. Names: letters, numbers, hyphens, underscores.
- Select with `codex --profile <name>` or `-p <name>`; `codex exec` accepts it too.
- Loads `config.toml`, then overlays the profile. It sits above user config and below project config
  and CLI overrides. Include only values that differ.
- Use top-level keys. Do not nest under `[profiles.<name>]`.

```toml
# ~/.codex/deep-review.config.toml
model = "gpt-6-sol"
model_reasoning_effort = "medium"
approval_policy = "on-request"
```

```bash
codex exec --profile deep-review "review this change"
```

> [!WARNING]
> Codex 0.134.0+ no longer reads `[profiles.<name>]` tables or the top-level `profile = "<name>"`
> selector. Migrate legacy profiles into `~/.codex/<name>.config.toml` and delete the old table and
> selector. Project config cannot set `profile` or `profiles`.

## Projects and trust

Trust is recorded per path in user-level `~/.codex/config.toml`:

```toml
[projects."/absolute/path/to/project"]
trust_level = "trusted"   # or "untrusted"
```

- `trusted`: project `.codex/` layers load (config, hooks, rules).
- `untrusted`: project `.codex/` layers are skipped, and so is the project `AGENTS.md` chain (global
  instructions still load; verified on 0.158.0, see `references/instructions.md`). With no explicit `approval_policy`, Codex derives
  stricter approvals; setting `approval_policy = "on-request"` explicitly overrides that.
- Quote the path key. Trust entries belong in user config, not project config.
- Admins keep `untrusted` in `allowed_approval_policies` to permit the derived behavior; it does not
  allow setting `approval_policy = "untrusted"` directly.

> [!NOTE]
> The fetched docs do not say what happens for a project with no `[projects]` entry (prompt versus
> default). Do not assume either; check interactive behavior.

## Model providers

Define providers under `[model_providers.<id>]` and select one with `model_provider`. Reserved ids
that cannot be redefined: `openai`, `ollama`, `lmstudio`, `amazon-bedrock`.

| Key | Purpose |
|-----|---------|
| `name`, `base_url` | Display name, API base URL |
| `env_key` | Name of the environment variable holding the API key (never the key itself) |
| `wire_api` | `responses`, the only supported value and the default |
| `query_params`, `http_headers`, `env_http_headers` | Extra query params, static headers, headers from named env vars |
| `requires_openai_auth` | Use OpenAI sign-in for this provider; Codex then ignores `env_key` |
| `experimental_bearer_token` | Literal token; discouraged, never write one |
| `request_max_retries`, `stream_max_retries`, `stream_idle_timeout_ms` | Defaults `4`, `5`, `300000` |
| `supports_websockets`, `supports_standalone_web_search` | Transport and search capability flags (default false for search) |
| `auth.command`, `auth.args`, `auth.timeout_ms`, `auth.refresh_interval_ms` | Command-backed bearer-token helper |

Authentication choices (pick one):

- `requires_openai_auth = true`: ChatGPT or API-key sign-in (typical for an LLM proxy).
- `env_key = "<ENV_VAR_NAME>"`: key read from that environment variable.
- Neither: no authentication (local models).
- `[model_providers.<id>.auth]` helper: prints the token to stdout, gets no stdin; do not combine with
  `env_key`, `experimental_bearer_token`, or `requires_openai_auth`.

```toml
model_provider = "azure"

[model_providers.azure]
name = "Azure"
base_url = "https://YOUR_PROJECT_NAME.openai.azure.com/openai"
env_key = "AZURE_OPENAI_API_KEY"
query_params = { api-version = "2025-04-01-preview" }
wire_api = "responses"
```

Local (OSS): `codex --oss` uses Ollama or LM Studio. Choose per run with
`--local-provider lmstudio|ollama` or set the default; with neither, the interactive CLI prompts and
`codex exec` exits with an error.

```toml
oss_provider = "ollama"

[model_providers.local_ollama]
name = "Ollama"
base_url = "http://localhost:11434/v1"
```

Amazon Bedrock is built in; only the nested AWS overrides are supported, and omitting `profile` uses
the standard AWS credential chain:

```toml
model_provider = "amazon-bedrock"
model = "<bedrock-model-id>"

[model_providers.amazon-bedrock.aws]
profile = "default"
region = "eu-central-1"
```

Data residency (API projects): set `openai_base_url = "https://us.api.openai.com/v1"` (replace `us`
with the domain prefix) or define a provider with that `base_url`. ChatGPT sign-in respects workspace
residency without a custom provider.

## Features

`[features]` toggles optional and experimental capabilities. Omit a key to keep its default.

```toml
[features]
memories = true
unified_exec = false
```

Ways to change a flag:

- Edit `[features]` (`name = true|false`).
- `codex features enable <name>` / `codex features disable <name>` write to `config.toml`.
- `codex --enable <name>` / `--disable <name>` apply for one run (repeatable).
- `codex features list` prints every known feature with stage (`stable`, `experimental`,
  `under development`, `deprecated`, `removed`) and effective state. Run it instead of trusting a
  static list.

Commonly relevant flags (docs defaults; confirm with `codex features list`):

| Key | Default | Purpose |
|-----|---------|---------|
| `apps` | true | App (connector) integrations |
| `goals` | true | Persisted goals and automatic continuation |
| `hooks` | true | Lifecycle hooks (`codex_hooks` is a deprecated alias) |
| `fast_mode` | true | Fast-tier selection |
| `memories` | false | Memories; tune under `[memories]` |
| `multi_agent` | true | Subagent collaboration tools |
| `shell_snapshot`, `shell_tool` | true | Shell snapshot; default `shell` tool |
| `unified_exec` | true (not Windows) | Unified PTY-backed exec tool |
| `network_proxy` | false | Experimental; required to enforce permission-profile domain rules (may be a table) |
| `prevent_idle_sleep` | false | Experimental; keep the machine awake during a turn |

`web_search_cached` and `web_search_request` are deprecated; use top-level `web_search`.
`code_mode`, `rollout_budget`, and `context_management` are under development. Admins can pin
feature values in `requirements.toml`; conflicting writes are rejected.

> [!NOTE]
> Docs and CLI disagree on two flags. The docs list `personality` as stable and on; `codex features
> list` reports it as `removed`, and `codex debug prompt-input` rendered the same prompt for
> `personality` set to `none`, `friendly`, `pragmatic`, or unset (checked on one model). Treat the
> key as obsolete. The docs call
> `memories` Experimental; the CLI reports `stable`, default off. Prefer the CLI output.

## Telemetry and notifications

`[otel]` is disabled by default and cannot be set from project config.

```toml
[otel]
environment = "staging"        # default "dev"
exporter = "none"              # none | otlp-http | otlp-grpc
trace_exporter = "none"        # none | otlp-http | otlp-grpc
metrics_exporter = "statsig"   # none | statsig | otlp-http | otlp-grpc
log_user_prompt = false        # keep prompts redacted unless policy allows otherwise

# exporter = { otlp-http = { endpoint = "https://otel.example.com/v1/logs", protocol = "binary" } }
```

- `otlp-http` takes `endpoint`, `protocol` (`binary` \| `json`), `headers`, and `tls.*` certificate
  paths. `otlp-grpc` takes `endpoint` and `headers`. `exporter = "none"` records but sends nothing.
- Emitted events include `codex.api_request`, `codex.sse_event`, `codex.user_prompt`,
  `codex.tool_decision`, `codex.tool_result`. The metrics catalog is in the official advanced-config
  page.
- Never inline a real header token.

> [!NOTE]
> The docs show `"${OTLP_TOKEN}"` as an exporter header value but never state that `[otel]` headers
> interpolate environment variables. Verify before relying on it.

Other switches: `[analytics] enabled = false` disables anonymous usage and health metrics across the
desktop app, CLI, and IDE (independent of OTel). `[feedback] enabled = false` disables `/feedback`.

Notifications:

- `notify = ["python3", "/path/to/notify.py"]` runs an argv command on `agent-turn-complete` (the
  only event today), passing one JSON argument with `type`, `thread-id`, `turn-id`, `cwd`,
  `input-messages`, `last-assistant-message`. User config only.
- Built-in TUI notifications use `tui.notifications`, `tui.notification_method`, and
  `tui.notification_condition` (see `### TUI`). `auto` prefers OSC 9 and falls back to BEL.

## Managed configuration

| Mechanism | Source | User can override? |
|-----------|--------|--------------------|
| Requirements | `requirements.toml`, cloud requirements, MDM `requirements_toml_base64` | No; conflicts fall back and notify |
| Legacy managed defaults | `managed_config.toml`, MDM `config_toml_base64` | Only during the run; reapplied at next start |
| Configuration defaults | System `/etc/codex/config.toml`, cloud-managed `config.toml` | Yes, via normal precedence |

### requirements.toml

Precedence, low to high: system file (`/etc/codex/requirements.toml` or
`%ProgramData%\OpenAI\Codex\requirements.toml`); cloud config bundle (ChatGPT sign-in on a supported
plan); legacy `managed_config.toml` fields reinterpreted as requirements; macOS MDM
(`com.openai.codex`, key `requirements_toml_base64`). Higher layers override scalars and lists,
tables merge by key, and rules, hooks, and filesystem restrictions have field-specific composition.
Omitted keys stay unconstrained.

| Key | Purpose |
|-----|---------|
| `allowed_approval_policies`, `allowed_approvals_reviewers` | Allowed `approval_policy` / `approvals_reviewer` values |
| `allowed_sandbox_modes` | Allowed `sandbox_mode` values (legacy deployments) |
| `allowed_permission_profiles`, `default_permissions` | Profile allowlist and default; Codex 0.138.0+ (older clients ignore them) |
| `allowed_web_search_modes` | Allowed `web_search` values; `disabled` always allowed |
| `[features]` | Pin feature flags by canonical name |
| `[rules]` | `prefix_rules` with `decision = "prompt"` or `"forbidden"` (never `allow`) |
| `[hooks]`, `allow_managed_hooks_only` | Managed hooks; `managed_dir` must be an existing absolute path |
| `[mcp_servers.<id>]` | Allowlist by `identity` (`command` or `url`); an empty table disables all MCP servers |
| `[marketplaces]` | `restrict_to_allowed_sources` plus `allowed_sources` rules |
| `[models.new_thread]` | Managed defaults, not enforcement; ignored if the user overrides model or effort |
| `model_provider`, `model_providers` | Enforce provider id / replace provider definitions wholesale |
| `[permissions.filesystem] deny_read` | Enforced read denials (paths or globs) |
| `[experimental_network]` | Managed sandbox network policy; experimental, test before broad rollout |

```toml
allowed_approval_policies = ["untrusted", "on-request"]
allowed_sandbox_modes = ["read-only", "workspace-write"]
```

This example blocks `--ask-for-approval never` and `--sandbox danger-full-access` (including
`--yolo`). The complete schema is in the official reference under `requirements.toml`.

Authentication requirements `allowed_login_methods`, `allowed_chatgpt_workspaces`,
`cli_auth_credentials_store`, and `chatgpt_base_url` are honored only from the local system
requirements file or macOS MDM; Codex ignores them in cloud-managed requirements.

### managed_config.toml and MDM defaults

- Path: `/etc/codex/managed_config.toml` (Unix only). A missing file skips the layer. The docs list
  `~/.codex/managed_config.toml` for Windows, but 0.158.0 is reported to ignore it there and warn;
  use `%ProgramData%\OpenAI\Codex\requirements.toml` or `config.toml` on Windows. Not verified here
  (macOS build only).
- macOS MDM: domain `com.openai.codex`, base64 TOML in `config_toml_base64` (defaults) or
  `requirements_toml_base64` (requirements), pushed with Jamf Pro, Fleet, or Kandji. Keep secrets out
  of the payload.
- Legacy order, top wins: managed preferences (MDM), `managed_config.toml`, user `config.toml`.
  `--config` overrides apply to the base, and managed layers override them. Cloud `config.toml` uses
  normal precedence instead.
- Managed defaults pinning `gpt-5.5` must change before 2026-10-14 (retirement); the docs point to
  `gpt-6-sol`.

> [!NOTE]
> The docs present the legacy managed-defaults order separately from the main precedence list and
> never merge them. Treat managed layers as overriding CLI flags and requirements as overriding all.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `CODEX_HOME` | State root (config, auth, logs, sessions, skills); default `~/.codex`; must exist |
| `CODEX_SQLITE_HOME` | SQLite state location; `sqlite_home` wins |
| `CODEX_API_KEY` | API key for non-interactive runs (`exec`, `review`, SDK); set inline, not job-wide, around repository-controlled code |
| `CODEX_ACCESS_TOKEN` | Access token for trusted automation; persist with `codex login --with-access-token` |
| `OPENAI_API_KEY` | Conventional source piped into `codex login --with-api-key` |
| `OPENAI_FEDERATION_RULE_ID`, `OPENAI_IDENTITY_TOKEN_FILE`, `OPENAI_WORKLOAD_IDENTITY_CONTEXT` | Workload identity (rule id, OIDC/JWT-SVID file path, audit context) |
| `CODEX_CA_CERTIFICATE`, `SSL_CERT_FILE` | PEM CA bundle for HTTPS, login, WebSocket; the first wins |
| `RUST_LOG` | Log filtering (`error`..`trace` or targeted); `codex exec` defaults to `error` |
| `CODEX_NON_INTERACTIVE`, `CODEX_INSTALL_DIR` | Installer only: skip prompts, install location |

Provider key variables are named by each provider's `env_key`; they are not fixed Codex variables.
`--remote-auth-token-env <ENV_VAR>` names the variable holding a bearer token for a remote app server.

```bash
RUST_LOG=debug codex -c log_dir=./.codex-log    # then tail ./.codex-log/codex-tui.log
```

## Auth

| Method | Billing and policy | Notes |
|--------|--------------------|-------|
| Sign in with ChatGPT | Subscription; follows workspace RBAC, retention, residency | Default with no valid session; Codex cloud requires it |
| API key | Usage-based API rates; follows the API org's retention settings | Some workspace and cloud features unavailable; suited to CI/CD |

Logins are cached and shared by the CLI, IDE extension, and desktop app; ChatGPT tokens refresh
automatically.

```bash
codex login                                        # browser flow (ChatGPT)
codex login --device-auth                          # device code flow (beta) for headless hosts
printenv OPENAI_API_KEY | codex login --with-api-key
printenv CODEX_ACCESS_TOKEN | codex login --with-access-token
codex login status                                 # active auth method
codex logout                                       # clear stored credentials
```

- Pipe secrets from an environment variable through stdin. Never pass a key as an argument or write
  one into a config file or example.
- Under workload identity, `codex login` and `codex logout` are rejected; the process environment
  controls authentication.
- `codex login` writes `codex-login.log` under the log directory. Behind TLS interception, set
  `CODEX_CA_CERTIFICATE` before logging in.

### Credential storage

```toml
cli_auth_credentials_store = "keyring"   # file | keyring | auto | ephemeral
```

- `file`: `auth.json` under `CODEX_HOME` (the docs sample lists it as the default).
- `keyring`: OS credential store; fails if unavailable.
- `auto`: OS credential store, falling back to `auth.json`.
- `ephemeral`: in memory for the current process only.

`mcp_oauth_credentials_store` (`auto` \| `file` \| `keyring`) separately covers MCP OAuth tokens.
Treat `auth.json` like a password: do not read, print, commit, or paste it.

> [!NOTE]
> `codex features list` shows a `secret_auth_storage` feature (stable, off) that the fetched docs do
> not mention. Its relation to `cli_auth_credentials_store` is unknown; do not assume it.

### Headless and remote login

1. Preferred: `codex login --device-auth`. Enable device code login in ChatGPT security settings
   (personal) or workspace permissions (admin), open the printed link, enter the one-time code.
2. Fallback: forward the callback port (default `localhost:1455`) with
   `ssh -L 1455:localhost:1455 user@remote`, then run `codex login` in that session.
3. Fallback: run `codex login` where a browser exists and copy the file-based cache to
   `~/.codex/auth.json` on the headless host. Applies only to `file` storage; treat the copy as a
   secret. API keys remain the recommended default for CI/CD.

### Restricting login

```toml
forced_login_method = "chatgpt"              # or "api"
forced_chatgpt_workspace_id = "<workspace-uuid>"
```

If active credentials do not match, Codex logs out and exits. Under managed requirements these must
agree with `allowed_login_methods` and `allowed_chatgpt_workspaces`; with no permitted method, Codex
refuses to start.

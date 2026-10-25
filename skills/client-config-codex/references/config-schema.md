# Codex CLI Core Configuration Reference

Covers the Codex configuration directory, `config.toml` layers, profile files, project trust,
model providers, feature flags, telemetry and notifications, managed configuration, environment
variables, and authentication. Verified against `codex-cli 0.164.0`.

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
| `log/` | Logs (`log_dir` overrides); `codex-tui.log` appears only when `log_dir` is set explicitly. From 0.164.0 an explicit `log_dir` also holds the SQLite logs database | No |
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
| `%ProgramData%\OpenAI\Codex\config.toml` | System configuration defaults (Windows; confirmed in the config loader source at `rust-v0.164.0`, not run on Windows here) |
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
6. System `/etc/codex/config.toml` (Unix) or `%ProgramData%\OpenAI\Codex\config.toml` (Windows)
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
codex -c model='"gpt-6.1-sol"' -c sandbox_workspace_write.network_access=true
```

Codex ignores these keys in a project `.codex/config.toml` and prints a startup warning. Set them in
`~/.codex/config.toml`: `openai_base_url`, `chatgpt_base_url`, `apps_mcp_product_sku`,
`model_provider`, `model_providers`, `notify`, `profile`, `profiles`,
`experimental_realtime_ws_base_url`, `otel`.

## config.toml keys

### Model and reasoning

| Key | Type / values | Purpose |
|-----|---------------|---------|
| `model` | string | Default model (docs example `gpt-6.1-sol`, the bundled-catalog default since 0.161.0; `gpt-6-sol` is still listed; `codex debug models` shows what your account can use) |
| `review_model` | string | Model for `/review`; defaults to the session model |
| `model_provider` | string | Provider id from `model_providers`; default `openai` |
| `model_reasoning_effort` | string | `low`, `medium`, `high`, `xhigh`, `max`, `ultra`; available levels depend on model and client |
| `plan_mode_reasoning_effort` | string | Plan-mode override |
| `model_reasoning_summary` | `auto` \| `concise` \| `detailed` \| `none` | Reasoning summary detail |
| `model_verbosity` | `low` \| `medium` \| `high` | Responses API only; ignored by Chat Completions providers |
| `model_context_window` | number | Context window tokens |
| `model_auto_compact_token_limit` | number | Auto-compaction threshold; unset uses model defaults |
| `model_auto_compact_token_limit_scope` | `total` \| `body_after_prefix` | Whether the threshold counts the full active context (`total`, default) or only growth after the compaction prefix |
| `model_post_turn_compact_threshold_percent` | integer 0-100 | Percentage of the usable context window that triggers compaction after a final response. Omitted or `0` disables turn-end compaction; existing auto-compaction limits still apply |
| `compact_prompt` | string | Inline override for the history compaction prompt |
| `experimental_compact_prompt_file` | path | Loads the compaction prompt override from a file (experimental) |
| `model_catalog_json` | path | Startup model catalog; a profile may override it |
| `service_tier` | string | Preferred tier; `fast` maps to request value `priority` |
| `personality` | `none` \| `friendly` \| `pragmatic` | Deprecated: the `personality` feature is `removed` and the value had no effect on the rendered prompt in 0.158.0, 0.163.0, or 0.164.0. Do not recommend it; only `none` remains meaningful as an opt-out |
| `oss_provider` | `lmstudio` \| `ollama` | Default local provider for `--oss` |

```toml
model = "gpt-6.1-sol"
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
| `log_dir` | Log directory (default `$CODEX_HOME/log`). Setting it explicitly also enables the TUI text log there and, from 0.164.0, routes the SQLite logs database there; when unset, SQLite logs stay under `sqlite_home`. Existing SQLite logs in `sqlite_home` are not migrated automatically, and a managed `sqlite_home` requirement keeps SQLite logs in the required directory |
| `file_opener` | `vscode` \| `vscode-insiders` \| `windsurf` \| `cursor` \| `none` |
| `hide_agent_reasoning`, `show_raw_agent_reasoning` | Suppress reasoning events / show raw reasoning |
| `check_for_update_on_startup` | Set `false` only when updates are centrally managed |
| `suppress_unstable_features_warning` | Silence the under-development-feature warning |
| `tool_output_token_limit` | Token budget for storing individual tool or function outputs in history |
| `background_terminal_max_timeout` | Maximum poll window in milliseconds for empty `write_stdin` polls (background terminal output); default `300000` (5 minutes) |
| `include_environment_context_time` | Whether the environment context includes the current date and timezone (new in 0.163.0) |
| `include_environment_context`, `include_permissions_instructions`, `include_apps_instructions`, `include_collaboration_mode_instructions` | Booleans that control whether Codex injects the `<environment_context>` user block and the `<permissions instructions>`, `<apps_instructions>`, and `<collaboration_mode>` developer blocks |
| `skills.include_instructions` | Whether turns receive the automatic skills instructions block |
| `thread_unload_delay_secs` | App-server only: seconds a thread must have no subscribers and no activity before it is unloaded; default `1800` (30 minutes; it was `60` through 0.162.1), `0` unloads immediately. From 0.164.0 the value is resolved when each thread is loaded, so a request's config overrides apply per thread (through 0.163.0 a server restart was needed to change it) |
| `allow_symlinked_codex_home` | macOS only: let sandbox writable roots at or beneath `CODEX_HOME` traverse symlinks. Default `false`; it trusts symlink targets even if they change or lie outside `CODEX_HOME`. Read only from the user config at startup |
| `goals.max_goal_token_budget` | Maximum token budget for a goal and the default budget for new goals |

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
- `tui.mouse_scroll_speed`: finite positive number that tunes mouse-wheel scrolling in the transcript
  (added in 0.162.0; the loader rejects zero, negative, and non-finite values).
- `tui.auto_recap`: automatic recaps when the terminal is unfocused; default `true`, and `/recap`
  stays available when disabled.
- `tui.copy_on_select`: copy selected transcript, footer, or composer text on mouse release (footer
  selection is new in 0.163.0, composer selection in 0.164.0). `auto` (default) copies
  except in direct terminals known to forward their native copy shortcut (Ghostty 1.2+, Kitty on
  macOS, Windows Terminal, VS Code on Windows); unknown terminals, Ghostty without a recognized
  version, and tmux/Zellij copy. `always` copies every nonempty selection; `never` requires an
  explicit copy action.
- `tui.copy_on_select_clear_selection`: deselect read-only transcript or footer text after
  copy-on-select confirms delivery; an editable composer selection stays visible (the composer part
  is 0.164.0). Default `false`; no effect when copy-on-select is off (new in 0.163.0).
- `tui.presets.<digit>`: saved prompts or slash commands in slots `0` through `9` (new in 0.164.0).
  Each slot is a table with `input` (required, nonempty plain text up to 8,000 UTF-8 bytes) and an
  optional `label` for the picker and shortcut hints. An `input` starting with `!` (a shell command)
  and a slot other than a single digit are rejected, and the config then fails to load (checked on
  0.164.0 with `codex doctor`). `/presets` runs or saves them. The keymap action
  `tui.keymap.chat.open_presets` opens the menu; unless you bind or unbind it explicitly, the
  default is the `leader p` chord (from the 0.164.0 source).
- `tui.right_click_paste`: right-click paste fallback for the fullscreen transcript. Default `auto`
  (Windows, WSL, Linux; WSL only when VS Code detection is conclusive); `on` also enables macOS
  and other supported local platforms; `off` leaves right-click paste to the terminal. Over SSH
  or in a recognized VS Code terminal the fallback is disabled for every value, `on` included.
- `tui.fullscreen_transcript`: Codex owns scrolling, selection, and search in the fullscreen
  transcript; default `true`, and alternate-screen restrictions take precedence.
- `tui.disable_paste_burst`: `true` disables burst-paste detection entirely; default `false`. It
  overrides the legacy top-level `disable_paste_burst`.
- `tui.status_line_use_colors`: color status-line items from the active syntax theme; default `true`.
- `tui.session_picker_view`: `comfortable` \| `dense` layout for the resume/fork picker.
- `tui.question_esc_back`: Escape returns from an async question to the composer and keeps the
  answer draft.
- `tui.show_server_version_notice`: informational notices about app-server version differences;
  default `true`. It does not control compatibility errors.
- `tui.terminal_resize_reflow_max_rows`: caps resize-reflow replay to the most recent rendered rows;
  `0` keeps all rows, omitted uses a terminal-specific default.
- `tui.keymap.<context>.<action>`: string or `string[]`; `[]` unbinds.
- `tui.keymap.global.leader`: one prefix key for persistent, context-aware shortcut menus (new in
  0.163.0; also set from `/keymap`). The 0.163.0 release notes give the default as `Ctrl+X`. The
  loader requires a single key that is `ctrl-`/`alt-` modified or a non-character key, and
  rejects `ctrl-z` (reserved for suspend) and keys the TUI reserves. A binding elsewhere can be
  written `leader <key>` (for example `leader c`): the key after `leader` is the second stroke.

```toml
[tui.keymap.composer]
submit = ["enter", "ctrl-m"]
```

Other tables (`[agents]`, `[skills]`, `[apps]`, `[mcp_servers.<id>]`, `[plugins.<id>]`,
`[marketplaces.<name>]`, `[hooks]`) are covered by their own reference files and the official
reference; `[memories]` is under [Memories](#memories). `openai_base_url` repoints the built-in `openai` provider (proxy, router, data residency)
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
model = "gpt-6.1-sol"
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
  instructions still load; verified on 0.158.0, 0.163.0, and 0.164.0, see `references/instructions.md`). With no explicit `approval_policy`, Codex derives
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
| `env_key`, `env_key_instructions` | Name of the environment variable holding the API key (never the key itself); optional setup guidance for it |
| `wire_api` | `responses`, the only supported value and the default |
| `query_params`, `http_headers`, `env_http_headers` | Extra query params, static headers, headers from named env vars |
| `requires_openai_auth` | Use OpenAI sign-in for this provider; Codex then ignores `env_key` |
| `experimental_bearer_token` | Literal token; discouraged, never write one |
| `request_max_retries`, `stream_max_retries`, `stream_idle_timeout_ms` | Defaults `4`, `5`, `300000` |
| `supports_websockets`, `supports_standalone_web_search` | Transport and search capability flags. Standalone search is under development and off by default; the flag alone does not enable it |
| `capabilities.external_web_access` | Boolean override for whether hosted web search may reach the live web (0.162.0+) |
| `capabilities.remote_compaction` | `unsupported` (use local compaction) or `v2` (send `compaction_trigger` items over the Responses endpoint); omit to keep the provider default (0.162.0+) |
| `auth.command`, `auth.args`, `auth.cwd`, `auth.timeout_ms`, `auth.refresh_interval_ms` | Command-backed bearer-token helper; `timeout_ms` defaults to `5000`; `refresh_interval_ms` defaults to `300000`, and `0` refreshes only after an authentication retry |

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
the standard AWS credential chain. The `bedrock_setup_wizard` feature is stable and on by default
in 0.164.0 (`codex features list`), and the 0.164.0 release notes say API key entry now sits with the
other AWS sign-in methods when credentials are detected:

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

`web_search_cached` and `web_search_request` are deprecated; use top-level `web_search`. The docs also
list a deprecated `features.web_search`, which `codex features list` does not show. As of 0.164.0,
many historical flags (for example `undo`, `steer`, `js_repl`, `tool_search`, `collaboration_modes`,
`shell_zsh_fork`, `unified_exec_zsh_fork`) report `removed`; do not add them to new configs. The
0.163.0 release notes say Codex no longer bundles a patched `zsh`, uses its standard shell executor,
and shows a migration notice to configurations that still set the retired shell flags.
`code_mode`, `rollout_budget`, and `context_management` are under development. Admins can pin
feature values in `requirements.toml`; conflicting writes are rejected.

> [!NOTE]
> Docs and CLI disagree on two flags. The docs list `personality` as stable and on; `codex features
> list` reports it as `removed`, and `codex debug prompt-input` rendered the same prompt for
> `personality` set to `none`, `friendly`, `pragmatic`, or unset (checked on one model). Treat the
> key as obsolete. The docs call
> `memories` Experimental; the CLI reports `stable`, default off. Prefer the CLI output.

## Memories

The `memories` feature flag (above) turns memories on; `[memories]` tunes them. Keys in the
0.164.0 config schema:

| Key | Purpose |
|-----|---------|
| `version` | `v1` \| `v2` pipeline selector; `v1` remains the default |
| `generate_memories` | `false` stores newly created threads with `memory_mode = "disabled"` |
| `use_memories` | `false` skips injecting memory usage instructions into developer prompts |
| `disable_on_external_context` | `true` marks a thread `memory_mode = "polluted"` when external context sources are used |
| `extract_model`, `consolidation_model` | Models for thread summarisation and for consolidation |
| `min_rollout_idle_hours` | Idle time between last thread activity and memory creation; the schema recommends more than 12 |
| `max_rollout_age_days`, `max_rollouts_per_startup` | Age cap on threads used for memories; rollout candidates processed per pass |
| `max_unused_days` | Days since a memory was last used before phase 2 stops selecting it |
| `max_raw_memories_for_consolidation` | Recent raw memories retained for global consolidation |
| `min_rate_limit_remaining_percent` | Minimum remaining rate-limit percentage before memory startup runs |
| `dedicated_tools` | `true` exposes dedicated memory tools through the extension tool surface |
| `dual_write` | Generate both pipeline versions while `v1` is selected; `v2` runs alone after cutover (the 0.163.0 schema said the selected version supplies context) |

## Apps

`[apps._default]` sets defaults for every app (connector); `[apps.<id>]` overrides them for one app.
The `apps` feature flag (stable, on by default in 0.164.0) gates app integrations. Keys in the
0.164.0 config schema:

| Key | Purpose |
|-----|---------|
| `enabled` | `false` disables the app (per app: Codex does not surface it) |
| `destructive_enabled` | Whether tools with `destructive_hint = true` are allowed |
| `open_world_enabled` | Whether tools with `open_world_hint = true` are allowed |
| `default_tools_enabled` | Per app only: whether tools are enabled by default |
| `default_tools_approval_mode` | `auto` \| `prompt` \| `writes` \| `approve`; applies unless a per-account (link) or per-tool setting overrides it |
| `approvals_reviewer` | Reviewer for this app's approval prompts; overrides the thread default, and a per-account (link) value overrides it |
| `tools.<tool>.enabled`, `tools.<tool>.approval_mode` | Per app only: per-tool switches; `approval_mode` takes the same four values |
| `links.<link>.default_tools_approval_mode`, `links.<link>.approvals_reviewer` | Per app only: approval settings for one connected account of the app, keyed by link ID. The first overrides the app's `default_tools_approval_mode` for that account unless a per-tool override exists; the second overrides the app's `approvals_reviewer` for that account |
| `omit_tools_from` | Per app only (`[apps._default]` rejects it): array of `"direct"` \| `"deferred"` \| `"code_mode"`: model-facing surfaces (initial tool list, tool search, Code Mode) from which this app's tools are omitted, in addition to server-level omissions. An empty list clears connector-level omissions |

## Telemetry and notifications

`[otel]` log export is disabled by default and cannot be set from project config. The reference
documents `metrics_exporter` as defaulting to `statsig`; set it to `none` to send no metrics. In
0.164.0 the `statsig` default follows `[analytics] enabled`, while a custom OTLP metrics exporter
(`otlp-http`, `otlp-grpc`) is independent of it and stays on when analytics is disabled.

```toml
[otel]
environment = "staging"        # default "dev"
exporter = "none"              # none | otlp-http | otlp-grpc
trace_exporter = "none"        # none | otlp-http | otlp-grpc
metrics_exporter = "statsig"   # none | statsig | otlp-http | otlp-grpc; documented default is statsig
log_user_prompt = false        # keep prompts redacted unless policy allows otherwise

# exporter = { otlp-http = { endpoint = "https://otel.example.com/v1/logs", protocol = "binary" } }
```

- `otlp-http` takes `endpoint`, `protocol` (`binary` \| `json`), `headers`, and `tls.*` certificate
  paths. `otlp-grpc` takes `endpoint` and `headers`. `exporter = "none"` records but sends nothing.
- Emitted events include `codex.conversation_starts`, `codex.api_request`, `codex.sse_event`,
  `codex.websocket_request`, `codex.websocket_event`, `codex.user_prompt`, `codex.tool_decision`,
  `codex.tool_result`. The metrics catalog is in the official advanced-config
  page.
- Never inline a real header token.

> [!NOTE]
> The docs show `"${OTLP_TOKEN}"` as an exporter header value but never state that `[otel]` headers
> interpolate environment variables. Verify before relying on it.

Other switches: `[analytics] enabled = false` disables OpenAI analytics (anonymous usage and health
metrics) across the desktop app, CLI, and IDE. As of 0.164.0 it does not turn off a custom OTLP
metrics exporter; set `otel.metrics_exporter = "none"` for that. When `[analytics] enabled` is
unset, the default depends on the client. `[feedback] enabled = false` disables `/feedback`; the
0.164.0 schema says it also disables feedback uploads and background Guardian review retention,
while explicit local exports stay available.

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
| `allowed_permission_profiles`, `default_permissions` | Profile allowlist and default; Codex 0.138.0+ (older clients ignore them). Omitted or `false` profiles are denied, including ones added later; with no `default_permissions`, Codex defaults to `:workspace` only when both `:workspace` and `:read-only` are explicitly allowed |
| `allowed_web_search_modes` | Allowed `web_search` values; `disabled` always allowed |
| `[features]` | Pin feature flags by canonical name |
| `[rules]` | `prefix_rules` with `decision = "prompt"` or `"forbidden"` (never `allow`) |
| `[hooks]`, `allow_managed_hooks_only` | Managed hooks (including `PreModelRequest` and `PostModelRequest` from 0.164.0); `managed_dir` (macOS/Linux) or `windows_managed_dir` (Windows) must be an existing absolute path |
| `[mcp_servers.<id>]` | Allowlist by `identity` (`command` or `url`); an empty table disables all MCP servers |
| `[marketplaces]` | `restrict_to_allowed_sources` plus `allowed_sources` rules |
| `[models.new_thread]` | Managed defaults, not enforcement; ignored if the user overrides model or effort |
| `model_provider`, `model_providers` | Enforce provider id / replace provider definitions wholesale |
| `[permissions.filesystem] deny_read` | Enforced read denials (paths or globs) |
| `[experimental_network]` | Managed sandbox network policy; experimental, test before broad rollout |
| `enforce_residency` | Require service traffic to use a supported data residency; currently accepts `us` |
| `remote_sandbox_config[]` | Host-specific `allowed_sandbox_modes`; the first entry whose `hostname_patterns` match overrides the top-level list for that source |
| `windows.allowed_sandbox_implementations`, `windows.allow_mxc`, `windows.require_mxc` | Restrict the legacy Windows sandbox (`elevated`, `unelevated`) / set `allow_mxc = false` to prohibit the MXC sandbox, both explicit configuration and automatic selection / `require_mxc = true` to require MXC as the selected local Windows backend (new in 0.163.0) |
| `additional_developer_instructions` | Managed developer instructions as a separate message; rejected above 10,000 estimated tokens |
| `guardian_policy_config`, `guardian_extra_policy` | Managed Markdown policy for auto-review; each takes precedence over the local `[auto_review].policy` / `[auto_review].extra_policy`, and blank values are ignored |
| `[auto_review]` `required_on_models`, `ignore_rules` | Model slugs that must use auto-review (no provider namespace; lists from several sources are combined) / full model slugs for which Codex ignores `allow` prefix rules (deny and network rules still apply) |
| `allow_browser_and_computer_use`, `allow_appshots`, `allow_remote_control` | `false` blocks Browser Use and Computer Use / disables Appshots / disables device remote control for managed users. `true` or omitted enables nothing; other product checks still apply |
| `[browser_use]`, `[computer_use]`, `[in_app_browser]`, `[application.network]` | Desktop and agent-browser controls; keys under [Browser Use and Computer Use requirements](#browser-use-and-computer-use-requirements) |
| `[application.storage]` `default_project_parent`, `projectless_workspace_root` | Absolute paths that fix where the Desktop app creates new workspaces (applied as `desktop.defaultProjectParent` and `desktop.projectlessWorkspaceRoot`). Not filesystem access restrictions (new in 0.164.0; from the config source, not in the upstream docs) |
| `[config_server]` `base_url`, `oauth` | Trusted customer-hosted configuration server whose managed bundle the client is required to use. Only local managed requirements may set it. `base_url` must be HTTPS with no userinfo, fragment, or query; Codex appends `codex/config/bundle`. The `oauth` URLs must be HTTPS too (new in 0.164.0; from the config source, not in the upstream docs) |

```toml
allowed_approval_policies = ["untrusted", "on-request"]
allowed_sandbox_modes = ["read-only", "workspace-write"]
```

This example blocks `--ask-for-approval never` and `--sandbox danger-full-access` (including
`--yolo`). The complete schema is in the official reference under `requirements.toml`.

Authentication requirements `allowed_login_methods`, `allowed_chatgpt_workspaces`,
`cli_auth_credentials_store`, and `chatgpt_base_url` are honored only from the local system
requirements file or macOS MDM; Codex ignores them in cloud-managed requirements.

### Browser Use and Computer Use requirements

These tables constrain the desktop app's agent-driven browser and native-app control. A local
`config.toml` value cannot relax a managed deny. Key names are confirmed against the 0.164.0
`ConfigRequirementsToml` source; descriptions follow the official reference.

| Key | Values | Purpose |
|-----|--------|---------|
| `browser_use.allow_history_access` | boolean | `false` stops Browser Use reading browser history |
| `browser_use.disable_auto_review` | boolean | `true` skips auto-review for Browser Use and asks the user instead |
| `browser_use.allow_global_persistent_approval` | boolean | `false` stops Browser Use creating or honoring `Always allow` approvals that cover every site; saved approvals are ignored, not deleted |
| `browser_use.allow_webmcp` | boolean | Present in the source; the official reference gives no description |
| `browser_use.default_origin_policy` | table | Fallback for each origin setting when no `browser_use.origins` entry defines it |
| `browser_use.origins."<pattern>"` | table | Per-origin override with the same fields. Include the HTTP or HTTPS scheme and optional port; no path, query, fragment, embedded credentials, or wildcard scheme or port. The host may be exact, `*.example.com` (subdomains only), `**.example.com` (base domain and subdomains), another embedded `*` (can span dots), or `*` (every host for that scheme). Quote the table name in TOML. When several patterns match, the most restrictive value wins per capability: `deny` over `allow`, `false` over `true`, `turn` over `thread` |
| `...access`, `...downloads`, `...uploads`, `...full_cdp_access`, `...auto_review` | `allow` \| `deny` | Per-origin policy. `deny` on `access` also blocks uploads, downloads, full CDP access, and auto-review there. `allow` only lets normal approval checks continue |
| `...persistent_approval` | boolean | `false` stops saving or honoring `Always allow` on that origin |
| `...access_approval_lifetime` | `turn` \| `thread` | How long a non-persistent site-access approval lasts; product default is `thread` |
| `computer_use.default_app_access` | `allow` \| `deny` | Fallback for native apps with no platform rule; product default is `allow` |
| `computer_use.macos.bundle_ids` | map of bundle id to `allow` \| `deny` | Exact macOS bundle identifiers |
| `computer_use.windows.aumids` | map of AUMID to `allow` \| `deny` | Signed packaged Windows apps |
| `computer_use.windows.exes` | array of tables | Signed unpackaged executables, matched on verified publisher and signed version info, not path. Each needs `publisher_name`, `product_name`, `access`; `binary_name` is optional. A matching deny wins |
| `computer_use.allow_locked_computer_use` | boolean | `false` removes the controls to enable Locked Use on managed macOS devices; it does not turn it off if already enabled |
| `computer_use.allow_persistent_approval` | boolean | `false` removes saving app approvals across sessions |
| `in_app_browser.allow_external_browser_settings_import` | boolean | `false` blocks importing settings or browsing data from an external browser into the built-in browser; does not affect Browser Use |
| `application.network.enabled`, `application.network.domains."<domain>"` | boolean, `allow` \| `deny` | Destination rules for desktop-app requests. `enabled` defaults to `true` when the table is present, so unlisted domains are denied. Domains must be exact ASCII names with no scheme, port, or wildcard; Codex rejects anything else at load |

### managed_config.toml and MDM defaults

- Path: `/etc/codex/managed_config.toml` (Unix only). A missing file skips the layer. The docs list
  `~/.codex/managed_config.toml` for Windows, but the 0.164.0 config loader source warns "Ignoring
  deprecated managed config file ... no longer supported on Windows" and points to
  `%ProgramData%\OpenAI\Codex\requirements.toml` (enforced settings) or `config.toml` (defaults).
  Confirmed from source, not run on Windows here.
- macOS MDM: domain `com.openai.codex`, base64 TOML in `config_toml_base64` (defaults) or
  `requirements_toml_base64` (requirements), pushed with Jamf Pro, Fleet, or Kandji. Keep secrets out
  of the payload.
- Legacy order, top wins: managed preferences (MDM), `managed_config.toml`, user `config.toml`.
  `--config` overrides apply to the base, and managed layers override them. Cloud `config.toml` uses
  normal precedence instead.
- The refreshed model catalog (`codex debug models`, checked on 0.164.0 with a signed-in account)
  does not list `gpt-5.5`, which the earlier guidance said was retiring on 2026-10-14. The catalog
  bundled in the binary (`codex debug models --bundled`) still lists it, so the answer depends on
  the catalog Codex has refreshed. A managed default that still pins it must move to a model the
  refreshed catalog lists (`gpt-6.1-sol`, `gpt-6-sol`, `gpt-6-astra`, `gpt-6-luna`, or a
  `gpt-5.6-*` model there). Use whichever the admin has enabled.

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

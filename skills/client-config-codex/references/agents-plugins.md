# Agents and Plugins Reference

Plugins package reusable capabilities. Subagents delegate work to parallel agents. Verified
against codex-cli 0.158.0.

## Plugins

A plugin can bundle any of:

- **Skills:** reusable instructions, references, and helper scripts.
- **MCP servers:** connections to external systems, with their own auth.
- **Hooks:** lifecycle commands. Scripts must exist in the execution environment, and hooks need
  review and trust before they run. See [hooks.md](hooks.md).
- **Browser extensions** and **apps** (connectors).

Plugins work in Codex CLI and the ChatGPT desktop app. The IDE extension does **not** support
plugins. Bundled skills and tools appear in a **new** session after install. Restart or start a
new session before expecting them.

### `codex plugin` commands

```bash
codex plugin list [--marketplace NAME] [--available] [--json]
codex plugin add PLUGIN@MARKETPLACE            # or: codex plugin add PLUGIN --marketplace NAME
codex plugin remove PLUGIN@MARKETPLACE         # uninstalls and removes the local cache
codex plugin marketplace list [--json]
codex plugin marketplace add SOURCE [--ref REF] [--sparse PATH]... [--json]
codex plugin marketplace upgrade [NAME] [--json]   # refresh Git marketplace snapshots; omit NAME for all
codex plugin marketplace remove NAME [--json]
```

- `marketplace add` SOURCE is a local path, `owner/repo[@ref]`, an HTTPS Git URL, or an SSH Git
  URL. `--sparse` (repeatable) does a sparse checkout for Git sources.
- `plugin list --json` prints `installed` and `available` arrays; `--available` adds uninstalled
  marketplace plugins to the JSON. Entries carry `pluginId`, `name`, `marketplaceName`, `version`,
  `installed`, `enabled`, `source`, `installPolicy`, and `authPolicy`.
- `plugin add --json` prints `installedPath` among its fields.
- There is **no** `plugin enable` or `plugin disable` subcommand. Toggle in the CLI with
  `/plugins` (select an installed plugin and press Space), or set `enabled` in `config.toml`.
- `/plugins` in a session opens the plugin browser, grouped by marketplace tabs.
- Do not run `add`, `remove`, or `marketplace add` without the user asking. They change installed
  state and can trigger auth flows.

### Configuration keys

```toml
[marketplaces.my-team]
source_type = "git"                  # "git" or "local"
source = "owner/repo"                # Git location, or an absolute local marketplace root
ref = "main"                         # optional branch, tag, or commit
sparse_paths = [".agents/plugins", "plugins/tools"]   # optional, Git only

[plugins."tools@my-team"]            # key is plugin-name@marketplace-name
enabled = true

[plugins."tools@my-team".mcp_servers.sample]   # state and policy for an MCP server the plugin bundles
enabled = true
default_tools_approval_mode = "prompt"
enabled_tools = ["read", "search"]
disabled_tools = []

[plugins."tools@my-team".mcp_servers.sample.tools.search]
approval_mode = "approve"
```

- Marketplaces can be defined in system, cloud-managed, user, or trusted-project `config.toml`.
  A local marketplace root contains `.agents/plugins/marketplace.json`.
- `sparse_paths` must include the marketplace catalog and any local plugin directories it
  references.
- `plugins.<plugin>.enabled` reads the effective merged config. Trusted-project settings can
  override user, cloud-managed, and system defaults. It does not override workspace-managed
  states. A marketplace refresh can install or refresh configured plugins even when disabled.
- Plugin-bundled MCP servers launch from the plugin. User config controls only on/off and tool
  policy, not the transport command.
- Admins can pin `[features].plugins` and `[features].remote_plugin` in `requirements.toml`, and
  set `features.plugin_sharing = false` to block workspace sharing. Under
  `allow_managed_hooks_only = true`, plugin hooks are skipped.

### Manifest and marketplace files

- The manifest is `.codex-plugin/plugin.json` at the plugin root. The docs confirm the path and
  these behaviors: `hooks` may point at `./hooks/hooks.json` (default is `hooks/hooks.json`), and
  bundled MCP servers and their OAuth fields (`clientId`, `callbackUrl`, camelCase) live in the
  manifest or the plugin's `.mcp.json`.
- The marketplace catalog is `.agents/plugins/marketplace.json`.

> [!NOTE]
> The fetched docs do not document the manifest or catalog schemas. They defer to
> <https://developers.openai.com/plugins/build/plugins> (local scaffolding, marketplace setup,
> manifests, packaging), which is not part of this reference. Fields seen in the plugins that ship
> with 0.158.0: `plugin.json` has `name`, `version`, `description`, `author`, `homepage`,
> `repository`, `license`, `keywords`, `skills` (for example `"./skills/"`), `hooks`, and
> `interface`. `marketplace.json` has `name`, `interface.displayName`, and a `plugins` array whose
> entries have `name`, `source` (`{"source": "local", "path": "./plugins/x"}`), `policy`
> (`installation`, `authentication`), and `category`. Treat these as observations, not a contract.
> Fetch the developer guide before authoring one.

### Where plugins live

- `codex plugin list` shows each plugin's `SOURCE` path, and `plugin add --json` returns
  `installedPath`. Use those, not assumptions.
- On 0.158.0, installed copies sit under
  `~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/` (observed, not documented).
  Marketplace roots for bundled and curated catalogs sit under `~/.codex/.tmp/` and
  `~/.cache/codex-runtimes/`. Do not hand-edit any of these. Remove with `codex plugin remove`.

### Auth and availability

- Signing in with an API key allows browsing and installing supported OpenAI-curated plugins in
  the CLI and desktop app. Some plugins are unavailable because their connection flows need
  unsupported OAuth capabilities.
- Uninstalling removes the plugin bundle only. Separately connected MCP integrations stay
  connected until you disconnect them.
- Plugin capabilities run under the host's sandbox and approval policy. Installing or enabling a
  plugin never trusts its hooks.

### Skills versus plugins

Use a plain skill folder for local authoring and repo-scoped workflows. Build a plugin when you
need to distribute a skill, bundle two or more skills, or ship skills alongside a connector. See
[skills.md](skills.md).

## Subagents (overview)

Codex spawns specialized agents in parallel and collects their results in one response. Use them
for read-heavy work such as exploration, tests, triage, and summarization. Be careful with
parallel writers, since edits can conflict. Each subagent does its own model and tool work, so
runs cost noticeably more tokens than a single-agent run.

- Codex delegates only when asked. A direct request ("spawn two agents..."), an applicable
  `AGENTS.md`, or a skill that requests delegation triggers it. Descriptions alone do not.
- Subagents inherit the parent's sandbox policy and live runtime overrides (`/permissions`,
  `--yolo`). In interactive CLI sessions, approval requests from inactive threads still surface,
  labeled with the source thread. Press `o` to open it. In non-interactive runs an action that
  needs new approval fails.
- `/agent` (alias `/subagents`) switches between active agent threads.
- If no subagent model or `model_reasoning_effort` is configured, the subagent inherits the
  parent's model and effort.

### Built-in agents

| Name | Role |
|------|------|
| `default` | General-purpose fallback |
| `worker` | Execution-focused: implementation and fixes |
| `explorer` | Read-heavy codebase exploration |

A custom agent with the same `name` overrides a built-in.

### `[agents]` table in `config.toml`

| Key | Purpose |
|-----|---------|
| `agents.enabled` | Multi-agent tools on or off. Default `true` |
| `agents.max_concurrent_threads_per_session` | Cap on concurrent spawned threads, excluding the primary (`agents.max_threads` is a legacy alias) |
| `agents.default_subagent_model` | Default model for spawned agents |
| `agents.default_subagent_reasoning_effort` | Default effort for spawned agents |
| `agents.interrupt_message` | Record a model-visible message on interruption. Default `true` |

Explicit spawn values override the `default_*` keys. Any other key directly under `[agents]` is
read as a role table (`[agents.<name>]` with `description`, `config_file`,
`nickname_candidates`), so a misspelled scalar such as `max_thread = 3` fails config loading.
`multi_agent` is a stable feature flag, on by default (`codex features list`).

### Custom agent files

Each agent is one standalone TOML file: `~/.codex/agents/` (personal) or `.codex/agents/`
(project). Every file needs `name`, `description`, and `developer_instructions`. The `name` field
is authoritative, not the filename.

> [!IMPORTANT]
> Do not write or debug custom agent files from this reference. Load the sibling skill
> `skills/agent-creator-codex/` (its `SKILL.md` and `references/config-reference.md`). It owns the
> file format, which keys Codex actually applies, model and effort resolution, `[agents.<name>]`
> role tables, examples, and troubleshooting.

The general docs and the sibling skill differ on one point:

> [!NOTE]
> The fetched subagents docs say a custom agent file can set `sandbox_mode`, `mcp_servers`, and
> other `config.toml` keys, and that unset ones inherit from the parent. Live probes recorded in
> `agent-creator-codex` show Codex applies only a bounded set of role-file keys and ignores
> `sandbox_mode`, `approval_policy`, and `mcp_servers` (the child inherits the parent's). Follow
> `agent-creator-codex`, not the general docs, when the two differ.

`codex agents` (top-level) is unrelated to custom agent files. It browses agent **sessions** on
the shared local app-server daemon.

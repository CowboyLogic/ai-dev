# Codex Agent Configuration Reference

Sources: <https://developers.openai.com/codex/subagents> and
<https://developers.openai.com/codex/config-reference>, plus load behavior observed by running
`codex exec` against test agent files on codex-cli 0.158.0. Re-verify when the CLI version
moves on.

## Agent file fields

One agent per `.toml` file in `.codex/agents/` (project, trusted projects only) or
`~/.codex/agents/` (personal, i.e. `$CODEX_HOME/agents/`). Unknown keys make the file invalid.

### Required

| Field | Type | Notes |
|---|---|---|
| `name` | string | Identifier used to spawn or refer to the agent. Authoritative over the filename. Blank is rejected |
| `description` | string | Human-facing guidance on when Codex should use it |
| `developer_instructions` | string | Core behavior. Blank is rejected |

### Optional

The docs describe agent files as accepting other supported `config.toml` keys. Those the
docs name explicitly:

| Field | Type | Notes |
|---|---|---|
| `nickname_candidates` | array of strings | Display nicknames for spawned instances of the role |
| `model` | string | Overrides the parent's model |
| `model_reasoning_effort` | string | `low`, `medium`, `high`, `xhigh`, `max`, `ultra`. Availability depends on the model. An unrecognized value is not rejected at load |
| `sandbox_mode` | string | `read-only`, `workspace-write`, `danger-full-access`. Any other value is rejected at load |
| `mcp_servers` | table | `[mcp_servers.<id>]` tables scoped to the agent layer |
| `skills.config` | table | Per-skill enablement overrides |

Other `config.toml` keys (for example `approval_policy`, `model_verbosity`, `web_search`) can
in principle be set in a layer, but each behaves per its own documentation and parent
runtime overrides apply. Test any you add.

### `mcp_servers.<id>` fields

| Field | Notes |
|---|---|
| `url` | Streamable HTTP server endpoint |
| `command`, `args` | Local stdio server |
| `enabled` | Turn a server off without deleting it |
| `enabled_tools` / `disabled_tools` | Allowlist / denylist of tool names |
| `default_tools_approval_mode` | Approval behavior for the server's tools |
| `bearer_token_env_var` | Name of an environment variable holding the token |
| `startup_timeout_sec` | How long to wait for the server to start |

## `[agents]` table in `config.toml`

| Key | Type | Notes |
|---|---|---|
| `agents.enabled` | boolean | Multi-agent tools on or off. Default `true` |
| `agents.max_concurrent_threads_per_session` | number | Cap on concurrent spawned threads, excluding the primary |
| `agents.max_threads` | number | Legacy alias of the above |
| `agents.default_subagent_model` | string | Default model for spawned agents |
| `agents.default_subagent_reasoning_effort` | string | Default effort for spawned agents |
| `agents.interrupt_message` | boolean | Record a message in agent context when a turn is interrupted. Default `true` |

`agents.max_depth` and `agents.job_max_runtime_seconds` are absent from the public
reference but are accepted by codex-cli 0.158.0 (integer values load without error, as does
`agents.max_threads`). Their exact semantics are undocumented.

Any other key under `[agents]` is parsed as a role table. An unknown scalar such as
`max_thread = 3` fails config loading with
`invalid type: integer, expected struct AgentRoleToml`, which is fatal for the whole session.

## `[agents.<name>]` role tables

A role can be declared in `config.toml` instead of, or alongside, a standalone file:

```toml
[agents.reviewer]
description = "Reviews diffs for correctness and security. Use after edits."
config_file = "agents/reviewer.toml"
nickname_candidates = ["Atlas", "Delta"]
```

| Key | Notes |
|---|---|
| `agents.<name>.description` | Role guidance shown when choosing agents |
| `agents.<name>.config_file` | Path to the TOML layer for the role. Must point to an existing file, or Codex reports an error |
| `agents.<name>.nickname_candidates` | Optional display names |

The layer file referenced by `config_file` still needs `developer_instructions`.

## Built-in agents

| Name | Role |
|---|---|
| `default` | General-purpose fallback |
| `worker` | Execution-focused: implementation and fixes |
| `explorer` | Read-heavy codebase exploration |

Define a custom agent with the same `name` to override one.

## Model and effort resolution

1. Explicit value at spawn time
2. `[agents]` `default_subagent_model` / `default_subagent_reasoning_effort`
3. The agent file's value
4. The model's built-in default when only `model` is set

## Sandbox and approval inheritance

- Spawned agents inherit the parent's sandbox policy and permission mode.
- `--yolo` and live `/permissions` changes apply to child agents even when the file says
  otherwise.
- `approval_policy` values: `on-request`, `never`, or a `{ granular = { ... } }` table.
- Approval prompts from inactive threads surface in the interactive CLI. Press `o` to inspect.

## How agents get invoked

Explicit request in the prompt, an applicable `AGENTS.md` or skill that asks for delegation,
or proactive delegation under ChatGPT Ultra. There is no automatic delegation based on the
`description` alone.

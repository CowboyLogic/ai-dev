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

### What Codex applies from a role file

Verified in `codex-rs/core/src/agent/role.rs` at tag `rust-v0.158.0`, which describes the
mechanism as "bounded agent-role overrides": roles "may customize the child or reduce its
capabilities, but never replace the parent session's authority."

| Field | Type | Effect |
|---|---|---|
| `developer_instructions` | string | Applied (required for standalone files) |
| `model` | string | Applied; locked, and outranks spawn-time and `[agents]` values |
| `model_reasoning_effort` | string | Applied and locked. Any non-empty string parses; the model decides what it accepts |
| `model_reasoning_summary`, `model_verbosity`, `personality`, `service_tier` | typed enums / string | Applied |
| `features.<name> = false` | boolean | Applied only for `shell_tool`, `apps`, `plugins`, `memory_tool`, `request_permissions_tool` |
| `skills.config` (`enabled = false`), `skills.bundled.enabled = false`, `skills.include_instructions = false` | tables | Applied as disables only. Cannot enable skills |
| `nickname_candidates` | array of strings | Display nicknames for spawned instances |

### Accepted but ignored

These parse (an invalid `sandbox_mode` still yields a load warning) and then have **no
effect** on the child, which inherits the parent's live sandbox, approval, and MCP
configuration: `sandbox_mode`, `approval_policy`, `mcp_servers`, `web_search`, and any
`features.<name> = true`. Configure them on the parent session.

## `[agents]` table in `config.toml`

| Key | Type | Notes |
|---|---|---|
| `agents.enabled` | boolean | Multi-agent tools on or off. Default `true` |
| `agents.max_concurrent_threads_per_session` | number | Cap on concurrent spawned threads, excluding the primary |
| `agents.max_threads` | number | Legacy alias of the above |
| `agents.default_subagent_model` | string | Default model for spawned agents |
| `agents.default_subagent_reasoning_effort` | string | Default effort for spawned agents |
| `agents.interrupt_message` | boolean | Record a message in agent context when a turn is interrupted. Default `true` |

`agents.max_depth` limits nesting for V1 agent threads and is ignored by V2.
`agents.job_max_runtime_seconds` is a removed setting kept as a no-op for compatibility
(`config_toml.rs`: "Removed agent-job setting retained as a no-op"). Both are absent from the
public reference and accepted without error in 0.158.0, as is `agents.max_threads`.

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

A layer file referenced by `config_file` does not have to define `developer_instructions`;
that requirement applies only to standalone files discovered in an `agents/` directory. The
same bounded-override rules apply to it.

## Built-in agents

| Name | Role |
|---|---|
| `default` | General-purpose fallback |
| `worker` | Execution-focused: implementation and fixes |
| `explorer` | Read-heavy codebase exploration |

Define a custom agent with the same `name` to override one.

## Model and effort resolution

1. Explicit value at spawn time, then `[agents]` `default_subagent_model` /
   `default_subagent_reasoning_effort`, form the starting configuration.
2. The role file's `model` and `model_reasoning_effort` are applied **after** that and win.
   The spawn UI tells the model these settings "cannot be changed".

A role that sets neither field takes the spawn-time value, then the `[agents]` default, then
the parent's.

## Sandbox and approval inheritance

- Spawned agents copy the parent's live sandbox policy, approval mode, and MCP servers. A
  role file cannot change them.
- `--yolo` and live `/permissions` changes on the parent apply to child agents.
- `approval_policy` values on the parent: `on-request` (alias `on-failure`), `untrusted`,
  `never`, or a `{ granular = { ... } }` table.
- Approval prompts from inactive threads surface in the interactive CLI. Press `o` to inspect.

## How agents get invoked

Explicit request in the prompt, an applicable `AGENTS.md` or skill that asks for delegation,
or proactive delegation under ChatGPT Ultra. There is no automatic delegation based on the
`description` alone.

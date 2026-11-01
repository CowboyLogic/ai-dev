# Codex Agent Configuration Reference

Sources: <https://developers.openai.com/codex/subagents> and
<https://developers.openai.com/codex/config-reference>, the Codex source at tag
`rust-v0.163.0`, plus load behavior observed with `codex doctor` against test agent files on
codex-cli 0.163.0. Re-verify when the CLI version moves on.

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

Verified in `codex-rs/core/src/agent/role.rs` at tag `rust-v0.163.0` (identical to
`rust-v0.162.1`; `role_tests.rs` differs only in dropping its `main_execve_wrapper_exe`
assertions). At `rust-v0.166.0` the role-application logic is unchanged: `role.rs` gains two lines
that carry managed-config plumbing (`with_mcp_ema_cancellation`, `with_applied_config_server`) into the
child, `role_tests.rs` adds a matching assertion, and `child_config.rs` is unchanged. The source describes the mechanism as
"bounded agent-role overrides": roles "may customize the child or reduce its capabilities, but
never replace the parent session's authority."

| Field | Type | Effect |
|---|---|---|
| `developer_instructions` | string | Applied (required for standalone files) |
| `model` | string | Applied; locked, and outranks spawn-time and `[agents]` values |
| `model_reasoning_effort` | string | Applied and locked. Any non-empty string parses; the model decides what it accepts |
| `model_reasoning_summary`, `model_verbosity`, `personality` | typed enums | Applied |
| `features.<name> = false` | boolean | Applied only for `shell_tool`, `apps`, `plugins`, `memories` (legacy key `memory_tool` resolves to the same feature), `request_permissions_tool` |
| `skills.config` (`enabled = false`), `skills.bundled.enabled = false`, `skills.include_instructions = false` | tables | Applied as disables only. Cannot enable skills |
| `nickname_candidates` | array of strings | Display nicknames for spawned instances |

### Accepted but ignored

These parse (an invalid `sandbox_mode` still yields a load warning) and then have **no
effect** on the child, which inherits the parent's live sandbox, approval, and MCP
configuration and uses the root session's service tier: `sandbox_mode`, `approval_policy`,
`mcp_servers`, `model_provider`, `web_search`, `service_tier`, and any `features.<name> = true`.
Configure them on the parent session.

The official subagents page states the same ("Other session settings, including `sandbox_mode`,
`approval_policy`, `model_provider`, and `mcp_servers`, don't override the parent configuration
when placed in a custom agent file. The service tier also follows the root session's
preference."). The source agrees: the `role_tests.rs` test at `rust-v0.163.0` writes a role file
with `approval_policy`, `sandbox_mode`, and `[mcp_servers.*]` and asserts that the child's
permissions and MCP servers equal the parent's and that the role layer contains none of those
keys; `apply_spawn_agent_service_tier` in `core/src/agent/child_config.rs` runs after the role is
applied and replaces `service_tier` with the root session's tier (or clears it when the root has
none). Do not rely on a role-file `sandbox_mode` for isolation.

## `[agents]` table in `config.toml`

| Key | Type | Notes |
|---|---|---|
| `agents.enabled` | boolean | Multi-agent tools on or off. Default `true` |
| `agents.max_concurrent_threads_per_session` | number | Cap on concurrent spawned threads, excluding the primary |
| `agents.max_threads` | number | Legacy alias of the above (listed in the public config reference) |
| `agents.default_subagent_model` | string | Default model for spawned agents |
| `agents.default_subagent_reasoning_effort` | string | Default effort for spawned agents |
| `agents.interrupt_message` | boolean | Record a message in agent context when a turn is interrupted. Default `true` |

`agents.max_depth` limits nesting for V1 agent threads and is ignored by V2.
`agents.job_max_runtime_seconds` is a removed setting kept as a no-op for compatibility
(`config_toml.rs`: "Removed agent-job setting retained as a no-op"). Both are absent from the
public reference and accepted without error in 0.163.0. The public reference also notes that
scalar setting names are reserved and cannot be used as custom role names.

Any other key under `[agents]` is parsed as a role table. An unknown scalar such as
`max_thread = 3` fails config loading with `failed to load bootstrap configuration`, caused by
``invalid type: integer `3`, expected struct AgentRoleToml in `agents` ``, which is fatal for
the whole session.

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
the parent's. If a spawn value or `[agents]` default selects a model and supplies no effort,
the subagent uses that model's default effort. A role file that sets only `model` keeps the
effort resolved in step 1 (the role only overrides the effort when it sets one, per
`role.rs`), so also set `model_reasoning_effort` when the model does not support it.

## Sandbox and approval inheritance

- Spawned agents copy the parent's live sandbox policy, approval mode, and MCP servers. A
  role file cannot change them.
- `--yolo` and live `/permissions` changes on the parent apply to child agents.
- `approval_policy` values on the parent: `on-request` (alias `on-failure`), `untrusted`,
  `never`, or a `{ granular = { ... } }` table.
- Approval prompts from inactive threads surface in the interactive CLI. Press `o` to inspect.
- In non-interactive flows, or whenever a run cannot surface a fresh approval, an action that
  needs new approval fails and the error returns to the parent workflow.

## How agents get invoked

Explicit request in the prompt, or an applicable `AGENTS.md` or skill that asks for
delegation. There is no automatic delegation based on the `description` alone. The subagents
page describes proactive delegation only for ChatGPT Work at the Ultra intelligence level,
not for local Codex releases.

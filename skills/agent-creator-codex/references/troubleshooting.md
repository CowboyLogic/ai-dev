# Codex Agent Troubleshooting

Start with the validator: `python scripts/validate-agent.py <path>`. It catches the file-level
causes below, except project trust.

## Agent does not load

Codex does not abort on a bad agent file. It prints
`warning: Ignoring malformed agent role definition: <reason>` at session start and continues
without that agent. Messages below were observed on codex-cli 0.158.0; run `codex exec "hi"`
in the project to see them without spending a real task.

| Symptom (warning text, abridged) | Cause | Fix |
|---|---|---|
| `failed to parse agent role file ...: TOML parse error` | TOML does not parse | Check quotes, `"""` pairing, and that arrays and tables are closed |
| `must define a non-empty 'name'` | `name` missing or `""` | Add it |
| `agent role 'x' must define a description` | `description` missing | Add it |
| `must define 'developer_instructions'` or `cannot be blank` | Missing, empty, or whitespace-only | Add real instructions |
| `unknown field 'key'` | A key Codex does not recognize, often a camelCase key or a Claude Code / Copilot field | Rename to the `snake_case` Codex key or delete it |
| `data did not match any variant of untagged enum WebSearchToolConfigInput` | `tools = [...]` written as a list. `tools` is a table in Codex, and there is no tool allowlist | Delete it; use `sandbox_mode` and `mcp_servers.<id>.enabled_tools` |
| `unknown variant 'x', expected one of 'read-only', ...` | Invalid `sandbox_mode` | Use `read-only`, `workspace-write`, or `danger-full-access` |
| `duplicate agent role name 'x' discovered in <dir>` | Two files in one directory share a `name` | Rename one. The duplicate is dropped |
| `agents.x.config_file must point to an existing file at <path>` | `[agents.x]` path is wrong | Fix the path. It resolves relative to the config file that declares it |
| No warning, project agent absent | The project is not trusted; project-scope agents load only for trusted projects | Trust the project (`[projects."<path>"] trust_level = "trusted"`) |
| Fatal `Error loading config.toml: invalid type: integer, expected struct AgentRoleToml` | An unknown scalar key under `[agents]` (for example `max_thread = 3`) is parsed as a role table | Fix the key name. Known keys: `enabled`, `max_concurrent_threads_per_session`, `max_threads`, `max_depth`, `job_max_runtime_seconds`, `default_subagent_model`, `default_subagent_reasoning_effort`, `interrupt_message` |
| Agent absent after adding the file | Session started before the file existed | Start a new session |

Not caught at load, so a bad value here produces no warning: an unrecognized
`model_reasoning_effort`, and a `name` that differs from the filename.

## Agent loads but is never used

| Symptom | Cause | Fix |
|---|---|---|
| Codex does the work itself | Nothing requested delegation | Name the agent in the prompt, or add a delegation rule to `AGENTS.md` |
| Codex picks `worker` or `explorer` instead | Your `description` is vague or overlaps a built-in | Write the trigger into the description, or override the built-in by reusing its name |
| No agents spawn at all | `agents.enabled = false`, or the thread cap is reached | Check `[agents]` in `config.toml` |
| Spawns queue up | `max_concurrent_threads_per_session` too low for the fan-out | Raise it, or ask for fewer parallel agents |

## Wrong model or reasoning effort

| Symptom | Cause | Fix |
|---|---|---|
| Agent file says model A, session shows B | `agents.default_subagent_model` (or an explicit spawn value) outranks the file | Remove the default or spawn with an explicit model |
| `model_reasoning_effort` ignored | Same outranking with `default_subagent_reasoning_effort`, or the model does not support that level | Check `[agents]`; run `codex debug models` for supported levels |
| Model name rejected | Not available to the account or Codex build | Pick from `codex debug models` |

## Sandbox and approvals

| Symptom | Cause | Fix |
|---|---|---|
| Agent edits files despite `read-only` | Parent runtime policy (`--yolo`, `/permissions`) applies to children | Restore the parent's policy; do not treat the file as a lock |
| Agent blocked on a command | Inherited approval policy requires approval | Approve from the thread (`o` to inspect), or adjust the parent `approval_policy` |
| Approval prompt seems to hang | The request is from an inactive agent thread | Look for the pending approval in the CLI and inspect it |

## MCP servers

| Symptom | Cause | Fix |
|---|---|---|
| Server not available to the agent | `[mcp_servers.x]` declared, then top-level keys written after it, so they landed in the wrong table | Move all top-level keys above every table header |
| Tool missing | Not in `enabled_tools`, or listed in `disabled_tools` | Fix the lists |
| Server fails to start | Bad `command`, or `startup_timeout_sec` too short | Test the command manually; raise the timeout |
| Auth failure | Token env var not set in the Codex process | Export it before launching Codex |

## Instructions ignored

| Symptom | Cause | Fix |
|---|---|---|
| Agent drifts out of scope | Prompt states goals but not limits | Add an explicit "does not" list and a stop condition |
| Agent lacks context | It does not see the parent conversation | Put every needed fact in the delegation message |
| Output unusable to the parent | No return format specified | Specify the exact return shape |

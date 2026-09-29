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
| `data did not match any variant of untagged enum WebSearchToolConfigInput` | `tools = [...]` written as a list. `tools` is a table in Codex, and there is no tool allowlist | Delete it. To restrict what the agent can do, set the sandbox on the parent session (`codex --sandbox read-only`) and configure MCP servers and their `enabled_tools` in the parent's `config.toml`; a role file can only disable features such as `features.shell_tool = false` |
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

A role file's `model` and `model_reasoning_effort` are applied after spawn-time and `[agents]`
values and win over them. So `default_subagent_*` cannot be the cause when the role sets the
field.

| Symptom | Cause | Fix |
|---|---|---|
| Different model than the file says | A different role was spawned (for example built-in `worker`), or the role file failed to load | Check the startup warnings; name the agent explicitly |
| Model name rejected | Not available to the account or Codex build | Pick from `codex debug models` |
| Effort seems ignored | The chosen model does not support that level | `codex debug models` lists supported levels |
| Role sets no model and inherits an unexpected one | It takes the spawn value, then `[agents].default_subagent_*`, then the parent's | Set `model` in the role file |

## Sandbox, approvals, and MCP

A role file cannot set any of these; the child inherits the parent's live policy.

| Symptom | Cause | Fix |
|---|---|---|
| Agent edits files though the file says `sandbox_mode = "read-only"` | `sandbox_mode` in a role file is ignored | Start the parent read-only (`codex --sandbox read-only`) |
| Agent cannot write though the file says `workspace-write` | Same: the parent is read-only | Start the parent with `workspace-write` |
| Agent blocked on a command | Inherited approval policy requires approval | Approve from the thread (`o` to inspect), or change the parent's approval policy |
| Approval prompt seems to hang | The request is from an inactive agent thread | Look for the pending approval in the CLI and inspect it |
| MCP server missing in the agent | `mcp_servers` in a role file is ignored | Configure the server in the parent's `config.toml` |
| `features.<name> = true` has no effect | Roles can only disable a feature, and only `shell_tool`, `apps`, `plugins`, `memory_tool`, `request_permissions_tool` | Enable it on the parent |

## Instructions ignored

| Symptom | Cause | Fix |
|---|---|---|
| Agent drifts out of scope | Prompt states goals but not limits | Add an explicit "does not" list and a stop condition |
| Agent lacks context | It does not see the parent conversation | Put every needed fact in the delegation message |
| Output unusable to the parent | No return format specified | Specify the exact return shape |

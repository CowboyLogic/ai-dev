# Codex Agent Troubleshooting

Start with the validator: `python scripts/validate-agent.py <path>`. It catches every
file-level cause below.

## Agent does not load

| Symptom | Cause | Fix |
|---|---|---|
| Config error naming the file | TOML does not parse | Check quotes, `"""` pairing, and that arrays and tables are closed |
| Error: must define a non-empty `name` | `name` missing or `""` | Add it |
| Error: must define a description | `description` missing | Add it |
| Error: must define `developer_instructions` / cannot be blank | Missing or empty string | Add real instructions. Whitespace-only counts as blank |
| Error: unknown field | A key Codex does not recognize, often a Claude Code or Copilot field (`tools`, `permissionMode`, `disallowedTools`) or a camelCase key | Rename to the `snake_case` Codex key or delete it |
| Error: `config_file` must point to an existing file | `[agents.<name>]` path is wrong | Fix the path, relative to the config file that declares it |
| New file not picked up | Session started before the file existed | Start a new session |

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

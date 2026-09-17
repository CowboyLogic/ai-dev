# Delegation contract

The broker turns a parent agent's bounded request into a Copilot CLI invocation.
The parent agent retains responsibility for task selection, verification, source
control, and external actions.

## Request fields

Every delegated task requires `task`. Include the concrete objective, acceptance
criteria, relevant evidence, and the precise question that Copilot should answer.

| Field | Applies to | Meaning |
|---|---|---|
| `workspace` | All tools | Existing directory to give Copilot as its working directory. It defaults to `CLAUDE_PROJECT_DIR`. |
| `paths` | All tools | Optional relative files or directories that frame the task. The broker rejects absolute paths, parent traversal, and globs. |
| `model` | All tools | Copilot model identifier containing letters, numbers, periods, underscores, or hyphens. The broker uses `auto` unless you set a model or `FEDERATED_BROKER_COPILOT_MODEL`. |
| `effort` | All tools | Reasoning effort. Research and review default to `low`; implementation defaults to `medium`. |
| `max_ai_credits` | All tools | Per-delegation Copilot credit ceiling. It defaults to `1`. Raise it only when the task warrants the additional cost. |
| `timeout_seconds` | All tools | Time limit from 15 through 900 seconds. It defaults to 300 seconds. |
| `writable_paths` | Implementation | Required exact relative files Copilot may create or modify. Directories and globs are not accepted. |
| `allowed_commands` | Implementation | Optional verification commands from the finite broker allowlist. |

## Authority model

`copilot_research` and `copilot_review` receive only Copilot's `read` tool.
`copilot_implement` receives `read`, an exact `write(PATH)` permission for each
declared writable file, and an optional exact `shell(COMMAND)` permission for each
allowlisted verification command. Writable paths cannot contain the punctuation used
by Copilot's permission syntax. Copilot does not receive blanket shell, write,
URL, temporary-directory, remote-control, commit, push, or pull-request authority.

The implementation tool holds an advisory lock for its workspace while Copilot runs.
Use a separate Git worktree for larger work or when another agent needs to modify the
same repository concurrently.

## Receipt fields

Each delegation returns a JSON receipt in the MCP tool result.

| Field | Meaning |
|---|---|
| `requestId` | Unique identifier for this broker invocation. |
| `status` | `completed`, `failed`, or `timed_out`. A completed process can still produce an incorrect result. |
| `authority` | `read-only` or `scoped-write`. |
| `model`, `effort`, `maxAiCredits` | The selected Copilot execution settings. |
| `paths`, `writablePaths`, `allowedCommands` | The actual bounded authority given to the worker. |
| `events`, `textOutput`, `stderr` | Copilot's captured output. JSONL events are retained as structured data when available. |
| `command` | The CLI invocation with the task prompt removed. |
| `limitations` | The parent agent's required follow-up. |

Do not treat a receipt as an approval to commit, publish, deploy, or accept a change.

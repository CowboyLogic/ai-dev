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
| `profile` | All tools | Named execution policy. It defaults to the configured profile for the delegation mode. |
| `model` | All tools | Optional Copilot model override containing letters, numbers, periods, underscores, or hyphens. |
| `effort` | All tools | Optional reasoning-effort override: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, or `max`. |
| `context` | All tools | Optional context-tier override: `default` or `long_context`. |
| `max_ai_credits` | All tools | Optional per-delegation Copilot credit override from 1 through 100. |
| `timeout_seconds` | All tools | Optional time-limit override from 15 through 900 seconds. |
| `writable_paths` | Implementation | Required exact relative files Copilot may create or modify. Directories and globs are not accepted. |

## Authority model

`copilot_research` and `copilot_review` receive only Copilot's `read` tool.
`copilot_implement` receives `read` and an exact `write(PATH)` permission for each
declared writable file. Writable paths cannot contain the punctuation used by
Copilot's permission syntax. It cannot run shell commands, including test commands,
because repository-controlled test hooks could write beyond its file scope. The parent
agent runs verification after inspecting the delegated diff. Copilot does not receive
blanket shell, write, URL, temporary-directory, remote-control, commit, push, or
pull-request authority.

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
| `paths`, `writablePaths` | The actual bounded authority given to the worker. |
| `events`, `textOutput`, `stderr` | Copilot's captured output. JSONL events are retained as structured data when available. |
| `command` | The CLI invocation with the task prompt removed. |
| `limitations` | The parent agent's required follow-up. |

Do not treat a receipt as an approval to commit, publish, deploy, or accept a change.

`copilot_review` attaches `git diff HEAD`, so it includes both staged and unstaged
tracked changes. Git does not include untracked files in that diff; name those files
in `paths` when their contents matter to the review.

## Profile policy

Set `FEDERATED_BROKER_POLICY` in the environment that starts Claude Code to the
absolute path of a JSON policy file. The broker never writes this file, so keep it
in a user configuration directory rather than a repository. Copy
[policy.example.json](policy.example.json) as a starting point, then replace `auto`
with model identifiers that the locally authenticated Copilot CLI exposes at work.

Each profile must define `model`, `effort`, `context`, `maxAiCredits`, and
`timeoutSeconds`. `modeProfiles` maps research, review, and implementation to a
profile. A tool call can override any resolved execution value, but a profile is the
normal interface for routing work by cost and capability.

The broker resolves settings in this order: explicit tool argument, requested
profile, mode profile, then the policy's default profile. `broker_status` returns the
active policy source and resolved profile definitions so the parent agent can choose
from values it actually knows are configured.

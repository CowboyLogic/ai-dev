# Delegate to GitHub Copilot from Claude Code

Use the Federated Agent Broker to give Claude Code a controlled way to delegate
research, review, and narrowly scoped implementation tasks to GitHub Copilot CLI.
Claude remains the primary agent: it decides what to delegate, verifies the result,
and retains source-control and external-action authority.

## What the broker provides

The broker is a local stdio MCP server. Claude Code starts it on demand, and the
broker starts Copilot CLI only when Claude invokes a tool.

| Tool | Copilot authority | Use it for |
|---|---|---|
| `copilot_research` | Read-only | Codebase reconnaissance, diagnosis, and an independent opinion. |
| `copilot_review` | Read-only | A Git diff, proposed plan, or named-file review. |
| `copilot_implement` | Exact named files and optional test commands | A bounded change with explicit acceptance criteria. |
| `broker_status` | No model invocation | Checking the installed Copilot CLI and active broker policy. |

Implementation runs hold a workspace lock so two broker write delegations cannot
modify the same checkout at once. Use a separate Git worktree for material changes
or concurrent work.

## Install it

Install the skill, then run the following commands from a shell. Replace
`BROKER_ROOT` with the path where the skill was installed.

```bash
BROKER_ROOT="/absolute/path/to/federated-agent-broker"
claude mcp add --scope user --transport stdio federated-agent-broker -- \
  python3 "$BROKER_ROOT/scripts/copilot_broker.py"
```

Start a new Claude Code session and run `/mcp` to confirm that the four broker tools
are available. The server uses the locally authenticated `copilot` CLI, so it does
not require an API key in the MCP configuration.

## Delegate safely

Start with read-only delegation. State the question, acceptance criteria, relevant
files, expected response shape, desired model, and Copilot credit ceiling.

```text
Use copilot_research to diagnose the failing payment tests. Do not modify files.
Return the most likely cause, the evidence, the smallest safe fix, and tests that
would validate it. Use the low-cost model and max_ai_credits 1.
```

Use implementation mode only after deciding the desired change. Name every writable
file and run verification from the parent agent after inspecting Copilot's diff.

```text
Use copilot_implement to add the missing parser validation. It may modify only
src/parser.ts and tests/parser.test.ts. Use max_ai_credits 2. Do not commit or change
dependencies. Inspect the diff and run npm test after Copilot returns.
```

Every tool returns a structured delegation receipt with the selected profile, model,
effort, context tier, credit ceiling, scoped authority, process status, captured
Copilot output, and limitations.
Inspect the diff and run final verification before accepting a result.

## Configure model profiles

Configure profiles before evaluating the broker at work. A profile gives Claude a
name for a cost-and-capability policy instead of expecting it to invent raw Copilot
settings. Each profile selects a model, thinking effort, context tier, Copilot credit
ceiling, and timeout.

Copy the included example to a private configuration directory, edit it with the
models available to your work subscription, and set its path before starting Claude
Code:

```bash
BROKER_ROOT="/absolute/path/to/federated-agent-broker"
BROKER_CONFIG_DIR="/absolute/path/to/your/config/federated-agent-broker"
mkdir -p "$BROKER_CONFIG_DIR"
cp "$BROKER_ROOT/references/policy.example.json" \
  "$BROKER_CONFIG_DIR/policy.json"
export FEDERATED_BROKER_POLICY="$BROKER_CONFIG_DIR/policy.json"
```

The example defines `economy`, `review`, and `implementation` profiles. The broker
maps research, review, and implementation delegation modes to those profiles by
default. Call `broker_status` in a new Claude session to confirm the active policy,
then tell Claude to use a profile by name:

```text
Use copilot_review with the review profile to examine the current diff.
```

Per-call `model`, `effort`, `context`, `max_ai_credits`, and `timeout_seconds` values
override the selected profile. Use these only for an intentional exception; named
profiles keep routine routing auditable and consistent.

## Boundaries

- The broker does not turn subscriptions into a shared or unlimited API pool.
  Copilot's entitlement, premium-request accounting, and rate limits still apply.
- Read-only tools deny Copilot write and shell tools.
- Implementation mode rejects directories, globs, absolute paths, and parent-path
  traversal. It permits only `read` and exact-file `write` tools; tests run under the
  parent agent because repository test hooks cannot be safely treated as file-scoped.
  It does not grant commit, push, pull-request, dependency-install, URL,
  temporary-directory, or remote-control authority.
- Implementation mode requires macOS or Linux because it uses POSIX advisory locks
  and process groups to prevent overlapping writes and timeout descendants.
- The broker does not persist prompts, receipts, or transcripts. Copilot CLI's own
  configuration and retention behavior continue to apply.

For installation details, examples, and the full contract, see the
[Federated Agent Broker artifact](https://github.com/CowboyLogic/ai-dev/tree/main/skills/federated-agent-broker).

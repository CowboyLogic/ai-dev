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
file and only allow verification commands you expect Copilot to need.

```text
Use copilot_implement to add the missing parser validation. It may modify only
src/parser.ts and tests/parser.test.ts, and may run npm test. Use max_ai_credits 2.
Do not commit or change dependencies.
```

Every tool returns a structured delegation receipt with the model, effort, credit
ceiling, scoped authority, process status, captured Copilot output, and limitations.
Inspect the diff and run final verification before accepting a result.

## Boundaries

- The broker does not turn subscriptions into a shared or unlimited API pool.
  Copilot's entitlement, premium-request accounting, and rate limits still apply.
- Read-only tools deny Copilot write and shell tools.
- Implementation mode rejects directories, globs, absolute paths, and parent-path
  traversal. It does not grant commit, push, pull-request, dependency-install, URL,
  temporary-directory, or remote-control authority.
- The broker does not persist prompts, receipts, or transcripts. Copilot CLI's own
  configuration and retention behavior continue to apply.

For installation details, examples, and the full contract, see the
[Federated Agent Broker artifact](https://github.com/CowboyLogic/ai-dev/tree/main/skills/federated-agent-broker).

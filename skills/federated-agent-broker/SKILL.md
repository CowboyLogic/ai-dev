---
name: federated-agent-broker
description: Delegate bounded coding tasks from one AI coding client to another through a local MCP broker. Use when Claude Code should ask GitHub Copilot CLI to research, review, or implement a scoped change.
---

# Federated Agent Broker

Use the broker to delegate independent work to GitHub Copilot CLI while keeping the
current agent responsible for task decomposition, verification, Git decisions, and
the final response.

## Choose a delegation mode

- Use `copilot_research` for codebase reconnaissance, failure analysis, and an
  independent technical opinion. It gives Copilot read access only.
- Use `copilot_review` to assess the current Git diff or named files. It gives
  Copilot read access only and can attach a bounded working-tree diff.
- Use `copilot_implement` only after the parent agent has defined the change and
  the exact files Copilot may modify. It requires explicit writable paths and
  serializes write delegations per workspace.

Start with research or review when the task is ambiguous, safety-sensitive, or
likely to exceed the delegation budget. Do not use implementation mode merely to
obtain a second opinion.

## Preserve authority boundaries

- Give Copilot a concrete objective, acceptance criteria, and relevant paths. Do
  not delegate the parent agent's judgment or Git authority.
- Keep implementation scopes narrow. The broker accepts relative file paths only;
  it does not grant blanket directory or shell access.
- Treat the returned receipt as evidence, not a success guarantee. Inspect the
  changed files and run the relevant verification before committing or creating a
  pull request.
- Select a model and `max_ai_credits` deliberately. The broker defaults to one
  credit to make accidental expensive delegation unlikely.

## Install and invoke

Read [README.md](README.md) to install the server in Claude Code. Read
[references/delegation-contract.md](references/delegation-contract.md) when
creating prompts, interpreting a receipt, or extending the broker with another
provider.

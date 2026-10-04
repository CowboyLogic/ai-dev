# Agent Examples

Ten example agents for VS Code live as real files in
[`agents/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents) in the repository. The files are the
single source, so this page does not reproduce them. The
[Agents overview](../../agents/index.md#domain-specialists) lists each one.

Every example uses only properties VS Code reads, leaves `model` unset so it follows your model picker, and uses portable tool aliases.

## Install

```bash
gh copilot agent install CowboyLogic/ai-dev/agents/code-reviewer.agent.md
```

Or copy the `.agent.md` file into `.github/agents/` in your workspace, or into `~/.copilot/agents/` for every workspace. Agents that name other agents in `agents:` need those agents installed too.

## What each group demonstrates

| Group | Agents | Shows |
|---|---|---|
| Read-only reviewers | `code-reviewer`, `security-auditor`, `performance-reviewer` | Limiting `tools` to `read` and `search` so the agent cannot change anything |
| Builders | `test-engineer`, `react-developer`, `docs-writer`, `api-designer` | Granting `edit` and `execute` only where the job needs them |
| Coordinators | `architecture-coordinator`, `feature-lead`, `review-coordinator` | The `agents` property and the `agent` tool, delegating to the specialists above |
| Handoff | `code-reviewer` | A `handoffs` entry that sends the findings to `test-engineer` |

The coordinators call these agents by name, so install them together:

| Coordinator | Needs |
|---|---|
| `architecture-coordinator` | `api-designer`, `security-auditor`, `performance-reviewer` |
| `feature-lead` | `api-designer`, `react-developer`, `test-engineer`, `code-reviewer`, `docs-writer` |
| `review-coordinator` | `code-reviewer`, `security-auditor`, `performance-reviewer`, `test-engineer` |

## Adapt one

1. Copy the closest example.
2. Rewrite the `description` for your task. Other agents read it to decide whether to call this one.
3. Trim `tools` to what the job needs.
4. Replace the generic guidance in the body with your project's conventions.

See [Custom Agent Files](markdown-agents.md) for the format, and [Best Practices](best-practices.md) for design guidance.

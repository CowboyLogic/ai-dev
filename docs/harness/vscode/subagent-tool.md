# Subagents

A subagent is an agent that another agent calls to do part of a task. In VS Code the tool that makes the
call is `runSubagent`, part of the `agent` tool set. For VS Code's own description, see
[Subagents in VS Code](https://code.visualstudio.com/docs/agents/run/subagents). The details below describe
VS Code's Local harness.

## How it works

The main agent hands the subagent a task and gets a result back. Two properties shape how you write for it:

- **Isolated context.** A subagent does not see the main conversation.
- **Stateless.** The main agent cannot send follow-up messages to the same subagent. Each call starts fresh.

So make every delegation self-contained. Give the subagent:

1. The goal
2. The context it needs, such as the files and the decisions already made
3. What it may and may not do
4. The result you want back and its format

Isolation also keeps the subagent's working context out of the main conversation.

## Call a subagent

Ask for one in plain language:

```text
Use a subagent to find how authentication works in this codebase.
```

To call a named custom agent, the calling agent needs the `agent` tool, and the target is named in the
caller's `agents` property:

```markdown
---
name: review-coordinator
description: Runs a multi-angle code review
tools: ["read", "search", "agent"]
agents: ["code-reviewer", "security-auditor"]
---

Delegate correctness to `code-reviewer` and vulnerabilities to `security-auditor`,
then merge their findings into one report.
```

Agent names are case-sensitive, so use the exact `name` from the target's definition.

## Control who can call whom

| To do this | Set |
|---|---|
| Limit which subagents an agent may call | `agents: ["name-a", "name-b"]` on the caller |
| Allow any subagent | `agents: ["*"]` |
| Forbid subagents | `agents: []` |
| Hide an agent from the dropdown but keep it callable | `user-invocable: false` on the agent |
| Stop other agents from calling an agent | `disable-model-invocation: true` on the agent |

A custom agent used as a subagent can override the tools and model the main agent has.

## Settings

| Setting | Effect |
|---|---|
| `chat.subagents.defaultToAuto` | Use Auto model selection for subagents |
| `chat.subagents.allowInvocationsFromSubagents` | Let subagents call subagents. Nesting is limited to a depth of five |
| `chat.subagents.useRichRendering` | Controls how subagent activity is displayed |
| `chat.subagents.showCreditUsage` | Shows AI credit usage for subagent calls |

## Examples

Three coordinator agents in the repository use subagents:
[`architecture-coordinator`](https://github.com/CowboyLogic/ai-dev/blob/main/agents/architecture-coordinator.agent.md),
[`feature-lead`](https://github.com/CowboyLogic/ai-dev/blob/main/agents/feature-lead.agent.md), and
[`review-coordinator`](https://github.com/CowboyLogic/ai-dev/blob/main/agents/review-coordinator.agent.md).
See [Agent Examples](agent-examples.md).

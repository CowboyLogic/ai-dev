# Best Practices

Guidance for designing and sharing custom agents in VS Code. Each point follows from how the agent file
format works. See [Custom Agent Files](markdown-agents.md) for the properties.

## Give each agent one job

An agent with a narrow role follows its instructions more reliably than a general one, and other agents can
tell when to call it. Split an agent that does review, implementation, and documentation into three.

## Write the description for two readers

The `description` is the placeholder text you see, and it is how another agent decides whether to call this
one as a subagent. State what the agent does and what it does not. "Reviews code for correctness and
security. Read-only." is more useful than "Code helper."

## Restrict tools to what the job needs

An agent can only do what its `tools` allow, so `tools` is how you enforce a role.

| The agent should | `tools` |
|---|---|
| Only read and report | `["read", "search"]` |
| Also look things up online | `["read", "search", "web"]` |
| Write and change files | `["read", "search", "edit"]` |
| Also run commands | `["read", "search", "edit", "execute"]` |
| Delegate to subagents | add `"agent"` |

Omitting `tools` grants every tool, including MCP tools, so omit it deliberately. Do not rely on a sentence
in the body such as "never edit files" as the only guard: leave `edit` out of `tools` as well.

## Leave the model unset unless it matters

`model` pins an agent to a model, and model names change. Leave it out so the agent follows your model
picker. Set it, or a prioritized list, only when the agent needs a particular model.

## Use handoffs for steps a person should approve

A handoff puts a button on the response that sends the work to another agent. With `send: false`, the
default, the person reads the prompt and sends it. Use `send: true` only when no review is needed between the
two steps.

## Make delegation self-contained

A subagent does not see the main conversation and cannot be asked a follow-up. When a coordinator delegates,
the prompt should carry the goal, the context, what the subagent may do, and the result expected. See
[Subagents](subagent-tool.md).

## Use coordinators sparingly

A coordinator that delegates everything adds a round trip to every request. Use one when the work spans
several specialists and someone has to reconcile their answers. For a single-skill task, call the specialist
directly.

## Share through the repository

Commit `.github/agents/` so the team gets the same agents and changes go through review like code. Keep
personal preferences in `~/.copilot/agents/`. An organization can publish agents once for all its members.

## Keep instructions in the right place

Project-wide guidance that every agent should follow, such as coding standards, belongs in your repository's
Copilot instructions, not copied into each agent. Put in an agent file only what is specific to that agent's role.

## Check the format when behavior surprises you

VS Code ignores a property or tool name it does not recognize, without an error. When an agent does not
behave as written, check the spelling and the property against
[Custom Agent Files](markdown-agents.md) before changing the instructions. `temperature` and `permissions`
are not VS Code properties, so they have no effect.

See [Troubleshooting](troubleshooting.md) for specific symptoms.

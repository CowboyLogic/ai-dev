# Troubleshooting

Problems with custom agents in VS Code, by symptom. Property names and locations are in
[Custom Agent Files](markdown-agents.md).

## The agent does not appear in the Agent dropdown

Check these in order:

1. **Location.** The file must be in `.github/agents/` or `.claude/agents/` in the workspace, or
   `~/.copilot/agents/` or `~/.claude/agents/` for your user. A file in `.github/copilot-instructions/` or any
   other folder is not detected.
2. **Extension.** Use `.agent.md` in `.github/agents/` and `~/.copilot/agents/`. Files in `.claude/agents/` are plain `.md`. A legacy `.chatmode.md` file should be renamed.
3. **Frontmatter.** The block must open and close with `---` on their own lines and be valid YAML. A tab, a
   missing quote around a value containing a colon, or a stray character in the block can stop it parsing.
4. **`user-invocable`.** `user-invocable: false` hides an agent from the dropdown on purpose.
5. **Session target.** Agents are listed after you choose a session target (harness). Check that the one you
   picked supports custom agents.
6. **`target`.** `target: github-copilot` limits an agent to GitHub Copilot, and `target: vscode` limits it to
   VS Code. Omit `target` to make it available in both.

## An older agent file stopped working or is ignored

Files written to the earlier layout do not work. Move them and drop the properties VS Code does not read:

| Old | Use instead |
|---|---|
| `.github/copilot-instructions/name.md` | `.github/agents/name.agent.md` |
| An entry in `settings.json` pointing at the file | Nothing. VS Code finds agents by location |
| `temperature` | Nothing. VS Code has no such property |
| `permissions: read / write / execute` | `tools`, for example `["read", "search"]` for read-only |

## The agent can do more than I intended

Check `tools`. Leaving it out grants every tool. List only what the agent needs, for example `["read", "search"]`. A
sentence in the instructions is not a restriction. Remember that an unrecognized tool name is ignored, so a
typo leaves the intended tool off the list without any error.

## A property or tool seems to have no effect

VS Code ignores a property or tool name it does not recognize. Compare the spelling with the table in
[Custom Agent Files](markdown-agents.md), and with the
[Tools Reference](https://github.com/CowboyLogic/ai-dev/blob/main/skills/agent-creator-copilot/references/tools-reference.md)
for tool names.

## A subagent is never called

1. **The `agent` tool.** The calling agent must list `agent` in `tools`.
2. **The `agents` property.** The target must be named in the caller's `agents` list, or the list must be `*`.
   `agents: []` forbids all subagents.
3. **The name.** Names are case-sensitive and must match the target's `name` exactly.
4. **`disable-model-invocation`.** `disable-model-invocation: true` on the target stops other agents choosing it. Naming it in the caller's `agents` list overrides that, so a coordinator that lists it can still call it.
5. **The description.** Another agent chooses a subagent partly from its `description`. Make it say when to use the agent.
6. **Nesting.** A subagent calling another subagent requires `chat.subagents.allowInvocationsFromSubagents`, and nesting
   stops at a depth of five.

## A subagent returns something unrelated to the task

A subagent does not see the main conversation and keeps no state between calls. If the delegation prompt
assumed context the subagent never received, the result will miss. Include the goal, the relevant context, what
the subagent may do, and the expected result in the delegation. See [Subagents](subagent-tool.md).

## A handoff button does nothing useful

- `agent` in the handoff must name an agent that exists.
- `send: false`, the default, fills the prompt and waits for you to send it. Set `send: true` to submit it automatically.

## The wrong model is used

If `model` is set, it overrides the picker. A list is tried in priority order. Remove `model` to follow the picker. A
model name that your plan does not offer cannot be used.

## Get help

- [Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [Subagents in VS Code](https://code.visualstudio.com/docs/agents/run/subagents)
- [Frontmatter Reference](https://github.com/CowboyLogic/ai-dev/blob/main/skills/agent-creator-copilot/references/frontmatter-reference.md)
- [VS Code issues](https://github.com/microsoft/vscode/issues)

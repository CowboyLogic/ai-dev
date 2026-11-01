# Custom Agent Files

A custom agent in VS Code is a Markdown file with YAML frontmatter. The frontmatter sets the agent's tools and behavior, and the Markdown body is its instructions.

This page covers what VS Code reads. For every property across VS Code, GitHub.com, and the Copilot CLI, see the
[Frontmatter Reference](https://github.com/CowboyLogic/ai-dev/blob/main/skills/agent-creator-copilot/references/frontmatter-reference.md)
in the Copilot Agent Creator skill, and for VS Code's own description see
[Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents) and the
[Custom agent file reference](https://code.visualstudio.com/docs/agents/reference/custom-agent-file-reference).

> [!WARNING]
> Earlier versions of this guide described agents stored in `.github/copilot-instructions/*.md`, mapped in
> `settings.json`, with `temperature` and `permissions.read/write/execute` frontmatter. **None of that is
> supported.** VS Code ignores a `copilot-instructions/` folder as an agent location, has no `settings.json`
> mapping for agent files, and has no `temperature` or `permissions` property. Move such files to
> `.github/agents/`, give them the `.agent.md` extension, and replace `permissions` with `tools`.

## Where agent files live

| Scope | Folder |
|---|---|
| Workspace | `.github/agents/` or `.claude/agents/` |
| User (all workspaces), Copilot harness | `~/.copilot/agents/` |
| User (all workspaces), Anthropic Claude harness | `~/.claude/agents/` |

Files in `.github/agents/` and `~/.copilot/agents/` use the `.agent.md` extension, which is the one to prefer; VS Code's
file-locations table also lists plain `.md` files for both folders. Files in `.claude/agents/` are in Claude Code's format and are plain `.md` files, so do not
rename them. A legacy `.chatmode.md` file should be renamed to `.agent.md`. Commit the workspace folder to share agents with your team.

Copilot (Agent Host) sessions read user-level agents from the host's `~/.copilot/agents/`, and Anthropic Claude
harness sessions read `~/.claude/agents/`; neither comes from VS Code profile user data. VS Code's migration list can move existing agents there.

An organization can publish agents that VS Code detects for its members. Discovery is on by default; set
`github.copilot.chat.organizationCustomAgents.enabled` to `false` to stop showing them.

## File format

```markdown
---
description: Generate an implementation plan
tools: ["search", "web"]
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Now implement the plan outlined above.
    send: false
---

You are a planning agent. Produce a step-by-step plan and do not edit files.
```

## Frontmatter VS Code reads

| Property | Purpose |
|---|---|
| `description` | Short summary, shown as the placeholder in the chat input |
| `name` | Display name. Defaults to the file name without `.agent.md` |
| `argument-hint` | Guidance text shown in the chat input |
| `tools` | Tools the agent may use. Omit it for all tools. User-defined tool sets are deprecated and not supported in the Copilot harness |
| `agents` | Subagents this agent may call. `*` allows all, `[]` allows none |
| `model` | One model name, or a prioritized list. Local subagents also use it when choosing their model |
| `reasoning-effort` | `low`, `medium`, `high`, `xhigh`, or `max`, for the Copilot harness. Availability depends on the model |
| `user-invocable` | Whether the agent appears in the Agent dropdown, in the Local and Copilot harnesses. Default `true` |
| `disable-model-invocation` | Stops other agents from selecting this one as a subagent, unless a coordinator names it in its `agents` list |
| `target` | `vscode` or `github-copilot`. Omit it for both |
| `handoffs` | Suggested next steps, shown as buttons after a response (Local harness) |
| `hooks` | Commands scoped to the agent. Run in the Local harness; the Copilot harness supports them, but VS Code currently drops `hooks` when it converts plugin-provided agents |
| `mcp-servers` | MCP server configuration, for GitHub Copilot only |

An unrecognized property or tool name is ignored, not an error. That makes a mistyped name fail quietly, so check the spelling when an agent does not behave as written.

### Tools

`tools` takes tool aliases, individual tools, and MCP tools:

```yaml
tools: ["read", "search"]               # aliases, read-only
tools: ["read", "edit", "execute"]      # can change files and run commands
tools: ["search/codebase", "web/fetch"] # individual tools
tools: ["agent"]                        # may invoke subagents
tools: ["my-server/*"]                  # every tool from one MCP server
tools: []                               # no tools
```

An agent has no write access unless its tools include `edit`, and no shell unless they include `execute`. Restricting `tools` is how you make a read-only agent. See the
[Tools Reference](https://github.com/CowboyLogic/ai-dev/blob/main/skills/agent-creator-copilot/references/tools-reference.md)
for the full list of aliases and tool names.

### Handoffs

A handoff adds a button that sends the conversation to another agent:

| Field | Meaning |
|---|---|
| `label` | Text on the button |
| `agent` | The target agent |
| `prompt` | The prompt pre-filled when the user selects the handoff (required) |
| `send` | `true` submits it automatically. Default `false` |
| `model` | Optional model for the target, as a qualified name such as `GPT-5 (copilot)` |

### Model

`model` takes a single name or a list in priority order. Leave it out to use whatever model is selected in the picker. Pin a model only when the agent needs one, since model names change.

## Create and select an agent

Create an agent from the Command Palette with **Chat: New Custom Agent**, from the Agent Customizations editor (**Open Customizations** in the Chat view title bar, then **Agents**), or, in a Local harness session, by typing `/create-agent` in chat and describing the role.

To use an agent, pick it from the **Agent** dropdown in the Chat view.

## Examples

Ten example agents live as real files in the repository, so they stay current in one place. See
[Agent Examples](agent-examples.md).

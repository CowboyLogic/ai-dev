---
name: agent-creator-copilot
description: Guide for creating custom agents for GitHub Copilot and VS Code. Use this when building custom agent profiles (.agent.md files), configuring tools, handoffs, subagents, or MCP server integrations for Copilot.
license: MIT
---

# Copilot Agent Creator

Custom agents for GitHub Copilot and VS Code are defined in `.agent.md` Markdown files called **agent profiles**. They encode a role, behavioral instructions, and tool access without requiring extension development.

> **Always verify against official docs.** The canonical references are:
> - [About custom agents](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents)
> - [VS Code custom agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
> - [Configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration)

---

## When to Use This Skill

- Creating a new custom agent profile for Copilot or VS Code
- Configuring tools, handoffs, subagents, or MCP servers in a profile
- Choosing the right scope (workspace, user profile, org/enterprise)
- Designing multi-agent workflows
- Writing effective agent prompts

---

## Quick Decision Guide

| Need | Approach |
|---|---|
| Persistent persona with tool restrictions | **Custom agent profile** (this skill) |
| One-off reusable task instructions | Prompt file (`.prompt.md`) |
| Portable domain knowledge with scripts | Agent skill (`SKILL.md`) |
| Deep VS Code IDE integration, custom UI | VS Code extension |
| Custom tools exposed via protocol | MCP server |

---

## Agent Profile Format

```markdown
---
description: Brief description of the agent's purpose and capabilities
tools: ["read", "search"]
---

# Agent Name

Write your agent's prompt here. This content is prepended to every chat message.
```

YAML frontmatter is optional. An agent can consist of only a Markdown body.

> For the full property reference, load `references/frontmatter-reference.md`.

---

## Where to Store Agent Profiles

| Scope | Location | Use Case |
|---|---|---|
| Workspace | `.github/agents/` | Shared with team via version control |
| Workspace (Claude compat) | `.claude/agents/` | Works in VS Code and Claude Code |
| User profile | `~/.copilot/agents/` | Personal agents, available everywhere |
| Organization | `agents/` in `.github-private` repo | Shared across all org repos |

---

## Tools

```yaml
tools: ["read", "search"]          # specific tools (least privilege)
tools: ["*"]                       # all tools
tools: []                          # no tools
tools: ["read", "my-server/*"]     # built-in + all tools from an MCP server
```

Apply least privilege — start read-only and add write/execute tools only when required.

> For tool aliases, config syntax patterns, and the built-in server list, load `references/tools-reference.md`.

---

## Handoffs

Handoffs create guided transitions between agents. After a response, handoff buttons appear so users can continue with context pre-filled.

```yaml
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Implement the plan outlined above.
    send: false
```

> For the full handoffs property table and `model` override, load `references/frontmatter-reference.md`.

---

## Subagents

Agents can invoke other agents for subtasks. The `agent` tool must be in `tools`.

```yaml
agents:
  - planner
  - code-reviewer
  - "*"    # allow all agents
```

To hide an agent from the agents dropdown (subagent-only), set `user-invocable: false`.
To prevent the cloud agent from auto-selecting an agent, set `disable-model-invocation: true`.

---

## Writing the Prompt Body

```markdown
# Agent Name

You are a [role] focused on [domain]. Your scope is limited to [specific boundaries].

## Responsibilities
- [What it does]
- [What it hands off, not handles]

## Constraints
- Do not modify [out-of-scope files/systems]
- When [situation], [action]
```

Key principles: state scope explicitly, use imperative language, define handoff conditions, keep it under 30,000 characters.

> For detailed principles, anti-patterns, and guidance on what NOT to include, load `references/prompt-writing-guide.md`.

---

## Creating an Agent Profile: Step-by-Step

### Step 1: Plan
1. Define the role and domain (one sentence)
2. List responsibilities and what it does NOT do
3. Choose scope: workspace, user profile, or org
4. Identify required tools — start read-only

### Step 2: Create the File

**VS Code UI (preferred):**
1. Open Chat → Configure Chat (gear icon) → Agents → **New Agent (Workspace)**
2. Enter a filename → a `.agent.md` is created in `.github/agents/`

**Via AI generation:**
Type `/create-agent` in Agent mode chat. Copilot generates the file from a description.

**Manually:**
Create `.github/agents/<name>.agent.md`. Filename: only `.`, `-`, `_`, `a-zA-Z0-9`.

### Step 3: Write Frontmatter

```yaml
---
description: Agent specializing in [domain] — [specific scope]
tools: ["read", "search"]
---
```

### Step 4: Write the Prompt Body

Follow the template above. Be specific about scope and handoff conditions.

### Step 5: Test

1. Switch to the agent in VS Code Chat using the agents dropdown
2. Run representative prompts covering normal use and edge cases
3. Verify scope boundaries are respected
4. Confirm handoffs trigger correctly
5. Check Chat Diagnostics (right-click Chat → Diagnostics) for load errors

---

## Security Considerations

- **Least privilege for tools.** Read-only agents cannot accidentally modify files or run commands.
- **Review shared agents.** Audit tool lists and prompts before committing to a repository.
- **Secrets in MCP config.** Always use `${{ secrets.NAME }}` — never hardcode credentials.
- **Organization agents.** Review org-level agents carefully — they are available to all repos in the org.

---

## Reference Files

| File | When to Load |
|---|---|
| `references/frontmatter-reference.md` | Full property tables, model array syntax, handoffs, MCP config, Claude format |
| `references/tools-reference.md` | Tool aliases, all config syntax patterns, built-in server list |
| `references/prompt-writing-guide.md` | Detailed prompt principles, anti-patterns, output format guidance |
| `references/workspace-agent-example.agent.md` | Full-featured workspace agent example |
| `references/user-profile-agent-example.agent.md` | Minimal personal agent example |
| `references/cloud-agent-with-mcp-example.agent.md` | Cloud agent with MCP + subagents |

---

## Official Documentation

| Resource | URL |
|---|---|
| About custom agents | https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents |
| Create custom agents | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-custom-agents |
| Configuration reference | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| Custom agents in VS Code | https://code.visualstudio.com/docs/copilot/customization/custom-agents |
| Awesome Copilot agents | https://github.com/github/awesome-copilot/tree/main/agents |
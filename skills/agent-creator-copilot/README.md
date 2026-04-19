# Copilot Agent Creator

A skill for creating custom agents for GitHub Copilot and VS Code.

## Overview

Custom agents are specialized Copilot configurations defined in `.agent.md` Markdown files called **agent profiles**. They encode a domain role, behavioral instructions, and tool access into a reusable, shareable file — without requiring any extension development.

This skill covers:
- Agent profile format and all supported frontmatter properties
- Where to store agent files (workspace, user profile, organization)
- Tools configuration and the tool alias reference
- Handoffs for multi-agent workflows
- Subagent orchestration
- MCP server configuration for cloud agents
- Writing effective agent prompts
- The Claude agent format for cross-tool compatibility
- When to use extensions or MCP servers instead of agent profiles

## Quick Start

1. In VS Code, open Chat → Configure Chat (gear icon) → Agents → **New Agent (Workspace)**
2. Enter a filename. A `.agent.md` file is created in `.github/agents/`
3. Add a `description` and write the prompt body
4. Switch to your agent in the agents dropdown and test it

Or type `/create-agent` in Agent mode chat to have Copilot generate the profile for you.

## Key Concepts

### Agent Profiles vs. Other Customizations

| Use | When |
|---|---|
| **Agent profile** | Persistent persona, tool restrictions, handoffs between roles |
| **Prompt file** | One-off reusable instructions, no tool restrictions |
| **Skill (SKILL.md)** | Portable domain knowledge loaded at session start |
| **VS Code extension** | Deep IDE integration, custom UI |
| **MCP server** | Custom tools exposed via Model Context Protocol |

### Scope Levels

| Scope | Location |
|---|---|
| Workspace | `.github/agents/<name>.agent.md` |
| User profile | `~/.copilot/agents/<name>.agent.md` |
| Organization | `agents/<name>.agent.md` in `.github-private` repo |
| Claude compat | `.claude/agents/<name>.md` |

## Example Files

- [workspace-agent-example.agent.md](references/workspace-agent-example.agent.md) — A full-featured workspace-scoped agent with tools, handoffs, and prompt
- [user-profile-agent-example.agent.md](references/user-profile-agent-example.agent.md) — A minimal user-profile agent for personal reuse
- [cloud-agent-with-mcp-example.agent.md](references/cloud-agent-with-mcp-example.agent.md) — A cloud agent profile with inline MCP server config and secrets

## Official Documentation

| Resource | URL |
|---|---|
| About custom agents | https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents |
| Create custom agents | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/create-custom-agents |
| Configuration reference | https://docs.github.com/en/copilot/reference/custom-agents-configuration |
| Custom agents in VS Code | https://code.visualstudio.com/docs/copilot/customization/custom-agents |
| Awesome Copilot agents | https://github.com/github/awesome-copilot/tree/main/agents |
# Copilot Agent Creator

A skill for creating custom agents for GitHub Copilot: Copilot cloud agent on GitHub.com, GitHub Copilot CLI, VS Code, and other supported IDEs.

## Overview

Custom agents are specialized Copilot configurations defined in `.agent.md` Markdown files called **agent profiles**. They encode a domain role, behavioral instructions, tool access, and optionally a model into a reusable, shareable file, without requiring any extension development.

This skill covers:

- Agent profile format and supported frontmatter properties, with a per-surface compatibility table
- Where to store agent files (repository, user, organization, enterprise, CLI plugins)
- Tools configuration: cross-platform aliases, VS Code tool sets, MCP namespacing
- Model selection and current model names, including retired models to avoid
- Handoffs, subagents, and agent-scoped hooks in VS Code
- CLI-only fields (`models`, `modelPolicy`, `reasoningEffort`, `include-custom-instructions`)
- MCP server configuration and secrets for the cloud agent
- Writing effective agent prompts and descriptions
- The Claude agent format for cross-tool compatibility

## Quick Start

1. In VS Code, open the Chat view → **Configure Chat** (gear icon) → **Agents**, then select **New Agent (Workspace)**
2. Enter a filename. A `.agent.md` file is created in `.github/agents/`
3. Add a `description` and write the prompt body
4. Select your agent in the agents dropdown and test it

Alternatives: run `/agent` → **Create new agent** in Copilot CLI, or use **Create an agent** at [github.com/copilot/agents](https://github.com/copilot/agents).

## Key Concepts

### Agent Profiles vs. Other Customizations

| Use | When |
|---|---|
| **Agent profile** | Persistent persona, tool restrictions, handoffs between roles |
| **Prompt file** | One-off reusable instructions |
| **Skill (SKILL.md)** | Portable domain knowledge loaded when relevant |
| **Hook** | Deterministic command at a lifecycle event |
| **VS Code extension** | Deep IDE integration, custom UI |
| **MCP server** | Custom tools exposed via Model Context Protocol |

### Scope Levels

| Scope | Location |
|---|---|
| Repository | `.github/agents/<name>.agent.md` |
| User | `~/.copilot/agents/<name>.agent.md` (VS Code, CLI) |
| Organization | `agents/<name>.md` in the org's `.github` or `.github-private` repo |
| Enterprise | `agents/<name>.md` in the `.github-private` repo of an org designated in enterprise settings |
| Claude compat | `.claude/agents/<name>.md` (VS Code, CLI), `~/.claude/agents/` (VS Code) |

## Example Files

- [workspace-agent-example.agent.md](references/workspace-agent-example.agent.md): VS Code workspace agent with a model fallback list, `argument-hint`, and handoffs
- [user-profile-agent-example.agent.md](references/user-profile-agent-example.agent.md): minimal personal agent. Its `model` uses the VS Code display name; the CLI expects IDs such as `gpt-5.6-luna`
- [cloud-agent-with-mcp-example.agent.md](references/cloud-agent-with-mcp-example.agent.md): GitHub.com cloud agent with inline MCP server config, a `COPILOT_MCP_` secret, and metadata

## Official Documentation

| Resource | URL |
|---|---|
| About custom agents | <https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents> |
| Create custom agents (cloud agent) | <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents> |
| Configuration reference | <https://docs.github.com/en/copilot/reference/custom-agents-configuration> |
| Custom agents for Copilot CLI | <https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli> |
| Custom agents in VS Code | <https://code.visualstudio.com/docs/agent-customization/custom-agents> |
| Supported AI models | <https://docs.github.com/en/copilot/reference/ai-models/supported-models> |
| Awesome Copilot agents | <https://github.com/github/awesome-copilot/tree/main/agents> |

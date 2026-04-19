# OpenCode Agent Creator

Skill for creating and configuring custom AI agents for the [OpenCode CLI](https://opencode.ai).

## When to Load This Skill

Load this skill when:

- Writing a new `.md` agent file for OpenCode
- Configuring agents in `opencode.json`
- Designing subagent workflows and delegation patterns
- Setting up fine-grained tool permissions
- Choosing models and temperature settings for specialized agents
- Scaffolding with `opencode agent create`

## What This Skill Covers

| Topic | Coverage |
|---|---|
| Markdown agent files (`.opencode/agents/*.md`) | Full |
| JSON config (`opencode.json` `agent` block) | Full |
| Built-in agent customization | Full |
| Permission model (`permission` key) | Full |
| Multi-agent orchestration | Full |
| Temperature and model selection | Full |
| OpenCode skills (`opencode.ai/docs/skills/`) | Out of scope |
| MCP server configuration | Out of scope |

## Key Files

- **`SKILL.md`** — Core guide: format choice, file locations, permission model, step-by-step workflow, prompt writing tips
- **`references/agent-reference.md`** — Complete property reference for every YAML/JSON configuration key with types, defaults, and examples

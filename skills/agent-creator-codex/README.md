# Codex Agent Creator

A skill for creating and troubleshooting custom subagents for OpenAI Codex.

## Overview

Codex custom agents are standalone TOML files in `.codex/agents/` or `~/.codex/agents/`. Each
file needs `name`, `description`, and `developer_instructions`; every other field is an
optional `config.toml` key applied as a layer over the parent session. There is no Markdown
body. Two behaviors surprise people coming from other tools: Codex delegates only when asked,
and a parent's runtime sandbox and approval settings override whatever the agent file says.

This skill covers:

- The agent file format and its three required fields
- Optional fields: `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`,
  `skills.config`, `nickname_candidates`
- The `[agents]` table (`enabled`, `max_concurrent_threads_per_session`,
  `default_subagent_model`, `default_subagent_reasoning_effort`) and `[agents.<name>]` roles
- Built-in `default`, `worker`, and `explorer` agents and how to override them
- Model and reasoning-effort resolution order, including why `[agents]` defaults beat the file
- Sandbox and approval inheritance, and why `read-only` in a file is not a lock
- How delegation is triggered: explicit request, `AGENTS.md`, or a skill
- Symptom-to-cause troubleshooting
- A validator script that checks a file or directory of agents

## Quick Start

1. Create `.codex/agents/<name>.toml` with `name`, `description`, and `developer_instructions`.
2. Set `sandbox_mode = "read-only"` unless the role must edit.
3. Validate: `python scripts/validate-agent.py .codex/agents/`
4. Start a new Codex session and ask for the agent by name.

## Validator

```bash
python scripts/validate-agent.py .codex/agents/my_agent.toml
python scripts/validate-agent.py .codex/agents/ --strict
```

Standard library only (Python 3.11+). It flags TOML that does not parse, missing or blank
required fields, Claude Code / Copilot / OpenCode fields Codex does not have, misspelled or
mis-cased keys, invalid `sandbox_mode` and `model_reasoning_effort` values, duplicate names,
filename and `name` mismatches, and literal secrets in `mcp_servers`.

It cannot know which models your account can use; run `codex debug models`.

## Key Concepts

### Agents vs. Other Customizations

| Use | When |
|---|---|
| **Custom agent** | Isolated context, a different model, or a narrower sandbox for a side task |
| **`AGENTS.md`** | Instructions every session in a repository should follow |
| **Skill** | A reusable procedure loaded on demand |
| **Built-in agent** | Parallel work that needs no custom behavior |

### Scope Levels

| Scope | Location |
|---|---|
| Project | `.codex/agents/` |
| Personal | `~/.codex/agents/` |
| Config table | `[agents.<name>]` in `config.toml` with `config_file` |

## Example Files

- [agent-examples.md](references/agent-examples.md): a read-only reviewer, an implementer, an MCP-backed researcher, a `config.toml` role, and an `AGENTS.md` delegation rule

## Official Documentation

| Resource | URL |
|---|---|
| Subagents | <https://developers.openai.com/codex/subagents> |
| Config reference | <https://developers.openai.com/codex/config-reference> |

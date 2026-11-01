# Codex Agent Creator

A skill for creating and troubleshooting custom subagents for OpenAI Codex.

> [!NOTE]
> **Codex version:** verified against [Codex CLI 0.163.0](https://github.com/openai/codex/releases/tag/rust-v0.163.0)
> (released 2026-10-15). Role-file behavior comes from the Codex source at tag `rust-v0.163.0`
> and from running that CLI. Re-verify when Codex ships a new release.

## Overview

Codex custom agents are standalone TOML files in `.codex/agents/` or `~/.codex/agents/`. Each
file needs `name`, `description`, and `developer_instructions`. There is no Markdown body.
Two behaviors surprise people coming from other tools: Codex delegates only when asked, and a
role file can only customize the child, never widen or narrow the parent's authority. Codex
applies a bounded set of keys; `sandbox_mode`, `approval_policy`, `mcp_servers`, and
`service_tier` parse but are ignored, because the child inherits the parent's sandbox,
approvals, and MCP servers, and uses the root session's service tier. The official subagents
page and the Codex source agree on this.

This skill covers:

- The agent file format and its three required fields
- The bounded set of keys a role file can actually set: instructions, model and reasoning
  effort, summary, verbosity, personality, and disabling features and skills
- The `[agents]` table (`enabled`, `max_concurrent_threads_per_session`,
  `default_subagent_model`, `default_subagent_reasoning_effort`) and `[agents.<name>]` roles
- Built-in `default`, `worker`, and `explorer` agents and how to override them
- Model and reasoning-effort precedence: the role file outranks spawn values and `[agents]` defaults
- Sandbox, approval, and MCP inheritance from the parent, and how to get a read-only agent
- How delegation is triggered: explicit request, `AGENTS.md`, or a skill
- Symptom-to-cause troubleshooting
- A validator script that checks a file or directory of agents

## Quick Start

1. Create `.codex/agents/<name>.toml` with `name`, `description`, and `developer_instructions`.
2. Start the parent session with the sandbox the role needs (`codex --sandbox read-only`); the role file cannot set it.
3. Validate: `python scripts/validate-agent.py .codex/agents/`
4. Run `codex doctor` to see any `Ignoring malformed agent role definition` startup warnings
   without starting a session.
5. Start a new Codex session and ask for the agent by name.

## Validator

```bash
python scripts/validate-agent.py .codex/agents/my_agent.toml
python scripts/validate-agent.py .codex/agents/ --strict
```

Standard library only (Python 3.11+). It scans the directory recursively, as Codex does. It
flags TOML that does not parse, missing or blank required fields, Claude Code / Copilot /
OpenCode fields Codex does not have, misspelled or mis-cased keys, duplicate names, filename
and `name` mismatches, and keys Codex accepts but ignores in a role file (`sandbox_mode`,
`approval_policy`, `mcp_servers`, and others).

It cannot know which models your account can use; run `codex debug models`.

## Key Concepts

### Agents vs. Other Customizations

| Use | When |
|---|---|
| **Custom agent** | Isolated context, a different model, custom instructions, or fewer capabilities (such as no shell tool) for a side task. It does not change the sandbox |
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

- [agent-examples.md](references/agent-examples.md): a reviewer, an implementer, an MCP-dependent researcher, a capability-disabling role, a `config.toml` role, and an `AGENTS.md` delegation rule

## Official Documentation

| Resource | URL |
|---|---|
| Subagents | <https://developers.openai.com/codex/subagents> |
| Config reference | <https://developers.openai.com/codex/config-reference> |

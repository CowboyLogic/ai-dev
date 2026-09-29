# Codex Agent Creator

Create and troubleshoot custom subagents for OpenAI Codex: standalone TOML files in
`.codex/agents/` or `~/.codex/agents/`. Covers the required and optional fields, the `[agents]`
table in `config.toml`, model and sandbox resolution, how delegation is triggered, and a
validator script.

- **Skill name:** `agent-creator-codex`
- **Last updated:** 2026-09-29
- **Source:** [skills/agent-creator-codex](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-codex)

---

## What it does

A Codex agent has no Markdown body: the system prompt is the `developer_instructions` string
in the TOML. Codex also delegates only when asked, and a parent session's runtime sandbox and
approval settings override the agent file. The skill gives an agent a workflow for planning,
writing, validating, and testing a Codex agent, and loads detailed reference material only when
the task needs it.

**Topics covered:**

- Agent file format — `name`, `description`, and `developer_instructions` are required
- Optional fields — `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`,
  `skills.config`, `nickname_candidates`
- The `[agents]` table and `[agents.<name>]` role tables with `config_file`
- Built-in `default`, `worker`, and `explorer` agents
- Model and reasoning-effort resolution order
- Sandbox and approval inheritance, and why a file's `sandbox_mode` is not a hard lock
- Triggering delegation through an explicit request, `AGENTS.md`, or a skill
- Symptom-to-cause troubleshooting
- Writing effective `description` and `developer_instructions`

**Where agents live:**

| Scope | Location |
|-------|----------|
| Project | `.codex/agents/` |
| Personal | `~/.codex/agents/` |
| Config table | `[agents.<name>]` in `config.toml` |

> [!IMPORTANT]
> Codex does not delegate based on `description` alone. Name the agent in the request or add a
> delegation rule to `AGENTS.md`.

---

## Validator

The skill bundles `scripts/validate-agent.py` (standard library only, Python 3.11+):

```bash
python scripts/validate-agent.py .codex/agents/
```

It reports TOML that does not parse, missing or blank required fields, fields from other agent
tools that Codex does not have, misspelled keys, invalid enum values, duplicate names, and
literal secrets in `mcp_servers`.

---

## Reference files

| File | When the skill loads it |
|------|-------------------------|
| `references/config-reference.md` | Every field, allowed values, the `[agents]` table, role tables, resolution order |
| `references/agent-examples.md` | Read-only reviewer, implementer, MCP researcher, config-table role, `AGENTS.md` rule |
| `references/troubleshooting.md` | Symptom-to-cause tables for load, delegation, model, sandbox, and MCP problems |

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill agent-creator-codex -g
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [Claude Code Agent Creator](agent-creator-claudecode.md) — the equivalent skill for Claude Code
- [Copilot Agent Creator](agent-creator-copilot.md) — the equivalent skill for GitHub Copilot
- [OpenCode Agent Creator](agent-creator-opencode.md) — the equivalent skill for OpenCode

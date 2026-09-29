# Codex Agent Creator

Create and troubleshoot custom subagents for OpenAI Codex, defined as standalone TOML files
in `.codex/agents/` or `~/.codex/agents/`.

- **Skill name:** `agent-creator-codex`
- **Last updated:** 2026-09-29
- **Source:** [skills/agent-creator-codex](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-codex)

---

## What it does

A Codex agent has no Markdown body: its instructions are a field in the TOML file. Codex also
delegates only when asked, and it applies only a bounded set of keys from an agent file. The
sandbox, approvals, and MCP servers always come from the parent session. The skill gives an
agent a workflow for planning, writing, validating, and testing a Codex agent, and loads
detailed reference material only when the task needs it.

**Topics covered:**

- The agent file format and its three required fields
- Which keys Codex applies from an agent file, and which it accepts but ignores
- Model and reasoning-effort precedence
- Sandbox, approval, and MCP inheritance from the parent session
- The `[agents]` table and `[agents.<name>]` role tables in `config.toml`
- Built-in `default`, `worker`, and `explorer` agents
- How to trigger delegation
- Symptom-to-cause troubleshooting, based on the messages Codex actually prints
- A validator script for a file or directory of agents

> [!IMPORTANT]
> Codex does not delegate based on `description` alone, and an agent file cannot set its own
> sandbox. See the skill for how to handle both.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill agent-creator-codex -g

# Install for Codex only
npx skills add CowboyLogic/ai-dev --skill agent-creator-codex --agent codex -g
```

### Verify installation

```bash
npx skills ls -g
```

The skill, its references, examples, and validator live in the repository:
[skills/agent-creator-codex](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-codex).

---

## Related

- [Claude Code Agent Creator](agent-creator-claudecode.md) — the equivalent skill for Claude Code
- [Copilot Agent Creator](agent-creator-copilot.md) — the equivalent skill for GitHub Copilot
- [OpenCode Agent Creator](agent-creator-opencode.md) — the equivalent skill for OpenCode

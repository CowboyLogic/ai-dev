# Claude Code Agent Creator

Create and troubleshoot custom subagents for Claude Code: Markdown files with YAML
frontmatter in `.claude/agents/` or `~/.claude/agents/`. Covers every frontmatter field, the
conditions under which Claude Code silently skips a file, and tool and permission behavior.

- **Skill name:** `agent-creator-claudecode`
- **Source:** [skills/agent-creator-claudecode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-claudecode)

---

## What it does

Claude Code ignores frontmatter fields it does not recognize and skips some malformed files
without telling the session, so a misspelled field looks exactly like a working agent. The
skill gives an agent a workflow for planning, writing, validating, and testing a subagent,
and loads detailed reference material only when the task needs it. It bundles a validator
script for agent files.

**Topics covered:**

- The agent file format and its required fields
- The conditions under which Claude Code silently skips a file
- Tools, permissions, and models
- Hooks, MCP servers, preloaded skills, persistent memory, and worktree isolation
- Which agent scopes support which fields: project, user, managed, `--agents` JSON, and plugin
- Troubleshooting by symptom
- Writing effective `description` values and prompt bodies

## Where it applies

Use it when an agent writes or debugs Claude Code subagents.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill agent-creator-claudecode -g

# Install for Claude Code only
npx skills add CowboyLogic/ai-dev --skill agent-creator-claudecode --agent claude-code -g
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [Claude Code Configuration Manager](client-config-claudecode.md) — permissions, hooks, and MCP
  in `settings.json`
- [Copilot Agent Creator](agent-creator-copilot.md) — the equivalent skill for GitHub Copilot
- [OpenCode Agent Creator](agent-creator-opencode.md) — the equivalent skill for OpenCode
- [Matrix Topology](../agents/matrix-topology.md) — a multi-agent system with a Claude mirror

# Copilot Agent Creator

Create custom agent profiles (`.agent.md` files) for GitHub Copilot across VS Code, the
Copilot CLI, and the Copilot cloud agent on GitHub.com. Covers the frontmatter schema with
per-surface compatibility, tool aliases and VS Code tool sets, model selection, handoffs,
subagents, hooks, and MCP servers.

- **Skill name:** `agent-creator-copilot`
- **Source:** [skills/agent-creator-copilot](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-copilot)

---

## What it does

A single agent profile can run on several Copilot surfaces, but many properties only work on
some of them. The skill gives an agent a step-by-step workflow for planning, writing, and
testing a profile, and loads detailed reference material only when the task needs it.

**Topics covered:**

- The agent profile format
- Storage scope: repository, user, organization, enterprise, plugin, and Claude-format
  locations
- Tools: portable aliases, MCP namespacing, and least-privilege defaults
- Model selection
- Handoffs, subagents, `user-invocable`, and `disable-model-invocation`
- Fields that only some surfaces support
- MCP server configuration and secrets for the cloud agent
- Writing effective prompts and descriptions

## Where it applies

Use it when an agent writes or debugs Copilot agent profiles for VS Code, the Copilot CLI,
or the cloud agent. The VS Code guide under
[Visual Studio Code](../harness/vscode/index.md) covers the same file format from the
editor's side.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill agent-creator-copilot -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill agent-creator-copilot --agent copilot -g
```

### Using `gh copilot` (Copilot CLI only)

```bash
gh copilot skill install CowboyLogic/ai-dev/skills/agent-creator-copilot
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [Copilot Instruction Creator](copilot-instruction-creator.md) — repository, path, and
  personal instructions rather than agent personas
- [Claude Code Agent Creator](agent-creator-claudecode.md) — the equivalent skill for Claude Code
- [OpenCode Agent Creator](agent-creator-opencode.md) — the equivalent skill for OpenCode

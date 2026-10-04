# OpenCode Agent Creator

Create and configure custom agents for the [OpenCode CLI](https://opencode.ai). Native
OpenCode V2 is the default output; V1 is still supported when you are on V1 or the files
beside the new agent are V1-shaped. Covers Markdown and JSON agent definitions, the
permission model, V1 → V2 migration, model and variant selection, and subagent patterns.

- **Skill name:** `agent-creator-opencode`
- **Source:** [skills/agent-creator-opencode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-opencode)

---

## What it does

OpenCode V1 and V2 use different field names and different permission models for the same
concepts, and a single agent must be entirely one format. The skill picks the format version
first, then guides the agent through writing and testing the definition, and loads reference
material by version and task rather than all at once.

**Topics covered:**

- Markdown and JSON agent definitions
- The permission model in V1 and V2
- Migrating agents and permissions from V1 to V2
- Model and variant selection, including cost gating
- Multi-agent orchestration

## Where it applies

Use it when an agent writes or migrates OpenCode agents. OpenCode skills, commands, plugins,
MCP servers, and providers are out of scope; use the
[OpenCode Configuration Manager](client-config-opencode.md) for those.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill agent-creator-opencode -g

# Install for OpenCode only
npx skills add CowboyLogic/ai-dev --skill agent-creator-opencode --agent opencode -g
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [OpenCode Configuration Manager](client-config-opencode.md) — the rest of `opencode.json`
- [Copilot Agent Creator](agent-creator-copilot.md) — the equivalent skill for GitHub Copilot
- [Claude Code Agent Creator](agent-creator-claudecode.md) — the equivalent skill for Claude Code
- [Matrix Topology](../agents/matrix-topology.md) and [Lane Topology](../agents/lane-topology.md)
  — multi-agent systems built on OpenCode agents

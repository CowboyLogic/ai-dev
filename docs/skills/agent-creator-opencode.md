# OpenCode Agent Creator

Create and configure custom agents for the [OpenCode CLI](https://opencode.ai). Native
OpenCode V2 is the default output; V1 is still supported when you are on V1 or the files
beside the new agent are V1-shaped. Covers Markdown and JSON agent definitions, the
permission model, V1 → V2 migration, model and variant selection, and subagent patterns.

- **Skill name:** `agent-creator-opencode`
- **Last updated:** 2026-09-25
- **Source:** [skills/agent-creator-opencode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-opencode)

---

## What it does

OpenCode V1 and V2 use different field names and different permission models for the same
concepts, and a single agent must be entirely one format. The skill starts by picking the
format version, then walks through mode, scope, prompt, permissions, model, file creation,
and testing.

**Format detection:**

| V1 signals | V2 signals |
|------------|------------|
| `agent` map, `prompt`, `permission` map, `disable`, `variant`, `temperature`, `top_p`, `maxSteps`, `tools`, `bash` / `task` keys | `agents` map, `system`, `permissions` array of `{action, resource, effect}`, `disabled`, `model: ...#variant`, `request`, `shell` / `subagent` actions |

> [!IMPORTANT]
> Never mix `permission` with `permissions`, or `prompt` with `system`, in one agent. V2
> tolerates V1 and V2 fields side by side at the top level of a config file, but it does
> not infer formats inside an individual agent.

**Key rules the skill enforces:**

- **Set `mode` explicitly.** The default is `all` in V1 and `primary` in V2.
- **Start permissions with a catch-all deny.** Denying only `edit` and `shell` still leaves
  `subagent`, `skill`, `question`, `webfetch`, and `websearch` open. In V2, permission rules
  are ordered and the last match wins.
- **Always set an explicit `model`** unless told to inherit, and match it to the role.
- **Never auto-select extreme-cost models** (such as Opus fast mode or Fable) without
  explicit cost acceptance.
- **Only use a model `#variant` that exists** — an unknown variant is an error in V2.
- **Keep `hidden: false` on subagents an orchestrator must discover.** In V2, `hidden: true`
  also removes the agent from the subagent catalog.

**Scope:** agents, the permission model, V1 → V2 migration of agents and permissions,
multi-agent orchestration, and model selection are covered in full. OpenCode skills,
commands, plugins, MCP servers, and providers are out of scope — use the
[OpenCode Configuration Manager](client-config-opencode.md) for those.

---

## Reference files

The skill loads references on demand by version and task rather than all at once.

| Task | V2 (default) | V1 |
|------|--------------|----|
| Fields, types, defaults, locations, built-ins | `references/v2/agents.md` | `references/v1/properties.md` |
| Permission rules, actions, defaults, external dirs | `references/v2/permissions.md` | `references/v1/permissions.md` |
| Full working agent templates | `references/v2/examples.md` | `references/v1/examples.md` |
| Converting V1 agents to V2 | `references/v2/migration.md` | — |
| Model IDs, variants, cost gating | `references/models.md` | `references/models.md` |

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
- [Matrix Topology](../agents/matrix-topology.md) and [Lane Topology](../agents/lane-topology.md)
  — multi-agent systems built on OpenCode agents

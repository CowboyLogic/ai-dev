# OpenCode Agent Creator

Skill for creating and configuring custom AI agents for the [OpenCode CLI](https://opencode.ai).
Native OpenCode V2 is the default output; V1 is still supported when the user is
on V1 or their existing files are V1-shaped.

## When to Load This Skill

Load this skill when:

- Writing a new `.md` agent file for OpenCode
- Configuring agents in `opencode.json(c)` (`agents` in V2, `agent` in V1)
- Converting V1 agent definitions to native V2
- Designing subagent workflows and delegation patterns
- Setting up fine-grained tool permissions
- Choosing models and model variants for specialized agents

## What This Skill Covers

| Topic | Coverage |
|---|---|
| Markdown agent files (`.opencode/agents/*.md`), V2 and V1 | Full |
| JSON config (V2 `agents` / V1 `agent` block) | Full |
| Built-in agent customization | Full |
| Permission model (V2 `permissions` array / V1 `permission` map) | Full |
| V1 to V2 agent migration | Agents and permissions only |
| Multi-agent orchestration | Full |
| Model selection, variants, cost gating | Full |
| Config-level policies (`experimental.policies`) | Summary |
| OpenCode skills, commands, plugins, MCP servers, providers | Out of scope |

## Key Files

- **`SKILL.md`** — Core guide: version selection, format examples, step-by-step workflow, prompt tips, reference map
- **`references/v2/agents.md`** — V2 fields, locations, defaults, built-ins, merge rules
- **`references/v2/permissions.md`** — V2 rule shape, matching, actions, defaults, approvals, policies
- **`references/v2/examples.md`** — Full working V2 agent templates
- **`references/v2/migration.md`** — V1 to V2 field and permission mapping, behavior changes
- **`references/v1/properties.md`** — V1 property keys, types, defaults, annotated full config
- **`references/v1/permissions.md`** — V1 permission syntax, patterns, keys, external dirs, task rules
- **`references/v1/examples.md`** — Full working V1 agent templates
- **`references/models.md`** — Model ID and variant syntax (both versions), provider tables, extreme-cost gating

Load references on demand via the reference map at the end of `SKILL.md` — do not pull the whole set into context for every agent-creation task.

# OpenCode Agent Creator

Skill for creating and configuring custom AI agents for the [OpenCode CLI](https://opencode.ai).
Native OpenCode V2 is the default output; V1 is still supported when the user is
on V1 or their existing files are V1-shaped.

> [!NOTE]
> **OpenCode version:** verified against OpenCode V2
> [2.2.5](https://github.com/anomalyco/opencode/tree/v2.2.5) (tagged 2026-10-30) and V1
> [1.19.5](https://github.com/anomalyco/opencode/tree/v1.19.5) (tagged 2026-10-28),
> checked 2026-11-01. Against the previous baseline (V2 2.0.29) the V2 agents, permissions, and migration
> docs changed: `external_directory` is now allowed by default, agent files are read as one format, agent
> `request.body` is documented as not sent (sampling goes on a model variant), and the policy actions were
> split into `mcp.use`, `skill.use`, `plugin.use`, `integration.connect`, and `integration.use`. V1 changes since 1.19.0
> have no agent-authoring surface (V1 release notes were not reachable, so this rests on the tag diff and commit log).
> The Copilot model table in `references/models.md` was re-checked against GitHub's supported-models and
> retirement pages and the models.dev catalog on the same date: GPT-6.1 Terra was added, and GPT-5 mini, GPT-5.4,
> GPT-5.4 mini, GPT-5.5, and Gemini 3.7 Flash moved to the retired table (retired 2026-10-19). Neither binary was
> run for this check, so V2 notes that were verified on the 2.0.27 binary keep that basis. Re-verify when either
> line ships a new release.

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
| Config-level policies (`policies`) | Summary |
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

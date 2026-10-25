# OpenCode Agent Creator

Skill for creating and configuring custom AI agents for the [OpenCode CLI](https://opencode.ai).
Native OpenCode V2 is the default output; V1 is still supported when the user is
on V1 or their existing files are V1-shaped.

> [!NOTE]
> **OpenCode version:** verified against OpenCode V2
> [2.1.4](https://github.com/anomalyco/opencode/tree/v2.1.4) (tagged 2026-10-23) and V1
> [1.19.4](https://github.com/anomalyco/opencode/releases/tag/v1.19.4) (released 2026-10-22),
> checked 2026-10-25, with the 2.1.4 binary run for `{file:...}` substitution in agent `system`.
> Against the previous baseline (V2 2.0.29): agent files that use V2-only fields are now read as V2
> agents; `request.body` is still not sent to the model; the permissions reference gained the MCP
> resource actions and corrects the `external_directory` default (allowed, not `ask`; the source did
> not change, the docs did). V1 1.19.1 discontinued session sharing; no other V1 agent docs changed.
> The Copilot model table in `references/models.md` was re-checked against GitHub's supported-models
> and retirement pages and the models.dev catalog on the same date: GPT-5 mini, GPT-5.4, GPT-5.4 mini,
> GPT-5.5, and Gemini 3.7 Flash were retired on 2026-10-19 and moved to the retired list. Re-verify
> when either line ships a new release.

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

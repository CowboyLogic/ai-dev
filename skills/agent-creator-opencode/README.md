# OpenCode Agent Creator

Skill for creating and configuring custom AI agents for the [OpenCode CLI](https://opencode.ai).
Native OpenCode V2 is the default output; V1 is still supported when the user is
on V1 or their existing files are V1-shaped.

> [!NOTE]
> **OpenCode version:** verified against OpenCode V2
> [2.3.2](https://github.com/anomalyco/opencode/tree/v2.3.2) (tagged 2026-11-18) and V1
> [1.19.6](https://github.com/anomalyco/opencode/tree/v1.19.6) (tagged 2026-11-17),
> checked 2026-11-22. Since the previous refresh (V2 2.3.0) the agent-authoring surface changed in one place: V2 now
> falls back to `CLAUDE.md` in a directory with no `AGENTS.md` (2.3.2), reversing the earlier "AGENTS.md only" note in the
> V2 migration reference; the agents and permissions docs only gained descriptions. V1 1.19.6 changed CI, desktop, and
> image history handling only. The Copilot model table in `references/models.md` was re-checked against GitHub's
> supported-models, comparison, and retirement pages and the models.dev `github-copilot` catalog on 2026-11-22: GPT-6.2
> Sol, Gemini 4 Neon, MAI Code 2, and MAI Code 2 Flash were added, GPT-6.2 Astra joined the gated extreme-cost list, and
> Claude Opus 4.8, Claude Opus 5, and GPT-5.6 Terra were retired on 2026-11-16. Neither binary was
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

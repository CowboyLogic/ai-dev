# OpenCode V2 Agent Reference

Native V2 agent fields, file locations, defaults, and merge rules.

**Sources (checked 2026-09-24):** <https://opencode.ai/v2/docs/agents/> ·
<https://opencode.ai/v2/docs/config/> · <https://opencode.ai/v2/docs/models/> ·
<https://opencode.ai/v2/docs/tools/> · <https://opencode.ai/v2/docs/migrate-v1/>

Load this file when writing or reviewing a native V2 agent. For permission
rules, load `permissions.md` (this folder). For converting a V1 agent, load
`migration.md`. For model IDs, load `../models.md`. For templates, load
`examples.md`.

> [!IMPORTANT]
> Keep each agent entirely in one format. V2 accepts V1 and V2 fields side by
> side at the top level of a config file, but it does **not** infer formats
> inside an individual agent. Never mix `permission` and `permissions`, or
> `prompt` and `system`, in the same agent.

---

## Locations

| Scope | Location |
|---|---|
| Global (Markdown) | `~/.config/opencode/agents/<name>.md` |
| Project (Markdown) | `.opencode/agents/<name>.md` |
| JSON/JSONC | `agents.<id>` in any config file: `~/.config/opencode/opencode.json(c)`, `<project>/opencode.json(c)`, `<project>/.opencode/opencode.json(c)` |

- Project `.opencode` directories are discovered from the current directory up
  to the project root.
- A nested path becomes part of the ID: `.opencode/agents/team/reviewer.md`
  becomes `team/reviewer`.
- V2 still discovers the legacy V1 directories `agent/`, `agents/`, `mode/`,
  and `modes/`, but `agents/` is the preferred location. Files under `mode/` or
  `modes/` are primary agents.
- Config merge order: direct `opencode.json(c)` files merge from the farthest
  directory to the closest, then files inside `.opencode` directories in the
  same order, so every discovered `.opencode` config overrides every direct
  config.

---

## Formats

### Markdown

Frontmatter accepts the same fields as an `agents` configuration entry. The
Markdown body becomes the agent's system prompt, so do **not** add a `system`
field to frontmatter.

```markdown
---
description: Reviews changes for correctness and regressions
mode: subagent
model: anthropic/claude-sonnet-5#high
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: deny
---

Review the current changes. List findings in severity order with file and line references.
```

### JSON/JSONC

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agents": {
    "reviewer": {
      "description": "Reviews current changes",
      "mode": "subagent",
      "system": "Report findings in severity order.",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" }
      ]
    }
  }
}
```

> [!NOTE]
> The V2 docs use `"$schema": "https://opencode.ai/config.json"`. When fetched on
> 2026-09-24, that schema still described the V1 shape (`agent`, `permission`)
> with `additionalProperties: false` and no `agents` or `permissions` keys, and no
> separate V2 schema URL was found. Editors may therefore flag valid native V2
> keys. Trust the V2 docs over editor warnings for those keys.

---

## Fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `description` | string | none | Shown to the model when it chooses a subagent. Add it to every subagent. |
| `mode` | `primary` \| `subagent` \| `all` | `primary` for a new custom agent | **V1 defaulted to `all`.** Always set it explicitly. |
| `model` | string or object | see below | `provider/model` with optional `#variant` |
| `system` | string | provider base prompt | JSON only. In Markdown, use the body. |
| `permissions` | array of rules | base policy | Ordered `{action, resource, effect}` rules. See `permissions.md`. |
| `steps` | positive integer | not documented | Maximum model steps |
| `hidden` | boolean | `false` | Hides from listings **and** the subagent catalog |
| `color` | string | none | Six-digit hex only, for example `"#ff6b6b"` |
| `disabled` | boolean | `false` | Removes a built-in or custom agent |
| `request` | object | none | `headers` and `body` overlays. **Not sent yet**, see below. |

Do not use these legacy V1 fields in a native V2 agent: `temperature`, `top_p`,
`prompt`, `permission`, `tools`, `disable`, `maxSteps`. The V1 JSON `name` field
inside an agent is ignored by V2 with a warning.

### description

```yaml
description: Reviews database migrations for safety
```

State the specialty and what the agent does not do. Vague descriptions cause
the wrong subagent to be launched.

### mode

| Value | Behavior |
|---|---|
| `primary` | Runs as the main agent for a session. Default for a new custom agent. |
| `subagent` | Runs only in a child session through the `subagent` tool. |
| `all` | Runs either as a primary agent or a subagent. |

Subagents run with fresh context in foreground or background child sessions.
The parent's `subagent` permission controls which agents it may launch; the
child uses its own configured permissions, not a subset of the parent's.

> [!NOTE]
> The tools page says "Only subagent-mode agents can be used" by the `subagent`
> tool, while the agents page says `all` agents run "either as a primary agent
> or a subagent". Use `mode: subagent` for anything an orchestrator must launch.

The default subagent nesting depth is one (subagents cannot launch subagents).
The migration guide names `experimental.subagent_depth` as the V2 location of the
V1 top-level `subagent_depth` setting.

### model

```yaml
model: anthropic/claude-sonnet-5#high
```

JSON also accepts the expanded form:

```json
{
  "model": {
    "providerID": "anthropic",
    "model": "claude-sonnet-5",
    "variant": "high"
  }
}
```

- The provider ends at the first `/`; the model may contain more `/`; the
  variant follows `#`. IDs are case-sensitive.
- Variant names come from the model's catalog metadata. An unknown variant is a
  model-resolution error, so check the variant exists before writing it.
- A subagent with no `model` inherits the parent session's model.
- A session stores its selected model separately; selecting a primary agent does
  not change the session's model.
- The root `model` field does not retain a `#variant`; agent and command model
  references do.

### system

```json
{ "agents": { "reviewer": { "system": "Review only. Do not modify files." } } }
```

A non-empty `system` replaces the provider's base prompt for that agent. Project
instructions (`AGENTS.md`), skills, and references are still added.

> [!NOTE]
> The V2 docs do not document `{file:...}` substitution for `system`, but it works:
> verified on OpenCode 2.0.16 with `opencode debug agents`, where
> `"system": "{file:./prompts/plan.txt}"` resolved to the file's contents, relative to
> the config file, including when OpenCode was started from a subdirectory. Because
> the behavior is undocumented, a Markdown agent file (body = prompt) is still the
> more durable choice for a long prompt.

### steps

```yaml
steps: 8
```

On the final step OpenCode removes tools and asks the model to summarize in
text. New user input resets the allowance.

### hidden

```yaml
hidden: true
```

Removes the agent from normal listings, interactive discovery, **and the
subagent catalog**. This is visibility, not security; use `permissions` to
restrict behavior.

> [!WARNING]
> This differs from V1, where `hidden` only removed a subagent from `@`
> autocomplete and the model could still launch it. The V2 docs do not say
> whether an orchestrator can still launch a hidden agent by exact ID. Do not
> hide a subagent an orchestrator must discover; test before relying on it.

### color

```yaml
color: "#ff6b6b"
```

V2 documents only six-digit hex. V1 theme names (`accent`, `primary`, and so on)
are not documented for V2.

### disabled

```json
{ "agents": { "plan": { "disabled": true } } }
```

### request

```json
{
  "agents": {
    "reviewer": {
      "request": {
        "headers": { "x-agent": "reviewer" },
        "body": { "temperature": 0.1 }
      }
    }
  }
}
```

> [!WARNING]
> The V2 session runner preserves `request` values but **does not yet send them**
> with model requests. Per-agent temperature, `top_p`, and provider options
> therefore have no effect in V2 today. Configure active request settings on the
> provider, model, or a model variant (see `../models.md`) and select the variant
> with `model: provider/model#variant`.

---

## Built-in agents

| Agent | Mode | Purpose and default policy |
|---|---|---|
| `build` | primary | Default coding agent. Tools allowed; `.env` reads and access outside the workspace ask. Allows questions. |
| `plan` | primary | Explores and plans. Denies edits except files under `~/.opencode/plan`. Shell stays permission-controlled. |
| `general` | subagent | Research and multi-step work with broad tool access. Denies questions and launching subagents. |
| `explore` | subagent | Reads code and web sources. Denies everything except read, glob, grep, webfetch, websearch. |

Hidden maintenance agents: `compaction`, `title`, `summary`. They cannot be
selected directly. **V2 has no built-in `scout` agent** (V1 had one).

Override a built-in by using its ID:

```json
{
  "agents": {
    "build": {
      "permissions": [
        { "action": "shell", "resource": "git push *", "effect": "ask" }
      ]
    }
  }
}
```

In native V2 config, set the title agent's model with `agents.title.model`
(replaces V1 `small_model`).

---

## Default agent

```json
{
  "default_agent": "writer",
  "agents": { "writer": { "mode": "primary" } }
}
```

The default must exist, be visible, and support primary use. Otherwise OpenCode
uses `build`, then the first visible primary-capable agent. Changing it does not
change the agent stored on an existing session.

---

## Merging

- Agent definitions merge in configuration order.
- Later scalar values replace earlier ones.
- `request` maps merge by key.
- `permissions` rules **append**. Global rules apply first, then agent rules, so
  agent rules can refine global ones (last match wins).

---

## Not documented for V2

These V1 features have no equivalent in the V2 pages checked. Do not assume
they exist:

- `opencode agent create` (V1 scaffolding command). V2 recommends asking
  OpenCode to edit config for you.
- `opencode models` (V1 CLI listing). V2 documents `/models` inside a session.
- `@mention` invocation of subagents. V2 docs describe asking the primary agent
  to use a subagent.

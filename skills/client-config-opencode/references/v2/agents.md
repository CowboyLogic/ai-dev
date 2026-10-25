# V2 Agents Reference

Source: <https://opencode.ai/v2/docs/agents/> (2.1.4 tag). Permission rules: [permissions.md](permissions.md).

## Built-in agents

| Agent | Mode | Purpose |
|-------|------|---------|
| `build` | `primary` | Default coding agent; tools and access outside the workspace allowed, `.env` reads ask |
| `plan` | `primary` | Explores and plans; no edits to normal project files (may write OpenCode plan files) |
| `general` | `subagent` | Research and multi-step work; cannot launch more subagents |
| `explore` | `subagent` | Searches and reads code or web sources without editing; shell stays allowed, so it is permission-controlled rather than blocked |
| `compaction`, `title`, `summary` | hidden | Maintenance; not selectable |

V2 has **no built-in `scout` agent** (V1 had one). Override a built-in by defining the same ID.

## Locations

```text
~/.config/opencode/agents/<name>.md      # global
.opencode/agents/<name>.md               # project (discovered from cwd up to the project root)
```

Nested paths become part of the ID: `.opencode/agents/team/reviewer.md` → `team/reviewer`.
V2 still discovers the V1 directories `agent/`, `mode/`, and `modes/` (files under `mode(s)/` are primary agents);
`agents/` is preferred.

## Markdown format

Frontmatter accepts the same fields as an `agents` entry; the body becomes `system`.

V1 frontmatter fields are deprecated but still translated. Each file is read as **one** format: a file that uses any
of `permissions`, `request`, `system`, or `disabled` is read as V2 (2.1.4 release notes), and V1 fields in it, such as
`name`, `tools`, `permission`, or `temperature`, are ignored with a warning in the log. Other files that use V1
fields are read as V1. Convert a file's frontmatter all at once; do not mix the two.

```markdown
---
description: Reviews changes for correctness and regressions
mode: subagent
model: anthropic/claude-sonnet-5-5#high
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

## JSON format

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "agents": {
    "reviewer": {
      "description": "Reviews current changes",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-5-5#high",
      "system": "Report findings in severity order.",
      "steps": 8,
      "color": "#ff6b6b",
      "request": { "headers": { "x-agent": "reviewer" }, "body": { "temperature": 0.1 } },
      "permissions": [{ "action": "edit", "resource": "*", "effect": "deny" }],
    },
  },
}
```

## Fields

| Field | Description |
|-------|-------------|
| `description` | Shown to the model choosing a subagent — add it to every subagent |
| `mode` | `primary` (**default for a new custom agent**), `subagent`, or `all` |
| `model` | `provider/model[#variant]`, or `{ "providerID", "model", "variant" }`. A subagent without a model inherits the parent session's |
| `system` | System prompt; non-empty replaces the provider base prompt. In Markdown, use the body instead |
| `permissions` | Ordered rule array, appended after global rules |
| `steps` | Positive max model steps; on the last step tools are removed and the model summarizes |
| `hidden` | Hide from listings and the subagent catalog (visibility only, not security) |
| `color` | Six-digit hex, e.g. `"#ff6b6b"` |
| `disabled` | Remove a built-in or custom agent |
| `request` | `headers` and JSON `body` overlays (temperature, top_p, provider options). **Preserved but not yet sent** with model requests in V2 — set active request settings on the provider, model, or a model variant instead |

> [!WARNING]
> Do not use V1 agent fields in new V2 agents: `prompt`, `permission`, `tools`, `disable`, `maxSteps`,
> `temperature`, `top_p`, `variant`, `options`, or `name`. Nested agent entries are not format-inferred — keep
> each entry entirely V1 or entirely V2.

The V2 doc documents color as a six-digit hex only; V1's theme color names (`primary`, `accent`, …) are not
mentioned for V2.

## Default agent and small model

```jsonc
{
  "default_agent": "writer",
  "agents": {
    "writer": { "mode": "primary" },
    "title": { "model": "anthropic/claude-haiku-4-5" },
  },
}
```

The default must exist, be visible, and be primary-capable; otherwise OpenCode uses `build`, then the first visible
primary agent. V1 `small_model` maps to `agents.title.model`.

## Merging

Definitions merge in configuration order: later scalars replace earlier ones, `request` maps merge by key, and
`permissions` rules append.

## Subagent control

The parent's `subagent` rules decide which agents it may launch; the child uses its own permissions.
Default nesting depth is one; raise it with `experimental.subagent_depth` (top-level `subagent_depth` is ignored in V2).
Since 2.1.4 a session that has no model of its own uses the selected agent's model (2.1.4 release notes).

```jsonc
{
  "agents": {
    "orchestrator": {
      "permissions": [
        { "action": "subagent", "resource": "*", "effect": "deny" },
        { "action": "subagent", "resource": "reviewer", "effect": "allow" },
      ],
    },
  },
}
```

## TUI

`/agents` or `<leader>a` lists agents; `shift+tab` cycles (`agent.cycle`). Check what loaded with
`opencode debug agents`.

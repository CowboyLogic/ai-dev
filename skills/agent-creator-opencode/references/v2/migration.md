# Converting OpenCode Agents from V1 to V2

Field-by-field mapping for converting V1 agent definitions to the native V2
format.

**Sources (checked 2026-09-24):** <https://opencode.ai/v2/docs/migrate-v1/> ·
<https://opencode.ai/v2/docs/agents/> · <https://opencode.ai/v2/docs/permissions/>

Load this file when converting an existing V1 agent, or when a user on V1 asks
what changes in V2.

> [!IMPORTANT]
> Conversion is **optional**. V2 reads the same config locations as V1 and
> normalizes supported V1 fields in memory without rewriting files. V1 and V2 use
> the same config locations, so **do not point V1 at a file after converting it
> to native V2**. Convert only when the user is on V2 and wants native V2.

---

## Rules for mixed files

- Top-level V1 and V2 fields may coexist in one config file. When both set the
  same value, a valid native V2 value wins regardless of key order.
- Mixed members are recognized only inside `mcp`, `compaction`, and
  `experimental`. **Each individual agent, provider, command, and model must be
  entirely V1 or entirely V2.** Convert a whole agent at once.
- Conflicting V1/V2 values, malformed values, and unsupported legacy fields
  produce warnings; unrelated valid settings still load.

---

## Agent field mapping

| V1 | V2 | Notes |
|---|---|---|
| `agent` (top-level map) | `agents` | |
| `mode` (deprecated top-level map) | `agents` with `mode: primary` | Entries become primary agents |
| `prompt` (JSON) | `system` | Markdown body stays the prompt; no `system` in frontmatter |
| `disable` | `disabled` | |
| `permission` (map) | `permissions` (ordered array) | See conversion below |
| `tools` (boolean map) | `permissions` deny/allow rules | `false` becomes a `deny` rule |
| `model` + `variant` | `model: provider/model#variant` | Remove the separate `variant` |
| `temperature`, `top_p` | `request.body.temperature`, `request.body.top_p` | Not sent yet in V2 (see warning) |
| Provider pass-through keys (`reasoningEffort`, and so on) | `request.body` | Not sent yet in V2 |
| `maxSteps` | `steps` | `steps` already existed in V1 |
| `steps`, `description`, `mode`, `hidden`, `color` | same name | See behavior changes below |
| `name` inside a V1 JSON agent | remove | Ignored by V2 with a warning |
| `small_model` (top level) | `agents.title.model` | |
| `subagent_depth` (top level) | `experimental.subagent_depth` | V2 ignores top-level with a warning |

> [!WARNING]
> The V2 docs state that `request` values are preserved but not yet sent with
> model requests. Converting `temperature` or `reasoningEffort` into
> `request.body` keeps the value but it has no effect today. To keep the
> behavior, move the setting onto a model variant under `providers` and reference
> it with `#variant`. See `../models.md`.

### Behavior changes that are not renames

| Topic | V1 | V2 |
|---|---|---|
| `mode` default | `all` | `primary` for a new custom agent. Set `mode` explicitly when converting. |
| `hidden` | Hides from `@` autocomplete only; model can still invoke via Task | Hides from listings and the subagent catalog |
| `color` | Hex or theme name (`accent`, and so on) | Six-digit hex documented only |
| Built-in `scout` | Exists | Does not exist |
| `.env` reads | `deny` | `ask` |
| No matching rule | Tool default (mostly `allow`) | `ask` (base policy allows all first) |
| `always` approval | Rest of the current session | Durable, project-scoped |
| `doom_loop`, `lsp` permissions | Supported | Not V2 core actions |

The migration guide does not say whether a V1 agent with no `mode` is treated as
`all` or `primary` after V2 loads it. Setting `mode` explicitly removes the
ambiguity.

---

## Permission conversion

Action renames: `bash` becomes `shell`, `task` becomes `subagent`, and `write` and
`patch` become `edit`. Other actions (`read`, `edit`, `glob`, `grep`, `skill`,
`question`, `webfetch`, `websearch`, `external_directory`) keep their names.

Conversion steps for one agent:

1. For a shorthand value (`edit: deny`), emit one rule with `resource: "*"`.
2. For an object value, emit one rule per pattern **in the same order** as the
   V1 object. V1 and V2 both use last-match-wins, so order is preserved.
3. A V1 whole-config string (`"permission": "allow"`) becomes
   `{ "action": "*", "resource": "*", "effect": "allow" }`.
4. A V1 `"*"` key or wildcard key (`"mymcp_*": "deny"`) becomes an `action`
   wildcard rule. Place a `"*"` action rule before per-tool rules so the specific
   rules can override it (this ordering is inferred from V1's "specific key
   overrides `*`" example; the migration guide does not state it).
5. Drop `doom_loop` and `lsp`. Drop `list` and `todowrite` (no documented V2
   action). Tell the user what was dropped.
6. Legacy `tools` entries: `false` becomes `deny` with `resource: "*"`. The V1
   docs define `true` as `{"*": "allow"}`.

Example from the migration guide:

```jsonc
// V1
{
  "permission": {
    "bash": { "git push *": "ask" },
    "edit": "allow"
  },
  "tools": { "websearch": false }
}
```

```jsonc
// V2
{
  "permissions": [
    { "action": "shell", "resource": "git push *", "effect": "ask" },
    { "action": "edit", "resource": "*", "effect": "allow" },
    { "action": "websearch", "resource": "*", "effect": "deny" }
  ]
}
```

---

## Full agent example (JSON)

```jsonc
// V1
{
  "agent": {
    "reviewer": {
      "prompt": "Review for correctness and missing tests.",
      "model": "anthropic/claude-sonnet-5",
      "variant": "high",
      "disable": false,
      "permission": { "edit": "deny" }
    }
  }
}
```

```jsonc
// V2
{
  "agents": {
    "reviewer": {
      "system": "Review for correctness and missing tests.",
      "model": "anthropic/claude-sonnet-5#high",
      "disabled": false,
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" }
      ]
    }
  }
}
```

## Full agent example (Markdown)

V1 `.opencode/agents/reviewer.md`:

```markdown
---
description: Code review without edits
mode: subagent
model: anthropic/claude-sonnet-5
variant: high
temperature: 0.1
permission:
  edit: deny
  bash:
    "*": ask
    "git diff*": allow
  webfetch: deny
---

Only analyze code and suggest changes.
```

V2 `.opencode/agents/reviewer.md`:

```markdown
---
description: Code review without edits
mode: subagent
model: anthropic/claude-sonnet-5#high
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: shell
    resource: "*"
    effect: ask
  - action: shell
    resource: "git diff *"
    effect: allow
  - action: webfetch
    resource: "*"
    effect: deny
request:
  body:
    temperature: 0.1
---

Only analyze code and suggest changes.
```

`temperature` moved to `request.body` as the migration guide directs, but V2
does not send it yet. Tell the user the setting is currently inert, and offer a
model variant if the behavior matters.

`git diff*` became `git diff *`: in V2 a pattern ending in `" *"` also matches the
bare command, which is the usual intent.

---

## File locations

| V1 | V2 |
|---|---|
| `.opencode/agent/`, `.opencode/agents/` | `.opencode/agents/` (both still discovered; path-derived ID unchanged) |
| `.opencode/mode/`, `.opencode/modes/` | `.opencode/agents/` plus `mode: primary` in frontmatter |
| `CLAUDE.md` fallback for instructions | `AGENTS.md` only. V2 does not read `CLAUDE.md`. |

---

## Verify after converting

Start V2 in the project and check the agent appears, its model resolves (unknown
`#variant` is an error), and its permissions behave as intended. Keep a copy of
the V1 files until the V2 behavior is confirmed.

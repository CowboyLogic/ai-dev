# OpenCode V1 Agent Property Reference

Configuration keys for **OpenCode V1** agents (Markdown frontmatter or the
`agent` block in `opencode.json`).

**Sources (checked 2026-09-24):** <https://opencode.ai/docs/agents/> ·
<https://opencode.ai/docs/permissions/> · <https://opencode.ai/docs/config/> ·
<https://opencode.ai/config.json>

> [!IMPORTANT]
> This file describes the **V1** format (`agent`, `prompt`, `permission`,
> `disable`). For native V2 (`agents`, `system`, `permissions`, `disabled`), load
> `../v2/agents.md`. Keep each agent entirely in one format.

Load this file when you need types, defaults, or edge cases for a specific V1
key. For permission syntax and patterns, load `permissions.md` (this folder).
For model IDs, load `../models.md`. For full agent templates, load `examples.md`.

---

## Annotated Full Example

### Markdown format

```yaml
---
# REQUIRED
description: Short description of what this agent does and when to invoke it

# Agent mode — determines how the agent is available
mode: subagent          # primary | subagent | all (default: all)

# Model — uses provider/model-id format
model: anthropic/claude-sonnet-5

# Optional default model variant (e.g. high, max for Anthropic)
variant: high

# Inline prompt or file reference
prompt: "You are a specialized assistant."
# OR: prompt: "{file:./prompts/my-agent.txt}"

# Temperature — controls response randomness (0.0–1.0)
temperature: 0.1

# Top P — alternative randomness control (0.0–1.0)
top_p: 0.9

# Max agentic iterations before forced text response
steps: 10

# Hide from @ autocomplete (subagent mode only)
hidden: false

# Disable this agent entirely
disable: false

# Visual color in the UI
color: "#ff6b6b"        # hex color or theme name

# Permissions — controls what the agent can do
permission:
  read: allow
  edit: deny
  bash:
    "*": ask
    "git status": allow
    "git log*": allow
    "rm -rf*": deny
  webfetch: allow
  task:
    "*": deny
    "reviewer": allow
---

System prompt body goes here. This is the agent's instructions.
```

### JSON format (opencode.json)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "agent-name": {
      "description": "Short description of what this agent does",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-5",
      "variant": "high",
      "prompt": "You are a specialized assistant.",
      "temperature": 0.1,
      "top_p": 0.9,
      "steps": 10,
      "hidden": false,
      "disable": false,
      "color": "#ff6b6b",
      "permission": {
        "edit": "deny",
        "bash": {
          "*": "ask",
          "git status": "allow"
        },
        "webfetch": "allow",
        "task": {
          "*": "deny",
          "reviewer": "allow"
        }
      }
    }
  }
}
```

---

## Property Reference

### description

**Required** (per the V1 agents docs). A brief description of what the agent does and when to use it.

- Used by the OpenCode UI and by other agents to decide when to invoke this agent via the Task tool
- Keep it clear and specific — vague descriptions lead to incorrect auto-invocation
- Include the agent's specialty domain and what it does NOT do

```yaml
description: Reviews code for security vulnerabilities and suggests fixes without making changes
```

```json
"description": "Reviews code for security vulnerabilities and suggests fixes without making changes"
```

---

### mode

Controls how the agent is available to users and other agents.

| Value | Behavior |
|---|---|
| `primary` | User-selectable via Tab key or `switch_agent` keybind; handles main conversations |
| `subagent` | Invoked by primary agents via Task tool or by users via `@mention` |
| `all` | Available as both primary and subagent |

**Default:** `all` (when `mode` is omitted)

```yaml
mode: subagent
```

**Guidance:**

- Use `primary` for agents you want to switch between interactively
- Use `subagent` for specialists that primary agents delegate to
- Subagents can be invoked manually: `@agent-name do something`
- When a primary agent invokes a subagent, it creates a child session
- Top-level `subagent_depth` (default `1`) lets primary agents launch subagents but blocks subagents from launching more. Set `2` for one extra level, `0` to block all subagent launches.

---

### model

Override the model used by this agent. Uses `provider/model-id` format.

**Default:**

- Primary agents: use the globally configured model
- Subagents: inherit the model from the primary agent that invoked them

```yaml
model: anthropic/claude-sonnet-5
```

```yaml
model: openai/gpt-5.5
```

See `../models.md` for valid values. Run `opencode models` to list all available models.

**Guidance:**

- **Always set `model` on new agents** unless the user explicitly asks to omit it and inherit
- Be intentional: match the model to the agent's role (see `../models.md`)
- Use faster/cheaper models for lightweight subagents; stronger models for coding, orchestration, and deep reasoning
- Omit `model` only when inheritance is desired (subagent follows its primary; primary uses global config)

---

### variant

Default model variant for this agent. The config schema notes it **applies only
when the agent uses its configured model** (not an inherited one). Valid values
are model- and provider-specific. Built-in examples from the V1 models docs:

- Anthropic: `high` (default), `max`
- OpenAI: roughly `none`, `minimal`, `low`, `medium`, `high`, `xhigh` (varies by model)
- Google: `low`, `high`

Custom variants are defined under `provider.<id>.models.<model>.variants`.

```yaml
variant: high
```

> [!NOTE]
> `variant` is in the published config schema but is not described on the V1
> agents page. V2 drops this field and uses `model: provider/model#variant`.

---

### prompt

The system prompt for this agent. Can be an inline string or a file reference.

```yaml
# Inline
prompt: "You are a database specialist. Only work with SQL and schema changes."

# File reference (relative to the config file location)
prompt: "{file:./prompts/db-specialist.txt}"
```

```json
"prompt": "{file:./prompts/db-specialist.txt}"
```

**Notes:**

- When using Markdown format, the prompt body (below the frontmatter `---`) is the system prompt — the `prompt` key is not needed in that case
- `{file:./path}` paths are relative to the config file location
- External prompt files allow version-controlling complex prompts separately
- The docs do not define what happens when both a frontmatter `prompt` key and a Markdown body are present. Use one or the other.

---

### temperature

Controls the randomness and creativity of model responses. Ranges from `0.0` to `1.0`.

| Range | Behavior |
|---|---|
| `0.0–0.2` | Deterministic, focused — best for code analysis, security review, planning |
| `0.3–0.5` | Balanced — good for general development tasks |
| `0.6–1.0` | Creative, varied — useful for brainstorming, documentation, exploration |

**Default:** Model-specific (typically `0` for most models, `0.55` for Qwen models)

```yaml
temperature: 0.1
```

```json
"temperature": 0.1
```

---

### top_p

Alternative to `temperature` for controlling response diversity. Ranges from `0.0` to `1.0`.

- Lower values: more focused
- Higher values: more diverse

```yaml
top_p: 0.9
```

**Note:** Generally use either `temperature` or `top_p`, not both simultaneously.

---

### steps

Maximum number of agentic iterations before the agent is forced to respond with text only.

**Default:** Unlimited (agent iterates until the model stops or the user interrupts)

```yaml
steps: 10
```

```json
"steps": 10
```

**When the limit is reached:** The agent receives a system prompt instructing it to summarize its work and list remaining tasks.

**Note:** The legacy `maxSteps` field is deprecated. Use `steps`.

**Guidance:**

- Set a step limit on orchestrator agents to control cost
- Leave unlimited for focused single-task agents
- A limit of 5–10 is appropriate for analysis agents; 20–50 for build agents on large tasks

---

### permission

Controls what actions the agent can take. See `permissions.md` for full details.

```yaml
permission:
  edit: deny
  bash: ask
  webfetch: allow
```

**Agent permissions are merged with global permissions; agent rules take precedence.**

---

### hidden

Hide the agent from the `@` autocomplete menu. The agent can still be invoked by the model via the Task tool if permissions allow. (V2 changes this: hidden agents are also removed from the subagent catalog.)

**Default:** `false`

**Only applies to:** `mode: subagent` agents

```yaml
hidden: true
```

```json
"hidden": true
```

**Use cases:**

- Internal pipeline agents that should only be called by orchestrators
- Helper agents that aren't useful for users to invoke directly

---

### color

Customize the agent's visual appearance in the OpenCode UI.

**Values:**

- Hex color: `"#FF5733"`, `"#6c63ff"`, `"#ff6b6b"`
- Theme color: `primary`, `secondary`, `accent`, `success`, `warning`, `error`, `info`

```yaml
color: "#6c63ff"
```

```yaml
color: accent
```

---

### disable

Set to `true` to disable the agent without deleting its configuration.

**Default:** `false`

```json
"disable": true
```

---

### tools (deprecated)

> [!WARNING]
> **Deprecated as of v1.1.1.** Use `permission` instead.

The `tools` boolean map is still supported for backwards compatibility but should not be used in new configs.

```json
"tools": {
  "write": false,
  "edit": false,
  "bash": true
}
```

In the legacy system, `true` = `{"*": "allow"}` permission and `false` = `{"*": "deny"}` permission. Wildcards like `"mymcp_*"` were also supported.

---

### options

The config schema also lists an `options` object on agents. The V1 agents page
does not document it; prefer the documented pass-through keys below.

---

### Additional provider options

Any other key in the agent config is passed through directly to the provider as a model option. This allows provider-specific parameters.

```json
{
  "agent": {
    "deep-thinker": {
      "description": "Uses high reasoning effort for complex architectural decisions",
      "model": "openai/gpt-5",
      "reasoningEffort": "high",
      "textVerbosity": "low"
    }
  }
}
```

Check your model provider's documentation for available parameters.

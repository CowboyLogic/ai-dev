# OpenCode Agent Configuration Reference

Complete reference for all agent configuration properties in the OpenCode CLI.

**Sources:** https://opencode.ai/docs/agents/ · https://opencode.ai/docs/permissions/

---

## Table of Contents

1. [Annotated Full Example](#annotated-full-example)
2. [Property Reference](#property-reference)
   - [description](#description)
   - [mode](#mode)
   - [model](#model)
   - [prompt](#prompt)
   - [temperature](#temperature)
   - [top_p](#top_p)
   - [steps](#steps)
   - [permission](#permission)
   - [hidden](#hidden)
   - [color](#color)
   - [disable](#disable)
   - [tools (deprecated)](#tools-deprecated)
   - [Additional provider options](#additional-provider-options)
3. [Permission Deep Reference](#permission-deep-reference)
4. [Model ID Format](#model-id-format)
5. [Complete Working Examples](#complete-working-examples)

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
model: anthropic/claude-sonnet-4-20250514

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
      "model": "anthropic/claude-sonnet-4-20250514",
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

**Required.** A brief description of what the agent does and when to use it.

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

---

### model

Override the model used by this agent. Uses `provider/model-id` format.

**Default:**
- Primary agents: use the globally configured model
- Subagents: inherit the model from the primary agent that invoked them

```yaml
model: anthropic/claude-sonnet-4-20250514
```

```yaml
model: openai/gpt-4o
```

See [Model ID Format](#model-id-format) for valid values. Run `opencode models` to list all available models.

**Guidance:**
- Use faster/cheaper models for planning and analysis agents (`claude-haiku`)
- Use stronger models for code generation and complex reasoning (`claude-sonnet`, `gpt-5`)
- Omit model for subagents when you want them to use whatever the primary agent is using

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
- When both the frontmatter `prompt` key and a Markdown body are present, behavior may be undefined — use one or the other

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

Maximum number of agentic iterations (tool calls) before the agent is forced to respond with text only.

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

Controls what actions the agent can take. See [Permission Deep Reference](#permission-deep-reference) for full details.

```yaml
permission:
  edit: deny
  bash: ask
  webfetch: allow
```

**Agent permissions are merged with global permissions; agent rules take precedence.**

---

### hidden

Hide the agent from the `@` autocomplete menu. The agent can still be invoked programmatically by other agents via the Task tool.

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

### Additional provider options

Any key not recognized by OpenCode is passed directly to the model provider. This allows provider-specific parameters.

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

---

## Permission Deep Reference

### Syntax forms

**Simple form** — same action for all inputs:

```yaml
permission:
  edit: deny
  webfetch: allow
  bash: ask
```

**Object form** — different actions per input pattern:

```yaml
permission:
  bash:
    "*": ask
    "git *": allow
    "git commit *": ask
    "git push *": deny
    "rm *": deny
    "grep *": allow
  edit:
    "*": deny
    "src/docs/**": allow
```

### Pattern matching rules

- `*` — matches zero or more of any character
- `?` — matches exactly one character
- All other characters match literally
- **Last matching rule wins** — put the catch-all `"*"` first, specific overrides after
- Commands matched against full command string including arguments: `"git status"` matches `git status --porcelain`
- For commands with arguments, use `"git status *"` to also allow argument variants

```yaml
permission:
  bash:
    "*": ask           # default: ask for everything
    "git *": allow     # allow all git subcommands
    "git push *": deny # but block push (overrides the git * rule above)
```

### Available permission keys

| Key | What it matches |
|---|---|
| `read` | File path being read |
| `edit` | File path being written/edited/patched |
| `glob` | Glob pattern being used |
| `grep` | Regex being searched |
| `bash` | Full shell command string |
| `webfetch` | URL being fetched |
| `websearch` / `codesearch` | Search query |
| `task` | Subagent name being invoked |
| `skill` | Skill name being loaded |
| `lsp` | LSP queries (non-granular) |
| `external_directory` | Paths outside the project working directory |
| `doom_loop` | Repeated identical tool calls (safety guard) |

### Defaults

- Most permissions: `allow`
- `doom_loop`: `ask`
- `external_directory`: `ask`
- `read` for `.env` files: `deny` (`.env`, `.env.*` denied, `.env.example` allowed)

### External directory access

To allow an agent to access files outside the project root:

```yaml
permission:
  external_directory:
    "~/projects/shared/**": allow
  edit:
    "~/projects/shared/**": deny  # read allowed but not edit
```

### Task permissions (subagent invocation)

Control which subagents this agent can invoke via the Task tool:

```yaml
permission:
  task:
    "*": deny                 # block all subagent invocation by default
    "orchestrator-*": allow   # allow agents matching this pattern
    "code-reviewer": ask      # ask before invoking this specific agent
```

- `deny`: the subagent is removed from the Task tool description; the model won't attempt to invoke it
- Users can always invoke subagents directly via `@mention` regardless of task permissions
- Rules evaluated in order; last match wins

---

## Model ID Format

```
provider/model-id
```

Run `opencode models` to list all model IDs for your configured providers.

### GitHub Copilot models

Auth via GitHub OAuth — use `/connect` inside opencode to authenticate. No API key required.

| Model ID | Display Name | Best for |
|---|---|---|
| `github-copilot/claude-sonnet-4.6` | Claude Sonnet 4.6 | Orchestrators, complex code generation |
| `github-copilot/claude-opus-4.6` | Claude Opus 4.6 | Highest-quality reasoning and architecture agents |
| `github-copilot/claude-opus-4.7` | Claude Opus 4.7 | Highest-quality reasoning and architecture agents |
| `github-copilot/claude-opus-4.5` | Claude Opus 4.5 | Heavyweight analysis agents |
| `github-copilot/claude-opus-41` | Claude Opus 4.1 | Heavyweight analysis agents |
| `github-copilot/claude-sonnet-4` | Claude Sonnet 4 | Orchestrators, general coding |
| `github-copilot/gpt-5.4` | GPT-5.4 | Code review, complex reasoning |
| `github-copilot/gpt-5.3-codex` | GPT-5.3-Codex | Code-focused agents |
| `github-copilot/gpt-5.2-codex` | GPT-5.2-Codex | Code-focused agents |
| `github-copilot/gpt-5.2` | GPT-5.2 | General-purpose agents |
| `github-copilot/gpt-5.4-mini` | GPT-5.4 Mini | Fast subagents, planning, analysis |
| `github-copilot/gpt-5.4-nano` | GPT-5.4 Nano | High-volume lightweight subagents |
| `github-copilot/gpt-5-mini` | GPT-5-mini | Fast, cheap subagents |
| `github-copilot/gpt-5.5` | GPT-5.5 | High-capability general agents |
| `github-copilot/gpt-5.1-codex` | GPT-5.1-Codex | Code generation |
| `github-copilot/gpt-5.1-codex-mini` | GPT-5.1-Codex-mini | Lightweight code agents |
| `github-copilot/gpt-5.1-codex-max` | GPT-5.1-Codex-max | Max-context code agents |
| `github-copilot/gemini-3.1-pro-preview` | Gemini 3.1 Pro Preview | Architecture, design, multimodal agents |
| `github-copilot/gemini-3-pro-preview` | Gemini 3 Pro Preview | Architecture, design, multimodal agents |
| `github-copilot/gemini-3-flash-preview` | Gemini 3 Flash | Fast, cheap analysis subagents |
| `github-copilot/gemini-2.5-pro` | Gemini 2.5 Pro | Deep reasoning, large context |
| `github-copilot/grok-code-fast-1` | Grok Code Fast 1 | Research, web-augmented agents |

### Other common providers

| Provider | Example model IDs |
|---|---|
| Anthropic | `anthropic/claude-sonnet-4-20250514` |
| Anthropic | `anthropic/claude-haiku-4-20250514` |
| OpenAI | `openai/gpt-4o` |
| OpenAI | `openai/gpt-5` |
| OpenCode Zen | `opencode/gpt-5.1-codex` |

**When to specify model per-agent:**
- Different capability tiers for different roles (nano/mini for planning, sonnet/opus for coding)
- Specific provider features (reasoning effort, extended context)
- Subagents that should always use a specific model regardless of the primary agent

---

## Complete Working Examples

### Code Reviewer (subagent, read-only)

`.opencode/agents/code-reviewer.md`

```markdown
---
description: Reviews code changes for security issues, performance problems, and maintainability. Does not modify files.
mode: subagent
model: anthropic/claude-haiku-4-20250514
temperature: 0.1
permission:
  edit: deny
  bash:
    "git diff*": allow
    "git log*": allow
    "*": deny
  webfetch: deny
---

You are a code reviewer. When given code or a diff, analyze it for:

- Security vulnerabilities (injection, auth bypass, data exposure)
- Performance issues (N+1 queries, unnecessary allocations, blocking calls)
- Code clarity and maintainability
- Missing error handling or edge cases

Format your response as:

**Summary:** One sentence overview
**Issues found:** Bulleted list with severity (critical/major/minor)
**Suggestions:** Specific, actionable improvements

Do not make any changes to files. Do not run tests.
```

### Database Migration Specialist (subagent, controlled write access)

`.opencode/agents/db-migrator.md`

```markdown
---
description: Creates and validates database migration files. Runs migrations in dry-run mode only unless explicitly asked.
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
permission:
  edit:
    "migrations/**": allow
    "*": deny
  bash:
    "psql --dry-run*": allow
    "alembic check": allow
    "alembic history": allow
    "*": ask
  webfetch: deny
---

You are a database migration specialist. Your responsibilities:

- Generate new migration files in the `migrations/` directory
- Validate migration syntax and safety
- Check for missing indexes, locking issues, and data loss risks
- Never run destructive migrations without explicit user confirmation

Always use `--dry-run` or equivalent when testing migrations.
```

### Orchestrator (primary, multi-agent workflow)

`.opencode/agents/dev-lead.md`

```markdown
---
description: Coordinates complex development tasks by delegating to specialized subagents. Use for multi-step workflows involving code changes, tests, and review.
mode: primary
model: anthropic/claude-sonnet-4-20250514
temperature: 0.2
steps: 30
permission:
  edit: ask
  bash:
    "*": ask
    "git status": allow
    "git log*": allow
    "git diff*": allow
  webfetch: allow
  task:
    "code-reviewer": allow
    "db-migrator": ask
    "*": allow
---

You are a development lead who coordinates complex tasks. Break down large requests into subtasks and delegate them to specialized subagents.

Workflow:
1. Clarify requirements and scope
2. Create a plan with clear subtasks
3. Delegate to appropriate subagents using the Task tool
4. Review all subagent output before proceeding
5. Run the code reviewer before marking work complete

Do not write code directly — delegate to the appropriate specialist.
```

### Security Auditor (subagent, aggressive read-only)

`~/.config/opencode/agents/security-auditor.md`

```markdown
---
description: Performs deep security audits across the codebase. Identifies vulnerabilities without making changes. Invoke with @security-auditor.
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.0
permission:
  edit: deny
  bash:
    "grep *": allow
    "find *": allow
    "cat *": allow
    "git log*": allow
    "git diff*": allow
    "*": deny
  webfetch: deny
---

You are a security expert performing a thorough audit. Focus on:

- Input validation vulnerabilities (injection, XSS, CSRF)
- Authentication and authorization flaws
- Sensitive data exposure (credentials in code, weak encryption)
- Dependency vulnerabilities
- Configuration security issues (open ports, weak defaults)
- Business logic flaws

For each finding, report:
- **Severity**: Critical / High / Medium / Low
- **Location**: File and line number
- **Description**: What is vulnerable and why
- **Recommendation**: Specific fix

Do not modify any files.
```

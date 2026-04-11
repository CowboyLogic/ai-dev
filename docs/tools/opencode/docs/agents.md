# OpenCode — Agents

> Source: <https://opencode.ai/docs/agents/>  
> Last updated: April 10, 2026

Agents are specialized AI assistants configured for specific tasks: custom prompts, models, and tool access.

---

## Agent Types

### Primary agents

Direct assistants you interact with. Cycle through them with `Tab` (or `switch_agent` keybind). Full tool access is configured per-agent via permissions.

### Subagents

Specialized assistants invoked by primary agents or manually via `@mention`.

```
@general help me search for this function
```

---

## Built-in Agents

| Agent | Mode | Description |
|-------|------|-------------|
| `build` | primary | Default agent — all tools enabled |
| `plan` | primary | Analysis only — `edit` and `bash` set to `ask` |
| `general` | subagent | General research and multi-step tasks (full tools minus todo) |
| `explore` | subagent | Read-only codebase exploration — cannot modify files |
| `compaction` | primary (hidden) | Auto-compacts long context |
| `title` | primary (hidden) | Auto-generates session titles |
| `summary` | primary (hidden) | Auto-creates session summaries |

---

## Usage

- Press `Tab` to cycle primary agents
- Invoke subagents with `@agent-name` in your message
- Navigate child sessions: `<Leader>+Down` (enter), `Right`/`Left` (cycle), `Up` (return to parent)

---

## Configuration

### JSON

```jsonc
// opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "build": {
      "mode": "primary",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "{file:./prompts/build.txt}",
      "tools": { "write": true, "edit": true, "bash": true }
    },
    "plan": {
      "mode": "primary",
      "model": "anthropic/claude-haiku-4-20250514",
      "tools": { "write": false, "edit": false, "bash": false }
    },
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "tools": { "write": false, "edit": false }
    }
  }
}
```

### Markdown files

Place agents in:
- Global: `~/.config/opencode/agents/`
- Per-project: `.opencode/agents/`

The filename becomes the agent name (`review.md` → `review` agent).

```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
tools:
  write: false
  edit: false
  bash: false
---

You are in code review mode. Focus on:

- Code quality and best practices
- Potential bugs and edge cases
- Performance implications
- Security considerations
```

### Create interactively

```bash
opencode agent create
```

Guides you through agent creation and generates the markdown file.

---

## Configuration Options

### `description`

Brief description of the agent's purpose. **Required** for custom agents.

### `mode`

| Value | Meaning |
|-------|---------|
| `primary` | Main agent — selectable via Tab |
| `subagent` | Invoked by primary agents or `@mention` |
| `all` | Both (default if not specified) |

### `model`

Override the model for this agent:

```jsonc
{
  "agent": {
    "plan": { "model": "anthropic/claude-haiku-4-20250514" }
  }
}
```

Format: `provider/model-id`.

### `prompt`

Custom system prompt file:

```jsonc
{
  "agent": {
    "review": { "prompt": "{file:./prompts/code-review.txt}" }
  }
}
```

Path is relative to the config file location.

### `temperature`

| Range | Use case |
|-------|---------|
| `0.0–0.2` | Very focused — code analysis, planning |
| `0.3–0.5` | Balanced — general development |
| `0.6–1.0` | Creative — brainstorming, exploration |

Default is model-specific (usually `0`, Qwen models use `0.55`).

### `steps`

Maximum agentic iterations:

```jsonc
{
  "agent": {
    "quick-thinker": {
      "steps": 5
    }
  }
}
```

When the limit is reached, the agent summarizes and lists remaining tasks.

### `permissions`

```jsonc
{
  "permission": { "edit": "deny" },
  "agent": {
    "build": {
      "permission": { "edit": "ask" }
    }
  }
}
```

Values: `"allow"`, `"ask"`, `"deny"`.

**Bash command-level permissions:**

```jsonc
{
  "agent": {
    "build": {
      "permission": {
        "bash": {
          "*": "ask",
          "git status *": "allow"
        }
      }
    }
  }
}
```

Supports glob patterns. Last matching rule wins.

### `hidden`

Hide a subagent from `@` autocomplete (still invocable by other agents):

```jsonc
{
  "agent": {
    "internal-helper": { "mode": "subagent", "hidden": true }
  }
}
```

### `color`

```jsonc
{
  "agent": {
    "creative": { "color": "#ff6b6b" },
    "code-reviewer": { "color": "accent" }
  }
}
```

Accepts hex colors or theme tokens: `primary`, `secondary`, `accent`, `success`, `warning`, `error`, `info`.

### `top_p`

Alternative to `temperature` for controlling response diversity (0.0–1.0).

### `disable`

```jsonc
{
  "agent": {
    "review": { "disable": true }
  }
}
```

### Task permissions

Control which subagents a primary agent can invoke via the Task tool:

```jsonc
{
  "agent": {
    "orchestrator": {
      "mode": "primary",
      "permission": {
        "task": {
          "*": "deny",
          "orchestrator-*": "allow",
          "code-reviewer": "ask"
        }
      }
    }
  }
}
```

---

## Example Agents

### Documentation writer

```markdown
---
description: Writes and maintains project documentation
mode: subagent
tools:
  bash: false
---

You are a technical writer. Create clear, comprehensive documentation.

Focus on:
- Clear explanations
- Proper structure
- Code examples
- User-friendly language
```

### Security auditor

```markdown
---
description: Performs security audits and identifies vulnerabilities
mode: subagent
tools:
  write: false
  edit: false
---

You are a security expert. Focus on identifying potential security issues.

Look for:
- Input validation vulnerabilities
- Authentication and authorization flaws
- Data exposure risks
- Dependency vulnerabilities
- Configuration security issues
```

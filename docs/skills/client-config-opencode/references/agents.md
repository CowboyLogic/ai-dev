# Agents Reference

## Built-in agents

| Agent | Mode | Default behavior |
|-------|------|-----------------|
| `build` | primary | Full tool access — default for development work |
| `plan` | primary | file edits and bash set to `ask` — analysis/planning |
| `general` | subagent | Full access — multi-step research tasks |
| `explore` | subagent | Read-only codebase exploration |

Switch primary agents with Tab or the `switch_agent` keybind.
Invoke subagents with `@general`, `@explore`, or let the primary agent call them automatically.

---

## Agent configuration in opencode.json

```json
{
  "agent": {
    "build": {
      "model": "anthropic/claude-opus-4-5",
      "steps": 50
    },
    "plan": {
      "prompt": "{file:~/.config/opencode/prompts/plan.md}"
    },
    "my-reviewer": {
      "description": "Reviews code for security and quality issues",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-5",
      "temperature": 0.1,
      "color": "#e06c75",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      }
    }
  }
}
```

## Agent fields reference

| Field | Description | Example |
|-------|-------------|---------|
| `description` | Purpose — used for @ autocomplete and auto-routing | `"Reviews code for quality"` |
| `mode` | `"primary"` (user-selectable), `"subagent"` (invoked by agents), `"all"` | `"subagent"` |
| `model` | Override default model for this agent | `"anthropic/claude-opus-4-5"` |
| `variant` | Model variant specification | `"thinking"` |
| `prompt` | System prompt — inline string or `{file:path}` | `"{file:./prompts/reviewer.md}"` |
| `temperature` | Response randomness 0.0–1.0 | `0.1` |
| `top_p` | Response diversity control | `0.9` |
| `steps` | Max agentic iterations before falling back to text | `30` |
| `permission` | Tool access rules (see permissions.md) | `{"edit": "deny"}` |
| `color` | Hex `#RRGGBB` or theme color name | `"#e06c75"` or `"accent"` |
| `disable` | Set `true` to disable agent | `true` |
| `hidden` | Hide from @ autocomplete | `true` |
| `options` | Generic options object | `{}` |

Theme color names: `primary`, `secondary`, `accent`, `success`, `warning`, `error`, `info`

---

## Agent markdown files (alternative to JSON)

Create agents as markdown files with YAML frontmatter:

**Global**: `~/.config/opencode/agents/<name>.md`
**Project**: `.opencode/agents/<name>.md`

```markdown
---
description: Reviews code for security vulnerabilities and quality issues
mode: subagent
model: anthropic/claude-sonnet-4-5
temperature: 0.1
color: "#e06c75"
permission:
  edit: deny
  bash: deny
  read: allow
---

# Security Reviewer

You are a security-focused code reviewer. When reviewing code:

1. Check for injection vulnerabilities (SQL, command, XSS)
2. Identify exposed secrets or credentials
3. Flag insecure dependencies
4. Look for auth and authorization flaws
5. Note insecure data handling

Always provide specific line references and concrete remediation steps.
```

**Invoke via CLI**: `opencode agent create` for interactive setup.

---

## Granular bash permissions in agents

Use glob patterns for fine-grained bash control:

```json
{
  "agent": {
    "build": {
      "permission": {
        "bash": {
          "*": "ask",
          "git status": "allow",
          "git diff *": "allow",
          "git add *": "allow",
          "git commit *": "allow",
          "git push *": "deny",
          "npm run *": "allow",
          "rm *": "ask"
        }
      }
    }
  }
}
```

---

## Default agent

```json
{ "default_agent": "build" }
```

Must be a `primary` mode agent. The default is `build`.

# Agents Reference

## Built-in agents

| Agent | Mode | Default behavior |
|-------|------|-----------------|
| `build` | primary | Full tool access — default for development work |
| `plan` | primary | file edits and bash set to `ask` — analysis/planning |
| `general` | subagent | Full access (except todo) — multi-step research tasks, parallelizable |
| `explore` | subagent | Read-only codebase exploration — find files/patterns fast |
| `scout` | subagent | Read-only external docs/dependency research — clones deps into opencode's cache, cross-references upstream source |
| `compaction` | system (hidden) | Summarises context when it fills up |
| `title` | system (hidden) | Generates session titles |
| `summary` | system (hidden) | Generates session summaries |

Switch primary agents with Tab (`agent_cycle`) or Shift+Tab (`agent_cycle_reverse`).
Invoke subagents with `@general`, `@explore`, `@scout`, or let the primary agent call them automatically.
When a subagent creates a child session: `session_child_first` (default Leader+Down) enters it, `session_child_cycle`/`session_child_cycle_reverse` (default Right/Left) cycle siblings, `session_parent` (default Up) returns.

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
| `description` | Purpose — used for @ autocomplete and auto-routing. **Required** | `"Reviews code for quality"` |
| `mode` | `"primary"` (user-selectable), `"subagent"` (invoked by agents), `"all"` — defaults to `"all"` if unset | `"subagent"` |
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
        },
        "task": {
          "*": "allow",
          "my-mcp_*": "deny"
        }
      }
    }
  }
}
```

The `task` permission controls which subagents this agent can invoke, using glob patterns on agent or MCP tool names. Set `"deny"` to block invocation.

---

## Default agent

```json
{ "default_agent": "build" }
```

Must be a `primary` mode agent. The default is `build`.

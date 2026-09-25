# V1 Agents Reference

> [!NOTE]
> This file covers **V1** agent config (`agent` map, `prompt`, `permission`, `disable`, `temperature`). Native V2
> uses `agents`, `system`, `permissions` arrays, `disabled`, and `request.body`, defaults new custom agents to
> `mode: primary`, and has no `scout` agent. See [v2/agents.md](v2/agents.md).

## Built-in agents

| Agent | Mode | Default behavior |
|-------|------|-----------------|
| `build` | primary | Full tool access — default for development work |
| `plan` | primary | file edits and bash set to `ask` — analysis/planning |
| `general` | subagent | Full access (except todo) — multi-step research tasks, parallelizable |
| `explore` | subagent | Read-only codebase exploration — find files/patterns fast |
| `scout` | subagent | Read-only external docs/dependency research — clones deps into opencode's cache, cross-references upstream source |
| `compaction` | primary (hidden) | Summarises context when it fills up |
| `title` | primary (hidden) | Generates session titles |
| `summary` | primary (hidden) | Generates session summaries |

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
| `variant` | Default model variant (applies only when using the agent's configured model) | `"high"` |
| `prompt` | System prompt — inline string or `{file:path}` (path relative to the config file) | `"{file:./prompts/reviewer.md}"` |
| `temperature` | Response randomness, typically 0.0–1.0; unset uses model defaults | `0.1` |
| `top_p` | Response diversity control | `0.9` |
| `steps` | Max agentic iterations before falling back to text | `30` |
| `permission` | Tool access rules (see permissions.md) | `{"edit": "deny"}` |
| `color` | Hex `#RRGGBB` or theme color name | `"#e06c75"` or `"accent"` |
| `disable` | Set `true` to disable agent | `true` |
| `hidden` | Hide a subagent from @ autocomplete (still invocable via the Task tool) | `true` |
| `options` | Generic options object | `{}` |
| `tools` | **Deprecated** — use `permission` (`true` ≈ `{"*": "allow"}`, `false` ≈ `{"*": "deny"}`) | `{"write": false}` |
| `maxSteps` | **Deprecated** — use `steps` | — |

Theme color names: `primary`, `secondary`, `accent`, `success`, `warning`, `error`, `info`

Any other key in an agent entry is passed straight to the provider as a model option (e.g. `"reasoningEffort": "high"`
for OpenAI reasoning models).

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
          "*": "deny",
          "code-reviewer": "ask",
          "orchestrator-*": "allow"
        }
      }
    }
  }
}
```

The `task` permission controls which subagents this agent can invoke via the Task tool, using glob patterns on
subagent names. A denied subagent is removed from the Task tool description entirely.

---

## Default agent

```json
{ "default_agent": "build" }
```

Must be a `primary` mode agent. The default is `build`.

# OpenCode — Permissions

> Source: <https://opencode.ai/docs/permissions/>  
> Last updated: April 10, 2026

The `permission` config controls whether a given action runs automatically, prompts for approval, or is blocked outright.

> As of v1.1.1, the legacy `tools` boolean config is deprecated and merged into `permission`. The old config is still supported for backwards compatibility.

---

## Actions

Each permission rule resolves to one of:

| Value | Behavior |
|-------|----------|
| `"allow"` | Run without approval |
| `"ask"` | Prompt for approval |
| `"deny"` | Block the action |

---

## Configuration

Set a global default and override specific tools:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "*": "ask",
    "bash": "allow",
    "edit": "deny"
  }
}
```

Set all permissions at once:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": "allow"
}
```

---

## Granular Rules (Object Syntax)

Use an object to apply different actions based on the tool input:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "npm *": "allow",
      "rm *": "deny",
      "grep *": "allow"
    },
    "edit": {
      "*": "deny",
      "packages/web/src/content/docs/*.mdx": "allow"
    }
  }
}
```

Rules are evaluated by pattern match; **the last matching rule wins**. Put the catch-all `"*"` first, more specific rules after.

### Wildcards

- `*` matches zero or more of any character
- `?` matches exactly one character
- All other characters match literally

### Home Directory Expansion

Use `~` or `$HOME` at the start of a pattern:

```
~/projects/*  →  /Users/username/projects/*
$HOME/projects/*  →  /Users/username/projects/*
```

### External Directories

Use `external_directory` to allow tool calls outside the working directory:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "external_directory": {
      "~/projects/personal/**": "allow"
    }
  }
}
```

Layer additional allow/deny rules:

```jsonc
{
  "permission": {
    "external_directory": {
      "~/projects/personal/**": "allow"
    },
    "edit": {
      "~/projects/personal/**": "deny"
    }
  }
}
```

---

## Available Permissions

| Permission | Matches |
|------------|---------|
| `read` | File path being read |
| `edit` | All file modifications (edit, write, patch, multiedit) |
| `glob` | Glob pattern |
| `grep` | Regex pattern |
| `list` | Directory path |
| `bash` | Parsed shell command (e.g., `git status --porcelain`) |
| `task` | Subagent type |
| `skill` | Skill name |
| `lsp` | LSP queries (non-granular) |
| `question` | Asking user questions |
| `webfetch` | URL being fetched |
| `websearch` / `codesearch` | Search query |
| `external_directory` | Tool touching paths outside project directory |
| `doom_loop` | Same tool call repeated 3 times with identical input |

---

## Defaults

| Permission | Default |
|------------|---------|
| Most permissions | `"allow"` |
| `doom_loop` | `"ask"` |
| `external_directory` | `"ask"` |
| `read` on `*.env`, `*.env.*` | `"deny"` |
| `read` on `*.env.example` | `"allow"` |

---

## What "Ask" Does

When OpenCode prompts for approval:

| Option | Behavior |
|--------|----------|
| `once` | Approve just this request |
| `always` | Approve future matching requests (for this session) |
| `reject` | Deny the request |

---

## Per-Agent Permissions

Override permissions for specific agents. Agent rules take precedence over global config:

```jsonc
{
  "permission": {
    "bash": {
      "*": "ask",
      "git *": "allow",
      "git commit *": "deny",
      "git push *": "deny"
    }
  },
  "agent": {
    "build": {
      "permission": {
        "bash": {
          "*": "ask",
          "git *": "allow",
          "git commit *": "ask",
          "git push *": "deny"
        }
      }
    }
  }
}
```

Via Markdown agent config:

```markdown
---
description: Code review without edits
mode: subagent
permission:
  edit: deny
  bash: ask
  webfetch: deny
---

Only analyze code and suggest changes.
```

> **Tip:** Use pattern matching for commands with arguments. `"grep *"` allows `grep pattern file.txt`, while `"grep"` alone would block it when arguments are passed.

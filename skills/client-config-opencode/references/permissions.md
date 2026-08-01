# Permissions Reference

## Structure

Permissions can be set globally (top-level) or per-agent.

```json
{
  "permission": {
    "bash": "ask",
    "edit": "allow",
    "read": "allow",
    "webfetch": "ask"
  },
  "agent": {
    "build": {
      "permission": {
        "bash": "allow",
        "edit": "allow"
      }
    },
    "plan": {
      "permission": {
        "bash": "ask",
        "edit": "ask"
      }
    }
  }
}
```

---

## Permission actions

| Action | Behavior |
|--------|----------|
| `"allow"` | Runs without prompting |
| `"ask"` | Prompts for confirmation each time |
| `"deny"` | Blocked entirely |

---

## Permission types

Permission keys are matched as wildcard patterns against the underlying tool name — the same glob syntax works for built-ins, custom tools, and MCP tools (e.g. `"mymcp_*": "deny"` denies every tool from an MCP server).

### Rule-based (support glob patterns per-command)

| Key | Gates | Description |
|-----|-------|-------------|
| `read` | `read` | File reading |
| `edit` | `write`, `edit`, `apply_patch` | File editing/writing |
| `glob` | `glob` | File pattern matching |
| `grep` | `grep` | File content searching |
| `list` | `list` | Directory listing |
| `bash` | `bash` | Shell command execution |
| `task` | — | Which subagents/MCP tools this agent can invoke |
| `lsp` | `lsp` | Language server protocol |
| `skill` | `skill` | Skill execution |
| `external_directory` | any tool | Reading/writing outside the project worktree |

### Simple action (single value only)

| Key | Gates | Description |
|-----|-------|-------------|
| `todowrite` | `todowrite`, `todoread` | Task list writing/reading |
| `question` | `question` | Asking clarifying questions |
| `webfetch` | `webfetch` | Fetching URLs |
| `websearch` | `websearch` | Web search queries |
| `doom_loop` | — | Recovery prompts when an agent appears stuck |

> [!NOTE]
> `codesearch` is not a current permission key — removed/renamed upstream; don't rely on it.

---

## Glob patterns for bash

The `bash` permission supports an object with glob patterns as keys:

```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git status": "allow",
      "git diff *": "allow",
      "git add *": "allow",
      "git commit *": "allow",
      "git push *": "deny",
      "npm run *": "allow",
      "npm install *": "ask",
      "rm *": "ask",
      "rm -rf *": "deny"
    }
  }
}
```

Rules are evaluated in order and **the last matching rule wins** — put `"*"` first and more specific patterns after it, not the other way around (a trailing `"*"` would override everything above it).

---

## Common patterns

### Permissive (trust all)
```json
{
  "permission": {
    "bash": "allow",
    "edit": "allow",
    "read": "allow",
    "webfetch": "allow"
  }
}
```

### Cautious (ask for writes)
```json
{
  "permission": {
    "read": "allow",
    "glob": "allow",
    "grep": "allow",
    "list": "allow",
    "edit": "ask",
    "bash": "ask",
    "webfetch": "ask"
  }
}
```

### Read-only agent
```json
{
  "agent": {
    "my-analyzer": {
      "permission": {
        "read": "allow",
        "glob": "allow",
        "grep": "allow",
        "list": "allow",
        "edit": "deny",
        "bash": "deny",
        "webfetch": "deny"
      }
    }
  }
}
```

### Safe git workflow
```json
{
  "permission": {
    "bash": {
      "*": "ask",
      "git status": "allow",
      "git log *": "allow",
      "git diff *": "allow",
      "git add *": "allow",
      "git commit *": "allow",
      "git push *": "deny"
    }
  }
}
```

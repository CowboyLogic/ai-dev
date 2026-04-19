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

### Rule-based (support glob patterns per-command)

| Tool | Description |
|------|-------------|
| `read` | File reading |
| `edit` | File editing/writing |
| `glob` | File pattern matching |
| `grep` | File content searching |
| `list` | Directory listing |
| `bash` | Shell command execution |
| `task` | Spawning subtasks |
| `lsp` | Language server protocol |
| `skill` | Skill execution |
| `external_directory` | Access outside working directory |

### Simple action (single value only)

| Tool | Description |
|------|-------------|
| `todowrite` | Task list writing |
| `question` | Asking clarifying questions |
| `webfetch` | Fetching URLs |
| `websearch` | Web search queries |
| `codesearch` | Codebase semantic search |
| `doom_loop` | Loop detection override |

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

`"*"` as a key sets the default for unmatched commands.

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

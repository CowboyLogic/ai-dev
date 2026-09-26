# V1 Permissions Reference

> [!NOTE]
> This file covers the **V1** `permission` object. Native V2 uses an ordered `permissions` array with
> `{action, resource, effect}` rules and renamed actions (`bash` → `shell`, `task` → `subagent`). See
> [v2/permissions.md](v2/permissions.md).

## Structure

Permissions can be set globally (top-level) or per-agent. Agent permissions merge with the global config, and agent
rules take precedence. Since `v1.1.1` the legacy `tools` boolean map is deprecated and merged into `permission`
(still honored for backwards compatibility).

Shorthands:

```json
{ "permission": "allow" }
{ "permission": { "*": "ask", "bash": "allow", "edit": "deny" } }
```

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

The V1 schema accepts additional keys as pattern rules, which suggests custom and MCP tool names (e.g.
`"mymcp_*"`) can be keyed directly; the V1 docs don't show this, so verify before relying on it. Wildcards: `*` = zero or more characters, `?` = exactly one; everything else is literal.
`~` or `$HOME` at the start of a pattern expands to the home directory.

### Rule-based (support glob patterns per-command)

| Key | Gates | Description |
|-----|-------|-------------|
| `read` | `read` | File reading |
| `edit` | `write`, `edit`, `apply_patch` | File editing/writing |
| `glob` | `glob` | File pattern matching |
| `grep` | `grep` | File content searching |
| `list` | `list` | Directory listing |
| `bash` | `bash` | Shell command execution |
| `task` | `task` | Which subagents this agent can launch (matches the subagent name) |
| `lsp` | `lsp` | LSP queries (currently non-granular) |
| `skill` | `skill` | Loading a skill (matches the skill name) |
| `external_directory` | any path-taking tool | Paths outside the working directory; default `ask` |

### Simple action (single value only)

| Key | Gates | Description |
|-----|-------|-------------|
| `todowrite` | `todowrite`, `todoread` | Task list writing/reading |
| `question` | `question` | Asking clarifying questions |
| `webfetch` | `webfetch` | Fetching URLs |
| `websearch` | `websearch` | Web search queries |
| `doom_loop` | — | Same tool call repeated 3 times with identical input; default `ask` |

> [!NOTE]
> `codesearch` is not in the current V1 schema — don't rely on it.

---

## Defaults

Most permissions default to `"allow"`; `doom_loop` and `external_directory` default to `"ask"`; `read` denies
`.env` files by default:

```json
{ "permission": { "read": { "*": "allow", "*.env": "deny", "*.env.*": "deny", "*.env.example": "allow" } } }
```

## Approvals and auto mode

When prompted: `once` approves this request; `always` approves requests matching the tool's suggested patterns for
the **rest of the current session**; `reject` denies. Start with `opencode --auto` (or `opencode run --auto`) to
auto-approve anything not explicitly denied; the TUI command palette can toggle auto-approve too.

## External directories

```json
{
  "permission": {
    "external_directory": { "~/projects/personal/**": "allow" },
    "edit": { "~/projects/personal/**": "deny" }
  }
}
```

Allowed external directories inherit workspace defaults (so `read` is allowed unless overridden).

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

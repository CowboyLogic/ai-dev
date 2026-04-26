# Hooks Reference

## Structure in settings.json

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "MatcherValue",
        "hooks": [
          {
            "type": "command",
            "command": "path/to/script.sh",
            "timeout": 60
          }
        ]
      }
    ]
  },
  "disableAllHooks": false,
  "allowedHttpHookUrls": ["https://hooks.example.com/*"],
  "httpHookAllowedEnvVars": ["MY_TOKEN"]
}
```

Hooks can also be defined in **skill or agent YAML frontmatter** — they are scoped to the component's lifetime and cleaned up when it finishes:

```yaml
---
name: secure-operations
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

---

## Hook events (lifecycle order)

| Event | When it fires | Matcher values | Can block? |
| ------- | --------------- | ---------------- | ------------ |
| `SessionStart` | Session begins/resumes | `startup`, `resume`, `clear`, `compact` | No |
| `InstructionsLoaded` | CLAUDE.md/.claude/rules loaded | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` | No |
| `UserPromptSubmit` | Before Claude processes user input | none | Yes |
| `UserPromptExpansion` | Before a slash command expands into a prompt | command name | Yes |
| `PreToolUse` | Before tool execution | Tool name: `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `ExitPlanMode`, MCP tools | Yes |
| `PermissionRequest` | When permission dialog appears | Tool name | Yes |
| `PostToolUse` | After tool succeeds | Tool name | No (feedback only) |
| `PostToolUseFailure` | After tool fails | Tool name | No (feedback only) |
| `PostToolBatch` | After a batch of tool calls, before next model call | none | Yes (stop loop) |
| `PermissionDenied` | Auto mode denied a tool call | Tool name | No (can signal retry) |
| `Notification` | Notification sent | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` | No |
| `SubagentStart` | Subagent spawned | Agent type name | No |
| `SubagentStop` | Subagent finished | Agent type name | Yes |
| `TeammateIdle` | Agent-team teammate about to go idle | none | Yes |
| `TaskCreated` | Task created via TaskCreate | none | Yes |
| `TaskCompleted` | Task marked complete | none | Yes |
| `Stop` | Claude finishes responding | none | Yes |
| `StopFailure` | Turn ends due to API error | `rate_limit`, `authentication_failed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown` | No |
| `PreCompact` | Before context compaction | `manual`, `auto` | Yes |
| `PostCompact` | After compaction | `manual`, `auto` | No |
| `ConfigChange` | Config file changed during session | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` | Yes (except `policy_settings`) |
| `CwdChanged` | Working directory changed (e.g. after `cd`) | none | No |
| `FileChanged` | Watched file changed on disk | Literal filename(s): `.envrc\|.env` | No |
| `WorktreeCreate` | Worktree being created (hook must return the path) | none | Yes (any non-zero aborts) |
| `WorktreeRemove` | Worktree being removed | none | No |
| `SessionEnd` | Session terminates | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` | No |
| `Elicitation` | MCP server requests user input (form or URL dialog) | MCP server name | Yes |
| `ElicitationResult` | After user responds to an elicitation | MCP server name | Yes (can override response) |

---

## Matcher patterns

| Pattern | Behavior |
| --------- | ---------- |
| `"*"`, `""`, or omitted | Match all |
| Letters/digits/`_`/`\|` | Exact string or pipe-separated list: `Edit\|Write` |
| Contains other chars | JavaScript regex: `^Notebook`, `mcp__memory__.*` |

`UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, and `CwdChanged` do not support matchers and fire on every occurrence.

---

## Hook handler types

All handler types share a common `if` field that provides a second-level filter **without spawning the process unless it matches**:

```json
{
  "type": "command",
  "if": "Bash(rm *)",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm.sh"
}
```

The `if` field uses [permission rule syntax](/en/permissions) and is only evaluated on tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`). On other events a handler with `if` never runs.

### `command` (most common)

```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/script.sh",
  "if": "Bash(git *)",
  "async": false,
  "asyncRewake": false,
  "shell": "bash",
  "timeout": 600
}
```

- `async: true` — run in background, don't block
- `asyncRewake: true` — run in background, wake Claude on exit code 2
- `shell` — `"bash"` (default) or `"powershell"`

**Env vars available in scripts:**

- `$CLAUDE_PROJECT_DIR` — project root
- `${CLAUDE_PLUGIN_ROOT}` — plugin install dir
- `${CLAUDE_PLUGIN_DATA}` — plugin data dir

### `http`

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "headers": { "Authorization": "Bearer $MY_TOKEN" },
  "allowedEnvVars": ["MY_TOKEN"],
  "timeout": 30
}
```

### `mcp_tool` (call a tool on a connected MCP server)

```json
{
  "type": "mcp_tool",
  "server": "my_server",
  "tool": "security_scan",
  "input": { "file_path": "${tool_input.file_path}" },
  "timeout": 30
}
```

- `server` — name of an already-connected MCP server
- `tool` — name of the tool to call
- `input` — arguments; string values support `${path}` substitution from hook JSON input
- Non-blocking if the server is not connected or the tool returns an error

### `prompt` (uses a fast model to decide)

```json
{
  "type": "prompt",
  "prompt": "Should this be allowed?\n\n$ARGUMENTS",
  "model": "claude-haiku-4",
  "timeout": 30
}
```

Model must return `{ "ok": true }` to allow or `{ "ok": false, "reason": "..." }` to block.

### `agent` (spawns a subagent verifier — experimental)

```json
{
  "type": "agent",
  "prompt": "Verify all tests pass before stopping. $ARGUMENTS",
  "timeout": 120
}
```

Same response schema as `prompt`. Agent can use Read, Grep, Glob to inspect the codebase.

---

## Exit codes for command hooks

| Code | Meaning |
| ------ | --------- |
| `0` | Success — process JSON from stdout |
| `2` | Blocking error — block action, stderr becomes error message |
| `1`, `3+` | Non-blocking — continue, show stderr in transcript |

> **Warning**: Only exit code 2 blocks. Exit code 1 is non-blocking (unlike typical Unix convention). Exception: `WorktreeCreate` — any non-zero aborts creation.

---

## JSON output from hooks

Return JSON on stdout (exit 0) for structured control. Key fields:

| Field | Effect |
| ------- | -------- |
| `continue: false` | Stop Claude entirely. `stopReason` shown to user |
| `decision: "block"` | Block the action (used by `PostToolUse`, `Stop`, `UserPromptSubmit`, etc.) |
| `reason` | Message shown to user/Claude when blocking |

### PreToolUse decisions (use `hookSpecificOutput`)

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Safe command",
    "updatedInput": { "command": "npm run lint" },
    "additionalContext": "Running in production environment"
  }
}
```

`permissionDecision` values: `"allow"` | `"deny"` | `"ask"` | `"defer"`

### PermissionDenied retry

```json
{ "hookSpecificOutput": { "hookEventName": "PermissionDenied", "retry": true } }
```

### Elicitation (accept/decline without showing dialog)

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept",
    "content": { "username": "alice" }
  }
}
```

### WorktreeCreate (hook must print the worktree path to stdout)

```bash
# Command hook: print the created directory path on stdout
echo "$HOME/.claude/worktrees/$NAME"
```

---

## Common hook patterns

### Run linter after every file edit

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "cd \"$CLAUDE_PROJECT_DIR\" && npm run lint --silent 2>&1 || true" }]
      }
    ]
  }
}
```

### Desktop notification when Claude stops

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [{ "type": "command", "command": "osascript -e 'display notification \"Claude finished\" with title \"Claude Code\"'" }]
      }
    ]
  }
}
```

### Block dangerous bash commands (using `if` for efficiency)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "if": "Bash(rm *)",
          "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm.sh"
        }]
      }
    ]
  }
}
```

### MCP security scan after each write

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "mcp_tool",
          "server": "my_server",
          "tool": "security_scan",
          "input": { "file_path": "${tool_input.file_path}" }
        }]
      }
    ]
  }
}
```

### Block task completion until tests pass

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "command",
          "command": "cd \"$CLAUDE_PROJECT_DIR\" && npm test 2>&1 || (echo 'Tests must pass before completing' >&2; exit 2)"
        }]
      }
    ]
  }
}
```

### Reload direnv when .envrc changes

```json
{
  "hooks": {
    "FileChanged": [
      {
        "matcher": ".envrc|.env",
        "hooks": [{ "type": "command", "command": "direnv reload 2>/dev/null || true" }]
      }
    ]
  }
}
```

### Load .env on session start

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{ "type": "command", "command": "[ -f \"$CLAUDE_PROJECT_DIR/.env\" ] && cat \"$CLAUDE_PROJECT_DIR/.env\" >> \"$CLAUDE_ENV_FILE\" 2>/dev/null || true" }]
      }
    ]
  }
}
```

---

## Disable all hooks (emergency off switch)

```json
{ "disableAllHooks": true }
```

## View configured hooks

Type `/hooks` inside Claude Code to browse all configured hooks by source (User, Project, Local, Plugin, Session, Built-in).

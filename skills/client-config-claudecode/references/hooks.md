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

---

## Hook events (lifecycle order)

| Event | When it fires | Matcher values |
|-------|---------------|----------------|
| `SessionStart` | Session begins/resumes | `startup`, `resume`, `clear`, `compact` |
| `InstructionsLoaded` | CLAUDE.md/.claude/rules loaded | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` |
| `UserPromptSubmit` | Before Claude processes user input | none |
| `PreToolUse` | Before tool execution | Tool name: `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `WebFetch`, `WebSearch`, MCP tools |
| `PermissionRequest` | When permission dialog appears | Tool name |
| `PostToolUse` | After tool succeeds | Tool name |
| `PostToolUseFailure` | After tool fails | Tool name |
| `PermissionDenied` | Auto mode denied a tool call | Tool name |
| `Notification` | Notification sent | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog` |
| `SubagentStart` | Subagent spawned | Agent type name |
| `SubagentStop` | Subagent finished | Agent type name |
| `Stop` | Claude finishes responding | none |
| `StopFailure` | Turn ends due to API error | `rate_limit`, `authentication_failed`, `billing_error`, `invalid_request`, `server_error`, `max_output_tokens`, `unknown` |
| `PreCompact` | Before context compaction | `manual`, `auto` |
| `PostCompact` | After compaction | `manual`, `auto` |
| `ConfigChange` | Config file changed | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` |
| `FileChanged` | Watched file changed | Literal filename(s): `.envrc\|.env` |
| `SessionEnd` | Session terminates | `clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other` |
| `TaskCreated` | Task created via TaskCreate | none |
| `TaskCompleted` | Task marked complete | none |

---

## Matcher patterns

| Pattern | Behavior |
|---------|----------|
| `"*"`, `""`, or omitted | Match all |
| Letters/digits/`_`/`\|` | Exact string or pipe-separated list: `Edit\|Write` |
| Contains other chars | JavaScript regex: `^Notebook`, `mcp__memory__.*` |

---

## Hook handler types

### `command` (most common)
```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/script.sh",
  "async": false,
  "asyncRewake": false,
  "shell": "bash",
  "timeout": 600,
  "statusMessage": "Running check..."
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

### `prompt` (uses a fast model to decide)
```json
{
  "type": "prompt",
  "prompt": "Should this be allowed?\n\n$ARGUMENTS",
  "model": "claude-haiku-4",
  "timeout": 30
}
```

### `agent`
```json
{
  "type": "agent",
  "prompt": "Verify this config:\n\n$ARGUMENTS",
  "timeout": 60
}
```

---

## Exit codes for command hooks

| Code | Meaning |
|------|---------|
| `0` | Success — process JSON from stdout |
| `2` | Blocking error — block action, stderr becomes error message |
| `1`, `3+` | Non-blocking — continue, show stderr in transcript |

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

### Block dangerous bash commands
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "COMMAND=$(echo $CLAUDE_TOOL_INPUT | python3 -c \"import sys,json; print(json.load(sys.stdin)['command'])\"); if echo \"$COMMAND\" | grep -qE 'rm -rf|DROP TABLE|format'; then echo '{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"Blocked destructive command\"}}'; exit 0; fi"
        }]
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

---

## Disable all hooks (emergency off switch)
```json
{ "disableAllHooks": true }
```

## View configured hooks
Type `/hooks` inside Claude Code to browse all configured hooks by source.

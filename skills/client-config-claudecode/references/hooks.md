# Hooks Reference

Upstream: `https://code.claude.com/docs/en/hooks.md`.

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

**Hook locations**: `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, managed settings, plugin `hooks/hooks.json`, skill frontmatter (rest of the session once invoked), and subagent frontmatter (while that subagent runs). Hook entries **merge** across levels; an identical handler defined in several settings files runs once. All matching hooks run in parallel. Settings-file hooks also fire for tool calls inside subagents (input carries `agent_id`/`agent_type`).

Hooks can also be defined in **skill or agent YAML frontmatter**:

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
| `SessionStart` | Session begins/resumes | `startup`, `resume`, `clear`, `compact`, `fork` | No |
| `Setup` | Only with `--init-only`, or `--init`/`--maintenance` + `-p` (NOT normal startup) | `init`, `maintenance` | No |
| `InstructionsLoaded` | CLAUDE.md/.claude/rules loaded | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` | No |
| `UserPromptSubmit` | Before Claude processes user input | none | Yes |
| `UserPromptExpansion` | Before a slash command expands into a prompt | command name | Yes |
| `MessageDisplay` | While an assistant message streams to screen (display-only, transcript/Claude keep original text) | none | No |
| `PreToolUse` | Before tool execution | Tool name: `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `WebFetch`, `WebSearch`, `AskUserQuestion`, `ExitPlanMode`, MCP tools | Yes |
| `PermissionRequest` | When a tool call needs a permission decision | Tool name | Yes, via `decision.behavior` only (exit 2 is NOT honored) |
| `PostToolUse` | After tool succeeds | Tool name | No (feedback only) |
| `PostToolUseFailure` | After tool fails | Tool name | No (feedback only) |
| `PostToolBatch` | After a batch of tool calls, before next model call | none | Yes (stop loop) |
| `PermissionDenied` | Auto mode denied a tool call | Tool name | No (can signal retry) |
| `Notification` | Notification sent | `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`, `elicitation_url_dialog`, `elicitation_complete`, `elicitation_response`, `agent_needs_input`, `agent_completed`, `quota_auto_resume_fired`, `quota_auto_resume_stale`, `quota_auto_resume_disabled` | No |
| `SubagentStart` | Subagent spawned | Agent type name | No |
| `SubagentStop` | Subagent finished | Agent type name | Yes |
| `TeammateIdle` | Agent-team teammate about to go idle | none | Yes |
| `TaskCreated` | Task created via TaskCreate | none | Yes (rolls back creation) |
| `TaskCompleted` | Task marked complete | none | Yes |
| `Stop` | Claude finishes responding | none | Yes |
| `StopFailure` | Turn ends due to API error | `rate_limit`, `overloaded`, `authentication_failed`, `oauth_org_not_allowed`, `account_on_hold`, `billing_error`, `invalid_request`, `model_not_found`, `server_error`, `max_output_tokens`, `cloud_credential_error` (v2.1.267+), `unknown` | No |
| `PreCompact` | Before context compaction | `manual`, `auto` | Yes |
| `PostCompact` | After compaction | `manual`, `auto` | No |
| `PreModelSwitch` | Before a user/client-requested model switch (`/model`, picker, `/config`, fast mode, SDK `set_model`); not for automatic fallback (v2.1.251+) | Canonical target model name (`claude-opus-5`, `.*opus.*`) | Yes |
| `PostModelSwitch` | After the session's model changes, including automatic changes | Canonical target model name | No |
| `ConfigChange` | Config file changed during session | `user_settings`, `project_settings`, `local_settings`, `policy_settings`, `skills` | Yes (except `policy_settings`) |
| `CwdChanged` | Working directory changed (e.g. after `cd`) | none | No |
| `DirectoryAdded` | Working dir added mid-session via `/add-dir` or SDK `register_repo_root` (not `--add-dir` at startup); runs in background | `slash_command`, `register_repo_root` | No |
| `FileChanged` | Watched file changed on disk | Literal filename(s): `.envrc\|.env` | No |
| `WorktreeCreate` | Worktree being created (hook must return the path) | none | Yes (any non-zero aborts) |
| `WorktreeRemove` | Worktree being removed | none | Yes (non-zero fails removal if the dir still exists) |
| `SessionEnd` | Session terminates | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` (`bypass_permissions_disabled` removed in v2.1.234) | No |
| `Elicitation` | MCP server requests user input (form or URL dialog) | MCP server name | Yes |
| `ElicitationResult` | After user responds to an elicitation | MCP server name | Yes (can override response) |

---

## Matcher patterns

| Pattern | Behavior |
| --------- | ---------- |
| `"*"`, `""`, or omitted | Match all |
| Letters/digits/`_`/`-`/spaces/`,`/`\|` | Exact string or list, separated by `\|` or `,`: `Edit\|Write`, `Edit, Write` |
| Contains other chars | JavaScript regex (unanchored): `^Notebook`, `mcp__memory__.*` |

Hyphenated exact names (e.g. `code-reviewer`) require v2.1.195+ — earlier versions fall through to the regex path (a hyphenated name then also matches as a substring, e.g. `senior-code-reviewer`). `FileChanged` and `StopFailure` use a narrower exact-match set (letters/digits/`_`/`|` only, no hyphen/space/comma) — only `|` separates alternatives there.

`UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, `WorktreeRemove`, `MessageDisplay`, and `CwdChanged` do not support matchers and fire on every occurrence; a `matcher` on them is silently ignored.

**MCP tool matchers need `.*`**: `mcp__memory` is an exact string and matches no tool — write `mcp__memory__.*`. Plugin-bundled servers use `mcp__plugin_<plugin-name>_<server-name>__<tool>`. Regex matchers are unanchored (`Edit.*` also matches `NotebookEdit`; use `^Edit$`).

---

## Hook handler types

**Common fields** (all handler types): `type` (required), `if`, `timeout` (seconds; defaults 600 for `command`/`http`/`mcp_tool`, 30 for `prompt`, 60 for `agent`; lowered to 30 on `UserPromptSubmit`/`PreModelSwitch`/`PostModelSwitch` and 10 on `MessageDisplay`; `SessionEnd` hooks share a 1.5 s budget), `statusMessage` (custom spinner text), `once` (remove after first successful run — honored only in skill frontmatter).

The `if` field provides a second-level filter **without spawning the process unless it matches**:

```json
{
  "type": "command",
  "if": "Bash(rm *)",
  "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-rm.sh"
}
```

The `if` field holds exactly one permission rule (no `&&`/`||`/lists) and is only evaluated on tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`). On other events a handler with `if` never runs.

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
- `shell` — `"bash"` (default; `"powershell"` on Windows without Git Bash) or `"powershell"`; ignored when `args` is set
- `args` — **exec form**: when present, `command` is spawned directly as an executable with `args` as argv (no shell, no quoting issues). Omit `args` for shell form (pipes, `&&`, globs)

```json
{ "type": "command", "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"] }
```

**Env vars available in scripts:**

- `$CLAUDE_PROJECT_DIR` — project root
- `${CLAUDE_PLUGIN_ROOT}` — plugin install dir
- `${CLAUDE_PLUGIN_DATA}` — plugin data dir
- `$CLAUDE_ENV_FILE` — only for `SessionStart`, `Setup`, `CwdChanged`, `FileChanged`; append `export` lines to persist env vars into later Bash commands
- `$CLAUDE_CODE_REMOTE` — `"true"` in remote web environments

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

- `server` — name of an already-connected MCP server (plugin servers: `plugin:<plugin-name>:<server-name>`); never triggers OAuth/connection. Skipped on `Setup` and on the launch-time `SessionStart`
- `tool` — name of the tool to call
- `input` — arguments; string values support `${path}` substitution from hook JSON input
- Non-blocking if the server is not connected or the tool returns an error

### `prompt` (uses a fast model to decide)

```json
{
  "type": "prompt",
  "prompt": "Should this be allowed?\n\n$ARGUMENTS",
  "timeout": 30
}
```

Optional `model` (defaults to a fast model). `$ARGUMENTS` is replaced by the hook input JSON; escape a literal `$` as `\$`. Model must return `{ "ok": true }` to allow or `{ "ok": false, "reason": "..." }` to block, optionally with `"impossible": true` (on `Stop`/`SubagentStop` this lets the turn end instead of feeding the reason back). On `PreToolUse`, `ok: false` denies and ends the turn unless the handler sets `continueOnBlock: true`.

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
| `2` | Blocking error — block action, stderr becomes error message (not honored for `PermissionRequest`) |
| `1`, `3+` | Non-blocking — continue, show stderr in transcript |

> [!WARNING]
> Only exit code 2 blocks. Exit code 1 is non-blocking (unlike typical Unix convention). Exceptions: `WorktreeCreate` — any non-zero aborts creation; `WorktreeRemove` — any non-zero fails removal if the directory still exists.

Stdout is parsed as JSON on every exit code when it starts with `{` and ends with `}`. For most events plain stdout only goes to the debug log; for `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and `PostModelSwitch` plain stdout is added as context for Claude.

---

## JSON output from hooks

Return JSON on stdout (exit 0) for structured control. Key fields:

| Field | Effect |
| ------- | -------- |
| `continue: false` | Stop Claude entirely (any event). `stopReason` shown to the user and stays in the conversation. Takes precedence over event-specific decisions |
| `decision: "block"` | Block the action (used by `PostToolUse`, `Stop`, `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUseFailure`, `PostToolBatch`, `SubagentStop`, `ConfigChange`, `PreCompact`, `TaskCreated`, `PreModelSwitch`). `TeammateIdle`/`TaskCompleted` block via exit 2 or `continue: false` |
| `reason` | Message shown to user/Claude when blocking |
| `suppressOutput` | Accepted but has **no effect** — successful hook stdout is never shown in the transcript anyway |
| `systemMessage` | Warning string shown to the user |
| `terminalSequence` | Terminal escape sequence Claude Code emits on your behalf (desktop notif, title, bell). Only OSC `0`/`1`/`2`/`9`/`99`/`777` and bare BEL allowed — anything else is silently ignored. Use instead of writing to `/dev/tty` (unavailable to hooks) |

All hook output strings (`additionalContext`, `systemMessage`, `initialUserMessage`, plain stdout) are capped at 10,000 chars; overflow is saved to a file and Claude gets the path plus a 2,000-char preview.

**Other event-specific outputs** (`hookSpecificOutput`): `PostToolUse` → `updatedToolOutput` (replaces what Claude sees; the tool already ran); `SessionStart` → `additionalContext`, `initialUserMessage`, `watchPaths`, `sessionTitle`, `reloadSkills`; `SubagentStart`/`PostModelSwitch` → `additionalContext`; `MessageDisplay` → `displayContent` (display-only); `PreModelSwitch` → `permissionDecision` (`allow`/`deny`/`ask`); `PermissionRequest` `allow` → optional `updatedPermissions`.

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

`permissionDecision` values: `"allow"` | `"deny"` | `"ask"` | `"defer"`. Multiple hooks disagreeing resolves as `deny` > `defer` > `ask` > `allow`. Deny/ask permission *rules* still apply regardless of what a hook returns (deny always wins). `"allow"` never skips the prompt for connector tools your org set to `ask`, or MCP tools marked `requiresUserInteraction`.

`"defer"` — only honored in non-interactive mode (`-p`); ignored with a warning in interactive sessions or when Claude makes several tool calls in one turn. Exits with `stop_reason: "tool_deferred"` and the pending call in `deferred_tool_use` (id/name/input); an external process resumes with `claude -p --resume <session-id>` and the same tool call fires `PreToolUse` again so the hook can return `"allow"` with the answer in `updatedInput`. Typical use: `AskUserQuestion` answered by a host UI with no terminal.

**Legacy note**: top-level `decision`/`reason` (`"approve"`/`"block"`) are deprecated for `PreToolUse` specifically — use `hookSpecificOutput.permissionDecision`. Other events (`PostToolUse`, `Stop`, etc.) still use top-level `decision`/`reason`.

### PermissionRequest (use `hookSpecificOutput.decision`)

```json
{ "hookSpecificOutput": { "hookEventName": "PermissionRequest", "decision": { "behavior": "allow", "updatedInput": { "command": "npm run lint" } } } }
```

`decision.behavior`: `"allow"` | `"deny"`. No prompt reaches the user; runs even for background subagents in headless mode (denies by default if no hook decides). For `allow`, `updatedPermissions` can also add rules or change the session mode. Not run for a sandboxed command's network request.

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

Also turns off a custom `statusLine`, `subagentStatusLine`, and `fileSuggestion`. The value after settings precedence applies, so a project `"disableAllHooks": false` overrides a user-level `true` — pass `--settings '{"disableAllHooks": true}'` to force it for one run. Outside managed settings it can't disable managed hooks.

## View configured hooks

Type `/hooks` inside Claude Code for a read-only browser of all configured hooks, labeled by type and source (`User Settings`, `Project Settings`, `Local Settings`, `Plugin Hooks`, `Session Hooks`). Direct edits to settings files are normally picked up by the file watcher.

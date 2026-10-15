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

A `UserPromptSubmit` hook in a skill's own frontmatter first runs on the prompt *after* the one that invokes the skill (changelog only, v2.1.299).

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
| `PreCompact` | Before context compaction | `manual` (`/compact`), `auto` (reaching the auto-compact window, and idle compaction) | Yes |
| `PostCompact` | After compaction | `manual` (`/compact`), `auto` (reaching the auto-compact window, and idle compaction) | No |
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

`Notification` `permission_prompt` fires once you haven't typed for about six seconds. In sessions that send permission requests to the Agent SDK's `canUseTool` callback (Claude Desktop and the VS Code extension host Claude Code this way) it fires about six seconds after the request whether or not you type, does not fire if a `PermissionRequest` hook or you answer sooner, and `CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS=1` turns it off there. Before v2.1.233 it did not fire in those sessions.

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

**Common fields** (all handler types): `type` (required), `if`, `timeout` (seconds; defaults 600 for `command`/`http`/`mcp_tool`, 30 for `prompt`, 60 for `agent`; lowered to 30 on `UserPromptSubmit`/`PreModelSwitch`/`PostModelSwitch` and 10 on `MessageDisplay`; `SessionEnd` hooks share a 1.5 s budget, see [SessionEnd time budget](#sessionend-time-budget)), `statusMessage` (custom spinner text), `once` (remove after first successful run — honored only in skill frontmatter).

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
  "onFailure": "continue",
  "timeout": 600
}
```

- `async: true` — run in background, don't block
- `asyncRewake: true` — run in background, wake Claude on exit code 2
- `shell` — `"bash"` (default; `"powershell"` on Windows without Git Bash) or `"powershell"`; ignored when `args` is set
- `args` — **exec form**: when present, `command` is spawned directly as an executable with `args` as argv (no shell, no quoting issues). Omit `args` for shell form (pipes, `&&`, globs)
- `onFailure` — `"continue"` (default) or `"block"`; see [Block the action when a hook fails](#block-the-action-when-a-hook-fails) (v2.1.295+; `command` and `http` only)

```json
{ "type": "command", "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"] }
```

**Env vars available in scripts:**

- `$CLAUDE_PROJECT_DIR` — project root
- `${CLAUDE_PLUGIN_ROOT}` — plugin install dir
- `${CLAUDE_PLUGIN_DATA}` — plugin data dir
- `$CLAUDE_ENV_FILE` — only for `SessionStart`, `Setup`, `CwdChanged`, `FileChanged`; append `export` lines to persist env vars into later Bash commands. PowerShell commands receive the variables too from v2.1.296, but PowerShell never runs the file: Claude Code copies the assignments across only when every line is a blank line, a `#` comment, or a plain `export NAME=value` / `declare -x NAME=value` / `NAME=value` with a simple quoted-or-unquoted value
- `$CLAUDE_CODE_REMOTE` — `"true"` in remote web environments
- `$CLAUDE_EFFORT` — the effort level in effect (same value as the `effort.level` input field)

A hook process inherits Claude Code's environment, minus the `OTEL_*` exporter variables, and minus the credentials `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` strips when it is set.

### `http`

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "headers": { "Authorization": "Bearer $MY_TOKEN" },
  "allowedEnvVars": ["MY_TOKEN"],
  "onFailure": "block",
  "timeout": 30
}
```

`onFailure` is optional (`"continue"` by default); an HTTP failure is a connection error, a non-2xx status, or a 2xx body that is neither empty nor a JSON object.

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

## Hook input (stdin JSON)

Command hooks receive one JSON object on stdin; `http` hooks receive the same object as the POST body. Every event gets these common fields, plus the event-specific fields documented per event upstream (`tool_name`, `tool_input`, `tool_use_id` on tool events, `reason` on `SessionEnd`, `last_assistant_message` on `Stop`, and so on):

| Field | Meaning |
| ----- | ------- |
| `session_id` | Current session identifier |
| `prompt_id` | UUID of the user prompt being processed; matches the `prompt.id` attribute on OpenTelemetry events. Absent until the first user input |
| `transcript_path` | Path to the conversation JSON. Written asynchronously, so it can lag the current turn; on `Stop`/`SubagentStop` read `last_assistant_message` instead |
| `cwd` | Working directory when the hook is invoked |
| `scratchpad_dir` | The session's scratchpad directory (v2.1.257+); absent when the session has none |
| `permission_mode` | `default`, `plan`, `acceptEdits`, `auto`, `dontAsk`, or `bypassPermissions`. Manual mode arrives as `default`, never `manual`. Not every event receives it |
| `effort` | Object with `level` (`low`/`medium`/`high`/`xhigh`/`max`); present on events within a tool-use context when the model supports effort |
| `hook_event_name` | Name of the event that fired |
| `agent_id`, `agent_type` | Which subagent, teammate, or `--agent` session the hook fired in. `agent_id` appears for subagents and in-process teammates; `agent_type` is also set for `--agent` sessions |

Only `SessionStart` hooks can receive a `model` field, and not always. `PreModelSwitch`/`PostModelSwitch` receive `from_model` and `to_model`. There is no `$CLAUDE_MODEL` environment variable.

Command hooks on macOS and Linux run in their own session with no controlling terminal, so they can't open `/dev/tty`; return `systemMessage` or `terminalSequence` JSON instead.

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

### Block the action when a hook fails

Requires v2.1.295+. By default a hook that can't start, times out, or exits with a code other than 0 or 2 is a **non-blocking** error — the action goes ahead, so a policy hook with a mistyped path lets everything through. Set `"onFailure": "block"` on a `command` or `http` hook to make a failure do what exit code 2 does on that event (on `PermissionRequest` it denies the request).

```json
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PROJECT_DIR}/.claude/hooks/check-command.js"],
  "onFailure": "block"
}
```

A failure is: the hook can't start; exit code other than 0 or 2 (even if it printed JSON that allows the action — exit 0 to return a JSON decision); an HTTP connection failure or non-2xx status; a timeout; or JSON output that can't be parsed or fails schema validation. Plain-text stdout from a command hook is not a failure.

`onFailure` has no effect on `Stop`, `SubagentStop`, `TaskCompleted`, and `TeammateIdle` hooks (exit 2 there sends Claude back to work, and Claude can't repair a hook that won't run) or on background command hooks (`async`/`asyncRewake`). A timed-out `command`, `http`, or `mcp_tool` hook on `PreToolUse` does **not** block the call. Set `onFailure: "block"` on a `command` or `http` hook to make a timeout block; `mcp_tool` hooks don't accept `onFailure`, so a timed-out one always lets the call continue.

**Changelog only (v2.1.299), three fail-closed changes:**

- On Windows, a `PreToolUse` or `PermissionRequest` hook that sets no `shell` used to fail open when Git for Windows isn't installed; a guard that fails now blocks the call.
- Plan mode no longer runs a write (an MCP tool's, a file's, a shell command's) that a `PreToolUse` hook allowed.
- `UserPromptSubmit` hooks now run before a skill or custom slash command expands, so a hook that blocks the prompt also stops the command's embedded shell commands.

### Stop hooks that keep blocking

`Stop` and `SubagentStop` hooks receive `stop_hook_active: true` when Claude is already continuing because of a stop hook; check it, or the hook can block on a condition that never resolves. Claude Code also caps this loop: after stop hooks continue the turn 8 times in a row it overrides the next block and ends the turn. The count resets each time Claude calls a tool. `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` changes the cap (default 8; `0` disables it).

### SessionEnd time budget

`SessionEnd` hooks get a 1.5 s default timeout on exit, `/clear`, and interactive `/resume`. Two ways to raise it: set `timeout` on the hook (the overall budget rises to the highest per-hook `timeout` in your settings files, up to 60 s; plugin-provided hooks don't raise it, and a hook without its own `timeout` keeps the default), or set `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`, which also becomes the timeout of each hook with no `timeout` of its own. Before v2.1.268 the variable raised only the overall budget.

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

All hook output strings (`additionalContext`, `systemMessage`, `initialUserMessage`, plain stdout) are capped at 10,000 chars; overflow is saved to a file and Claude gets the path plus a 2,000-char preview. A literal `<system-reminder>` or `</system-reminder>` tag in `additionalContext` has its `<` replaced with `&lt;`.

An **async** hook's JSON response must be alone on stdout or on one line of its own; multi-line (pretty-printed) JSON alone on stdout needs v2.1.295+ (earlier versions ignore it). Fields with the wrong type are dropped, and `--debug` names each one.

**Other event-specific outputs** (`hookSpecificOutput`): `PostToolUse` → `updatedToolOutput` (replaces what Claude sees; the tool already ran; `updatedMCPToolOutput` does the same for MCP tools only — prefer `updatedToolOutput`); `SessionStart` → `additionalContext`, `initialUserMessage`, `watchPaths`, `sessionTitle`, `reloadSkills`; `SubagentStart`/`PostModelSwitch` → `additionalContext`; `MessageDisplay` → `displayContent` (display-only); `PreModelSwitch` → `permissionDecision` (`allow`/`deny`/`ask`); `PermissionRequest` `allow` → optional `updatedPermissions`.

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

### Elicitation (answer without showing the dialog)

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Elicitation",
    "action": "accept",
    "content": { "username": "alice" }
  }
}
```

`action` is `"accept"` (with form values in `content`, keyed by the request's `requested_schema` property names), `"decline"`, or `"cancel"`; the server receives it and no dialog appears. No output and exit 0 leaves the request to the user. Exit code 2, or a top-level `"decision": "block"`, also declines (the block overrides an `action` in the same output; `decision: "block"` was ignored from v2.1.105 until the fix in v2.1.284). `reason`, `systemMessage`, and `continue` are discarded. When several hooks match, a decline overrides an accept or cancel.

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

## Debug a slow hook

Run with `--debug` (or `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` for matcher counts) and search the log for `Hooks:` lines. From v2.1.296 each command hook on a tool event, `UserPromptSubmit`, `SessionStart`, `Stop`, and several other events logs one when it finishes, e.g. `Hooks: PostToolUse:Write [.claude/hooks/log-write.sh] finished with status 0 (31ms)`. A run can also end as `timed out after <N>ms`, `cancelled`, `moved to the background`, or `failed to start`. On some events (`Notification`, `SessionEnd`, `PreCompact`) the line is `completed with status` without a duration.

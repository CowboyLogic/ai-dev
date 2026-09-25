# Hooks Reference

Hooks run external commands (or HTTP calls, or auto-submitted prompts) at lifecycle points in a
session. Copilot CLI and Copilot cloud agent share the format; differences are noted.

## Where hooks are loaded from (CLI)

All sources are combined; when the same event appears in several, every entry runs. Load order:

| Source | Location |
|--------|----------|
| Policy (admin, machine-wide) | `/etc/github-copilot/policy.d/*.json` (Linux/macOS), `C:\ProgramData\GitHub\Copilot\policy.d\*.json` or registry `HKLM\Software\Policies\GitHub\Copilot` (Windows) |
| Repository hook files | `.github/hooks/*.json` — any number of files, name each after its purpose |
| User hook files | `~/.copilot/hooks/*.json` (`$COPILOT_HOME/hooks/` if set; Windows `%USERPROFILE%\.copilot\hooks\`) |
| Repository inline | `hooks` key in `.github/copilot/settings.json` or `.github/copilot/settings.local.json` (also `.claude/settings.json` / `.claude/settings.local.json`) |
| User inline | `hooks` key in `~/.copilot/settings.json` |
| Plugins | Each plugin's `hooks.json` or `hooks/hooks.json` |

- Hook config changes load when the CLI starts — restart after editing.
- Policy hooks must be root-owned and not group/world-writable (POSIX); they ignore
  `disableAllHooks` and folder trust.
- Repository hooks in prompt mode (`-p`) load only if the folder is trusted, `COPILOT_ALLOW_ALL` is
  set, or `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`.
- Cloud agent reads only `.github/hooks/*.json` from the cloned repo (must be on the default
  branch), runs on Linux, honors only `bash` (or `command`) entries, and has a firewall-restricted
  network.
- Windows: the docs' example hooks need PowerShell 7+ (`pwsh`) — `winget install Microsoft.PowerShell`.

## File structure

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "bash": "./scripts/validate-tool.sh",
        "powershell": "./scripts/validate-tool.ps1",
        "cwd": ".",
        "timeoutSec": 30,
        "env": { "LOG_LEVEL": "INFO" },
        "matcher": "bash|edit"
      }
    ]
  }
}
```

- `"version": 1` is required.
- A malformed item in a hook **file** is dropped and logged; siblings still load. Invalid JSON, a
  bad `version`, or a non-array event list rejects the whole file. Inline `hooks` in
  `settings.json` are strict — any item error rejects the whole field.
- Optional top-level `"disableAllHooks": true` skips every hook in that file.

---

## Hook entry types

### `command`

| Field | Required | Description |
|-------|----------|-------------|
| `type` | No | `"command"` (default when omitted) |
| `bash` | One of `bash`/`powershell`/`command` (unless `exec`) | Unix shell command |
| `powershell` | One of `bash`/`powershell`/`command` (unless `exec`) | Windows shell command |
| `command` | One of `bash`/`powershell`/`command` (unless `exec`) | Cross-platform fallback, copied to whichever of `bash`/`powershell` is absent |
| `exec` | Instead of the shell fields | Executable run directly, no shell (CLI only) |
| `args` | No | Arguments for `exec` (CLI only) |
| `cwd` | No | Working directory (relative to repo root, or absolute) |
| `env` | No | Extra environment variables (supports variable expansion) |
| `timeoutSec` | No | Seconds; default `30` |
| `timeout` | No | Alias for `timeoutSec` (used only if `timeoutSec` is absent) |
| `matcher` | No | Regex filter (see [Matchers](#matchers)) |

Don't combine `exec` with `bash`/`powershell`/`command`.

**Input** arrives as JSON on **stdin**. **Output** is JSON on stdout — exactly one final object.
Progress lines are allowed before it: a single-line `{"type": "progress", "message": "...",
"temporary": true}` is shown in the timeline and stripped from the output. Output over 10 MiB is
truncated; unparseable output is treated as no output.

### `http`

Posts the input payload as JSON.

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"http"` |
| `url` | Yes | `https://` required for `preToolUse` and `permissionRequest`. Plain `http://` only for localhost with `COPILOT_HOOK_ALLOW_LOCALHOST=1` |
| `headers` | No | Request headers |
| `allowedEnvVars` | No | Env var names that may be expanded inside `headers` (forces `https://`) |
| `timeoutSec` / `timeout` | No | Seconds; default `30` |

```json
{
  "type": "http",
  "url": "https://hooks.example.com/copilot",
  "headers": { "X-Source": "copilot-cli" },
  "timeoutSec": 10
}
```

The docs don't show the placeholder syntax for expanding `allowedEnvVars` inside `headers`;
verify before relying on it.

### `prompt` (CLI, `sessionStart` only)

Auto-submits text or a slash command at the start of a **new interactive** session (not on resume,
not in `-p`).

```json
{ "type": "prompt", "prompt": "/chronicle standup" }
```

---

## Hook events

| Event | Fires when | Output used |
|-------|------------|-------------|
| `sessionStart` | New or resumed session begins | Optional `additionalContext` |
| `sessionEnd` | Session ends (also `/clear`, with `reason: "user_exit"`) | No |
| `userPromptSubmitted` | User submits a prompt | `modifiedPrompt` — SDK hooks only; config-file hook output is dropped |
| `userPromptTransformed` | Prompt transformed into model-facing content | `modifiedTransformedPrompt` |
| `preToolUse` | Before each tool runs | Allow / deny / ask / modify args |
| `permissionRequest` | Before the permission service runs (CLI only) | `behavior` allow/deny |
| `postToolUse` | After a tool succeeds | `modifiedResult`, `additionalContext` |
| `postToolUseFailure` | After a tool fails | `additionalContext` (exit `2`) |
| `agentStop` | Main agent finishes a turn | `decision: "block"` forces another turn |
| `subagentStart` | Subagent spawned | `additionalContext` prepended to its prompt |
| `subagentStop` | Subagent completes | `decision`, `reason`, `modifiedResponse` |
| `preCompact` | Context compaction begins | No |
| `errorOccurred` | An error occurs | No |
| `notification` | CLI system notification (async, CLI only) | Optional `additionalContext` |

Event-name casing selects the payload format: camelCase (`preToolUse`) gets camelCase fields;
PascalCase VS Code-compatible names (`SessionStart`, `SessionEnd`, `UserPromptSubmit`,
`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SubagentStop`, `ErrorOccurred`,
`PreCompact`, `PermissionRequest`) get snake_case fields (`tool_name`, `tool_input`,
`hook_event_name`, ...).

The built-in `general-purpose` agent does not emit `subagentStart`/`subagentStop`.

### Input payloads (camelCase)

Every payload includes `sessionId`, `timestamp` (epoch ms), and `cwd`. Additional fields:

| Event | Extra fields |
|-------|--------------|
| `sessionStart` | `source` (`"startup"`, `"resume"`, `"new"`), `initialPrompt?` |
| `sessionEnd` | `reason` (`"complete"`, `"error"`, `"abort"`, `"timeout"`, `"user_exit"`) |
| `userPromptSubmitted` | `prompt` |
| `userPromptTransformed` | `prompt`, `transformedPrompt` |
| `preToolUse` | `toolName`, `toolArgs` |
| `postToolUse` | `toolName`, `toolArgs`, `toolResult { resultType, textResultForLlm }` |
| `postToolUseFailure` | `toolName`, `toolArgs`, `error` |
| `agentStop` | `transcriptPath`, `stopReason`, `stop_hook_active` |
| `subagentStart` | `transcriptPath`, `agentName`, `agentDisplayName?`, `agentDescription?` |
| `subagentStop` | `transcriptPath`, `agentId`, `agentType`, `agentName`, `agentDisplayName?`, `response`, `stopReason` |
| `errorOccurred` | `error { message, name, stack? }`, `errorContext`, `recoverable` |
| `preCompact` | `transcriptPath`, `trigger` (`"manual"`/`"auto"`), `customInstructions` |
| `notification` | `hook_event_name`, `message`, `title?`, `notification_type` |

`notification_type` values: `shell_completed`, `shell_detached_completed`, `agent_completed`,
`agent_idle`, `permission_prompt`, `elicitation_dialog`.

---

## Decision output

### `preToolUse`

| Field | Values |
|-------|--------|
| `permissionDecision` | `"allow"`, `"deny"`, `"ask"` (cloud agent treats `"ask"` as deny) |
| `permissionDecisionReason` | Required when denying; shown to the agent |
| `modifiedArgs` | Replacement tool arguments |

If any `preToolUse` hook denies, the tool is blocked.

### `permissionRequest`

| Field | Values |
|-------|--------|
| `behavior` | `"allow"`, `"deny"` — short-circuits the normal permission flow |
| `message` | Reason fed back when denying |
| `interrupt` | `true` with deny stops the agent |

Doesn't run for `read` and `hook` permission kinds. A hook `allow` never pre-approves a
sandbox-bypass request (only `deny` propagates). Useful for `-p`/CI where no prompt is possible.

### `postToolUse`

`modifiedResult` (`{ resultType: "success", textResultForLlm }`) replaces the result;
`additionalContext` is appended to the tool output (joined across hooks, capped at 10 KB).

### `agentStop` / `subagentStop`

`decision: "block"` plus `reason` forces another turn using `reason` as the prompt.
`subagentStop` also accepts `modifiedResponse`. After 8 consecutive blocks the CLI ends the turn
anyway — check `stop_hook_active` to self-limit.

---

## Matchers

`matcher` is a regex anchored as `^(?:PATTERN)$` — it must match the full value. Invalid regexes
skip the entry.

| Event | Matched against |
|-------|-----------------|
| `preToolUse`, `postToolUse`, `permissionRequest` | `toolName` |
| `subagentStart` | `agentName` |
| `preCompact` | `trigger` |
| `notification` | `notification_type` |

Tool names: `ask_user`, `bash`, `create`, `edit`, `glob`, `grep`, `powershell`, `task`, `view`,
`web_fetch`.

PascalCase `PreToolUse` / `PermissionRequest` use Claude-style matchers: `*`, `**`, or empty
matches everything; `Bash` or `Edit|Write` match Claude tool names (`bash`/`powershell` → `Bash`,
`view` → `Read`, `create` → `Write`, `edit`/`apply_patch` → `Edit`, `grep` → `Grep`, `glob` →
`Glob`, `web_fetch` → `WebFetch`, `task` → `Agent`).

---

## Exit codes and failure behavior

| Exit | Meaning |
|------|---------|
| `0` | Success; stdout parsed as output |
| `2` | Warning (stderr shown). **Deny** for `preToolUse` and `permissionRequest`. For `postToolUseFailure`, stdout becomes `additionalContext` |
| Other non-zero | Logged, run continues — **except** `preToolUse` command hooks, which deny |
| Timeout | Always fail-open, even for `preToolUse` and policy hooks |

HTTP `preToolUse` hooks are fail-open on network errors, timeouts, and non-2xx responses.

---

## Disabling hooks

- `"disableAllHooks": true` inside a hook file skips that file's hooks.
- `disableAllHooks: true` in repository or user `settings.json` skips every hook from every source
  for those sessions (CLI only); policy hooks still run.

---

## Examples

### Block destructive shell commands (`.github/hooks/guard.json`)

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "matcher": "bash",
        "bash": "./.github/hooks/block-dangerous.sh",
        "timeoutSec": 10
      }
    ]
  }
}
```

```bash
#!/bin/bash
# block-dangerous.sh — input JSON arrives on stdin
INPUT=$(cat)
if echo "$INPUT" | grep -qE 'rm -rf|DROP TABLE'; then
  echo '{"permissionDecision": "deny", "permissionDecisionReason": "Destructive command blocked by hook"}'
fi
exit 0
```

### Notify when the agent stops (macOS, `~/.copilot/hooks/notify.json`)

```json
{
  "version": 1,
  "hooks": {
    "agentStop": [
      {
        "type": "command",
        "bash": "osascript -e 'display notification \"Agent stopped\" with title \"Copilot CLI\"'",
        "timeoutSec": 5
      }
    ]
  }
}
```

---

## Testing and debugging

```bash
# Pipe sample input into the script
echo '{"timestamp":1704614400000,"cwd":"/tmp","toolName":"bash","toolArgs":"{\"command\":\"ls\"}"}' \
  | ./.github/hooks/block-dangerous.sh

echo $?                                   # exit code
./.github/hooks/block-dangerous.sh < sample.json | jq .   # validate output JSON
```

Checklist when hooks don't run: file in the right directory, valid JSON (`jq . file.json`),
`"version": 1` present, script executable (`chmod +x`) with a shebang, output is one JSON object,
CLI restarted. Add `set -x` and write debug output to stderr.

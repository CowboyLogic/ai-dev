# Hooks Reference

Hooks are configured in `settings.json` under a `hooks` key. Precedence (highest to lowest):
project `.gemini/settings.json` → user `~/.gemini/settings.json` → system settings → extensions.

## Global enable/disable

Control the entire hooks system with `hooksConfig`:

```json
{
  "hooksConfig": {
    "enabled": true,
    "disabled": ["hook-name-to-skip"],
    "notifications": true
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `hooksConfig.enabled` | `true` | Master toggle — `false` disables all hooks |
| `hooksConfig.disabled` | `[]` | Hook names (commands) that never execute, even if configured |
| `hooksConfig.notifications` | `true` | Show visual indicators when hooks are executing |

## Configuration schema

Each event is an array of **matcher groups**. Each group has an optional `matcher`/`sequential` and a required `hooks` array of command definitions — the `hooks` array is nested inside the group, not the top-level event array:

```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "write_file|replace",
        "sequential": false,
        "hooks": [
          {
            "name": "security-check",
            "type": "command",
            "command": "$GEMINI_PROJECT_DIR/.gemini/hooks/security.sh",
            "timeout": 5000,
            "description": "Blocks risky file writes"
          }
        ]
      }
    ]
  }
}
```

**Matcher-group fields:**

| Field | Type | Required | Description |
|-------|------|----------|--------------|
| `matcher` | string | No | Regex (tool events) or exact string (lifecycle events) filtering when the group runs. `"*"` or `""` matches everything |
| `sequential` | boolean | No | `true` runs the group's hooks one after another; `false` (default) runs them in parallel |
| `hooks` | array | Yes | Array of hook command definitions (below) |

**Hook command fields:**

| Field | Type | Required | Description |
|-------|------|----------|--------------|
| `type` | string | Yes | Execution engine — currently only `"command"` |
| `command` | string | Yes* | Shell command to execute (required when `type` is `"command"`) |
| `name` | string | No | Friendly name shown in logs and `/hooks` commands |
| `description` | string | No | Human-readable purpose |
| `timeout` | number | No | Timeout in milliseconds (default: 60000) |

## Event types

| Event | When it fires | Impact | Common use |
|-------|---------------|--------|------------|
| `SessionStart` | Session begins (startup/resume/clear) | Inject context (advisory only) | Load initial context |
| `SessionEnd` | Session ends (exit/clear/logout/prompt_input_exit/other) | Best-effort, non-blocking | Cleanup, save state |
| `BeforeAgent` | After prompt submit, before planning | Can block/discard the turn | Validate prompts, inject context |
| `AfterAgent` | After agent's final response for the turn | Can force retry or halt | Review output, auto-retry |
| `BeforeModel` | Before sending request to LLM | Can block turn or mock response | Modify prompts, swap models |
| `BeforeToolSelection` | Before LLM picks tools | Can filter available tools | Restrict/force tool modes |
| `AfterModel` | After each LLM response chunk | Can block turn or redact | Real-time redaction/PII filtering |
| `BeforeTool` | Before a tool executes | Can block or rewrite args | Validate arguments, block dangerous ops |
| `AfterTool` | After a tool executes | Can hide/replace result, inject context | Audit results, route to another tool |
| `PreCompress` | Before history compression | Advisory only | Save state, notify user |
| `Notification` | On a system notification (e.g. ToolPermission) | Observability only | Forward to external logging |

### Matchers by event type

- Tool events (`BeforeTool`, `AfterTool`): `matcher` is a **regex** against the tool name. Built-in tool names (`read_file`, `run_shell_command`, …) or MCP tools (`mcp_<server>_<tool>`).
- Lifecycle events: `matcher` is an **exact string** (e.g. `"startup"` for `SessionStart`'s `source`).

## Input to hooks (via stdin)

All hooks receive these common fields, plus event-specific fields:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript",
  "cwd": "/current/working/dir",
  "hook_event_name": "BeforeTool",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

| Event | Extra input fields |
|-------|--------------------|
| `BeforeTool` | `tool_name`, `tool_input`, `mcp_context`, `original_request_name` |
| `AfterTool` | `tool_name`, `tool_input`, `tool_response` (`llmContent`/`returnDisplay`/`error`), `mcp_context`, `original_request_name` |
| `BeforeAgent` | `prompt` |
| `AfterAgent` | `prompt`, `prompt_response`, `stop_hook_active` |
| `BeforeModel` / `BeforeToolSelection` / `AfterModel` | `llm_request` (`model`/`messages`/`config`/`toolConfig`); `AfterModel` also gets `llm_response` |
| `SessionStart` | `source`: `"startup"` \| `"resume"` \| `"clear"` |
| `SessionEnd` | `reason`: `"exit"` \| `"clear"` \| `"logout"` \| `"prompt_input_exit"` \| `"other"` |
| `Notification` | `notification_type` (e.g. `"ToolPermission"`), `message`, `details` |
| `PreCompress` | `trigger`: `"auto"` \| `"manual"` |

## Output from hooks (via stdout)

Common fields:

| Field | Description |
|-------|-------------|
| `systemMessage` | User-visible feedback message |
| `decision` | `"allow"` or `"deny"` (alias `"block"`) — effect depends on event |
| `reason` | Explanation for denials/retries |
| `continue` | Boolean — `false` stops the agent loop immediately |
| `suppressOutput` | Hide hook metadata from logs/telemetry |
| `stopReason` | Shown to the user when `continue` is `false` |

Event-specific `hookSpecificOutput` fields:

| Event | Field | Effect |
|-------|-------|--------|
| `BeforeTool` | `tool_input` | Merges with/overrides the model's tool arguments |
| `AfterTool` | `additionalContext` | Text appended to the tool result for the agent |
| `AfterTool` | `tailToolCallRequest` (`{name, args}`) | Runs another tool immediately, replacing this tool's response |
| `BeforeAgent` | `additionalContext` | Text appended to the prompt for this turn only |
| `AfterAgent` | `clearContext` (boolean) | Clears conversation history while preserving UI display |
| `BeforeModel` | `llm_request` | Overrides parts of the outgoing request (model, temperature, …) |
| `BeforeModel` | `llm_response` | A synthetic response — CLI skips the LLM call entirely |
| `BeforeToolSelection` | `toolConfig.mode` (`"AUTO"`\|`"ANY"`\|`"NONE"`) | Forces/disables tool calling. `"NONE"` wins over other hooks |
| `BeforeToolSelection` | `toolConfig.allowedFunctionNames` | Tool whitelist — union across hooks. No `decision`/`continue`/`systemMessage` support here |
| `AfterModel` | `llm_response` | Replaces the model's response chunk (fires per streaming chunk) |
| `SessionStart` | `additionalContext` | Injected as first turn (interactive) or prepended to prompt (non-interactive) |

`SessionEnd`, `Notification`, and `PreCompress` are advisory/best-effort only — `continue`/`decision` are ignored for them, and startup/shutdown/compression are never blocked by them.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success — parse JSON from stdout |
| `2` | Block — use stderr content as rejection/replacement reason (tool blocked, turn aborted, response discarded, or retry triggered depending on event) |
| other | Warning — non-fatal failure, continue with original parameters |

**Golden rule:** stdout must contain *only* the final JSON — any stray `print`/`echo` before it breaks parsing and the CLI defaults to "allow", treating the polluted output as a `systemMessage`. Use stderr for all logging/debugging.

## Environment variables available to hook scripts

| Variable | Description |
|----------|-------------|
| `GEMINI_PROJECT_DIR` | Absolute path to the project root |
| `GEMINI_PLANS_DIR` | Absolute path to the plans directory |
| `GEMINI_SESSION_ID` | Current session ID |
| `GEMINI_CWD` | Current working directory |
| `CLAUDE_PROJECT_DIR` | Alias of `GEMINI_PROJECT_DIR`, for cross-tool script compatibility |

## Security

Hooks run arbitrary code with your user privileges. Project-level hooks are fingerprinted — if a hook's name or command changes (e.g. via `git pull`), the CLI treats it as new/untrusted and warns before executing.

## Managing hooks (CLI commands)

| Command | Description |
|---------|-------------|
| `/hooks panel` | View configured hooks |
| `/hooks enable-all` / `/hooks disable-all` | Toggle all hooks |
| `/hooks enable <name>` / `/hooks disable <name>` | Toggle an individual hook by `name` |

## Examples

**Block dangerous shell commands:**
```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "run_shell_command",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.gemini/hooks/block-rm-rf.py",
            "name": "safety-check"
          }
        ]
      }
    ]
  }
}
```

**Run on session start:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Session started at $(date)\" >> ~/.gemini/sessions.log"
          }
        ]
      }
    ]
  }
}
```

## Hook scripts (stderr for logging)

Hooks receive context on stdin and write JSON to stdout. Use stderr for log messages — stderr output is shown as a warning and doesn't affect the decision.

```python
#!/usr/bin/env python3
import json, sys

data = json.load(sys.stdin)
tool_name = data.get("tool_name", "")

if "rm -rf" in data.get("tool_input", {}).get("command", ""):
    print(json.dumps({"decision": "deny", "reason": "rm -rf is not allowed"}))
    sys.exit(2)

print(json.dumps({"decision": "allow"}))
```

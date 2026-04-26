# Hooks Reference

Hooks are configured in `settings.json` under a `hooks` key.

## Global enable/disable

Control the entire hooks system with `hooksConfig`:

```json
{
  "hooksConfig": {
    "enabled": true,
    "notifications": true
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `hooksConfig.enabled` | `true` | Master toggle — `false` disables all hooks |
| `hooksConfig.notifications` | `true` | Show visual indicators when hooks are executing |

## Configuration location

```json
{
  "hooks": {
    "BeforeTool": [...],
    "AfterTool": [...],
    "BeforeAgent": [...],
    "AfterAgent": [...],
    "BeforeModel": [...],
    "BeforeToolSelection": [...],
    "AfterModel": [...],
    "SessionStart": [...],
    "SessionEnd": [...],
    "Notification": [...],
    "PreCompress": [...]
  }
}
```

## Event types

### Tool hooks
| Event | When it fires |
|-------|---------------|
| `BeforeTool` | Before any tool executes — can block or modify inputs |
| `AfterTool` | After tool completes — can audit results, inject context |

### Agent hooks
| Event | When it fires |
|-------|---------------|
| `BeforeAgent` | Before agent processes a prompt — can validate or modify |
| `AfterAgent` | After agent response — can trigger retries |

### Model hooks
| Event | When it fires |
|-------|---------------|
| `BeforeModel` | Before sending request to model — can inject synthetic response |
| `BeforeToolSelection` | Before model chooses which tool to call |
| `AfterModel` | After model responds |

### Lifecycle hooks
| Event | When it fires |
|-------|---------------|
| `SessionStart` | Once when session begins — context initialization |
| `SessionEnd` | Once when session ends — cleanup |
| `Notification` | When CLI surfaces a notification |
| `PreCompress` | Before context compression occurs |

## Handler fields

Each hook entry is an object:

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | Handler type — currently only `"command"` |
| `command` | Yes | Shell command to execute |
| `name` | No | Display name for the hook |
| `description` | No | Human-readable description |
| `timeout` | No | Timeout in milliseconds (default: 60000) |
| `matcher` | No | Regex (for tool hooks) or exact string to filter which events trigger this hook |
| `sequential` | No | Boolean — run sequentially instead of in parallel |

## Input to hooks (via stdin)

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript",
  "cwd": "/current/working/dir",
  "hook_event_name": "BeforeTool",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Tool hooks also receive tool name and arguments.

## Output from hooks (via stdout)

| Field | Description |
|-------|-------------|
| `systemMessage` | User-visible feedback message |
| `decision` | `"allow"` or `"deny"` / `"block"` |
| `reason` | Explanation for denials |
| `continue` | Boolean — `false` stops the agent loop |
| `suppressOutput` | Hide hook metadata from logs |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success — parse JSON from stdout |
| `2` | Block — use stderr content as rejection reason |
| other | Warning — non-fatal failure, continue |

## Examples

**Log all tool calls:**
```json
{
  "hooks": {
    "BeforeTool": [
      {
        "type": "command",
        "command": "echo \"Tool called\" >> ~/.gemini/tool-log.txt",
        "name": "tool-logger"
      }
    ]
  }
}
```

**Block dangerous shell commands:**
```json
{
  "hooks": {
    "BeforeTool": [
      {
        "type": "command",
        "command": "python3 ~/.gemini/hooks/block-rm-rf.py",
        "matcher": "run_shell_command",
        "name": "safety-check"
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
        "type": "command",
        "command": "echo \"Session started at $(date)\" >> ~/.gemini/sessions.log"
      }
    ]
  }
}
```

## Hook scripts (stderr for logging)

Hooks receive context on stdin and write JSON to stdout. Use stderr for log messages — stderr output is shown as warnings and doesn't affect the decision.

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

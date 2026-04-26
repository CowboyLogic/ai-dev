# Hooks Reference

## File location

```
.github/hooks/hooks.json        ← project scope (must be on default branch for cloud agent)
```

For CLI, hooks are loaded from the current working directory. The file must be on the default branch to work with the cloud agent.

## Structure

```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "bash": "echo '$INPUT' | ./scripts/validate-tool.sh",
        "powershell": "Write-Output '$INPUT' | .\\scripts\\validate-tool.ps1",
        "cwd": ".",
        "timeoutSec": 30,
        "env": {
          "MY_VAR": "value"
        },
        "matcher": "shell"
      }
    ]
  }
}
```

**Required**: `"version": 1`

**`matcher` field**: When set on `preToolUse` or `postToolUse` hooks, the hook only fires for tool names that fully match the pattern. Partial matches are ignored (fixed in v1.0.36).

---

## Hook events

| Event | When it fires |
|-------|---------------|
| `sessionStart` | When an agent session begins |
| `sessionEnd` | When an agent session concludes |
| `userPromptSubmitted` | After user input is received |
| `preToolUse` | Before a tool is executed |
| `postToolUse` | After a tool completes execution |
| `errorOccurred` | When an error happens |

---

## Hook command fields

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"command"` or `"http"` |
| `bash` | command only* | Command string for Unix/Linux/macOS |
| `powershell` | command only* | Command string for Windows PowerShell |
| `url` | http only | URL to POST the hook payload to |
| `headers` | http only | HTTP headers object (for auth etc.) |
| `cwd` | No | Working directory (default: `"."`) — command type only |
| `timeoutSec` | No | Max execution time in seconds (default: 30) |
| `env` | No | Additional environment variables object — command type only |
| `matcher` | No | Tool name pattern; hook only fires for fully matching tool names (`preToolUse`/`postToolUse`) |

*For `command` type, provide both `bash` and `powershell` for cross-platform compatibility, or just one if targeting a specific OS.

---

## Hook types

### `command` (run a local script)

Runs a local process. Input is passed via `$INPUT` (bash) or `$INPUT` (PowerShell).

```json
{
  "type": "command",
  "bash": "echo '$INPUT' | ./scripts/validate-tool.sh",
  "powershell": "Write-Output '$INPUT' | .\\scripts\\validate-tool.ps1",
  "cwd": ".",
  "timeoutSec": 30
}
```

### `http` (POST to a URL)

Posts the hook payload as JSON to a remote or local HTTP endpoint. Useful for webhooks, audit logging, or integrations.

```json
{
  "type": "http",
  "url": "https://hooks.example.com/copilot-events",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
  },
  "timeoutSec": 10
}
```

---

## Script requirements

Hook scripts must:
- Be executable: `chmod +x script.sh`
- Include a shebang: `#!/bin/bash`
- Return valid JSON on a single line to stdout
- Exit with appropriate status codes

---

## Examples

### Log all tool calls
```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "bash": "echo \"[$(date)] Tool: $TOOL_NAME\" >> ~/copilot-tool-log.txt",
        "timeoutSec": 5
      }
    ]
  }
}
```

### Block dangerous shell commands
```json
{
  "version": 1,
  "hooks": {
    "preToolUse": [
      {
        "type": "command",
        "bash": "./.github/hooks/block-dangerous.sh",
        "timeoutSec": 10
      }
    ]
  }
}
```

```bash
#!/bin/bash
# block-dangerous.sh — blocks rm -rf and DROP TABLE
INPUT=$(cat)
if echo "$INPUT" | grep -qE 'rm -rf|DROP TABLE'; then
  echo '{"decision": "deny", "reason": "Destructive command blocked by hook"}'
  exit 0
fi
exit 0
```

### Notify on session end
```json
{
  "version": 1,
  "hooks": {
    "sessionEnd": [
      {
        "type": "command",
        "bash": "osascript -e 'display notification \"Copilot session ended\" with title \"Copilot CLI\"' 2>/dev/null || true",
        "timeoutSec": 5
      }
    ]
  }
}
```

---

## Testing & debugging hooks

```bash
# Test a hook script by piping sample input
echo '{"tool": "shell", "command": "ls"}' | ./.github/hooks/my-hook.sh

# Check exit code
echo $?

# Validate JSON output
echo '{"tool": "shell"}' | ./.github/hooks/my-hook.sh | python3 -m json.tool

# Enable bash debug tracing
bash -x ./.github/hooks/my-hook.sh
```

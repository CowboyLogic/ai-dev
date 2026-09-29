# Hooks Reference

Hooks run scripts (or MCP tools) at lifecycle points in a Codex session. They are enabled by
default. Verified against codex-cli 0.158.0.

## Where hooks are loaded from

Codex discovers hooks next to every active config layer, in either form:

| Source | Location |
|--------|----------|
| User | `~/.codex/hooks.json` or `[hooks]` in `~/.codex/config.toml` (`$CODEX_HOME`) |
| Project | `<repo>/.codex/hooks.json` or `[hooks]` in `<repo>/.codex/config.toml` |
| Plugin | `hooks/hooks.json` in the plugin root, or `hooks` in `.codex-plugin/plugin.json` |
| Managed | `[hooks]` in `requirements.toml`, plus system, MDM, and cloud-managed layers |

- Every matching hook from every source runs. A higher-precedence layer does **not** replace
  lower-precedence hooks.
- One layer with both `hooks.json` and inline `[hooks]` is merged, with a startup warning. Use
  one form per layer.
- Project hooks load only when the project `.codex/` layer is trusted. User and system hooks
  still load in untrusted projects.
- Multiple matching command hooks for one event start **concurrently**. One hook cannot stop
  another from starting.
- Commands run with the session `cwd` as working directory. Codex may launch from a
  subdirectory, so resolve repo-local scripts from the git root:
  `"$(git rev-parse --show-toplevel)/.codex/hooks/x.sh"`.

## Trust and review

Non-managed hooks are skipped until reviewed and trusted.

- Codex records trust against a hash of the hook definition. A **new or changed** hook is marked
  for review and does not run until trusted again.
- Run `/hooks` in the CLI to inspect sources, review new or changed hooks, trust them, and
  disable or re-enable individual non-managed hooks. Codex warns at startup when hooks need
  review and points at `/hooks`.
- Managed hooks are trusted by policy and cannot be disabled from `/hooks`.
- Installing or enabling a plugin does not trust its hooks. Review them the same way.
- Editing a hook definition means re-trusting it. After any edit to `hooks.json`, open `/hooks`
  and confirm the hook shows as trusted.
- `--dangerously-bypass-hook-trust` (top-level `codex` flag) runs enabled hooks without persisted
  trust for that invocation. Use it only in automation that vets hook sources itself.

> [!NOTE]
> The docs do not say where trust is persisted. On 0.158.0 it appears as `[hooks.state."<path>:<event>:<group>:<index>"]`
> tables holding a `trusted_hash` in `~/.codex/config.toml`. Treat those tables as machine
> state: do not hand-edit or copy them between machines. Re-trust through `/hooks`.

## Feature flag

Hooks are a stable feature, on by default (`codex features list` shows `hooks  stable  true`).

```toml
[features]
hooks = false   # turn all hooks off
```

- `hooks` is the canonical key. `codex_hooks` is a deprecated alias.
- `codex features enable hooks` / `codex features disable hooks` write the flag to `config.toml`.
  `--enable hooks` / `--disable hooks` override it for one run.
- Admins can pin it in `requirements.toml` with `[features].hooks = true` (enforce) or `false`.

`codex features list` also lists `plugin_hooks` as `removed`. Do not set it.

## File format (`hooks.json`)

Three levels: event, matcher group, handlers.

```json
{
  "description": "Optional note. Does not change which hooks run.",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$(git rev-parse --show-toplevel)/.codex/hooks/guard.sh\"",
            "timeout": 30,
            "statusMessage": "Checking Bash command"
          }
        ]
      }
    ]
  }
}
```

Equivalent inline TOML (same event schema, in `config.toml`):

```toml
[[hooks.PreToolUse]]
matcher = "^Bash$"

[[hooks.PreToolUse.hooks]]
type = "command"
command = '"$(git rev-parse --show-toplevel)/.codex/hooks/guard.sh"'
timeout = 30
statusMessage = "Checking Bash command"
```

Event names are PascalCase: `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreToolUse`,
`PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `SubagentStart`,
`SubagentStop`, `Stop`, `Interrupt`.

## Handler types

Only `command` and `mcp_tool` run. `prompt` and `agent` handlers are parsed and **skipped**.

### `command`

| Field | Description |
|-------|-------------|
| `type` | `"command"` |
| `command` | Shell command line. Receives the event JSON on stdin |
| `commandWindows` | Optional Windows-only override. TOML also accepts `command_windows` |
| `timeout` | Seconds. Default `600`. `SessionEnd` and `Interrupt` default to `1`, max `3` |
| `statusMessage` | Optional text shown while the hook runs |
| `async` | `true` runs it in the background (see below). Default `false` |
| `additionalContextLimit` | Approximate token threshold for `additionalContext` (default `2500`) |

### `mcp_tool`

Calls a tool on an **already-connected** MCP server. Same trust review and output contract as a
command hook.

```json
{ "type": "mcp_tool", "server": "scanner", "tool": "scan_patch",
  "input": { "patch": "${tool_input.command}" }, "timeout": 30 }
```

- `server` and `tool` are required. `input` is an optional object of argument templates
  (default `{}`). `timeout` defaults to `600` (the shorter of hook and server timeouts applies).
- `${field.nested}` reads a dotted field from the hook event. A whole-value placeholder keeps its
  JSON type; inside a larger string it renders as text.
- Hooks never start or reconnect servers. A missing server, unavailable tool, or error does **not**
  block the operation. Only a tool that returns a blocking decision does.
- Runs synchronously, requests no approval, triggers no other hooks. `SessionStart` can fire before
  the server is ready (it then does not block). `SessionEnd` does not support MCP tool hooks.

### Background hooks (`async: true`)

- Command hooks only. Output is delivered at the next safe point (next model request in an active
  turn, else the next user turn): `additionalContext` reaches the model, `systemMessage` shows as
  a warning.
- They **cannot** block, approve, rewrite, or control the triggering operation. Use synchronous
  hooks for policy, permissions, prompt rejection, and continuation.
- At most 8 run concurrently per session; unfinished ones are cancelled at session end.
  `SessionEnd` always runs synchronously.

## Events

| Event | Fires | `matcher` filters |
|-------|-------|-------------------|
| `SessionStart` | Session starts, resumes, clears, or after compaction | `source`: `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | Main thread ends (archive/delete of an open chat, normal close, 30 min idle). Not for subagents | `reason` (currently always `other`) |
| `UserPromptSubmit` | Before a prompt is sent | Not supported (ignored) |
| `PreToolUse` | Before a supported tool runs | Tool name |
| `PermissionRequest` | Codex is about to ask for approval (not for commands needing none) | Tool name |
| `PostToolUse` | After a supported tool produces output (including non-zero Bash exits) | Tool name |
| `PreCompact` | Before chat compaction | `trigger`: `manual`, `auto` |
| `PostCompact` | After chat compaction | `trigger`: `manual`, `auto` |
| `SubagentStart` | A subagent starts | `agent_type` |
| `SubagentStop` | A subagent finishes | `agent_type` |
| `Stop` | The main turn is about to end | Not supported (ignored) |
| `Interrupt` | You interrupt an active turn on the main thread. Not idle threads or subagents | Not supported (ignored) |

## Matchers

`matcher` is a regex string. `"*"`, `""`, or omitting it matches every occurrence.

- Examples: `Bash`, `^apply_patch$`, `Edit|Write`, `mcp__filesystem__.*`, `startup|resume`,
  `manual|auto`.
- The docs do not say whether patterns are anchored. Anchor with `^...$` when you need an exact
  match.
- `apply_patch` also matches `Edit` and `Write`, but input still reports `tool_name: "apply_patch"`.
- `spawn_agent` also matches `Agent`.

Tool coverage for `PreToolUse` and `PostToolUse`: shell and unified exec (`Bash`), `apply_patch`
(`apply_patch`/`Edit`/`Write`), MCP tools (`mcp__<server>__<tool>`), and other local function
tools (by function name, for example `update_plan`). Hosted tools such as `WebSearch` are **not**
hooked.

`write_stdin` polls do not re-run `PreToolUse`. Some specialized tool paths can opt out. Treat
tool hooks as a guardrail, not a complete enforcement boundary.

## Input payload (stdin)

Every command hook gets one JSON object on stdin.

| Field | Meaning |
|-------|---------|
| `session_id` | Session id (subagent hooks use the parent's) |
| `transcript_path` | Transcript file path or `null`. Format is not a stable interface |
| `cwd` | Session working directory |
| `hook_event_name` | Event name |
| `model` | Active model slug |
| `permission_mode` | `default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions` (on all events except `SessionEnd`, `PreCompact`, `PostCompact`) |

Event-specific additions (`turn_id` is also present on turn-scoped events):

| Event | Extra fields |
|-------|--------------|
| `SessionStart` | `source` |
| `SessionEnd` | `reason` |
| `UserPromptSubmit` | `turn_id`, `prompt` |
| `PreToolUse` | `turn_id`, `tool_name`, `tool_use_id`, `tool_input` |
| `PermissionRequest` | `turn_id`, `tool_name`, `tool_input` (`tool_input.description` when available) |
| `PostToolUse` | `turn_id`, `tool_name`, `tool_use_id`, `tool_input`, `tool_response` |
| `PreCompact`, `PostCompact` | `turn_id`, `trigger` |
| `SubagentStart` | `turn_id`, `agent_id`, `agent_type` |
| `SubagentStop` | `turn_id`, `agent_id`, `agent_type`, `agent_transcript_path`, `stop_hook_active`, `last_assistant_message` |
| `Stop` | `turn_id`, `stop_hook_active`, `last_assistant_message` |
| `Interrupt` | `turn_id` |

`tool_input` for `Bash` and `apply_patch` is an object with `command`. MCP and other function
tools send their arguments.

## Output and decisions

Exit `0` with no output is success. Plain stdout is added as developer context **only** for
`SessionStart`, `UserPromptSubmit`, and `SubagentStart`. Every other event ignores plain text, and
`SubagentStop`, `Stop`, and `Interrupt` treat plain text on exit `0` as invalid (they expect JSON).

Shared JSON fields (`SessionStart`, `PreCompact`, `PostCompact`, `UserPromptSubmit`,
`SubagentStop`, `Stop`): `continue` (`false` marks the hook run stopped), `stopReason`,
`systemMessage` (surfaced as a UI warning), `suppressOutput` (parsed, not implemented).

Per-event behavior:

| Event | How to act |
|-------|-----------|
| `PreToolUse` | Deny: `hookSpecificOutput.permissionDecision: "deny"` plus `permissionDecisionReason`; or legacy `{"decision":"block","reason":...}`; or exit `2` with reason on stderr. Rewrite: `permissionDecision: "allow"` plus `updatedInput`. Context: `hookSpecificOutput.additionalContext` |
| `PermissionRequest` | `hookSpecificOutput.decision.behavior` = `"allow"` or `"deny"` (with `message`). Any `deny` wins; otherwise `allow` skips the prompt; no decision means the normal prompt |
| `PostToolUse` | `decision: "block"` plus `reason` (or exit `2` with stderr) replaces the tool result with your feedback and continues. It cannot undo the tool. `continue: false` also replaces the result. `additionalContext` adds developer context |
| `UserPromptSubmit` | `decision: "block"` plus `reason` (or exit `2`) rejects the prompt. `additionalContext` adds context |
| `Stop`, `SubagentStop` | `decision: "block"` plus `reason` (or exit `2`) does **not** reject the turn. It continues, using `reason` as a new prompt. `continue: false` from any hook wins over continuation |
| `SessionStart` | `additionalContext` adds developer context. After compaction, `continue: false` ends the turn without another model request |
| `SubagentStart` | `additionalContext` goes to the subagent. `continue: false` does not stop it |
| `PreCompact`, `PostCompact` | `continue: false` stops before or after compacting |
| `SessionEnd`, `Interrupt` | Advisory only. Optional `systemMessage` |

`updatedInput` rules: for `Bash` and `apply_patch` it must contain a string `command`; for MCP and
other function tools it is the replacement arguments object. Return it only with
`permissionDecision: "allow"`.

Unsupported today. Codex marks the hook run failed, reports it, and **continues the tool call**:
on `PreToolUse`, `permissionDecision: "ask"`, legacy `decision: "approve"`, `continue: false`,
`stopReason`, `suppressOutput`. Do not return `updatedInput`, `updatedPermissions`, or `interrupt`
from `PermissionRequest`. `updatedMCPToolOutput` and `suppressOutput` fail on `PostToolUse`.

### Exit codes

`0` is success (stdout parsed per the event rules). `2` blocks or gives feedback, with the reason
on stderr (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`, `SubagentStop`). Any other
exit is reported as a hook failure.

> [!WARNING]
> The docs define only exit `0` and `2`. Do not rely on any other non-zero exit, a timeout, or a
> missing script to block a tool call. Emit an explicit deny decision (or exit `2`) to block.

### Large output

Model-visible hook output is capped near 2,500 tokens per message. Oversized text is saved under
`<temp_dir>/hook_outputs/<session_id>/` and the model sees a head-and-tail preview. Set
`additionalContextLimit` on a handler to change the threshold (`0` disables it; avoid). Never put
secrets in hook output, since it can land on disk.

## Plugin-bundled and managed hooks

- Plugin default file is `hooks/hooks.json` in the plugin root. A `hooks` entry in
  `.codex-plugin/plugin.json` replaces it (a `./` path, array of paths, inline object, or array of
  inline objects; paths must stay inside the plugin root). Commands get `PLUGIN_ROOT` and
  `PLUGIN_DATA`, plus `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` for compatibility.
- Managed hooks live in `requirements.toml` under `[hooks]` with the same event schema, plus
  `managed_dir` (macOS/Linux) and `windows_managed_dir`. Codex does not distribute the scripts;
  deliver them by MDM and use absolute paths. Set `allow_managed_hooks_only = true` to skip user,
  project, session, and plugin hooks, and pin `[features].hooks = true` to enforce hooks.

## Examples

### PreToolUse guard that blocks a Bash pattern

Register it under `PreToolUse` with `"matcher": "Bash"` and
`"command": "~/.codex/hooks/block-rm.sh"`, then trust it in `/hooks`. The script:

```bash
#!/bin/bash
COMMAND=$(jq -r '.tool_input.command')
if printf '%s\n' "$COMMAND" | grep -Eq '(^|[;&|][[:space:]]*)rm[[:space:]]+-rf[[:space:]]+/([[:space:]]|$)'; then
  jq -n '{hookSpecificOutput: {hookEventName: "PreToolUse",
          permissionDecision: "deny",
          permissionDecisionReason: "Recursive delete from / is blocked by hook."}}'
fi
exit 0
```

### Stop hook that asks for one more pass

```bash
#!/bin/bash
INPUT=$(cat)
# Guard against infinite continuation: only continue once per turn.
[ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ] && exit 0
jq -n '{decision: "block", reason: "Run the test suite and fix any failures before finishing."}'
```

The `reason` becomes a new user-style prompt. Always check `stop_hook_active`. Plain stdout from
`SessionStart` and `UserPromptSubmit` is added as developer context without any JSON.

## Testing and debugging

There is no `codex debug` hooks subcommand. Test scripts directly:

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf /"},"cwd":"/tmp"}' \
  | ~/.codex/hooks/block-rm.sh | jq .
```

Checklist when a hook does not fire:

1. Run `/hooks`. Is the hook listed, trusted, and not disabled? New or edited hooks need review.
2. `codex features list | grep hooks` shows `true`, and no `[features] hooks = false` in a layer.
3. Project hooks: is the project trusted? Untrusted projects skip `<repo>/.codex/`.
4. The `matcher` matches the canonical tool name (`Bash`, `apply_patch`, `mcp__server__tool`).
5. `jq . hooks.json` parses. Prefer one of `hooks.json` or `[hooks]` per layer.
6. Script is executable with a shebang, resolves from the git root, and prints one JSON object.
7. Output shape matches the event. Unsupported fields mark the run failed and the tool call
   proceeds. Hosted tools and some specialized tool paths bypass hooks entirely.

`hooks.run` and `hooks.run.duration_ms` OpenTelemetry metrics (by `hook_name`, `source`,
`status`) are emitted when telemetry is configured.

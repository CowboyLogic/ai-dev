# Frontmatter Reference — Claude Code Subagents

Reference for the YAML frontmatter fields of Claude Code agent files. Load this file when
writing, reviewing, or debugging agent frontmatter.

**Source (last verified September 2026; the docs reference versions up to v2.1.281):**
<https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields>

Field names are camelCase and case-sensitive. **Unrecognized fields are ignored without an
error**, so a misspelling looks exactly like a working file.

---

## All Fields at a Glance

```yaml
---
name: code-reviewer                  # required
description: Reviews code. Use proactively after changes.   # required
tools: Read, Grep, Glob              # allowlist; omit = inherit all
disallowedTools: Write, Edit         # denylist; applied before tools
model: sonnet                        # sonnet | opus | haiku | fable | full ID | inherit
permissionMode: default              # default|manual|acceptEdits|auto|dontAsk|bypassPermissions|plan
maxTurns: 15                         # positive integer
skills:                              # preloaded, full content
  - code-standards
mcpServers:                          # names or inline definitions
  - github
hooks:                               # PreToolUse | PostToolUse | Stop | any hook event
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"
memory: project                      # user | project | local
background: false
omitClaudeMd: false                  # v2.1.271+
effort: high                         # low | medium | high | xhigh | max
isolation: worktree                  # only value
color: blue
initialPrompt: "Start by reading TODO.md"   # main-session use only
experimental:                        # v2.1.248+
  cacheTtl: 5m
---
```

---

## Field Details

### `name` (required)

| Rule | Detail |
|---|---|
| Format | Unique identifier such as `code-reviewer` or `reviewer-v2` |
| Must not start with `-` | The file is skipped and an error goes to the debug log |
| Must not contain `:` | Reserved for plugin-scoped names (`my-plugin:reviewer`). Skipped since v2.1.218; earlier versions accepted it |
| Filename | Does not have to match `name` |
| Hooks | `SubagentStart`/`SubagentStop` matchers and the `agent_type` input use this value |
| Uniqueness | Same `name` twice in one directory tree: only one loads, by filesystem order |

Spaces and capitals are accepted (the Matrix topology uses `name: The Architect`). The docs
restrict only a leading `-` and `:`.

### `description` (required)

When Claude should delegate to the agent. A file with a `name` but no `description` is
skipped (reason logged to the debug log). Include "use proactively" to encourage automatic
delegation. Combined `name` + `description` text across all non-built-in agents over
15,000 tokens shows a startup warning; every agent still loads.

### `tools`

| Form | Example |
|---|---|
| Comma-separated string | `tools: Read, Grep, Bash` |
| YAML list | `tools: [Read, Grep, Bash]` |
| Omitted | Inherits every tool available to subagents |
| Empty list | Launches with no tools and no error |
| Spawn allowlist | `tools: Agent(worker, researcher), Read` (main-session use only) |
| MCP server | `tools: mcp__github__*` |

- If entries are given but **none** resolve, launch is refused ("zero tools" error).
- Do not list `Skill` to preload skills; use the `skills` field.
- Legacy `Task(...)` still works as an alias for `Agent(...)` (renamed in v2.1.63).

See `tools-reference.md`.

### `disallowedTools`

Same format as `tools`. Removed first, then `tools` resolves against what is left; a tool in
both is removed. A specifier entry such as `Bash(git push *)` removes the **whole** tool.
`mcp__github` removes a server; `mcp__*` removes every MCP tool.

### `model`

| Value | Meaning |
|---|---|
| `sonnet`, `opus`, `haiku`, `fable` | Family alias, resolved to the current version |
| Full ID, e.g. `claude-opus-5-5` | Accepts what `--model` accepts |
| `inherit` | The main conversation's model |
| Omitted | Falls through the resolution order |

Resolution order: (1) per-invocation `model` parameter, (2) frontmatter `model`,
(3) `CLAUDE_CODE_SUBAGENT_MODEL`, (4) main conversation's model. With
`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (v2.1.257+) frontmatter and per-invocation values are
ignored for every subagent, including built-in Explore and Plan.

Before v2.1.251, `CLAUDE_CODE_SUBAGENT_MODEL` came first in the order. Values are checked
against the organization's `availableModels` allowlist and substituted with a warning if
blocked. Subagents inherit the parent's extended-thinking setting (v2.1.198+); there is no
per-agent thinking field.

### `permissionMode`

| Value | Behavior |
|---|---|
| `default` (alias `manual`, v2.1.200+) | Prompts for permission |
| `acceptEdits` | Auto-accepts edits and common filesystem commands in the working directory or `additionalDirectories` |
| `auto` | Background classifier reviews commands and protected-directory writes |
| `dontAsk` | Auto-denies prompts; explicitly allowed tools still work |
| `bypassPermissions` | Skips checks, but only when the parent session is already in this mode (v2.1.267+) |
| `plan` | Read-only exploration; keeps `ExitPlanMode` |

**The parent wins in some cases.** If the parent is in `bypassPermissions`, `acceptEdits`, or
`auto`, the agent runs in the parent's mode and this field is ignored. If the parent is in
`default`, `dontAsk`, or `plan`, the field applies (except `bypassPermissions`, which falls
back to the parent's mode). Ignored for plugin agents. Unset = inherit the parent's mode.

### `maxTurns`

Positive integer. At the limit the agent stops and its output is marked partial (v2.1.246+);
Claude can resume it to continue.

### `skills`

List of skill names. The **full** skill content is injected at startup. The agent can still
invoke unlisted skills through the Skill tool unless `Skill` is omitted from `tools` or
listed in `disallowedTools`. Skills with `disable-model-invocation: true` cannot be
preloaded. A missing or policy-disabled skill is skipped with a debug-log warning.

### `mcpServers`

List of entries, each either a name string (shares the parent's connection) or a one-key
object with an inline definition (`stdio`, `http`, `sse`, `ws`), scoped to this agent and
disconnected when it finishes:

```yaml
mcpServers:
  - playwright:
      type: stdio
      command: npx
      args: ["-y", "@playwright/mcp@latest"]
  - github
```

Inline servers from a project `.claude/agents/` (or an `--add-dir` directory) load only after
the **folder containing the agent file** is trusted (parent-folder trust does not count).
Inline servers from `~/.claude/agents/`, `--agents`, or managed settings, and name
references, load without that check. `--strict-mcp-config`, `--bare`, managed MCP config, and
`allowedMcpServers`/`deniedMcpServers` policies still apply. Ignored for plugin agents.

### `hooks`

Hooks scoped to this agent, cleaned up when it finishes. All hook events are supported;
common ones are `PreToolUse`, `PostToolUse`, and `Stop` (converted to `SubagentStop`).
Same schema as `settings.json` hooks. They fire when the file runs as a subagent, via
@-mention, or as the main session. Project-level agents need the folder trusted; otherwise
the agent runs with hooks skipped and an error in the debug log. Ignored for plugin agents.

### `memory`

| Scope | Directory |
|---|---|
| `user` | `~/.claude/agent-memory/<name>/` |
| `project` | `.claude/agent-memory/<name>/` (recommended default; shareable) |
| `local` | `.claude/agent-memory-local/<name>/` (not for version control) |

Adds memory instructions and the first 200 lines or 25 KB of `MEMORY.md` to the system
prompt and enables Read, Write, and Edit. Has no effect if auto memory is off
(`autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY`). Tell the agent in its
prompt to consult and update memory.

### `background`

`true` keeps the agent in the background even if Claude asks for the foreground. Background
agents get a reduced built-in tool set and route permission prompts to the main session.

### `omitClaudeMd`

`true` launches without user, project, and local CLAUDE.md. Managed policy CLAUDE.md files
still load (except for managed agents). Ignored when running as the main session agent.
Requires v2.1.271+. Use for agents that take everything from the delegation prompt.

### `effort`

`low`, `medium`, `high`, `xhigh`, `max`; which are available depends on the model. Overrides
the session effort while the agent is active.

### `isolation`

Only `worktree`. Runs in a temporary git worktree branched from the **default branch** (not
the parent's `HEAD`); cleaned up automatically when there are no changes. Commands whose
working directory resolves to the main checkout fail. In sessions with agent teams enabled, a
*named* spawn becomes a teammate and runs in the main working directory, even with `isolation`
in the frontmatter, unless the Agent call itself passes `isolation`.

### `color`

`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. Display only. Not
accepted in `--agents` JSON (ignored).

### `initialPrompt`

Submitted as the first user turn when the file runs as the main session agent (`--agent` or
the `agent` setting); commands and skills in it are processed and it is prepended to any
user prompt. Ignored for plugin agents. Does nothing when the file is used as a subagent.

### `experimental`

Map, read only from subagent files. `cacheTtl: 5m | 1h` sets the prompt-cache lifetime
(v2.1.248+). `1h` is ignored while the subscription is using usage credits. Must be nested
under `experimental`, not a top-level key. Not accepted in `--agents` JSON.

---

## Per-Scope Field Support

| Field | Project / user / managed file | `--agents` JSON | Plugin agent |
|---|---|---|---|
| `name` | Yes | Top-level key (must not start with `-`) | Yes (falls back to filename if missing or unparsable) |
| Body / `prompt` | Markdown body | `prompt` key (may be empty, v2.1.281+) | Markdown body |
| `hooks` | Yes (folder trust for project) | Yes | **Ignored** |
| `mcpServers` | Yes (folder trust for project inline) | Yes | **Ignored** |
| `permissionMode` | Yes | Yes | **Ignored** |
| `initialPrompt` | Yes | Yes | **Ignored** |
| `color`, `experimental` | Yes | **Ignored** | Yes |

---

## `--agents` JSON

Session-only agents, not saved to disk. Each top-level key is the name; the value takes
`prompt` plus these fields: `description`, `tools`, `disallowedTools`, `model`,
`permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`,
`effort`, `background`, `omitClaudeMd`, `isolation`.

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer.",
    "tools": ["Read", "Grep", "Glob"],
    "model": "sonnet"
  }
}'
claude -p --agents ./agents.json "Review my changes"   # file form: -p only, v2.1.281+
```

An invalid value makes `claude` **exit with code 1** (since v2.1.242) and print
`Error: Invalid --agents configuration:` followed by up to 20 problem lines. Checks run in
order: JSON parse, then schema per definition, then names not starting with `-`. Fix the
first class of error and re-run to see the next.

---

## Running an Agent File as the Session

```bash
claude --agent code-reviewer
```

or `{"agent": "code-reviewer"}` in `settings.json`. The session then uses the agent's system
prompt, tool restrictions, and model. `initialPrompt` fires, `Agent(type)` spawn allowlists
apply, and `omitClaudeMd` is ignored.

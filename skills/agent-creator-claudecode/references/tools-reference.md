# Tools Reference — Claude Code Subagents

Load this file when choosing values for `tools` / `disallowedTools`, restricting what an
agent can spawn, or debugging "zero tools" and missing-tool problems.

**Sources:** <https://code.claude.com/docs/en/sub-agents#control-subagent-capabilities> ·
<https://code.claude.com/docs/en/tools-reference>

---

## Built-in Tool Names

Names are case-sensitive (`Grep`, not `grep`). Common ones for agent files:

| Tool | Use |
|---|---|
| `Read` | Read files |
| `Grep`, `Glob` | Search content / find files (absent by default on macOS, Linux, WSL, but subagents can still receive them) |
| `Edit`, `Write` | Modify or create files |
| `NotebookEdit` | Jupyter notebook cells |
| `Bash`, `PowerShell` | Shell commands |
| `WebFetch`, `WebSearch` | Web access |
| `LSP` | Language-server code intelligence |
| `Agent` | Spawn subagents (formerly `Task`; `Task(...)` still works as an alias) |
| `SendMessage` | Message or resume another agent |
| `Skill` | Invoke skills (do not list it to preload; use `skills`) |
| `TodoWrite`, `TaskCreate`/`TaskGet`/`TaskList`/`TaskUpdate` | Task tracking |
| `Monitor`, `TaskStop` | Background command monitoring and stopping |
| `EnterWorktree`, `ExitWorktree` | Worktree switching |
| `Artifact`, `ToolSearch` | Artifacts; deferred-tool loading |

The full list is in the tools reference page; verify a name there before using it.

---

## Removed From Every Subagent

These are removed even if listed in `tools`:

- `Agent` when the agent is at the nesting depth limit
- `AskUserQuestion`
- `EndConversation`
- `EnterPlanMode`
- `ExitPlanMode` (kept only when `permissionMode: plan`)
- `ScheduleWakeup`
- `WaitForMcpServers`
- `Workflow`

## Removed From Background Subagents

Background is the default in interactive sessions. A background subagent keeps every MCP
tool but only these built-ins (plus `SubagentHandback` where used): `Read`, `Grep`, `Glob`,
`LSP`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`,
`TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`,
`SendMessage`, `Artifact`. Everything else (for example `CronCreate`) is silently dropped
whether inherited or listed. `Agent` and `ExitPlanMode` follow the every-subagent rules.

The same file can therefore have different tools in the foreground and background. If a
tool works when you run the agent with `--agent` but not when Claude delegates to it, this
is the usual reason.

Forks skip both filters and get the parent's exact tool pool.

---

## Allowlist vs Denylist

```yaml
tools: Read, Grep, Glob, Bash        # only these (recommended for least privilege)
```

```yaml
disallowedTools: Write, Edit         # everything inherited except these
```

Both together: `disallowedTools` first, then `tools` against the remainder; a tool in both
is removed. Choose the allowlist when the agent's purpose is narrow, the denylist when you
want "everything except writes" and expect MCP tools to come along.

## MCP Patterns

| Entry | Effect |
|---|---|
| `mcp__github__*` or `mcp__github` in `tools` | Grants all tools from the `github` server |
| `mcp__github` in `disallowedTools` | Removes all tools from that server |
| `mcp__*` in `disallowedTools` | Removes all MCP tools from every server |

An allowlist that names an MCP server with no connected server resolves to nothing for that
entry, which can trigger the zero-tools refusal if nothing else in the list resolves.

## Specifiers Remove the Whole Tool

`disallowedTools: Bash(git push *)` does **not** keep Bash and block `git push`. It removes
Bash entirely. To block specific commands and keep the tool, add a deny rule to
`permissions.deny` in settings (`"Bash(git push *)"`), which applies to the whole session
including subagents, or use a `PreToolUse` hook in the agent's frontmatter.

---

## Restricting Which Subagents an Agent Can Spawn

```yaml
---
name: coordinator
description: Coordinates work across specialized agents
tools: Agent(worker, researcher), Read, Bash
---
```

- Works **only when the file runs as the main session** (`claude --agent coordinator` or the
  `agent` setting). The parenthesized list is then an allowlist.
- In a normal subagent definition the list inside the parentheses is ignored; `Agent` alone
  only controls whether it *can* spawn, within the depth limit.
- `tools: Agent, Read` allows any type. Omitting `Agent` means no spawning at all.
- To block a specific agent for everyone, deny it in settings:
  `"permissions": {"deny": ["Agent(my-agent)"]}` or `claude --disallowedTools "Agent(Explore)"`.
  This works for built-in and custom agents.

### Nesting limits

| Setting | Default | Notes |
|---|---|---|
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` | 3 layers below the main conversation | `1` turns nesting off. At the limit `Agent` is withheld (except for forks, where it errors) |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` | 20 | Over the limit: `Concurrent subagent limit reached`. Ultracode sessions are exempt |

A list containing only `Agent` resolves to nothing at the depth limit, so pair it with at
least one other tool. To keep a reviewer read-only and non-spawning, omit `Agent`.

---

## Permission Modes and Tools

Tools listed in `tools` still go through permission checks. `permissionMode` decides whether
the agent is prompted, and the parent's mode can override it: a parent in `bypassPermissions`,
`acceptEdits`, or `auto` forces its own mode on the subagent. Background agents route prompts
to the main session. `dontAsk` denies anything not explicitly allowed. See
`frontmatter-reference.md` for the full table.

Permission rules in `settings.json` (`permissions.allow` / `deny`) apply to subagents too.
For a plugin agent that needs a rule its frontmatter cannot carry, either copy the file to
`.claude/agents/` or add the rule to settings, knowing it then applies to the whole session.

---

## Built-in Agents You May Want to Override or Block

| Agent | Purpose | Default model |
|---|---|---|
| `Explore` | Read-only codebase search; skips CLAUDE.md and git status | Inherits, capped at Opus on the Claude API |
| `Plan` | Read-only research during plan mode | Inherits |
| `general-purpose` | Multi-step tasks needing exploration and action | Follows the model order |
| `claude` | Catch-all with every tool | Follows the model order |
| `statusline-setup`, `claude-code-guide` | Helper agents | Sonnet, Haiku |

Defining your own agent named `Explore` (for example with `model: haiku`) replaces the
built-in and keeps exploration cheap. Environment switches:
`CLAUDE_CODE_DISABLE_EXPLORE_PLAN_AGENTS=1`, `CLAUDE_CODE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1`
(non-interactive and SDK).

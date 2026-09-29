# Claude Code Agent Creator

A skill for creating and troubleshooting custom subagents for Claude Code.

## Overview

Claude Code agents are Markdown files with YAML frontmatter in `.claude/agents/` or
`~/.claude/agents/`. The frontmatter sets identity, tools, model, permissions, hooks, and
more; the body is the agent's system prompt. Claude Code **silently ignores** unrecognized
fields and **silently skips** files with certain problems, so a typo looks exactly like a
working file. This skill exists to make those failures visible.

This skill covers:

- Every supported frontmatter field, with allowed values, minimum Claude Code versions, and
  per-scope support (project, user, managed, `--agents` JSON, plugin)
- The exact conditions under which a file is skipped without notice
- Tools: allowlists, denylists, MCP patterns, what is removed from every or background subagent,
  and the `Agent(type)` spawn allowlist
- Model selection and resolution order, permission modes and when the parent overrides them
- Hooks, MCP servers, preloaded skills, persistent memory, and worktree isolation in frontmatter
- Symptom-to-cause troubleshooting tables
- Writing effective `description` and prompt bodies for subagents
- A validator script that checks a file or directory of agents

## Quick Start

1. Run `/agents` in Claude Code and choose **Create new agent**, or create
   `.claude/agents/<name>.md` by hand.
2. Set `name` and `description`, add `tools`, and write the prompt body.
3. Validate: `python scripts/validate-agent.py .claude/agents/`
4. Test with an @-mention (`@agent-<name>`), and run `claude --debug` if it does not appear.

## Validator

```bash
python scripts/validate-agent.py .claude/agents/my-agent.md
python scripts/validate-agent.py .claude/agents/ --strict
python scripts/validate-agent.py path/to/plugin/agents --plugin
```

Requires `pyyaml`. It flags: missing `name` or `description`, an opening `---` that is not on
line 1, `name` values Claude Code skips, YAML that does not parse, unknown and mis-cased fields
(`disallowed-tools` becomes a "did you mean `disallowedTools`" error), Copilot or OpenCode
fields that Claude Code ignores, invalid enum values, `tools`/`disallowedTools` conflicts,
fields ignored for plugin agents, and duplicate names within the scanned set.

It cannot know whether a tool name exists in your Claude Code build; check names against the
tools reference.

## Key Concepts

### Agents vs. Other Customizations

| Use | When |
|---|---|
| **Subagent** | Isolated context, restricted tools, or a different model for a side task |
| **Skill** | Reusable instructions loaded into the main conversation |
| **`--agent` session** | A whole session under one agent's prompt, tools, and model |
| **Fork** | A side task that needs the full conversation so far |
| **Hook** | Deterministic action on a lifecycle event |

### Scope Levels

| Scope | Location | Priority |
|---|---|---|
| Managed | `.claude/agents/` in the managed settings directory | 1 (highest) |
| CLI | `--agents '<json>'` | 2 |
| Project | `.claude/agents/` | 3 |
| User | `~/.claude/agents/` | 4 |
| Plugin | `<plugin>/agents/` | 5 (lowest) |

## Example Files

- [read-only-agent-example.md](references/read-only-agent-example.md): a reviewer with a read-only allowlist
- [worktree-implementer-example.md](references/worktree-implementer-example.md): an implementer with worktree isolation, a `PreToolUse` hook, project memory, and a preloaded skill

## Official Documentation

| Resource | URL |
|---|---|
| Create custom subagents | <https://code.claude.com/docs/en/sub-agents> |
| Tools reference | <https://code.claude.com/docs/en/tools-reference> |
| Errors reference | <https://code.claude.com/docs/en/errors> |
| Permission modes | <https://code.claude.com/docs/en/permission-modes> |
| Hooks | <https://code.claude.com/docs/en/hooks> |

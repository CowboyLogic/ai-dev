# Claude Code Agent Creator

Create and troubleshoot custom subagents for Claude Code: Markdown files with YAML
frontmatter in `.claude/agents/` or `~/.claude/agents/`. Covers every frontmatter field, the
conditions under which Claude Code silently skips a file, tool and permission behavior, and a
validator script.

- **Skill name:** `agent-creator-claudecode`
- **Last updated:** 2026-09-29
- **Source:** [skills/agent-creator-claudecode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-claudecode)

---

## What it does

Claude Code ignores frontmatter fields it does not recognize and skips some malformed files
without telling the session, so a misspelled `disallowed-tools` looks exactly like a working
agent. The skill gives an agent a workflow for planning, writing, validating, and testing a
subagent, and loads detailed reference material only when the task needs it.

**Topics covered:**

- Agent file format — `name` and `description` are the only required fields; the Markdown body
  is the system prompt
- The silent-skip rules: no `name`, opening `---` not on line 1, `name` starting with `-` or
  containing `:`, no `description`, YAML that does not parse
- Tools — `tools` allowlists, `disallowedTools`, MCP patterns, tools removed from every or
  background subagent, and the `Agent(type)` spawn allowlist
- Model aliases and the model resolution order
- `permissionMode` and when the parent session overrides it
- Hooks, `mcpServers`, preloaded `skills`, persistent `memory`, and `isolation: worktree`
- Per-scope support for project, user, managed, `--agents` JSON, and plugin agents
- Symptom-to-cause troubleshooting, including "zero tools" and `--agents` errors
- Writing effective `description` values and prompt bodies

**Where agents live:**

| Scope | Location | Priority |
|-------|----------|----------|
| Managed | `.claude/agents/` in the managed settings directory | 1 (highest) |
| CLI | `--agents '<json>'` (session only) | 2 |
| Project | `.claude/agents/` | 3 |
| User | `~/.claude/agents/` | 4 |
| Plugin | `<plugin>/agents/` | 5 (lowest) |

> [!WARNING]
> Plugin agents ignore `hooks`, `mcpServers`, `permissionMode`, and `initialPrompt`. Copy the
> file into `.claude/agents/` if you need them.

---

## Validator

The skill bundles `scripts/validate-agent.py` (requires `pyyaml`):

```bash
python scripts/validate-agent.py .claude/agents/
```

It reports the silent-skip conditions, unknown and mis-cased fields with a "did you mean"
hint, invalid enum values, `tools` and `disallowedTools` conflicts, and fields ignored for
plugin agents.

---

## Reference files

| File | When the skill loads it |
|------|-------------------------|
| `references/frontmatter-reference.md` | Every field, allowed values, version requirements, `--agents` JSON, plugin restrictions |
| `references/tools-reference.md` | Tool names, removed and background tool sets, MCP patterns, `Agent(type)`, nesting limits |
| `references/troubleshooting.md` | Symptom-to-cause tables for load, tool, model, hook, MCP, memory, and delegation problems |
| `references/prompt-writing-guide.md` | Prompt body structure, `description` writing, anti-patterns |
| `references/read-only-agent-example.md` | Minimal read-only reviewer |
| `references/worktree-implementer-example.md` | Implementer with worktree isolation, hook, memory, and preloaded skill |

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill agent-creator-claudecode -g

# Install for Claude Code only
npx skills add CowboyLogic/ai-dev --skill agent-creator-claudecode --agent claude-code -g
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [Claude Code Settings Manager](client-config-claudecode.md) — permissions, hooks, and MCP
  in `settings.json`
- [Copilot Agent Creator](agent-creator-copilot.md) — the equivalent skill for GitHub Copilot
- [OpenCode Agent Creator](agent-creator-opencode.md) — the equivalent skill for OpenCode
- [Matrix Topology](../agents/matrix-topology.md) — a multi-agent system with a Claude mirror

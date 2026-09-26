# Copilot Agent Creator

Create custom agent profiles (`.agent.md` files) for GitHub Copilot across VS Code, the
Copilot CLI, and the Copilot cloud agent on GitHub.com. Covers the frontmatter schema with
per-surface compatibility, tool aliases and VS Code tool sets, model selection, handoffs,
subagents, hooks, and MCP servers.

- **Skill name:** `agent-creator-copilot`
- **Last updated:** 2026-09-25
- **Source:** [skills/agent-creator-copilot](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-copilot)

---

## What it does

A single agent profile can run on several Copilot surfaces, but many properties only work on
some of them — handoffs are ignored by the cloud agent, `model` takes display names in VS Code
and lowercase IDs in the CLI, and several fields are CLI-only. The skill gives an agent a
step-by-step workflow for planning, writing, and testing a profile, and loads detailed
reference material only when the task needs it.

**Topics covered:**

- Agent profile format — `description` is the only required property; the Markdown body is
  the prompt, capped at 30,000 characters
- Storage scope — repository, user, organization, enterprise, plugin, and Claude-format
  locations, plus name-conflict precedence
- Tools — portable aliases (`execute`, `read`, `edit`, `search`, `agent`, `web`, `todo`),
  MCP namespacing (`my-server/*`), and least-privilege defaults
- Model selection — display names versus IDs, fallback lists, and the retired-model table
- Handoffs, subagents, `user-invocable`, and `disable-model-invocation`
- CLI-only fields such as `include-custom-instructions`
- MCP server configuration and secrets for the cloud agent
- Writing effective prompts and descriptions

**Where profiles live:**

| Scope | Location | Surfaces |
|-------|----------|----------|
| Repository / workspace | `.github/agents/<name>.agent.md` | All |
| Repository (Claude format) | `.claude/agents/<name>.md` | VS Code, Copilot CLI |
| User | `~/.copilot/agents/` | VS Code, Copilot CLI |
| User (Claude format) | `~/.claude/agents/` | VS Code |
| Organization | `agents/<name>.md` in the org's `.github` or `.github-private` repo | GitHub.com, IDEs |
| Enterprise | `agents/<name>.md` in a designated org's `.github-private` repo | GitHub.com, IDEs |
| Plugin | `<plugin>/agents/` | Copilot CLI |

> [!WARNING]
> The Copilot CLI docs disagree on whether a user-level or project-level agent wins when
> names collide. Avoid duplicate agent names across scopes.

---

## Reference files

| File | When the skill loads it |
|------|-------------------------|
| `references/frontmatter-reference.md` | Full property tables, surface compatibility, model naming, handoffs, hooks, MCP config, CLI-only fields, Claude format |
| `references/tools-reference.md` | Tool aliases, VS Code tool sets, MCP namespacing, out-of-the-box MCP servers |
| `references/prompt-writing-guide.md` | Prompt principles, anti-patterns, output format guidance |
| `references/workspace-agent-example.agent.md` | VS Code workspace agent with handoffs and a model fallback list |
| `references/user-profile-agent-example.agent.md` | Minimal personal agent |
| `references/cloud-agent-with-mcp-example.agent.md` | GitHub.com cloud agent with inline MCP config and a `COPILOT_MCP_` secret |

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill agent-creator-copilot -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill agent-creator-copilot --agent copilot -g
```

### Using `gh copilot` (Copilot CLI only)

```bash
gh copilot skill install CowboyLogic/ai-dev/skills/agent-creator-copilot
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [Copilot Instruction Creator](copilot-instruction-creator.md) — repository, path, and
  personal instructions rather than agent personas
- [OpenCode Agent Creator](agent-creator-opencode.md) — the equivalent skill for OpenCode

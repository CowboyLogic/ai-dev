# Codex Configuration Manager

Manage OpenAI Codex CLI configuration from a single skill. Covers `config.toml` and the
project `.codex/` layer, sandbox and approval settings, permission profiles and rules,
MCP servers, hooks, skills, plugins, model providers, and `AGENTS.md` instructions.

- **Skill name:** `client-config-codex`
- **Source:** [skills/client-config-codex](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-codex)

---

## What it does

Codex configuration is TOML, changes often, and differs from the JSON-based clients an agent
is more likely to remember. Without this skill an agent answers from training data and
tends to invent keys or reuse another client's schema. The skill routes each task to the
reference material for the config area involved and loads only that material.

**Topics covered:**

- `config.toml` layers and precedence, profiles, and project trust
- Model, reasoning effort, and custom model providers
- Sandbox mode, approval policy, permission profiles, and `.rules` files
- MCP servers, hooks, skills, and plugins and marketplaces
- The `[agents]` table and where custom agents live (writing agent files is covered by
  [Codex Agent Creator](agent-creator-codex.md))
- `AGENTS.md` and `AGENTS.override.md` discovery
- Authentication, environment variables, and admin-enforced `requirements.toml`
- CLI subcommands, `-c` overrides, and sessions

The skill also bundles a script that shows the current configuration with secrets redacted,
and a script that refreshes its reference files from the upstream Codex documentation.

> [!IMPORTANT]
> The skill never reads or prints Codex credentials, and it asks before trusting a project
> or loosening the sandbox and approval settings.

## Where it applies

Use it when an agent edits or explains OpenAI Codex CLI configuration, global or per project.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill client-config-codex -g

# Install for Codex only
npx skills add CowboyLogic/ai-dev --skill client-config-codex --agent codex -g

# Preview what would be installed without installing
npx skills add CowboyLogic/ai-dev --skill client-config-codex -g -l
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [Codex Agent Creator](agent-creator-codex.md) — write custom Codex subagent files
- [Claude Code Configuration Manager](client-config-claudecode.md) — the equivalent skill for Claude Code
- [Copilot Configuration Manager](client-config-copilotcli.md) — the equivalent skill for GitHub Copilot CLI
- [OpenCode Configuration Manager](client-config-opencode.md) — the equivalent skill for OpenCode

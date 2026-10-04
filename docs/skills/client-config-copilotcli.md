# Copilot Configuration Manager

Manage all GitHub Copilot CLI configuration files from a single skill. Covers every
config file the Copilot CLI reads — trusted folders, user settings, MCP servers,
hooks, skills, custom agents, custom instructions, BYOK models, authentication,
and session management.

- **Skill name:** `client-config-copilotcli`
- **Source:** [skills/client-config-copilotcli](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-copilotcli)

---

## What it does

Without this skill, an agent answers Copilot CLI configuration questions from training
data alone, which can predate recent features and contain incorrect field names for
several config files. The skill loads authoritative reference material for the exact
config file the task requires, rather than loading everything at once.

It covers the CLI's global and project-level configuration, including settings, MCP and
LSP servers, hooks, skills, custom agents, plugins, custom instructions, bring-your-own-key
providers, and session management. It also bundles a script that shows the current
configuration.

## Where it applies

Use it when an agent edits or explains GitHub Copilot CLI configuration, in any client
that loads skills.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill client-config-copilotcli -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill client-config-copilotcli --agent copilot -g

# Preview what would be installed without installing
npx skills add CowboyLogic/ai-dev --skill client-config-copilotcli -g -l
```

### Using `gh copilot` (Copilot CLI only)

```bash
gh copilot skill install CowboyLogic/ai-dev/skills/client-config-copilotcli
```

### Verify installation

```bash
# List globally installed skills
npx skills ls -g

# Filter by agent
npx skills ls -g --agent copilot
```

---

## Evaluation and history

In a benchmark run on 2026-04-26, the skill raised the assertion pass rate from 30% to
100%, with the largest gains on session management and bring-your-own-key setup. The
detail is in the [skill README](https://github.com/CowboyLogic/ai-dev/blob/main/skills/client-config-copilotcli/README.md),
and the version history is in the
[CHANGELOG](https://github.com/CowboyLogic/ai-dev/blob/main/skills/client-config-copilotcli/CHANGELOG.md).

---

## Related

- [Claude Code Configuration Manager](client-config-claudecode.md) — the equivalent skill for Claude Code
- [OpenCode Configuration Manager](client-config-opencode.md) — the equivalent skill for OpenCode
- [Codex Configuration Manager](client-config-codex.md) — the equivalent skill for Codex
- [Copilot Agent Creator](agent-creator-copilot.md) — write custom Copilot agent profiles

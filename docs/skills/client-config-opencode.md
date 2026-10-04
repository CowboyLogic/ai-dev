# OpenCode Configuration Manager

Manage all opencode configuration files from a single skill, for both OpenCode V2 and V1.
Covers the full surface of `opencode.json` plus the terminal client config (`cli.json` in V2,
`tui.json` in V1) — providers, MCP servers, agents, permissions, plugins, keybinds, themes,
formatters, commands, instructions, compaction, and enterprise settings.

- **Skill name:** `client-config-opencode`
- **Source:** [skills/client-config-opencode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-opencode)

---

## What it does

Without this skill an agent answers opencode configuration questions from training data alone.
For provider-specific settings, the permission schema, and MCP transport details, the baseline
produces configurations that look plausible but are structurally wrong. The skill loads
targeted reference material only for the config area the task requires.

It reads any existing config first to tell V1 from V2, uses native V2 for new configuration,
and keeps a V1-shaped file in V1 unless asked to migrate. It also bundles a script that shows
the current configuration.

## Where it applies

Use it when an agent edits or explains OpenCode configuration, global or per project, on V2
or V1. For writing custom agent files, see
[OpenCode Agent Creator](agent-creator-opencode.md).

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill client-config-opencode -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill client-config-opencode --agent <agent> -g

# Preview what would be installed without installing
npx skills add CowboyLogic/ai-dev --skill client-config-opencode -g -l
```

### Verify installation

```bash
npx skills ls -g
```

---

## Evaluation and history

In a benchmark run on 2026-04-26, the skill raised the assertion pass rate from 67% to
100%, with the largest gains on the permission model and provider configuration. The
detail is in the [skill README](https://github.com/CowboyLogic/ai-dev/blob/main/skills/client-config-opencode/README.md),
and the version history is in the
[CHANGELOG](https://github.com/CowboyLogic/ai-dev/blob/main/skills/client-config-opencode/CHANGELOG.md).

---

## Related

- [OpenCode Agent Creator](agent-creator-opencode.md) — write custom OpenCode agents
- [Claude Code Configuration Manager](client-config-claudecode.md) — the equivalent skill for Claude Code
- [Copilot Configuration Manager](client-config-copilotcli.md) — the equivalent skill for GitHub Copilot CLI
- [Codex Configuration Manager](client-config-codex.md) — the equivalent skill for Codex

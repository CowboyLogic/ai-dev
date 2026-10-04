# Claude Code Configuration Manager

Manage all Claude Code configuration files from a single skill. Covers every scope
the Claude Code CLI reads — user settings, project settings, permissions, hooks,
MCP servers, model configuration, sandbox isolation, auto mode, voice, and plugins.

- **Skill name:** `client-config-claudecode`
- **Source:** [skills/client-config-claudecode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-claudecode)

---

## What it does

Without this skill an agent answers Claude Code configuration questions from training
data alone. For well-established settings that is usually accurate, but for settings
that have changed since training it can confidently describe the old shape and deny
that the newer fields exist. The skill loads authoritative reference material only for
the config area the task requires, rather than injecting the full schema on every
request.

It covers settings at every scope Claude Code reads, from user and project files to
command-line options and managed settings, and the subagent files that sit alongside
them. It also bundles scripts that show and validate the current configuration.

## Where it applies

Use it in Claude Code sessions where an agent edits `settings.json`, permissions, hooks,
MCP servers, or related configuration. The workflow centers on `settings.json` files.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill client-config-claudecode -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill client-config-claudecode --agent claude-code -g

# Preview what would be installed without installing
npx skills add CowboyLogic/ai-dev --skill client-config-claudecode -g -l
```

### Verify installation

```bash
# List globally installed skills
npx skills ls -g

# Filter by agent
npx skills ls -g --agent claude-code
```

---

## Evaluation and history

In a benchmark run on 2026-04-26, the skill raised the assertion pass rate from 80% to
100%, with the gain concentrated on settings that postdate the model's training. The
detail is in the [skill README](https://github.com/CowboyLogic/ai-dev/blob/main/skills/client-config-claudecode/README.md),
and the version history is in the
[CHANGELOG](https://github.com/CowboyLogic/ai-dev/blob/main/skills/client-config-claudecode/CHANGELOG.md).

---

## Related

- [Claude Code Agent Creator](agent-creator-claudecode.md) — write custom Claude Code subagent files
- [Copilot Configuration Manager](client-config-copilotcli.md) — the equivalent skill for GitHub Copilot CLI
- [OpenCode Configuration Manager](client-config-opencode.md) — the equivalent skill for OpenCode
- [Codex Configuration Manager](client-config-codex.md) — the equivalent skill for Codex

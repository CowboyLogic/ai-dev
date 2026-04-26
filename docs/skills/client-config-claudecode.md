# Claude Code Settings Manager

Manage all Claude Code configuration files from a single skill. Covers every scope
the Claude Code CLI reads — user settings, project settings, permissions, hooks,
MCP servers, model configuration, sandbox isolation, auto mode, voice, and plugins.

- **Skill name:** `client-config-claudecode`
- **Last updated:** 2026-04-26
- **Source:** [skills/client-config-claudecode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-claudecode)

---

## What it does

Without this skill an agent answers Claude Code configuration questions from training
data alone. For stable, well-established settings (hooks, permissions) the baseline
is accurate. For settings that have changed since training — such as the `voice` object
replacing the deprecated `voiceEnabled` boolean — the baseline defaults to the old
shape and confidently tells the user the newer fields don't exist.

The skill loads authoritative reference material only for the config area the task
requires, rather than injecting the full schema on every request.

**Config scopes covered:**

| Scope | File | Notes |
|-------|------|-------|
| User | `~/.claude/settings.json` | Primary focus |
| Local project | `.claude/settings.local.json` | Gitignored |
| Project | `.claude/settings.json` | Committed |
| Managed (macOS) | `/Library/Application Support/ClaudeCode/managed-settings.json` | IT-deployed |
| Managed (Linux/WSL) | `/etc/claude-code/managed-settings.json` | IT-deployed |
| Managed (Windows) | `C:\Program Files\ClaudeCode\managed-settings.json` | IT-deployed |

**Scope precedence (highest → lowest):** managed → local project → project → user

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

## Evaluation results

Benchmark run: **2026-04-26 · iteration 1** · 3 scenarios · 6 total runs

### Overall

| | With skill | Baseline (no skill) | Delta |
|---|---|---|---|
| Assertions passed | 15 / 15 | 12 / 15 | — |
| Pass rate | **100%** | **80%** | **+20 pp** |

### By scenario

| Scenario | With skill | Baseline | Delta | Notes |
|---|---|---|---|---|
| Lint hook on file edit/write (`PostToolUse`, `Edit\|Write`, `$CLAUDE_PROJECT_DIR`) | 5 / 5 | 5 / 5 | 0% | Well-established; both answered correctly |
| Git read-allow / destructive-deny (`Bash()` rule syntax, deny precedence) | 5 / 5 | 5 / 5 | 0% | Baseline has accurate permissions knowledge |
| Voice dictation + model (`voice` object, tap mode, `autoSubmit`) | 5 / 5 | 2 / 5 | +60% | Baseline used deprecated `voiceEnabled: true`; stated `voice.mode` and `voice.autoSubmit` do not exist |

> [!NOTE]
> This skill has marginal but measurable value when used with Claude models. For well-established
> configuration areas (hooks, permissions), the baseline is already reliable. Value increases for
> settings that postdate the model's training cutoff.

### Key takeaway

For Claude Code's established configuration surface (hooks structure, `Bash()` permission
rules), the baseline model is already reliable — the skill reinforces rather than corrects.
The gap opens on settings that have changed since training: the baseline defaults to the
deprecated `voiceEnabled: true` boolean, asserts the `voice` object sub-fields don't exist,
and confidently gives the user a configuration that will behave differently than expected.
The skill closes this gap entirely.

> [!TIP]
> **When does this skill matter most?** Any time a user asks about voice dictation
> settings, or any other Claude Code feature that postdates the model's training cutoff.
> The skill reference reflects the current schema; the baseline cannot.

---

## Changelog

### 2026-04-26 — v1.0 (initial release)

- `SKILL.md`: Full task-to-reference map covering all config areas; quick-edit snippets
  for common operations; helper scripts listed (`show-settings.py`, `validate-settings.py`).
- `references/settings-schema.md`: Complete `~/.claude/settings.json` schema covering
  Model & Performance, Auto Mode, UI & Display, Session & Behavior, Environment, Plugins,
  Subagents, Sandbox, and Misc/Enterprise sections. Documents `voice` object (replaces
  deprecated `voiceEnabled`), `effortLevel`, `alwaysThinkingEnabled`, `outputStyle`,
  `statusLine`, `teammateMode`, and all other current keys.
- `references/hooks.md`: Full hooks event table (23 events), matcher pattern rules,
  handler types (`command`, `http`), env vars available in hook context, and complete
  examples for PreToolUse/PostToolUse/Stop.
- `references/permissions.md`: `Bash()`, `Read()`, `Edit()`, `WebFetch()`, `mcp__*`,
  and `Agent()` rule syntax with glob semantics; all `defaultMode` values; common
  pattern library for dev workflows.
- `references/mcp.md`: MCP server config in `~/.claude/settings.json` mcpServers block;
  transport types; credential handling via `$VAR_NAME` env references.

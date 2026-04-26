# Copilot CLI Configuration Manager

Manage all GitHub Copilot CLI configuration files from a single skill. Covers every
config file the Copilot CLI reads — trusted folders, user settings, MCP servers,
hooks, skills, custom agents, custom instructions, BYOK models, authentication,
and session management.

- **Skill name:** `client-config-copilotcli`
- **Last updated:** 2026-04-26
- **Copilot CLI version tested:** v1.0.35 / v1.0.36
- **Source:** [skills/client-config-copilotcli](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-copilotcli)

---

## What it does

Without this skill, an agent answers Copilot CLI configuration questions from
training data alone — which predates the v1.0.35 feature additions and contains
incorrect field names for several config files. The skill loads authoritative
reference material for the exact config file the task requires, rather than loading
everything at once.

**Config files covered:**

| What | File | Scope |
|------|------|-------|
| Trusted folders | `~/.copilot/config.json` | Global |
| User settings | `~/.copilot/settings.json` | Global |
| MCP servers | `~/.copilot/mcp-config.json` | Global |
| Hooks | `.github/hooks/hooks.json` | Project |
| Skills | `~/.copilot/skills/<name>/SKILL.md` | Global personal |
| Custom agents | `~/.copilot/agents/<name>.agent.md` | Global personal |
| Custom instructions | `~/.copilot/copilot-instructions.md` | Global personal |
| Path-scoped instructions | `.github/instructions/*.instructions.md` | Project |

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

## Evaluation results

Benchmark run: **2026-04-26 · iteration 1** · 4 scenarios · 8 total runs

### Overall

| | With skill | Baseline (no skill) | Delta |
|---|---|---|---|
| Assertions passed | 20 / 20 | 6 / 20 | — |
| Pass rate | **100%** | **30%** | **+70 pp** |

### By scenario

| Scenario | With skill | Baseline | Delta | Notes |
|---|---|---|---|---|
| Add PostgreSQL MCP server | 5 / 5 | 4 / 5 | +20% | Baseline used wrong field name (`allowedTools` → `tools`) and omitted `type` field |
| HTTP audit hook (shell events only) | 6 / 6 | 2 / 6 | +67% | Baseline invented event name, wrong file path, wrong filter field, missing `version` field |
| Session naming + auto-switch (`--name`, `--resume`, `continueOnAutoMode`) | 4 / 4 | 0 / 4 | +100% | Baseline stated these features don't exist |
| BYOK Anthropic Claude Opus (`COPILOT_PROVIDER_*` env vars) | 5 / 5 | 0 / 5 | +100% | Baseline used wrong env vars and a non-existent `settings.json` model block |

### Key takeaway

The two largest gaps — session management and BYOK — are features added in
v1.0.35 that postdate the model's training data. The baseline doesn't give partial
answers for these; it confidently tells the user the features don't exist. The
skill closes that gap entirely.

---

## Changelog

### 2026-04-26 — v1.1 (iteration 1 feedback)

- `references/mcp.md`: All credential examples converted from hardcoded values
  to `$VAR_NAME` shell environment variable references. Added explanation of
  `$VAR` resolution pattern (values resolved from user shell env at load time).
  PostgreSQL example: credential moved from positional `args` to `env` block.

### 2026-04-26 — v1.0 (initial update to v1.0.35/v1.0.36)

- `SKILL.md`: Added `settings.json` to config file map; added session management
  triggers (`--name`, `--resume`); removed non-existent `validate-config.py` script reference.
- `references/config-schema.md`: New `settings.json` section (`continueOnAutoMode`);
  added `COPILOT_GH_HOST` env var; new Sessions section with `--name`/`--resume` flags
  and `/session delete*` commands; added `/keep-alive`, `/remote`, `/session delete`
  slash commands.
- `references/hooks.md`: Documented `http` hook type alongside `command`; added
  `matcher` field; full HTTP hook example; v1.0.36 full-match fix note.
- `references/skills.md`: Removed `.claude/skills/` from project locations;
  added deprecation warning — `~/.claude/` no longer loaded by Copilot CLI v1.0.36.
- `references/mcp.md`: Added OAuth note; documented server name quoting for
  names containing spaces or special characters.

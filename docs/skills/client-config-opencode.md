# OpenCode Configuration Manager

Manage all opencode configuration files from a single skill. Covers the full surface
of `opencode.json` and `tui.json` — providers, MCP servers, agents, permissions, keybinds,
themes, formatters, commands, instructions, compaction, LSP, and enterprise settings.

- **Skill name:** `client-config-opencode`
- **Last updated:** 2026-04-26
- **Source:** [skills/client-config-opencode](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-opencode)

---

## What it does

Without this skill an agent answers opencode configuration questions from training data alone.
For provider-specific env var names, the opencode permission schema, and MCP transport
details (such as timeout units), the baseline fabricates configurations that look plausible
but are structurally wrong or use incorrect identifiers. The skill loads targeted reference
material only for the config area the task requires.

**Config files covered:**

| File | Scope | What it controls |
|------|-------|-----------------|
| `~/.config/opencode/opencode.json` | Global | Providers, MCP, agents, permissions, commands, formatters, compaction, server, LSP |
| `opencode.json` (project root) | Project | Same as global — merges with global config |
| `~/.config/opencode/tui.json` | Global | Theme, keybinds, mouse, diff style, plugins |
| `~/.config/opencode/agents/<name>.md` | Global | Custom agent definitions (markdown format) |
| `.opencode/agents/<name>.md` | Project | Project-scoped custom agents |
| `~/.config/opencode/commands/<name>.md` | Global | Custom slash command definitions |
| `.opencode/commands/<name>.md` | Project | Project-scoped custom commands |
| `~/.local/share/opencode/auth.json` | Global | OAuth credentials (CLI-managed, not hand-edited) |

**Merge behavior:** all config files are merged — later configs only override conflicting keys.

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

## Evaluation results

Benchmark run: **2026-04-26** · 4 scenarios · 8 total runs

### Overall

| | With skill | Baseline (no skill) | Delta |
|---|---|---|---|
| Assertions passed | 24 / 24 | 16 / 24 | — |
| Pass rate | **100%** | **67%** | **+33 pp** |

### By scenario

| Scenario | With skill | Baseline | Delta | Notes |
|---|---|---|---|---|
| Remote MCP server with OAuth + timeout (`sentry`, `type: remote`, `oauth` omit for auto, `timeout: 10000`) | 6 / 6 | 5 / 6 | **+17 pp** | Baseline set `timeout: 10` (seconds) instead of `10000` (ms); also used a non-existent `auth.type` schema for OAuth |
| GitLab Duo self-hosted provider (`GITLAB_INSTANCE_URL` env var, `{env:}` syntax, `provider` key) | 5 / 5 | 2 / 5 | **+60 pp** | Baseline used wrong top-level key (`providers` not `provider`), wrong env syntax (`env:VAR` not `{env:VAR}`), and embedded `apiBase` in config instead of using `GITLAB_INSTANCE_URL` env var |
| Custom read-only subagent (JSON + markdown format, `permission` schema, `mode`, temperature) | 8 / 8 | 4 / 8 | **+50 pp** | Baseline fabricated an entirely wrong schema: `agents` (plural), `type: subagent` instead of `mode: subagent`, and `tools.x: bool` instead of `permission.x: allow/deny` |
| Keybind leader key + disable (`tui.json`, `keybinds.leader`, empty string to disable) | 5 / 5 | 5 / 5 | 0 pp | Non-discriminating — TUI keybind config is generic enough that both configurations scored perfectly |

### Key takeaway

The baseline fails most on opencode-specific schema details that cannot be inferred from
general training data. Three patterns account for the +33 pp gap:

- **Permission model** — opencode uses `permission.x: "allow"/"deny"` (string values, singular
  `permission` key); the baseline consistently invents `tools.x: bool` or similar.
- **Provider config schema** — `{env:VAR}` substitution syntax, the singular `provider` key,
  and `GITLAB_INSTANCE_URL` as an env var (not an `apiBase` config field) are all
  opencode-specific and get wrong without the reference.
- **MCP transport details** — `timeout` is in milliseconds; the baseline treats it as seconds.

The one area where the skill adds no value in these evals is TUI keybind configuration —
both configurations scored perfectly on the keybind scenario, suggesting that test is
non-discriminating and should be replaced in a future iteration.

> [!TIP]
> **When does this skill matter most?** Any task touching the `permission` schema, provider
> configuration (especially newer providers like GitLab Duo, Helicone, llama.cpp), MCP
> transport options, or schema fields added after the model's training cutoff (LSP config,
> `tool_output`, `compaction.tail_turns`, command template syntax).

---

## Changelog

### 2026-04-26 — v1.0 (initial release)

- `SKILL.md`: Full task-to-reference map; common quick-edit snippets; `tool_output` quick
  edit added; deprecation callout for `autoshare` → `share`, `maxSteps` → `steps`,
  `tools` → `permission`.
- `references/providers.md`: Added GitLab Duo, Helicone, llama.cpp (distinct from LM Studio),
  and OpenRouter sections. Added comprehensive model fields reference table (family, status,
  modalities, reasoning, variants, timeout, interleaved). Added `whitelist`/`blacklist` model
  filtering section. Added `enterpriseUrl` provider option.
- `references/tui.md`: Added `leader` key documentation. Added `app_exit` action. Expanded
  keybind tables to cover all actions: input editing (`input_*`), terminal controls
  (`terminal_suspend`, `title_toggle`, `tips_toggle`), model/agent (`model_provider_list`,
  `variant_cycle`, `model_reverse`, `agent_reverse`), and UI (`plugin_manager`,
  `display_thinking`, `tool_details`). Added `plugin` and `plugin_enabled` fields to TUI
  options table. Added `[!TIP]` callout for Shift+Enter terminal configuration.
- `references/config-schema.md`: Added `enterprise` field to core fields table. Noted
  `autoshare` and `layout` as deprecated. Added `lsp` section with full field reference.
  Added `tool_output` section (max_lines, max_bytes). Updated `compaction` with `tail_turns`
  and `preserve_recent_tokens` fields. Expanded commands section with full template syntax
  table (`$ARGUMENTS`, `$1`/`$2`, shell injection with `` !`cmd` ``, `@file` includes).
  Expanded built-in formatters list (25 formatters including `oxfmt`, `uv`, `zig`, `gleam`,
  `ktlint`, `nixfmt`, and others).
- `references/agents.md`: Added `compaction`, `title`, and `summary` system agents to
  built-in agents table. Added `task` permission example with glob patterns and explanation.
- `evals/evals.json`: Created 4 eval cases covering MCP remote OAuth, GitLab Duo provider,
  custom read-only agent, and keybind configuration.

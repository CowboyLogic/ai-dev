# Gemini CLI Configuration Manager

Manages `settings.json`, `GEMINI.md`, hooks, MCP servers, extensions, custom commands, themes, and trusted folders for Google's Gemini CLI. Use this skill whenever configuring any aspect of Gemini CLI — from switching models and themes to wiring up MCP servers, defining hooks, and enabling experimental features like voice mode and auto-memory.

- **Skill name:** `client-config-geminicli`
- **Last updated:** 2026-04-26
- **Source:** [skills/client-config-geminicli](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-geminicli)

---

## What it does

Gemini CLI's `settings.json` has grown significantly — it now has 14 top-level sections, many with renamed or restructured fields. Without the skill, an agent may give outdated field paths or miss entire sections entirely.

The skill covers every config file and scope:

| File | Scope | Purpose |
|------|-------|---------|
| `~/.gemini/settings.json` | User | Personal defaults — model, theme, tools, MCP |
| `.gemini/settings.json` | Project | Project overrides (requires trusted folder) |
| `~/.gemini/GEMINI.md` | User | Global context injected into every session |
| `GEMINI.md` | Project | Project context (hierarchical discovery) |
| `~/.gemini/commands/*.toml` | User | Global custom slash commands |
| `.gemini/commands/*.toml` | Project | Project custom slash commands |

**Key sections covered in `settings.json`:**
`general` · `ui` · `output` · `model` · `tools` · `security` · `context` · `mcpServers` · `agents` · `advanced` · `experimental` · `skills` · `hooksConfig` · `ide` · `billing`

**Important correct behaviors the skill enforces:**

- Uses `general.defaultApprovalMode` (not the old `general.approvalMode`)
- Knows YOLO mode is **CLI-only** (`--yolo` flag) — cannot be set in `settings.json`
- Uses `context.fileFiltering.*` sub-paths (not old flat `context.respectGitignore`)
- Knows the `experimental` section: voice mode, auto-memory, Gemma 4, memoryV2, worktrees, model steering
- Knows `hooksConfig.enabled` as the master hooks on/off toggle
- Knows `security.disableYoloMode`, `security.toolSandboxing`, `security.environmentVariableRedaction`

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all sessions
npx skills add CowboyLogic/ai-dev --skill client-config-geminicli -g

# Install for a specific agent
npx skills add CowboyLogic/ai-dev --skill client-config-geminicli --agent <agent> -g

# Preview installation without applying
npx skills add CowboyLogic/ai-dev --skill client-config-geminicli -g -l
```

### Verify installation

```bash
npx skills ls -g
```

### Using `gh copilot` (fallback — GitHub CLI required)

```bash
gh copilot skill add CowboyLogic/ai-dev/client-config-geminicli
```

---

## Evaluation results

Benchmark run: **2026-04-26 · iteration 1** · 4 scenarios · 8 total runs (clean re-run)

Model: Claude Sonnet 4.6. Methodology: without-skill subagents received the raw user question only — no skill content, no schema hints. With-skill subagents received the question plus explicit SKILL.md quick-edits and relevant `settings-schema.md` sections injected in the prompt. All subagents were stateless fresh invocations.

### Overall

| | With skill | Baseline (no skill) | Delta |
|---|---|---|---|
| Assertions passed | 16 / 16 | 3 / 16 | — |
| Pass rate | **100%** | **18.75%** | **+81.25 pp** |

### By scenario

| Scenario | With skill | Baseline | Delta | Baseline failure mode |
|---|---|---|---|---|
| `approval-mode-rename` | 4/4 100% | 1/4 25% | +75 pp | Used old `approvalMode` flat field; wrong nesting |
| `yolo-cli-only` | 4/4 100% | 1/4 25% | +75 pp | Wrongly showed YOLO settable in `settings.json` |
| `voice-mode-enable` | 4/4 100% | 0/4 0% | +100 pp | Stated voice mode does not exist in Gemini CLI |
| `context-filtering-paths` | 4/4 100% | 1/4 25% | +75 pp | Wrong nesting (`fileFiltering.*` not `context.fileFiltering.*`); `ui.fuzzyFileSearch` instead of `context.fileFiltering.enableFuzzySearch` |

### Key takeaway

The skill provides a **meaningful correctness lift** on all four scenarios. Baseline failures cluster around:

1. **Schema renames** — `approvalMode` → `general.defaultApprovalMode`; `context.*` flat fields → `context.fileFiltering.*` sub-object
2. **Behavioral changes** — YOLO mode moved to CLI-only; cannot be set in `settings.json`
3. **New experimental features** — `experimental.voiceMode` is entirely unknown to the baseline; it states the feature does not exist

---

## Changelog

### 2026-04-26 — v2 (schema sync)

- `references/settings-schema.md`: full rewrite to match current upstream schema
  - Renamed `general.approvalMode` → `general.defaultApprovalMode`; removed YOLO from settable modes
  - Renamed `general.autoUpdate` → `general.enableAutoUpdate`, `notifications` → `enableNotifications`
  - Renamed `general.sessionCleanup` → `general.sessionRetention` (with `.enabled` and `.maxAge`)
  - Renamed `general.planMode` → `general.plan.{enabled,directory,modelRouting}`
  - Added `general.topicUpdateNarration`, `retryFetchErrors`, `maxAttempts`
  - Updated `ui` section: all `show*` fields renamed to `hide*` (inverted), new fields for footer, accessibility, rendering
  - Updated `model` section: `contextCompression` → `model.compressionThreshold`, `loopDetection` → `model.disableLoopDetection`; default `maxSessionTurns` is now `-1`
  - Updated `tools` section: renamed shell fields, added `sandboxAllowedPaths`, `useRipgrep`, `truncateToolOutputThreshold`, `disableLLMCorrection`
  - Updated `security` section: `conseca` → `security.enableConseca`; new `toolSandboxing`, `disableYoloMode`, `disableAlwaysAllow`, `enablePermanentToolApproval`, `autoAddToPolicyByDefault`, `blockGitExtensions`, `environmentVariableRedaction.enabled`
  - Updated `context` section: all file-filter fields moved to `context.fileFiltering.*` sub-object
  - Updated `advanced` section: `nodeMemoryAutoConfig` → `advanced.autoConfigureMemory`
  - Added `experimental` section: `voiceMode`, `voice.*`, `gemma`, `gemmaModelRouter.*`, `memoryV2`, `autoMemory`, `generalistProfile`, `contextManagement`, `worktrees`, `modelSteering`, `directWebFetch`, `useOSC52*`
  - Added `output`, `billing`, `ide`, `agents`, `skills`, `hooksConfig` sections
- `references/hooks.md`: added `hooksConfig` global enable/disable section at top
- `references/context.md`: added `/memory inbox` command; updated context settings to `fileFiltering.*` sub-paths
- `SKILL.md`: updated quick edits (YOLO CLI-only note, new voice and autoMemory snippets, `hooksConfig` disable snippet); updated task→reference map with new entries

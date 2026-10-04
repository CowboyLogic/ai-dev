# Copilot Configuration Manager

Evaluation results for the `client-config-copilotcli` skill. The skill itself is
[SKILL.md](SKILL.md), and its history is in [CHANGELOG.md](CHANGELOG.md).

## Evaluation results

Benchmark run: **2026-04-26 · iteration 1** · 4 scenarios · 8 total runs

These results predate the 2026-09-24 v2.0 refresh. The eval cases for this benchmark are not
stored in the skill folder.

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

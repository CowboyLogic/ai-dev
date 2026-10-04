# OpenCode Configuration Manager

Evaluation results for the `client-config-opencode` skill. The skill itself is
[SKILL.md](SKILL.md), and its history is in [CHANGELOG.md](CHANGELOG.md).

## Evaluation results

Benchmark run: **2026-04-26** · 4 scenarios · 8 total runs

These results predate the 2026-09-24 v2.0 refresh, which pinned these cases to V1 in
[evals/evals.json](evals/evals.json) and added three V2 cases.

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

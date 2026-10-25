# Claude Code Configuration Manager

Evaluation results for the `client-config-claudecode` skill. The skill itself is
[SKILL.md](SKILL.md), and its history is in [CHANGELOG.md](CHANGELOG.md).

> [!NOTE]
> **Claude Code version:** verified against [Claude Code 2.1.310](https://github.com/anthropics/claude-code/releases/tag/v2.1.310)
> (released 2026-10-23; the npm `latest` and `next` tags on 2026-10-25, with `stable` at 2.1.308).
> References come from the `code.claude.com/docs` pages listed in
> [assets/sources.json](assets/sources.json), checked against the changelog through 2.1.310.
> Where only the changelog supports a claim, the reference says so. Last re-verified
> 2026-10-25. Re-verify when Claude Code ships a new release.

## Evaluation results

Benchmark run: **2026-04-26 · iteration 1** · 3 scenarios · 6 total runs

These results predate the 2026-09-24 v2.0 refresh, the 2026-10-11 v2.1 update, the
2026-10-13 v2.2 update, the 2026-10-14 v2.3 update, the 2026-10-18 v2.4 update, and the
2026-10-25 v2.5 update.
[evals/evals.json](evals/evals.json) holds the eval cases; it also includes five cases that
this run did not cover: `default-mode-scope` (added in v2.0), `hook-fail-closed` (added in
v2.1), `stop-hook-loop-cap` (added in v2.2), `idle-compaction` (added in v2.3),
`mcp-server-name-with-double-underscore` (added in v2.4), and
`user-or-managed-keys-in-project-settings` (added in v2.5).

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

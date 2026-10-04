# Changelog

Changes to the `client-config-claudecode` skill, newest first.

## 2026-09-24 — v2.0 (upstream refresh)

- Sources: the full key reference moved upstream to `settings-reference.md`; it is now
  the primary source for `references/settings-schema.md`. `assets/sources.json` gains
  `additional_urls` (settings, managed settings, subagents, permission modes, skills,
  managed MCP).
- `references/settings-schema.md`: rewritten against all documented keys with per-key
  scope labels, a files-and-precedence section, and a deprecated/removed keys section.
  Adds `modelSettings`, `maxEffortLevel`, `promptCacheTtl`, `autoCompactWindow`,
  `enableWorkflows`, sandbox credential keys, and more. Corrects `effortLevel`,
  `ultracode`, and `voice.autoSubmit` behavior.
- `references/hooks.md`: adds `DirectoryAdded`, `PreModelSwitch`, `PostModelSwitch`,
  new matcher values, handler fields (`args`, `statusMessage`, `once`), and output
  fields; corrects `PermissionRequest` and `WorktreeRemove` blocking behavior.
- `references/permissions.md`: adds `Skill()` rules, tool-name globs, `manual` mode
  alias, and project/local restrictions on `auto` and `bypassPermissions`.
- `references/mcp.md`: local-scope servers live under `projects["<path>"].mcpServers`
  in `~/.claude.json`; adds `ws` transport, per-server `timeout`, `headersHelper`,
  `alwaysLoad`; marks SSE deprecated.
- Scripts: `validate-settings.py` checks keys by scope, all hook events and handler
  types, and deprecated keys; `show-settings.py` gains `--settings` and shows managed
  and local-scope MCP configuration.
- Evals: new eval for project-scope `bypassPermissions` being ignored.

## 2026-04-26 — v1.0 (initial release)

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

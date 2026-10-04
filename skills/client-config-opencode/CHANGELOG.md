# Changelog

Changes to the `client-config-opencode` skill, newest first.

## 2026-09-24 — v2.0 (OpenCode V2 support)

- `SKILL.md`: rewritten with a format-selection step (read first; no file → V2; V1-shaped
  file stays V1), a V1/V2 detection signals table, and side-by-side file and task maps.
- New `references/v2/`: `config-schema.md`, `permissions.md` (ordered `permissions` rules),
  `agents.md`, `mcp.md` (`mcp.servers`, snake_case OAuth, split timeouts), `providers.md`,
  `cli.md` (`cli.json` and a `tui.json` → `cli.json` key map), `plugins.md` (new
  `Plugin.define` API), and `migration.md`.
- V1 references refreshed and labelled V1. Corrections: `server` settings nest under a
  `server` object; Anthropic Pro/Max login is no longer supported; formatters and LSP are
  off unless configured and use a `$FILE` placeholder; the `task` permission governs
  subagent launches; keybinds are disabled with `"none"` or `false`.
- `sources.json`: V2 doc URLs, the `v2/cli.json` schema, and additional V1 pages.
- `scripts/show-config.py`: JSONC parsing, `.opencode/opencode.json(c)` and `cli.json`
  support, and V1/V2/mixed format detection.
- `evals/evals.json`: existing cases pinned to V1; three V2 cases added (MCP OAuth,
  reviewer agent permissions, `cli.json` keybinds).

## 2026-04-26 — v1.0 (initial release)

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

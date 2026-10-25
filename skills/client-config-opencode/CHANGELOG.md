# Changelog

Changes to the `client-config-opencode` skill, newest first.

## 2026-10-25 — v2.4 (verified against V2 2.1.4 and V1 1.19.4)

Baselines: V2 2.0.29 → 2.1.4 (401 commits; 51 docs pages changed); V1 1.19.0 → 1.19.4. Sources are the
tag-to-tag diff `v2.0.29...v2.1.4` of the V2 docs source (`services/www/src/docs/content`) and the config
schema/core source, the V2 `CHANGELOG.md` (the 2.1.4 notes come from `dev`, since the tag's own copy lags), the
published `config.json` and `cli.json` schemas, and the V1 1.19.0..1.19.4 release notes and source. Unlike the last
two updates, the **2.1.4 binary was run**: `--help` output for the CLI commands and `{file:...}` substitution in an
agent `system` field were checked on it.

- `references/v2/permissions.md`: **docs correction, not a behavior change.** The base policy has no
  `external_directory` rule (identical in 2.0.29 and 2.1.4; upstream commit `20d172e462` fixed the docs), so
  access outside the project is allowed by default, and `explore` allows shell and external directories. Earlier
  versions of this skill listed an `ask` rule from the older docs. Added `opencode_list_mcp_resources` and
  `opencode_read_mcp_resource` actions, the effect of denying `execute`, and `todowrite` (only with
  `experimental.todo`).
- `references/v2/config-schema.md`: `config.json` now accepts the V1 and native V2 shape (the "V1-only" notes are
  gone); `instructions` loads files, globs, and URLs (2.0.30); `share` is inert (sharing was removed in 2.0.30);
  compaction `buffer` default is 15% (at least 16k), summaries cover the whole conversation,
  `agents.compaction.model`, and `experimental.background_compaction`; new Experimental section (`todo`,
  `subagent_depth`, `portable_shell_scanner`, `background_compaction`, `location_idle_timeout`); nested skill
  directories; `OPENCODE_DISABLE_CLAUDE_CODE*`, `OPENCODE_DISABLE_FREE_MODELS`; `{env:}` / `{file:}` are documented.
- `references/v2/mcp.md`: OAuth client registration order (pre-registered, CIMD, DCR); MCP resources, server
  instructions, and elicitation forms; `mcp.timeout` scope; `opencode mcp auth` without a name.
- `references/v2/plugins.md`: configured local plugin paths must be directories; `ctx.permission.assert` details;
  build-API changes between 2.0.29 and 2.1.4 (the `native` replay-data rename, `metadata`, paginated
  `session.list`, and others); `effect@4.0.1` and OpenTUI 0.6 peer ranges.
- `references/v2/agents.md`: agent files using V2-only fields are read as V2 (2.1.4); `request.body` is still not
  sent; the `build` and `explore` descriptions match the source.
- `references/v2/cli.md`: unknown settings and keybind IDs are ignored; `diffs.fullscreen`; new keybind command
  IDs; `/diff` opens docked; the TUI-tools experiment; theme `faint` token.
- `references/v2/providers.md`: `capabilities.reasoning`, `releaseDate`, `streamUsage`, the ChatGPT sign-in
  context caps and how to disable them, `OPENCODE_DISABLE_FREE_MODELS`, the Bedrock `mantle/messages` package; the
  docs now agree on the 15-minute chunk timeout.
- `references/v2/migration.md`: `instructions` loads; `autoshare` has no V2 equivalent; V1 `external_directory`
  prompted but V2 does not; the `temperature` / `top_p` mapping points at model variants; `upgrade --major` is a V1
  option (not in the 2.1.4 `upgrade --help`).
- V1 references: `reasoning_options` model config (1.19.3); sharing discontinued in 1.19.1 (`share`, `autoshare`,
  `/share`, `session_share`).
- `SKILL.md`: the instructions row, schema note, `{file:}` note, model IDs, and three new quick edits.
- Not changed: `references/mcp.md`, `references/agents.md`, `references/permissions.md` (V1; no related V1 docs
  changes in 1.19.0..1.19.4 beyond `zen.mdx`).

## 2026-10-14 — v2.3 (verified against V2 2.0.29 and V1 1.19.0)

Baselines: V2 2.0.27 → 2.0.29 (108 commits; 11 docs pages changed); V1 1.19.0 is unchanged. Sources are
the tag-to-tag diff `v2.0.27...v2.0.29` of the V2 docs source and the config schema/core source, the V2
`CHANGELOG.md` (2.0.28 at the 2.0.29 tag, 2.0.29 on `dev`), and the published `cli.json` schema. The
2.0.29 binary was **not** run, so binary-dependent claims keep their 2.0.27 basis.

- `references/v2/permissions.md`: policies live under top-level `policies` (2.0.29); `experimental.policies`
  still works and merges in. The `permission` policy action in earlier versions of this skill is not a valid
  value in the 2.0.27 or 2.0.29 schema; the actions are `provider.use`, `tool.use`, and `integration.use`.
  Documented `integration.use` (`mcp:`, `skill:`, `plugin:` resources) and the full policy precedence
  table (Console, macOS managed preferences, system directory, global, project).
- `references/v2/config-schema.md`: system configuration directory (macOS, Linux, Windows) and macOS managed
  preferences with highest precedence; the "MDM managed settings are V1-only" note no longer applies to those
  two. Added the top-level `policies` row. Re-baselined unchanged docs claims to 2.0.29.
- `references/v2/providers.md`: new Compatibility section (provider-level `compatibility`, the full field list
  from the schema, `cacheFormat` for Claude models behind OpenAI-compatible proxies); new Request encoding
  section (`settings.encoding`); streamed-chunk timeout default is 15 minutes since 2.0.28 (the docs page still
  says five).
- `references/v2/cli.md`: top-level `highlights` boolean in `cli.json` (release highlights dialog, `/highlights`).
- `references/v2/plugins.md`: `ctx.credential.activate` and `ctx.permission.assert`.
- `references/v2/migration.md`: `enabled_providers` / `disabled_providers` map to `policies`; V1
  `options.setCacheKey` maps to `compatibility.supportsPromptCacheKey`; the V2 CLI source defines no
  `upgrade --major` option.
- `SKILL.md`: system/managed row in the file map and the `policies` quick edit.
- `sources.json`: `covers` text for the permissions, config, and providers references.
- Not changed: V1 references (no V1 release since 1.19.0), `references/v2/agents.md`, and `references/v2/mcp.md`
  (their docs pages are identical between 2.0.27 and 2.0.29).

## 2026-10-12 — v2.2 (verified against V2 2.0.27 and V1 1.19.0)

Baselines: V2 2.0.26 → 2.0.27; V1 1.19.0 is unchanged (no V1 release since 2026-10-11). V2 now
publishes release notes in the repository's `CHANGELOG.md`, so this update uses them together with a
tag-to-tag diff of the V2 docs source, the published `cli.json` schema, and the 2.0.27 binary. The
notes for 2.0.26 first appeared in that file after the 2.0.26 tag.

- `references/v2/permissions.md`: the tools page lists Code Mode worktree utilities
  (`worktree_create`, `worktree_list`, `worktree_remove`); `worktree_remove` requests `edit` with the
  worktree directory as its resource, and the other two request no built-in permission action.
- `references/v2/cli.md`: `session.verbosity` (`low` | `medium` | `high`) is in the published
  `cli.json` schema but not on the V2 settings page; `FORCE_HYPERLINK=1` forces OSC 8 hyperlinks when
  terminal detection does not enable them (2.0.26 release notes).
- `references/v2/providers.md`: `/connect` → Vertex offers Google Cloud credentials (gcloud auth or
  environment) since 2.0.26; ADC honors `CLOUDSDK_CONFIG` since 2.0.27.
- `references/v2/config-schema.md`: `opencode pair --remote` asks for confirmation the first time it
  enables remote access, and `--yes` accepts for non-interactive use; the remote URL is a persistent
  random subdomain and a new one is issued when remote access is turned off and on again.
- `references/v2/plugins.md`: Effect plugins declare `effect` as a `peerDependency`, now
  `^4.0.0` in the docs (was `>=4.0.0-rc.112`).
- Re-verified on 2.0.27: `{file:...}` substitution in agent `system` (`opencode debug config`),
  `opencode auth export` and `auth import` appear in `auth --help` but not in the V2 docs, `opencode
  upgrade --help` has no `--major`, and `permission.mode`, `plugins.install`, and
  `dialog.plugins.install` are still absent from the published `cli.json` schema.
- `sources.json`: added the V2 CLI `commands` and `web` pages, the Effect plugin page, and the V2
  `CHANGELOG.md`.
- Not changed: the V1 references, and the V2 agents and MCP references (their docs pages are identical
  between 2.0.26 and 2.0.27).

## 2026-10-11 — v2.1 (verified against V2 2.0.26 and V1 1.19.0)

Baselines: V2 2.0.16 → 2.0.26 and V1 1.18.29 → 1.19.0. V2 publishes no release notes, so V2
changes come from a tag-to-tag diff of the V2 docs source, the published `cli.json` schema, and the
2.0.26 binary. V1 changes come from the 1.19.0 release notes and a tag-to-tag diff of the V1 docs.

- V1 `references/config-schema.md`: `autoupdate` now only checks and notifies; updates are never
  installed automatically (`/update` or `opencode upgrade` installs). The published JSON schema
  description still says `true` auto-updates, and the note says so.
- `references/v2/cli.md`: `diffs.source` accepts `turn`; `prompt.queue` is `<leader>return` and
  `input.newline` also accepts `alt+return`; added `queued_prompt.undo`, `theme.switch`, and
  `terminal.toggle`; the `permission.mode`, `plugins.install`, and `dialog.plugins.install` keybind IDs
  are no longer in the docs or schema.
- `references/v2/config-schema.md`: compaction `buffer` defaults to 10% of the limit (the 2.0.16
  docs said `20000`); skill frontmatter gains `disable-model-invocation` and drops `slash` and
  `metadata.opencode/slash` from the docs; formatter `{}` preserves inherited settings while `true`
  resets them; `tinyfish` web search provider; `opencode service set disabled true`.
- `references/v2/providers.md`: provider-wide `headerTimeout`, `chunkTimeout`, and `timeout`
  (defaults and retry behavior); Azure deployment discovery and `resourceName` precedence;
  `opencode auth export` and `auth import` (in `--help`, not in the docs).
- `references/v2/migration.md`: V1 `autoupdate: true` maps to `update: "auto"`, which is more
  aggressive than V1 1.19.0; compaction `reserved` carries over only when set explicitly.
- `references/v2/plugins.md`: the V1 object entrypoint is supported in `1.18.29` and newer.
- `references/v2/migration.md`: noted that the V1 1.19.0 docs list `opencode upgrade --major`, which
  upgrades to OpenCode 2 and removes OpenCode 1.
- `{file:...}` substitution in agent `system` re-verified on 2.0.26 with `opencode debug config`.
- `sources.json`: added the V2 CLI index page, which documents the background service.

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

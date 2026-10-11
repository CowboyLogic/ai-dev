# Changelog

Changes to the `client-config-claudecode` skill, newest first.

## 2026-10-11 — v2.1 (verified against Claude Code 2.1.296)

Basis: Claude Code 2.1.296 (npm `latest`; `stable` is 2.1.287), docs pages fetched with
`scripts/update-references.py --all`, and the changelog for 2.1.282–2.1.296.

- `references/settings-schema.md`: adds `availableModelsMatch` and `deniedModels` (v2.1.283),
  `allowedProviders` (v2.1.285), `maxProseWidth` and `allowClaudeInChromeWithManagedMcp`
  (v2.1.282), `prependPlugins` / `appendPlugins`, `bashEditDiffEnabled`,
  `awaySummaryEnabled`, and the global-config keys `claudeInChromeDefaultEnabled`,
  `copyFullResponse`, `defaultToAgentsView`, `leftArrowOpensAgents`, and
  `prStatusFooterEnabled`. `forceLoginGatewayUrl` is now *User or managed*: v2.1.295 also
  reads it, and `forceLoginMethod: "gateway"`, from user settings on a machine with no managed
  settings.
- `references/hooks.md`: adds `onFailure: "block"` (v2.1.295) with the failures it covers and
  the events it doesn't, multi-line async JSON (v2.1.295), the full Elicitation
  accept/decline/cancel contract and the v2.1.284 `decision: "block"` fix, `CLAUDE_ENV_FILE`
  in PowerShell commands (v2.1.296), the v2.1.296 hook duration debug lines, and
  `updatedMCPToolOutput`.
- `references/permissions.md`: adds which permission mode a session starts in (`auto` for
  terminal and VS Code from v2.1.283; `-p`/SDK rules from v2.1.285) and the v2.1.292
  network-path read behavior.
- `references/mcp.md`: adds a tool loading, limits, and runtime section: `alwaysLoad: false`
  (v2.1.287), per-tool `anthropic/alwaysLoad`, `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH`,
  `/mcp reconnect all` (v2.1.284), `MCP_SDK_GENERATION`, and `MCP_PROTOCOL_NEGOTIATION`.
  Claims the docs pages don't yet carry (4,096-character default, 16,384-character search
  cut, 16 MiB WebSocket limit, `bareElicitationCapability`, reserved `widgets` name) are
  labeled as changelog-only.
- `scripts/validate-settings.py`: corrects `forceLoginGatewayUrl` scope (was managed-only);
  adds the new managed-only, user-or-managed, any-file, and global-config keys; validates
  hook `onFailure` (value, handler type, events where it has no effect).
- `SKILL.md`: quick edits for the default mode and a fail-closed hook; the self-update
  procedure now records the Claude Code version checked.
- Evals: new eval for making a hook fail closed with `onFailure`; not yet run (the README
  results predate it).

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

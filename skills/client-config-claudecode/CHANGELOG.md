# Changelog

Changes to the `client-config-claudecode` skill, newest first.

## 2026-10-18 — v2.4 (verified against Claude Code 2.1.302)

Basis: Claude Code 2.1.302 (released 2026-10-16; npm `latest` and `next`, `stable` is
2.1.292), the 2.1.300–2.1.302 changelog, and the `code.claude.com/docs` pages fetched
2026-10-18. Claims only the changelog supports are labeled "changelog only" in the references.

- `references/permissions.md`: an MCP allow rule for a server whose name contains `__` or ends
  in `_` is now documented upstream, so it is no longer labeled changelog only (deny and ask
  rules still are); adds the auto mode classifier model (Sonnet 5 by default, with the fallbacks
  the permission-modes page lists); changelog only: `CLAUDE_CODE_AUTO_MODE_MODEL` (v2.1.302),
  server-side auto mode compacting a conversation too long for its safety check (v2.1.302), and
  `claude -p`/Agent SDK sessions now starting in `default` on third-party providers, with
  telemetry off, or on a fresh install (v2.1.302; the docs table still shows the earlier rule).
- `references/hooks.md`: the `prompt`/`agent` hook `model` default is now worded as the docs
  give it (the model used for background functionality). Changelog only: agent hooks honor
  `model` (v2.1.300), at most 12 prompt/agent hooks of one event run at once (v2.1.302),
  `updatedInput` from `PreToolUse`/`PermissionRequest` hooks is validated (v2.1.300), a
  `setMode` update in a `PermissionRequest` allow is ignored in Cowork cloud sessions
  (v2.1.300), and plugin `WorktreeCreate`/`WorktreeRemove` hooks run with `--worktree`
  (v2.1.300).
- `references/mcp.md`: adds the MCP docs page's rules for root-level `anyOf`/`oneOf`/`allOf`
  schemas, invalid input schemas, and tool names over 128 characters; changelog only: a tool
  whose schema the API still rejects is sent without parameters for the rest of the
  conversation (v2.1.300).
- `references/settings-schema.md`: `advisorModel` notes `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` and
  that the changelog adds `/advisor` on Claude Platform on AWS (v2.1.300) where the settings
  reference still lists it as unavailable; `idleCompaction` notes the `/config` row (v2.1.302,
  changelog only).
- Checked and unchanged: all 245 rows of the settings reference index are in the references and
  the validator; every hook event in the hooks docs is covered; the Google Vertex AI page
  claims hold.
- Evals: new `mcp-server-name-with-double-underscore` eval; not yet run (the README results
  predate it).

## 2026-10-14 — v2.3 (verified against Claude Code 2.1.299)

Basis: Claude Code 2.1.299 (released 2026-10-14; npm `latest` and `next`, `stable` is
2.1.287), the 2.1.297–2.1.299 changelog (no 2.1.297 or 2.1.298 release exists on npm), and the
docs pages fetched with `scripts/update-references.py --all`.

- `references/settings-schema.md`: adds `idleCompaction` (v2.1.290+; the docs page documents
  it, the earlier references lacked it) with its conditions and the
  `CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS` threshold; adds a "Variables Claude Code ignores in
  `env`" section for project and local settings, which includes the new
  `CLAUDE_CODE_DISABLE_FILE_MENTIONS` (v2.1.299).
- `references/hooks.md`: `PreCompact`/`PostCompact` `auto` matcher also covers idle
  compaction; changelog-only v2.1.299 notes that Windows hooks with no `shell` fail closed
  when Git for Windows is missing, plan mode no longer runs a write a `PreToolUse` hook
  allowed, and `UserPromptSubmit` hooks run before a skill or custom command expands; a
  skill's own `UserPromptSubmit` frontmatter hook first runs on the following prompt.
- `references/permissions.md`: changelog-only note that an MCP allow rule `mcp__a` no longer
  reaches a server named `a__b` or `a_`, and that deny and ask rules now apply to servers
  whose normalized name contains `__`.
- `scripts/validate-settings.py`: `idleCompaction` is a known any-file key; warns on an `env`
  entry Claude Code drops: the always-ignored identity and `*_RM_*` variables in any file, and
  the project/local list in project and local settings (a value that turns telemetry off
  still applies, so it isn't flagged).
- Checked and unchanged: every row of the settings reference index other than
  `idleCompaction` is already in the references and validator.
- Evals: new `idle-compaction` eval; not yet run (the README results predate it).

## 2026-10-13 — v2.2 (verified against Claude Code 2.1.296)

Basis: Claude Code 2.1.296, still the npm `latest` and GitHub release; `stable` is 2.1.287.
No release has shipped since the v2.1 update, so this pass compared the live docs pages
and changelog against the references and validator and filled the gaps it found.

- `references/hooks.md`: adds the common hook input fields every event receives on stdin
  (`session_id`, `prompt_id`, `transcript_path`, `cwd`, `scratchpad_dir`, `permission_mode`,
  `effort`, `hook_event_name`, `agent_id`, `agent_type`) and `$CLAUDE_EFFORT`; the 8-continuation
  cap on `Stop`/`SubagentStop` hooks and `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`; the `SessionEnd`
  1.5 s budget, how a per-hook `timeout` raises it (up to 60 s), and
  `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`; `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` in the hook
  environment; and how `Notification` `permission_prompt` behaves under the Agent SDK
  `canUseTool` callback (`CLAUDE_CODE_DISABLE_PERMISSION_PROMPT_NOTIFY_HOOKS`).
- `references/settings-schema.md`: adds `worktree.location`, the Desktop SSH worktree folder
  (user scope only; ignored by `--worktree`, `EnterWorktree`, isolated subagents, and
  background sessions).
- `scripts/validate-settings.py`: validates `worktree.location` (absolute path or `~/`) and
  warns when it appears in project, local, or managed settings.
- Checked and unchanged: every settings key and scope label in the settings reference index,
  and all 33 hook events, match the references and validator.
- Evals: new eval for the stop-hook continuation cap; not yet run (the README results predate
  it).

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
  hook `onFailure` (value, handler type, events where it has no effect), the
  `availableModelsMatch`, `allowedProviders`, and `maxProseWidth` values, and reports a
  wrong-typed value (a list or object where a string is expected) as an error instead of
  raising `TypeError`.
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

# Changelog

Changes to the `client-config-copilotcli` skill, newest first.

## 2026-10-25 — v2.6 (refresh to Copilot CLI v1.0.103)

Basis: GitHub Copilot CLI **v1.0.103** (released 2026-10-22), the latest stable release on
2026-10-25: the GitHub releases "latest" and the npm `latest` dist-tag both point to it.
v1.0.104-0 through v1.0.104-3 are prereleases and are not covered. There is no stable v1.0.99
release; its notes come from the v1.0.99-0 to v1.0.99-2 prereleases and are repeated in the
v1.0.100 notes. Claims were checked against the published docs.github.com pages (fetched through
the article API on 2026-10-25) and the v1.0.99 to v1.0.103 release notes. Items found only in
release notes are labeled as such in the references.

- `references/cli-commands.md`: `--sync-session[=on|off]`; `--disable-client-telemetry`;
  `--no-remote` is removed, and `--remote-export` and `--no-remote-export` are renamed to
  `--sync-session=on` and `--sync-session=off`; `--remote` no longer works for interactive or `-p`
  startup (use `/remote on`) and remains only for legacy SDK server startup with `--server` or
  `--headless`; `/share` with no subcommand opens a menu
  and `link` does the sharing; `/session cleanup`; `/extensions mode`; team-assigned plugin
  defaults under `/plugin list`; `/agent` creates an agent with `N`; ACP sessions honor
  saved sandbox settings and `--sandbox`/`--no-sandbox`.
- `references/config-schema.md`: `remoteSessions` replaces the old `remote` key in the settings
  reference, and `remoteExport` semantics changed; `showReasoning`; managed
  `requireBase64ImageAttachments`; `telemetry.headersProvider` (user and managed) with a new
  "Dynamic authentication headers" section; `assistedApprovalInstructions` (release notes only,
  type unverified).
- `references/permissions.md`: the sandbox's upstream-proxy selection (`HTTPS_PROXY`,
  `HTTP_PROXY`, `ALL_PROXY`) and `NO_PROXY` behavior. Records an unresolved conflict: the v1.0.99
  release notes say local network access is allowed by default, but the settings reference still
  lists `allowLocalNetwork` as `false`.
- `references/mcp.md`: LSP `bash`, `powershell`, and `cwd` launch fields, `command` is no longer
  required, plus the `initializationTimeoutMs`, `spawnTimeoutMs`, and `warmupTimeoutMs` fields;
  managed `serverName` allowlist character set.
- `references/agents-plugins.md`: creating an agent with `N`; release-notes-only items for
  the `search`/`web`/`todo` tool aliases, `ghapp://` plugin install links, and `git-subdir`
  marketplace sources.
- `references/skills.md`: release-notes-only `allowed-tools` comma handling.
- `SKILL.md`: quick operations for `--sync-session` and `--disable-client-telemetry`.
- `sources.json`: added the v1.0.99-0 to v1.0.103 release pages and the ACP, session, and remote
  control pages; updated `covers`.
- `README.md`: Copilot CLI v1.0.103 basis and 2026-10-25 refresh date.
- Reviewed and not carried into the references: docs commits that only moved or reworded pages
  (the Copilot IA "customizations" concepts reorganization moved the concept pages for custom
  agents, skills, hooks, MCP, plugins, and LSP servers to `concepts/customizations/`; the local
  sandbox concept page moved to `security-governance-and-network-settings`), and release-note
  fixes that change no configuration surface (Gemini and Windows fixes, MCP loading, and similar).
- Not done: the benchmark in `README.md` was not re-run, and the CLI itself was not run, because the
  npm release-age guard blocks installing a version this new.

## 2026-10-18 — v2.5 (documentation refresh, Copilot CLI v1.0.98 still the basis)

Basis: GitHub Copilot CLI **v1.0.98** (released 2026-10-14). It is still the latest stable
release on 2026-10-18: the GitHub releases "latest" and the npm `latest` dist-tag both point to
it, and the v1.0.99 and v1.0.100 tags are prereleases, so they are not covered. No CLI release
notes changed; this refresh covers the github/docs Copilot CLI content commits made after the
2026-10-14 pass (`02b43700` and `bab62c42`, 2026-10-16). Each claim was checked against the
current docs.github.com source.

- `references/cli-commands.md`: `/ask` and `/btw` take an optional question, render Markdown, and
  reopen the last answer when called with none (the `Ctrl+E` and `Ctrl+Y` answer shortcuts were
  labeled release-notes-only and are now documented); `/sandbox enable session` and
  `/sandbox disable session`; `--trust-folder` added to the permissions option list.
- `references/permissions.md`: `--trust-folder` semantics under "Trusted directories" (one new
  non-interactive session, not saved to `trustedFolders`, no permission grant, managed policy
  still applies, incompatible with `--resume`, `--continue`, and `--session-id`); the `/sandbox`
  dialog's General tab has separate session and default-for-new-sessions options.
- `references/hooks.md`: hooks that fire inside a subagent also receive `agentId`, `agentType`,
  and `parentAgentId` (snake_case equivalents for the PascalCase format).
- `references/instructions.md`: path-specific rules at the repository root and in the working
  directory are delivered automatically when the agent reads or edits a matching file.
- `sources.json`: added the programmatic reference and the side-question how-to; updated the
  `covers` text; repointed two source URLs that now redirect (the Copilot CLI overview moved to
  `concepts/copilot-surfaces/copilot-cli`, and the sandbox concepts page to
  `concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes`).
- `README.md`: refresh date and the statement that v1.0.98 is still the latest stable release.
- Reviewed and not carried into the references: the 2026-10-15 and 2026-10-16 github/docs commits
  that only moved or reworded pages (the Copilot CLI concepts audit repointed links to relocated
  autopilot, fleet, research, and rubber-duck pages; Copilot app download button and wording;
  Copilot surfaces entry points; a Gemini durable-cache link), none of which changes a CLI
  configuration surface.
- Not done: the benchmark in `README.md` was not re-run.

## 2026-10-14 — v2.4 (refresh to Copilot CLI v1.0.98)

Basis: GitHub Copilot CLI **v1.0.98** (released 2026-10-14, the latest stable release; the
v1.0.99 tag is a prerelease); previous refresh covered v1.0.96. Documentation changes were
identified from the github/docs commits to the Copilot CLI content since 2026-10-13, and each
claim was checked against the current docs.github.com page. The github/docs repository had no
further Copilot CLI content commits after the v1.0.97 pass. Items that appear only in the
github/copilot-cli v1.0.97 or v1.0.98 release notes are labeled as such.

- `references/hooks.md`: new "Agent-scoped hooks (CLI only)" section for the custom agent
  frontmatter `hooks` map (event names, per-platform commands, subagent `Stop`, trust, remote
  agents unsupported); `"ask"` from a `preToolUse` hook is denied in CLI autopilot mode.
- `references/agents-plugins.md`: `hooks` frontmatter field (noted as absent from the command
  reference's frontmatter table); marketplace and plugin fetches retry once with the signed-in
  GitHub token after an HTTPS authentication failure; the example agent uses the documented
  model ID `claude-sonnet-5.5`.
- `references/config-schema.md`: `forceRemoteSettingsRefresh` semantics (cached policy can't
  satisfy it, now also in the GitHub Copilot app, string value in registry and managed
  preferences); minimum client versions enforced by a managed `sandbox` key.
- `references/permissions.md`, `references/cli-commands.md`, `references/config-schema.md`,
  `references/agents-plugins.md`, `references/hooks.md`: v1.0.97 release-notes-only items,
  labeled in place: billed AI Credits in `/usage`, secret redaction in `--output-format json`,
  managed permission rules read-only in `/config`, `inlineImages` on by default without
  experimental mode, an invalid `config.json` entry no longer resets saved settings, agent
  discovery beyond 100 agents, `--plugin-dir` skills and agents in autocomplete, and plugin hooks
  after `--resume`.
- `references/cli-commands.md`: v1.0.98 release-notes-only `/ask` answer shortcuts (`Ctrl+E`, `Ctrl+Y`,
  reopen the last answer).
- `SKILL.md`: routing row mentions agent-scoped hooks.
- `sources.json`: added the enterprise managed settings reference; updated the `covers` text.
- `README.md`: associated Copilot CLI version and refresh date.
- Reviewed and not carried into the references (runtime fixes with no configuration surface):
  proxy `close_notify` handling, SCP remote parsing, Windows taskbar icon grouping, `view_range`
  timeline display, transcript selection, background-shell status, heap memory relief, MCP
  catalog refresh, `/user switch` layout, and the GitHub MCP toolset endpoint fix. From v1.0.98:
  command-hook completion under lost child-exit signals, `/mcp` status after split-view switches,
  resume handling of abandoned permission requests, and startup keystroke retention. Gemini 4 Argon
  support (v1.0.98) has no model ID in the command reference yet, so the model table is unchanged.
- Not done: the benchmark in `README.md` was not re-run.

## 2026-10-13 — v2.3 (refresh to Copilot CLI v1.0.96)

Basis: GitHub Copilot CLI **v1.0.96** (released 2026-10-12, the latest stable release; the
v1.0.97 tags are prereleases); previous refresh covered v1.0.95. Each claim comes from the current
docs.github.com documentation. Items that appear only in the github/copilot-cli v1.0.96 release
notes are labeled as such.

- `references/permissions.md`: new "Built-in safety checks" section (plan-mode enforcement,
  command safety analysis, environment-variable denylist, `web_fetch` SSRF protection) and
  sandbox tool-directory grants and a "Bypass and Windows details" subsection (bypass prompt behavior, Windows
  denial capture); `/add-dir` grants sandbox access for the session; the `/sandbox` dialog suggests
  secrets and masking hosts (v1.0.96).
- `references/config-schema.md`: new "OpenTelemetry monitoring" section (`COPILOT_OTEL_*` and
  `OTEL_*` variables, content capture); managed `sandbox`, `telemetry`, and `remoteControl`
  fields; `inlineImages`; model IDs are case-insensitive (v1.0.96).
- `references/cli-commands.md`: supported model IDs table from the command reference;
  `/model ... auto TIER`; `/release-notes`, `/collect-debug-logs`, and `/tuikit`.
- `references/hooks.md`: complete runtime-to-Claude tool-name mapping and matcher regex rules;
  cloud agent hook environment variables.
- v1.0.96 release-notes-only items, labeled in place: `/user list` authentication source,
  permission-decision attribution in the timeline, `/allow-all` during startup policy resolution.
- `SKILL.md`: routing rows for OpenTelemetry, the safety checks, and the model table.
- `README.md`: associated Copilot CLI version and refresh date.
- Not done: the benchmark in `README.md` was not re-run.

## 2026-10-12 — v2.2 (gap-fill against Copilot CLI v1.0.95)

Basis: GitHub Copilot CLI **v1.0.95** (released 2026-10-09), still the latest stable release; the
newer v1.0.96-0 through v1.0.96-2 tags are prereleases and were not used. The docs.github.com pages
listed in `sources.json` were re-fetched and compared with the references. None of those pages
changed in github/docs after 2026-10-09 (the last change, to the CLI command reference, predates
the previous refresh), so this pass fills gaps that refresh left. Each addition comes from the
current documentation.

- `references/cli-commands.md`: `/collect-debug-logs [file|gist|share] [PATH]` and its consent
  behavior, the `/release-notes` alias and arguments of `/changelog`, `/tuikit`, and a new
  OpenTelemetry monitoring section (activation conditions, environment variables, signals,
  content-capture warning, `nano_aiu` guidance).
- `references/permissions.md`: new built-in safety checks section (command safety analysis,
  environment variable denylist, `web_fetch` SSRF protection, plan mode limits) and the sandbox
  tool directory grants.
- `references/mcp.md`: private npm registry `args`, trust levels by source, the 1 MB stdio filter
  exception, and how the enterprise allowlist fingerprints servers.
- `references/hooks.md`: cloud agent execution environment (filesystem, working directory,
  environment variables, network, interactivity).
- `SKILL.md`, `sources.json`: reference map and `covers` entries updated for the additions.
- `README.md`: references-last-refreshed date.
- Not done: the benchmark in `README.md` was not re-run.

## 2026-10-11 — v2.1 (refresh to Copilot CLI v1.0.95)

Basis: GitHub Copilot CLI **v1.0.95** (released 2026-10-09); previous refresh covered
roughly v1.0.88. Each claim comes from the current docs.github.com documentation. Items that
appear only in the github/copilot-cli release notes are labeled as such.

- `references/permissions.md`: sandboxing section rewritten — command sandboxing is available to
  all users (v1.0.93 release notes); `allowLocalNetwork` default is `false`;
  `sandbox.userPolicy.filesystem.deniedPaths`, `sandbox.auth.git`/`gh`,
  `sandbox.credentials.envVars` masking, proxy settings, `/sandbox ca` and `copilot sandbox ca`,
  `--sandbox`/`--no-sandbox`, bypass semantics, and the managed floor. Added the managed
  `permissions.limitTo` domain boundary. Removed the "public preview" and "experimental-mode"
  labels on local sandboxing; only cloud sandboxing is documented as public preview.
- `references/config-schema.md`: user settings in `config.json` are ignored (v1.0.93 release
  notes); new keys `autoTier`, `connectors`, `ignoredSkillsLocations`, `terminalNotifications`,
  `worktreePathTemplate`, rubber-duck `autoInvoke`; managed keys; `TGREP_FILE_COUNT_THRESHOLD`;
  model-usage and BYOK examples updated. Removed `builtInAgents.*` keys and other claims the
  current documentation doesn't support.
- `references/cli-commands.md`: added `copilot config`, `copilot sandbox ca`,
  `copilot workflow run`, `--extension-sdk-path`, `/refine`, `/workflows`, `/downgrade`,
  `/clikit`, `/find`, `/sandbox ca`; dropped the "experimental" label on `/sandbox`.
- `references/mcp.md`: `oauthScopes`, the `timeout` floor, Entra/WorkIQ authentication, sandboxed
  stdio servers; release-notes-only items (`--mcp-github-auth`, config changes between turns,
  slash-containing tool filters) attributed.
- `references/hooks.md`: sandboxed-session behavior; `config.json` no longer read for hooks.
- `references/skills.md`: name character set, `ignoredSkillsLocations`, remote skills, added-root
  trust, plugin-qualified names.
- `references/agents-plugins.md`: resolved the user-vs-project agent precedence conflict (User >
  `.github/agents` > `.claude/agents` > added root > plugin > remote), agent ID derivation, built-in
  agent default models, agent communication, memory-write limits, subagent limits.
- `SKILL.md`: `copilot config` and `--sandbox` quick operations; corrected the `config.json`
  migration claim.
- `sources.json`: added the local-sandbox settings and cloud/local sandbox concept pages.
- `README.md`: records the associated Copilot CLI version.
- Not done: the benchmark in `README.md` was not re-run.

## 2026-09-24 — v2.0 (upstream refresh)

- Sources: docs are fetched as Markdown through the docs.github.com article API;
  `sources.json` adds the CLI command reference, configuration-directory reference,
  hooks reference, plugin reference, custom agents, BYOK, LSP, and permissions pages.
- `SKILL.md`: config file map expanded to repository/local settings,
  `permissions-config.json`, `lsp-config.json`, `providers.json`, plugins, and
  `.claude/` / `.agents/` project locations.
- `references/hooks.md`: rewritten — hook input arrives as JSON on stdin (not `$INPUT`),
  `preToolUse` returns `permissionDecision`, 14 events, `command`/`exec`/`http`/`prompt`
  entry types.
- `references/config-schema.md`: full `settings.json` key table and precedence,
  managed settings, environment variables, BYOK.
- New `references/permissions.md`, `references/cli-commands.md`, and
  `references/agents-plugins.md`.
- Removed unverifiable version-specific claims (v1.0.35/v1.0.36).
- `scripts/show-config.py`: covers the new config files and no longer prints
  `config.json` values, which can contain auth tokens.

## 2026-04-26 — v1.1 (iteration 1 feedback)

- `references/mcp.md`: All credential examples converted from hardcoded values
  to `$VAR_NAME` shell environment variable references. Added explanation of
  `$VAR` resolution pattern (values resolved from user shell env at load time).
  PostgreSQL example: credential moved from positional `args` to `env` block.

## 2026-04-26 — v1.0 (initial update to v1.0.35/v1.0.36)

- `SKILL.md`: Added `settings.json` to config file map; added session management
  triggers (`--name`, `--resume`); removed non-existent `validate-config.py` script reference.
- `references/config-schema.md`: New `settings.json` section (`continueOnAutoMode`);
  added `COPILOT_GH_HOST` env var; new Sessions section with `--name`/`--resume` flags
  and `/session delete*` commands; added `/keep-alive`, `/remote`, `/session delete`
  slash commands.
- `references/hooks.md`: Documented `http` hook type alongside `command`; added
  `matcher` field; full HTTP hook example; v1.0.36 full-match fix note.
- `references/skills.md`: Removed `.claude/skills/` from project locations;
  added deprecation warning — `~/.claude/` no longer loaded by Copilot CLI v1.0.36.
- `references/mcp.md`: Added OAuth note; documented server name quoting for
  names containing spaces or special characters.

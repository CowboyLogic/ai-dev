# Changelog

Changes to the `client-config-copilotcli` skill, newest first.

## 2026-10-14 — v2.4 (refresh to Copilot CLI v1.0.97)

Basis: GitHub Copilot CLI **v1.0.97** (released 2026-10-13, the latest stable release; the
v1.0.98 tags are prereleases); previous refresh covered v1.0.96. Documentation changes were
identified from the github/docs commits to the Copilot CLI content since 2026-10-13, and each
claim was checked against the current docs.github.com page. Items that appear only in the
github/copilot-cli v1.0.97 release notes are labeled as such.

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
- `SKILL.md`: routing row mentions agent-scoped hooks.
- `sources.json`: added the enterprise managed settings reference; updated the `covers` text.
- `README.md`: associated Copilot CLI version and refresh date.
- Reviewed and not carried into the references (runtime fixes with no configuration surface):
  proxy `close_notify` handling, SCP remote parsing, Windows taskbar icon grouping, `view_range`
  timeline display, transcript selection, background-shell status, heap memory relief, MCP
  catalog refresh, `/user switch` layout, and the GitHub MCP toolset endpoint fix.
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

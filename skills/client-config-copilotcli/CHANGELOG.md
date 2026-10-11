# Changelog

Changes to the `client-config-copilotcli` skill, newest first.

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

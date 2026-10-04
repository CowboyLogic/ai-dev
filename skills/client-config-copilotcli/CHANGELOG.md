# Changelog

Changes to the `client-config-copilotcli` skill, newest first.

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

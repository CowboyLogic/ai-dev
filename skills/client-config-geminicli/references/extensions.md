# Extensions Reference

Extensions are packages that add tools, commands, hooks, themes, sub-agents, agent skills, and MCP servers to Gemini CLI. Loaded from `~/.gemini/extensions/` (project: `.gemini/extensions/`).

## CLI commands

| Command | Description |
|---------|-------------|
| `gemini extensions install <source> [--ref <ref>] [--auto-update] [--pre-release] [--consent] [--skip-settings]` | Install from a GitHub URL or local path (requires `git` for GitHub sources) |
| `gemini extensions uninstall <name...>` | Uninstall one or more extensions |
| `gemini extensions disable <name> [--scope user\|workspace]` | Disable (globally or per-workspace) |
| `gemini extensions enable <name> [--scope user\|workspace]` | Re-enable |
| `gemini extensions update <name>` / `--all` | Update to the version pinned in the manifest |
| `gemini extensions new <path> [template]` | Scaffold from a template (`mcp-server`, `context`, `custom-commands`) |
| `gemini extensions link <path>` | Symlink a local dev directory for live testing |
| `gemini extensions config <name> [setting] [--scope <scope>]` | Update an extension's `settings` values |
| `/extensions list` | View installed extensions from inside the CLI (install/uninstall are not supported in interactive mode) |

Installing copies the source — `gemini extensions update` is required to pull upstream changes. All management operations (including slash-command changes) take effect only after restarting the session.

## Directory structure

```
my-extension/
├── gemini-extension.json   # Manifest (required)
├── commands/               # Custom slash commands (.toml)
├── hooks/
│   └── hooks.json          # Extension-scoped hooks
├── agents/                 # Sub-agent definitions (.md)
├── skills/                 # Agent skill bundles
├── themes/                 # Custom themes
└── policies/               # Policy rules (.toml)
```

## Manifest: gemini-extension.json

```json
{
  "name": "my-extension",
  "version": "1.0.0",
  "description": "What this extension does",
  "contextFileName": "GEMINI.md",
  "excludeTools": ["run_shell_command"],
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${extensionPath}/server.js"],
      "cwd": "${extensionPath}"
    }
  },
  "settings": [
    {
      "name": "API Key",
      "description": "Service API key",
      "envVar": "MY_SERVICE_API_KEY",
      "sensitive": true
    }
  ],
  "themes": [
    {
      "name": "my-theme",
      "type": "custom",
      "background": { "primary": "#1e1e2e" },
      "text": { "primary": "#cdd6f4", "secondary": "#a6adc8", "link": "#89b4fa" },
      "status": { "success": "#a6e3a1", "warning": "#f9e2af", "error": "#f38ba8" },
      "border": { "default": "#585b70" },
      "ui": { "comment": "#6c7086" }
    }
  ]
}
```

## Manifest fields

| Field | Description |
|-------|-------------|
| `name` | Unique ID — lowercase, dash-separated; must match directory name |
| `version` | Semantic version string |
| `description` | Shown in extension marketplace |
| `contextFileName` | Context file to auto-load (default: `GEMINI.md`) |
| `excludeTools` | Tool names to block from model access. Supports command-specific restrictions, e.g. `"run_shell_command(rm -rf)"` blocks just that invocation |
| `mcpServers` | MCP server configurations (same format as `settings.json`, except `trust` is not supported) |
| `settings` | User-configurable values stored as env vars |
| `themes` | Custom theme definitions |
| `plan.directory` | Where planning artifacts are stored |
| `migratedTo` | URL — triggers auto-migration to new repo |

## Variable substitution in manifests

| Variable | Value |
|----------|-------|
| `${extensionPath}` | Absolute path to extension directory |
| `${workspacePath}` | Current workspace directory |
| `${/}` | Platform-specific path separator |

## Environment variable sanitization

Extensions do **not** inherit the user's full shell environment. They only get standard safe vars (`HOME`, `PATH`, `TMPDIR`) plus any `envVar` explicitly declared in the manifest's `settings` array — declare any API key, host, or config path your extension needs there so the CLI allowlists it.

## Settings configuration

`sensitive: true` stores the value in the system keychain rather than plain `.env`:

```json
{
  "settings": [
    {
      "name": "Database URL",
      "envVar": "DATABASE_URL",
      "sensitive": false
    },
    {
      "name": "Secret Token",
      "envVar": "SECRET_TOKEN",
      "sensitive": true
    }
  ]
}
```

## Extension management in settings.json

```json
{
  "security": {
    "blockGitExtensions": false,
    "allowedExtensions": ["my-trusted-extension-pattern.*"]
  }
}
```

`security.allowedExtensions` holds regex patterns; if non-empty, only matching extensions are allowed, and it overrides `blockGitExtensions`. For enterprise lockdown, `admin.extensions.enabled: false` disallows installing/using extensions entirely (see `references/settings-schema.md`).

Policy rules (in an extension's `policies/*.toml`) run in their own tier — higher priority than defaults, lower than user/admin policies — and the CLI ignores any `allow`/`yolo` decisions they contain, so an extension can never auto-approve its own tool calls.

## Conflict resolution

- Commands from extensions use dot notation to avoid conflicts: `/gcp.deploy`
- MCP servers in `settings.json` take precedence over extension-defined servers
- Project-scoped configuration overrides extension defaults

## Extension installation locations

- Global: `~/.gemini/extensions/`
- Project: `.gemini/extensions/`

Use `/extensions` CLI command to manage installed extensions.

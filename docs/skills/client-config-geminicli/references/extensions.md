# Extensions Reference

Extensions are packages that add tools, commands, hooks, themes, and MCP servers to Gemini CLI.

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
| `excludeTools` | Tool names to block from model access |
| `mcpServers` | MCP server configurations (same format as `settings.json`) |
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
    "allowedExtensions": ["my-extension", "other-extension"],
    "blockedExtensions": ["untrusted-extension"]
  }
}
```

## Conflict resolution

- Commands from extensions use dot notation to avoid conflicts: `/gcp.deploy`
- MCP servers in `settings.json` take precedence over extension-defined servers
- Project-scoped configuration overrides extension defaults

## Extension installation locations

- Global: `~/.gemini/extensions/`
- Project: `.gemini/extensions/`

Use `/extensions` CLI command to manage installed extensions.

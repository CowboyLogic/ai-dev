---
name: client-config-geminicli
description: Manage Gemini CLI configuration files — settings.json, GEMINI.md, hooks, MCP servers, extensions, custom commands, themes, and trusted folders. Use this skill whenever the user wants to view, edit, add, or understand any Gemini CLI setting: models, tools, permissions, MCP servers, hooks, custom commands, themes, trusted folders, context/memory, or sandboxing. Trigger on: "configure gemini cli", "add MCP server", "set model", "create hook", "add custom command", "change theme", "trust folder", "show gemini config", "add trusted folder", "configure sandbox", "set approval mode", or any request touching ~/.gemini/settings.json or .gemini/settings.json.
---

# Gemini CLI Configuration Skill

## Config file map

| File | Scope | Purpose |
|------|-------|---------|
| `~/.gemini/settings.json` | User | Personal defaults — model, theme, tools, MCP |
| `.gemini/settings.json` | Project | Project overrides (requires trusted folder) |
| `~/.gemini/GEMINI.md` | User | Global context/memory injected into every session |
| `GEMINI.md` | Project | Project context (hierarchical discovery up tree) |
| `~/.gemini/trustedFolders.json` | User | Trusted folder registry (managed by CLI) |
| `~/.gemini/commands/*.toml` | User | Global custom slash commands |
| `.gemini/commands/*.toml` | Project | Project custom slash commands |
| `~/.gemini/tmp/<hash>/shell_history` | User | Per-project shell history |

**Priority (lowest → highest):** system defaults → user → project → system overrides → env vars → CLI args

## Task → reference map

| Task | Read this file |
|------|---------------|
| View/edit any setting field | `references/settings-schema.md` |
| Add/configure MCP server | `references/mcp.md` |
| Create/edit hooks | `references/hooks.md` |
| GEMINI.md / context / memory | `references/context.md` |
| Custom commands | `references/commands.md` |
| Themes | `references/settings-schema.md` (ui section) |
| Trusted folders / security | `references/settings-schema.md` (security section) |
| Extensions | `references/extensions.md` |
| Show current config | run `python scripts/show-config.py` |

## Quick edits

**Set model:**
```json
{ "model": { "name": "gemini-2.5-pro" } }
```

**Set theme:**
```json
{ "ui": { "theme": "Tokyo Night" } }
```

**Set approval mode:**
```json
{ "general": { "approvalMode": "auto_edit" } }
```
Valid modes: `default` | `auto_edit` | `plan` | `yolo`

**Add MCP server (stdio):**
```json
{ "mcpServers": { "my-server": { "command": "npx", "args": ["-y", "@scope/server"], "env": {} } } }
```

**Enable trusted folders:**
```json
{ "security": { "folderTrust": { "enabled": true } } }
```

## Variable substitution in settings

String values support env var interpolation:
- `$VAR_NAME`
- `${VAR_NAME}`
- `${VAR_NAME:-default}` (with fallback)

## Self-update procedure

When upstream docs change:
1. Run `python scripts/update-references.py` — fetches all source URLs to `_fetched/`
2. Diff `_fetched/` content against each file in `references/`
3. Rewrite any reference file with stale information

Source manifest: `sources.json`

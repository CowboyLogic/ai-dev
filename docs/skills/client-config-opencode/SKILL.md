---
name: client-config-opencode
description: Manage opencode configuration files — opencode.json, tui.json, agents, MCP servers, providers, commands, and permissions. Use this skill whenever the user wants to view, edit, add, or understand any opencode setting: models, providers, MCP servers, agents, permissions, keybinds, themes, formatters, custom commands, or instructions. Trigger on: "configure opencode", "add provider", "set model", "add MCP server", "create agent", "configure permissions", "change theme", "add keybind", "show opencode config", "add custom command", or any request touching opencode.json or tui.json.
---

# opencode Configuration Manager

You help the user manage all opencode configuration files.

## Config file map

| What | File | Scope |
|------|------|-------|
| Core settings | `~/.config/opencode/opencode.json` | Global |
| Core settings | `opencode.json` (project root) | Project |
| TUI / keybinds / theme | `~/.config/opencode/tui.json` | Global |
| Agents | `~/.config/opencode/agents/<name>.md` | Global |
| Agents | `.opencode/agents/<name>.md` | Project |
| Commands | `~/.config/opencode/commands/<name>.md` | Global |
| Commands | `.opencode/commands/<name>.md` | Project |
| Auth / credentials | `~/.local/share/opencode/auth.json` | Global (managed by CLI) |

**Env overrides**: `OPENCODE_CONFIG` (custom config path), `OPENCODE_CONFIG_CONTENT` (inline JSON)

**Merge behavior**: All config files are **merged together**, not replaced. Later configs only override conflicting keys.

**Schema references**:
- Main config: `https://opencode.ai/config.json`
- TUI config: `https://opencode.ai/tui.json`

## Workflow

1. **Identify the task** → use the task-to-reference map below to load only what you need
2. **Read the target file first** before making any changes
3. **Edit safely** → use Edit for targeted changes; validate JSON after editing
4. **Confirm** → show the user exactly what changed

## Task → Reference map (load only what's needed)

| Task | Reference file |
|------|----------------|
| Providers, API keys, models | `references/providers.md` |
| MCP servers | `references/mcp.md` |
| Agents (built-in & custom) | `references/agents.md` |
| Permissions (tool access) | `references/permissions.md` |
| TUI, keybinds, themes | `references/tui.md` |
| Commands, instructions, misc | `references/config-schema.md` |
| Full schema / unknown field | `references/config-schema.md` |

## Common quick edits (no reference needed)

```jsonc
// Set default model
{ "model": "anthropic/claude-sonnet-4-5" }

// Set lightweight model for titles/summaries
{ "small_model": "anthropic/claude-haiku-4-5" }

// Share mode
{ "share": "manual" }    // "manual" | "auto" | "disabled"

// Auto-update
{ "autoupdate": true }   // true | false | "notify"

// Disable change tracking
{ "snapshot": false }

// Set default agent
{ "default_agent": "build" }

// Restrict to specific providers
{ "enabled_providers": ["anthropic", "openai"] }

// Disable a provider
{ "disabled_providers": ["bedrock"] }

// Log level
{ "logLevel": "INFO" }   // "DEBUG" | "INFO" | "WARN" | "ERROR"
```

## Variable substitution

Use in any string value:
- `{env:MY_API_KEY}` — environment variable
- `{file:~/.secrets/key.txt}` — file contents (supports `~` and relative paths)

## Scripts

- `scripts/show-config.py` — display all config files with annotations
- `scripts/update-references.py` — fetch latest upstream docs for self-update

Run with: `python scripts/<script>.py`

## Self-update procedure

When the user asks to **update**, **refresh**, or **sync** this skill:

1. Run `python scripts/update-references.py --all` → fetches docs to `_fetched/`
2. Read each `_fetched/` file alongside its corresponding `references/` file
3. Update `references/` files to reflect documentation changes
4. Delete `_fetched/` and report what changed

Source URLs are in `sources.json`.

## Safety rules

- Always read the file before editing
- Config files merge — editing global doesn't remove project overrides
- Don't touch `auth.json` directly — use `opencode auth` CLI commands
- Validate JSON/JSONC is well-formed after any edit
- For agent markdown files: preserve the YAML frontmatter structure

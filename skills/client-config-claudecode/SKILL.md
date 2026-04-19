---
name: client-config-claudecode
description: Manage and maintain Claude Code configuration files and settings. Use this skill whenever the user wants to view, edit, add, remove, or understand any Claude Code settings — permissions, hooks, MCP servers, environment variables, model settings, sandbox, auto mode, or any other configuration field. Trigger on: "add permission", "allow tool", "deny tool", "configure hook", "add MCP server", "change model", "update settings", "show my settings", "what settings do I have", or "set default mode".
---

# Claude Code Settings Manager

You help the user manage `~/.claude/settings.json` — their user-level Claude Code configuration that applies across all projects.

## Settings file locations (scope precedence: highest → lowest)

| Scope | File | Shared? |
|-------|------|---------|
| Managed | `/Library/Application Support/ClaudeCode/managed-settings.json` (mac) | IT-deployed |
| Local project | `.claude/settings.local.json` | No (gitignored) |
| Project | `.claude/settings.json` | Yes (git) |
| **User** | **`~/.claude/settings.json`** | No |

**This skill focuses on the User scope**: `~/.claude/settings.json`

## Workflow

1. **Read current settings first** — always read `~/.claude/settings.json` before making changes
2. **Identify the task** — use the task-to-reference map below to load only what you need
3. **Edit safely** — use the Edit tool for targeted changes; validate JSON after editing
4. **Confirm** — show the user the diff of what changed

## Task → Reference map (load only what's needed)

| Task | Reference file to read |
|------|------------------------|
| Add/remove allow, deny, ask rules | `references/permissions.md` |
| Configure hooks (PreToolUse, PostToolUse, etc.) | `references/hooks.md` |
| Add/configure MCP servers | `references/mcp.md` |
| Model, effort, thinking, output style | `references/settings-schema.md` §Model |
| Sandbox filesystem/network isolation | `references/settings-schema.md` §Sandbox |
| Auto mode classifier | `references/settings-schema.md` §AutoMode |
| Environment variables, attribution, misc | `references/settings-schema.md` §Misc |
| Unknown / full schema lookup | `references/settings-schema.md` |

## Common quick edits (no reference needed)

```jsonc
// Auto-updates channel
{ "autoUpdatesChannel": "stable" }          // or "latest" (default)

// Default permission mode
{ "permissions": { "defaultMode": "acceptEdits" } }
// valid: "default" | "acceptEdits" | "plan" | "auto" | "dontAsk" | "bypassPermissions"

// Response language
{ "language": "spanish" }

// Effort level
{ "effortLevel": "high" }  // "low" | "medium" | "high" | "xhigh"

// Show thinking summaries
{ "showThinkingSummaries": true }

// Disable all hooks (emergency)
{ "disableAllHooks": true }
```

## Scripts

For complex operations, use the helper scripts in `scripts/`:

- `scripts/show-settings.py` — pretty-print current settings across all scopes
- `scripts/validate-settings.py` — validate JSON structure and flag bad values
- `scripts/update-references.py` — fetch latest upstream docs (used during self-update)

Run with: `python scripts/<script>.py` from the skill directory, or with absolute paths.

## Self-update procedure

When the user asks you to **update**, **refresh**, or **sync** this skill with the latest Claude Code documentation, follow these steps:

1. **Fetch** — run `python scripts/update-references.py --all` (requires network access). This fetches each source URL listed in `sources.json` and saves raw content to `_fetched/`.

2. **Diff** — for each file in `_fetched/`, read it alongside the corresponding file in `references/`. Identify: new fields, removed fields, changed valid values, new examples, behavioral changes.

3. **Update** — rewrite each `references/*.md` file to reflect what changed. Preserve the existing structure and token-efficient style; add/remove/correct only what differs from the source.

4. **Validate** — run `python scripts/validate-settings.py` to confirm the schema knowledge is still coherent.

5. **Clean up** — delete the `_fetched/` directory.

6. **Report** — tell the user what changed (new keys added, deprecated fields, etc.).

### Source URLs (for manual lookup)

See `sources.json` for the full manifest. Key URLs:

| Reference file | Source URL |
|----------------|-----------|
| `references/settings-schema.md` | `https://code.claude.com/docs/en/settings.md` |
| `references/permissions.md` | `https://code.claude.com/docs/en/permissions.md` |
| `references/hooks.md` | `https://code.claude.com/docs/en/hooks.md` |
| `references/mcp.md` | `https://code.claude.com/docs/en/mcp.md` |
| Doc index | `https://code.claude.com/docs/llms.txt` |

## Safety rules

- Always read the file before editing
- Never remove fields you don't recognize without asking
- Keep a mental diff — tell the user exactly what changed
- If the file doesn't exist yet, create it with `{ "$schema": "https://json.schemastore.org/claude-code-settings.json" }` as the base
- Validate JSON is well-formed after any edit

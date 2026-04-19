---
name: client-config-copilotcli
description: Manage GitHub Copilot CLI configuration files — config.json, mcp-config.json, hooks.json, skills, and custom instructions. Use this skill whenever the user wants to view, edit, add, or understand any Copilot CLI setting: trusted folders, tool permissions, MCP servers, hooks, skills, BYOK models, authentication, or custom instructions. Trigger on: "add trusted folder", "allow tool", "configure MCP", "add hook", "create skill", "set model", "use my own API key", "add custom instructions", "show my copilot config", or any request touching ~/.copilot/ config files.
---

# GitHub Copilot CLI Configuration Manager

You help the user manage all GitHub Copilot CLI configuration files.

## Config file map

| What | File | Scope |
|------|------|-------|
| Trusted folders, core settings | `~/.copilot/config.json` | Global |
| MCP servers | `~/.copilot/mcp-config.json` | Global |
| Hooks | `.github/hooks/hooks.json` | Project (default branch) |
| Skills | `~/.copilot/skills/<name>/SKILL.md` | Global personal |
| Skills | `.github/skills/<name>/SKILL.md` | Project |
| Custom instructions | `~/.copilot/copilot-instructions.md` | Global personal |
| Custom instructions | `.github/copilot-instructions.md` | Project-wide |
| Path-specific instructions | `.github/instructions/*.instructions.md` | Project (glob-matched) |

**Config directory override**: Set `COPILOT_HOME` env var to use a different base directory.

## Workflow

1. **Identify the task** → use the task-to-reference map below to load only what you need
2. **Read the target file first** before making any changes
3. **Edit safely** → use the Edit tool for targeted changes; validate JSON after editing
4. **Confirm** → show the user exactly what changed

## Task → Reference map (load only what's needed)

| Task | Reference file |
|------|----------------|
| Trusted folders, core config.json | `references/config-schema.md` |
| Tool/path/URL permissions (CLI flags) | `references/config-schema.md` §Permissions |
| MCP servers | `references/mcp.md` |
| Hooks | `references/hooks.md` |
| Skills / custom agents | `references/skills.md` |
| Custom instructions | `references/instructions.md` |
| BYOK models / custom providers | `references/config-schema.md` §BYOK |
| Authentication | `references/config-schema.md` §Auth |

## Common quick operations (no reference needed)

```bash
# Trust a folder permanently (edit config.json)
# Add path to "trusted_folders" array

# Check auth status
gh auth status

# List MCP servers
/mcp show           # inside a session

# List skills
/skills list        # inside a session

# Change model for a session
/model              # inside a session

# Allow a tool for a session
/allow-all          # or --allow-all-tools CLI flag

# Offline mode (no GitHub contact)
export COPILOT_OFFLINE=true
```

## Scripts

- `scripts/show-config.py` — display all config files with annotations
- `scripts/validate-config.py` — validate JSON config files
- `scripts/update-references.py` — fetch latest upstream docs

Run with: `python scripts/<script>.py`

## Self-update procedure

When the user asks to **update**, **refresh**, or **sync** this skill:

1. Run `python scripts/update-references.py --all` → fetches docs to `_fetched/`
2. Read each `_fetched/` file alongside its corresponding `references/` file
3. Update `references/` files to reflect documentation changes
4. Run `python scripts/validate-config.py` to confirm no breakage
5. Delete `_fetched/` and report what changed

Source URLs are in `sources.json`.

## Safety rules

- Always read the file before editing
- Never remove `trusted_folders` entries without confirming with the user
- Hooks and skills live in project directories — confirm scope (global vs project) before creating
- JSON files: validate well-formed after any edit
- Markdown files: preserve frontmatter structure

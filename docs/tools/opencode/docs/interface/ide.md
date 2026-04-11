# OpenCode — IDE Integration

> Source: <https://opencode.ai/docs/ide/>  
> Last updated: April 10, 2026

OpenCode integrates with VS Code, Cursor, Windsurf, VSCodium, and any IDE with a terminal.

---

## Installation

The simplest method for VS Code and popular forks:

1. Open your IDE
2. Open the integrated terminal
3. Run `opencode` — the extension installs automatically

### Manual Install

Search for **OpenCode** in the Extension Marketplace and click Install.

### Troubleshooting

If the extension fails to install automatically:

1. Ensure you're running `opencode` in the integrated terminal
2. Confirm the CLI for your IDE is installed and in PATH:
   - VS Code: `code` command
   - Cursor: `cursor` command
   - Windsurf: `windsurf` command
   - VSCodium: `codium` command
3. If not, run `Cmd+Shift+P` (Mac) / `Ctrl+Shift+P` (Windows/Linux) and search: **Shell Command: Install 'code' command in PATH** (or equivalent for your IDE)
4. Ensure VS Code has permission to install extensions

---

## Usage

| Action | Mac | Windows / Linux |
|--------|-----|-----------------|
| Open OpenCode (split terminal) | `Cmd+Esc` | `Ctrl+Esc` |
| New OpenCode session | `Cmd+Shift+Esc` | `Ctrl+Shift+Esc` |
| Insert file reference | `Cmd+Option+K` | `Alt+Ctrl+K` |

- **Quick Launch:** Opens OpenCode in a split terminal view, or focuses an existing session
- **New Session:** Starts a new session even if one is already open
- **Context Awareness:** Automatically shares your current selection or tab with OpenCode
- **File Reference Shortcuts:** Inserts references like `@File#L37-42`

---

## Editor Commands (`/editor`, `/export`)

To use your IDE as the editor when running `/editor` or `/export` from the TUI, set the `EDITOR` environment variable:

```bash
export EDITOR="code --wait"        # VS Code
export EDITOR="cursor --wait"      # Cursor
export EDITOR="windsurf --wait"    # Windsurf
```

See [tui.md](tui.md) for more on editor setup.

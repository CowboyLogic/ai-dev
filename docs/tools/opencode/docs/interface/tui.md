# OpenCode — TUI

> Source: <https://opencode.ai/docs/tui/>  
> Last updated: April 10, 2026

OpenCode provides an interactive terminal interface (TUI) for working on projects with an LLM.

---

## Start

```bash
opencode                    # current directory
opencode /path/to/project   # specific directory
```

---

## File References

Use `@` to fuzzy-search and include files in your message:

```
How is auth handled in @packages/functions/src/api/index.ts?
```

---

## Bash Commands

Start a message with `!` to run a shell command and inject its output into the conversation:

```
!ls -la
```

---

## Slash Commands

Type `/` followed by a command name:

| Command | Keybind | Description |
|---------|---------|-------------|
| `/connect` | | Add a provider API key |
| `/compact` | `ctrl+x c` | Compact the current session (alias: `/summarize`) |
| `/details` | `ctrl+x d` | Toggle tool execution details |
| `/editor` | `ctrl+x e` | Open external editor for composing messages |
| `/exit` | `ctrl+x q` | Exit OpenCode (aliases: `/quit`, `/q`) |
| `/export` | `ctrl+x x` | Export conversation to Markdown |
| `/help` | `ctrl+x h` | Show help dialog |
| `/init` | `ctrl+x i` | Create or update `AGENTS.md` |
| `/models` | `ctrl+x m` | List available models |
| `/new` | `ctrl+x n` | Start new session (alias: `/clear`) |
| `/redo` | `ctrl+x r` | Redo previously undone message |
| `/sessions` | `ctrl+x l` | List and switch sessions (aliases: `/resume`, `/continue`) |
| `/share` | `ctrl+x s` | Share current session |
| `/themes` | `ctrl+x t` | List available themes |
| `/thinking` | | Toggle visibility of reasoning blocks |
| `/undo` | `ctrl+x u` | Undo last message and revert file changes |
| `/unshare` | | Unshare current session |

Custom commands are added the same way — type `/my-command`. See [commands.md](../features/commands.md).

---

## Editor Setup

Both `/editor` and `/export` use the `EDITOR` environment variable:

```bash
# Linux / macOS
export EDITOR=vim
export EDITOR=nano
export EDITOR="code --wait"   # VS Code (needs --wait)
export EDITOR="cursor --wait"

# Windows (CMD)
set EDITOR=notepad

# Windows (PowerShell)
$env:EDITOR = "notepad"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`) to make it permanent.

---

## Configure

TUI settings live in `tui.json` (or `tui.jsonc`), separate from `opencode.json`:

```jsonc
// tui.json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "opencode",
  "keybinds": {
    "leader": "ctrl+x"
  },
  "scroll_speed": 3,
  "scroll_acceleration": {
    "enabled": true
  },
  "diff_style": "auto",
  "mouse": true
}
```

### Options

| Option | Description |
|--------|-------------|
| `theme` | UI theme — see [themes.md](themes.md) |
| `keybinds` | Keyboard shortcuts — see [keybinds.md](keybinds.md) |
| `scroll_speed` | Scroll speed (min: 0.001, default: 3). Ignored if `scroll_acceleration.enabled` is true |
| `scroll_acceleration.enabled` | macOS-style scroll acceleration |
| `diff_style` | `"auto"` adapts to terminal width; `"stacked"` always single-column |
| `mouse` | Enable/disable mouse capture (default: true) |

Use `OPENCODE_TUI_CONFIG` to load a custom TUI config path.

---

## Customization

Access the command palette with `ctrl+x h` or `/help`. Settings persist across restarts.

**Toggle username display:** Search for "username" or "hide username" in the command palette.

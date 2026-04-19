# TUI, Keybinds & Themes Reference

## File location

```
~/.config/opencode/tui.json
```

Schema: `https://opencode.ai/tui.json`

```json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "opencode",
  "mouse": true,
  "diff_style": "auto",
  "scroll_speed": 3,
  "scroll_acceleration": {
    "enabled": true
  },
  "keybinds": {
    "session_new": "ctrl+n",
    "messages_page_up": "pgup"
  }
}
```

---

## TUI options

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `theme` | string | UI theme identifier | `"opencode"` |
| `mouse` | boolean | Enable mouse capture | `true` |
| `diff_style` | `"auto"` \| `"stacked"` | Diff rendering mode | `"auto"` |
| `scroll_speed` | number (min 0.001) | Scroll velocity | — |
| `scroll_acceleration.enabled` | boolean | Enable scroll acceleration | — |

---

## Keybinds

Override any action by setting a key combo string. Key format examples:
- `"ctrl+n"` — Ctrl+N
- `"alt+left"` — Alt+Left arrow
- `"pgup"` — Page Up
- `"f5"` — F5
- `"leader+d"` — Leader key + D

Set a keybind to `""` (empty string) to disable it.

### Session management

| Action | Default | Description |
|--------|---------|-------------|
| `session_new` | — | Start new session |
| `session_list` | — | Browse sessions |
| `session_export` | — | Export session |
| `session_rename` | — | Rename session |
| `session_delete` | — | Delete session |
| `session_fork` | — | Fork current session |
| `session_share` | — | Share session |
| `session_unshare` | — | Unshare session |
| `session_interrupt` | — | Interrupt current response |
| `session_compact` | — | Compact context manually |
| `session_timeline` | — | View session timeline |
| `session_child_first` | Leader+Down | Enter child session |
| `session_child_cycle` | — | Cycle child sessions |
| `session_parent` | — | Return to parent session |

### Message navigation

| Action | Description |
|--------|-------------|
| `messages_page_up` | Scroll up one page |
| `messages_page_down` | Scroll down one page |
| `messages_line_up` | Scroll up one line |
| `messages_line_down` | Scroll down one line |
| `messages_half_page_up` | Scroll up half page |
| `messages_half_page_down` | Scroll down half page |
| `messages_first` | Jump to first message |
| `messages_last` | Jump to last message |
| `messages_next` | Next message |
| `messages_previous` | Previous message |
| `messages_last_user` | Jump to last user message |

### Message operations

| Action | Description |
|--------|-------------|
| `messages_copy` | Copy message content |
| `messages_undo` | Undo last action |
| `messages_redo` | Redo |
| `messages_toggle_conceal` | Toggle message visibility |

### Model & agent

| Action | Description |
|--------|-------------|
| `model_list` | Open model picker (`/models`) |
| `model_cycle_recent` | Cycle recent models |
| `model_favorite_toggle` | Toggle model favorite |
| `agent_list` | Open agent picker |
| `agent_cycle` | Cycle / switch primary agent (default: Tab) |

### UI controls

| Action | Description |
|--------|-------------|
| `sidebar_toggle` | Toggle sidebar |
| `scrollbar_toggle` | Toggle scrollbar |
| `username_toggle` | Toggle username display |
| `theme_list` | Open theme picker |
| `editor_open` | Open external editor |
| `status_view` | Toggle status view |

---

## Themes

Set in `tui.json`:
```json
{ "theme": "tokyonight" }
```

Browse available themes inside opencode with `/themes` or by using the `theme_list` keybind.

Custom themes can be placed in:
- `~/.config/opencode/themes/`
- `.opencode/themes/`

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
    "leader": "ctrl+x",
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
| `diff_style` | `"auto"` \| `"stacked"` | `auto` adapts to terminal width; `stacked` always single-column | `"auto"` |
| `scroll_speed` | number (min 0.001) | Scroll velocity | — |
| `scroll_acceleration.enabled` | boolean | Enable scroll acceleration | — |
| `leader_timeout` | integer (ms) | How long to wait for the next key after the leader key | `2000` |
| `attention.enabled` | boolean | Enable TUI desktop notifications/sounds | — |
| `attention.notifications` \| `.sound` \| `.volume` (0-1) \| `.sound_pack` | — | Notification sub-options | — |
| `attention.sounds.{default,question,permission,error,done,subagent_done}` | string | Per-event sound override | — |
| `prompt.max_height` | integer | Prompt textarea max height | — |
| `prompt.max_width` | integer \| `"auto"` | Home prompt max width | — |
| `plugin` | array | Plugin definitions (same format as `opencode.json`) | — |
| `plugin_enabled` | object | Enable/disable plugins by name (`{"plugin-name": true}`) | — |

```json
{ "leader_timeout": 2000, "attention": { "enabled": true, "notifications": true, "sound": true, "volume": 0.4 } }
```

---

## Keybinds

Override any action by setting a key combo string. Key format examples:
- `"ctrl+n"` — Ctrl+N
- `"alt+left"` — Alt+Left arrow
- `"pgup"` — Page Up
- `"f5"` — F5
- `"<leader>d"` — Leader key + D

Set a keybind to `""` or `"none"`/`false` to disable it.

**Binding value forms**:
```jsonc
{ "keybinds": {
  "session_compact": "<leader>c",                              // single shortcut
  "messages_copy": ["<leader>y", "ctrl+shift+c"],               // multiple shortcuts (array)
  "input_paste": { "key": "ctrl+v", "preventDefault": false }   // advanced: key/event/preventDefault/fallthrough
} }
```
A string may also hold comma-separated shortcuts (`"ctrl+c,ctrl+d,<leader>q"`).

### Leader key

The leader key is `ctrl+x` by default. Override in `tui.json`:

```json
{ "keybinds": { "leader": "ctrl+x" } }
```

### App

| Action | Description |
|--------|-------------|
| `app_exit` | Exit the application |
| `app_debug` | Toggle debug mode |
| `app_console` | Open dev console |
| `app_heap_snapshot` | Write a heap snapshot (debugging) |
| `app_toggle_animations` | Toggle UI animations |
| `app_toggle_file_context` | Toggle file-context display |
| `app_toggle_diffwrap` | Toggle diff line wrapping |
| `app_toggle_paste_summary` | Toggle paste-summary behavior |
| `app_toggle_session_directory_filter` | Toggle session directory filter |
| `help_show` | Show help |
| `docs_open` | Open docs in browser |

### Session management

| Action | Default | Description |
|--------|---------|-------------|
| `session_new` | Leader+n | Start new session |
| `session_list` | Leader+l | Browse sessions |
| `session_export` | Leader+x | Export session |
| `session_copy` | — | Copy session |
| `session_move` | — | Move session |
| `session_rename` | ctrl+r | Rename session |
| `session_delete` | ctrl+d | Delete session |
| `session_share` / `session_unshare` | — | Share / unshare session |
| `session_interrupt` | escape | Interrupt current response |
| `session_background` | — | Send session to background |
| `session_compact` | Leader+c | Compact context manually |
| `session_timeline` | Leader+g | View session timeline |
| `session_toggle_timestamps` | — | Toggle message timestamps |
| `session_toggle_generic_tool_output` | — | Toggle generic tool-output rendering |
| `session_queued_prompts` | — | View queued prompts |
| `session_pin_toggle` | — | Pin/unpin session |
| `session_quick_switch_1` … `session_quick_switch_9` | — | Jump to Nth recent session |
| `session_child_first` | Leader+Down | Enter first child session |
| `session_child_cycle` / `session_child_cycle_reverse` | Right / Left | Cycle child sessions |
| `session_parent` | Up | Return to parent session |
| `stash_delete` | ctrl+d | Delete a stashed prompt |

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

### UI controls

| Action | Description |
|--------|-------------|
| `sidebar_toggle` | Toggle sidebar |
| `scrollbar_toggle` | Toggle scrollbar |
| `theme_list` | Open theme picker |
| `theme_switch_mode` / `theme_mode_lock` | Toggle / lock dark-light mode |
| `editor_open` | Open external editor |
| `status_view` | Toggle status view |
| `debug_view` | Toggle debug view |
| `tool_details` | Toggle tool details panel |
| `terminal_suspend` | Suspend to terminal (Unix) |
| `terminal_title_toggle` | Toggle terminal title updates |
| `tips_toggle` | Toggle tips/hints display |
| `plugin_manager` | Open plugin manager |
| `plugin_install` | Install a plugin |
| `plugins.toggle` / `dialog.plugins.install` | Plugin dialog toggle / install action |
| `display_thinking` | Toggle thinking display |

> [!NOTE]
> `username_toggle` and `title_toggle` are not current keybind actions — removed/renamed upstream.

### Diff view

| Action | Description |
|--------|-------------|
| `diff_open` / `diff_close` / `diff_toggle` | Open / close / toggle diff view |
| `diff_expand` / `diff_expand_all` / `diff_collapse` | Expand one, expand all, collapse hunks |
| `diff_switch_focus` | Switch focus between file tree and diff |
| `diff_next_hunk` / `diff_previous_hunk` | Navigate hunks |
| `diff_next_file` / `diff_previous_file` | Navigate files |
| `diff_toggle_file_tree` | Toggle file tree panel |
| `diff_single_patch` | Toggle single-patch view |
| `diff_switch_source` | Switch diff source |
| `diff_toggle_view` | Toggle view mode |
| `diff_help` | Show diff-view help |

### Model & agent

| Action | Description |
|--------|-------------|
| `model_list` | Open model picker (`/models`) |
| `model_cycle_recent` / `model_cycle_recent_reverse` | Cycle recent models (forward/reverse) |
| `model_cycle_favorite` / `model_cycle_favorite_reverse` | Cycle favorite models (forward/reverse) |
| `model_favorite_toggle` | Toggle model favorite |
| `model_provider_list` | Open provider picker |
| `mcp_list` | Open MCP server list |
| `provider_connect` | Open `/connect` flow |
| `console_org_switch` | Switch console org (Zen/Go) |
| `agent_list` | Open agent picker |
| `agent_cycle` / `agent_cycle_reverse` | Cycle / switch primary agent (default: Tab / Shift+Tab) |
| `variant_cycle` / `variant_list` | Cycle / open model variant picker |
| `command_list` | Open command picker |

### Prompt & stash

| Action | Description |
|--------|-------------|
| `prompt_submit` | Submit prompt |
| `prompt_editor_context_clear` | Clear editor context |
| `prompt_skills` | Open skills picker |
| `prompt_stash` / `prompt_stash_pop` / `prompt_stash_list` | Stash current prompt / pop / list stashed prompts |
| `workspace_set` | Set workspace |

### Input editing

| Action | Description |
|--------|-------------|
| `input_clear` | Clear input field |
| `input_paste` | Paste clipboard into input |
| `input_submit` | Submit current input |
| `input_newline` | Insert newline (Shift+Enter) |
| `input_move_left` / `input_move_right` / `input_move_up` / `input_move_down` | Move cursor |
| `input_select_left` / `_right` / `_up` / `_down` | Extend selection |
| `input_line_home` / `input_line_end` | Jump to line start/end |
| `input_select_line_home` / `input_select_line_end` | Select to line start/end |
| `input_visual_line_home` / `input_visual_line_end` | Jump to visual (wrapped) line start/end |
| `input_select_visual_line_home` / `input_select_visual_line_end` | Select to visual line start/end |
| `input_buffer_home` / `input_buffer_end` | Jump to buffer start/end |
| `input_select_buffer_home` / `input_select_buffer_end` | Select to buffer start/end |
| `input_delete_line` | Delete current line |
| `input_delete_to_line_end` / `input_delete_to_line_start` | Kill to line end/start |
| `input_delete` / `input_backspace` | Delete character |
| `input_word_forward` / `input_word_backward` | Move by word |
| `input_select_word_forward` / `input_select_word_backward` | Select by word |
| `input_delete_word_forward` / `input_delete_word_backward` | Delete word |
| `input_undo` / `input_redo` | Undo/redo in input |
| `input_select_all` | Select all input text |
| `history_previous` / `history_next` | Browse input history |

> [!TIP]
> `input_newline` (Shift+Enter) may need terminal configuration. In Windows Terminal, add a key binding action for the `\u001b[13;2u` sequence.

### Dialogs & autocomplete

| Action | Description |
|--------|-------------|
| `dialog.select.prev` / `.next` / `.page_up` / `.page_down` / `.home` / `.end` / `.submit` | Navigate any select-style dialog |
| `dialog.prompt.submit` | Submit a prompt dialog |
| `dialog.mcp.toggle` | Toggle an MCP entry in its dialog |
| `dialog.move_session.new` / `.delete` / `.refresh` | Move-session dialog actions |
| `prompt.autocomplete.prev` / `.next` / `.hide` / `.select` / `.complete` | Navigate @ / command autocomplete |
| `permission.prompt.fullscreen` | Toggle permission prompt fullscreen |

### Which-key

| Action | Description |
|--------|-------------|
| `which_key_toggle` | Show/hide the which-key hint layer |
| `which_key_layout_toggle` | Toggle layout |
| `which_key_pending_toggle` | Toggle pending-key display |
| `which_key_group_previous` / `which_key_group_next` | Switch key group |
| `which_key_scroll_up` / `which_key_scroll_down` | Scroll |
| `which_key_page_up` / `which_key_page_down` | Page scroll |
| `which_key_home` / `which_key_end` | Jump to start/end |

---

## Themes

Set in `tui.json`:
```json
{ "theme": "tokyonight" }
```

Browse available themes inside opencode with `/theme` or by using the `theme_list` keybind.

Built-in: `opencode` (default), `system` (adapts to terminal background), `tokyonight`, `everforest`, `ayu`, `catppuccin`, `catppuccin-macchiato`, `gruvbox`, `kanagawa`, `nord`, `matrix`, `one-dark` (more added over time).

Requires a truecolor (24-bit) terminal; check with `echo $COLORTERM` (expect `truecolor`/`24bit`), or set `COLORTERM=truecolor`.

Theme directories, later overrides earlier:
1. Built-in (embedded in binary)
2. `~/.config/opencode/themes/*.json` (or `$XDG_CONFIG_HOME/opencode/themes/`)
3. `<project-root>/.opencode/themes/*.json`
4. `./.opencode/themes/*.json` (current working directory)

Custom theme JSON supports: hex (`"#ffffff"`), ANSI (`0`-`255`), color references (`"primary"` or a name from an optional `defs` block), dark/light variants (`{"dark": "#000", "light": "#fff"}`), and `"none"` (inherit terminal default). Theme schema: `https://opencode.ai/theme.json`.

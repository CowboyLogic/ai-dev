# V2 CLI Settings Reference (`cli.json`)

Sources: <https://opencode.ai/v2/docs/cli/config/>, <https://opencode.ai/v2/docs/cli/keybinds/>,
<https://opencode.ai/v2/docs/cli/theme/>, <https://opencode.ai/v2/docs/themes/>,
<https://opencode.ai/v2/docs/cli/plugins/>. Schema: `https://opencode.ai/v2/cli.json`.

`cli.json` replaces the layered V1 `tui.json(c)` files. It controls the terminal clients only (TUI and
`opencode mini`); server/project settings stay in `opencode.json(c)`.

## Location

| Path | Notes |
|------|-------|
| `~/.config/opencode/cli.json` | The only CLI settings file |
| `$XDG_CONFIG_HOME/opencode/cli.json` | Used when `XDG_CONFIG_HOME` is set |

- There is **no project-local** CLI settings file.
- **Unknown settings are rejected.** Valid edits hot-reload while the TUI runs.
- On first V2 startup without `cli.json`, OpenCode migrates supported **global** `tui.json` settings (V1 files are
  left unchanged; project-local `tui.json` is not migrated).
- `OPENCODE_CLI_CONFIG_CONTENT='{"tabs":{"mode":"off"}}' opencode` merges inline JSON over `cli.json` (objects
  merge; arrays and scalars replace).
- `Ctrl+P` → Open settings edits common values from the TUI.

```json
{
  "$schema": "https://opencode.ai/v2/cli.json",
  "theme": { "name": "tokyonight", "mode": "system" },
  "animations": true,
  "mouse": true,
  "keybinds": { "leader": "ctrl+x" },
  "leader": { "timeout": 2000 }
}
```

## Settings

| Setting | Values | Description |
|---------|--------|-------------|
| `theme.name` | string | Built-in, custom, or `system` (terminal-derived) theme |
| `theme.mode` | `system` \| `dark` \| `light` | Follow terminal or lock a mode |
| `animations` | boolean | Interface animations |
| `cursor.style` | `block` \| `underline` \| `line` \| `default` | `default` keeps the terminal cursor |
| `cursor.blinking` | boolean | No effect when style is `default` |
| `mouse` | boolean | Terminal mouse capture |
| `scroll.speed` | number ≥ `0.001` | Distance per scroll tick |
| `scroll.acceleration` | boolean | Takes precedence over speed when enabled |
| `prompt.editor` | boolean | Include active editor file/selection as context |
| `prompt.paste` | `compact` \| `full` | Large paste display |
| `prompt.image_preview` | boolean | Image previews above the prompt |
| `session.sidebar` | `auto` \| `hide` | |
| `session.scrollbar` | boolean | |
| `session.thinking` | `show` \| `hide` | Model reasoning visibility |
| `session.grouping` | `auto` \| `none` | |
| `session.image_preview` | boolean | |
| `session.tps` | boolean | Output tokens/sec in footers |
| `session.markdown` | `source` \| `rendered` | |
| `session.new_location` | `launch` \| `inherit` | Where new sessions start |
| `session.permissions` | `prompt` \| `autoaccept` | `autoaccept` accepts every permission request |
| `tabs.mode` | `auto` \| `on` \| `off` | Legacy `tabs.enabled` boolean still read |
| `tabs.scope` | `cwd` \| `global` | |
| `tabs.layout` | `horizontal` \| `vertical` | |
| `tabs.indicators` | `status` \| `numbers` | |
| `diffs.source` | `branch` \| `committed` \| `working` | Initial `/diff` scope |
| `diffs.wrap` | `word` \| `none` | |
| `diffs.tree` / `diffs.single` | boolean | File tree / single-patch view |
| `diffs.view` | `auto` \| `split` \| `unified` | |
| `attention.notifications` | boolean | System notifications |
| `attention.sound` | boolean | Attention sounds |
| `attention.volume` | `0`–`1` | |
| `attention.sound_pack` | string | e.g. `opencode.default` |
| `attention.sounds` | object | Overrides for `default`, `question`, `permission`, `error`, `done`, `subagent_done` |
| `terminal.title` | boolean | Update window title |
| `terminal.copy` | `manual` \| `select` | Default `manual` on Windows, `select` elsewhere |
| `mini.*` | see docs | `thinking`, `tools`, `shell_output`, `turn_summary`, `footer`, `splash` (`show`/`hide`), `work_spinner`, `mono`, `replay`, `replay_limit` (default `200`) |
| `keybinds` | object | See below |
| `leader.timeout` | positive integer ms | Wait after the leader key |
| `plugins` | array | CLI-only plugins (see below) |
| `debug.devtools` / `debug.timing` | boolean | Debug bar diagnostics |
| `debug.turn_tokens` | boolean \| `verbose` | Per-turn token usage |
| `experimental` | object of feature ID → boolean | Only IDs listed in the TUI Experiments dialog |

> [!NOTE]
> V2 `attention` has no `enabled` flag (V1 `tui.json` did). Set `notifications` and `sound` directly.

## V1 `tui.json` → V2 `cli.json` key map

| V1 `tui.json` | V2 `cli.json` |
|---------------|---------------|
| `theme: "name"` | `theme.name` |
| `leader_timeout` | `leader.timeout` |
| `scroll_speed` | `scroll.speed` |
| `scroll_acceleration.enabled` | `scroll.acceleration` |
| `keybinds.<snake_case_id>` | `keybinds.<dotted.id>` (e.g. `session_new` → `session.new`) |
| `attention.enabled` | (removed) |
| `plugin` / `plugin_enabled` | `plugins` (with `-id` disable directives) |
| `cursor`, `mouse` | unchanged |

This table is derived from comparing the two documented schemas; the V2 docs describe the migration as automatic
but do not publish a field-by-field map. `diff_style` and `prompt.max_height`/`max_width` have no documented V2
equivalent.

## Keybinds

```json
{
  "keybinds": {
    "leader": "ctrl+space",
    "command.palette.show": "ctrl+k",
    "app.exit": ["ctrl+c", "ctrl+d"],
    "model.list": "<leader>m",
    "prompt.paste": { "key": "ctrl+v", "event": "press", "preventDefault": false, "fallthrough": false },
    "app.debug": "none",
    "help.show": false
  },
  "leader": { "timeout": 1500 }
}
```

- Value forms: string, comma-separated string (`"ctrl+c,ctrl+d"`), array of alternatives, or object
  (`key`, `event` = `press`/`release`, `preventDefault`, `fallthrough`).
- Disable with `"none"` or `false`.
- `leader` defaults to `ctrl+x`; `<leader>` refers to it.
- **Unknown command IDs are rejected.** V2 IDs are dotted (V1 used snake_case).

Common IDs and defaults:

| ID | Default |
|----|---------|
| `app.exit` | `ctrl+c,ctrl+d,<leader>q` |
| `command.palette.show` | `ctrl+p` |
| `opencode.settings` | `none` |
| `permission.mode` | `none` (toggle auto-approve) |
| `session.new` | `<leader>n` |
| `session.list` | `<leader>l` |
| `session.rename` | `ctrl+r` |
| `session.interrupt` | `escape` |
| `session.compact` | `<leader>c` |
| `session.fork` | `none` |
| `model.list` | `<leader>m` |
| `model.cycle_recent` / `model.cycle_recent_reverse` | `f2` / `shift+f2` |
| `agent.list` | `<leader>a` |
| `agent.cycle` / `agent.cycle.reverse` | `shift+tab` / `none` |
| `messages.copy` | `<leader>y` |
| `app.clear` (mini only) | `ctrl+l` |

For the full list (diff viewer, input editing, composer, dialogs, which-key), see
<https://opencode.ai/v2/docs/cli/keybinds/>. Retired diff IDs (`diff.toggle`, `diff.expand`, `diff.expand_all`,
`diff.collapse`, `diff.switch_focus`) are accepted but register nothing.

## Themes

```json
{ "theme": { "name": "catppuccin", "mode": "dark" } }
```

Built-ins include `aura`, `ayu`, `carbonfox`, `catppuccin`, `catppuccin-frappe`, `catppuccin-macchiato`, `cobalt2`,
`cursor`, `dracula`, `everforest`, `flexoki`, `github`, `gruvbox`, `kanagawa`, `lucent-orng`, `material`, `matrix`,
`mercury`, `monokai`, `nightowl`, `nord`, `one-dark`, `opencode` (default), `orng`, `osaka-jade`, `palenight`,
`rosepine`, `solarized`, `synthwave84`, `tokyonight`, `vercel`, `vesper`, `zenburn`, and `system` (when the terminal
palette is readable). `/themes` switches interactively.

Custom themes: `~/.config/opencode/themes/<name>.json` (global) or `.opencode/themes/<name>.json` (project; closer
wins). Filename = theme name; `.json` only.

The V2 theme format is **not** the V1 format. Every V2 theme has one complete `base` token tree and at least one of
`light`/`dark` with a complete `hue` palette:

```json
{
  "$schema": "https://opencode.ai/theme.json",
  "base": {
    "text": { "base": "$hue.neutral.200", "muted": "$hue.neutral.400" },
    "categorical": ["accent", "purple", "green"]
  },
  "dark": { "hue": { "accent": "$hue.cyan" } }
}
```

- Colors: 3/4/6/8-digit hex, `transparent`, or `$` references (`$hue.<name>.<step>`, `$text.muted`).
- Hues: `gray`, `red`, `orange`, `yellow`, `green`, `cyan`, `blue`, `purple`; aliases `accent`, `interactive`,
  `neutral`; steps `100`–`900`.
- Token groups: `text`, `background` (incl. `raised.base/high/max`), `border`, `scrollbar`, `diff`, `syntax`,
  `markdown`; action states `$hovered`, `$focused`, `$pressed`, `$selected`, `$disabled`; `@dialog` overrides.
- Use the official theme tool to generate a complete `base` before customizing (the excerpt above is incomplete).

## CLI-only plugins

Plugins in `opencode.json(c)` that expose a TUI component load automatically — do not repeat them here. Use
`cli.json` `plugins` for terminal-only plugins that should stay active when connected to a remote server:

```json
{
  "plugins": [
    "*",
    "-opencode.notifications",
    { "package": "./plugins/status", "options": { "compact": true } }
  ]
}
```

Entries apply in order; `-id` or `-prefix.*` disables. Local discovery: `<global-config>/plugins/<name>/tui.ts` and
`<project>/.opencode/plugins/<name>/tui.ts`. See [plugins.md](plugins.md).

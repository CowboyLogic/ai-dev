# OpenCode — Themes

> Source: <https://opencode.ai/docs/themes/>  
> Last updated: April 10, 2026

OpenCode supports built-in themes, a terminal-adaptive system theme, and custom JSON themes.

---

## Terminal Requirements

Themes require truecolor (24-bit color) support:

```bash
echo $COLORTERM   # should output "truecolor" or "24bit"
```

If not set:

```bash
export COLORTERM=truecolor
```

Modern terminals with truecolor support: iTerm2, Alacritty, Kitty, WezTerm, Windows Terminal, GNOME Terminal.

---

## Built-in Themes

| Theme | Description |
|-------|-------------|
| `opencode` | Default OpenCode theme |
| `system` | Adapts to your terminal's background color |
| `tokyonight` | Based on Tokyonight |
| `everforest` | Based on Everforest |
| `ayu` | Based on Ayu dark |
| `catppuccin` | Based on Catppuccin |
| `catppuccin-macchiato` | Based on Catppuccin Macchiato |
| `gruvbox` | Based on Gruvbox |
| `kanagawa` | Based on Kanagawa |
| `nord` | Based on Nord |
| `matrix` | Hacker-style green on black |
| `one-dark` | Based on Atom One Dark |

---

## System Theme

The `system` theme automatically adapts to your terminal's color scheme:

- Generates a custom gray scale from your terminal's background color
- Uses ANSI colors (0–15) for syntax highlighting
- Preserves your terminal's native appearance with `none` color values

---

## Using a Theme

### Via TUI command

```
/themes
```

### Via config

```jsonc
// tui.json
{
  "$schema": "https://opencode.ai/tui.json",
  "theme": "tokyonight"
}
```

---

## Custom Themes

### Locations (priority order, later overrides earlier)

1. Built-in themes (embedded in binary)
2. `~/.config/opencode/themes/*.json` — user-wide
3. `<project-root>/.opencode/themes/*.json` — project-specific
4. `./.opencode/themes/*.json` — current directory

### Create a theme

```bash
# User-wide
mkdir -p ~/.config/opencode/themes
vim ~/.config/opencode/themes/my-theme.json

# Project-specific
mkdir -p .opencode/themes
vim .opencode/themes/my-theme.json
```

### JSON format

```jsonc
{
  "$schema": "https://opencode.ai/theme.json",
  "defs": {
    "myblue": "#5E81AC",
    "myred": "#BF616A"
  },
  "theme": {
    "primary": { "dark": "myblue", "light": "myblue" },
    "error": { "dark": "myred", "light": "myred" },
    "text": "none",
    "background": "none"
  }
}
```

**Color value formats:**
- Hex: `"#ffffff"`
- ANSI index: `3` (0–255)
- Color reference: `"primary"` or a name defined in `defs`
- Dark/light variant: `{"dark": "#000", "light": "#fff"}`
- Terminal default: `"none"`

**Available theme keys (selection):**

| Key | Description |
|-----|-------------|
| `primary` | Primary accent color |
| `secondary` | Secondary accent color |
| `accent` | Additional accent |
| `error` | Error state color |
| `warning` | Warning state color |
| `success` | Success state color |
| `info` | Info state color |
| `text` | Default text color |
| `textMuted` | Muted/secondary text |
| `background` | Main background |
| `backgroundPanel` | Panel background |
| `backgroundElement` | Element background |
| `border` | Border color |
| `borderActive` | Active border color |
| `borderSubtle` | Subtle border color |
| `diffAdded` | Added lines color |
| `diffRemoved` | Removed lines color |
| `diffContext` | Context lines color |
| `diffAddedBg` | Added lines background |
| `diffRemovedBg` | Removed lines background |
| `syntaxComment` | Syntax: comments |
| `syntaxKeyword` | Syntax: keywords |
| `syntaxFunction` | Syntax: functions |
| `syntaxVariable` | Syntax: variables |
| `syntaxString` | Syntax: strings |
| `syntaxNumber` | Syntax: numbers |
| `syntaxType` | Syntax: types |
| `syntaxOperator` | Syntax: operators |
| `syntaxPunctuation` | Syntax: punctuation |
| `markdownText` | Markdown text |
| `markdownHeading` | Markdown headings |
| `markdownCode` | Markdown inline code |
| `markdownCodeBlock` | Markdown code blocks |
| `markdownLink` | Markdown links |

Use `"none"` for `text` and `background` to inherit terminal defaults — ideal for themes that blend with any terminal color scheme.

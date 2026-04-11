# OpenCode — Introduction

> Source: <https://opencode.ai/docs>  
> Last updated: April 10, 2026

[OpenCode](https://opencode.ai/) is an open source AI coding agent available as a terminal-based interface (TUI), desktop app, or IDE extension.

---

## Prerequisites

To use OpenCode in your terminal you need:

- A modern terminal emulator:
  - [WezTerm](https://wezterm.org/) — cross-platform
  - [Alacritty](https://alacritty.org/) — cross-platform
  - [Ghostty](https://ghostty.org/) — Linux and macOS
  - [Kitty](https://sw.kovidgoyal.net/kitty/) — Linux and macOS
- API keys for the LLM providers you want to use

---

## Install

### Linux / macOS (install script)

```bash
curl -fsSL https://opencode.ai/install | bash
```

### Using Node.js

```bash
npm install -g opencode-ai
# or
bun add -g opencode-ai
# or
pnpm add -g opencode-ai
```

### macOS (Homebrew)

```bash
brew install anomalyco/tap/opencode
```

> Use the OpenCode tap for the most up-to-date releases. The official `brew install opencode` formula is maintained by Homebrew and updated less frequently.

### Arch Linux

```bash
sudo pacman -S opencode        # Stable
paru -S opencode-bin           # Latest from AUR
```

### Windows

For the best experience on Windows, use [WSL](https://opencode.ai/docs/windows-wsl). It provides better performance and full compatibility.

```powershell
choco install opencode         # Chocolatey
scoop install opencode         # Scoop
npm install -g opencode-ai     # npm
```

You can also grab the binary from [GitHub Releases](https://github.com/anomalyco/opencode/releases).

---

## Configure

OpenCode works with any LLM provider. Run `/connect` in the TUI to add API keys:

```
/connect
```

New users can start with [OpenCode Zen](https://opencode.ai/docs/zen) — a curated, tested model list managed by the OpenCode team.

---

## Initialize

Navigate to your project and start OpenCode:

```bash
cd /path/to/project
opencode
```

Then run `/init` to analyze the project and create an `AGENTS.md` file:

```
/init
```

Commit `AGENTS.md` to Git so OpenCode understands your project across sessions.

---

## Usage

### Ask questions

```
How is authentication handled in @packages/functions/src/api/index.ts
```

Use `@` to fuzzy-search for files and include them in context.

### Plan then build

Press `Tab` to switch to Plan mode (LLM cannot make changes). Describe what you want:

```
When a user deletes a note, flag it as deleted in the database.
Then create a screen that shows recently deleted notes.
```

Iterate on the plan, then press `Tab` again to switch to Build mode and ask it to proceed.

### Make changes directly

```
Add authentication to the /settings route. See how it's done in
@packages/functions/src/notes.ts and implement the same in
@packages/functions/src/settings.ts
```

### Undo / Redo

```
/undo    # Reverts last change and shows your original prompt again
/redo    # Re-applies undone changes
```

Both commands work multiple times and use Git snapshots internally.

---

## Share

```
/share
```

Creates a shareable link to the current conversation and copies it to the clipboard. Conversations are not shared by default.

---

## Customize

- [Themes](themes.md) — `/theme` or set in `tui.json`
- [Keybinds](keybinds.md) — customizable in `tui.json`
- [Formatters](https://opencode.ai/docs/formatters) — code auto-formatting
- [Custom Commands](commands.md) — `/my-command` shortcuts
- [Config reference](config.md) — full `opencode.json` schema

---

## Doc sections

| Page | Description |
|------|-------------|
| [config.md](config.md) | Full configuration reference |
| [providers.md](providers.md) | LLM provider setup (75+ providers) |
| [models.md](models.md) | Model selection and configuration |
| [agents.md](agents.md) | Built-in and custom agents |
| [tools.md](tools.md) | Built-in tools and permissions |
| [rules.md](rules.md) | AGENTS.md / custom instructions |
| [mcp-servers.md](mcp-servers.md) | MCP (Model Context Protocol) servers |
| [cli.md](cli.md) | CLI commands and flags |
| [tui.md](tui.md) | Terminal UI usage and commands |
| [themes.md](themes.md) | Themes and customization |
| [keybinds.md](keybinds.md) | Keyboard shortcuts |
| [commands.md](commands.md) | Custom slash commands |

# Mods

Mods change an AI client's own interface: panes, panels, status lines, and slash commands that
the client does not ship with. Where a skill teaches an agent how to do a task, a mod changes
what you see and use while working with that agent.

All mod files live at the root of the repository under
[`mods/`](https://github.com/CowboyLogic/ai-dev/tree/main/mods), in one folder per client.

---

## Claude Code

Claude Code mods are plugins built on function hooks: a `plugin.json` manifest and a TypeScript
hooks module that draws into the client's surfaces. They live under
[`mods/claude/`](https://github.com/CowboyLogic/ai-dev/tree/main/mods/claude).

| Mod | What it does |
|---|---|
| [Git-Aware File Explorer](git-aware-file-explorer.md) | A Files pane that marks changed files in the tree and shows a file's diff beside it |

### Installing a Claude Code mod

Clone the repository, then load the mod's folder into Claude Code.

```bash
git clone https://github.com/CowboyLogic/ai-dev.git
```

For a terminal session, pass the folder on the command line. The mod loads for that session only.

```bash
claude --plugin-dir /path/to/ai-dev/mods/claude/<mod-name>
```

For every session, including those the desktop app starts, name the folder in the `env` block of
`~/.claude/settings.json`. Separate several folders with `:` (`;` on Windows).

```json
{
  "env": {
    "CLAUDE_CODE_PLUGIN_DIRS": "/path/to/ai-dev/mods/claude/<mod-name>"
  }
}
```

> [!NOTE]
> The repository has no plugin marketplace yet, so `/plugin install` does not work for these mods.
> Loading the folder also means a `git pull` updates the mod.

# CLI Commands, Options, and Slash Commands

Run `copilot help [TOPIC]` for built-in help (topics: `billing`, `config`, `commands`,
`environment`, `logging`, `monitoring`, `permissions`, `providers`, `sandbox`). Run `/help` in a
session for the full slash-command list.

## Terminal commands

| Command | Purpose |
|---------|---------|
| `copilot` | Interactive UI |
| `copilot login [--host H] [--web-flow\|--device-code\|--with-token]` | Authenticate |
| `copilot init` | Generate or improve `.github/copilot-instructions.md` |
| `copilot mcp list\|get\|add\|enable\|disable\|remove` | Manage MCP servers (see `mcp.md`) |
| `copilot skill list\|add\|remove\|enable\|disable` | Manage skills (see `skills.md`) |
| `copilot plugin ...` | Manage plugins and marketplaces (`copilot plugins` is a legacy alias; see `agents-plugins.md`) |
| `copilot instruction list [--json]` | List discovered instruction sources |
| `copilot lsp list [--json]` | List configured language servers |
| `copilot completion bash\|zsh\|fish` | Shell completion script |
| `copilot help [TOPIC]` | Help |
| `copilot update` / `copilot version` | Update / version |
| `copilot app` | Open the GitHub Copilot app in the current directory |

Custom agents and session-scoped hooks have no terminal subcommand — they need a live session.

---

## Command-line options

### Session and mode

| Option | Purpose |
|--------|---------|
| `-p PROMPT`, `--prompt=PROMPT` | Run programmatically and exit |
| `-i PROMPT`, `--interactive=PROMPT` | Start interactive and run this prompt |
| `-n NAME`, `--name=NAME` | Name the new session |
| `-r`, `--resume[=VALUE]` | Resume by ID, ID prefix, or name (exact, case-insensitive); bare opens picker (needs TTY) |
| `--continue` | Resume most recent session in cwd (else globally) |
| `--session-id ID` | Exact session/task ID; creates a new session only for a valid UUID |
| `--connect[=SESSION-ID]` | Connect to a remote session |
| `-C DIRECTORY` | Change directory first |
| `-w`, `--worktree[=NAME]` | Start in a Git worktree under `<repo>.worktrees/` |
| `--mode=interactive\|plan\|autopilot` | Initial mode; `--plan --mode autopilot` = plan-then-autopilot |
| `--plan` | Start in plan mode |
| `--autopilot` | Keep working until `task_complete` |
| `--max-autopilot-continues=COUNT` | Cap autopilot continuations |
| `--fleet` | Run the prompt with parallel subagents |
| `--agent=AGENT` | Use a custom agent |
| `--model=MODEL` | Model (`auto` allowed) |
| `--effort=LEVEL`, `--reasoning-effort=LEVEL` | `low`, `medium`, `high`, `xhigh`, `max` |
| `--context default\|long_context` | Context tier |
| `--max-ai-credits=CREDITS` | Soft per-response AI credit cap |
| `--acp` | Run as Agent Client Protocol server |

### Permissions and tools

`--allow-all`, `--yolo`, `--allow-all-tools`, `--allow-all-paths`, `--allow-all-urls`,
`--allow-tool`, `--deny-tool`, `--allow-url`, `--deny-url`, `--available-tools`,
`--excluded-tools`, `--disallow-temp-dir`, `--add-dir`, `--no-ask-user`, `--sandbox`,
`--no-sandbox`, `--secret-env-vars=VAR` — see `permissions.md`.

### MCP, plugins, instructions

| Option | Purpose |
|--------|---------|
| `--additional-mcp-config=JSON\|@FILE` | Add MCP servers for this session (highest priority) |
| `--disable-builtin-mcps` | Disable built-in MCP servers |
| `--disable-mcp-server=NAME` / `--enable-mcp-server=NAME` | Per-session toggle |
| `--add-github-mcp-tool=TOOL` / `--add-github-mcp-toolset=TOOLSET` / `--enable-all-github-mcp-tools` | Widen GitHub MCP tool set |
| `--allow-all-mcp-server-instructions` | Put all MCP server instructions in the system prompt |
| `--plugin-dir=DIRECTORY` | Load a plugin from a local directory |
| `--no-custom-instructions` | Skip `AGENTS.md` and related instruction files |
| `--enable-memory` | Enable memory in prompt mode |

### Output and UI

`--output-format=text|json` (JSONL), `-s`/`--silent`, `--stream=on|off`, `--share=PATH`,
`--share-gist`, `--attachment PATH`, `--log-dir`, `--log-level`, `--banner`/`--no-banner`,
`--no-color`, `--plain-diff`, `--screen-reader`, `--mouse[=on|off]`/`--no-mouse`,
`--experimental`/`--no-experimental`, `--no-auto-update`, `--bash-env`/`--no-bash-env`,
`--remote`/`--no-remote`, `--remote-export`/`--no-remote-export`.

### Deprecated options

| Option | Status |
|--------|--------|
| `--config-dir=DIRECTORY` | Deprecated — use `COPILOT_HOME` |
| `--enable-reasoning-summaries` | Accepted but ignored |

---

## Sessions

```bash
copilot --name my-feature-work      # name a new session
copilot --resume=my-feature-work    # resume by name, ID, or ID prefix
copilot --continue                  # most recent session in this directory
```

| Slash command | Purpose |
|---------------|---------|
| `/session [info\|checkpoints [n]\|files\|plan\|rename [NAME]\|cleanup\|prune\|delete [ID]\|delete-all]` | Session info and management (`/sessions` alias) |
| `/rename [NAME]` | Rename current session |
| `/resume [ID]`, `/continue [ID]` | Switch session |
| `/fork [NAME]`, `/branch [NAME]` | Fork current session |
| `/clear`, `/new`, `/reset` | Start a new conversation |
| `/undo`, `/rewind` | Roll back to an earlier turn (optionally restore files) |
| `/restart` | Restart the CLI, restoring live sessions |
| `/share [link\|off\|file\|html\|gist\|research]`, `/export` | Share/export the session |

Session history lives in `~/.copilot/session-state/`.

---

## Slash commands by area

### Configuration

| Command | Purpose |
|---------|---------|
| `/settings [--repo\|--local] [show KEY\|KEY\|KEY VALUE]`, `/config` | Settings editor or inline set |
| `/model [--session\|--global\|--repo\|--local] [MODEL]`, `/models` | Choose model, effort, context |
| `/theme [default\|github\|dim\|high-contrast\|colorblind]` | Color theme |
| `/statusline`, `/footer` | Status-line items |
| `/experimental [on\|off\|show]` | Experimental features |
| `/terminal-setup` | Multiline input keys |
| `/vim` | Toggle Vim mode |
| `/keep-alive [on\|off\|busy\|DURATION]`, `/caffeinate` | Prevent sleep |
| `/limits`, `/limits set max-ai-credits VALUE`, `/limits unset` | Per-response credit limits |

### Customization

| Command | Purpose |
|---------|---------|
| `/mcp [config\|list\|show\|add\|edit\|delete\|disable\|enable\|auth\|reload\|search] [NAME]` | MCP servers |
| `/skills [list\|info\|add\|remove\|reload]` | Skills |
| `/plugin [install\|update\|uninstall\|list\|marketplace ...]` | Plugins |
| `/agent` | Pick or create a custom agent |
| `/subagents`, `/agents` | Per-agent subagent models |
| `/instructions` | View and toggle instruction files |
| `/lsp [show\|test\|reload\|logs\|help] [NAME]` | Language servers |
| `/extensions`, `/extension` | Extensions (experimental) |
| `/env` | Show loaded instructions, MCP, skills, agents, hooks, plugins, LSPs, extensions |
| `/init` | Create/update `copilot-instructions.md` (`/init suppress` hides the startup hint) |

The experimental `/plugins` command was removed — use `/plugin`, `/mcp`, `/skills`, `/subagents`,
and `/instructions`.

### Permissions and directories

`/permissions [default|assisted|allow-all|show|reset]`, `/allow-all`, `/yolo`,
`/reset-allowed-tools`, `/add-dir PATH`, `/list-dirs`, `/cwd`, `/cd [PATH]`,
`/sandbox [config|status|policy|enable|disable]` (experimental).

### Work

| Command | Purpose |
|---------|---------|
| `/plan [PROMPT]` | Plan before coding (project files write-protected) |
| `/autopilot [OBJECTIVE]`, `/goal` | Autopilot, optional `--max-ai-credits N` |
| `/fleet [PROMPT]` | Parallel subagents |
| `/delegate [PROMPT]` | Hand off to Copilot cloud agent (opens a PR) |
| `/review [PROMPT]` / `/security-review [PROMPT]` | Code / security review agents |
| `/rubber-duck [PROMPT]` | Second-opinion agent |
| `/research TOPIC` | Deep research |
| `/pr [view\|create\|fix\|auto\|automerge]` | Pull requests for the current branch |
| `/diff` | Review changes |
| `/worktree [branch\|task]`, `/worktree new`, `/move` | Git worktrees |
| `/every`, `/after` | Scheduled prompts (experimental) |
| `/tasks` | Background subagents and shells |
| `/ask QUESTION`, `/btw` | Side question outside history |
| `/compact [FOCUS]` / `/context` | Compress / inspect context |
| `/chronicle <standup\|tips\|improve\|reindex\|skills ...>` | Session-history insights |
| `/usage` | Usage and AI credits |
| `/diagnose [PROMPT]` | Analyze the session log |

### Account and app

`/login`, `/logout`, `/user [show|list|switch]`, `/remote [on|off]`, `/ide`, `/app`,
`/feedback` (`/bug`), `/changelog`, `/update` (`/upgrade`), `/version`, `/voice`, `/copy`,
`/search`, `/exit` (`/quit`).

# CLI Commands, Options, and Slash Commands

Run `codex --help` or `codex <command> -h` for built-in help. Run `/` in a session to open the
slash-command popup. Flag tables below were verified against `codex-cli 0.158.0`; slash commands come
from the Codex docs and cannot be listed from the terminal.

> [!NOTE]
> Prefer local `-h` output over the docs when they differ. In `0.158.0`, `codex <group> <sub> --help`
> can print the root help; use `-h` instead.

The CLI reads defaults from `~/.codex/config.toml`. Any `-c key=value` override applies to that one
invocation and wins over the file.

## Terminal commands

| Command | Purpose |
|---------|---------|
| `codex [PROMPT]` | Interactive TUI; accepts the global flags plus `-i` image attachments |
| `codex exec` (`codex e`) | Non-interactive run for scripts and CI (see [Non-interactive runs](#non-interactive-runs)) |
| `codex review` | Non-interactive code review |
| `codex resume` / `codex fork` | Resume or fork a saved interactive session |
| `codex queue` | Queue a message for an existing session |
| `codex archive` / `unarchive` / `delete` | Manage saved sessions |
| `codex login` / `logout` | Authenticate / remove stored credentials |
| `codex mcp list\|get\|add\|remove\|login\|logout` | Manage MCP servers (see `mcp.md`) |
| `codex plugin add\|list\|remove\|marketplace` | Manage plugins and marketplaces |
| `codex features list\|enable\|disable` | Inspect or persist feature flags |
| `codex doctor` | Diagnose installation, config, auth, and runtime health |
| `codex debug models\|prompt-input\|app-server` | Debugging tools |
| `codex sandbox [COMMAND]...` | Run a command under the Codex sandbox |
| `codex execpolicy check -r RULES...` | Check execpolicy rule files against a command (preview) |
| `codex apply TASK_ID` (`codex a`) | Apply the latest diff from a Codex cloud task with `git apply` |
| `codex cloud [list\|exec\|status\|apply\|diff]` | Browse and submit Codex cloud tasks (experimental) |
| `codex completion [SHELL]` | Shell completion script: `bash` (default), `elvish`, `fish`, `powershell`, `zsh` |
| `codex update` | Self-update when the installed release supports it |
| `codex app-server`, `codex remote-control`, `codex exec-server` | Experimental server tooling; may change without notice |

`codex mcp-server` was removed (the docs point to the Codex app server); `0.158.0` confirms it is gone.

---

## Global flags

These apply to `codex` and propagate to most subcommands. Run the subcommand's `-h` for exceptions.

### Configuration and features

| Flag | Purpose |
|------|---------|
| `-c`, `--config key=value` | Override a config value; dotted path for nested keys; value parsed as TOML, else a literal string |
| `-p`, `--profile NAME` | Layer `$CODEX_HOME/<NAME>.config.toml` on top of the base user config |
| `--enable FEATURE` / `--disable FEATURE` | Repeatable; equivalent to `-c features.<name>=true` / `false` |
| `--strict-config` | Error when `config.toml` has fields this version does not recognize |
| `--remote ADDR`, `--remote-auth-token-env ENV_VAR` | Connect the TUI to an app server (`ws://`, `wss://`, `unix://`, `unix://PATH`); token is read from the named env var |

```bash
codex -c model="o3" -c shell_environment_policy.inherit=all
codex --enable unified_exec --profile review
```

> [!NOTE]
> The docs describe `--profile` only as "profiles" in config. The `0.158.0` CLI defines `-p, --profile`
> as a separate file layer, `$CODEX_HOME/<name>.config.toml`. Note also that `-p` means `--profile`,
> not `--prompt`. `codex features` does not accept `--profile`.

### Model, sandbox, and approvals

| Flag | Purpose |
|------|---------|
| `-m`, `--model MODEL` | Model for the session |
| `--oss`, `--local-provider lmstudio\|ollama` | Use an open-source local provider |
| `-s`, `--sandbox MODE` | `read-only`, `workspace-write`, `danger-full-access` |
| `-a`, `--ask-for-approval POLICY` | `on-request` or `never` (interactive commands only; `codex exec` rejects it) |
| `--approve-for-me` | Route approval requests through automatic review under the `workspace-write` sandbox |
| `--dangerously-bypass-approvals-and-sandbox` | No prompts, no sandbox; only inside an externally sandboxed environment |
| `--dangerously-bypass-hook-trust` | Run enabled hooks without persisted hook trust for this invocation |
| `--search` | Live web search; default is cached mode |

For low-friction local work, use `--sandbox workspace-write --ask-for-approval on-request`.

### Directories and display

| Flag | Purpose |
|------|---------|
| `-C`, `--cd DIR` | Working root for the agent |
| `--add-dir DIR` | Extra writable directory beside the primary workspace |
| `--worktree` | Run in a new managed Git worktree |
| `-i`, `--image FILE...` | Attach images to the initial prompt |
| `--no-alt-screen` | Inline TUI that preserves scrollback |
| `--no-daemon` | Skip the shared background server, even if it is running |

### Flag safety

- Prefer `--add-dir` over `--sandbox danger-full-access` when Codex needs more write access.
- Reserve `--dangerously-bypass-approvals-and-sandbox` for a dedicated sandbox VM.
- Pass secrets through the environment, never as `-c` values, because command lines land in shell
  history and process listings.

---

## Sessions

| Command | Purpose |
|---------|---------|
| `codex resume [SESSION] [PROMPT]` | Resume by session ID (UUID) or name; opens a picker when omitted |
| `codex resume --last` | Most recent session in the current directory |
| `codex resume --all` | Search all sessions; drops the cwd filter and shows a CWD column |
| `codex resume --include-non-interactive` | Include non-interactive sessions in the picker and `--last` |
| `codex fork [SESSION] [PROMPT]` | Fork into a new chat; picker by default, `--last` for the newest |
| `codex archive SESSION` / `codex unarchive SESSION` | Hide or restore a session without deleting the transcript |
| `codex delete SESSION [--force]` | Permanently delete a session |
| `codex queue --thread SESSION --message TEXT` | Queue a message for an existing session |

```bash
codex resume --last
codex resume my-feature-work "continue with the tests"
codex fork --last
codex delete 0198a1b2-... --force    # --force only with a session UUID
```

- Session arguments accept an ID or a name; a UUID takes precedence if the value parses as one.
- `codex fork` help says UUID only for its `SESSION_ID`; `codex exec fork` and `codex queue --thread`
  accept a UUID or session name.
- `--force` on `codex delete` skips the prompt and requires a UUID. Named sessions always prompt, so a
  repeated or ambiguous name is never deleted silently.
- When the current directory differs from the session's saved directory, `resume` and `fork` ask which
  to use. Set `tui.resume_cwd` to `"current"` or `"session"` to skip the prompt; an explicit `--cd`
  beats `tui.resume_cwd`.

---

## Non-interactive runs

```bash
codex exec "summarize this repo"                  # prompt as argument
echo "fix the failing test" | codex exec -        # prompt from stdin
codex exec --json -o last.txt "audit deps"        # JSONL events + final message file
codex exec resume --last "now add tests"          # continue the latest session
codex exec fork SESSION "try another approach"    # fork by UUID or thread name
codex exec review --uncommitted                   # review inside exec
```

Piped stdin plus a prompt argument is appended as a `<stdin>` block. Default output is formatted text.

| Option | Purpose |
|--------|---------|
| `--json` | Newline-delimited JSON events on stdout |
| `-o`, `--output-last-message FILE` | Write the agent's final message to a file |
| `--output-schema FILE` | JSON Schema for the final response shape |
| `--color always\|never\|auto` | Output color (default `auto`) |
| `--skip-git-repo-check` | Allow running outside a Git repository |
| `--ephemeral` | Do not persist session files |
| `--ignore-user-config` | Skip `$CODEX_HOME/config.toml`; auth still uses `CODEX_HOME` |
| `--ignore-rules` | Skip user and project execpolicy `.rules` files |
| `--thread-source SOURCE` | Source classification for new or forked threads |

`exec` also takes `-m`, `-p`, `-s`, `-C`, `-i`, `--add-dir`, `--oss`, `--worktree`, `--approve-for-me`,
`-c`, `--enable`, `--disable`, and `--strict-config`. `exec resume` takes `[SESSION_ID] [PROMPT]`,
`--last`, and `--all`. Pair `--json` with `--output-last-message` in CI to capture progress and a
final summary.

### Review

`codex review` and `codex exec review` take exactly one target: `--uncommitted`, `--base BRANCH`,
`--commit SHA`, or a custom `PROMPT` (`-` reads stdin). `--title` pairs only with `--commit`.

---

## Diagnostics and maintenance

| Command | Notes |
|---------|-------|
| `codex doctor` | Checks install, config, auth, runtime, Git, terminal, app-server, and thread inventory. Flags: `--json` (redacted report), `--summary`, `--all` (expand long lists), `--no-color`, `--ascii` |
| `codex features list` | Known features with stage and effective state |
| `codex features enable FEATURE` / `disable FEATURE` | Persist to `$CODEX_HOME/config.toml` for future sessions |
| `codex debug models [--bundled]` | Raw model catalog as JSON; `--bundled` skips the remote refresh |
| `codex debug prompt-input [PROMPT]` | Model-visible prompt input as JSON; use to debug instruction discovery |
| `codex update` | Update the CLI; debug builds tell you to install a release build |
| `codex login status` | Exits `0` when credentials are present |
| `codex logout` | Removes saved API-key and ChatGPT credentials |

`codex login` opens a browser for ChatGPT OAuth by default. Alternatives: `--device-auth`,
`--with-api-key` (reads the key from stdin, for example `printenv OPENAI_API_KEY | codex login --with-api-key`), and `--with-access-token` (reads the token from stdin).

`codex sandbox` runs a command under the same policy Codex uses. The `0.158.0` CLI has a single form,
`codex sandbox [OPTIONS] [COMMAND]...`, with `-P`/`--permission-profile NAME`, `-p`/`--profile`,
`-C`/`--cd`, `--allow-unix-socket PATH`, `--log-denials`, and `--sandbox-state-*` options.

> [!NOTE]
> The docs list separate macOS, Linux, and Windows sandbox subcommands. The local macOS build shows one
> `codex sandbox` command whose help says "run under seatbelt". Check `codex sandbox -h` on the target
> platform.

`codex features enable`/`disable` edit `config.toml`; run them only for a persistent change and use
`--enable`/`--disable` for a one-off run.

---

## Interactive shortcuts

| Input | Effect |
|-------|--------|
| `@` | Search for a workspace file and insert its path |
| `!` prefix | Run a local shell command under the current approval and sandbox settings |
| Tab while working | Queue a prompt, slash command, or shell command for the next turn |
| Enter while working | Inject new instructions into the current turn |
| Ctrl+G | Open `VISUAL` (else `EDITOR`) for a long prompt |
| Ctrl+C, `/exit`, or `/quit` | Close the session; save or commit first |

---

## Slash commands by area

Slash commands come from the docs and were not verifiable from the terminal. Availability varies by
model, platform, and state. Codex hides `/fast` and `/personality` when the model lacks support.

### Session and chat

| Command | Purpose |
|---------|---------|
| `/new [NAME]`, `/clear [NAME]` | New chat; `/clear` also clears the terminal |
| `/resume`, `/fork` | Pick a saved chat / clone the current one |
| `/side [TEXT]`, `/btw` | Ephemeral side chat; unavailable in side chats and review mode |
| `/rename [NAME]` | Rename the current chat |
| `/archive`, `/delete` | Archive / permanently delete the current session and exit (`/delete` also removes descendants) |
| `/compact` | Summarize the chat to free context |
| `/copy` | Copy the latest completed output (also Ctrl+O) |
| `/app` | Continue in the ChatGPT desktop app (macOS, Windows) |

### Model and behavior

| Command | Purpose |
|---------|---------|
| `/model` | Choose model and reasoning effort |
| `/fast` | Toggle the Fast service tier when the model catalog offers one |
| `/personality` | `friendly`, `pragmatic`, or `none` |
| `/plan [PROMPT]` | Plan mode; unavailable while Codex is working |
| `/goal [OBJECTIVE\|edit\|pause\|resume\|clear]` | Persistent task goal, max 4,000 characters |
| `/memories` | Toggle memory use and generation |
| `/experimental` | Toggle experimental features; may need a restart |

### Permissions and safety

| Command | Purpose |
|---------|---------|
| `/permissions` | Change approval preset mid-session (for example Auto or Read Only), including named custom profiles |
| `/approve` | Retry one recently denied action from the automatic reviewer |
| `/hooks` | Inspect, trust, or disable non-managed lifecycle hooks; managed hooks cannot be disabled |
| `/setup-default-sandbox`, `/sandbox-add-read-dir PATH` | Windows only: elevated sandbox setup / read access to an extra directory |

### Context and tools

| Command | Purpose |
|---------|---------|
| `/mention PATH` | Attach a file to the chat |
| `/ide` | Include IDE selection and open files |
| `/mcp [verbose]` | List configured MCP servers and tools; any other argument prints usage |
| `/apps` | Insert an app (connector) as `$app-slug` |
| `/plugins` | Browse installed and discoverable plugins; Space toggles an installed plugin |
| `/skills` | Browse and apply skills |
| `/agent`, `/subagents` | Switch to a spawned subagent thread |
| `/ps`, `/stop` | List / stop background terminals (`/clean` aliases `/stop`) |
| `/import` | Import Claude Code or Cursor setup, projects, and chats from a local TUI session |

### Inspect and review

| Command | Purpose |
|---------|---------|
| `/status` | Active model, approval policy, writable roots, token usage |
| `/usage [daily\|weekly\|cumulative]` | Account token activity or reset redemption |
| `/debug-config` | Config layers (lowest precedence first) and policy sources |
| `/diff` | Git diff including untracked files |
| `/review` | Review the working tree; honors `review_model` in `config.toml` |
| `/feedback` | Send logs to the maintainers |
| `/init`, `/logout` | Write an `AGENTS.md` scaffold in the current directory / clear local credentials |

### TUI settings

`/theme` (`tui.theme`; custom `.tmTheme` files go in `$CODEX_HOME/themes`), `/statusline`
(`tui.status_line`), `/title` (`tui.terminal_title`), `/keymap` (`tui.keymap`; context bindings
override `tui.keymap.global`), `/vim` (default via `tui.vim_mode_default = true`), `/raw [on|off]`
(default via `tui.raw_output_mode = true`), `/pets [off]` (`/pet`). Each picker persists its choice
to `config.toml`.

---

## Customization and notifications

- **Shell completions**: `eval "$(codex completion zsh)"` in the shell profile. If zsh reports
  `command not found: compdef`, run `autoload -Uz compinit && compinit` first.
- **Notifications**: the CLI notification settings and the external-program `notify` hook live in the
  advanced configuration guide, not in this page's sources. Do not invent key names; confirm them
  against the config reference before writing them.

# CLI Commands, Options, and Slash Commands

Run `codex --help` or `codex <command> -h` for built-in help. Run `/` in a session to open the
slash-command popup. Flag tables below were verified against `codex-cli 0.162.1`; slash commands come
from the Codex docs and release notes and cannot be listed from the terminal.

> [!NOTE]
> Prefer local `-h` output over the docs when they differ. The upstream developer-commands page
> renders its flag tables as components, so most flag-level detail here comes from `-h`. In 0.162.1,
> `codex <group> <sub> --help` and `-h` both print the subcommand help; a single quoted string such
> as `codex 'mcp list' --help` is parsed as a prompt and prints the root help.

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
| `codex plugin add\|list\|remove\|marketplace` | Manage plugins and marketplaces (`add`/`remove PLUGIN[@MARKETPLACE]` or `-m MARKETPLACE`; `list [--available] [--json]`; `marketplace add SOURCE [--ref REF] [--sparse PATH]\|list\|upgrade [NAME]\|remove NAME`) |
| `codex features list\|enable\|disable` | Inspect or persist feature flags |
| `codex doctor` | Diagnose installation, config, auth, and runtime health |
| `codex debug models\|prompt-input\|app-server` | Debugging tools |
| `codex sandbox [COMMAND]...` | Run a command under the Codex sandbox; `codex sandbox uninstall` removes the legacy Windows sandbox's machine-wide accounts and network rules |
| `codex execpolicy check -r RULES... COMMAND...` | Check execpolicy rule files against a command (preview; not listed in `codex --help`, but `codex help execpolicy` works). Flags: `--pretty`, `--resolve-host-executables` |
| `codex agents` | Browse all agent sessions on the shared local app-server daemon (the agent command center). Takes `--remote`, `--remote-auth-token-env`, `-C`, `--no-alt-screen` |
| `codex migrate-rollouts [--apply]` | Report, or with `--apply` migrate, legacy local sessions to paginated thread history. Also `--thread ID`, `--max-mib-per-second N`, `--json`, `--verbose` |
| `codex app [PATH]` | Open a workspace in the ChatGPT desktop app (macOS, Windows); offers the installer when missing |
| `codex apply TASK_ID` (`codex a`) | Apply the latest diff from a Codex cloud task with `git apply` |
| `codex cloud [list\|exec\|status\|apply\|diff]` | Browse and submit Codex cloud tasks (experimental). `exec --env ENV_ID [--attempts N] [--branch B] [QUERY]`; `list [--env ID] [--limit N] [--cursor C] [--json]`; `status TASK_ID`; `apply`/`diff TASK_ID [--attempt N]` |
| `codex completion [SHELL]` | Shell completion script: `bash` (default), `elvish`, `fish`, `powershell`, `zsh` |
| `codex update` | Self-update when the installed release supports it |
| `codex app-server`, `codex remote-control`, `codex exec-server` | Experimental server tooling; may change without notice |

`codex mcp-server` was removed (the docs point to the Codex app server); `0.162.1` confirms it is gone.

Experimental server tooling, from `-h` on 0.162.1:

- `codex app-server` takes `--listen stdio://|unix://[PATH]|ws://IP:PORT|off`, `--code-mode-host`, and
  `--ws-*` authentication options, and has subcommands `daemon`, `proxy`, `generate-ts`, and
  `generate-json-schema`.
- `codex remote-control [start|stop|pair]` starts or stops the app-server daemon with remote control
  enabled; `pair` prints a short-lived pairing code. `--json` emits JSON and `--no-daemon` runs an
  embedded server in the foreground.
- `codex exec-server [--listen URL]` runs the standalone exec-server; `exec-server forward` registers
  an existing WebSocket exec-server as a remote environment.

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
> The docs describe `--profile` only as "profiles" in config. The `0.162.1` CLI defines `-p, --profile`
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

| `--cyber-access-program standard\|daybreak_blue\|daybreak_red` | Per-turn Cyber access program (OpenAI provider only; not supported with `review`; `fork` requires a prompt). Added in 0.161.0 |

`exec` also takes `-m`, `-p`, `-s`, `-C`, `-i`, `--add-dir`, `--oss`, `--local-provider`, `--worktree`,
`--approve-for-me`, `--dangerously-bypass-approvals-and-sandbox`, `--dangerously-bypass-hook-trust`,
`-c`, `--enable`, `--disable`, and `--strict-config`. `exec resume` adds `[SESSION_ID] [PROMPT]`,
`--last`, and `--all`; `exec resume`, `exec fork SESSION_ID [PROMPT]`, and `exec review` take the
model and output options (`-m`, `-i` except on `review`, `--json`, `-o`, `--output-schema`,
`--ephemeral`, `--skip-git-repo-check`, `--ignore-*`, `--worktree`) but not `-p`, `-s`, `-C`,
`--add-dir`, `--oss`, `--approve-for-me`, or `--color`. Pair `--json` with `--output-last-message`
in CI to capture progress and a final summary.

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
| `codex debug app-server send-message-v2 USER_MESSAGE` | Send one V2 thread/turn through the built-in app-server test client |
| `codex update` | Update the CLI; debug builds tell you to install a release build |
| `codex login status` | Exits `0` when credentials are present |
| `codex logout` | Removes saved API-key and ChatGPT credentials |

`codex login` opens a browser for ChatGPT OAuth by default. Alternatives: `--device-auth`,
`--with-api-key` (reads the key from stdin, for example `printenv OPENAI_API_KEY | codex login --with-api-key`), and `--with-access-token` (reads the token from stdin).

`codex sandbox` runs a command under the same policy Codex uses. The `0.162.1` CLI has one run form,
`codex sandbox [OPTIONS] [COMMAND]...`, with `-P`/`--permission-profile NAME`, `-p`/`--profile`,
`-C`/`--cd`, `--include-managed-config`, `--allow-unix-socket PATH` (repeatable), `--log-denials`
(macOS), and `--sandbox-state-json`, `--sandbox-state-readable-root`, and
`--sandbox-state-disable-network`. Its only subcommand is `codex sandbox uninstall` (added in 0.162.0).

> [!NOTE]
> The docs list separate `macos`, `linux`, and `windows` sandbox subcommands (with `seatbelt` and
> `landlock` aliases), a `--permissions-profile` flag, and `sandbox` under `codex debug`. None of that
> exists in 0.162.1: `codex debug` has only `models`, `app-server`, and `prompt-input`, and the flag is
> `-P/--permission-profile`. Check `codex sandbox -h` on the target platform.

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
| Up / Down | Restore draft history |
| Ctrl+R | Search prompt history; Enter uses a match, Escape cancels |
| Ctrl+O or `/copy` | Copy the latest completed output; Ctrl+Insert copies a selection (0.162.0 release notes) |
| Escape twice with an empty composer | Edit the previous user message and fork the chat from that point |
| Ctrl+L | Clear the terminal view only; the chat continues (unlike `/clear`) |
| Ctrl+G | Open `VISUAL` (else `EDITOR`) for a long prompt |
| Ctrl+C, `/exit`, or `/quit` | Close the session; save or commit first |

---

## Slash commands by area

Slash commands come from the docs and were not verifiable from the terminal. Availability varies by
model, platform, and state. Codex hides `/fast` when the model lacks support.

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
| `/plan [PROMPT]` | Plan mode; unavailable while Codex is working |
| `/goal [OBJECTIVE\|edit\|pause\|resume\|clear]` | Persistent task goal, max 4,000 characters |
| `/memories` | Toggle memory use and generation |
| `/experimental` | Toggle experimental features; may need a restart |
| `/personality` | Choose `friendly`, `pragmatic`, or `none`; hidden when the model lacks support. The `personality` feature is `removed` in 0.162.1, so treat this as legacy |

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
| `/mcp [verbose\|login NAME]` | List configured MCP servers and tools; `verbose` adds diagnostics; `login NAME` signs in to a server from the session (0.161.0 release notes; the docs still say any other argument prints usage) |
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
(default via `tui.raw_output_mode = true`), `/pets [off]` (`/pet`). The `/theme`, `/statusline`,
`/title`, `/keymap`, and `/pets` pickers persist their choice to `config.toml`; `/vim` and `/raw`
toggle for the current session only (Alt+R also toggles raw mode).

---

## Customization and notifications

- **Shell completions**: `eval "$(codex completion zsh)"` in the shell profile. If zsh reports
  `command not found: compdef`, run `autoload -Uz compinit && compinit` first.
- **Notifications**: the CLI notification settings and the external-program `notify` hook live in the
  advanced configuration guide, not in this page's sources. Do not invent key names; confirm them
  against the config reference before writing them.

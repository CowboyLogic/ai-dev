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
| `copilot config [KEY] [VALUE]` | Read or change settings outside a session (see below) |
| `copilot sandbox ca status\|create\|trust [CA.PEM]\|rotate\|remove` | Manage the sandbox proxy certificate authority without a session (see `permissions.md`) |
| `copilot workflow run WORKFLOW-NAME [--args JSON\|@PATH] [--result-file PATH] [-s] [--output-format text\|json]` | Run a dynamic workflow registered by an extension, without a chat prompt; can't be combined with `-p`, `-i`, `--agent`, `--fleet`, `--autopilot`, `--resume`, or `--continue` |
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

### `copilot config`

Non-interactive counterpart to `/settings`. Keys use dot notation.

```bash
copilot config theme                       # print a setting
copilot config footer.showQuota off        # set a nested value
copilot config allowedUrls github.com      # append to a list (only if absent)
copilot config --rm allowedUrls github.com # remove one list item (--rm KEY removes the key)
copilot config --repo --list --json        # list repo-overridable settings as JSON
```

| Option | Purpose |
|--------|---------|
| `--list` | List `key=value` lines (conflicts with `KEY`/`VALUE`/`--rm`) |
| `--json` | JSON output for `--list` |
| `--rm` | Remove the key or one list item; requires `KEY` |
| `--global` (default) / `--repo` / `--local` | User `settings.json`, `.github/copilot/settings.json`, or `.github/copilot/settings.local.json`; `--repo` and `--local` accept only repo-overridable settings |

Booleans take `on`/`off` or `true`/`false`. An unset key exits `1`; secret values are redacted. Put
`--` before a value that starts with a dash. Run `copilot help config` for the available settings.

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
| `--mcp-github-auth` | Scope GitHub account auth to approved MCP server origins (v1.0.90 release notes; not in the docs reference — run `copilot --help` for exact semantics) |
| `--plugin-dir=DIRECTORY` | Load a plugin from a local directory |
| `--extension-sdk-path=DIRECTORY` | Override the bundled `@github/copilot-sdk` injected into extension subprocesses (invalid paths fall back to the bundled SDK) |
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
`/sandbox [config|status|policy [COMMAND]|enable|disable]`, `/sandbox ca [create|trust|rotate|remove]`
(see `permissions.md`).

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
| `/collect-debug-logs [file\|gist\|share] [PATH]` | Collect debug logs into a local archive (`file`, at `PATH` when given), a secret GitHub gist (`gist`), or a local archive that is then uploaded to GitHub (`share`) |
| `/refine TEXT` | Rewrite a rough prompt into a clear one for review (no argument: clean up the input box) |
| `/workflows` | Observe workflow runs, phases, agents, and progress (needs a token-based-billing plan) |

### Account and app

`/login`, `/logout`, `/user [show|list|switch]`, `/remote [on|off]`, `/ide`, `/app`,
`/feedback` (`/bug`), `/changelog [summarize] [VERSION|last N|since VERSION]` (`/release-notes`),
`/update` (`/upgrade`), `/version`, `/voice`, `/copy`, `/search` (`/find`),
`/downgrade VERSION` (team accounts), `/clikit [COMPONENT]` (preview CLI business components),
`/tuikit [colors|icons|select|tabbar]` (preview TUIkit design-system components and color tokens),
`/exit` (`/quit`).

### Debug logs

`/collect-debug-logs` and the feedback-with-logs route offered from `/feedback` first save a local
archive. `share` and the feedback route then ask for fresh consent, defaulting to **No**, before
uploading to GitHub. Per the docs, uploading is currently available only to GitHub staff and
internal users; everyone else uses the `file` and `gist` routes and the existing public feedback
route.

## OpenTelemetry monitoring

Copilot CLI can export OpenTelemetry (OTel) traces and metrics, following the OTel GenAI Semantic
Conventions. It is off by default and has no overhead until one of these is set:
`COPILOT_OTEL_ENABLED=true`, `OTEL_EXPORTER_OTLP_ENDPOINT`, or `COPILOT_OTEL_FILE_EXPORTER_PATH`.
The docs also say OTel can be configured in VS Code or in an enterprise `managed-settings.json`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `COPILOT_OTEL_ENABLED` | `false` | Enable OTel explicitly (not needed when the endpoint variable is set) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | OTLP endpoint URL; setting it enables OTel |
| `COPILOT_OTEL_EXPORTER_TYPE` | `otlp-http` | `otlp-http` or `file`; `file` is selected automatically when the file path is set |
| `COPILOT_OTEL_FILE_EXPORTER_PATH` | — | Write all signals to this file as JSON lines; setting it enables OTel |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `http/json` | `http/json` or `http/protobuf` (`otlp-http` exporter only) |
| `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`, `OTEL_EXPORTER_OTLP_METRICS_PROTOCOL` | — | Per-signal override of the protocol |
| `OTEL_EXPORTER_OTLP_HEADERS` | — | Auth headers for the exporter, such as `Authorization=Bearer token` |
| `OTEL_SERVICE_NAME` | `github-copilot` | `service.name` resource attribute |
| `OTEL_RESOURCE_ATTRIBUTES` | — | Extra resource attributes as comma-separated `key=value` pairs (percent-encode special characters) |
| `COPILOT_OTEL_SOURCE_NAME` | `github.copilot` | Instrumentation scope name for the tracer and meter |
| `OTEL_LOG_LEVEL` | — | OTel diagnostic log level: `NONE`, `ERROR`, `WARN`, `INFO`, `DEBUG`, `VERBOSE`, `ALL` |
| `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | `false` | Capture full prompts, responses, system instructions, tool definitions, and tool arguments/results |

### Signals

- **Traces:** an `invoke_agent` root span per agent invocation, with `chat` (one per LLM request)
  and `execute_tool` child spans. Subagent invocations also use `invoke_agent` spans.
- **Metrics:** `gen_ai.client.operation.duration`, `gen_ai.client.token.usage`,
  `gen_ai.client.operation.time_to_first_chunk`, `gen_ai.client.operation.time_per_output_chunk`,
  `gen_ai.invoke_agent.duration`, `gen_ai.invoke_agent.inference_calls`,
  `gen_ai.invoke_agent.tool_calls`, `gen_ai.invoke_workflow.duration`, plus
  `github.copilot.tool.call.count`, `github.copilot.tool.call.duration`,
  `github.copilot.agent.turn.count`, `github.copilot.mcp.server.connection.count`,
  `github.copilot.code.lines_added`, and `github.copilot.code.lines_removed`.
- **Span events** on `chat` / `invoke_agent` spans: `github.copilot.hook.start`, `.hook.end`,
  `.hook.error`, `.session.truncation`, `.session.compaction_start`, `.session.compaction_complete`,
  `.skill.invoked`, `.session.shutdown`, `.session.abort`, and `exception`.

> [!WARNING]
> By default only metadata (model names, token counts, durations) is captured. Content capture can
> include code, file contents, and prompts; enable it only in trusted environments.

To measure AI-unit consumption, read `github.copilot.nano_aiu` from the root `invoke_agent` span
only: it is also stamped on child `chat` spans, so summing across spans double-counts.
`github.copilot.cost` is a per-request model multiplier used for billing, not a monetary value.

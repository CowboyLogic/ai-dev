# V2 Config Schema Reference

Native OpenCode V2 shape for `opencode.json(c)`. Sources: <https://opencode.ai/v2/docs/config/>,
<https://opencode.ai/v2/docs/migrate-v1/>, and the per-topic V2 pages linked below.

> [!IMPORTANT]
> The V2 docs tell you to use `"$schema": "https://opencode.ai/config.json"`, but that schema currently
> describes only the **V1** shape and sets `additionalProperties: false`. Editors that validate against it
> will flag native V2 keys (`permissions`, `agents`, `providers`, `commands`, `plugins`, `snapshots`, `media`,
> `update`, `warming`, `websearch`, `worktree`). OpenCode V2 itself accepts them. No separate V2 config schema
> URL was found (`https://opencode.ai/v2/config.json` returns 404). Keep the `$schema` line as documented and
> expect editor warnings on V2 keys.

## Table of Contents

- [Locations and precedence](#locations-and-precedence)
- [Top-level fields](#top-level-fields)
- [Fields V2 ignores](#fields-v2-ignores)
- [Commands](#commands)
- [Skills](#skills)
- [Formatters](#formatters)
- [Compaction](#compaction)
- [Media (image limits)](#media-image-limits)
- [Web search](#web-search)
- [Warming](#warming)
- [References](#references)
- [Worktrees](#worktrees)
- [Instructions](#instructions)
- [Experimental](#experimental)
- [Environment and service settings](#environment-and-service-settings)
- [Annotated example](#annotated-example)

---

## Locations and precedence

| Scope | Path |
|-------|------|
| System (managed, machine-wide) | macOS `/Library/Application Support/opencode`, Linux `/etc/opencode`, Windows `%ProgramData%\opencode` (`opencode.json(c)` plus `agents/`, `commands/`, `skills/`, `plugins/`) |
| macOS managed preferences (MDM) | `/Library/Managed Preferences/<user>/ai.opencode.managed.plist`, then `/Library/Managed Preferences/ai.opencode.managed.plist` (domain `ai.opencode.managed`; the user-specific profile replaces the machine-wide one) |
| Global | `~/.config/opencode/opencode.json` or `opencode.jsonc` |
| Project (direct) | `<dir>/opencode.json(c)` |
| Project (`.opencode`) | `<dir>/.opencode/opencode.json(c)` |
| CLI client (not this file) | `~/.config/opencode/cli.json` — see [cli.md](cli.md) |

JSON and JSONC are both supported; JSONC allows comments and trailing commas.

OpenCode searches from the current directory **up to the filesystem root**. It merges direct
`opencode.json(c)` files from the farthest directory to the closest, **then** merges `.opencode/opencode.json(c)`
files in the same order. Every discovered `.opencode` config therefore overrides every direct config.
Use one form throughout a directory tree unless you need that behavior.

The system directory and macOS managed preferences have the **highest** precedence, so users and projects cannot
override the settings they set (managed preferences override the system directory). Overriding a setting cannot stop
a user from adding providers, MCP servers, agents, or plugins; enforce those restrictions with
[`policies`](permissions.md#policies). This is the 2.0.29 docs behavior: the 2.0.28 release notes say the system
directory loaded at the *lowest* precedence, and the 2.0.29 notes give centrally managed configuration precedence
over local and user configuration. Behavior on 2.0.28 or earlier differs.

Settings merge; non-conflicting keys are preserved. Exceptions to "closest wins":

- `permissions` arrays **append** (lower-priority files first, agent rules last) — see [permissions.md](permissions.md).
- `plugins` arrays apply from lowest to highest precedence rather than replacing each other.
- `skills` arrays from every discovered config are combined.
- `policies` reverse precedence: broader config (Console, managed, system, global) wins over project config.
- An MCP server with the same name in a higher-precedence file **replaces** the whole server object.
- `update` is read from the global config only; project-level values are ignored.

---

## Top-level fields

| Key | Type | Notes | Reference |
|-----|------|-------|-----------|
| `$schema` | string | `"https://opencode.ai/config.json"` (see note above) | — |
| `shell` | string | Shell for the terminal and shell tools | — |
| `model` | string or object | `provider/model`; root default does **not** retain a `#variant` | [providers.md](providers.md) |
| `default_agent` | string | Must exist, be visible, and be primary-capable; else falls back to `build`, then first visible primary agent | [agents.md](agents.md) |
| `update` | `"disable"` \| `"notify"` \| `"auto"` | Default `"notify"`. Global config only. `auto` does not restart a running server | — |
| `share` | `"manual"` \| `"auto"` \| `"disabled"` | Accepted by the schema, but the session-sharing backend and `/share` command were removed in 2.0.30 and the 2.2.5 docs drop the field | — |
| `timezone` | string | IANA time zone for schedules (for example `America/Los_Angeles`); defaults to the server's zone. In the 2.2.5 config schema, not in the docs pages | — |
| `username` | string | Accepted but not displayed in conversations | — |
| `permissions` | array of `{action, resource, effect}` | Ordered, last match wins | [permissions.md](permissions.md) |
| `agents` | object | Agent definitions keyed by ID | [agents.md](agents.md) |
| `commands` | object | Slash commands keyed by name | [Commands](#commands) |
| `providers` | object | Providers and model overrides | [providers.md](providers.md) |
| `mcp` | object | `mcp.servers.<name>` plus `mcp.timeout` defaults | [mcp.md](mcp.md) |
| `plugins` | array | Package strings or `{package, options}` | [plugins.md](plugins.md) |
| `skills` | array of strings | Extra skill directories or HTTP catalog URLs | [Skills](#skills) |
| `snapshots` | boolean | Default `true` | — |
| `watcher` | object | `{ "ignore": ["dist/**"] }` | — |
| `formatter` | boolean or object | Disabled unless set | [Formatters](#formatters) |
| `media` | object | `media.image` resize limits | [Media](#media-image-limits) |
| `tool_output` | object | `max_lines`, `max_bytes` retained from a tool result (docs example: `2000`, `51200`) | — |
| `websearch` | object or `false` | `{ "provider": "exa" \| "firecrawl" \| "parallel" \| "tavily" \| "tinyfish" \| "random" }` | [Web search](#web-search) |
| `compaction` | object | `auto`, `keep.tokens`, `buffer` (token count or percentage) | [Compaction](#compaction) |
| `warming` | boolean or object | Disabled by default | [Warming](#warming) |
| `references` | object | Named local dirs or Git repos | [References](#references) |
| `worktree` | object | `{ "directory": "../worktrees" }` | [Worktrees](#worktrees) |
| `instructions` | array | Files, globs, and HTTP(S) URLs loaded after `AGENTS.md` (2.0.30+) | [Instructions](#instructions) |
| `policies` | array | Ordered `{ action, resource, effect }` statements; actions `provider.use`, `tool.use`, `integration.connect`, `integration.use`, `mcp.use`, `skill.use`, `plugin.use` (2.2.3+ for the last four; `experimental.policies` is deprecated but still merges in) | [permissions.md](permissions.md#policies) |
| `experimental` | object | See [Experimental](#experimental) | [Experimental](#experimental) |

Fields that keep the V1 shape and need no migration: `shell`, `model`, `default_agent`, `watcher`, `formatter`,
`instructions`, `enterprise`, `tool_output`.

`lsp` is accepted and preserved, but V2 does **not** run language servers, expose LSP tools, or produce LSP
diagnostics. Point agents at lint/typecheck commands instead.

### Snapshots

```jsonc
{ "snapshots": false }
```

Snapshots require a Git repository and cover the session's active directory (tracked files plus non-ignored
untracked files up to 2 MiB each). Disabling them does not delete stored snapshots. `/undo` (`<leader>u`) stages a
rollback; `/redo` (`<leader>r`) cancels it.

---

## Fields V2 ignores

V2 accepts these V1 values, ignores them, and logs a warning:

| V1 field | V2 replacement |
|----------|----------------|
| `logLevel` | `OPENCODE_LOG_LEVEL` env var when starting OpenCode |
| `server` | V2 service settings (`opencode service set ...`) and `serve` flags |
| Top-level `subagent_depth` | `experimental.subagent_depth` |
| `compaction.tail_turns`, `compaction.prune` | `compaction.keep.tokens` |
| Agent `name` inside JSON config | Use the map key |
| An `enabled`-only MCP entry without `type` | Full V2 server entry |
| `experimental.batch_tool`, `openTelemetry`, `primary_tools`, `continue_loop_on_deny` | None |
| Provider `id`, `whitelist`, `blacklist` | `disabled: true` on models; policies for providers |
| Model `release_date`, `attachment`, `reasoning`, `temperature`, `experimental`, non-`deprecated` `status`, boolean `interleaved` | `capabilities`, `compatibility`, `disabled` |

V1 fields that V2 **normalizes silently** (still work, but have native V2 equivalents):
`enabled_providers` / `disabled_providers` (become `provider.use` policies), `experimental.policies` (merges into `policies`), `autoupdate` (becomes `update`),
`small_model` (becomes `agents.title.model`), `autoshare` (becomes `share`). See [migration.md](migration.md).

---

## Commands

Define under `commands` (plural) or as Markdown files. Each JSON command requires `template`.

```jsonc
{
  "commands": {
    "audit": {
      "template": "Audit $ARGUMENTS.",
      "description": "Audit a package",
      "agent": "general",
      "model": "anthropic/claude-sonnet-4-5#high",
      "subagent": true,
    },
  },
}
```

| Field | Required | Behavior |
|-------|----------|----------|
| `template` | JSON only | Prompt template (Markdown files use the body instead — never put `template` in frontmatter) |
| `description` | No | Shown in command lists |
| `agent` | No | Agent selected when the command runs (switches the current session to it) |
| `model` | No | `provider/model` or `provider/model#variant`; overrides every other model |
| `subagent` | No | `true` = background child session; `false` = current session; omitted = child only if the agent is `mode: subagent` |
| `subtask` | No | Deprecated alias for `subagent`; `subagent` wins if both are set |

Markdown locations: `~/.config/opencode/commands/<name>.md` and `.opencode/commands/<name>.md` (legacy `command/`
still discovered). Nested paths become names with `/` (`.opencode/commands/team/review.md` → `/team/review`).
Project sources override global; nearer project sources override ancestors; a custom command can replace a built-in.

Template syntax:

| Syntax | Behavior |
|--------|----------|
| `$ARGUMENTS` | Full argument string as entered |
| `$1`, `$2`, … | Positional args; quotes group words; the highest-numbered placeholder consumes the rest |
| (no placeholder) | Non-empty arguments are appended after a blank line |
| `` !`cmd` `` | Shell output inserted before submit (placeholders expand first — don't put untrusted args in shell blocks) |
| `@path` | **Not expanded** in stored templates in V2; attach files through the composer instead |

---

## Skills

```jsonc
{ "skills": ["./team-skills", "~/shared/opencode-skills", "/opt/company-skills", "https://example.com/opencode/skills/"] }
```

- Relative paths resolve from the **working directory**, not the config file.
- URLs are HTTP catalogs: `<base>/index.json` listing `{ "name", "version", "files" }`.
- Automatic discovery (no config needed): `~/.config/opencode/skills`, `~/.claude/skills`, `~/.agents/skills`,
  and project `.opencode/skills`, `.claude/skills`, `.agents/skills` from cwd up to the project root.
- A source holds root-level `*.md` files or `SKILL.md` files nested in grouping directories
  (`skills/git-release/SKILL.md`, `skills/teams/release/SKILL.md`). A directory containing `SKILL.md` is one skill and
  is not searched for more; hidden files and directories and `node_modules` are skipped; search stops six directories
  below the source root (2.2.5 docs). The **path** determines the skill ID (`git-release/SKILL.md` → `git-release`);
  frontmatter `name` is a display label only. In an HTTP catalog each downloaded skill directory becomes a source root
  named after the entry, so `git-release.md` and a root-level `SKILL.md` both get the ID `git-release`.
- `OPENCODE_DISABLE_CLAUDE_CODE` and `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS` are honored when discovering `.claude`
  skills (2.0.30 release notes).
- Frontmatter: `name`, `description` (required for the model to see it), `metadata.opencode/autoinvoke` (`false`
  hides the skill from the model's list), and `disable-model-invocation` (`true` has the same effect; if both are
  set, `opencode/autoinvoke` wins). The skill stays registered and can still be loaded explicitly by ID, or in a
  prompt as `@skill-id`. The `slash` and `metadata.opencode/slash` fields are no longer in the 2.0.29 docs.
- Precedence (low → high): built-ins, `.claude/skills`, `.agents/skills`, `~/.config/opencode/skills`, project
  `.opencode/skills`, explicit `skills` entries.
- Gate loading with the `skill` permission action (resource = skill ID).

---

## Formatters

Disabled unless a config file sets `formatter`. `true` enables every built-in whose requirements are met and resets
inherited formatter settings to the built-ins. An object also enables the built-ins; an empty object `{}`
**preserves** inherited formatter settings rather than resetting them. `false` disables all, including formatting
that a lower-priority config file enabled.

```jsonc
{
  "formatter": {
    "prettier": { "disabled": true },
    "deno-markdown": { "command": ["deno", "fmt", "$FILE"], "extensions": [".md"] },
  },
}
```

| Field | Type | Behavior |
|-------|------|----------|
| `disabled` | boolean | Removes the named formatter |
| `command` | string[] | Argument array (not a shell string); `$FILE` becomes the absolute file path; runs from the project directory |
| `environment` | object | Extra env vars |
| `extensions` | string[] | Final extension match, case-sensitive, leading dot required |

A custom formatter needs both `command` and `extensions`. When several match, OpenCode tries them in order
(built-ins first, then custom in object order) and stops after the first success.

Built-ins: `gofmt`, `mix`, `oxfmt`, `prettier`, `biome`, `zig`, `clang-format`, `ktlint`, `ruff`, `air`, `uv`,
`rubocop`, `standardrb`, `htmlbeautifier`, `dart`, `ocamlformat`, `terraform`, `latexindent`, `gleam`, `shfmt`,
`nixfmt`, `rustfmt`, `pint`, `ormolu`, `cljfmt`, `dfmt`.

---

## Compaction

```jsonc
{ "compaction": { "auto": true, "keep": { "tokens": 15000 } } }
```

| Field | Default | Behavior |
|-------|---------|----------|
| `auto` | `true` | Compact automatically near the context limit, and recover once when a provider rejects a request as too long; manual compaction always works |
| `keep.tokens` | `15000` | Approximate recent conversation kept beside the summary |
| `buffer` | `"15%"`, at least 16k (2.2.5 docs) | Share of the model's context window kept free; automatic compaction starts once the conversation reaches the rest |

`keep.tokens` accepts a non-negative integer. `buffer` (2.2.5) accepts a percentage string from `"1%"` to `"99%"`,
decimals included, or a token count. `"20%"` compacts at 80% full, which is about 102k tokens on a 128k window and
800k on a 1M window. A token count at least as large as the model's window is ignored and the default applies.
The 2.0.16 docs gave `buffer` a fixed default of `20000` and the 2.0.29 docs said 10% of the limit; the 2.2.5 docs say
`"15%"` with a 16k floor, so set it explicitly if you depend on a specific value.

Summaries cover the entire current conversation and keep the most recent `keep.tokens` beside the summary; sending the
full conversation lets the summary request reuse the normal request's prompt cache where the provider supports it
(2.1.0 notes, 2.2.5 docs). Set `agents.compaction.model` to write summaries with a different model than the session's.
`experimental.background_compaction: true` (2.1.4) prepares a summary in the background as a session nears its
threshold; summaries that are never used still cost tokens.

Native provider compaction is opt-in per provider or model:
`providers.<id>.settings.compaction.type` = `"native"` or `"summary"` (model setting overrides provider). Native
compaction supports OpenAI Responses models, and its encrypted checkpoint only works with the same provider, model,
and endpoint. Compaction uses the session's model unless `agents.compaction.model` is set.

Request compaction on demand with `opencode api post /api/session/<session-id>/compact --data '{}'`.

---

## Media (image limits)

```jsonc
{ "media": { "image": { "auto_resize": true, "max_width": 2000, "max_height": 2000, "max_base64_bytes": 5242880 } } }
```

Applies to prompt attachments and images returned by `read`. `auto_resize: false` rejects oversized images.
Prompt attachments support UTF-8 text, directories, PNG, JPEG, GIF, WebP (PDF and other binaries are not sent to
the model); 20 MiB per item.

---

## Web search

```jsonc
{ "websearch": { "provider": "tavily" } }   // "exa" | "firecrawl" | "parallel" | "tavily" | "tinyfish" | "random"
{ "websearch": false }                      // remove the tool
```

Credentials: `/connect` or `EXA_API_KEY`, `FIRECRAWL_API_KEY`, `PARALLEL_API_KEY`, `TAVILY_API_KEY`, and
`TINYFISH_API_KEY` (optional for TinyFish).
`random` rotates to another provider on HTTP 429.

---

## Warming

Keeps provider prompt caches warm with periodic transient requests. Off by default; costs real tokens.

```jsonc
{ "warming": true }   // 4-minute interval, 30-minute window
{ "warming": { "prompt": "Do not perform any work. Reply with exactly: OK", "interval": "5 minutes", "duration": "1 hour" } }
```

`interval` and `duration` are duration strings that must resolve to finite values greater than zero.

---

## References

```jsonc
{
  "references": {
    "docs": { "path": "../product-docs", "description": "Use for product behavior and terminology" },
    "effect": { "repository": "Effect-TS/effect", "branch": "main" },
    "shared": "~/work/shared",
  },
}
```

| Field | Local | Git | Notes |
|-------|-------|-----|-------|
| `path` | Required | — | Relative to the config file; absolute and `~/` allowed |
| `repository` | — | Required | `owner/repo`, Git URL, host/path, or SCP-style; no `file:` repos |
| `branch` | — | Optional | Defaults to the remote default branch |
| `description` | Optional | Optional | Only described references are advertised to agents |
| `hidden` | Optional | Optional | Hide from interactive selectors only |

Git checkouts live under `~/.local/share/opencode/repos/<host>/<path>` and refresh at most every 24 hours.
References grant no extra permissions — `external_directory` rules still apply. The V1 singular `reference` key is
deprecated; use `references`.

---

## Worktrees

```jsonc
{ "worktree": { "directory": "../worktrees" } }
```

Relative paths resolve against the project's canonical checkout; `~/` resolves to home. Without it, worktrees go
under the server data directory at `worktree/<first-six-project-ID-characters>`.

---

## Instructions

V2 loads `AGENTS.md` files only: `~/.config/opencode/AGENTS.md` plus every `AGENTS.md` from the workspace up to
home (stops at the project root for workspaces outside home). Nested `AGENTS.md` files load as the agent reads
those areas. `CLAUDE.md` is **not** discovered in V2.

The `instructions` array (2.0.30+; earlier releases accepted it without loading it) adds files, globs, or HTTP(S) URLs
that load **after** the discovered `AGENTS.md` files, in listed order; entries from every config document combine:

| Entry | Resolution |
|-------|------------|
| Relative path or glob | Searched in each directory from the workspace up to the project root |
| `~/` path | Resolved from the home directory |
| Absolute path | Used as written; the file name may be a glob |
| `http://` or `https://` | Fetched when config loads, with a five-second timeout |

Local files update like `AGENTS.md` when they change; new files matching a glob load on the next config change. Missing
files are skipped, and an unreachable URL is skipped or keeps its last fetched content.
`OPENCODE_DISABLE_PROJECT_CONFIG=1` skips project `AGENTS.md` discovery and resolves relative entries against the global
config directory.

---

## Environment and service settings

V2 runs a shared background server per user. Environment variables for model requests must reach **that server
process**:

```bash
opencode service set env ANTHROPIC_API_KEY sk-ant-...   # persist for the background service (restarts it)
opencode service unset env ANTHROPIC_API_KEY
opencode --standalone                                   # private server that uses the current shell env
```

To make private servers the default instead of starting the shared one, run `opencode service set disabled true`
(this stops the running service; undo with `opencode service unset disabled`). `--server` still reaches an explicit
server, `opencode service start` still starts the shared service, and `opencode pair` needs the shared service, so
it is unavailable while it is disabled.

Remote access: `opencode pair --remote` pairs through an OpenTunnel address and turns remote access on if it is off.
That exposes the server to the internet, so the first time it asks you to accept; without an interactive terminal it
fails unless you also pass `--yes`. Once accepted, later runs skip the prompt, even after
`opencode service set remote false`. The remote URL is a random subdomain that persists across restarts; turning
remote access off and on again issues a new one (2.0.26 release notes). Both flags are in the V2 CLI docs (unchanged through 2.0.29)
and were in the 2.0.27 `opencode pair --help`.

| Variable | Purpose |
|----------|---------|
| `OPENCODE_LOG_LEVEL` | Log level (replaces V1 `logLevel`) |
| `OPENCODE_DB` | Override the SQLite database path |
| `OPENCODE_CLI_CONFIG_CONTENT` | Inline JSON merged over `cli.json` |
| `OPENCODE_DISABLE_PROJECT_CONFIG` | Skip project `AGENTS.md` discovery |
| `OPENCODE_PASSWORD` | Server HTTP Basic password (`OPENCODE_SERVER_PASSWORD` still works; `OPENCODE_SERVER_USERNAME` is no longer supported and the username is always `opencode`) |
| `OPENCODE_CLAUDE_PATH` | Override the Claude executable used by the Claude Agent provider |
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | Proxy; `NO_PROXY` must include `localhost,127.0.0.1,::1` |
| `NODE_EXTRA_CA_CERTS` | Extra CA bundle (PEM) |

> [!NOTE]
> The V2 docs do not mention `OPENCODE_CONFIG`, `OPENCODE_CONFIG_CONTENT`, `OPENCODE_CONFIG_DIR`, or remote
> `.well-known/opencode` config. Treat those as V1-documented only; verify with `opencode debug config` before
> relying on them in V2. System-directory and macOS managed-preference settings are documented in V2 from 2.0.29
> (see [Locations and precedence](#locations-and-precedence)).

The shared server listens on localhost only. Its default port is 49374 on macOS, Linux, and WSL and 28894 on Windows
(2.1.3 notes and the 2.2.5 web docs; Windows reserves ports from 49152 up). `opencode service status` prints the current
address. `opencode debug heap-dump [--directory <dir>]` writes a heap snapshot of the running server (2.1.4).

Useful diagnostics: `opencode debug config` (list configuration sources), `opencode debug paths`,
`opencode reload` (reload configuration without restarting the server), `opencode service status`.

Variable substitution: the 2.2.5 config docs document both forms inside JSON strings. `{env:NAME}` is replaced with
the variable's value (empty string when unset). `{file:path}` is replaced with the file's contents; the path is
relative to the config file's directory, absolute, or starts with `~/`; a missing file becomes an empty string. Earlier
V2 docs showed only `{env:}`; `{file:}` was verified working on the 2.0.27 binary for an agent `system` value. The
2.2.5 binary was not run.

---

## Experimental

All keys live under `experimental` and may change or disappear in any release. Verified against the 2.2.5 docs and
config schema (`packages/schema/src/config/experimental.ts`).

| Key | Type / default | Effect |
|-----|----------------|--------|
| `todo` | boolean, `false` | Gives agents the `todowrite` tool (2.1.0; todos are off by default in V2) |
| `subagent_depth` | integer, `1` | How deeply subagents can start their own subagents |
| `background_compaction` | boolean, `false` | Writes the compaction summary in the background; unused summaries still cost tokens |
| `image_generate` | boolean or `{ model }` | Default model for `experimental_image_generate` as `providerID/modelID[#variant]`; the tool appears while a connected provider has an image model, and since 2.2.2 needs no other setup |
| `location_idle_timeout` | duration string or `false`, `"60 minutes"` | How long a project location can be idle before its services unload; running sessions and background jobs keep it loaded; project config can override global |
| `schedules` | boolean, `false` | Opt-in scheduled prompts (`/schedule`, agent tools); `timezone` sets the zone. Release-notes only |
| `artifacts` | boolean, `false` | Opt-in `artifact_create`/`artifact_read`/`artifact_update`/`artifact_delete` with a local static-file provider (2.2.4). Release-notes and schema only |
| `media_blob` | boolean, `false` | Stores new session media once in a deduplicated blob table (2.2.0). Schema and release notes only |
| `policies` | array | Deprecated; use top-level `policies` |
| `portable_shell_scanner` | boolean | Deprecated; the scanner is always on |

`OPENCODE_DISABLE_FREE_MODELS=1` (or `true`) on the server process hides zero-input-price `opencode` and `opencode-go`
models from catalogs and defaults (2.1.2); selecting one then fails with `Model unavailable`. For the shared background
server use `opencode service set env OPENCODE_DISABLE_FREE_MODELS 1`.

---

## Annotated example

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5",
  "default_agent": "build",
  "update": "notify",
  "snapshots": true,
  "formatter": true,

  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" },
  ],

  "agents": {
    "title": { "model": "anthropic/claude-haiku-4-5" },
    "reviewer": {
      "description": "Review changes without editing files",
      "mode": "subagent",
      "system": "Focus on correctness, security, and missing tests.",
      "permissions": [{ "action": "edit", "resource": "*", "effect": "deny" }],
    },
  },

  "mcp": {
    "servers": {
      "context7": { "type": "remote", "url": "https://mcp.context7.com/mcp" },
    },
  },

  "commands": {
    "review": { "description": "Review the current changes", "template": "Review the current diff for correctness and missing tests." },
  },

  "skills": ["./team-skills"],
  "plugins": ["opencode-example-plugin"],

  "policies": [{ "action": "provider.use", "resource": "openai", "effect": "deny" }],
}
```

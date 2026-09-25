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
- [Environment and service settings](#environment-and-service-settings)
- [Annotated example](#annotated-example)

---

## Locations and precedence

| Scope | Path |
|-------|------|
| Global | `~/.config/opencode/opencode.json` or `opencode.jsonc` |
| Project (direct) | `<dir>/opencode.json(c)` |
| Project (`.opencode`) | `<dir>/.opencode/opencode.json(c)` |
| CLI client (not this file) | `~/.config/opencode/cli.json` — see [cli.md](cli.md) |

JSON and JSONC are both supported; JSONC allows comments and trailing commas.

OpenCode searches from the current directory **up to the filesystem root**. It merges direct
`opencode.json(c)` files from the farthest directory to the closest, **then** merges `.opencode/opencode.json(c)`
files in the same order. Every discovered `.opencode` config therefore overrides every direct config.
Use one form throughout a directory tree unless you need that behavior.

Settings merge; non-conflicting keys are preserved. Exceptions to "closest wins":

- `permissions` arrays **append** (lower-priority files first, agent rules last) — see [permissions.md](permissions.md).
- `plugins` arrays apply from lowest to highest precedence rather than replacing each other.
- `skills` arrays from every discovered config are combined.
- `experimental.policies` reverse precedence: broader config (global, Console) wins over project config.
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
| `share` | `"manual"` \| `"auto"` \| `"disabled"` | Accepted, but V2 does not support session sharing yet | — |
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
| `websearch` | object or `false` | `{ "provider": "exa" \| "firecrawl" \| "parallel" \| "tavily" \| "random" }` | [Web search](#web-search) |
| `compaction` | object | `auto`, `keep.tokens`, `buffer` | [Compaction](#compaction) |
| `warming` | boolean or object | Disabled by default | [Warming](#warming) |
| `references` | object | Named local dirs or Git repos | [References](#references) |
| `worktree` | object | `{ "directory": "../worktrees" }` | [Worktrees](#worktrees) |
| `instructions` | array | **Accepted but not loaded** in V2 — use `AGENTS.md` | [Instructions](#instructions) |
| `experimental` | object | `policies`, `subagent_depth`, `portable_shell_scanner` | [permissions.md](permissions.md) |

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
`enabled_providers` / `disabled_providers` (become `provider.use` policies), `autoupdate` (becomes `update`),
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
- A source holds root-level `*.md` files or `SKILL.md` at any depth. The **path** determines the skill ID
  (`git-release/SKILL.md` → `git-release`); frontmatter `name` is a display label only.
- Frontmatter: `name`, `description` (required for the model to see it), `slash` (`false` hides from command
  catalogs), `metadata.opencode/slash`, `metadata.opencode/autoinvoke` (`false` hides from the model's list).
- Precedence (low → high): built-ins, `.claude/skills`, `.agents/skills`, `~/.config/opencode/skills`, project
  `.opencode/skills`, explicit `skills` entries.
- Gate loading with the `skill` permission action (resource = skill ID).

---

## Formatters

Disabled by default. `true` (or `{}`) enables every built-in whose requirements are met; `false` disables all.

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
{ "compaction": { "auto": true, "keep": { "tokens": 15000 }, "buffer": 20000 } }
```

| Field | Default | Behavior |
|-------|---------|----------|
| `auto` | `true` | Preflight auto-compaction plus one overflow-recovery retry; does not affect manual compaction |
| `keep.tokens` | `15000` | Recent context retained beside the summary |
| `buffer` | `20000` | Safety margin below the input limit; larger starts compaction earlier |

Native provider compaction is opt-in per provider or model:
`providers.<id>.settings.compaction.type` = `"native"` or `"summary"` (model setting overrides provider).
There is no separate compaction model.

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
{ "websearch": { "provider": "tavily" } }   // "exa" | "firecrawl" | "parallel" | "tavily" | "random"
{ "websearch": false }                      // remove the tool
```

Credentials: `/connect` or `EXA_API_KEY`, `FIRECRAWL_API_KEY`, `PARALLEL_API_KEY`, `TAVILY_API_KEY`.
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

The `instructions` array is accepted by the schema but V2 **does not currently load** its files, globs, or URLs.
`OPENCODE_DISABLE_PROJECT_CONFIG=1` skips project `AGENTS.md` discovery.

---

## Environment and service settings

V2 runs a shared background server per user. Environment variables for model requests must reach **that server
process**:

```bash
opencode service set env ANTHROPIC_API_KEY sk-ant-...   # persist for the background service (restarts it)
opencode service unset env ANTHROPIC_API_KEY
opencode --standalone                                   # private server that uses the current shell env
```

| Variable | Purpose |
|----------|---------|
| `OPENCODE_LOG_LEVEL` | Log level (replaces V1 `logLevel`) |
| `OPENCODE_DB` | Override the SQLite database path |
| `OPENCODE_CLI_CONFIG_CONTENT` | Inline JSON merged over `cli.json` |
| `OPENCODE_DISABLE_PROJECT_CONFIG` | Skip project `AGENTS.md` discovery |
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | Proxy; `NO_PROXY` must include `localhost,127.0.0.1,::1` |
| `NODE_EXTRA_CA_CERTS` | Extra CA bundle (PEM) |

> [!NOTE]
> The V2 docs do not mention `OPENCODE_CONFIG`, `OPENCODE_CONFIG_CONTENT`, `OPENCODE_CONFIG_DIR`, remote
> `.well-known/opencode` config, or file/MDM managed settings. Treat those as V1-documented only; verify with
> `opencode debug config` before relying on them in V2.

Useful diagnostics: `opencode debug config` (list configuration sources), `opencode debug paths`,
`opencode reload` (reload configuration without restarting the server), `opencode service status`.

Variable substitution: V2 docs use `{env:NAME}` throughout. `{file:path}` is not shown in V2 docs.

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

  "experimental": {
    "policies": [{ "action": "provider.use", "resource": "openai", "effect": "deny" }],
  },
}
```

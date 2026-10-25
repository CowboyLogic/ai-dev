# V1 → V2 Migration Reference

Source: <https://opencode.ai/v2/docs/migrate-v1/> (2.1.4 tag).

## What actually breaks

V2 has three intentional breaking changes:

1. Plugins use a new API — V1 plugin code does not run (see [plugins.md](plugins.md)).
2. The server API and clients have new contracts (`@opencode/client`).
3. Terminal client config moves from layered `tui.json(c)` files to one global `cli.json` (auto-migrated once;
   see [cli.md](cli.md)).

Everything else is meant to stay compatible. V2 reads the same config locations and **normalizes supported V1
fields in memory without rewriting the file**. Converting to native V2 is optional.

> [!CAUTION]
> V1 and V2 share config locations and both use the `opencode` command. Do not point V1 at a file you have
> converted to native V2-only shapes. Keep a copy of the V1 setup until V2 is verified.
>
> The V1 1.19.0 CLI docs list `opencode upgrade --major`, described as "Upgrade to OpenCode 2 and remove
> OpenCode 1", and the V1 1.19.2 release notes name it (and the 2.0 offer in `/update`) as the explicit path to
> OpenCode 2; 1.x installs are not offered 2.x as a regular update. The flag is a **V1** option: the 2.1.4
> `opencode upgrade --help` lists only `--method`. Back up the V1 config and any V1 plugins before running it.

## Mixing rules

- V1 and V2 fields may coexist at the **top level**. When both set the same value, a valid native V2 value wins
  regardless of key order.
- Mixed V1/V2 members are recognized inside `mcp`, `compaction`, and `experimental` only.
- Individual **agents, providers, commands, and models are not format-inferred** — keep each nested entry entirely
  in one format.
- Malformed values, unsupported legacy fields, and conflicting V1/V2 values produce warnings; unrelated settings
  still load.

## Top-level renames

| V1 | V2 |
|----|----|
| `autoshare: true` | `share: "auto"` (the 2.1.4 migration guide dropped this section: session sharing is gone — V1 1.19.1 discontinued it and 2.0.30 removed the V2 backend and `/share`; the 2.1.4 source still normalizes `autoshare`) |
| `permission` (object) + `tools` (booleans) | `permissions` (ordered array) |
| `agent`, `mode` | `agents` (entries from `mode` become primary agents) |
| `snapshot` | `snapshots` |
| `attachment` | `media` |
| `command` | `commands` |
| `reference` | `references` |
| `provider` | `providers` |
| `plugin` | `plugins` (a configured local path must be a directory with an `index` or `server` module) |
| `skills: { paths, urls }` | `skills: [ ...paths, ...urls ]` |
| `autoupdate: false` / `"notify"` / `true` | `update: "disable"` / `"notify"` / `"auto"` |
| `small_model` | `agents.title.model` |
| `enabled_providers` / `disabled_providers` | `policies` with `provider.use` (`experimental.policies` is the pre-2.0.29 location and still works) |
| Provider `options.setCacheKey` | Provider `compatibility.supportsPromptCacheKey` |
| `subagent_depth` | `experimental.subagent_depth` |
| `logLevel` | `OPENCODE_LOG_LEVEL` env var |
| `server` | `opencode service set ...` / `serve` flags |

Unchanged: `shell`, `model`, `default_agent`, `watcher`, `formatter`, `instructions`, `enterprise`, `tool_output`.
(`instructions` loads files, globs, and HTTP(S) URLs in V2 since 2.0.30; configured entries come after `AGENTS.md`.
Earlier V2 releases accepted it without loading it. See [config-schema.md](config-schema.md#instructions).) `lsp` is
preserved but inert.

Todos are off by default in V2; `experimental.todo: true` turns the `todowrite` tool back on (may change or be
removed in any release).

> [!NOTE]
> The migration guide maps `autoupdate: true` to `update: "auto"`, which installs updates automatically in V2. V1
> 1.19.0 no longer installs updates automatically for `true` (it only notifies; install with `/update`), so the
> mapped value is more aggressive than the V1 behavior it replaces. Use `"notify"` to keep the 1.19.0 behavior.

## Permissions

```jsonc
// V1
{ "permission": { "bash": { "git push *": "ask" }, "edit": "allow" }, "tools": { "websearch": false } }

// V2
{
  "permissions": [
    { "action": "shell", "resource": "git push *", "effect": "ask" },
    { "action": "edit", "resource": "*", "effect": "allow" },
    { "action": "websearch", "resource": "*", "effect": "deny" }
  ]
}
```

Action renames: `bash` → `shell`, `task` → `subagent`, `write`/`patch` → `edit`. A V1 string value such as
`"edit": "allow"` becomes one rule with `resource: "*"`. A V1 pattern object becomes one rule per key, kept in the same
order (inferred from the docs' example; both formats are last-match-wins). A V1 `tools: { "x": false }` becomes `{ action: "x", resource: "*",
effect: "deny" }`.

## Agents

| V1 agent field | V2 |
|----------------|----|
| `prompt` | `system` (Markdown files keep the body) |
| `disable` | `disabled` |
| `permission` | `permissions` |
| `model` + `variant` | `model: "provider/model#variant"` |
| `temperature`, `top_p`, `options` | **No agent-level equivalent that takes effect.** `request.body` is kept but not sent to the model; set them on a model variant (`providers.<id>.models.<model>.variants[]` with `body` / `settings`) and select it with `#variant` |
| `maxSteps` | `steps` |
| `tools` | `permissions` rules |
| `name` (JSON) | ignored — use the map key |

> [!IMPORTANT]
> A new custom agent without `mode` defaults to `primary` in V2 (V1 defaulted to `all`). Set `mode` explicitly when
> converting. Files moved from `mode/` or `modes/` into `agents/` need `mode: primary`.

Permission defaults also differ:

> [!WARNING]
> V1 asks before accessing paths outside the project; V2 does not (`external_directory` is allowed by default).
> To keep the V1 behavior add `{ "action": "external_directory", "resource": "*", "effect": "ask" }` to
> `permissions` (2.1.4 migration guide).

V1 agent **files**: V1 frontmatter is deprecated but translated. A file using any of `permissions`, `request`,
`system`, or `disabled` is read as V2 and its V1 fields (`name`, `tools`, `permission`, `temperature`) are ignored with
a log warning; other files with V1 fields are read as V1. Convert a file's frontmatter all at once.

## Commands

`command` → `commands`, `subtask` → `subagent` (legacy still accepted), `model` + `variant` →
`model: "provider/model#variant"`. `template`, `description`, `agent` unchanged. Markdown commands move from
`command/` to `commands/` at the same relative path.

## MCP

| V1 | V2 |
|----|----|
| `mcp.<name>` | `mcp.servers.<name>` |
| `enabled: true/false` | `disabled: false/true` |
| `timeout: 30000` | `timeout: { "catalog": 30000, "execution": 30000 }` |
| `experimental.mcp_timeout` | `mcp.timeout.catalog` / `mcp.timeout.execution` |
| `oauth.clientId` / `clientSecret` / `callbackPort` / `redirectUri` | `client_id` / `client_secret` / `callback_port` / `redirect_uri` |
| `tools: { "srv*": false }` | `permissions: [{ action: "srv_*", resource: "*", effect: "deny" }]` |

## Compaction

`preserve_recent_tokens` → `keep.tokens`; `reserved` → `buffer`; `auto` unchanged; `tail_turns` and `prune` are
ignored with a warning.

V2 `buffer` defaults to 15% of the model's limit, at least 16k, in the 2.1.4 docs (10% in 2.0.29; see
[config-schema.md](config-schema.md#compaction)), so a V1 `reserved` value is only carried over when it was set
explicitly.

## Providers and models

| V1 | V2 |
|----|----|
| `provider` | `providers` |
| `npm: "@ai-sdk/openai-compatible"` | `package: "aisdk:@ai-sdk/openai-compatible"` |
| `api` | `settings.baseURL` |
| `options` | split into `settings`, `headers`, `body` by request role |
| model `id` | `modelID` |
| model `tool_call`, `modalities` | `capabilities.tools`, `capabilities.input`, `capabilities.output` |
| model `status: "deprecated"` | `disabled: true` |
| model `cost.cache_read` / `cache_write` | `cost.cache.read` / `cost.cache.write` |
| model `options` | `settings` |
| model `variants: { "high": {...} }` | `variants: [{ "id": "high", "settings": {...} }]` |
| `whitelist`, `blacklist`, provider `id` | ignored |

Provider ID consolidation: `azure-cognitive-services` → `azure`; `google-vertex-anthropic` → `google-vertex`.
Migration rewrites these IDs in provider/agent/command/filter fields, but **not** in top-level `model` — update it by
hand.

## Files under `.opencode/`

| Kind | V1 dirs still discovered | Preferred V2 dir |
|------|--------------------------|------------------|
| Agents | `agent/`, `agents/`, `mode/`, `modes/` | `agents/<name>.md` |
| Commands | `command/`, `commands/` | `commands/<name>.md` |
| Skills | `skill/`, `skills/` | `skills/<id>/SKILL.md` (move the whole directory) |
| Plugins | `plugin/`, `plugins/` | `plugins/` |

`CLAUDE.md` is not discovered in V2 — move that guidance into `AGENTS.md`.

## Credentials

V2 imports supported credentials from the legacy `auth.json` into its SQLite database during migration; new
credentials are not written back to `auth.json`.

## Suggested procedure

1. Keep existing config; start V2; verify models, credentials, agents, permissions, MCP servers.
2. Port plugins (mandatory) and server-API integrations.
3. Optionally convert to native V2, one top-level area at a time, keeping each nested entry single-format.
4. Verify with `opencode debug config` and `opencode debug agents`.

The docs' recommended prompt for letting OpenCode convert its own config:

```text
Migrate my OpenCode configuration, including file-based definitions, from the V1 format to the native V2 format.
Preserve its behavior and all unrelated settings.
```

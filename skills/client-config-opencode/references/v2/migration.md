# V1 → V2 Migration Reference

Source: <https://opencode.ai/v2/docs/migrate-v1/>.

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
| `autoshare: true` | `share: "auto"` |
| `permission` (object) + `tools` (booleans) | `permissions` (ordered array) |
| `agent`, `mode` | `agents` (entries from `mode` become primary agents) |
| `snapshot` | `snapshots` |
| `attachment` | `media` |
| `command` | `commands` |
| `reference` | `references` |
| `provider` | `providers` |
| `plugin` | `plugins` |
| `skills: { paths, urls }` | `skills: [ ...paths, ...urls ]` |
| `autoupdate: false` / `"notify"` / `true` | `update: "disable"` / `"notify"` / `"auto"` |
| `small_model` | `agents.title.model` |
| `enabled_providers` / `disabled_providers` | `experimental.policies` with `provider.use` |
| `subagent_depth` | `experimental.subagent_depth` |
| `logLevel` | `OPENCODE_LOG_LEVEL` env var |
| `server` | `opencode service set ...` / `serve` flags |

Unchanged: `shell`, `model`, `default_agent`, `watcher`, `formatter`, `instructions`, `enterprise`, `tool_output`.
(`instructions` is accepted but not loaded in V2 — move content into `AGENTS.md`.) `lsp` is preserved but inert.

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
| `temperature`, `top_p`, `options` | `request.body` |
| `maxSteps` | `steps` |
| `tools` | `permissions` rules |
| `name` (JSON) | ignored — use the map key |

> [!IMPORTANT]
> A new custom agent without `mode` defaults to `primary` in V2 (V1 defaulted to `all`). Set `mode` explicitly when
> converting. Files moved from `mode/` or `modes/` into `agents/` need `mode: primary`.

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

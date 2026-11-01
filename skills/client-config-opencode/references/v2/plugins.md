# V2 Plugins Reference

Sources: <https://opencode.ai/v2/docs/plugins/>, <https://opencode.ai/v2/docs/build/plugins/>,
<https://opencode.ai/v2/docs/build/plugins/server/>, <https://opencode.ai/v2/docs/build/plugins/gui/>,
<https://opencode.ai/v2/docs/build/plugins/migrate-v1/>, <https://opencode.ai/v2/docs/cli/plugins/>. Verified against 2.2.5;
the build-docs index was split into `server` and `gui` pages in 2.2.x.

> [!WARNING]
> V1 plugin **implementations do not run in V2**. Configuration is normalized automatically, but plugin code must
> be ported to the new API (`@opencode/plugin`, `Plugin.define`). This is one of V2's three intentional breaking
> changes.

## Configure

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": [
    "opencode-acme-plugin",
    "opencode-acme-plugin@1.2.0",
    "@acme/opencode-plugin",
    "./plugins/local",
    "/absolute/path/plugin",
    "file:///home/me/plugins/local",
    { "package": "@acme/opencode-plugin", "options": { "agent": "reviewer", "strict": true } },
  ],
}
```

- Key is `plugins` (plural). V1 `["pkg", {opts}]` tuples become `{ "package", "options" }` objects.
- Relative paths resolve from the **config file** that contains the entry. A configured local path must be a
  **directory** (2.2.x docs); a path to a single file is skipped, so a ported local plugin lives at
  `./plugins/local/index.ts` and is configured as `./plugins/local`.
- Arrays from all applicable configs apply from lowest to highest precedence (they do not replace each other).

## Discovery

Direct `.ts`/`.js` files and immediate plugin package directories load automatically from every discovered
`.opencode/plugins/` and from `~/.config/opencode/plugins/`. V2 also reads the V1 `.opencode/plugin/` directory;
use `plugins/` for new files. A `plugins/` directory beside a project-root `opencode.json` is **not** discovered —
list it explicitly or move it under `.opencode/`.

## Enable / disable

Entries apply in order. `-id` disables, `*` matches every plugin, `prefix.*` matches an ID prefix, and a later ID
re-enables:

```jsonc
{ "plugins": ["*", "-opencode.provider.*", "opencode.provider.openai", "-acme.reviewer"] }
```

Built-ins `opencode.config.policy` and `opencode.provider.opencode` ignore removals. Local-model discovery can be
turned off with `-opencode.provider.ollama`, `-opencode.provider.lmstudio`, `-opencode.provider.vllm`.

## Manage

```bash
opencode plugin add opencode-acme-plugin@1.2.0     # installs and adds to global config
opencode plugin add github:acme/opencode-plugin
opencode plugin list [--builtin]
opencode plugin check                              # check package plugins for updates
opencode plugin update [name]
opencode plugin remove opencode-acme-plugin@1.2.0
```

Exact npm versions and full Git commit hashes stay pinned. Config-directory changes reload automatically; unwatched
local dependencies may need `opencode service restart`.

CLI-only plugins go in `cli.json` — see [cli.md](cli.md#cli-only-plugins). Since 2.2.3 TUI plugins need
`@opentui/core` and `@opentui/solid` 0.8.0 or later (2.2.0 required 0.7.0). `plugin check` and `plugin update` also
cover GUI-only plugins.

## Desktop (GUI) plugins

Experimental, since 2.2.0. A package that exports `./gui-experimental` adds panels, commands, or settings to OpenCode
Desktop. The app loads plugins from the server it runs, so configure the plugin in the global `opencode.json(c)` to
use it in every window. **Settings > Extensions > Plugins** lists them when the app's own server is selected; a
plugin's switch turns off only its desktop UI, and **Reload** loads it again after a failure. To turn off the whole
plugin, add `-<id>` to `plugins`. Build details are on the `build/plugins/gui` page, which this skill does not
reproduce.

## Minimal V2 plugin

```ts
import { Plugin } from "@opencode/plugin"

export default Plugin.define({
  id: "company.guard",
  async setup(ctx) {
    const strict = ctx.options.strict === true

    await ctx.tool.hook("execute.before", (event) => {
      const input = event.input as { filePath?: string }
      if (strict && event.tool === "read" && input.filePath?.includes(".env")) {
        throw new Error("Do not read .env files")
      }
    })

    await ctx.shell.hook("create.before", (event) => {
      event.env.COMPANY_ENV = "development"
    })

    return () => console.log("unloaded")
  },
})
```

- Every plugin needs a stable `id` (storage is scoped by it).
- `setup(ctx)` may return a cleanup function.
- `ctx.options` holds config options; `ctx.location` gives `directory`, optional `workspaceID`, and `project`.
- The API reference documents context domains for agents, providers, models, commands, integrations, MCP,
  plugins, references, generate, permissions, sessions, skills, storage, tools, VCS, worktrees, web search, and
  events, plus hooks on sessions, permissions, shell, and tools. See the build docs for exact method names.
- Added after 2.0.29 (release notes): `ctx.session.list(...)` (paginated, Effect and Promise APIs; 2.1.0),
  `ctx.session.instructions.entry.put/list/remove` for keyed session instructions that add small updates instead of
  editing the system prompt and survive compaction and reverts (2.2.0), an `experimental.idle` session hook that lets a
  plugin continue work before a session goes idle (2.2.1), and `ctx.experimental.artifact.transform(...)` for artifact
  providers (2.2.4). 2.1.0 renamed provider replay data to `native` on the public SDK, event, and plugin surfaces
  (for example `SessionCompactionResult.providerState` is now `.native`); check any plugin that read the old names.
- `ctx.credential.activate({ credentialID })` makes a saved credential the active one for its integration (in the
  2.0.29 build docs; `credential.activate` reached Effect and Promise server plugins in 2.0.28).
- `ctx.permission.assert` (2.0.29 release notes; not in the build docs) lets an Effect or Promise plugin check the
  configured permission rules and use the native approval prompt. A block or a correction fails the tool call with an
  error carrying the rule's message or the user's feedback.

## V1 hook → V2 API

| V1 | V2 |
|----|----|
| `event` | `ctx.event.subscribe()` |
| `dispose` | Cleanup function returned by `setup` |
| `config` | `transform(...)` on the affected domain |
| `tool` map | `ctx.tool.transform(...)` |
| `auth` | `ctx.integration.transform(...)` |
| `provider` | `ctx.provider.transform(...)` / `ctx.model.transform(...)` |
| `chat.message` | `ctx.session.hook("prompt", ...)` |
| `chat.params` | `ctx.session.hook("context", ...)` (edit `event.options`) |
| `chat.headers` | `ctx.session.hook("model.request", ...)` or `"http.request"` |
| `permission.ask` | `ctx.permission.hook("evaluate", ...)` |
| `tool.execute.before` / `.after` | `ctx.tool.hook("execute.before" \| "execute.after", ...)` |
| `shell.env` | `ctx.shell.hook("create.before", ...)` |
| `tool.definition` | `ctx.tool.transform(...)` |
| `experimental.chat.system.transform` | `ctx.session.hook("context", ...)`, edit `event.system` |
| `experimental.chat.messages.transform` | `ctx.session.hook("context", ...)`, edit `event.messages` |
| `experimental.session.compacting` | `ctx.session.hook("compaction", ...)` |
| `command.execute.before` | Command transform or the prompt hook (no 1:1 global hook) |

These are migration destinations, not exact renames. The V1 context maps as: `directory` → `ctx.location.directory`,
`project` → `ctx.location.project`, `client` → domain methods on `ctx`, the `$` Bun shell → your own process API.

## Supporting V1 and V2 from one package

Default-export an object that spreads `Plugin.define({...})` (V2 reads `id` + `setup`) and adds a V1 `server()`
function (V1 calls it and uses the returned hooks). The migration guide says V1 object entrypoints are supported in
OpenCode `1.18.29` and newer; for older V1 releases use separate function exports.

## Publishing

`package.json` with `"type": "module"`, an `exports["."]` entrypoint, and a dependency on a compatible
`@opencode/plugin` version. An optional `./rpc` export publishes a shared RPC contract.

An Effect plugin declares `effect` as a `peerDependency`: the 2.0.29 docs use `"effect": "^4.0.0"` (the 2.0.26 docs
had `">=4.0.0-rc.112"`), and OpenCode redirects `effect` imports to the host's copy. Effect 4 import paths moved from
`effect/unstable/http` to `effect/http` in the 2.0.29 docs examples.

# V2 Plugins Reference

Sources: <https://opencode.ai/v2/docs/plugins/>, <https://opencode.ai/v2/docs/build/plugins/>,
<https://opencode.ai/v2/docs/build/plugins/migrate-v1/>, <https://opencode.ai/v2/docs/cli/plugins/>.

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
- Relative paths resolve from the **config file** that contains the entry.
- A configured local path must be a **directory**. OpenCode loads its `server` or `index` module (for example
  `index.ts`); a path to a single file is skipped, with a warning in the log (2.1.4 docs; the 2.0.29 docs showed
  `.ts` file paths).
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

CLI-only plugins go in `cli.json` — see [cli.md](cli.md#cli-only-plugins).

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
- `ctx.credential.activate({ credentialID })` makes a saved credential the active one for its integration (in the
  2.0.29 build docs; `credential.activate` reached Effect and Promise server plugins in 2.0.28).
- `ctx.permission.assert({ sessionID, agent, source, action, resources, save })` (2.0.29 release notes; in the build
  docs from 2.1.x) lets an Effect or Promise plugin check the configured permission rules, including saved approvals,
  and use the native approval prompt. Any `deny` blocks; otherwise any `ask` prompts; `save` lists the patterns stored
  on "always allow". A deny or a rejection with feedback rejects with a `Tool.Error` carrying the reason, which the
  model sees; a plain rejection ends the step. Let those errors propagate instead of returning them as tool output.

### Build-API changes between 2.0.29 and 2.1.4

From the build docs diff and the 2.1.0 / 2.1.3 / 2.1.4 release notes; check the build docs for exact signatures
before porting code.

- Provider replay data is `native` everywhere (was `state` / `providerState` / `resultState`);
  `SessionCompactionResult.providerState` is now `native`; tool parts share one `native`; summary compactions
  reference kept messages through `metadata.keepID` instead of `recent`; `providerContext` became `native.messages`;
  the `session.compacted` event was removed (use `session.compaction.started` / `.ended`). The 2.1.0 notes call
  these intentional breaking changes to the SDK, HTTP message/event, and plugin contracts.
- `Credential.Key.configuration` was removed; put setup-form answers in `metadata`.
- `ctx.permission.reply` takes `decision` (was `reply`); session-scoped rules are set with
  `ctx.session.update({ sessionID, permissions })`; `ctx.session.command` takes `{ name, text }` and returns nothing;
  `ctx.session.interrupt` takes `resume` (was `continue`); `ctx.session.list` is paginated (`cursor.next`);
  `ctx.vcs.branches` became `ctx.vcs.branch.list`; plugin list items expose `item.state.status`.
- `ctx.skill.transform` takes branded values (`Skill.ID.make`, `Skill.Name.make`).

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

An Effect plugin declares `effect` as a `peerDependency`: the 2.1.4 docs use `"effect": "^4.0.1"` plus a
`devDependencies` pin `"effect": "4.0.1"` so development installs one copy (2.0.29: `^4.0.0`; 2.0.26:
`">=4.0.0-rc.112"`), and OpenCode redirects `effect` imports to the host's copy. Install it with
`bun add --peer @opencode/plugin effect@4.0.1`. Effect 4 import paths moved from `effect/unstable/http` to
`effect/http` in the 2.0.29 docs examples.

CLI (TUI) plugins that render with OpenTUI: the 2.1.4 docs list `@opentui/core` and `@opentui/solid` peers at
`>=0.6.6` (2.0.29: `>=0.5.8`). Since OpenTUI 0.6, `SyntaxStyle`, `TextBuffer`, and `EditBuffer` constructors take an
owner (`context.renderer.nativeScene`), and `getLayoutNode()` is removed; see the build docs section "Plugins built
for OpenTUI 0.5".

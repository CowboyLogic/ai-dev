# OpenCode — Plugins

> Source: <https://opencode.ai/docs/plugins/>  
> Last updated: April 10, 2026

Plugins extend OpenCode by hooking into events and customizing behavior. Create plugins to add features, integrate with external services, or modify default behavior.

Browse community plugins in the [ecosystem](../ecosystem.md).

---

## Using Plugins

### From Local Files

Place JS/TS files in:

| Scope | Path |
|-------|------|
| Project | `.opencode/plugins/` |
| Global | `~/.config/opencode/plugins/` |

Files in these directories are automatically loaded at startup.

### From npm

Specify packages in `opencode.json`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-helicone-session", "opencode-wakatime", "@my-org/custom-plugin"]
}
```

Packages are installed automatically via Bun at startup and cached in `~/.cache/opencode/node_modules/`.

### Load Order

1. Global config (`~/.config/opencode/opencode.json`)
2. Project config (`opencode.json`)
3. Global plugin directory (`~/.config/opencode/plugins/`)
4. Project plugin directory (`.opencode/plugins/`)

---

## Creating a Plugin

A plugin is a JS/TS module that exports one or more plugin functions.

### Basic Structure

```javascript
// .opencode/plugins/example.js
export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  console.log("Plugin initialized!")

  return {
    // Hook implementations
  }
}
```

Context provided:

| Property | Description |
|----------|-------------|
| `project` | Current project information |
| `directory` | Current working directory |
| `worktree` | Git worktree path |
| `client` | OpenCode SDK client |
| `$` | Bun's shell API for executing commands |

### TypeScript Support

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // Type-safe hook implementations
  }
}
```

### Dependencies

Use external npm packages by adding a `package.json` to your config directory:

```json
// .opencode/package.json
{
  "dependencies": {
    "shescape": "^2.1.0"
  }
}
```

OpenCode runs `bun install` at startup. Your plugins can then import them.

---

## Events

Plugins can subscribe to events:

### Tool Events

| Event | When |
|-------|------|
| `tool.execute.before` | Before a tool executes |
| `tool.execute.after` | After a tool executes |

### Session Events

| Event | When |
|-------|------|
| `session.created` | Session created |
| `session.idle` | Session completes a response |
| `session.error` | Session encounters an error |
| `session.deleted` | Session deleted |
| `session.compacted` | Session context compacted |

### Other Events

| Category | Events |
|----------|--------|
| File | `file.edited`, `file.watcher.updated` |
| Message | `message.updated`, `message.removed`, `message.part.updated` |
| LSP | `lsp.client.diagnostics`, `lsp.updated` |
| Permission | `permission.asked`, `permission.replied` |
| Shell | `shell.env` |
| TUI | `tui.prompt.append`, `tui.command.execute`, `tui.toast.show` |
| Server | `server.connected` |
| Command | `command.executed` |
| Todo | `todo.updated` |
| Installation | `installation.updated` |

---

## Examples

### Send Notifications

```javascript
// .opencode/plugins/notification.js
export const NotificationPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        await $`osascript -e 'display notification "Session completed!" with title "opencode"'`
      }
    },
  }
}
```

### .env Protection

```javascript
// .opencode/plugins/env-protection.js
export const EnvProtection = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("Do not read .env files")
      }
    },
  }
}
```

### Inject Environment Variables

```javascript
// .opencode/plugins/inject-env.js
export const InjectEnvPlugin = async () => {
  return {
    "shell.env": async (input, output) => {
      output.env.MY_API_KEY = "secret"
      output.env.PROJECT_ROOT = input.cwd
    },
  }
}
```

### Custom Tools via Plugin

```typescript
// .opencode/plugins/custom-tools.ts
import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "This is a custom tool",
        args: {
          foo: tool.schema.string(),
        },
        async execute(args, context) {
          return `Hello ${args.foo} from ${context.directory}`
        },
      }),
    },
  }
}
```

### Compaction Hooks

Inject context into the compaction prompt:

```typescript
// .opencode/plugins/compaction.ts
import type { Plugin } from "@opencode-ai/plugin"

export const CompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      output.context.push(`
## Custom Context

- Current task status
- Important decisions made
- Files being actively worked on
`)
    },
  }
}
```

Replace the compaction prompt entirely by setting `output.prompt`.

### Structured Logging

```typescript
// .opencode/plugins/my-plugin.ts
export const MyPlugin = async ({ client }) => {
  await client.app.log({
    body: {
      service: "my-plugin",
      level: "info",
      message: "Plugin initialized",
      extra: { foo: "bar" },
    },
  })
}
```

Levels: `debug`, `info`, `warn`, `error`.

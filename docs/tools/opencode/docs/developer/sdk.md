# OpenCode — SDK

> Source: <https://opencode.ai/docs/sdk/>  
> Last updated: April 10, 2026

The OpenCode JS/TS SDK provides a type-safe client for interacting with the OpenCode server programmatically.

---

## Install

```bash
npm install @opencode-ai/sdk
```

---

## Create Client

Start a server and client together:

```typescript
import { createOpencode } from "@opencode-ai/sdk"

const { client } = await createOpencode()
```

### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `hostname` | string | Server hostname | `127.0.0.1` |
| `port` | number | Server port | `4096` |
| `signal` | AbortSignal | Cancellation signal | `undefined` |
| `timeout` | number | Timeout in ms for server start | `5000` |
| `config` | Config | Configuration object | `{}` |

With custom config:

```typescript
const opencode = await createOpencode({
  hostname: "127.0.0.1",
  port: 4096,
  config: {
    model: "anthropic/claude-3-5-sonnet-20241022",
  },
})

console.log(`Server running at ${opencode.server.url}`)
opencode.server.close()
```

---

## Client Only

Connect to an already-running OpenCode instance:

```typescript
import { createOpencodeClient } from "@opencode-ai/sdk"

const client = createOpencodeClient({
  baseUrl: "http://localhost:4096",
})
```

| Option | Type | Default |
|--------|------|---------|
| `baseUrl` | string | `http://localhost:4096` |
| `fetch` | function | `globalThis.fetch` |
| `parseAs` | string | `auto` |
| `responseStyle` | string | `fields` |
| `throwOnError` | boolean | `false` |

---

## Types

```typescript
import type { Session, Message, Part } from "@opencode-ai/sdk"
```

All types are generated from the server's OpenAPI specification.

---

## Errors

```typescript
try {
  await client.session.get({ path: { id: "invalid-id" } })
} catch (error) {
  console.error("Failed:", (error as Error).message)
}
```

---

## Structured Output

Request validated JSON output matching a JSON Schema:

```typescript
const result = await client.session.prompt({
  path: { id: sessionId },
  body: {
    parts: [{ type: "text", text: "Research Anthropic" }],
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          company: { type: "string" },
          founded: { type: "number" },
        },
        required: ["company", "founded"],
      },
    },
  },
})

console.log(result.data.info.structured_output)
// { company: "Anthropic", founded: 2021 }
```

If validation fails after retries, the response includes a `StructuredOutputError`:

```typescript
if (result.data.info.error?.name === "StructuredOutputError") {
  console.error("Failed after retries:", result.data.info.error.retries)
}
```

| Format type | Description |
|-------------|-------------|
| `text` | Default. Standard text response |
| `json_schema` | Returns validated JSON matching the provided schema |

---

## API Reference

### Global

| Method | Description |
|--------|-------------|
| `global.health()` | Check server health and version |

### App

| Method | Description |
|--------|-------------|
| `app.log({ body })` | Write a log entry |
| `app.agents()` | List all available agents |

### Sessions

| Method | Description |
|--------|-------------|
| `session.list()` | List sessions |
| `session.get({ path })` | Get session details |
| `session.create({ body })` | Create a session |
| `session.delete({ path })` | Delete a session |
| `session.update({ path, body })` | Update session properties |
| `session.prompt({ path, body })` | Send a prompt (use `noReply: true` to inject context without triggering AI) |
| `session.command({ path, body })` | Execute a slash command |
| `session.shell({ path, body })` | Run a shell command |
| `session.abort({ path })` | Abort a running session |
| `session.share({ path })` | Share a session |
| `session.unshare({ path })` | Unshare a session |
| `session.messages({ path })` | List messages |
| `session.revert({ path, body })` | Revert a message |
| `session.unrevert({ path })` | Restore reverted messages |

### Files

| Method | Description |
|--------|-------------|
| `find.text({ query })` | Search for text in files |
| `find.files({ query })` | Find files/directories by name |
| `find.symbols({ query })` | Find workspace symbols |
| `file.read({ query })` | Read a file |
| `file.status({ query? })` | Get status for tracked files |

### TUI

| Method | Description |
|--------|-------------|
| `tui.appendPrompt({ body })` | Append text to the prompt |
| `tui.submitPrompt()` | Submit the current prompt |
| `tui.clearPrompt()` | Clear the prompt |
| `tui.executeCommand({ body })` | Execute a command |
| `tui.showToast({ body })` | Show a toast notification |
| `tui.openHelp()` | Open the help dialog |
| `tui.openSessions()` | Open the session selector |
| `tui.openThemes()` | Open the theme selector |
| `tui.openModels()` | Open the model selector |

### Auth

| Method | Description |
|--------|-------------|
| `auth.set({ path, body })` | Set authentication credentials |

### Events

| Method | Description |
|--------|-------------|
| `event.subscribe()` | Server-sent events stream |

```typescript
const events = await client.event.subscribe()
for await (const event of events.stream) {
  console.log("Event:", event.type, event.properties)
}
```

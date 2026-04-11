# OpenCode — Server

> Source: <https://opencode.ai/docs/server/>  
> Last updated: April 10, 2026

The `opencode serve` command runs a headless HTTP server exposing an OpenAPI endpoint for programmatic interaction.

---

## How It Works

When you run `opencode`, it starts both a TUI and a server. The TUI is a client that communicates with the server. The server exposes an OpenAPI 3.1 spec.

This architecture supports multiple clients and programmatic control. Run `opencode serve` to start a standalone server (if opencode TUI is already running, `serve` starts a new separate server).

---

## Usage

```bash
opencode serve [--port <number>] [--hostname <string>] [--cors <origin>]
```

| Flag | Description | Default |
|------|-------------|---------|
| `--port` | Port to listen on | `4096` |
| `--hostname` | Hostname to listen on | `127.0.0.1` |
| `--mdns` | Enable mDNS discovery | `false` |
| `--mdns-domain` | Custom domain for mDNS | `opencode.local` |
| `--cors` | Additional browser origins to allow | `[]` |

Multiple CORS origins:

```bash
opencode serve --cors http://localhost:5173 --cors https://app.example.com
```

---

## Authentication

Set `OPENCODE_SERVER_PASSWORD` for HTTP basic auth:

```bash
OPENCODE_SERVER_PASSWORD=your-password opencode serve
```

Username defaults to `opencode`; override with `OPENCODE_SERVER_USERNAME`.

---

## OpenAPI Spec

View the spec at:

```
http://<hostname>:<port>/doc
```

Example: `http://localhost:4096/doc`

Use the spec to generate clients, inspect types, or browse in a Swagger explorer.

---

## Connecting to an Existing Server

The `/tui` endpoint can drive the TUI through the server (used by IDE plugins to prefill or run prompts). Pass `--hostname` and `--port` flags when starting the TUI to connect to a specific server.

---

## API Reference

### Global

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/global/health` | Server health and version |
| GET | `/global/event` | Global SSE event stream |

### Project & Path

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/project` | List all projects |
| GET | `/project/current` | Current project |
| GET | `/path` | Current path |
| GET | `/vcs` | VCS info for current project |

### Config & Provider

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/config` | Get config |
| PATCH | `/config` | Update config |
| GET | `/config/providers` | List providers and default models |
| GET | `/provider` | List all providers |
| GET | `/provider/auth` | Get provider auth methods |
| POST | `/provider/{id}/oauth/authorize` | Authorize via OAuth |
| POST | `/provider/{id}/oauth/callback` | Handle OAuth callback |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/session` | List all sessions |
| POST | `/session` | Create session |
| GET | `/session/:id` | Get session details |
| DELETE | `/session/:id` | Delete session |
| PATCH | `/session/:id` | Update session |
| GET | `/session/:id/children` | Get child sessions |
| POST | `/session/:id/init` | Create `AGENTS.md` |
| POST | `/session/:id/fork` | Fork session at message |
| POST | `/session/:id/abort` | Abort running session |
| POST | `/session/:id/share` | Share session |
| DELETE | `/session/:id/share` | Unshare session |
| GET | `/session/:id/diff` | Get session diff |
| POST | `/session/:id/summarize` | Summarize session |
| POST | `/session/:id/revert` | Revert a message |
| POST | `/session/:id/unrevert` | Restore reverted messages |
| POST | `/session/:id/permissions/:permissionID` | Respond to permission request |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/session/:id/message` | List messages |
| POST | `/session/:id/message` | Send message and wait for response |
| GET | `/session/:id/message/:messageID` | Get message details |
| POST | `/session/:id/prompt_async` | Send message asynchronously (returns 204) |
| POST | `/session/:id/command` | Execute a slash command |
| POST | `/session/:id/shell` | Run a shell command |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/find?pattern=<pat>` | Search text in files |
| GET | `/find/file?query=<q>` | Find files/directories by name |
| GET | `/find/symbol?query=<q>` | Find workspace symbols |
| GET | `/file?path=<path>` | List files and directories |
| GET | `/file/content?path=<p>` | Read a file |
| GET | `/file/status` | Status for tracked files |

`/find/file` query parameters: `type` (`file`/`directory`), `directory` (override root), `limit` (1-200).

### TUI

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tui/append-prompt` | Append text to prompt |
| POST | `/tui/submit-prompt` | Submit current prompt |
| POST | `/tui/clear-prompt` | Clear prompt |
| POST | `/tui/execute-command` | Execute a command |
| POST | `/tui/show-toast` | Show toast notification |
| POST | `/tui/open-help` | Open help dialog |
| POST | `/tui/open-sessions` | Open session selector |
| POST | `/tui/open-themes` | Open theme selector |
| POST | `/tui/open-models` | Open model selector |
| GET | `/tui/control/next` | Wait for next control request |
| POST | `/tui/control/response` | Respond to control request |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/agent` | List all agents |
| GET | `/command` | List all commands |
| GET | `/lsp` | LSP server status |
| GET | `/formatter` | Formatter status |
| GET | `/mcp` | MCP server status |
| POST | `/mcp` | Add MCP server dynamically |
| PUT | `/auth/:id` | Set authentication credentials |
| GET | `/event` | Server-sent events stream |
| GET | `/doc` | OpenAPI 3.1 specification |
| POST | `/log` | Write log entry |

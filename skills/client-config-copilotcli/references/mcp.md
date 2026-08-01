# MCP Servers Reference

## Config file location

```
~/.copilot/mcp-config.json
```

(Or `$COPILOT_HOME/mcp-config.json`)

**Server names** can include spaces and special characters (supported as of v1.0.35). Enclose in quotes when referencing in CLI commands.

**OAuth**: MCP OAuth authentication is handled through the shared runtime flow. When removing an MCP server, its OAuth state is automatically cleared.

## Structure

```json
{
  "mcpServers": {
    "server-name": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PERSONAL_ACCESS_TOKEN"
      },
      "tools": ["*"]
    }
  }
}
```

**Credential pattern**: Values in `env` that start with `$` are resolved from the user's shell environment at load time. Set credentials in your shell profile (e.g. `~/.bashrc`, `~/.zshrc`, PowerShell `$PROFILE`) — never hardcode secret values in `mcp-config.json`.

---

## Transport types

### `local` (stdio — most common)

Starts a local process, communicates over stdin/stdout.

```json
{
  "type": "local",
  "command": "node",
  "args": ["path/to/server.js"],
  "env": { "API_KEY": "$MY_API_KEY" },
  "tools": ["*"]
}
```

### `http` (Streamable HTTP)

```json
{
  "type": "http",
  "url": "https://mcp.example.com/mcp",
  "headers": { "Authorization": "Bearer YOUR_TOKEN" },
  "tools": ["*"]
}
```

### `sse` (Server-Sent Events — legacy, deprecated but supported)

```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse",
  "headers": { "Authorization": "Bearer YOUR_TOKEN" },
  "tools": ["*"]
}
```

---

## Fields reference

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `local` \| `http` \| `sse` |
| `tools` | Yes | Array of allowed tool names, or `["*"]` for all |
| `command` | local only | Executable to run |
| `args` | local only | Arguments array |
| `env` | local only | Environment variables object |
| `url` | http/sse only | Remote server URL |
| `headers` | http/sse only | HTTP headers (for auth etc.) |

---

## Common MCP servers

### GitHub
```json
"github": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_PERSONAL_ACCESS_TOKEN" },
  "tools": ["*"]
}
```

Set the token in your shell profile: `export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...`

### Filesystem
```json
"filesystem": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"],
  "tools": ["*"]
}
```

### Memory
```json
"memory": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"],
  "tools": ["*"]
}
```

### PostgreSQL
```json
"postgres": {
  "type": "local",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres"],
  "env": { "DATABASE_URL": "$DATABASE_URL" },
  "tools": ["*"]
}
```

Set the connection string in your shell profile: `export DATABASE_URL=postgresql://user:pass@localhost/db`

> If the server package requires the connection string as a positional argument rather than an env var, use `"args": ["-y", "@modelcontextprotocol/server-postgres", "$DATABASE_URL"]` — the `$VAR` reference is expanded from the user environment at load time.

---

## Adding servers

### Via interactive CLI (recommended)
```
/mcp add
```
Launches a guided form — enter server name, type, command/URL, and any env vars.

### Via terminal subcommand (no interactive session needed)
```bash
# Local (stdio) — command follows `--`
copilot mcp add SERVER-NAME -- COMMAND [ARGS...]
copilot mcp add context7 -- npx -y @upstash/context7-mcp

# Remote (http/sse)
copilot mcp add --transport http SERVER-NAME URL
copilot mcp add --transport http notion https://mcp.notion.com/mcp
```

| Flag | Description |
|------|-------------|
| `--env KEY=VALUE` | Set an env var for the server (repeatable) |
| `--header "HEADER: VALUE"` | Set an HTTP header for remote servers (repeatable) |
| `--transport TRANSPORT` | `stdio` (default) \| `http` \| `sse` |
| `--tools TOOLS` | `*` (default, all), comma-separated list, or `""` for none |
| `--timeout MS` | Timeout in milliseconds |

Added servers go to the user config `~/.copilot/mcp-config.json`.

### Via direct editing
Edit `~/.copilot/mcp-config.json` directly. Useful for sharing configs or adding multiple servers at once.

### Via registry search (experimental)
```
/mcp search              # browse top servers by stars
/mcp search QUERY        # search by name/keyword
```
Requires starting Copilot CLI with `--experimental`, or running `/experimental on` in-session. Pre-populates the add form from the registry entry; org-configured registry URLs/allowlists apply if set.

---

## Per-repository (project-level) MCP servers

Configure servers that only load for a specific project by committing a JSON file to the repo.

| Path | Recommended use |
|------|------------------|
| `.mcp.json` (any dir from cwd up to repo root) | Local/per-checkout config, typically at project root |
| `.github/mcp.json` | Shared config committed to the repo |

- On startup inside a git repo, Copilot CLI walks from cwd up to the repo root loading these files.
- If both `.mcp.json` and `.github/mcp.json` exist in the same directory, `.mcp.json` wins.
- On server-name conflicts, files closer to cwd win; project-level definitions always beat `~/.copilot/mcp-config.json`.
- Project files may use the `mcpServers` wrapper (as above) **or** a bare top-level format — each key is directly a server name:
  ```json
  { "playwright": { "type": "local", "command": "npx", "args": ["@playwright/mcp@latest"] } }
  ```
- **Trust gate**: project-level servers load only after you've confirmed folder trust; silently skipped in untrusted dirs. In `copilot -p` (prompt mode) they're skipped by default in untrusted dirs too — set `GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP=true` to load them anyway (prompt mode can't show an interactive trust prompt).
- **Not read**: VS Code's `.vscode/mcp.json` — it uses the unsupported top-level key `servers`, so it must be migrated to `.mcp.json`/`.github/mcp.json` format.

---

## Management commands (inside sessions)

| Command | Purpose |
|---------|---------|
| `/mcp show` | List all configured servers |
| `/mcp show SERVER-NAME` | Show status and tools for one server |
| `/mcp edit SERVER-NAME` | Modify server config |
| `/mcp delete SERVER-NAME` | Remove server |
| `/mcp disable SERVER-NAME` | Disable without removing |
| `/mcp enable SERVER-NAME` | Re-enable disabled server |

## Management commands (terminal, no session needed)

| Command | Purpose |
|---------|---------|
| `copilot mcp list [--json]` | List servers from all sources (user, workspace, plugin) |
| `copilot mcp get SERVER-NAME [--json]` | Show a server's type, status, and tools |
| `copilot mcp remove SERVER-NAME` | Remove from the user config |

---

## Tool permissions for MCP

In CLI flags, reference MCP tools with:

```bash
--allow-tool='SERVER_NAME'              # allow all tools from server
--allow-tool='SERVER_NAME(tool_name)'   # allow specific tool
--deny-tool='SERVER_NAME(tool_name)'    # block specific tool
```

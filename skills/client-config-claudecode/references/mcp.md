# MCP Servers Reference

Upstream: `https://code.claude.com/docs/en/mcp.md` (managed config: `https://code.claude.com/docs/en/managed-mcp.md`).

## File locations (installation scopes)

| Scope | Loads in | Stored in |
|-------|----------|-----------|
| Local (default for `claude mcp add`) | Current project only, private | `~/.claude.json` → `projects["/abs/path"].mcpServers` |
| Project (shared via git) | Current project | `.mcp.json` in project root → `mcpServers` |
| User | All your projects | `~/.claude.json` → top-level `mcpServers` |
| Managed | Everyone | `managed-mcp.json` in the managed system dir, or the `managedMcpServers` managed setting |

> [!NOTE]
> MCP servers are NOT configured in `settings.json` — they live in `~/.claude.json` (local/user scope) or `.mcp.json` (project scope). "Local scope" for MCP is unrelated to `.claude/settings.local.json`.

**Precedence when the same server is defined twice** (whole entry wins, no field merge): local → project → user → plugin-provided → claude.ai connectors. A `managedMcpServers` entry ranks above all of them (v2.1.259+). Scopes match duplicates by name; plugins/connectors match by endpoint.

Prefer the CLI over hand-editing:

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp                # local scope
claude mcp add --transport http shared --scope project https://example.com/mcp  # writes .mcp.json
claude mcp add --transport stdio --env API_KEY=xxx airtable -- npx -y airtable-mcp-server
claude mcp add-json my-server '{"type":"http","url":"https://mcp.example.com/mcp"}' --scope user
claude mcp list
claude mcp get <name>
claude mcp remove <name>
claude mcp reset-project-choices                 # reset .mcp.json approvals
```

`--` separates Claude's options from the stdio server command.

---

## ~/.claude.json mcpServers structure (user scope)

```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@bytebase/dbhub", "--dsn", "${DB_DSN}"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  }
}
```

---

## Transport types

### stdio (local process)

```json
{
  "type": "stdio",
  "command": "node",
  "args": ["path/to/server.js"],
  "env": { "API_KEY": "..." }
}
```

### HTTP (streamable HTTP — recommended for remote)

```json
{
  "type": "http",
  "url": "https://mcp.example.com/mcp",
  "headers": { "Authorization": "Bearer ${MY_TOKEN}" }
}
```

`"streamable-http"` is accepted as an alias for `"http"`.

### SSE (deprecated)

```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse",
  "headers": { "Authorization": "Bearer ${MY_TOKEN}" }
}
```

SSE is deprecated; `claude mcp add --transport http` falls back to SSE automatically when the server doesn't accept HTTP (v2.1.265+).

### WebSocket

```json
{
  "type": "ws",
  "url": "wss://mcp.example.com/socket",
  "headers": { "Authorization": "Bearer ${MY_TOKEN}" }
}
```

Configure only via `.mcp.json` or `claude mcp add-json` (`--transport` doesn't accept `ws`). Header auth only (no OAuth).

A JSON entry with a `url` but no `type` is an error — Claude Code reads it as stdio and skips the server. Server names may contain only letters, numbers, hyphens, and underscores.

**Other per-server fields**:

- `timeout` — per-server tool-call timeout in ms (values < 1000 ignored; overrides `MCP_TOOL_TIMEOUT`). Startup timeout is the `MCP_TIMEOUT` env var.
- `headersHelper` — script that generates auth headers at connect time (project `.mcp.json` helpers run only after workspace trust).
- `alwaysLoad` — `true` skips tool-search deferral (all the server's tools load at session start; valid on every server type, `ws` included); `false` keeps all of the server's tools deferred (v2.1.287+). See [Tool loading, limits, and runtime](#tool-loading-limits-and-runtime).
- `oauth` — `{clientId, callbackPort, authServerMetadataUrl, scopes}`; pass a secret with `claude mcp add-json ... --client-secret`.

`widgets` is a reserved server name in cloud sessions and on self-hosted runners — rename a server of that name (v2.1.285; changelog only).

Stdio servers receive `CLAUDE_PROJECT_DIR` (project root) in their environment. Referencing it in `command`/`args` of `.mcp.json` or `~/.claude.json` entries needs a default: `${CLAUDE_PROJECT_DIR:-.}` (plugin configs substitute it directly).

### Environment variable expansion

`${VAR}` and `${VAR:-default}` expand in `command`, `args`, `env`, `url`, and `headers`. An unset variable with no default is left as literal `${VAR}` with a warning in `claude mcp list`. In a remote server's `url`/`headers`, credential variables such as `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `AWS_BEARER_TOKEN_BEDROCK`, `HTTPS_PROXY`, and `NPM_TOKEN` always read as empty — copy the value into a variable with your own name.

---

## Tool loading, limits, and runtime

Tool search is on by default: a server's tools are deferred and found on demand. With `ENABLE_TOOL_SEARCH` unset, Claude Code falls back to loading every MCP tool upfront when `ANTHROPIC_BASE_URL` is a non-first-party host, on a Microsoft Foundry deployment hosted on Azure, and on Google Cloud Agent Platform models earlier than the Claude 4.5 generation. On a non-first-party host, setting `ENABLE_TOOL_SEARCH` explicitly overrides the fallback; `ENABLE_TOOL_SEARCH=true` does not override the Foundry and earlier-model cases. The `ENABLE_TOOL_SEARCH` values are in the [MCP docs](https://code.claude.com/docs/en/mcp#configure-tool-search).

- **`alwaysLoad: true`** (server entry) loads all of that server's tools upfront. Startup then waits for the server's tools, capped at the 5-second connect timeout, unless a valid `cached` entry supplies them. Other servers connect in the background; `MCP_CONNECTION_NONBLOCKING=0` makes startup wait for them too.
- **`alwaysLoad: false`** (server entry) defers every tool of that server, including tools its author marked to load upfront (v2.1.287+).
- **Per-tool `_meta["anthropic/alwaysLoad"]`** (set by the server author): `true` loads that tool upfront. `false` keeps it deferred when the user's config sets `alwaysLoad: true` for a server passed with `--mcp-config`, supplied by an Agent SDK app, or provided by a plugin (v2.1.285+).
- **Description limits**: each tool description and each server's instructions are truncated at a default character limit; `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` (v2.1.280+) sets it for every server. The MCP docs page states the default as 2,048 characters; the v2.1.296 changelog says the default changed from 2,048 to 4,096, so treat the docs page as lagging. Per the v2.1.295 changelog, tool descriptions loaded through tool search are cut at 16,384 characters.
- **Retry failed servers**: `/mcp reconnect all` retries every server that failed or needs authentication. In the interactive terminal it needs v2.1.284+; earlier versions print `MCP server "all" not found`.
- **Client runtime**: Claude Code picks the v1 or v2 MCP client runtime at startup. `MCP_SDK_GENERATION` (`v1` | `v2`) forces one. `MCP_PROTOCOL_NEGOTIATION` (`auto` | `legacy`) decides whether Claude Code asks servers for protocol revision 2026-07-28; `legacy` keeps every server on the earlier handshake.
- **URL elicitation** (changelog, v2.1.287): servers on the 2025-11-25 protocol can send URL prompts. A server that stops connecting after that update can be given `"bareElicitationCapability": true` in its config entry. This key is not in the MCP docs page.
- **WebSocket limit** (changelog, v2.1.295): a `ws` message over 16 MiB is no longer parsed and closes the connection, the same limit the other transports already have.

---

## Examples from the upstream docs

```bash
# GitHub remote server with a PAT
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer YOUR_GITHUB_PAT"

# PostgreSQL via DBHub (use a read-only DB user)
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
```

---

## MCP settings in settings.json

These control MCP behavior; the servers themselves are in `~/.claude.json` / `.mcp.json`:

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": ["memory", "github"],
  "disabledMcpjsonServers": ["filesystem"],
  "allowedMcpServers": [{ "serverName": "github" }],
  "deniedMcpServers": [{ "serverName": "filesystem" }],
  "allowManagedMcpServersOnly": true,
  "disableClaudeAiConnectors": true,
  "allowAllClaudeAiMcps": true
}
```

| Setting | Effect |
|---------|--------|
| `enableAllProjectMcpServers` | Auto-approve all project `.mcp.json` servers |
| `enabledMcpjsonServers` | Approve specific servers from `.mcp.json` |
| `disabledMcpjsonServers` | Block specific servers from `.mcp.json` |
| `allowedMcpServers` | Allowlist (any file; entries merge unless `allowManagedMcpServersOnly`). Each entry has exactly one of `serverName`, `serverCommand`, `serverUrl`; `[]` blocks every user-added server |
| `deniedMcpServers` | Denylist (any file; always merges). Same entry shape; `serverName` can name a connector such as `"claude.ai Slack"` |
| `allowManagedMcpServersOnly` | (managed) Only managed servers allowed |
| `disableClaudeAiConnectors` | Disable claude.ai connectors entirely. Any-source-true: a `true` in any scope wins over a `false` elsewhere. `--mcp-config` servers unaffected |
| `allowAllClaudeAiMcps` | (managed) Load claude.ai connectors alongside a deployed `managed-mcp.json`, which otherwise suppresses them |
| `allowClaudeInChromeWithManagedMcp` | (managed, on-machine) Let the built-in Claude in Chrome server run alongside a deployed `managed-mcp.json`, which otherwise blocks it in terminal sessions (v2.1.282+) |
| `managedMcpServers` | (managed) Provide remote `http`/`sse` servers (`https://` URL required) to every user; users can't edit/remove them (v2.1.259+) |

`enableAllProjectMcpServers` and `enabledMcpjsonServers` in a repo's `.claude/settings.json` are ignored until you trust the folder. `claude -p`, SDK, and cloud sessions load `.mcp.json` servers without asking — use `disabledMcpjsonServers`, `--setting-sources`, or `--strict-mcp-config` to keep one out.

**Per-project on/off toggles** in `/mcp` are stored in `~/.claude.json` as `disabledMcpServers` (opt-out list) and `enabledMcpServers` (opt-in, for default-off built-ins like `computer-use`) — unrelated to `enabledMcpjsonServers`/`disabledMcpjsonServers`.

---

## MCP permission rules (in settings.json permissions)

```json
{
  "permissions": {
    "allow": ["mcp__github__*"],
    "deny": ["mcp__filesystem__write*"],
    "ask": ["mcp__puppeteer__*"]
  }
}
```

Pattern: `mcp__<server-name>__<tool-name>` (bare `mcp__<server>` also matches all its tools). Plugin-bundled servers use `mcp__plugin_<plugin-name>_<server-name>__<tool>`; claude.ai connectors use `mcp__claude_ai_<server>__<tool>`. Allow-rule globs need a literal `mcp__<server>__` prefix; `mcp__*` works only in deny/ask.

**Tools that force a prompt regardless of allow rules / permission mode:**

- Server marks a tool `_meta["anthropic/requiresUserInteraction"]: true` — always prompts (even `acceptEdits`/`auto`/`bypassPermissions`); denied outright in `dontAsk`.
- Org sets a claude.ai connector tool to `ask` (via admin console) — same forced-prompt behavior. Org can also set a tool to `blocked`, which filters it out before Claude ever sees it.

---

## Add a new MCP server

Prefer `claude mcp add` / `claude mcp add-json --scope user`. To hand-edit at user scope, add the entry to the top-level `mcpServers` object in `~/.claude.json` (not settings.json); local-scope servers live under `projects["<path>"].mcpServers` instead.

```bash
# View current MCP config
python3 -m json.tool ~/.claude.json
```

## Verify MCP servers are loaded

Inside Claude Code, type `/mcp` to see all configured servers and their status, or run `claude mcp list` / `claude mcp get <name>` from a shell.

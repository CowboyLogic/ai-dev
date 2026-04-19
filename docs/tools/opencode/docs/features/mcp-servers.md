# OpenCode — MCP Servers

> Source: <https://opencode.ai/docs/mcp-servers/>  
> Last updated: April 10, 2026

Add external tools to OpenCode using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). OpenCode supports both local and remote MCP servers.

> [!TIP]
> MCP servers add to your context window. Be selective — servers like the GitHub MCP server can easily exceed context limits.

---

## Enable / Disable

Define MCP servers in `opencode.json` under `mcp`. Each server needs a unique name:

```jsonc
{
  "mcp": {
    "name-of-mcp-server": {
      // config...
      "enabled": true
    },
    "name-of-other-mcp-server": {
      // config...
      "enabled": false   // temporarily disable without removing
    }
  }
}
```

---

## Local MCP Servers

```jsonc
{
  "mcp": {
    "my-local-mcp-server": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true,
      "environment": {
        "MY_ENV_VAR": "my_env_var_value"
      }
    }
  }
}
```

**Example — `@modelcontextprotocol/server-everything`:**

```jsonc
{
  "mcp": {
    "mcp_everything": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-everything"]
    }
  }
}
```

**Local server options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `type` | String | Y | Must be `"local"` |
| `command` | Array | Y | Command and arguments |
| `environment` | Object | | Environment variables |
| `enabled` | Boolean | | Enable/disable on startup |
| `timeout` | Number | | Tool fetch timeout in ms (default 5000) |

---

## Remote MCP Servers

```jsonc
{
  "mcp": {
    "my-remote-mcp": {
      "type": "remote",
      "url": "https://my-mcp-server.com",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer MY_API_KEY"
      }
    }
  }
}
```

**Remote server options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `type` | String | Y | Must be `"remote"` |
| `url` | String | Y | URL of the remote MCP server |
| `enabled` | Boolean | | Enable/disable on startup |
| `headers` | Object | | Headers to send with requests |
| `oauth` | Object | | OAuth configuration |
| `timeout` | Number | | Tool fetch timeout in ms (default 5000) |

---

## OAuth Authentication

OpenCode automatically handles OAuth for remote MCP servers.

### Automatic (no config needed)

```jsonc
{
  "mcp": {
    "my-oauth-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp"
    }
  }
}
```

OpenCode detects 401 responses and initiates the OAuth flow automatically.

### Pre-registered client credentials

```jsonc
{
  "mcp": {
    "my-oauth-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "oauth": {
        "clientId": "{env:MY_MCP_CLIENT_ID}",
        "clientSecret": "{env:MY_MCP_CLIENT_SECRET}",
        "scope": "tools:read tools:execute"
      }
    }
  }
}
```

### Disable OAuth (API key servers)

```jsonc
{
  "mcp": {
    "my-api-key-server": {
      "type": "remote",
      "url": "https://mcp.example.com/mcp",
      "oauth": false,
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      }
    }
  }
}
```

### Manage OAuth credentials

```bash
opencode mcp auth my-oauth-server    # authenticate
opencode mcp list                    # list servers and auth status
opencode mcp logout my-oauth-server  # remove credentials
opencode mcp debug my-oauth-server   # debug connection issues
opencode mcp auth list               # list OAuth-capable servers and status
```

Tokens are stored in `~/.local/share/opencode/mcp-auth.json`.

---

## Manage Tools

### Globally disable an MCP server's tools

```jsonc
{
  "mcp": { "my-mcp-foo": { "type": "local", "command": ["bun", "x", "my-mcp"] } },
  "tools": { "my-mcp-foo": false }
}
```

Use glob patterns to disable multiple servers:

```jsonc
{
  "tools": { "my-mcp*": false }
}
```

Pattern syntax: `*` matches zero or more characters; `?` matches exactly one.

MCP tools are prefixed with the server name: `mymcpservername_*` disables all tools for that server.

### Per-agent MCP tools

Disable globally but enable for a specific agent:

```jsonc
{
  "mcp": { "my-mcp": { "type": "local", "command": ["bun", "x", "my-mcp"], "enabled": true } },
  "tools": { "my-mcp*": false },
  "agent": {
    "my-agent": {
      "tools": { "my-mcp*": true }
    }
  }
}
```

---

## Overriding Organizational Defaults

```jsonc
{
  "mcp": {
    "jira": {
      "type": "remote",
      "url": "https://jira.example.com/mcp",
      "enabled": true
    }
  }
}
```

---

## Examples

### Sentry

```jsonc
{
  "mcp": {
    "sentry": {
      "type": "remote",
      "url": "https://mcp.sentry.dev/mcp",
      "oauth": {}
    }
  }
}
```

```bash
opencode mcp auth sentry
```

### Context7 (documentation search)

```jsonc
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "{env:CONTEXT7_API_KEY}"
      }
    }
  }
}
```

Add to `AGENTS.md`:

```markdown
When you need to search docs, use `context7` tools.
```

### Grep by Vercel (GitHub code search)

```jsonc
{
  "mcp": {
    "gh_grep": {
      "type": "remote",
      "url": "https://mcp.grep.app"
    }
  }
}
```

Add to `AGENTS.md`:

```markdown
If you are unsure how to do something, use `gh_grep` to search code examples from GitHub.
```

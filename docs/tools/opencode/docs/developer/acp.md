# OpenCode — ACP Support

> Source: <https://opencode.ai/docs/acp/>  
> Last updated: April 10, 2026

OpenCode supports the [Agent Client Protocol](https://agentclientprotocol.com/) (ACP), allowing use directly in compatible editors and IDEs via JSON-RPC over stdio.

See the [ACP progress report](https://zed.dev/blog/acp-progress-report#available-now) for a list of editors that support ACP.

---

## Configure

Run OpenCode as an ACP subprocess:

```bash
opencode acp
```

### Zed

Add to `~/.config/zed/settings.json`:

```jsonc
{
  "agent_servers": {
    "OpenCode": {
      "command": "opencode",
      "args": ["acp"]
    }
  }
}
```

Open with the `agent: new thread` action in the Command Palette.

Optional keyboard shortcut in `keymap.json`:

```jsonc
[
  {
    "bindings": {
      "cmd-alt-o": [
        "agent::NewExternalAgentThread",
        {
          "agent": {
            "custom": {
              "name": "OpenCode",
              "command": {
                "command": "opencode",
                "args": ["acp"]
              }
            }
          }
        }
      ]
    }
  }
]
```

### JetBrains IDEs

Add to `acp.json`:

```jsonc
{
  "agent_servers": {
    "OpenCode": {
      "command": "/absolute/path/bin/opencode",
      "args": ["acp"]
    }
  }
}
```

The new `OpenCode` agent appears in the AI Chat agent selector.

### Avante.nvim

```lua
{
  acp_providers = {
    ["opencode"] = {
      command = "opencode",
      args = { "acp" },
      -- Optional: pass environment variables
      env = {
        OPENCODE_API_KEY = os.getenv("OPENCODE_API_KEY")
      }
    }
  }
}
```

### CodeCompanion.nvim

```lua
require("codecompanion").setup({
  interactions = {
    chat = {
      adapter = {
        name = "opencode",
        model = "claude-sonnet-4",
      },
    },
  },
})
```

See [CodeCompanion docs](https://codecompanion.olimorris.dev/getting-started#setting-an-api-key) for environment variable configuration.

---

## Supported Features

All OpenCode features work via ACP:

- Built-in tools (file operations, terminal commands, etc.)
- Custom tools and slash commands
- MCP servers from your config
- Project-specific rules from `AGENTS.md`
- Custom formatters and linters
- Agents and permissions system

> Some built-in slash commands like `/undo` and `/redo` are currently unsupported via ACP.

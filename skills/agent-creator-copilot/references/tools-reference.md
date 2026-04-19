# Tools Reference — Custom Agent Profiles

Load this file when configuring the `tools` property in an agent profile.

---

## Tool Configuration Syntax

```yaml
# Allow all tools (default — same as omitting tools entirely):
tools: ["*"]

# Specific tools only:
tools: ["read", "edit", "search"]

# Disable all tools:
tools: []

# All tools from a specific MCP server:
tools: ["my-mcp-server/*"]

# Mix of built-in and MCP tools:
tools: ["read", "edit", "my-mcp-server/some-tool"]
```

---

## Tool Aliases (Cross-Platform)

Use aliases rather than platform-specific tool names to ensure your agent works across VS Code, JetBrains, and GitHub.com.

| Alias | Maps to | Description |
|---|---|---|
| `read` | Read, NotebookRead | Read file contents |
| `edit` | Edit, MultiEdit, Write, NotebookEdit | Edit files |
| `search` | Grep, Glob | Search files and text |
| `execute` | shell, Bash, powershell | Run shell commands |
| `agent` | custom-agent, Task | Invoke another agent as a subagent |
| `web` | WebSearch, WebFetch | Fetch URLs and perform web searches |
| `todo` | TodoWrite | Structured task lists (VS Code only) |

---

## Referencing Tools in the Agent Body

Use `#tool:<tool-name>` syntax in the Markdown body to reference a specific tool explicitly:

```markdown
Use #tool:web/fetch to retrieve the latest API documentation before answering.
```

---

## Least Privilege Guidance

Apply the minimum tool set the agent needs to do its job:

| Agent role | Recommended tools |
|---|---|
| Read-only reviewer / analyst | `["read", "search"]` |
| Documentation writer | `["read", "search", "edit"]` |
| Developer agent | `["read", "search", "edit", "execute"]` |
| Orchestrator / conductor | `["read", "search", "agent"]` |
| Research / web-aware agent | `["read", "search", "web"]` |
| Full-capability agent | `["*"]` or omit `tools` |
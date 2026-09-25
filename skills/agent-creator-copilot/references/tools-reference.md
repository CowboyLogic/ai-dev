# Tools Reference — Custom Agent Profiles

Load this file when configuring the `tools` property in an agent profile.

**Sources (last verified September 2026):**

- GitHub configuration reference, Tools section: <https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools>
- VS Code tools and context reference: <https://code.visualstudio.com/docs/agents/reference/tools-reference>
- Copilot CLI custom agents reference: <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#custom-agents-reference>

---

## Tool Configuration Syntax

```yaml
# All tools (default, same as omitting tools):
tools: ["*"]

# Specific tools only:
tools: ["read", "edit", "search"]

# Comma-separated string form (documented for GitHub.com):
tools: "read, edit, search"

# No tools:
tools: []

# All tools from one MCP server:
tools: ["my-mcp-server/*"]

# Mix of aliases and a specific MCP tool:
tools: ["read", "edit", "my-mcp-server/some-tool"]

# Tool from a VS Code extension (extension name as proxy):
tools: ["azure.some-extension/some-tool"]
```

Rules that apply everywhere:

- Unrecognized tool names are **ignored**, not errors, so one profile can list tools for several surfaces.
- Omitting `tools` enables every available tool, including MCP tools from the profile and repository settings.
- `tools: []` disables all tools.
- In the CLI, `*` anywhere in the list grants every tool (`["view", "*"]` = all tools).

---

## Tool Aliases (Cross-Platform)

Use these aliases for portability. All aliases are case-insensitive.

| Primary alias | Compatible aliases | Cloud agent mapping | Purpose |
|---|---|---|---|
| `execute` | `shell`, `Bash`, `powershell` | `bash` or `powershell` | Run a command in the OS-appropriate shell |
| `read` | `Read`, `NotebookRead` | `view` | Read file contents |
| `edit` | `Edit`, `MultiEdit`, `Write`, `NotebookEdit` | Edit tools, for example `str_replace`, `str_replace_editor` | Edit files |
| `search` | `Grep`, `Glob` | `search` | Search for files or text in files |
| `agent` | `custom-agent`, `Task` | "Custom agent" tools | Invoke another custom agent |
| `web` | `WebSearch`, `WebFetch` | Not applicable on cloud agent | Fetch URLs and search the web |
| `todo` | `TodoWrite` | Not applicable on cloud agent | Structured task lists (supported by VS Code) |

In VS Code, `read`, `search`, `edit`, `execute`, `web`, and `agent` are also names of built-in **tool sets**, so the aliases enable the whole set there.

> [!NOTE]
> VS Code's current tools reference lists the todo tool as `#todos`, while the GitHub alias table uses `todo`. Both documents are current. If `todo` does not enable the todo list in VS Code, add `todos` too, because unknown names are ignored.

---

## VS Code Tool Sets and Tool Names

VS Code accepts tool sets, individual `set/tool` names, MCP tools, and extension tools in `tools`. Names from the current VS Code reference:

| Tool set | Individual tools |
|---|---|
| `read` | `read/readFile`, `read/problems`, `read/terminalLastCommand`, `read/terminalSelection`, `read/getNotebookSummary`, `read/readNotebookCellOutput` |
| `search` | `search/changes`, `search/codebase`, `search/fileSearch`, `search/listDirectory`, `search/textSearch`, `search/usages` |
| `edit` | `edit/createDirectory`, `edit/createFile`, `edit/editFiles`, `edit/editNotebook` |
| `execute` | `execute/createAndRunTask`, `execute/getTerminalOutput`, `execute/runInTerminal`, `execute/testFailure`, `execute/runNotebookCell` |
| `web` | `web/fetch` |
| `agent` | `agent/runSubagent` |
| `browser` | Browser navigation and interaction tools |
| `vscode` | `vscode/askQuestions`, `vscode/extensions`, `vscode/getProjectSetupInfo`, `vscode/installExtension`, `vscode/runCommand`, `vscode/VSCodeAPI` |

Standalone tools: `githubRepo`, `githubTextSearch`, `todos`, `newWorkspace`.

> [!WARNING]
> Many older community agents (including much of awesome-copilot) use legacy flat names such as `codebase`, `fetch`, `editFiles`, `runCommands`, `runTasks`, `terminalLastCommand`, `findTestFiles`, and `openSimpleBrowser`. These are not in VS Code's current tools reference. Prefer the aliases or the `set/tool` names above. The list of available tools depends on the harness, extensions, and MCP servers, so type `#` in the chat input to see what is actually available. Copilot-harness sessions in VS Code don't get every built-in or extension tool.

---

## MCP Tool Namespacing

Reference MCP tools as `<server-name>/<tool-name>`, or `<server-name>/*` for all of a server's tools. The server name is the key under `mcp-servers` (GitHub.com, CLI) or the server name in your MCP configuration (VS Code).

### Out-of-the-box MCP servers (GitHub.com cloud agent)

| Server | Tools |
|---|---|
| `github` | All read-only tools by default. The token is scoped to the source repository. Use `github/*` or `github/<tool name>`. |
| `playwright` | All Playwright tools, with the server restricted to localhost. Use `playwright/*` or `playwright/<tool name>`. |

---

## Referencing Tools in the Agent Body

In VS Code, use `#tool:<tool-name>` in the Markdown body to reference a tool:

```markdown
Use #tool:web/fetch to retrieve the latest API documentation before answering.
```

The body can also reference files with Markdown links or `#file:` (paths resolve relative to the agent file, and `~/` means the home folder).

In the Copilot CLI, agents in a multi-agent session can use `list_agents` and `write_agent` to inspect and message nearby agents.

---

## Least Privilege Guidance

| Agent role | Recommended tools |
|---|---|
| Read-only reviewer / analyst | `["read", "search"]` |
| Documentation writer | `["read", "search", "edit"]` |
| Developer agent | `["read", "search", "edit", "execute"]` |
| Orchestrator / coordinator | `["agent", "read", "search"]` |
| Research / web-aware agent (IDE, CLI) | `["read", "search", "web"]` |
| Full-capability agent | `["*"]` or omit `tools` |

`web` has no effect on the GitHub.com cloud agent, so a cloud research agent needs an MCP server for external data.

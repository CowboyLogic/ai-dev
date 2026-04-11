# OpenCode — Tools

> Source: <https://opencode.ai/docs/tools/>  
> Last updated: April 10, 2026

Tools allow the LLM to perform actions in your codebase. All built-in tools are enabled by default. Control behavior through [permissions](https://opencode.ai/docs/permissions).

---

## Configure Permissions

```jsonc
// opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "edit": "deny",
    "bash": "ask",
    "webfetch": "allow"
  }
}
```

Use wildcards for multiple tools at once:

```jsonc
{
  "permission": {
    "mymcp_*": "ask"
  }
}
```

Values: `"allow"`, `"ask"`, `"deny"`.

---

## Built-in Tools

### `bash`

Execute shell commands.

```jsonc
{ "permission": { "bash": "allow" } }
```

Runs terminal commands like `npm install`, `git status`, etc.

### `edit`

Modify existing files using exact string replacements. Primary way the LLM modifies code.

```jsonc
{ "permission": { "edit": "allow" } }
```

> The `edit` permission also controls `write`, `apply_patch`, and `multiedit`.

### `write`

Create new files or overwrite existing ones.

```jsonc
{ "permission": { "edit": "allow" } }   // same permission as edit
```

### `read`

Read file contents. Supports line ranges for large files.

```jsonc
{ "permission": { "read": "allow" } }
```

### `grep`

Search file contents using regular expressions.

```jsonc
{ "permission": { "grep": "allow" } }
```

### `glob`

Find files by glob pattern (e.g., `**/*.js`). Returns paths sorted by modification time.

```jsonc
{ "permission": { "glob": "allow" } }
```

### `list`

List files and directories. Accepts glob patterns to filter results.

```jsonc
{ "permission": { "list": "allow" } }
```

### `apply_patch`

Apply patch files to your codebase.

```jsonc
{ "permission": { "edit": "allow" } }   // controlled by edit permission
```

Note: use `input.tool === "apply_patch"` (not `"patch"`) in hooks.

### `skill`

Load a `SKILL.md` file and return its content in the conversation.

```jsonc
{ "permission": { "skill": "allow" } }
```

### `todowrite`

Manage todo lists during coding sessions (task tracking). Disabled for subagents by default.

```jsonc
{ "permission": { "todowrite": "allow" } }
```

### `webfetch`

Fetch and read web pages. Useful for looking up documentation.

```jsonc
{ "permission": { "webfetch": "allow" } }
```

### `websearch`

Search the web using Exa AI. Available when using the OpenCode provider or with:

```bash
OPENCODE_ENABLE_EXA=1 opencode
```

```jsonc
{ "permission": { "websearch": "allow" } }
```

> Use `websearch` for discovery, `webfetch` for retrieving content from a known URL.

### `question`

Ask the user questions during task execution. Useful for clarification.

```jsonc
{ "permission": { "question": "allow" } }
```

### `lsp` (experimental)

Interact with configured LSP servers for code intelligence (definitions, references, hover, etc.).

Enable with `OPENCODE_EXPERIMENTAL_LSP_TOOL=true`.

```jsonc
{ "permission": { "lsp": "allow" } }
```

Supported operations: `goToDefinition`, `findReferences`, `hover`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, `prepareCallHierarchy`, `incomingCalls`, `outgoingCalls`.

---

## Custom Tools

Define your own functions that the LLM can call. See [Custom Tools docs](https://opencode.ai/docs/custom-tools).

---

## MCP Servers

Integrate external tools via Model Context Protocol. See [mcp-servers.md](mcp-servers.md).

---

## Internals

Tools like `grep`, `glob`, and `list` use [ripgrep](https://github.com/BurntSushi/ripgrep) under the hood. By default, ripgrep respects `.gitignore` patterns.

### Override ignore patterns

Create a `.ignore` file to explicitly allow certain paths:

```
!node_modules/
!dist/
!build/
```

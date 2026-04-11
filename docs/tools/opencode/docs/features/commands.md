# OpenCode — Custom Commands

> Source: <https://opencode.ai/docs/commands/>  
> Last updated: April 10, 2026

Custom commands let you define reusable prompts that run when invoked with `/` in the TUI.

```
/my-command
```

Custom commands are in addition to built-in commands like `/init`, `/undo`, `/redo`, `/share`. Built-in commands can be overridden by defining a custom command with the same name.

---

## Create via Markdown Files (recommended)

Create files in `.opencode/commands/` (per-project) or `~/.config/opencode/commands/` (global):

```markdown
<!-- .opencode/commands/test.md -->
---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Run the full test suite with coverage report and show any failures.
Focus on the failing tests and suggest fixes.
```

The filename becomes the command name: `test.md` → `/test`.

---

## Create via JSON Config

```jsonc
// opencode.json
{
  "command": {
    "test": {
      "template": "Run the full test suite with coverage report and show any failures.\nFocus on the failing tests and suggest fixes.",
      "description": "Run tests with coverage",
      "agent": "build",
      "model": "anthropic/claude-3-5-sonnet-20241022"
    }
  }
}
```

Run with:

```
/test
```

---

## Prompt Syntax

### Arguments

Use `$ARGUMENTS` as a placeholder for the full argument string:

```markdown
---
description: Create a new component
---

Create a new React component named $ARGUMENTS with TypeScript support.
Include proper typing and basic structure.
```

```
/component Button
```

Access individual positional arguments:

```markdown
---
description: Create a file with content
---

Create a file named $1 in the directory $2 with the following content: $3
```

```
/create-file config.json src "{ \"key\": \"value\" }"
```

### Shell output

Use `` !`command` `` to inject bash command output:

```markdown
---
description: Analyze test coverage
---

Here are the current test results:
!`npm test`

Based on these results, suggest improvements to increase coverage.
```

```markdown
---
description: Review recent changes
---

Recent git commits:
!`git log --oneline -10`

Review these changes and suggest any improvements.
```

### File references

Use `@` followed by a filename to include file content:

```markdown
---
description: Review component
---

Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

---

## Options

| Option | Required | Description |
|--------|----------|-------------|
| `template` | Y | Prompt sent to the LLM |
| `description` | | Description shown in the TUI |
| `agent` | | Agent to execute the command (defaults to current agent) |
| `model` | | Override the model for this command |
| `subtask` | | Force a subagent invocation (`true`/`false`) |

### `agent`

```jsonc
{
  "command": {
    "review": {
      "agent": "plan"
    }
  }
}
```

If the specified agent is a subagent, the command triggers a subagent invocation by default.

### `subtask`

Force the command to run as a subagent even if the agent mode is `primary`:

```jsonc
{
  "command": {
    "analyze": {
      "subtask": true
    }
  }
}
```

---

## Built-in Commands

OpenCode includes: `/init`, `/undo`, `/redo`, `/share`, `/help`, `/connect`, `/compact`, `/details`, `/editor`, `/exit`, `/export`, `/models`, `/new`, `/sessions`, `/themes`, `/thinking`, `/unshare`.

See [tui.md](../interface/tui.md) for the full list.

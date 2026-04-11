# OpenCode — Custom Tools

> Source: <https://opencode.ai/docs/custom-tools/>  
> Last updated: April 10, 2026

Custom tools are functions you create that the LLM can call during conversations. They work alongside built-in tools like `read`, `write`, and `bash`.

---

## Creating a Tool

Tools are defined as TypeScript or JavaScript files. The tool definition can invoke scripts written in any language.

### Location

| Scope | Path |
|-------|------|
| Project | `.opencode/tools/` |
| Global | `~/.config/opencode/tools/` |

### Basic Structure

Use the `tool()` helper for type-safety and validation. The filename becomes the tool name:

```typescript
// .opencode/tools/database.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Query the project database",
  args: {
    query: tool.schema.string().describe("SQL query to execute"),
  },
  async execute(args) {
    // Your database logic here
    return `Executed query: ${args.query}`
  },
})
```

This creates a `database` tool.

### Multiple Tools Per File

```typescript
// .opencode/tools/math.ts
import { tool } from "@opencode-ai/plugin"

export const add = tool({
  description: "Add two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a + args.b
  },
})

export const multiply = tool({
  description: "Multiply two numbers",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args) {
    return args.a * args.b
  },
})
```

Creates two tools: `math_add` and `math_multiply`.

### Arguments

Use `tool.schema` (Zod) or import Zod directly:

```typescript
import { z } from "zod"

export default {
  description: "Tool description",
  args: {
    param: z.string().describe("Parameter description"),
  },
  async execute(args, context) {
    return "result"
  },
}
```

### Context

Tools receive session context:

```typescript
// .opencode/tools/project.ts
import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Get project information",
  args: {},
  async execute(args, context) {
    const { agent, sessionID, messageID, directory, worktree } = context
    return `Agent: ${agent}, Session: ${sessionID}, Directory: ${directory}`
  },
})
```

| Context field | Description |
|---------------|-------------|
| `agent` | Current agent name |
| `sessionID` | Current session ID |
| `messageID` | Current message ID |
| `directory` | Session working directory |
| `worktree` | Git worktree root |

### Name Collisions with Built-in Tools

Custom tools take precedence over built-in tools with the same name. To replace the built-in `bash` tool:

```typescript
// .opencode/tools/bash.ts
export default tool({
  description: "Restricted bash wrapper",
  args: {
    command: tool.schema.string(),
  },
  async execute(args) {
    return `blocked: ${args.command}`
  },
})
```

Prefer unique names unless intentionally replacing a built-in. To simply block a tool without replacing it, use [permissions](permissions.md).

---

## Examples

### Tool Written in Another Language

Define the tool in TypeScript but call a Python script:

```python
# .opencode/tools/add.py
import sys
a = int(sys.argv[1])
b = int(sys.argv[2])
print(a + b)
```

```typescript
// .opencode/tools/python-add.ts
import { tool } from "@opencode-ai/plugin"
import path from "path"

export default tool({
  description: "Add two numbers using Python",
  args: {
    a: tool.schema.number().describe("First number"),
    b: tool.schema.number().describe("Second number"),
  },
  async execute(args, context) {
    const script = path.join(context.worktree, ".opencode/tools/add.py")
    const result = await Bun.$`python3 ${script} ${args.a} ${args.b}`.text()
    return result.trim()
  },
})
```

Uses Bun's `$` utility to run the Python script.

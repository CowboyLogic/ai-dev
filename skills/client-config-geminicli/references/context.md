# Context & Memory Reference

## GEMINI.md

The primary way to inject persistent context into every session.

### Discovery order
1. `~/.gemini/GEMINI.md` — global, always loaded
2. `GEMINI.md` files walking up from cwd to workspace root
3. Just-in-time (JIT) context from files accessed during the session

All found files are concatenated and injected into the system prompt.

### File naming
Configure alternative names in `settings.json`:
```json
{
  "context": {
    "fileName": ["GEMINI.md", "AGENTS.md", "CONTEXT.md"]
  }
}
```

### Import directives
Modularize with `@` imports:
```markdown
# My Project

@./docs/coding-standards.md
@./docs/api-conventions.md
@../shared/company-style.md
```

Supports relative and absolute paths.

### Discovery boundary
Upward traversal from cwd stops at the first directory containing any name in `context.memoryBoundaryMarkers` (array, default `[".git"]`). An empty array disables parent traversal entirely.

### Example GEMINI.md
```markdown
# Project Context

This is a TypeScript monorepo using pnpm workspaces.

## Conventions
- Use named exports, not default exports
- All async functions must handle errors explicitly
- Tests use Vitest, not Jest

## Directory structure
- `packages/api` — Express REST API
- `packages/web` — React frontend
- `packages/shared` — Shared utilities
```

---

## Memory commands

| Command | Description |
|---------|-------------|
| `/memory show` | Display all loaded context concatenated |
| `/memory reload` | Force re-scan and reload all context files |
| `/memory add <text>` | Append text to `~/.gemini/GEMINI.md` |
| `/memory inbox` | Review skills auto-extracted from past sessions (requires `experimental.autoMemory: true`) |

---

## .geminiignore

Exclude files from context loading and file tools. Lives at project root alongside `.gitignore`.

```
# .geminiignore
node_modules/
dist/
*.log
.env*
secrets/
coverage/
```

Control in `settings.json` (note the casing — `respectGeminiIgnore`, not `respectGeminiignore`):
```json
{
  "context": {
    "fileFiltering": {
      "respectGeminiIgnore": true,
      "respectGitIgnore": true
    }
  }
}
```

---

## Memory model

There is no `experimental.memoryV2` toggle in current docs — prompt-driven memory editing is the default and only documented path: tell the agent to remember something ("Remember that I prefer `const` over `let`") and it edits the appropriate Markdown memory file directly. No explicit `/memory add` invocation is required, though it's still available.

## Auto-memory (experimental)

When `experimental.autoMemory: true`, the CLI automatically extracts memory patches and reusable skills from past sessions in the background. Every change is written as a unified diff `.patch` file under `<projectMemoryDir>/.inbox/<kind>/` and held for review — nothing is applied until approved via `/memory inbox`.

---

## Context settings reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `context.fileName` | string \| array | `["GEMINI.md"]` | File name(s) to scan for |
| `context.importFormat` | string | — | Format used when importing memory |
| `context.includeDirectoryTree` | boolean | `true` | Include the cwd directory tree in the initial model request |
| `context.discoveryMaxDirs` | number | `200` | Max directories to search for memory |
| `context.memoryBoundaryMarkers` | array | `[".git"]` | Names marking the GEMINI.md upward-discovery boundary |
| `context.includeDirectories` | array | `[]` | Additional directories included in workspace context |
| `context.loadMemoryFromIncludeDirectories` | boolean | `false` | Scan include dirs on `/memory reload` |
| `context.fileFiltering.respectGitIgnore` | boolean | `true` | Skip gitignored files |
| `context.fileFiltering.respectGeminiIgnore` | boolean | `true` | Skip .geminiignore files |
| `context.fileFiltering.enableFileWatcher` | boolean | `false` | File-watcher updates for `@` suggestions (experimental) |
| `context.fileFiltering.enableRecursiveFileSearch` | boolean | `true` | Enable recursive search for `@` completions |
| `context.fileFiltering.enableFuzzySearch` | boolean | `true` | Enable fuzzy file matching |
| `context.fileFiltering.customIgnoreFilePaths` | array | `[]` | Additional ignore files (highest precedence) |

---

## Session & history

- Shell history: `~/.gemini/tmp/<project_hash>/shell_history`
- Session files stored under `~/.gemini/tmp/`
- Cleanup controlled by `general.sessionRetention.*` in settings (`enabled`, `maxAge`, `maxCount`, `minRetention`)

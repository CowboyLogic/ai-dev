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

Control in `settings.json`:
```json
{
  "context": {
    "respectGeminiignore": true,
    "respectGitignore": true
  }
}
```

---

## Auto-memory

When enabled, the CLI automatically saves important information between sessions:

- Configured via `settings.json` (experimental section)
- Stored in `~/.gemini/GEMINI.md`
- Use `/memory show` to inspect what's been saved

---

## Context settings reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `context.fileName` | array | `["GEMINI.md"]` | File names to scan for |
| `context.discoveryMaxDirs` | number | `200` | Max directories to search for memory |
| `context.loadMemoryFromIncludeDirectories` | boolean | `false` | Scan include dirs on `/memory reload` |
| `context.fileFiltering.respectGitIgnore` | boolean | `true` | Skip gitignored files |
| `context.fileFiltering.respectGeminiIgnore` | boolean | `true` | Skip .geminiignore files |
| `context.fileFiltering.enableRecursiveFileSearch` | boolean | `true` | Enable recursive search for `@` completions |
| `context.fileFiltering.enableFuzzySearch` | boolean | `true` | Enable fuzzy file matching |
| `context.fileFiltering.customIgnoreFilePaths` | array | `[]` | Additional ignore files (highest precedence) |

---

## Session & history

- Shell history: `~/.gemini/tmp/<project_hash>/shell_history`
- Session files stored under `~/.gemini/tmp/`
- Cleanup controlled by `general.sessionCleanup` in settings

# Custom Instructions Reference

Custom instructions give Copilot persistent context about your project, coding standards, and preferences. All matching instruction files are **combined** — they don't replace each other.

## Instruction file locations (all combined when applicable)

| File | Scope | Notes |
|------|-------|-------|
| `$HOME/.copilot/copilot-instructions.md` | Global personal | Applies across repositories |
| `$HOME/.copilot/instructions/**/*.instructions.md` | Global personal, path-specific | Modular; matched by `applyTo` |
| `.github/copilot-instructions.md` | Project-wide | Discovered in standard locations (repo root, cwd, intermediate dirs, dirs nested in a file's path) |
| `.github/instructions/*.instructions.md` | Path-specific | Matched by `applyTo` glob |
| `.github/instructions/**/*.instructions.md` | Path-specific | Nested subdirs; standard locations only, not intermediate dirs |
| `AGENTS.md` | Project-wide | Discovered in standard locations |
| `CLAUDE.md` | Project-wide | Discovered in standard locations; Copilot CLI also reads `.claude/CLAUDE.md` |
| `GEMINI.md` | Project-wide | Discovered in standard locations |
| Dirs in `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | Additional | Comma-separated list of extra dirs to scan for `AGENTS.md` and `*.instructions.md` |

Setting `COPILOT_HOME` redirects both global-personal locations (instead of `$HOME/.copilot`).

Use `/instructions` in-session to view which instruction files were discovered and to enable/disable individual ones.

**Priority note (no fixed precedence)**: Copilot CLI **combines** all applicable user-level and repository instruction files rather than picking one. It dedupes identical copies of user-level `copilot-instructions.md`, repo-wide, and agent instruction content, but does **not** define a general precedence order between `copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` — avoid writing conflicting instructions across these files, since resolution isn't deterministic. Path-specific (`*.instructions.md`) files are included only when their `applyTo` matches a file in context; files disabled via `/instructions` are excluded.

### Referencing other files

Inside `.github/copilot-instructions.md`, `AGENTS.md`, or `CLAUDE.md`, use `@relative/path` to inline another file's content (read immediately; references within referenced files are also resolved). Referenced files must stay inside the repo (or inside the custom-instructions directory for personal instructions) — absolute paths and `~/`-prefixed paths are not loaded. `@`-references are **not** expanded in `GEMINI.md` or `*.instructions.md` files.

### Live reload

Edits to instruction files don't apply to an already-running session. Exit and resume (`copilot --continue`) or start fresh (`/new`) to pick up changes.

---

## Format

### Repository-wide (plain markdown, no frontmatter needed)

```markdown
# Project Guidelines

## Coding standards
- Use TypeScript strict mode
- All functions must have JSDoc comments
- Prefer functional patterns over class-based

## Testing
- Jest for unit tests
- Playwright for e2e tests
- 80% minimum coverage required

## Git
- Conventional commits format
- No force-pushes to main
```

### Path-specific instructions (requires YAML frontmatter)

```markdown
---
applyTo: "app/models/**/*.rb"
excludeAgent: "code-review"
---

# Rails Model Guidelines

- Use Active Record scopes for reusable queries
- Validate all user-facing attributes
- Use `belongs_to required: true` by default
```

### Frontmatter fields for path-specific files

| Field | Description |
|-------|-------------|
| `applyTo` | Glob pattern(s), comma-separated for multiple — instructions apply when matched file is in context |
| `excludeAgent` | Optionally exclude from: `"code-review"` or `"cloud-agent"` (default: used by both if omitted) |

Glob quick reference: `*` (files in current dir), `**`/`**/*` (all files, all dirs), `*.py` (current dir only), `**/*.py` (recursive), `src/*.py` (non-recursive in `src/`), `src/**/*.py` (recursive under `src/`), `**/subdir/**/*.py` (matches `subdir` at any depth).

---

## What to put in instructions

### Good candidates
- Project architecture and folder structure
- Coding conventions and style rules
- Preferred libraries and frameworks
- Test frameworks and coverage requirements
- Git workflow and commit message format
- Security requirements ("never log tokens")
- Domain-specific terminology

### Avoid
- Duplicate content across files (can cause conflicting advice)
- Instructions that contradict each other
- Anything better suited as a skill (task-specific detailed guidance)

---

## Examples

### Global personal instructions (`~/.copilot/copilot-instructions.md`)
```markdown
# My Personal Preferences

- I prefer concise responses without excessive explanation
- Always use TypeScript over JavaScript when given a choice
- I work primarily on macOS — shell examples should use bash
- When suggesting refactors, explain the trade-offs
```

### Project instructions (`.github/copilot-instructions.md`)
```markdown
# Acme Corp API Project

## Stack
- Node.js 20 + TypeScript 5
- Express 4 for HTTP, Zod for validation
- PostgreSQL 16 via Prisma

## Conventions
- All endpoints return `{ data, error, meta }` envelope
- Use kebab-case for URL paths
- Environment variables documented in `.env.example`

## Testing
- Vitest for unit tests
- Supertest for integration tests
- Run: `npm test`
```

### Path-specific (`.github/instructions/api-routes.instructions.md`)
```markdown
---
applyTo: "src/routes/**/*.ts"
---

# Route Handler Guidelines

- Always validate request body with Zod schema before processing
- Return 422 with field errors for validation failures
- Use `asyncHandler` wrapper for all async route handlers
- Log request/response with correlation ID
```

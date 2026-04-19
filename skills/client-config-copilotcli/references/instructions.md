# Custom Instructions Reference

Custom instructions give Copilot persistent context about your project, coding standards, and preferences. All matching instruction files are **combined** — they don't replace each other.

## Instruction file locations (all combined when applicable)

| File | Scope | Notes |
|------|-------|-------|
| `~/.copilot/copilot-instructions.md` | Global personal | Applies to all sessions |
| `.github/copilot-instructions.md` | Project-wide | All files in the repo |
| `.github/instructions/*.instructions.md` | Path-specific | Matched by `applyTo` glob |
| `.github/instructions/**/*.instructions.md` | Path-specific | Nested subdirectories |
| `AGENTS.md` (repo root) | Project-wide | "Primary" weight; works with other AI agents too |
| `CLAUDE.md` (repo root) | Project-wide | Claude Code compatible |
| `GEMINI.md` (repo root) | Project-wide | Gemini compatible |

**Priority note**: `AGENTS.md` at the root is treated as "primary" and carries more weight. If both `AGENTS.md` and `.github/copilot-instructions.md` exist, both are used. Conflicting instructions are resolved non-deterministically — avoid overlapping directives.

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
| `applyTo` | Glob pattern — instructions apply when matched file is in context |
| `excludeAgent` | Optionally exclude from: `"code-review"` or `"cloud-agent"` |

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

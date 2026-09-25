# Custom Instructions Reference

Custom instructions give Copilot persistent context. All applicable files are **combined**; none
replaces another.

## Locations

"Standard locations" = the repository root, the cwd, intermediate directories between them, and
directories nested in the path of a file being worked on.

| File | Scope | Notes |
|------|-------|-------|
| `$HOME/.copilot/copilot-instructions.md` | Personal, all repos | `$COPILOT_HOME` replaces `$HOME/.copilot` |
| `$HOME/.copilot/instructions/**/*.instructions.md` | Personal, modular | Matched by `applyTo` |
| `.github/copilot-instructions.md` | Repository-wide | Standard locations |
| `.github/instructions/**/*.instructions.md` | Path-specific | Standard locations, **not** intermediate dirs |
| `AGENTS.md` | Repository-wide | Standard locations |
| `CLAUDE.md` | Repository-wide | Standard locations; `.claude/CLAUDE.md` also read |
| `GEMINI.md` | Repository-wide | Standard locations |
| Dirs in `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | Additional | Comma-separated; scanned for `AGENTS.md` and `*.instructions.md` |

- `/instructions` shows discovered files and toggles individual ones; `copilot instruction list
  [--json]` lists them from the terminal.
- `--no-custom-instructions` disables loading `AGENTS.md` and related files.
- `copilot init` or `/init` generates or improves `.github/copilot-instructions.md`
  (`/init suppress` hides the "No copilot instructions found" hint for the repo).

### How files combine

No general precedence between `copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md`.
Identical copies are deduplicated; conflicting instructions resolve non-deterministically — avoid
them. Path-specific files are included only when `applyTo` matches a file in context; files
disabled via `/instructions` are excluded.

### Subagents

Custom agents running as subagents don't receive repository instructions unless their frontmatter
sets `include-custom-instructions: true` (see `agents-plugins.md`). The `general-purpose` subagent
does receive them.

### Referencing other files

In `.github/copilot-instructions.md`, `AGENTS.md`, or `CLAUDE.md`, a line starting with `@` followed
by a relative path inlines that file (recursively, with depth, cycle, and size guards). The how-to
guide says referenced files must stay inside the repo (or the personal instructions directory) and
that absolute and `~/` paths are not loaded. `@` references are **not** expanded in `GEMINI.md` or
`*.instructions.md`.

> [!NOTE]
> The command reference says import paths "can be relative to the instruction file's directory or
> absolute", which contradicts the how-to guide. Prefer relative paths inside the repository.

### Live reload

Edits don't reach a running session. Exit and resume (`copilot --continue`) or start fresh (`/new`).

---

## Format

### Repository-wide (plain Markdown, no frontmatter)

```markdown
# Project Guidelines

- Use TypeScript strict mode
- Jest for unit tests, Playwright for e2e
- Conventional commits
```

### Path-specific (YAML frontmatter required)

```markdown
---
applyTo: "app/models/**/*.rb"
excludeAgent: "code-review"
---

# Rails Model Guidelines

- Use Active Record scopes for reusable queries
```

| Field | Description |
|-------|-------------|
| `applyTo` | Glob(s), comma-separated, e.g. `"**/*.ts,**/*.tsx"` |
| `excludeAgent` | `"code-review"` or `"cloud-agent"` — excludes that GitHub.com agent; omitted = used by both |

Glob quick reference: `*` (files in current dir), `**` or `**/*` (everything), `*.py` (current dir
only), `**/*.py` (recursive), `src/*.py` (non-recursive in `src/`), `src/**/*.py` (recursive under
`src/`), `**/subdir/**/*.py` (`subdir` at any depth).

---

## What to put where

- Instructions: architecture, conventions, preferred libraries, test commands, git workflow,
  security rules — short guidance relevant to nearly every task.
- Skills: detailed task-specific procedures (see `skills.md`).
- Avoid duplicating or contradicting content across instruction files.

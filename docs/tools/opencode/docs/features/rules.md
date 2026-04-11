# OpenCode — Rules (AGENTS.md)

> Source: <https://opencode.ai/docs/rules/>  
> Last updated: April 10, 2026

Provide custom instructions to OpenCode via an `AGENTS.md` file. Similar to Cursor's rules — content is included in the LLM's context to customize behavior for your project.

---

## Initialize

Run `/init` in the TUI to auto-generate `AGENTS.md` from your codebase:

```
/init
```

`/init` scans your repo and creates or updates `AGENTS.md` with:

- Build, lint, and test commands
- Architecture and repo structure notes
- Project-specific conventions and setup quirks
- References to existing instruction sources (Cursor rules, Copilot instructions, etc.)

**Commit `AGENTS.md` to Git** so OpenCode understands the project in all sessions.

---

## Example

```markdown
# SST v3 Monorepo Project

This is an SST v3 monorepo with TypeScript. Uses bun workspaces.

## Project Structure

- `packages/` - Workspace packages (functions, core, web, etc.)
- `infra/` - Infrastructure split by service (storage.ts, api.ts, web.ts)
- `sst.config.ts` - Main SST configuration

## Code Standards

- Use TypeScript with strict mode
- Shared code goes in `packages/core/` with proper exports
- Functions go in `packages/functions/`

## Monorepo Conventions

- Import shared modules: `@my-app/core/example`
```

---

## Types

### Project rules

Place `AGENTS.md` in the project root. Applies when working in that directory or sub-directories.

### Global rules

`~/.config/opencode/AGENTS.md` — applies across all OpenCode sessions (not committed to Git).  
Use this for personal preferences the LLM should always follow.

### Claude Code compatibility

OpenCode treats these as fallbacks:

| File | Purpose |
|------|---------|
| `CLAUDE.md` in project root | Project rules (if no `AGENTS.md` exists) |
| `~/.claude/CLAUDE.md` | Global rules (if no `~/.config/opencode/AGENTS.md` exists) |
| `~/.claude/skills/` | Skills (see [Agent Skills](https://opencode.ai/docs/skills/)) |

**Disable Claude Code compatibility:**

```bash
export OPENCODE_DISABLE_CLAUDE_CODE=1         # disable all .claude support
export OPENCODE_DISABLE_CLAUDE_CODE_PROMPT=1  # disable ~/.claude/CLAUDE.md only
export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1  # disable .claude/skills only
```

---

## Precedence

1. Local `AGENTS.md` / `CLAUDE.md` (traverses up from current directory)
2. Global `~/.config/opencode/AGENTS.md`
3. `~/.claude/CLAUDE.md` (unless disabled)

The first matching file wins per category.

---

## Custom Instructions

Via `opencode.json` — load existing rule files without duplicating them in `AGENTS.md`:

```jsonc
{
  "instructions": [
    "CONTRIBUTING.md",
    "docs/guidelines.md",
    ".cursor/rules/*.md"
  ]
}
```

Remote URLs are supported (fetched with 5-second timeout):

```jsonc
{
  "instructions": [
    "https://raw.githubusercontent.com/my-org/shared-rules/main/style.md"
  ]
}
```

All instruction files are combined with `AGENTS.md`.

---

## Referencing External Files

### Via `opencode.json` (recommended for monorepos)

```jsonc
{
  "instructions": [
    "docs/development-standards.md",
    "test/testing-guidelines.md",
    "packages/*/AGENTS.md"
  ]
}
```

### Via manual instructions in `AGENTS.md`

Teach OpenCode to read files on demand:

```markdown
# TypeScript Project Rules

## External File Loading

CRITICAL: When you encounter a file reference (e.g., @rules/general.md), use your Read
tool to load it on a need-to-know basis. Load files relevant to the specific task at hand.

Instructions:
- Do NOT preemptively load all references — use lazy loading
- When loaded, treat content as mandatory instructions that override defaults

## Development Guidelines

For TypeScript code style: @docs/typescript-guidelines.md
For React component patterns: @docs/react-patterns.md
For API design: @docs/api-standards.md
For testing: @test/testing-guidelines.md
```

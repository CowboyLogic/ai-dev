# Copilot Instruction Creator

Create custom instructions that tailor GitHub Copilot's responses at the personal,
repository, and organization level. Covers `copilot-instructions.md`, path-specific
`.instructions.md` files with `applyTo` and `excludeAgent` frontmatter,
`AGENTS.md`/`CLAUDE.md`/`GEMINI.md` agent instructions, precedence, and per-surface support.

- **Skill name:** `copilot-instruction-creator`
- **Last updated:** 2026-09-25
- **Source:** [skills/copilot-instruction-creator](https://github.com/CowboyLogic/ai-dev/tree/main/skills/copilot-instruction-creator)

---

## What it does

Custom instructions give Copilot persistent context so you do not repeat it in every
conversation. The skill guides an agent through choosing the right scope and file type,
gathering project context, structuring and writing the instructions, and testing that they
take effect. It tells the agent to check GitHub's current documentation first, because file
support differs by surface and changes often.

**Instruction types:**

| Type | Location | Notes |
|------|----------|-------|
| Personal | Copilot Chat on GitHub.com (profile picture > **Personal instructions**); `~/.copilot/copilot-instructions.md` and `~/.copilot/instructions/**/*.instructions.md` for the Copilot CLI | Individual preferences |
| Repository-wide | `.github/copilot-instructions.md` | Applies to the whole repository |
| Path-specific | `.github/instructions/**/NAME.instructions.md` | Requires an `applyTo` glob in frontmatter; optional `excludeAgent: "code-review"` or `"cloud-agent"` |
| Agent instructions | `AGENTS.md` anywhere (nearest wins), or one root `CLAUDE.md` or `GEMINI.md` | Read by Copilot agents |
| Organization | Organization **Settings** > **Copilot** > **Custom instructions** | Owners only, Copilot Business or Enterprise; GitHub.com Chat, code review, and cloud agent only |

**Precedence:** personal > repository (path-specific, then repository-wide, then agent) >
organization. All relevant instruction sets are sent to Copilot; precedence only decides
conflicts between them.

> [!WARNING]
> A path-specific `.instructions.md` file without an `applyTo` glob is never applied.
> This is the most common reason path instructions appear to do nothing.

**Workflow:**

1. Determine the scope and instruction type.
2. Gather project context and the Copilot behaviors that need correcting.
3. Structure the file — project overview, folder structure, coding standards, libraries.
4. Write short, self-contained statements that do not conflict.
5. Create the instruction files.
6. Test across Copilot features and refine.
7. Review and update as project standards change.

---

## Reference files

| File | Contents |
|------|----------|
| `references/example-repository-instructions.md` | Sample `.github/copilot-instructions.md` for a React/TypeScript project |
| `references/example-path-instructions.md` | Sample path-specific `.instructions.md` for API files, with `applyTo` frontmatter |

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill copilot-instruction-creator -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill copilot-instruction-creator --agent copilot -g
```

### Using `gh copilot` (Copilot CLI only)

```bash
gh copilot skill install CowboyLogic/ai-dev/skills/copilot-instruction-creator
```

### Verify installation

```bash
npx skills ls -g
```

---

## Related

- [Copilot Agent Creator](agent-creator-copilot.md) — custom agent personas rather than
  instructions
- [GitHub custom instructions support matrix](https://docs.github.com/en/copilot/reference/custom-instructions-support)

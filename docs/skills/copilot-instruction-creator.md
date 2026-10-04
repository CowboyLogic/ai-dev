# Copilot Instruction Creator

Create custom instructions that tailor GitHub Copilot's responses at the personal,
repository, and organization level. Covers `copilot-instructions.md`, path-specific
`.instructions.md` files with `applyTo` and `excludeAgent` frontmatter,
`AGENTS.md`/`CLAUDE.md`/`GEMINI.md` agent instructions, precedence, and per-surface support.

- **Skill name:** `copilot-instruction-creator`
- **Source:** [skills/copilot-instruction-creator](https://github.com/CowboyLogic/ai-dev/tree/main/skills/copilot-instruction-creator)

---

## What it does

Custom instructions give Copilot persistent context so you do not repeat it in every
conversation. The skill guides an agent through choosing the right scope and file type,
gathering project context, writing the instructions, and testing that they take effect.
It tells the agent to check GitHub's current documentation first, because file support
differs by surface and changes often.

**Topics covered:**

- Personal, repository-wide, path-specific, agent, and organization instructions
- Precedence between instruction sets
- Which surfaces read which files
- Structuring and writing short, non-conflicting instructions
- Testing and maintaining instructions as project standards change

## Where it applies

Use it when an agent sets up Copilot instructions for a person, a repository, or an
organization.

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

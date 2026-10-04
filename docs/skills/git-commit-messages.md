# Git Commit Messages

Write descriptive yet concise git commit messages that follow the
[Conventional Commits](https://www.conventionalcommits.org/) specification. Covers type
selection, scope notation, subject line rules, body and footer formatting, and breaking
change declarations.

- **Skill name:** `git-commit-messages`
- **Source:** [skills/git-commit-messages](https://github.com/CowboyLogic/ai-dev/tree/main/skills/git-commit-messages)

---

## What it does

The skill has an agent review the staged diff, pick a type and scope, and write a message in
the Conventional Commits format. It includes guidance and examples by change type and size,
a script that analyzes staged changes and suggests a message, and notes on wiring the
convention into VS Code and commitlint.

## Where it applies

Use it in any repository whose history follows Conventional Commits, in any client that
loads skills.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill git-commit-messages -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill git-commit-messages --agent <agent> -g
```

### Verify installation

```bash
npx skills ls -g
```

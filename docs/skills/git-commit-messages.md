# Git Commit Messages

Write descriptive yet concise git commit messages that follow the
[Conventional Commits](https://www.conventionalcommits.org/) specification. Covers type
selection, scope notation, subject line rules, body and footer formatting, and breaking
change declarations.

- **Skill name:** `git-commit-messages`
- **Last updated:** 2026-04-19
- **Source:** [skills/git-commit-messages](https://github.com/CowboyLogic/ai-dev/tree/main/skills/git-commit-messages)

---

## What it does

The skill has an agent review the staged diff, pick a type and scope, and write a message in
this structure:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

| Type | Use for |
|------|---------|
| `feat` | New feature or functionality |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting changes with no logic change |
| `refactor` | Code restructuring with no feature change or bug fix |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks and dependency updates |
| `perf` | Performance improvements |
| `ci` | CI/CD pipeline changes |
| `build` | Build system changes |

**Rules:**

- **Subject** — at most 50 characters, imperative mood ("add", not "added"), no trailing
  period, specific about what changed.
- **Body** — separated from the subject by a blank line, wrapped at 72 characters, explains
  what changed and why, and uses bullet points for multi-part changes.
- **Footer** — `BREAKING CHANGE:` with a migration path, issue references such as
  `Closes #123`, and `Co-authored-by:` trailers.

Example:

```text
fix(payment): resolve double-charge issue

Prevent duplicate payment processing when users refresh
the confirmation page. Added idempotency key validation
and improved error messaging.

Fixes #567
```

---

## Included files

| File | Contents |
|------|----------|
| `SKILL.md` | Guidelines, step-by-step instructions, and examples by change type and size |
| `examples.md` | Good and bad commit message comparisons |
| `commit-generator.py` | Python script that analyzes staged changes and suggests a message |
| `vscode-integration.md` | VS Code tasks, `commit-msg` hooks, and commitlint setup |

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

# Markdownlint Validator

Identify and fix markdownlint rule violations in Markdown files. Covers the full
[DavidAnson/markdownlint](https://github.com/DavidAnson/markdownlint) rule set (MD001–MD060)
used by VS Code, markdownlint-cli, and markdownlint-cli2, along with configuration and
inline suppression.

- **Skill name:** `markdownlint-validator`
- **Source:** [skills/markdownlint-validator](https://github.com/CowboyLogic/ai-dev/tree/main/skills/markdownlint-validator)

---

## What it does

The skill gives an agent a fix loop for lint output: collect the violations, fix the
auto-fixable ones, fix the rest manually, and re-run until the output is clean. It includes a
reference for every rule, guidance on configuration and targeted suppression, and a helper
script that runs markdownlint-cli.

## Where it applies

Use it in any repository with Markdown files, whether you lint from VS Code, markdownlint-cli,
or markdownlint-cli2.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill markdownlint-validator -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill markdownlint-validator --agent <agent> -g
```

### Verify installation

```bash
npx skills ls -g
```

# Markdownlint Validator

Identify and fix markdownlint rule violations in Markdown files. Covers the full
[DavidAnson/markdownlint](https://github.com/DavidAnson/markdownlint) rule set (MD001–MD060)
used by VS Code, markdownlint-cli, and markdownlint-cli2, along with configuration and
inline suppression.

- **Skill name:** `markdownlint-validator`
- **Last updated:** 2026-04-19
- **Source:** [skills/markdownlint-validator](https://github.com/CowboyLogic/ai-dev/tree/main/skills/markdownlint-validator)

---

## What it does

The skill gives an agent a fix loop for lint output: collect violations, fix the
auto-fixable ones with `markdownlint --fix`, fix the rest manually one rule at a time, and
re-run until the output is empty.

**Workflow:**

1. **Get the violations** — `markdownlint "docs/**/*.md"` or `bash scripts/validate.sh docs/`.
2. **Triage** — group violations by rule ID and check which are auto-fixable.
3. **Auto-fix** — `markdownlint --fix "docs/**/*.md"`.
4. **Fix the rest manually** — using the rule reference.
5. **Re-validate** — zero output means clean.

**Common violations covered by the quick-fix table:**

| Rule | Violation |
|------|-----------|
| MD009 | Trailing spaces |
| MD010 | Hard tabs |
| MD012 | Multiple consecutive blank lines |
| MD013 | Line too long |
| MD022 | Heading not surrounded by blank lines |
| MD031 | Fenced code block not surrounded by blank lines |
| MD032 | List not surrounded by blank lines |
| MD040 | Fenced code block missing a language |
| MD041 | First line is not an H1 |
| MD047 | File does not end with a newline |
| MD051 | Broken link fragment |
| MD058 | Table not surrounded by blank lines |

For violations that are intentional, the skill uses targeted inline suppression
(`<!-- markdownlint-disable-next-line MD033 -->`) or project configuration in
`.markdownlint.json` rather than blanket disabling.

---

## Reference files

| File | Contents |
|------|----------|
| `references/rules.md` | Every rule from MD001 to MD060: alias, description, whether it is auto-fixable, key parameters |
| `references/config.md` | `.markdownlint.json` format, inline suppression, VS Code integration |
| `scripts/validate.sh` | Bash helper that runs markdownlint-cli with common options |

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

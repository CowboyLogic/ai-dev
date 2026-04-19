# Markdownlint Validator

Skill for identifying and correcting markdownlint rule violations in Markdown files. Covers all rules in the [DavidAnson/markdownlint](https://github.com/DavidAnson/markdownlint) rule set (MD001–MD060).

## Purpose

Use this skill when:

- Fixing markdownlint errors reported by VS Code, CI, or markdownlint-cli
- Cleaning up markdown files before a PR or documentation publish
- Configuring `.markdownlint.json` or `.markdownlint.yaml` for a project
- Enforcing consistent markdown style across a repository

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Core workflow, common violations quick-fix table, inline suppression |
| `references/rules.md` | All MD001–MD060 rules: alias, description, fixable, key parameters |
| `references/config.md` | `.markdownlint.json` format, inline suppression, VS Code integration |
| `scripts/validate.sh` | Bash helper to run markdownlint-cli with common options |

## Sources

- Rule documentation: <https://github.com/DavidAnson/markdownlint/tree/main/doc>
- markdownlint-cli: <https://github.com/igorshubovych/markdownlint-cli>
- markdownlint-cli2: <https://github.com/DavidAnson/markdownlint-cli2>

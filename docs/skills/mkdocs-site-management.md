# MkDocs Site Management

Create and maintain [MkDocs](https://www.mkdocs.org/) documentation sites. The skill keeps
`mkdocs.yml` in sync with the `docs/` source directory, validates every configuration change
with a strict build, and resolves common build errors and warnings.

- **Skill name:** `mkdocs-site-management`
- **Source:** [skills/mkdocs-site-management](https://github.com/CowboyLogic/ai-dev/tree/main/skills/mkdocs-site-management)

---

## What it does

When pages are added, removed, or moved, an agent using this skill compares the `docs/`
directory with the `nav` section of `mkdocs.yml`, updates the navigation to match, and runs a
strict build to confirm the site still builds without errors or warnings. It also covers
resolving the errors and warnings that build reports.

## Where it applies

Use it in any repository that publishes a MkDocs site. This repository's own documentation
site uses the same workflow; see [Contributing](../contributing.md) for the local build
commands.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill mkdocs-site-management -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill mkdocs-site-management --agent <agent> -g
```

### Verify installation

```bash
npx skills ls -g
```

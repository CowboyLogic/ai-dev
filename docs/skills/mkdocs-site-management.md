# MkDocs Site Management

Create and maintain [MkDocs](https://www.mkdocs.org/) documentation sites. The skill keeps
`mkdocs.yml` in sync with the `docs/` source directory, validates every configuration change
with a strict build, and resolves common build errors and warnings.

- **Skill name:** `mkdocs-site-management`
- **Last updated:** 2026-04-19
- **Source:** [skills/mkdocs-site-management](https://github.com/CowboyLogic/ai-dev/tree/main/skills/mkdocs-site-management)

---

## What it does

When pages are added, removed, or moved, an agent using this skill compares the `docs/`
directory with the `nav` section of `mkdocs.yml`, updates the navigation to match, and runs
`mkdocs build --clean --strict` to confirm the site still builds without errors or warnings.

**Workflow:**

1. **Verify setup** — confirm MkDocs is installed, then locate `mkdocs.yml` and the source
   directory.
2. **Handle source changes** — add, remove, or re-nest `nav` entries to match the files.
3. **Change configuration** — edit `mkdocs.yml`, then run the strict build.
4. **Resolve issues** — fix any errors or warnings the build reports.
5. **Validate** — re-run the strict build until it is clean; optionally preview with
   `mkdocs serve`.

**Build issues covered:**

| Issue | Resolution |
|-------|------------|
| Page listed in navigation but not found | Add the missing file or remove the `nav` entry |
| YAML parsing error | Check indentation and quoting in `mkdocs.yml` |
| Plugin error or warning | Verify the plugin is installed and configured |
| Broken internal link | Update the link to match the current file structure |
| Theme warning | Verify the theme name and custom theme paths |
| Site does not update after a build | Rebuild with `--clean` |

> [!TIP]
> This repository's own documentation site uses the same workflow. See
> [Contributing](../contributing.md) for the local build commands.

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

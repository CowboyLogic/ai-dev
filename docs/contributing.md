# Contributing to AI Dev

Contributions of all kinds are welcome — agent configurations, MCP integration examples, documentation improvements, and troubleshooting guides.

**New to open source contributing?** See GitHub's [Contributing to Projects Guide](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project).

## Quick Start

1. Fork the repository and clone your fork
2. Create a descriptive branch (`add-postgres-mcp-config`, `fix-opencode-docs`)
3. Make your changes following the guidelines below
4. Run `mkdocs build` to verify everything renders correctly
5. Open a Pull Request with a clear description

## What to Contribute

| Type | Where to Put It |
| ---- | --------------- |
| MCP server configs | `mcp/sample-configs/` |
| Agent definitions | `docs/agents/` |
| Skill instructions | `docs/skills/<skill-name>/` |
| Tool documentation | `docs/tools/<tool-name>/` |
| General docs | `docs/` |

## Guidelines

### Configuration Files

Configurations should be self-documenting. Include inline comments explaining non-obvious settings, and never hardcode secrets — always reference environment variables:

```json
{
  "postgres": {
    "type": "local",
    "command": ["docker", "run", "--rm", "-i", "postgres-mcp"],
    "environment": {
      "DB_PASSWORD": "${DB_PASSWORD}"
    }
  }
}
```

> [!NOTE]
> JSON doesn't officially support comments, but they are shown here for illustration. Use a companion README for setup instructions when needed.

**Each configuration should be accompanied by:**

- Prerequisites (tools, accounts, environment variables needed)
- Setup instructions
- At least one usage example
- Common troubleshooting tips

### Documentation

All docs use [GitHub Flavored Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).

### Keeping Docs in Sync

When you change a configuration or behavior, update the related documentation in the same PR. Common places to check:

- Companion `README.md` files
- `docs/` pages that reference the changed content
- `mkdocs.yml` nav (required when adding or removing pages)
- `AGENTS.md` if agent behavior changes

## Pre-Submission Checklist

Before opening a PR:

- [ ] Configurations tested and working in a real environment
- [ ] All links resolve correctly
- [ ] Code blocks have language specifiers
- [ ] No hardcoded secrets or tokens
- [ ] `mkdocs build` passes without warnings
- [ ] `mkdocs.yml` updated if pages were added or removed
- [ ] Related documentation updated in the same PR

## Review and Merge

PRs are reviewed for accuracy, formatting, and completeness. At least one maintainer approval is required. Expect a response within a week — if you haven't heard back, feel free to ping on the issue.

## Questions and Feedback

- **Found a bug or gap?** [File an issue](https://github.com/CowboyLogic/ai-dev/issues)
- **Have an idea?** Start a discussion before building something large
- **Not sure it's ready?** Open a draft PR for early feedback

## Code of Conduct

Be respectful and constructive. Focus on the content, not the person. Assume good intentions and help keep this a welcoming space.

## License

By contributing, you agree that your work will be licensed under the same license as this project.

---

**Thank you for contributing!** Your improvements help the entire AI development community.

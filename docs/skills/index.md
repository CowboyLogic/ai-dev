# Agent Skills

Structured instruction sets that give AI agents specialized domain knowledge and workflows.
Skills follow the [Agent Skills open standard](https://agentskills.io) and are discoverable
by the GitHub Copilot CLI.

All skill files live at the root of the repository under
[`skills/`](https://github.com/CowboyLogic/ai-dev/tree/main/skills)
and can be installed directly using the GitHub Copilot CLI.

---

## Installing Skills

```bash
# Install a specific skill
gh copilot skill install CowboyLogic/ai-dev/skills/<skill-name>

# Browse all skills
gh copilot skill list CowboyLogic/ai-dev
```

---

## Core Skills

### High-Fidelity Context Scaffolder

Generate machine-optimized XML context files (`AGENTS.xml`, `ARCHITECTURE.xml`) for AI agent orchestration.
Produces structured, information-dense context that agents consume at session start to understand a codebase
without exploration overhead.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/high-fidelity-context-scaffolder)

---

### Google Style Docs

Write technical documentation following the Google Developer Documentation Style Guide.
Covers voice and tone, sentence structure, code samples, cross-references, and all
formatting conventions from Google's published standard.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/google-style-docs)

---

### Git Commit Messages

Write descriptive yet concise git commit messages following the Conventional Commits specification.
Covers type selection, scope notation, subject line rules, and multi-paragraph body formatting.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/git-commit-messages)

---

## Development Skills

### Docker Image Management

Build, tag, push, and manage Docker images across registries. Covers Dockerfile best practices,
multi-stage builds, docker-compose patterns, registry authentication, and image lifecycle management.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/docker-image-management)

---

### MkDocs Site Management

Build and maintain MkDocs documentation sites. Covers `mkdocs.yml` configuration, nav structure,
Material theme features, build validation, and resolving common build errors and warnings.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/mkdocs-site-management)

---

### Markdownlint Validator

Validate and fix Markdown files against markdownlint rules. Covers rule reference, configuration
options, integration with VS Code and CI, and automated fix workflows.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/markdownlint-validator)

---

## Copilot / VS Code Skills

### Copilot Agent Creator {#copilot-agent-creator}

Create custom `.agent.md` files for GitHub Copilot in VS Code. Covers frontmatter schema,
tool aliases, model selection, skill references, and platform compatibility. Includes
working examples for workspace agents, user-profile agents, and cloud agents with MCP.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-copilot)

---

### Copilot Instruction Creator

Create `copilot-instructions.md` files that tailor Copilot's behavior for a repository or workspace.
Covers repository instructions, path-scoped instructions, and prompt engineering for Copilot.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/copilot-instruction-creator)

---

### Copilot Prompt Creator

Create reusable `.prompt.md` files for GitHub Copilot based on the latest GitHub research
into effective prompt structures.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/copilot-prompt-creator)

---

## AI Platform Skills

### OpenCode Agent Creator

Create custom agent definitions for the OpenCode CLI. Covers the agent configuration schema,
model selection, tool permissions, MCP server integration, and subagent patterns.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-opencode)

---

## AI Client Configuration Skills

### Claude Code Settings Manager

Manage and maintain `~/.claude/settings.json` and all Claude Code configuration files.
Covers permissions, hooks, MCP servers, environment variables, model settings,
sandbox configuration, and auto mode.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-claudecode)

---

### Copilot CLI Configuration Manager

Manage GitHub Copilot CLI configuration files — `config.json`, `mcp-config.json`, hooks,
skills, and custom instructions. Covers trusted folders, tool permissions, MCP servers,
BYOK models, and authentication.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-copilotcli)

---

### Gemini CLI Configuration Manager

Manage Gemini CLI configuration files — `settings.json`, MCP servers, hooks, extensions,
custom commands, themes, and trusted folders. Covers all settings exposed by the Gemini CLI.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-geminicli)

---

### OpenCode Configuration Manager

Manage opencode configuration files — `opencode.json`, providers, agents, MCP servers,
permissions, keybinds, themes, formatters, and custom commands.

[View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-opencode)

---

## Skill Structure

Each skill directory contains:

- **`SKILL.md`** — Main instruction file with YAML frontmatter and detailed guidance
- **`README.md`** — Human-readable overview (most skills)
- **`references/`** — Supporting reference material, schemas, and examples (where applicable)
- **`scripts/`** — Validation tools and utilities (where applicable)

---

## Additional Resources

- [Agent Skills Open Standard](https://agentskills.io) — Official specification
- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Anthropic's guide (applies broadly to other agents too)

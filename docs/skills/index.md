# Agent Skills

Structured instruction sets that give AI agents specialized domain knowledge and workflows.
Skills follow the [Agent Skills open standard](https://agentskills.io) and are installable
across all major agent tools using `npx skills`.

All skill files live at the root of the repository under
[`skills/`](https://github.com/CowboyLogic/ai-dev/tree/main/skills).

---

## Installing Skills

### Using `npx skills` (recommended — works across all agents)

```bash
# Install a specific skill globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill <skill-name> -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill <skill-name> --agent <agent> -g

# Preview available skills without installing
npx skills add CowboyLogic/ai-dev -g -l

# List all installed skills
npx skills ls -g
```

### Using `gh copilot` (Copilot CLI only)

```bash
# Install a specific skill
gh copilot skill install CowboyLogic/ai-dev/skills/<skill-name>

# Browse all skills
gh copilot skill list CowboyLogic/ai-dev
```

---

## Core Skills

### About-Me Skill Creator

Create a private `about-me` skill containing durable personal context — background,
tooling, constraints, and how much autonomy you want — for agents to load each session.
The conversational wizard drafts the profile and writes it to a user-selected location,
defaulting to `~/.claude/skills/about-me`.

The generated `about-me` profile is personal and is not meant to be committed. It is
used by the [Lane Topology](../agents/lane-topology.md) Conductor as step one of every
session.

[Skill Overview](about-me-skill-creator.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/about-me-skill-creator)

---

### High-Fidelity Context Scaffolder

Generate machine-optimized XML context files (`AGENTS.xml`, `ARCHITECTURE.xml`) for AI agent orchestration.
Produces structured, information-dense context that agents consume at session start to understand a codebase
without exploration overhead.

[Skill Overview](high-fidelity-context-scaffolder.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/high-fidelity-context-scaffolder)

---

### Google Style Docs

Write technical documentation following the Google Developer Documentation Style Guide.
Covers voice and tone, sentence structure, code samples, cross-references, and all
formatting conventions from Google's published standard.

[Skill Overview](google-style-docs.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/google-style-docs)

---

### Git Commit Messages

Write descriptive yet concise git commit messages following the Conventional Commits specification.
Covers type selection, scope notation, subject line rules, and multi-paragraph body formatting.

[Skill Overview](git-commit-messages.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/git-commit-messages)

---

## Development Skills

### Docker Image Management

Build, tag, push, and manage Docker images across registries. Covers Dockerfile best practices,
multi-stage builds, docker-compose patterns, registry authentication, and image lifecycle management.

[Skill Overview](docker-image-management.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/docker-image-management)

---

### MkDocs Site Management

Build and maintain MkDocs documentation sites. Covers `mkdocs.yml` configuration, nav structure,
Material theme features, build validation, and resolving common build errors and warnings.

[Skill Overview](mkdocs-site-management.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/mkdocs-site-management)

---

### Markdownlint Validator

Validate and fix Markdown files against markdownlint rules. Covers rule reference, configuration
options, integration with VS Code and CI, and automated fix workflows.

[Skill Overview](markdownlint-validator.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/markdownlint-validator)

---

## Copilot / VS Code Skills

### Copilot Agent Creator {#copilot-agent-creator}

Create custom `.agent.md` files for GitHub Copilot across VS Code, the Copilot CLI, and the
GitHub.com cloud agent. Covers frontmatter schema and per-surface compatibility, tool aliases
and VS Code tool sets, current model selection, handoffs, hooks, and MCP servers. Includes
working examples for workspace agents, user-profile agents, and cloud agents with MCP.

[Skill Overview](agent-creator-copilot.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-copilot)

---

### Copilot Instruction Creator

Create custom instructions that tailor Copilot's behavior at the personal, repository, and
organization level. Covers `copilot-instructions.md`, path-specific `.instructions.md` files with
`applyTo` and `excludeAgent` frontmatter, `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` agent instructions,
precedence, and per-surface support.

[Skill Overview](copilot-instruction-creator.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/copilot-instruction-creator)

---

## AI Platform Skills

### OpenCode Agent Creator

Create custom agent definitions for the OpenCode CLI, in native V2 format by default with V1
still supported. Covers the agent configuration schema, V1 → V2 migration, model and variant
selection, ordered permission rules, and subagent patterns.

[Skill Overview](agent-creator-opencode.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/agent-creator-opencode)

---

## AI Client Configuration Skills

### Claude Code Settings Manager

Manage and maintain `~/.claude/settings.json` and all Claude Code configuration files.
Covers permissions, hooks, MCP servers, environment variables, model settings,
sandbox configuration, and auto mode.

[Skill Overview](client-config-claudecode.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-claudecode)

> [!NOTE]
> When using a newer Claude model for configuring Claude Code, this skill has marginal value.

---

### Copilot CLI Configuration Manager

Manage GitHub Copilot CLI configuration files — `settings.json`, `config.json`,
`permissions-config.json`, `mcp-config.json`, `lsp-config.json`, hooks, skills, custom agents,
plugins, and custom instructions. Covers trusted folders, tool permissions and sandboxing,
MCP and LSP servers, BYOK models, and authentication.

[Skill Overview](client-config-copilotcli.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-copilotcli)

---

> [!NOTE]
> The Gemini CLI Configuration Manager skill was removed following Google's [announcement that Gemini CLI is being replaced by Antigravity CLI for unpaid-tier and Google One users](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/).

---

### OpenCode Configuration Manager

Manage opencode configuration files for OpenCode V2 and V1 — `opencode.json`, `cli.json`
(V2) or `tui.json` (V1), providers, agents, MCP servers, permissions, plugins, keybinds,
themes, formatters, and custom commands, plus V1 → V2 migration.

[Skill Overview](client-config-opencode.md) · [View on GitHub](https://github.com/CowboyLogic/ai-dev/tree/main/skills/client-config-opencode)

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

# Agent Skills

This directory contains documentation for Agent Skills available in this repository. Agent Skills are specialized instruction sets that enhance AI assistants' capabilities for specific development tasks and workflows.

## What are Agent Skills?

Agent Skills are structured collections of instructions, templates, examples, and resources that teach AI agents how to perform specialized tasks more effectively. They follow the [Agent Skills open standard](https://agentskills.io) and enable agents to:

- Access domain-specific knowledge and best practices
- Follow established workflows and conventions
- Use project-specific tools and configurations
- Generate code and documentation with higher accuracy
- Maintain consistency across team development efforts

## Available Skills

### Core Skills

- **[High-Fidelity Context Scaffolder](high-fidelity-context-scaffolder/README.md)** - Generate machine-optimized XML context files for AI agent orchestration
- **[Google Style Docs](google-style-docs/README.md)** - Write technical documentation following Google's Developer Documentation Style Guide
- **[Copilot Agent Creator](agent-creator-copilot/README.md)** - Create custom agents and extensions for VS Code and GitHub Copilot
- **[Copilot Instruction Creator](copilot-instruction-creator/README.md)** - Create custom instructions to tailor GitHub Copilot responses
- **[Copilot Prompt Creator](copilot-prompt-creator/README.md)** - Create custom prompts for Copilot with latest GitHub research

### Development Skills

- **[Git Commit Messages](git-commit-messages/README.md)** - Write descriptive yet succinct git commit messages
- **[Docker Image Management](docker-image-management/README.md)** - Build, manage, and publish Docker images
- **[MkDocs Site Management](mkdocs-site-management/README.md)** - Build and maintain MkDocs documentation sites

### AI Platform Skills

- **[OpenCode Agent Creator](agent-creator-opencode/README.md)** - Create custom agents for the OpenCode CLI

### AI Client Configuration Skills

- **[Claude Code Settings Manager](client-config-claudecode/SKILL.md)** - Manage and maintain `~/.claude/settings.json` and all Claude Code configuration files
- **[Copilot CLI Configuration Manager](client-config-copilotcli/SKILL.md)** - Manage GitHub Copilot CLI configuration files including `config.json`, MCP servers, hooks, and custom instructions
- **[Gemini CLI Configuration Manager](client-config-geminicli/SKILL.md)** - Manage Gemini CLI configuration files including `settings.json`, MCP servers, hooks, extensions, and custom commands
- **[OpenCode Configuration Manager](client-config-opencode/SKILL.md)** - Manage opencode configuration files including `opencode.json`, providers, agents, MCP servers, and permissions

## Skill Structure

Each skill directory typically contains:

- **`SKILL.md`** - Main instruction file with YAML frontmatter and detailed guidance
- **`README.md`** - Human-readable overview and usage examples
- **Templates and examples** - Code samples, configuration files, and reference implementations
- **Supporting scripts** - Validation tools, generators, and utilities

## Using Skills

Skills are automatically discovered by AI agents when working in this repository. You can also:

1. **Reference skills explicitly** - Ask agents to "use the [skill name] skill" for specific tasks
2. **Browse skill documentation** - Read the README.md and SKILL.md files for detailed guidance
3. **Apply skill templates** - Use provided templates and examples as starting points

## Contributing Skills

To add new skills to this repository:

1. Follow the [Agent Skills standard](https://agentskills.io)
2. Use the [Skill Creator skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator) to generate it
3. Add the skill to this `docs/skills/` directory
4. Update the MkDocs navigation in `mkdocs.yml`

> [!TIP]
> **Want to create a new skill?** Anthropic publishes their own [Skill Creator skill](https://github.com/anthropics/skills/tree/main/skills/skill-creator) on GitHub — you can use it directly to generate new skills. It's also a great example of how well-crafted skills are structured.

## Additional Resources

- [Agent Skills Open Standard](https://agentskills.io) - Official specification and documentation
- [GitHub Copilot Skills](https://docs.github.com/en/copilot/using-github-copilot/using-extensions-to-integrate-external-tools-with-copilot) - Copilot-specific skill integration
- [Claude Skills Documentation](https://docs.anthropic.com/claude/docs/skills) - Claude-specific skill usage
- [The Complete Guide to Building Skill for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) - Anthropic's complete guide for building skills for Claude. These also work with other GenAI agents! Must read!

## Repository Structure

```
docs/skills/             # Skill definitions and documentation
├── high-fidelity-context-scaffolder/ # Generate XML context files
├── google-style-docs/   # Google Developer Documentation style
├── agent-creator-copilot/  # Copilot agent development
├── agent-creator-opencode/ # OpenCode CLI agent development
├── copilot-instruction-creator/ # Copilot customization
├── copilot-prompt-creator/  # Copilot prompt creation
├── git-commit-messages/     # Git commit message conventions
├── docker-image-management/ # Docker image workflows
├── mkdocs-site-management/  # MkDocs documentation sites
├── client-config-claudecode/ # Claude Code settings management
├── client-config-copilotcli/ # GitHub Copilot CLI configuration
├── client-config-geminicli/  # Gemini CLI configuration
└── client-config-opencode/   # OpenCode configuration management
```
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

- **[Skill Creator](skill-creator/README.md)** - Learn how to create new Agent Skills following the open standard
- **[Google Style Docs](google-style-docs/README.md)** - Write technical documentation following Google's Developer Documentation Style Guide
- **[Copilot Agent Creator](copilot-agent-creator/README.md)** - Create custom agents and extensions for VS Code and GitHub Copilot
- **[Copilot Instruction Creator](copilot-instruction-creator/README.md)** - Create custom instructions to tailor GitHub Copilot responses
- **[Copilot Prompt Creator](copilot-prompt-creator/README.md)** - Create custom prompts for Copilot with latest GitHub research

### Development Skills

- **[.NET API Development](dotnet-api-development/README.md)** - Build ASP.NET Core APIs with proper architecture and patterns
- **[ReactJS/NodeJS Web Apps](react-nodejs-webapp/README.md)** - Create full-stack React applications with Node.js backends
- **[PostgreSQL Database](postgresql-database/README.md)** - Design, implement, and optimize PostgreSQL databases
- **[Git Commit Messages](git-commit-messages/README.md)** - Write descriptive yet succinct git commit messages
- **[Amazon Web Services](amazon-web-services/README.md)** - Expert guidance for AWS development, deployment, and operations
- **[Azure](azure/README.md)** - Expert guidance for Microsoft Azure development, deployment, and operations

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
2. Use the [Skill Creator](skill-creator/README.md) skill for guidance
3. Place skills in the `.github/skills/` directory
4. Add documentation to this `docs/skills/` directory
5. Update the MkDocs navigation in `mkdocs.yml`

## Additional Resources

- [Agent Skills Open Standard](https://agentskills.io) - Official specification and documentation
- [GitHub Copilot Skills](https://docs.github.com/en/copilot/using-github-copilot/using-extensions-to-integrate-external-tools-with-copilot) - Copilot-specific skill integration
- [Claude Skills Documentation](https://docs.anthropic.com/claude/docs/skills) - Claude-specific skill usage

## Repository Structure

```
.github/skills/          # Authoritative skill definitions
├── skill-creator/       # Meta-skill for creating skills
├── google-style-docs/   # Documentation skill
├── copilot-agent-creator/ # Copilot agent development
├── copilot-instruction-creator/ # Copilot customization
├── copilot-prompt-creator/ # Copilot prompt creation
├── dotnet-api-development/  # .NET API development
├── react-nodejs-webapp/     # React/Node.js development
└── postgresql-database/     # PostgreSQL database development

docs/skills/             # Published skill documentation
├── skill-creator/
├── google-style-docs/
├── copilot-agent-creator/
├── copilot-instruction-creator/
├── copilot-prompt-creator/
├── dotnet-api-development/
├── react-nodejs-webapp/
└── postgresql-database/
```
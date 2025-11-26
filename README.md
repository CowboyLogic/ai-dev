# AI Development Tools & Configurations

A centralized repository for AI tools, agents, and configurations to streamline AI-assisted development workflows.

> [!IMPORTANT]
> This repository is both a live repository and a work in progress.
> It does and will contain information and insights I gain on my journey through the ever-changing AI landscape!
> Happy Trails! 

## Purpose

This repository serves as a comprehensive resource for:

- **AI Agent Configurations**: Ready-to-use configurations for various AI development agents and assistants
- **Tool Integration**: Settings and configurations for integrating AI tools into development environments
- **Best Practices**: Documented patterns and approaches for working with AI coding assistants
- **Shared Resources**: A collaborative space to store and share AI development configurations with the community

## Structure

- **`agents/`** - Configuration files and documentation for AI agents
  - `LLM-BaselineBehaviors.md` - Authoritative behavioral baseline for all AI assistants
- **`opencode/`** - OpenCode CLI configurations and samples
  - `opencode.json` - Main configuration file
  - `modular-config/` - Advanced modular subagent configuration
- **`mcp/`** - Model Context Protocol (MCP) server configurations
  - `sample-configs/` - Example configuration files for different MCP setups
- **`docs/`** - Comprehensive documentation site (MkDocs)
  - **`docs/tools/vscode/`** - Visual Studio Code agent/subagent configuration guide
  - **`docs/tools/opencode/`** - OpenCode configuration documentation

## Getting Started

### For AI Assistants

1. Read the **[LLM Baseline Behaviors](agents/LLM-BaselineBehaviors.md)** document
2. Review tool-specific `AGENTS.md` files
3. Follow instruction priority: User directives → Project rules → Tool guidelines → Baseline behaviors

### For Developers

Browse the directories to find configuration files relevant to your development environment:

- **[VS Code Agent/SubAgent Guide](docs/tools/vscode/README.md)** - Implementing efficient AI workflows with GitHub Copilot
- **[OpenCode Configuration](docs/tools/opencode/index.md)** - CLI tool with specialized agents
- **[MCP Server Examples](mcp/sample-configs/)** - Model Context Protocol integrations

Each configuration includes:
- Setup instructions
- Usage examples
- Customization options
- Integration guidelines

## Contributing

Contributions are welcome! If you have configurations or patterns that have improved your AI-assisted development workflow, feel free to share them here.

## Documentation

- See `AGENTS.md` files in respective directories for detailed documentation on specific agents and their configurations
- Check individual configuration files for inline documentation and usage notes

---

*This repository is actively maintained and updated with new configurations as AI development tools evolve.*

# AI Development Tools & Configurations

Welcome to the centralized repository for AI tools, agents, and configurations designed to streamline AI-assisted development workflows.

## Overview

This repository serves as a comprehensive resource for developers working with AI coding assistants. Whether you're using GitHub Copilot, Claude, GPT-4, or other AI models, you'll find configurations and guidelines to ensure consistent, efficient, and high-quality assistance.

## What's Inside

### 🤖 Behavioral Baseline

The **[LLM Baseline Behaviors](agents/baseline-behaviors.md)** document defines the standard behavioral expectations for all AI assistants working in development environments. This ensures consistency across different models and platforms.

Key aspects covered:
- **Communication Style** - Conversational clarity with appropriate detail
- **Action-Oriented Behavior** - Implementation over suggestion
- **Tool Usage** - Efficient patterns for file operations, searches, and edits
- **Code Quality** - Standards for writing, testing, and validating code
- **Problem-Solving** - Approaches for debugging, error handling, and unknown territory

### ⚙️ OpenCode CLI Configuration

The **[OpenCode](tools/opencode/index.md)** directory contains comprehensive configurations for the OpenCode CLI tool, including:

- **Tiered AI Models** - Smart model selection for different task types
- **Specialized Agents** - Pre-configured agents for quick fixes, code review, and documentation
- **Custom Commands** - Ready-to-use commands for common workflows
- **MCP Server Integration** - Examples for Docker and NPX-based Model Context Protocol servers

[Explore OpenCode Configuration →](tools/opencode/index.md)

### 📋 Agent Guidelines

Directory-specific `AGENTS.md` files provide targeted guidance for AI assistants:

- **Root Guidelines** - Overall repository structure and instruction priority
- **Agents Directory** - Core behavioral configurations
- **OpenCode Guidelines** - Tool-specific instructions and best practices

## Quick Start

### For AI Assistants

1. Read the **[LLM Baseline Behaviors](agents/baseline-behaviors.md)** document
2. Review any tool-specific `AGENTS.md` files in relevant directories
3. Follow the instruction priority hierarchy:
   - Explicit user directives (highest priority)
   - Project-specific rules
   - Tool-specific guidelines
   - Baseline behaviors (foundation)

### For Developers

1. Browse the configurations in the **[OpenCode](tools/opencode/index.md)** directory
2. Review sample configurations in `opencode/sample-configs/`
3. Adapt configurations to your development workflow
4. Reference the baseline behaviors when configuring your AI tools

## Key Features

### 🎯 Consistent AI Behavior

The baseline behavioral model ensures all AI assistants:
- Communicate clearly and conversationally
- Take action rather than just suggesting
- Complete tasks fully before stopping
- Use tools efficiently with proper context gathering
- Follow code quality and security standards

### 🔧 Ready-to-Use Configurations

Pre-configured setups for:
- Multi-model AI environments
- Specialized agents (quick fixes, reviews, documentation)
- MCP server integrations
- Custom command workflows

### 📚 Comprehensive Documentation

- Detailed explanations for all configurations
- Examples and use cases
- Best practices and troubleshooting guides
- GitHub Flavored Markdown format throughout

## Repository Structure

```
ai-dev/
├── agents/
│   ├── LLM-BaselineBehaviors.md    # Authoritative behavioral baseline
│   └── AGENTS.md                   # Agent configuration guidelines
├── opencode/
│   ├── opencode.json               # Main OpenCode configuration
│   ├── sample-configs/             # Example MCP server setups
│   ├── README.md                   # Human-readable guide
│   └── AGENTS.md                   # AI assistant guide
├── docs/                           # MkDocs documentation
├── AGENTS.md                       # Root agent guidelines
├── README.md                       # Repository overview
└── mkdocs.yml                      # Documentation site config
```

## Contributing

Contributions are welcome! If you have configurations or patterns that have improved your AI-assisted development workflow:

1. Fork the repository
2. Add your configuration to the appropriate directory
3. Document it in relevant README or AGENTS.md files
4. Submit a pull request

See **[Contributing Guidelines](contributing.md)** for more details.

## Use Cases

### Setting Up AI Tools

Use the baseline behaviors document to configure AI assistants in:
- VS Code extensions
- CLI tools like OpenCode
- Custom AI integrations
- Team collaboration environments

### Standardizing Team AI Usage

Organizations can adopt these configurations to:
- Ensure consistent AI behavior across team members
- Establish code quality standards
- Define communication preferences
- Create custom workflows for common tasks

### Learning Best Practices

Developers can reference these configurations to understand:
- Effective AI assistant communication patterns
- Tool usage optimization
- Task management for complex projects
- Security and quality considerations

## Resources

- **[LLM Baseline Behaviors](agents/baseline-behaviors.md)** - Foundational behavioral model
- **[OpenCode Configuration](tools/opencode/index.md)** - Detailed OpenCode setup guide
- **[GitHub Repository](https://github.com/CowboyLogic/ai-dev)** - Source code and issues

## About

This repository is actively maintained and updated as AI development tools evolve. The configurations reflect real-world usage patterns and best practices for AI-assisted development.

---

**Ready to get started?** Explore the [Getting Started Guide](getting-started/overview.md) or dive into the [OpenCode Configuration](tools/opencode/index.md).

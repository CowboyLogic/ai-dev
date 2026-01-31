# AI Development Tools & Configurations

Welcome to my repository for AI tools, agents, and configurations designed to streamline AI-assisted development workflows.

## Overview

This repository provides **practical configurations and working examples** for AI coding assistants. We focus on concrete implementations you can copy and adapt, not rewriting vendor documentation.

### Official Documentation

For comprehensive tool documentation, see:

- **[GitHub Copilot](https://docs.github.com/en/copilot)** - Official GitHub Copilot documentation
- **[Model Context Protocol](https://modelcontextprotocol.io)** - MCP specification and guides  
- **[OpenCode AI](https://opencode.ai/docs)** - OpenCode CLI documentation
- **[VS Code](https://code.visualstudio.com/docs)** - Visual Studio Code documentation

This repository complements official docs with **ready-to-use configurations, integration patterns, and behavioral guidelines**.

## What's Inside

This repository provides the following resources:

- **Behavioral Guidelines**:
  - [LLM Baseline Behaviors](LLM-BaselineBehaviors.md): Defines standard expectations for AI assistants.
  - [Copilot Instructions](copilot-instructions.md): Repository-specific directives for GitHub Copilot.

- **Contributing**:
  - [Contributing Guide](contributing.md): Learn how to contribute configurations, examples, and documentation improvements.

- **Tool Configurations**:
  - OpenCode CLI: Pre-configured agents and modular patterns for AI workflows.
  - VS Code: Integration examples and best practices.

- **Documentation**:
  - Tutorials, API references, and troubleshooting guides for AI tools.

Explore the repository to find practical examples and ready-to-use configurations.

### 🤖 Behavioral Baseline

The **[LLM Baseline Behaviors](LLM-BaselineBehaviors.md)** document defines the standard behavioral expectations for all AI assistants working in development environments. This ensures consistency across different models and platforms.

Key aspects covered:

- **Communication Style** - Conversational clarity with appropriate detail
- **Action-Oriented Behavior** - Implementation over suggestion
- **Tool Usage** - Efficient patterns for file operations, searches, and edits
- **Code Quality** - Standards for writing, testing, and validating code
- **Problem-Solving** - Approaches for debugging, error handling, and unknown territory

### ⚙️ Tool Configurations

#### OpenCode CLI

The **[OpenCode](tools/opencode/index.md)** directory provides two configuration approaches:

**Standard Configuration** (`opencode/standard-config/`)

- Single-file configuration with tiered agents
- Pre-configured agents for quick fixes, code review, and documentation
- Custom commands for common workflows
- MCP server integration examples

**Agent/SubAgent Configuration** - Modular pattern with 13 specialized subagents

- Individual agent definitions in markdown files with YAML frontmatter
- Automatic agent discovery and configuration loading
- Specialized agents: API design, security, DevOps, cloud, database, testing, performance, and more

**[📖 OpenCode Configuration Guide →](tools/opencode/configuration.md)**
- Ideal for complex projects and team collaboration

[Explore OpenCode Configuration →](tools/opencode/index.md)

#### Visual Studio Code

The **[VS Code Agent/SubAgent Guide](tools/vscode/README.md)** provides comprehensive documentation for implementing efficient AI agent workflows in VS Code using GitHub Copilot:

- **[Quick Start](tools/vscode/quick-start.md)** - Get your first agent running in 5 minutes
- **[Markdown-Based Agents](tools/vscode/markdown-agents.md)** - Declarative configuration with YAML frontmatter (recommended)
- **[Programmatic SubAgents](tools/vscode/subagent-tool.md)** - Complex autonomous task delegation
- **[Agent Examples Library](tools/vscode/agent-examples.md)** - Ready-to-use configurations for common tasks
- **[Best Practices](tools/vscode/best-practices.md)** - Optimization patterns and team collaboration
- **[Troubleshooting](tools/vscode/troubleshooting.md)** - Common issues and solutions

[Explore VS Code Agent Configuration →](tools/vscode/README.md)

### 📋 Agent Guidelines

Directory-specific `AGENTS.md` files provide targeted guidance for AI assistants:

- **Root Guidelines** - Overall repository structure and instruction priority
- **Agents Directory** - Core behavioral configurations
- **OpenCode Guidelines** - Tool-specific instructions and best practices

## Quick Start

### For AI Assistants

1. Read the **[LLM Baseline Behaviors](LLM-BaselineBehaviors.md)** document
2. Review any tool-specific `AGENTS.md` files in relevant directories
3. Follow the instruction priority hierarchy:
   - Explicit user directives (highest priority)
   - Project-specific rules
   - Tool-specific guidelines
   - Baseline behaviors (foundation)

### For Developers

#### Path 1: Using OpenCode CLI

1. Review the **[OpenCode Overview](tools/opencode/index.md)**
2. Copy configuration to your project:
   ```bash
   # Standard configuration (recommended for getting started)
   cp docs/tools/opencode/standard-config/opencode.json ~/your-project/.opencode.json
   
   # OR agent/subagent configuration (for complex projects)
   cp -r docs/tools/opencode/agent-subagent-config/* ~/your-project/
   ```
   📖 **[Complete Configuration Guide →](tools/opencode/configuration.md)**
3. Customize agents and commands for your needs
4. Set required environment variables (e.g., `GITHUB_TOKEN`)
5. Start using custom commands like `opencode quick-fix` or `opencode review`

#### Path 2: Configuring AI Assistant Behavior

1. Read the **[LLM Baseline Behaviors](LLM-BaselineBehaviors.md)** document
2. Use it as instruction material for your AI tools
3. Add project-specific rules on top of the baseline
4. Reference the baseline in your tool configurations

#### Path 3: Learning Best Practices

1. Explore the **[Behavioral Baseline](LLM-BaselineBehaviors.md)** to understand effective AI patterns
2. Review **[Sample Configurations](tools/opencode/samples.md)** for practical examples
3. Read **[LLM Baseline Behaviors](LLM-BaselineBehaviors.md)** for instruction hierarchy
4. Apply patterns to your own AI tool setup

## Key Concepts

### Behavioral Baseline

The **LLM Baseline Behaviors** document is the foundation of this repository. It defines how AI assistants should:

- Communicate (conversational and clear)
- Take action (implement rather than suggest)
- Use tools (efficiently with proper context)
- Handle errors (actively investigate and resolve)
- Maintain quality (code standards and testing)

### Instruction Hierarchy

When multiple instruction sources exist, follow this priority:

1. **Explicit user directives** - Direct commands in the current conversation
2. **Project-specific rules** - Guidelines in `.cursor/rules/` or similar
3. **Tool-specific guidelines** - Instructions in AGENTS.md files
4. **Baseline behaviors** - The foundational model

### Specialized Agents

Pre-configured agents handle specific workflows:

- **Quick agent** - Fast operations with lightweight model
- **Reviewer agent** - Read-only code analysis
- **Docs agent** - Documentation generation

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
│   ├── agent-subagent-config/      # Modular subagent configuration
│   ├── emulating-claude/           # Modular fully autonomous subagent configuration
│   ├── README.md                   # Human-readable guide
│   └── AGENTS.md                   # AI assistant guide
├── mcp/
│   ├── sample-configs/             # Example MCP server setups
│   └── README.md                   # MCP overview
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

- **[LLM Baseline Behaviors](LLM-BaselineBehaviors.md)** - Foundational behavioral model
- **[OpenCode Configuration](tools/opencode/index.md)** - Detailed OpenCode setup guide
- **[GitHub Repository](https://github.com/CowboyLogic/ai-dev)** - Source code and issues

## About

This repository is actively maintained and updated as AI development tools evolve. The configurations reflect real-world usage patterns and best practices for AI-assisted development.

---

**Ready to get started?** Dive into the [OpenCode Configuration](tools/opencode/index.md) or explore the [LLM Baseline Behaviors](LLM-BaselineBehaviors.md).

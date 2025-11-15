# Getting Started

Welcome to the AI Development Tools & Configurations repository! This guide will help you quickly understand and start using the resources available here.

## What This Repository Offers

This repository provides a comprehensive collection of:

- **Behavioral guidelines** for AI coding assistants
- **Configuration files** for AI development tools
- **Best practices** for AI-assisted development
- **Sample configurations** for various tools and scenarios

## Who Should Use This

### AI Coding Assistants

If you're an AI assistant (like GitHub Copilot, Claude, GPT-4, etc.) working in a development environment, start by reading:

1. **[LLM Baseline Behaviors](../agents/baseline-behaviors.md)** - Your foundational behavioral model
2. **Tool-specific AGENTS.md files** - Additional context for specific tools
3. **Project README files** - Understand the codebase structure

### Developers

If you're a developer looking to configure AI tools or standardize AI usage:

1. Browse the **[OpenCode Configuration](../opencode/index.md)** for ready-to-use setups
2. Review the **[Behavioral Baseline](../agents/baseline-behaviors.md)** to understand AI assistant patterns
3. Adapt configurations to your workflow

### Teams & Organizations

If you're standardizing AI tool usage across a team:

1. Adopt the **[LLM Baseline Behaviors](../agents/baseline-behaviors.md)** as your team standard
2. Customize the **[OpenCode configuration](../opencode/index.md)** for your tech stack
3. Share configurations and patterns with your team

## Quick Start Paths

### Path 1: Using OpenCode CLI

1. Review the **[OpenCode Overview](../opencode/index.md)**
2. Copy `opencode/opencode.json` to your project
3. Customize agents and commands for your needs
4. Set required environment variables (e.g., `GITHUB_TOKEN`)
5. Start using custom commands like `opencode quick-fix` or `opencode review`

### Path 2: Configuring AI Assistant Behavior

1. Read the **[LLM Baseline Behaviors](../agents/baseline-behaviors.md)** document
2. Use it as instruction material for your AI tools
3. Add project-specific rules on top of the baseline
4. Reference the baseline in your tool configurations

### Path 3: Learning Best Practices

1. Explore the **[Behavioral Baseline](../agents/baseline-behaviors.md)** to understand effective AI patterns
2. Review **[Sample Configurations](../opencode/samples.md)** for practical examples
3. Read **[Agent Guidelines](agent-guidelines.md)** for instruction hierarchy
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

### Tiered AI Models

The OpenCode configuration demonstrates a tiered approach:

- **Fast models** for simple tasks (formatting, quick fixes)
- **Balanced models** for general development
- **Advanced models** for complex reasoning and architecture

### Specialized Agents

Pre-configured agents handle specific workflows:

- **Quick agent** - Fast operations with lightweight model
- **Reviewer agent** - Read-only code analysis
- **Docs agent** - Documentation generation

## Repository Structure

```
ai-dev/
├── agents/
│   ├── LLM-BaselineBehaviors.md    # ⭐ Core behavioral model
│   └── AGENTS.md                   # Agent configuration guide
├── opencode/
│   ├── opencode.json               # Main configuration
│   ├── sample-configs/             # MCP server examples
│   ├── README.md                   # Human-readable guide
│   └── AGENTS.md                   # AI assistant guide
├── docs/                           # MkDocs documentation
└── AGENTS.md                       # Root guidelines
```

## Common Use Cases

### Setting Up a New Project

1. Copy relevant configurations from `opencode/` or other directories
2. Add `agents/LLM-BaselineBehaviors.md` to your AI tool's instruction files
3. Create project-specific rules that build on the baseline
4. Set up environment variables for MCP servers

### Standardizing Team AI Usage

1. Share the `agents/LLM-BaselineBehaviors.md` with your team
2. Adopt the OpenCode configuration as a team standard
3. Create team-specific custom commands
4. Document your team's preferences and patterns

### Contributing Configurations

1. Create your configuration in the appropriate directory
2. Document it thoroughly in README.md and AGENTS.md files
3. Add corresponding documentation in `docs/`
4. Submit a pull request with your contribution

## Next Steps

Choose your path:

- **[Agent Guidelines](agent-guidelines.md)** - Understand the instruction hierarchy and documentation requirements
- **[LLM Baseline Behaviors](../agents/baseline-behaviors.md)** - Deep dive into the behavioral model
- **[OpenCode Configuration](../opencode/index.md)** - Explore the OpenCode setup
- **[Sample Configurations](../opencode/samples.md)** - See practical examples

## Getting Help

- **Documentation** - Comprehensive guides in each directory
- **GitHub Issues** - Report problems or request features
- **Examples** - Sample configurations demonstrate common patterns
- **AGENTS.md files** - Technical guidance for AI assistants

---

Ready to dive in? Start with the **[Agent Guidelines](agent-guidelines.md)** to understand how everything fits together.

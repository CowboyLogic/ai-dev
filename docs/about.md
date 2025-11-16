# About AI Dev

## What is AI Dev?

AI Dev is a curated repository of configurations, behavioral guidelines, and best practices for working with AI-powered development tools. It provides a centralized location for:

- **Behavioral baselines** that define consistent AI assistant behavior
- **OpenCode CLI configurations** with specialized agents and MCP server integrations
- **Documentation and examples** to accelerate AI-assisted development
- **Community-contributed patterns** for effective AI tool usage

## Purpose

The repository serves developers who want to:

1. **Standardize AI behavior** across different tools and models
2. **Share effective configurations** with teams and the community
3. **Learn best practices** for AI-assisted development
4. **Customize AI assistants** for specific workflows and preferences
5. **Integrate advanced capabilities** through Model Context Protocol (MCP) servers

## Philosophy

### Conversational Clarity

AI assistants should communicate with clarity and thoroughness. Rather than favoring brevity, explanations should ensure full understanding while remaining focused and relevant.

**Core Principles:**
- Explain solutions clearly so users understand the approach
- Provide context for recommendations and decisions
- Balance detail with readability
- Demonstrate with examples when helpful

### Action-Oriented Behavior

AI assistants should act rather than just suggest. When given a task:
- Implement solutions using available tools
- Research missing information rather than guessing
- Continue working until completion
- Maintain momentum while preserving quality

### Documentation-First

Configuration and code changes are only complete when documentation is synchronized:
- All configurations must be documented
- Changes require updating related documentation
- Examples should reflect actual implementations
- Cross-references must stay current

## What's Included

### Behavioral Baselines

**[`agents/LLM-BaselineBehaviors.md`](agents/baseline-behaviors.md)** - The authoritative behavioral model for AI assistants working in this repository. Covers:

- Communication style and tone
- Action-oriented decision making
- Tool usage efficiency
- Code quality standards
- Problem-solving approaches

All AI assistants should follow this baseline as their foundation.

### OpenCode CLI Configuration

**[`opencode/`](tools/opencode/index.md)** directory contains:

- **Main configuration** (`opencode.json`) with tiered models and specialized agents
- **Sample MCP server configs** for Docker-based and NPX-based integrations
- **Custom commands** for common development tasks
- **Documentation and guides** for setup and customization

### Documentation Site

This MkDocs-powered site provides:

- **Getting Started guides** for new users
- **Agent configuration guides** with instruction hierarchy
- **Behavioral baseline documentation** for understanding AI assistant behavior
- **OpenCode configuration reference** with examples and samples
- **Contributing guidelines** for sharing improvements

## Use Cases

### Individual Developers

- Customize AI assistants to match your workflow
- Use consistent behavior across different tools
- Leverage MCP servers for enhanced capabilities
- Share configurations across projects

### Development Teams

- Standardize AI behavior team-wide
- Share effective configurations and patterns
- Document AI usage guidelines
- Collaborate on improvements

### Organizations

- Establish organizational AI standards
- Integrate internal tools via MCP servers
- Create custom specialized agents
- Train teams on effective AI usage

## Technology Stack

**AI Models:**
- Claude Sonnet 4.5 (primary balanced model)
- Grok 2 Mini (fast iteration model)
- GPT-4o, GPT-5, Gemini 2.5 Pro (via GitHub Copilot)

**Tools:**
- OpenCode CLI - AI-assisted development with tiered models
- MkDocs with Material theme - Documentation site
- Model Context Protocol (MCP) - Tool and service integration

**Standards:**
- GitHub Flavored Markdown (GFM) - All documentation
- JSON with comments - Configuration files
- Environment variables - Secret management

## Repository Structure

```
ai-dev/
├── agents/                           # Agent configurations
│   ├── LLM-BaselineBehaviors.md     # Authoritative behavioral model
│   └── AGENTS.md                     # Agent configuration guide
├── opencode/                         # OpenCode CLI configurations
│   ├── opencode.json                # Main configuration
│   ├── modular-config/              # Modular subagent configuration
│   ├── README.md                    # Human-readable guide
│   └── AGENTS.md                    # AI assistant guide
├── mcp/                              # MCP server configurations
│   ├── sample-configs/              # Example MCP server configs
│   └── README.md                    # MCP overview
├── docs/                             # MkDocs documentation source
│   ├── index.md                     # Main landing page
│   ├── getting-started/             # Getting started guides
│   ├── agents/                      # Behavioral baseline docs
│   ├── tools/                       # Tool-specific documentation
│   │   └── opencode/                # OpenCode documentation
│   ├── contributing.md              # Contribution guidelines
│   └── about.md                     # This page
├── mkdocs.yml                        # MkDocs configuration
├── AGENTS.md                         # Repository-wide agent guidelines
└── README.md                         # Repository overview
```

## Maintenance and Updates

**Primary Maintainer:** Repository owner (see GitHub profile)

**Update Frequency:**
- Configurations updated as tools evolve
- Behavioral baselines refined based on usage
- Documentation kept synchronized with changes
- Community contributions reviewed regularly

**Versioning:**
- Configuration files include schema references
- Breaking changes documented in commit messages
- Sample configurations maintained for current tool versions

## Contributing

We welcome contributions! Please see our **[Contributing Guide](contributing.md)** for:

- How to submit configurations
- Documentation standards
- Pull request process
- Style guidelines

**All contributions must:**
- Follow GitHub Flavored Markdown for documentation
- Use environment variables for secrets
- Include comprehensive documentation
- Update all related files

## Community

**Getting Help:**
- File an issue for bugs or questions
- Start a discussion for ideas and proposals
- Submit PRs for improvements

**Sharing Success:**
- Share your configurations
- Document your workflows
- Contribute improvements
- Help others learn

## License

This repository is provided as-is for community use. Check the repository LICENSE file for specific terms.

## Acknowledgments

This repository builds on:
- **OpenCode CLI** - AI-assisted development tool
- **Model Context Protocol** - Tool integration standard
- **MkDocs Material** - Documentation framework
- **Community Contributors** - Sharing configurations and improvements

## Contact

- **Repository:** [GitHub Repository URL]
- **Issues:** [GitHub Issues URL]
- **Discussions:** [GitHub Discussions URL]

---

**Ready to get started?** Visit the **[Getting Started Guide](getting-started/overview.md)** or explore **[OpenCode Configuration](tools/opencode/index.md)**.

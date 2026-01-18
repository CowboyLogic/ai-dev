# About AI Dev

## What is AI Dev?

AI Dev provides **practical configurations and working examples** for AI-powered development tools. This repository focuses on concrete, usable implementations rather than duplicating vendor documentation.

**What's here:**
- Behavioral guidelines for consistent AI assistant behavior
- Working configurations for OpenCode CLI and VS Code
- MCP server integration examples
- Ready-to-use agent definitions

**Official tool documentation:**
- [GitHub Copilot](https://docs.github.com/en/copilot)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [OpenCode AI](https://opencode.ai/docs)

## Purpose

This repository helps developers:

1. **Apply consistent patterns** across AI tools and models
2. **Share working configurations** with teams
3. **Integrate advanced capabilities** through MCP servers
4. **Start quickly** with copy-paste examples

## Philosophy

This repository emphasizes **examples over explanations**. We provide working configurations with links to authoritative documentation rather than rewriting vendor guides.

**Core approach:**
- **Action-oriented** - Implement changes, don't just suggest
- **Example-first** - Show concrete implementations
- **Link to authority** - Reference official docs for concepts
- **Documentation-aligned** - Keep examples synchronized with actual configs

## What's Included

### Behavioral Baselines

**[`agents/LLM-BaselineBehaviors.md`](LLM-BaselineBehaviors.md)** - The authoritative behavioral model for AI assistants working in this repository. Covers:

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

**AI Integration:**
- [GitHub Copilot](https://github.com/features/copilot) - AI pair programmer
- [OpenCode CLI](https://opencode.ai) - AI-assisted development tool
- [Model Context Protocol](https://modelcontextprotocol.io) - Tool integration standard

**Documentation:**
- [MkDocs](https://www.mkdocs.org) with [Material theme](https://squidfunk.github.io/mkdocs-material/)
- GitHub Flavored Markdown

## Repository Structure

```
ai-dev/
├── agents/                           # Agent configurations
│   ├── LLM-BaselineBehaviors.md     # Authoritative behavioral model
│   └── AGENTS.md                     # Agent configuration guide
├── opencode/                         # OpenCode CLI configurations
│   ├── opencode.json                # Main configuration
│   ├── agent-subagent-config/      # Modular subagent configuration
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

Contributions welcome! See our **[Contributing Guide](contributing.md)** and GitHub's [Contributing to Projects](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) guide.

**Contribute:**
- Working configurations and examples
- Integration patterns  
- Documentation improvements

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

**Ready to get started?** Explore the **[OpenCode Configuration](tools/opencode/index.md)** or dive into the **[LLM Baseline Behaviors](LLM-BaselineBehaviors.md)**.

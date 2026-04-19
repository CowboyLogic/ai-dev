# About AI Dev

## What is AI Dev?

AI Dev provides **practical configurations and working examples** for AI-powered development tools. This repository focuses on concrete, usable implementations rather than duplicating vendor documentation.

**What's here:**

- Behavioral guidelines for consistent AI assistant behavior
- Working configurations for Claude Code, OpenCode CLI, and VS Code
- MCP server integration examples
- Ready-to-use agent definitions

**Official tool documentation:**

- [Claude Code](https://claude.ai/code)
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

### Agents

**[Agents](agents/index.md)** — Specialized AI agent definitions for various development tasks:

- API design and .NET development
- Architecture and cloud platforms (GCP, AWS, Azure)
- Database and performance optimization
- Security and testing
- Documentation and web research

### Skills

**[Skills](skills/index.md)** — Domain-specific instruction sets teaching AI agents specialized capabilities:

- Programming languages and frameworks (.NET, React, Node.js, PostgreSQL)
- Documentation (Google Style Docs)
- DevOps and cloud tools (Docker, Terraform, AWS, Azure, GCP)
- Git workflows and Copilot customization
- MkDocs site management

### Tools

**[Tools](tools/index.md)** — Configuration and integration guides:

- **[Claude Code CLI](tools/claudecode/claudecode-vertexai.md)** - Enterprise VertexAI configuration for Google Cloud Platform
- **[OpenCode CLI](tools/opencode/index.md)** - Multi-agent configuration, custom commands, MCP integrations
- **[Visual Studio Code](tools/vscode/README.md)** - GitHub Copilot integration, agent examples, best practices

### MCP Servers

**[MCP Servers](mcp/overview.md)** — Working examples for Model Context Protocol server integrations.

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

- [Claude Code](https://claude.ai/code) - Anthropic's official CLI for Claude
- [GitHub Copilot](https://github.com/features/copilot) - AI pair programmer
- [OpenCode CLI](https://opencode.ai) - AI-assisted development tool
- [Model Context Protocol](https://modelcontextprotocol.io) - Tool integration standard

**Documentation:**

- [MkDocs](https://www.mkdocs.org) with [Material theme](https://squidfunk.github.io/mkdocs-material/)
- GitHub Flavored Markdown

## Repository Structure

```text
ai-dev/
├── docs/                             # MkDocs documentation source
│   ├── index.md                     # Home page
│   ├── about.md                     # This page
│   ├── contributing.md              # Contributing guidelines
│   ├── agents/                      # Agent configuration documentation
│   ├── skills/                      # Domain-specific instruction sets
│   ├── tools/                       # Tool configuration guides
│   └── mcp/                         # MCP server documentation
├── AGENTS.md                         # Repository-wide agent guidelines
├── README.md                         # Repository overview
├── mkdocs.yml                        # MkDocs configuration
├── agents/                           # Agent configuration files
├── tools/                            # Tool-specific configurations
│   ├── opencode/                    # OpenCode CLI configurations
│   └── vscode/                      # VS Code integration guides
├── mcp/                              # MCP server examples
└── site/                             # Generated documentation (build output)
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

- **Claude Code** - Anthropic's official CLI for Claude
- **OpenCode CLI** - AI-assisted development tool
- **Model Context Protocol** - Tool integration standard
- **MkDocs Material** - Documentation framework
- **Community Contributors** - Sharing configurations and improvements

## Contact

- **Repository:** [GitHub Repository URL]
- **Issues:** [GitHub Issues URL]
- **Discussions:** [GitHub Discussions URL]

---

**Ready to get started?** Explore the **[Claude Code VertexAI Configuration](tools/claudecode/claudecode-vertexai.md)** or the **[OpenCode Configuration](tools/opencode/index.md)**.

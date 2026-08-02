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

**[Agents](agents/index.md)** — Two multi-agent topologies for AI-assisted development:

- **Lane Topology** — classifies each request into a lane and sizes process to match, from a mechanical edit to a full plan-build-verify lifecycle (OpenCode-native, GitHub Copilot mirror)
- **Matrix Topology** — a fixed nine-stage lifecycle for production-quality development work (OpenCode-native, with Claude Code and GitHub Copilot mirrors)

### Skills

**[Skills](skills/index.md)** — Domain-specific instruction sets teaching AI agents specialized capabilities:

- Agent creation for GitHub Copilot and OpenCode CLI
- Client configuration for Claude Code, Copilot CLI, and OpenCode
- Documentation (Google Style Docs, Markdownlint validation, MkDocs site management)
- Docker image management
- Git commit messages, Copilot instructions, and Copilot prompts
- High-fidelity XML context scaffolding for agent orchestration

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
│   ├── agents/                      # Agent catalog pages
│   ├── skills/                      # Skills catalog page
│   ├── tools/                       # Tool configuration guides
│   └── mcp/                         # MCP server documentation
├── agents/                           # Installable agent definitions
│   ├── lane-topology/               # Lane Topology multi-agent system
│   └── matrix-topology/             # Matrix Topology multi-agent system
├── skills/                           # Installable skill definitions
│   └── <skill-name>/                # Each skill: SKILL.md + README + references/
├── harness/                           # Client harness configs (OpenCode symlink targets)
├── AGENTS.md                         # Repository-wide agent guidelines
├── README.md                         # Repository overview
├── mkdocs.yml                        # MkDocs configuration
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

This repository is provided as-is for community use. No LICENSE file is currently published at the repository root; contact the maintainer with licensing questions.

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

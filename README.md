# AI Development Tools & Configurations

Practical configurations and working examples for AI-powered development tools. Copy, adapt, and integrate.

> [!IMPORTANT]
> This repository is a living collection of AI development patterns, tools, and insights.
> It evolves with the AI landscape — contributions welcome!

## What's Here

**[📚 Full Documentation Site](https://cowboylogic.github.io/ai-dev)**

- **[Agents](docs/agents/README.md)** — Specialized AI agent definitions (API, architecture, security, testing, DevOps, cloud, database, documentation)
- **[Context & Baselines](docs/context/index.md)** — Behavioral baselines and instruction files governing AI assistant behavior
- **[Skills](docs/skills/README.md)** — Domain-specific instruction sets teaching AI agents specialized tasks
- **[Tools](docs/tools/index.md)** — Claude Code, OpenCode CLI, and VS Code configurations with examples
- **[MCP Servers](docs/mcp/overview.md)** — Model Context Protocol integration examples

## Quick Start

### AI Assistants

1. **Load directives**: Read [AGENTS.md](AGENTS.md) which points to [`.agents/manifest.xml`](.agents/manifest.xml)
2. **Baseline behaviors**: Review [LLM Baseline Behaviors](docs/context/LLM-BaselineBehaviors.md)
3. **Priority hierarchy**: User directives → Repository rules → Tool guidelines → Baseline behaviors

### Developers

**Claude Code:**

- [VertexAI Configuration](docs/tools/claudecode/claudecode-vertexai.md) — Configure Claude Code to use Google Cloud VertexAI

**OpenCode CLI:**

- [Overview](docs/tools/opencode/index.md) | [Configuration Guide](docs/tools/opencode/configuration.md) | [Samples](docs/tools/opencode/samples.md)

**VS Code + Copilot:**

- [Agent Guide](docs/tools/vscode/README.md) | [Quick Start](docs/tools/vscode/quick-start.md) | [Examples](docs/tools/vscode/agent-examples.md)

**MCP Servers:**

- [Overview](docs/mcp/overview.md) | [Configuration](docs/mcp/configuration.md) | [Samples](docs/mcp/sample-configs/)

## Repository Structure

```
ai-dev/
├── .agents/                    # XML directive system (high-fidelity context)
│   ├── AGENTS.xml              # Primary repository directives
│   ├── manifest.xml            # Agent configuration loader
│   └── ARCHITECTURE.xml        # Technical stack and patterns
├── docs/                       # MkDocs documentation source
│   ├── agents/                 # Agent configuration guides
│   ├── context/                # Behavioral baselines (Markdown + XML)
│   ├── skills/                 # Domain-specific instruction sets
│   ├── tools/                  # OpenCode & VS Code guides
│   └── mcp/                    # MCP server documentation
├── agent-output/               # Temporary agent output (gitignored)
├── AGENTS.md                   # Human-readable directive overview
├── README.md                   # This file
└── mkdocs.yml                  # Documentation site configuration
```

## Key Features

**High-Fidelity XML Context System** — Structured directives optimized for LLM parsing with `.agents/` XML modules ([learn more](docs/context/high-fidelity-context.md))

**Behavioral Baselines** — Consistent AI behavior patterns across tools and models ([LLM-BaselineBehaviors.md](docs/context/LLM-BaselineBehaviors.md))

**Agent Skills Framework** — Reusable instruction sets for domain-specific tasks ([Skills Overview](docs/skills/README.md))

**Multi-Tool Configurations** — Claude Code, OpenCode CLI, VS Code/Copilot, and MCP server integrations

## Contributing

Contributions welcome! See [Contributing Guide](docs/contributing.md) for:

- Configuration guidelines
- Documentation standards
- Pull request process
- Testing requirements

**Quick checklist:**

- Test your configurations
- Follow GitHub Flavored Markdown formatting
- Update related documentation
- No hardcoded secrets (use environment variables)

## Official Documentation

This repository provides configurations, not vendor documentation. For comprehensive tool docs:

- [Claude Code](https://claude.ai/code) — Anthropic's official CLI for Claude
- [GitHub Copilot](https://docs.github.com/en/copilot) — AI pair programmer
- [Model Context Protocol](https://modelcontextprotocol.io) — Tool integration standard
- [OpenCode CLI](https://opencode.ai/docs) — AI development CLI
- [VS Code](https://code.visualstudio.com/docs) — Code editor

## License

See [LICENSE](LICENSE) file for terms.

---

**[View Full Documentation →](https://cowboylogic.github.io/ai-dev)** | **[Contributing Guide →](docs/contributing.md)** | **[About This Project →](docs/about.md)**

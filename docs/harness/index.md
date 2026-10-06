# Harness

This section documents configurations and integration patterns for the harnesses that run AI agents: Claude Code, OpenCode, and VS Code with GitHub Copilot. Each harness has its own subsection with setup guides, examples, and best practices.

## Available Harnesses

### Claude Code CLI

Anthropic's official CLI for Claude, providing terminal-based AI development workflows with model flexibility and enterprise integration options.

- [Overview](claudecode/index.md) — The skills and agent topology this repository provides for Claude Code
- [Vertex AI](claudecode/claudecode-vertexai.md) — Run Claude Code against Claude models served through Google Cloud

### OpenCode CLI

A terminal-based AI development tool supporting multi-model configurations, specialized agents, and MCP server integrations.

- [Overview](opencode/index.md) — The sample configurations and how to install them
- [Configuration Guide](opencode/configuration.md) — Complete setup and customization

### Visual Studio Code

Integration patterns for GitHub Copilot in VS Code, including markdown-based agents and programmatic subagents.

- [Overview](vscode/index.md) — Quick start guide for first agent setup
- [Quick Start](vscode/quick-start.md) — Get running in 5 minutes
- [Markdown-Based Agents](vscode/markdown-agents.md) — Declarative configuration approach
- [Agent Examples](vscode/agent-examples.md) — Ready-to-use configurations
- [Best Practices](vscode/best-practices.md) — Optimization patterns and collaboration patterns
- [Programmatic SubAgents](vscode/subagent-tool.md) — Agents that delegate to other agents
- [Troubleshooting](vscode/troubleshooting.md) — When an agent does not show up or behave

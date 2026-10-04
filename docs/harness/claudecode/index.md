# Claude Code

[Claude Code](https://code.claude.com/docs) is Anthropic's terminal-based coding agent. This repository
ships skills and an agent topology for it. Anthropic's own documentation is the reference for how Claude
Code works, so these pages cover only what this repository adds.

## Skills for Claude Code

| Skill | Use it to |
|---|---|
| [Claude Code Settings Manager](../../skills/client-config-claudecode.md) | Configure `settings.json`, permissions, hooks, MCP servers, models, and plugins |
| [Claude Code Agent Creator](../../skills/agent-creator-claudecode.md) | Write and troubleshoot custom subagents in `.claude/agents/` |
| [Copilot Worker](../../skills/copilot-worker.md) | Hand bounded research, review, or implementation work to GitHub Copilot from a Claude Code session |

The [skills catalog](../../skills/index.md) lists every skill, including the ones that are not specific to
Claude Code.

## Multi-agent topology

The [Matrix Topology](../../agents/matrix-topology.md) has a Claude Code mirror. It keeps every agent
body from the canonical OpenCode definitions and translates the frontmatter to Claude Code tools and model
aliases. The mirror is in
[`agents/matrix-topology/claude/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology/claude).

## Provider setup

- [Claude Code with Google Vertex AI](claudecode-vertexai.md): run Claude Code against Claude models served through a Google Cloud project

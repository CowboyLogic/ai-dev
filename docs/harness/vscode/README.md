# Visual Studio Code

Custom agents for GitHub Copilot in VS Code: how to write them, ten ready-made examples, and how to
make them delegate to each other.

A custom agent is a Markdown file with YAML frontmatter in `.github/agents/`. The frontmatter sets which
tools the agent may use, and the body is its instructions. For the complete feature set, see
[Custom agents in VS Code](https://code.visualstudio.com/docs/agent-customization/custom-agents) and the
[GitHub Copilot documentation](https://docs.github.com/en/copilot).

## In this section

| Page | Read it to |
|---|---|
| [Quick Start](quick-start.md) | Create and use your first agent |
| [Custom Agent Files](markdown-agents.md) | Learn the file locations, frontmatter, tools, and handoffs |
| [Subagents](subagent-tool.md) | Have an agent delegate to other agents |
| [Agent Examples](agent-examples.md) | Install ready-made agents and see what each demonstrates |
| [Best Practices](best-practices.md) | Design agents that stay narrow and safe |
| [Troubleshooting](troubleshooting.md) | Fix an agent that does not appear or behave |

## Related

- [Copilot Agent Creator skill](../../skills/agent-creator-copilot.md): a skill that writes and checks agent files across VS Code, the Copilot CLI, and the cloud agent
- [Agents overview](../../agents/index.md): multi-agent topologies, with GitHub Copilot mirrors

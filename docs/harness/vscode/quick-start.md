# Quick Start

Create a custom agent in VS Code and use it.

## Prerequisites

- VS Code with GitHub Copilot enabled
- A workspace folder to put the agent in

## Create your first agent

1. Create the folder `.github/agents/` in your workspace.
2. Create `.github/agents/reviewer.agent.md`:

   ```markdown
   ---
   description: Reviews code for bugs and security problems without changing it
   tools: ["read", "search"]
   ---

   You are a code reviewer. Read the code you are asked about and report bugs,
   security problems, and missing tests. Cite the file and line for each finding.
   Never edit files.
   ```

3. Open the Chat view and choose **reviewer** from the **Agent** dropdown.
4. Ask it something: `Review src/auth/login.ts`.

The agent can only read and search, because those are the only tools it lists. To see the effect, remove the `tools` line and the agent gets every tool.

You can also generate an agent for you: run **Chat: New Custom Agent**, or type `/create-agent` in chat and describe the role.

## Install a ready-made agent

The repository's [example agents](agent-examples.md) install into your project with the GitHub CLI:

```bash
gh copilot agent install CowboyLogic/ai-dev/agents/code-reviewer.agent.md
```

Or copy a file from
[`agents/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents)
into `.github/agents/` by hand.

## Share it

Commit `.github/agents/` and everyone who opens the workspace gets the agents. To use an agent in every workspace, put it in `~/.copilot/agents/` instead.

## Next steps

- [Custom Agent Files](markdown-agents.md): locations, frontmatter, and tools
- [Agent Examples](agent-examples.md): ten ready-made agents
- [Subagents](subagent-tool.md): agents that delegate to other agents
- [Troubleshooting](troubleshooting.md): when an agent does not show up or behave

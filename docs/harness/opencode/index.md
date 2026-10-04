# OpenCode CLI Configuration

Sample configurations for the OpenCode CLI, and a guide to the configuration format they use.

[OpenCode](https://opencode.ai/docs) combines multiple AI models, custom commands, and specialized
agents in a terminal workflow. The samples show two ways to set that up.

> [!NOTE]
> The samples use the native **OpenCode V2** format: `agents` (not `agent`), `commands` (not
> `command`), ordered `permissions` rules (not `tools`/`permission` maps), and MCP servers under
> `mcp.servers`. V2 loads project guidance from `AGENTS.md` only. The
> [Configuration Guide](configuration.md) is the full reference.

## The samples

The samples live in [`harness/opencode-samples/`](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode-samples)
in the repository, not on this site.

| Sample | Directory | Best for |
|---|---|---|
| **Standard** | [`standard-config/`](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode-samples/standard-config) | A few agents, commands, permissions, and an MCP server in one `opencode.json` |
| **Modular** | [`agent-subagent-config/`](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode-samples/agent-subagent-config) | Many specialized subagents, one Markdown file each, plus `plan` and `build` primary agents |
| **MCP servers** | [`mcp/`](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode-samples/mcp) | Docker and npx MCP server entries to copy into your config. See [MCP Servers](../../mcp/index.md) |

The modular sample's subagents are `api`, `architect`, `cloud`, `data`, `database`, `devops`,
`documentation`, `performance`, `research`, `reviewer`, `security`, `testing`, and `uxui`. Each model
and permission set is in the agent's own file in
[`agents/`](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode-samples/agent-subagent-config/agents).

For a full multi-agent system built on the same pattern, see the
[Matrix](../../agents/matrix-topology.md) and [Lane](../../agents/lane-topology.md) topologies.

## Install

Run these from a clone of this repository. Both samples use the built-in GitHub Copilot
provider, so sign in once with `/connect` in the OpenCode interface.

```bash
# Standard: one file in your project
cp harness/opencode-samples/standard-config/opencode.json ~/your-project/opencode.json

# Or modular: config and plan prompt at the project root, subagents in .opencode/agents/
cp harness/opencode-samples/agent-subagent-config/opencode.json ~/your-project/
cp -r harness/opencode-samples/agent-subagent-config/prompts ~/your-project/
mkdir -p ~/your-project/.opencode/agents
cp harness/opencode-samples/agent-subagent-config/agents/*.md ~/your-project/.opencode/agents/
```

To apply the standard sample to every project, copy it to `~/.config/opencode/opencode.json`
instead. The modular sample's `plan` agent loads `{file:./prompts/plan.txt}` relative to
`opencode.json`, so keep `prompts/` beside it.

The standard sample's GitHub MCP server reads `{env:GITHUB_TOKEN}`, so set that variable before
starting OpenCode:

```bash
# Linux and macOS
export GITHUB_TOKEN="your-github-token"
```

```powershell
# Windows PowerShell
$env:GITHUB_TOKEN = "your-github-token"
```

Then start `opencode` in your project. The standard sample defines `/quick-fix`, `/review`,
`/document`, `/build`, `/test`, and `/deploy`.

## Where to go next

- [Configuration Guide](configuration.md): agents, commands, permissions, models, MCP, and migrating from V1
- [MCP Servers](../../mcp/index.md): the MCP samples and how to use them
- [OpenCode V2 documentation](https://opencode.ai/v2/docs/)
- [OpenCode Configuration Manager skill](../../skills/client-config-opencode.md): V1 and V2 configuration reference

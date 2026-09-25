# Custom Agents and Plugins Reference

## Custom agents

A custom agent is a Markdown file with YAML frontmatter. The filename minus `.agent.md` (or `.md`)
is the agent ID. When Copilot delegates to an agent it runs as a subagent with its own context
window.

### Locations

| Scope | Location |
|-------|----------|
| Project | `.github/agents/` or `.claude/agents/` — walked from cwd up to the Git root, all levels loaded |
| User | `~/.copilot/agents/` |
| Plugin | `<plugin>/agents/` (lowest) |
| Added root | `.github/agents/` under `--add-dir` / `/add-dir` directories (trusted) |
| Remote | Org/enterprise agents (skip with `customAgents.defaultLocalOnly: true`) |

At the same level `.github/agents/` beats `.claude/agents/`; the deepest `.github/agents/` wins.

> [!WARNING]
> The upstream docs conflict on user vs project precedence. The command reference and
> configuration-directory reference say **project beats user**; the "create custom agents" how-to
> and the plugin-reference loading diagram say the **user** (`~/.copilot/agents/`) copy wins. Avoid
> same-named agents in both places.

Create interactively with `/agent` → **Create new agent** (Project or User), then restart the CLI.

### Frontmatter

```markdown
---
name: security-auditor
description: Reviews code for security issues. Use for security reviews or "seccheck".
tools: ["view", "grep", "glob", "bash"]
model: claude-sonnet-4.6
include-custom-instructions: true
---

You are a security expert. Check code for exposed secrets, XSS, SQL injection, ...
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Shown in the agent list and `task` tool; drives inference |
| `name` | string | No | Display name (defaults to filename) |
| `tools` | string[] | No | Default `["*"]`; any `*` in the list grants all tools |
| `model` | string | No | Model for this agent (inherits when unset; ignored when the session model is Auto) |
| `models` | string[] | No | Priority list; first model the plan allows; overrides `model` |
| `modelPolicy` | `"preferred"` \| `"required"` | No | `required` locks dispatch to authored models |
| `reasoningEffort` | string | No | e.g. `"low"`, `"medium"`, `"high"` |
| `include-custom-instructions` | boolean | No | Give the subagent repository instruction files (default `false`) |
| `mcp-servers` | object | No | Agent-scoped MCP servers (same schema as `mcp-config.json`) |
| `infer` | boolean | No | Allow auto-delegation (default `true`) — see note |
| `sidekick` | object | No | Run automatically in the background (see below) |

The cross-product custom-agents reference also lists `target` (`vscode` or `github-copilot`),
`disable-model-invocation`, `user-invocable`, and `metadata`, and marks `infer` as **retired** in
favor of `disable-model-invocation` / `user-invocable`. The CLI command reference still documents
`infer`. Prefer `disable-model-invocation: true` for new agents; verify on your CLI version.

Model/effort precedence (highest first): explicit per-call value → `subagents.agents` override in
`settings.json` → agent frontmatter → parent session.

### Using agents

```bash
copilot --agent security-auditor --prompt "Check src/app/validator.go"
```

Or `/agent` in a session, an explicit prompt ("Use the security-auditor agent on ..."), or
inference from `description`.

### Subagent settings (`~/.copilot/settings.json`)

```json
{
  "subagents": {
    "agents": {
      "security-auditor": { "model": "gpt-5.4", "modelPolicy": "preferred", "effortLevel": "high" }
    },
    "disabledSubagents": ["research"],
    "maxConcurrency": 16,
    "maxDepth": 10
  }
}
```

- `subagents.agents.<name>`: `model`, `modelPolicy`, `effortLevel`, `contextTier`
  (`"default"`, `"long_context"`, `"inherit"`); `"inherit"` uses the parent's value.
- `maxConcurrency` / `maxDepth` apply only to usage-based billing (caps `32` / `256`). Default
  concurrency by plan: Free/Education 2, Pro/Pro+ 4, Max 8, Business 16, Enterprise 32.
- Configure interactively with `/subagents` (alias `/agents`).

### Built-in agents

`code-review`, `explore`, `general-purpose`, `research`, `rubber-duck`, `security-review`, `task`.
All except `rubber-duck` can be disabled via `subagents.disabledSubagents`;
`builtInAgents.rubberDuck: false` disables rubber-duck.

### Sidekick agents

Add a `sidekick:` block to run an agent automatically on session events:

```yaml
sidekick:
  triggers:
    - session.context_changed
    - event: user.message
      limit: 1
  behavior: persistent   # or "restart" (default)
  maxSendsPerTurn: 2     # default 1
```

Trigger events: `user.message`, `session.context_changed`.

---

## Plugins

Plugins package agents, skills, hooks, MCP servers, LSP servers, and commands. Built-in
marketplaces: `copilot-plugins` and `awesome-copilot`.

### Commands

```bash
copilot plugin marketplace list
copilot plugin marketplace add OWNER/REPO        # or OWNER/REPO#ref, URL, local path
copilot plugin marketplace browse awesome-copilot
copilot plugin install database-data-management@awesome-copilot
copilot plugin list [--json]
copilot plugin update NAME | --all
copilot plugin enable NAME / disable NAME
copilot plugin uninstall NAME                    # aliases remove, rm
copilot plugin marketplace update [NAME]         # alias refresh
copilot plugin marketplace remove NAME [--force]
```

Install specs: `plugin@marketplace`, `OWNER/REPO`, `OWNER/REPO:PATH/TO/PLUGIN`, a Git URL, or a
local path. In a session use `/plugin` (dashboard) or `/plugin install|update|uninstall|list|marketplace ...`.
`--plugin-dir=DIR` loads a local plugin for one session. The old cross-kind flags
(`--kind`, `--scope`, `--mcp`, `--skill`) were removed — use `copilot mcp|skill|instruction|lsp`.

### Declarative plugins (settings)

```json
{
  "enabledPlugins": { "my-plugin@my-marketplace": true }
}
```

`enabledPlugins` keys are plugin specs; `true` enables (auto-installs), `false` disables.
`extraKnownMarketplaces` is keyed by marketplace name, and each entry requires a `source`
(`"directory"`, `"git"`, or `"github"`). The docs don't show the full entry shape (whether `source`
is a string or an object, and the repo/path/URL fields) — check `copilot help config` before
writing one.
`autoUpdate: true` is honored only from user or managed settings. First-party plugins auto-update
each session in trusted directories unless `autoUpdate: false` or `COPILOT_AUTO_UPDATE=false`.

### Storage

| Item | Path |
|------|------|
| Marketplace installs | `~/.copilot/installed-plugins/MARKETPLACE/PLUGIN-NAME/` |
| Direct installs | `~/.copilot/installed-plugins/_direct/SOURCE-ID/` |
| Plugin data | `~/.copilot/plugin-data/` |
| Marketplace cache | `~/Library/Caches/copilot/marketplaces/` (macOS), `~/.cache/copilot/marketplaces/` (Linux) |

### Precedence

- Agents and skills: first found wins — project and personal definitions beat plugin ones.
- MCP servers: last loaded wins — a plugin's server overrides a same-named user server;
  `--additional-mcp-config` overrides both.
- Built-in tools and agents can't be overridden.

### Plugin manifest (`plugin.json`)

Two formats:

- **Agent Plugins 1.0** — `plugin.json` at the plugin root with
  `"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"`. Fields: `name`
  (required; lowercase letters, digits, hyphens, periods; 1–64 chars), `version`, `description`,
  `author`, `homepage`, `repository`, `license`, `keywords`, `extensions`. Components live at fixed
  paths: `skills/<name>/SKILL.md`, root `mcp.json`, and Copilot-specific
  `com.github.copilot/agents/`, `commands/`, `rules/`, `hooks/hooks.json`, `lsp.json`.
- **Legacy** — manifest at `.plugin/plugin.json`, `plugin.json`, `.github/plugin/plugin.json`, or
  `.claude-plugin/plugin.json`. Required `name` (kebab-case, max 64). Optional metadata
  (`description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`,
  `category`, `tags`) and component paths `agents` (default `agents/`), `skills` (default
  `skills/`), `commands`, `hooks`, `extensions`, `mcpServers`, `lspServers`.

`${PLUGIN_ROOT}` expands in plugin MCP/LSP config (and in plugin-shipped agents' `mcp-servers`);
`${PLUGIN_DATA}` points at a persistent writable directory for Agent Plugins 1.0 MCP servers.

### Marketplace (`marketplace.json`)

Looked up at `marketplace.json`, `.plugin/marketplace.json`, `.github/plugin/marketplace.json`, or
`.claude-plugin/marketplace.json`.

```json
{
  "name": "my-marketplace",
  "owner": { "name": "Your Organization", "email": "plugins@example.com" },
  "metadata": { "description": "Curated plugins", "version": "1.0.0" },
  "plugins": [
    { "name": "security-checks", "description": "...", "version": "1.3.0", "source": "./plugins/security-checks" }
  ]
}
```

Plugin entry `source` may be a relative path or an object such as
`{ "source": "github", "repo": "owner/repo", "ref": "v1.0.0", "path": "plugins/x" }`; `github` and
`url` sources accept a full 40-character `sha` to pin a commit.

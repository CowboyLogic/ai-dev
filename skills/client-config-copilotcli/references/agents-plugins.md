# Custom Agents and Plugins Reference

## Custom agents

A custom agent is a Markdown file with YAML frontmatter. For user, project, and added-root agents
the agent ID is the file's path relative to the `agents` directory, minus `.agent.md` (or `.md`),
with directory separators replaced by `--` (`agents/team/reviewer.agent.md` → `team--reviewer`).
When Copilot delegates to an agent it runs as a subagent with its own context window.

### Locations

Priority order (first loaded wins when IDs match):

| Priority | Scope | Location |
|----------|-------|----------|
| 1 (highest) | User | `~/.copilot/agents/` |
| 2 | Project | `.github/agents/`, from cwd up to the Git root |
| 3 | Project | `.claude/agents/`, from cwd up to the Git root |
| 4 | Added root | `.github/agents/` under `--add-dir` / `/add-dir` / SDK `additionalDirectories` (a trust decision: loaded as trusted configuration) |
| 5 | Plugin | `<plugin>/agents/` |
| 6 (lowest) | Remote | Org/enterprise agents (skip with `customAgents.defaultLocalOnly: true`) |

Within a project row the deepest directory wins, and every project `.github/agents/` is loaded
before any `.claude/agents/`. The `name` field does not affect deduplication: agents with the same
`name` but different IDs both load, and `--agent` picks the first match on ID or `name` in priority
order.

**v1.0.97 release notes only:** discovery now finds all custom agents even when a repository
defines more than 100 or nests agent files deeply.

Create interactively with `/agent`, then press `N` to create a new agent (Project or
User), then restart the CLI. A custom agent can also be selected for the whole session, not only
delegated to as a subagent. **v1.0.99 release notes only:** custom agents that declare the
documented `search`, `web`, or `todo` tool aliases, or name `github-mcp-server/web_search`, now
receive the matching tools.

### Frontmatter

```markdown
---
name: security-auditor
description: Reviews code for security issues. Use for security reviews or "seccheck".
tools: ["view", "grep", "glob", "bash"]
model: claude-sonnet-5.5
include-custom-instructions: true
---

You are a security expert. Check code for exposed secrets, XSS, SQL injection, ...
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | Yes | Shown in the agent list and `task` tool; drives inference |
| `name` | string | No | Display name; also usable with `--agent` (defaults to the agent ID) |
| `tools` | string[] | No | Default `["*"]`; any `*` in the list grants all tools |
| `model` | string | No | Model for this agent (inherits when unset; ignored when the session model is Auto) |
| `models` | string[] | No | Priority list; first model the plan allows; overrides `model` |
| `modelPolicy` | `"preferred"` \| `"required"` | No | `required` locks dispatch to authored models |
| `reasoningEffort` | string | No | e.g. `"low"`, `"medium"`, `"high"` |
| `include-custom-instructions` | boolean | No | Give the subagent repository instruction files (default `false`) |
| `mcp-servers` | object | No | Agent-scoped MCP servers (same schema as `mcp-config.json`) |
| `hooks` | object | No | Agent-scoped hooks that run only while this agent is selected (CLI only; v1.0.97). Documented in the hooks reference, not in the command reference's frontmatter table — see `hooks.md` |
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
- `maxConcurrency` / `maxDepth` apply only to usage-based billing (caps `32` / `256`; ignored on
  other plans). Default depth `6`; default concurrency by plan: Free/Education 2, Pro/Pro+ 4,
  Max 8, Business 16, Enterprise and usage-based 32.
- Configure interactively with `/subagents` (alias `/agents`).

### Built-in agents

| Agent | Default model (per the command reference) |
|-------|-------------------------------------------|
| `code-review`, `general-purpose`, `security-review` | `claude-sonnet-4.6` |
| `explore` | `gpt-5.4-mini` |
| `research` | `claude-haiku-4.5` |
| `rubber-duck` | A complementary model |
| `task` | `gpt-5.6-luna` (falls back to `gpt-5.4-mini`, then `claude-haiku-4.5`) |

These defaults are as documented and may lag the model roster; confirm with `/subagents`.

- Turn built-ins on or off with `subagents.disabledSubagents` or the `/subagents` picker.
  Proactive rubber-duck consultation is `subagents.agents["rubber-duck"].autoInvoke` (default
  `false`).
- `code-review` and `security-review` perform the review themselves rather than delegating a full
  review to another review agent; `code-review` hands security-focused portions to `security-review`.
- Only the root agent can call `store_memory` / `vote_memory`; subagents keep read access through
  `read_memories`.
- `list_agents` and `write_agent` let agents coordinate. `list_agents` takes a `scope`
  (`siblings`, `children`, `all`) and `write_agent` takes `scope` `"siblings"` or `"children"` to
  broadcast; scoped messaging works only from a subagent in a session with shared sibling
  communication enabled, otherwise use explicit `agent_id` values.

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
**Release notes only:** v1.0.100 installs verified skills and plugins from GitHub install links
(`copilot plugin install "ghapp://air/install?..."`; the quoted URL is truncated in the notes), and
v1.0.102 lets plugin marketplaces use `git-subdir` sources and long plugin descriptions. Neither
is in the plugin reference, so the field layout of a `git-subdir` source is unverified.
`--plugin-dir=DIR` loads a local plugin for one session (v1.0.97 release notes: its skills and
custom agents now reach autocomplete and invocation). The old cross-kind flags
(`--kind`, `--scope`, `--mcp`, `--skill`) were removed — use `copilot mcp|skill|instruction|lsp`.

When HTTPS authentication fails for a remote marketplace or plugin fetch, the CLI retries once
with your signed-in GitHub token; if that also fails, run `/login` (plugin reference; v1.0.97
release notes).

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

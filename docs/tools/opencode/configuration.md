# OpenCode Configuration Guide

Practical guide to configuring the OpenCode CLI with the patterns and sample configurations
in this repository.

**Official documentation:** [OpenCode V2 docs](https://opencode.ai/v2/docs/) ·
[Migrate from V1](https://opencode.ai/v2/docs/migrate-v1/) ·
[V1 docs](https://opencode.ai/docs/)

> [!IMPORTANT]
> **Everything in this guide uses the native OpenCode V2 format.** V2 still reads V1
> configuration, and V1 and V2 fields may coexist at the top level of a file. Each
> individual agent, provider, command, or model entry must be entirely one format,
> because V2 does not infer mixed formats inside a single entry. Do not point an
> OpenCode V1 client at files converted to the native V2 shape.

One limitation affects editor validation:

> [!WARNING]
> There is no published V2 schema for `opencode.json` yet.
> `https://opencode.ai/config.json` still describes V1 and rejects unknown keys, so an
> editor using it may flag valid V2 fields such as `agents`, `permissions`, and
> `mcp.servers`. Keep the `$schema` line for the fields it does cover, and treat
> those particular warnings as expected.

## Where configuration lives

| What | Global | Project |
|---|---|---|
| Main config | `~/.config/opencode/opencode.json(c)` | `opencode.json(c)` or `.opencode/opencode.json(c)` |
| Markdown agents | `~/.config/opencode/agents/<id>.md` | `.opencode/agents/<id>.md` |
| Markdown commands | `~/.config/opencode/commands/<name>.md` | `.opencode/commands/<name>.md` |
| Skills | `~/.config/opencode/skills/<id>/SKILL.md` | `.opencode/skills/<id>/SKILL.md` |
| Instructions | `~/.config/opencode/AGENTS.md` | `AGENTS.md` (workspace up to project root) |
| Terminal client settings | `~/.config/opencode/cli.json` | *(global only)* |

OpenCode searches from the current directory up to the filesystem root. It merges
direct `opencode.json(c)` files from the farthest directory to the closest, then merges
files inside `.opencode/` directories in the same order. Every `.opencode/` config
therefore overrides every direct config. Settings that do not conflict are kept.

Both `.json` and `.jsonc` accept comments and trailing commas.

## Configuration approaches

This repository ships two sample configurations under `docs/tools/opencode/`:

| Approach | Location | Best for |
|---|---|---|
| **Standard** | `standard-config/opencode.json` | A few agents, everything in one file |
| **Modular** | `agent-subagent-config/` | Many specialized agents, one Markdown file each |

For a real multi-agent system, see the topologies in `agents/`. They use the modular
pattern with a harness configuration, described in
[Topologies in this repository](#topologies-in-this-repository).

### Install the standard sample

```bash
cp docs/tools/opencode/standard-config/opencode.json ~/your-project/opencode.json
```

Or copy it to `~/.config/opencode/opencode.json` to apply it to every project.
`update` is honored only in the global file.

### Install the modular sample

```bash
cd ~/your-project
cp ~/src/ai-dev/docs/tools/opencode/agent-subagent-config/opencode.json .
cp -r ~/src/ai-dev/docs/tools/opencode/agent-subagent-config/prompts .
mkdir -p .opencode
cp -r ~/src/ai-dev/docs/tools/opencode/agent-subagent-config/agents .opencode/agents
```

The plan agent loads its prompt with `{file:./prompts/plan.txt}`, which resolves
relative to `opencode.json`. Keep `prompts/` beside it.

---

## Standard configuration walkthrough

The standard sample is a single [`opencode.json`](https://github.com/CowboyLogic/ai-dev/blob/main/docs/tools/opencode/standard-config/opencode.json).
Its sections are described below.

### Model and title agent

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "github-copilot/claude-sonnet-5",
  "default_agent": "build",
  "agents": {
    "title": { "model": "github-copilot/gpt-5-mini" }
  }
}
```

- `model` is the default in `provider/model` form. The root default does not keep a
  `#variant`; agent and command model references can.
- `default_agent` must name a visible, primary-capable agent. Otherwise OpenCode falls
  back to `build`.
- V1's `small_model` is replaced by the built-in `title` agent's model.
- The `github-copilot` provider is built in. Sign in once with `/connect`; no API key
  or `providers` block is needed.

### Agents

```jsonc
{
  "agents": {
    "quick": {
      "description": "Fast agent for basic tasks like code formatting, simple queries, and quick fixes",
      "mode": "primary",
      "model": "github-copilot/gpt-5-mini"
    },
    "reviewer": {
      "description": "Code review agent that analyzes code without making changes",
      "mode": "subagent",
      "model": "github-copilot/claude-sonnet-5",
      "permissions": [
        { "action": "*", "resource": "*", "effect": "deny" },
        { "action": "read", "resource": "*", "effect": "allow" },
        { "action": "glob", "resource": "*", "effect": "allow" },
        { "action": "grep", "resource": "*", "effect": "allow" },
        { "action": "webfetch", "resource": "*", "effect": "allow" }
      ]
    }
  }
}
```

| Field | Meaning |
|---|---|
| `description` | Purpose. Required in practice for subagents: the model reads it to choose which agent to launch. |
| `mode` | `primary`, `subagent`, or `all`. **A new custom agent defaults to `primary`.** |
| `model` | `provider/model`, optionally `#variant` (for example `anthropic/claude-sonnet-5#high`). A subagent without a model inherits the parent session's model. |
| `system` | System prompt (JSON only). In a Markdown agent the body is the prompt. Supports `{file:./path}`. |
| `permissions` | Ordered rule list. See [Permissions](#permissions). |
| `steps` | Maximum model steps before OpenCode forces a text summary. |
| `hidden` | Removes the agent from listings, `@` discovery, **and the subagent catalog**. |
| `disabled` | Removes a built-in or custom agent. |
| `color` | Six-digit hex UI color, for example `"#ff6b6b"`. |

Built-in agents: `build` and `plan` (primary), `general` and `explore` (subagents), plus
hidden `compaction`, `title`, and `summary`. Override a built-in by defining an agent
with the same ID. Agent definitions merge in configuration order: later scalars
replace earlier ones, and permission rules append.

> [!NOTE]
> **Temperature is not active per agent in V2.** V1's `temperature`, `top_p`, and
> provider options move under `request.body`, which V2 preserves but does not yet send
> with model requests. Configure request settings on a provider, model, or model
> variant instead, and select the variant with `model: provider/model#variant`. The
> samples in this repository no longer set a temperature.

### Commands

```jsonc
{
  "commands": {
    "review": {
      "template": "Review the following code for quality, security, and best practices: $ARGUMENTS",
      "description": "Code review without modifications",
      "agent": "reviewer",
      "subagent": true
    }
  }
}
```

Run it in the TUI as `/review src/auth.ts`.

| Field | Behavior |
|---|---|
| `template` | Prompt template (JSON only; a Markdown command uses its body). `$ARGUMENTS` receives the text after the command. |
| `description` | Shown in command lists. |
| `agent` | Agent selected when the command runs. |
| `model` | Model override, `provider/model` or `provider/model#variant`. |
| `subagent` | `true` runs the command in a background child session that reports back. Replaces V1 `subtask`. |

Markdown commands work the same way: `.opencode/commands/review.md`, with the fields
above as frontmatter and the body as the template.

### Global permissions, MCP, and client settings

```jsonc
{
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "ask" }
  ],
  "mcp": {
    "servers": {
      "github": {
        "type": "remote",
        "url": "https://api.githubcopilot.com/mcp/",
        "headers": { "Authorization": "Bearer {env:GITHUB_TOKEN}" }
      }
    }
  },
  "update": "notify",
  "share": "manual"
}
```

- Top-level `permissions` apply to every agent. Each agent's own rules are appended after
  them, so agent rules can refine global ones.
- `update` is `"disable"`, `"notify"` (default), or `"auto"`, and is honored only in the
  global config. It replaces V1 `autoupdate`.
- `share` is accepted, but session sharing is not supported yet in V2.
- `theme` and keybinds are not `opencode.json` fields in V2. They live in the terminal
  client config, `~/.config/opencode/cli.json`, which V2 migrates from `tui.json` on
  first start.

---

## Modular configuration

The modular sample keeps only the primary agents in
[`opencode.json`](https://github.com/CowboyLogic/ai-dev/blob/main/docs/tools/opencode/agent-subagent-config/opencode.json)
and defines each subagent as a Markdown file in `.opencode/agents/`.

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "model": "github-copilot/gpt-6-sol",
  "agents": {
    "plan": {
      "mode": "primary",
      "system": "{file:./prompts/plan.txt}",
      "model": "github-copilot/claude-sonnet-5",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "edit", "resource": "plans/**", "effect": "allow" },
        { "action": "shell", "resource": "*", "effect": "deny" }
      ]
    },
    "build": { "mode": "primary", "model": "github-copilot/gpt-6-sol" }
  }
}
```

### How agents are discovered

OpenCode discovers Markdown agents from `~/.config/opencode/agents/` and from every
`.opencode/agents/` directory between the current directory and the project root. No
`opencode.json` entry is needed.

- **The ID is the file path minus `.md`.** `.opencode/agents/security.md` is `security`,
  and `.opencode/agents/team/reviewer.md` is `team/reviewer`. A file named
  `security.agent.md` loads as `security.agent`.
- There is no `name` field. Rename the file to rename the agent.
- V2 still discovers the V1 directory names `agent/`, `mode/`, and `modes/`, but
  `agents/` is the preferred location. Files under `mode/` or `modes/` are primary
  agents.

> [!CAUTION]
> Agents are **not** loaded through `instructions`. Older versions of this guide
> listed `"instructions": ["agent/*.md"]` as the discovery mechanism. That never
> registered agents, and in V2 `instructions` entries are not loaded at all.

### Agent file format

The frontmatter accepts the same fields as a JSON `agents` entry. The Markdown body
becomes the system prompt.

```markdown
---
description: Security audits, vulnerability scanning, and best practices
mode: subagent
model: github-copilot/claude-sonnet-5
permissions:
  - { action: edit, resource: "*", effect: deny }
---

# Agent Purpose

The Security agent focuses on identifying vulnerabilities and ensuring best practices
for secure coding and infrastructure.
```

The rule list can be written in flow style (one rule per line, as above) or block
style. Both are standard YAML.

### Sample subagents

| Agent | Model | Access |
|---|---|---|
| `api` | `github-copilot/gpt-6-sol` | Full |
| `architect` | `github-copilot/claude-sonnet-5` | Read-only (deny all, then allow read, glob, grep) |
| `cloud` | `github-copilot/gpt-6-sol` | Full |
| `data` | `github-copilot/gpt-5-mini` | Full |
| `database` | `github-copilot/gpt-6-sol` | Full |
| `devops` | `github-copilot/gpt-5-mini` | Full |
| `documentation` | `github-copilot/gpt-6-luna` | Edit, no shell |
| `performance` | `github-copilot/gpt-6-sol` | Full |
| `research` | `github-copilot/gpt-5-mini` | Shell, no edit |
| `reviewer` | `github-copilot/claude-sonnet-5` | Read-only (deny all, then allow read, glob, grep) |
| `security` | `github-copilot/claude-sonnet-5` | Shell, no edit |
| `testing` | `github-copilot/gpt-5-mini` | Full |
| `uxui` | `github-copilot/gemini-3.8-flash` | Edit, no shell |

"Full" means the agent has no permission rules of its own and runs under the base
policy plus any global rules. The base policy does not deny the `subagent` action
either; add a `subagent` deny rule if an agent should not delegate.

Invoke a subagent by `@`-mentioning it in the TUI (`@security audit src/auth/`), or let
a primary agent launch it through the subagent tool.

### Adding an agent

1. Create `.opencode/agents/<id>.md`, using the file name as the ID.
2. Add `description` and `mode: subagent`, plus `model` and `permissions` as needed.
3. Write the prompt as the body.
4. Start a new session, then confirm the agent loaded with `opencode debug agents`.

---

## Permissions

`permissions` is an ordered list of rules. Each rule has three string fields:

| Field | Meaning |
|---|---|
| `action` | Tool or permission action. Wildcards allowed. |
| `resource` | Path, command, URL, query, skill ID, or agent ID. Wildcards allowed. |
| `effect` | `allow`, `ask`, or `deny`. |

**The last matching rule wins.** Put the broad rule first and the exceptions after it.
`*` matches zero or more characters, including `/`, and `?` matches exactly one
character. A shell pattern that ends in a space and `*` also matches the bare command,
so `git status *` matches `git status`.

| Action | Covers |
|---|---|
| `shell` | Shell commands (V1 `bash`) |
| `edit` | Edit, write, and patch tools (V1 `edit`, `write`, `patch`) |
| `subagent` | Launching child agents; resource is the agent ID (V1 `task`) |
| `read`, `glob`, `grep` | Local discovery tools |
| `webfetch`, `websearch` | Web tools |
| `skill` | Skill loading; resource is the skill ID |
| `external_directory` | Paths outside the project |
| `<server>_<tool>` | An MCP tool |

### The default is allow

Every agent starts from this base policy, and global and agent rules are appended after
it:

```json
[
  { "action": "*", "resource": "*", "effect": "allow" },
  { "action": "external_directory", "resource": "*", "effect": "ask" },
  { "action": "read", "resource": "*.env", "effect": "ask" },
  { "action": "read", "resource": "*.env.*", "effect": "ask" },
  { "action": "read", "resource": "*.env.example", "effect": "allow" }
]
```

**An action you do not mention is allowed.** Denying only `edit` and `shell` does not make
an agent read-only: `subagent`, `skill`, `question`, web, and MCP actions stay open. For a
read-only agent, start with a catch-all `{ "action": "*", "resource": "*", "effect": "deny" }`
and then allow `read`, `glob`, and `grep`. The topologies in this repository deny
every action a role must not have, by name.

### Rule order is the classic bug

```yaml
# Correct: catch-all first, exception after
permissions:
  - { action: edit, resource: "*", effect: deny }
  - { action: edit, resource: ".agent-output/**", effect: allow }
```

Reversed, the `"*"` deny is the last match for every path, so the agent cannot edit
anything, including the directory it was granted. OpenCode raises no error.

### Compound shell commands

V2's shell scanner checks each command in a compound command such as `cd x && git push`
separately. If any part is denied, the whole command is denied. Directory inference is
best effort, so prefer a narrow allowlist over a list of dangerous patterns when shell
access must be restricted.

### Approvals

When a rule resolves to `ask`, the prompt offers **once**, **always**, or **reject**.
"Always" saves a project-scoped allow rule, such as a command prefix, a skill ID, or an
agent ID. A saved approval never overrides a configured `deny`.

---

## Model selection

Models in this repository use the built-in `github-copilot` provider. The table covers
the models the samples and topologies use. Check `/models` for what your subscription
offers before pinning a model.

| Tier | Model | Used for |
|---|---|---|
| Fast and cheap | `github-copilot/gpt-6-luna`, `github-copilot/gpt-5-mini` | Title generation, docs, data, simple tasks |
| Balanced | `github-copilot/claude-sonnet-5` | Review, security, architecture, orchestration |
| Agentic coding | `github-copilot/gpt-6-sol` | Implementation, planning, and build loops |
| Cross-family review | `github-copilot/gemini-3.8-flash` | Independent review from a third model family |
| Heavy reasoning | `github-copilot/claude-opus-5.5` | Infrequent, high-stakes planning, design, and security review |

> [!WARNING]
> Copilot retires models regularly. Models that earlier versions of this guide and its
> samples used, including `claude-sonnet-4.5`, `claude-sonnet-4.6`, `gemini-2.5-pro`,
> `gemini-3.1-pro-preview`, `gpt-4o`, and `grok-code-fast-1`, have been retired. A pin to
> a retired model fails at request time, not at load time.

A model variant selects preset request settings, such as reasoning effort:
`github-copilot/claude-sonnet-5#high`. Available variants depend on the provider and
model.

---

## MCP servers

V2 nests servers under `mcp.servers`:

```jsonc
{
  "mcp": {
    "servers": {
      "github": {
        "type": "remote",
        "url": "https://api.githubcopilot.com/mcp/",
        "oauth": false,
        "headers": { "Authorization": "Bearer {env:GITHUB_TOKEN}" }
      },
      "everything": {
        "type": "local",
        "command": ["npx", "-y", "@modelcontextprotocol/server-everything"],
        "environment": { "MCP_API_KEY": "{env:MCP_API_KEY}" },
        "timeout": { "catalog": 30000, "execution": 30000 }
      }
    }
  }
}
```

- Servers connect automatically. Use `"disabled": true` to keep a server configured
  without connecting it. V1's `enabled` is inverted into `disabled`.
- Substitute environment variables with `{env:NAME}`. Shell syntax such as `$NAME` or
  `${NAME}` is not expanded inside JSON strings.
- Remote servers use OAuth by default. Set `"oauth": false` for servers that only accept
  a header credential. OAuth fields are snake_case (`client_id`, `client_secret`,
  `callback_port`, `redirect_uri`).
- `timeout` is an object with separate `catalog` and `execution` values in milliseconds.
  Set defaults under `mcp.timeout`.
- `opencode mcp add <name> --url <url>` writes a server entry for you, and
  `opencode mcp list` shows the connection state.

MCP tools are permission actions named `<server>_<tool>`. For example, deny one server's
tools for an agent with `{ "action": "github_*", "resource": "*", "effect": "deny" }`.

---

## Instructions and AGENTS.md

V2 loads project guidance from `AGENTS.md` files only:

- the global `~/.config/opencode/AGENTS.md`, then
- every `AGENTS.md` from the current workspace up toward the home directory. For a
  workspace outside the home directory, discovery stops at the project root.

Nested `AGENTS.md` files below the workspace are loaded as the agent reads files in
that area. V2 does not fall back to `CLAUDE.md`.

> [!CAUTION]
> **`instructions` is accepted but not loaded in V2.** A V1 config that loaded
> guardrails or rules through `"instructions": ["guardrails.md"]` silently stops
> applying them under V2. Move that guidance into an `AGENTS.md` that V2 discovers,
> for example by linking the file to `~/.config/opencode/AGENTS.md`.

---

## Topologies in this repository

The multi-agent topologies in `agents/` are the fullest examples of this configuration.
Each ships native V2 agents and a harness config:

| Topology | Agents | Harness |
|---|---|---|
| [Matrix](../../agents/matrix-topology.md) | `agents/matrix-topology/opencode/*.md` | `harness/opencode/` |
| [Lane](../../agents/lane-topology.md) | `agents/lane-topology/opencode/*.md` | `harness/opencode-lane/` |

They show the V2 rules that matter at scale:

- Agent files are named `<id>.md`. The Matrix files were renamed from `.agent.md`,
  because V2 would otherwise load `tank.agent.md` as `tank.agent` and dispatch to `tank`
  would fail.
- Subagents ship `hidden: false`, because `hidden: true` would remove them from the
  primary agent's subagent catalog.
- Every capability a role must not have is denied by name. Only the conductor holds
  `subagent`.
- `validate.py` (Lane) resolves the rules the way V2 does and fails on any V1 field or
  action name.

---

## Migrating from V1

V2 translates V1 configuration automatically, so migration is optional. To convert a
file to native V2:

| V1 | V2 |
|---|---|
| `agent`, `mode` (maps) | `agents` |
| `prompt` | `system` (JSON); Markdown keeps the body |
| `disable` | `disabled` |
| `maxSteps` | `steps` |
| `model` + `variant` | `model: provider/model#variant` |
| `temperature`, `top_p`, options | `request.body` (preserved, not yet sent) |
| `tools` + `permission` maps | ordered `permissions` rules |
| `bash`, `task`, `write`/`patch` actions | `shell`, `subagent`, `edit` |
| `command`, `subtask` | `commands`, `subagent` |
| `mcp.<name>`, `enabled` | `mcp.servers.<name>`, `disabled` |
| `small_model` | `agents.title.model` |
| `autoupdate` | `update` |
| `autoshare: true` | `share: "auto"` |
| `snapshot` | `snapshots` |
| `plugin` | `plugins` (V1 plugin code does not run in V2) |
| `tui.json` | `~/.config/opencode/cli.json` (migrated on first start) |

A V1 `tools` map converts to rules like this. `true` becomes `allow`, `false` becomes
`deny`, and each key is renamed to its V2 action:

```yaml
# V1
tools:
  write: false
  edit: false
  bash: true

# V2
permissions:
  - { action: edit, resource: "*", effect: deny }
  - { action: shell, resource: "*", effect: allow }
```

A V1 key you omitted was enabled by default, and the equivalent V2 action is still
allowed. The V1 idea that "no tools defined means read-only" was never true.

The `client-config-opencode` and `agent-creator-opencode` skills in this repository
cover the full V1-to-V2 field mapping.

---

## Troubleshooting

**Check what actually loaded.** These commands print the resolved result rather than
what the files say:

```bash
opencode debug config   # every config source and its parsed content
opencode debug agents   # every agent with its resolved model, mode, and permission rules
```

The first run in a directory that has never been opened can print an empty agent list.
Run it again.

| Symptom | Likely cause |
|---|---|
| Agent missing from `@` and from delegation | File is not under an `agents/` directory, or it has `hidden: true` |
| Delegation to `x` fails, but `x.agent` exists | File is named `x.agent.md`. Rename it to `x.md` |
| Read-only agent edited a file or launched a subagent | No catch-all deny. Omitted actions are allowed |
| Scoped edit grant denies everything | Catch-all `"*"` rule placed after the specific rule |
| Rules in `guardrails.md` are ignored | Loaded through `instructions`, which V2 does not load. Use `AGENTS.md` |
| Editor flags `agents` or `permissions` | The published schema is V1-only. See the warning at the top |
| Model request fails | Pinned model is retired or not enabled for your Copilot plan |

## Next steps

- [OpenCode Overview](index.md): feature overview and use cases
- [Sample Configurations](samples.md): MCP server examples
- [OpenCode Configuration Manager skill](../../skills/client-config-opencode.md): V1 and V2 configuration reference
- [OpenCode V2 documentation](https://opencode.ai/v2/docs/)

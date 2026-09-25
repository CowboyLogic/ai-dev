# OpenCode Sample Configurations

Guidance for working with the two OpenCode sample configurations in `docs/tools/opencode/`.
Both samples use the native **OpenCode V2** configuration format.

> [!NOTE]
> OpenCode V2 loads `AGENTS.md` files automatically: the global `~/.config/opencode/AGENTS.md`, then every `AGENTS.md` from the current workspace up to the project root. It does not fall back to `CLAUDE.md`, and it does not load files listed in `instructions` (the key is accepted but ignored). Put project guidance in `AGENTS.md`.

## The Two Samples

| Sample | Files | Best for |
| --- | --- | --- |
| Standard | `standard-config/opencode.json` | One file holding every agent, command, permission, and MCP server |
| Modular | `agent-subagent-config/opencode.json`, `agent-subagent-config/prompts/plan.txt`, `agent-subagent-config/agents/*.md` | Many specialized subagents, one Markdown file each |

Both samples use the built-in GitHub Copilot provider (`github-copilot/...` models). Sign in once with `/connect` in the OpenCode interface.

## Installing

### Standard configuration

Copy the file to a project root, or to the global config directory to apply it to every project:

```bash
# Project
cp docs/tools/opencode/standard-config/opencode.json ~/your-project/opencode.json

# Global
cp docs/tools/opencode/standard-config/opencode.json ~/.config/opencode/opencode.json
```

The `update` setting is honored only in the global config; a project config ignores it. The GitHub MCP server reads its token from the environment through `{env:GITHUB_TOKEN}`, so export `GITHUB_TOKEN` before starting OpenCode.

### Modular configuration

Copy `opencode.json` and `prompts/` to the project root, and the subagent files into `.opencode/agents/`:

```bash
cp docs/tools/opencode/agent-subagent-config/opencode.json ~/your-project/
cp -r docs/tools/opencode/agent-subagent-config/prompts ~/your-project/
mkdir -p ~/your-project/.opencode/agents
cp docs/tools/opencode/agent-subagent-config/agents/*.md ~/your-project/.opencode/agents/
```

The `plan` agent loads its system prompt with `"system": "{file:./prompts/plan.txt}"`, so keep `prompts/` next to `opencode.json`.

For global use, put the agent files in `~/.config/opencode/agents/` instead.

## Standard Configuration Agents

| Agent | Mode | Model | Access |
| --- | --- | --- | --- |
| `quick` | primary | `github-copilot/gpt-5-mini` | Full |
| `reviewer` | subagent | `github-copilot/claude-sonnet-5` | Read-only: deny all, then allow `read`, `glob`, `grep`, `webfetch` |
| `docs` | subagent | `github-copilot/gpt-6-luna` | Edits files, denies `shell` |
| `title` (built-in) | hidden | `github-copilot/gpt-5-mini` | Generates session titles; replaces V1 `small_model` |

The default model is `github-copilot/claude-sonnet-5` and the default agent is the built-in `build`.

Commands: `/quick-fix` (runs on `quick`), `/review` (runs `reviewer` as a subagent), `/document` (runs on `docs`), `/build`, `/test`, and `/deploy` (current agent).

Global permissions allow shell commands but ask before any `git push`.

## Modular Configuration Agents

Primary agents, defined in `opencode.json`:

| Agent | Model | Access |
| --- | --- | --- |
| `plan` | `github-copilot/claude-sonnet-5` | Edits files (to write plans), denies `shell`; prompt from `prompts/plan.txt` |
| `build` | `github-copilot/gpt-6-sol` | Full |

Subagents, one file each in `.opencode/agents/`:

| Agent | Model | Access |
| --- | --- | --- |
| `api` | `github-copilot/gpt-6-sol` | Full |
| `architect` | `github-copilot/claude-sonnet-5` | Read-only: deny all, then allow `read`, `glob`, `grep` |
| `cloud` | `github-copilot/gpt-6-sol` | Full |
| `data` | `github-copilot/gpt-5-mini` | Full |
| `database` | `github-copilot/gpt-6-sol` | Full |
| `devops` | `github-copilot/gpt-5-mini` | Full |
| `documentation` | `github-copilot/gpt-6-luna` | Edits files, denies `shell` |
| `performance` | `github-copilot/gpt-6-sol` | Full |
| `research` | `github-copilot/gpt-5-mini` | Denies `edit`, may run shell |
| `reviewer` | `github-copilot/claude-sonnet-5` | Read-only: deny all, then allow `read`, `glob`, `grep` |
| `security` | `github-copilot/claude-sonnet-5` | Denies `edit`, may run shell |
| `testing` | `github-copilot/gpt-5-mini` | Full |
| `uxui` | `github-copilot/gemini-3.8-flash` | Edits files, denies `shell` |

"Full" means the agent has no rules of its own and inherits the base policy. Ask a primary agent to use a subagent by name, for example "Use the security subagent to audit the login flow."

## Permission Basics

V2 replaces the V1 `tools` and `permission` maps with one ordered `permissions` list. Each rule has an `action`, a `resource`, and an `effect` (`allow`, `ask`, or `deny`). The **last matching rule wins**, so write broad rules first and exceptions after them.

```json
"permissions": [
  { "action": "shell", "resource": "*", "effect": "allow" },
  { "action": "shell", "resource": "git push *", "effect": "ask" }
]
```

- The base policy starts with allow-all, so any action no rule mentions is allowed. Reads of `.env` files and access outside the workspace (`external_directory`) ask for approval.
- Global `permissions` apply before an agent's own rules, so agent rules can refine them.
- Common actions: `shell` (V1 `bash`), `edit` (covers edit, write, and patch), `subagent` (V1 `task`), `read`, `glob`, `grep`, `webfetch`, `websearch`, `skill`, `external_directory`, and `<server>_<tool>` for MCP tools.
- In Markdown agent frontmatter the same rules are written as a YAML list:

  ```yaml
  permissions:
    - { action: edit, resource: "*", effect: deny }
  ```

## V2 Agent Notes

- Agents live under `agents` (V1 `agent`) and set their prompt with `system` (V1 `prompt`). A Markdown agent's body is its system prompt.
- A Markdown agent's ID is its path minus `.md` (`reviewer.md` becomes `reviewer`; `reviewer.agent.md` becomes `reviewer.agent`). There is no `name` field.
- A new custom agent defaults to `mode: primary`. Set `mode: subagent` for helper agents.
- `hidden: true` removes an agent from listings and from the subagent catalog. It is not a security control; use `permissions`.
- Models use `provider/model`, optionally with `#variant`.
- Do not set `temperature`. V2 preserves per-agent `request.body` values but does not send them yet.
- `theme` and keybinds belong in `~/.config/opencode/cli.json`, not `opencode.json`.
- The `$schema` URL (`https://opencode.ai/config.json`) still describes V1 and may flag V2 keys. There is no published V2 schema yet.

## Maintenance Checklist

When a sample changes, update these files in the same change:

- [ ] `docs/tools/opencode/configuration.md`: setup steps, agent tables, and examples
- [ ] `docs/tools/opencode/index.md`: overview, install commands, and agent lists
- [ ] `docs/tools/opencode/standard-config/AGENTS.md` (this file): install steps and agent tables
- [ ] `mkdocs.yml`: nav entries when a subagent file is added, removed, or renamed

Before committing, confirm that every model, permission, and path in these pages matches the sample files, then run `mkdocs build --clean --strict`.

See the [Configuration Guide](../configuration.md) for full details.

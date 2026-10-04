# OpenCode Sample Configurations

Guidance for working with the OpenCode sample configurations in this directory. All of them
use the native **OpenCode V2** configuration format.

> [!NOTE]
> OpenCode V2 loads `AGENTS.md` files automatically: the global `~/.config/opencode/AGENTS.md`, then every `AGENTS.md` from the current workspace up to the project root. It does not fall back to `CLAUDE.md`, and it does not load files listed in `instructions` (the key is accepted but ignored). Put project guidance in `AGENTS.md`.

## What is here

| Path | Contents | Best for |
| --- | --- | --- |
| `standard-config/opencode.json` | One file holding every agent, command, permission, and MCP server | A few agents, everything in one file |
| `agent-subagent-config/` | `opencode.json`, `prompts/plan.txt`, and `agents/*.md` | Many specialized subagents, one Markdown file each |
| `mcp/*.jsonc` | One MCP server entry per file, to copy into a config | Adding a Docker or npx MCP server |

These files are copied out by readers, not loaded by any harness in this repository. The
install commands are on the [OpenCode overview](../../docs/harness/opencode/index.md) page.
Both agent samples use the built-in GitHub Copilot provider (`github-copilot/...` models).

The files are the record of each agent's model and permissions. Do not restate them in prose:
a second copy goes stale the first time a model changes.

## Constraints that shape the files

- The modular sample's `plan` agent loads its system prompt with `"system": "{file:./prompts/plan.txt}"`,
  which resolves relative to `opencode.json`, so `prompts/` stays beside it.
- Subagents are files in `.opencode/agents/` once installed. A file's ID is its path minus
  `.md`, so `reviewer.md` is `reviewer` and `reviewer.agent.md` would be `reviewer.agent`.
  There is no `name` field.
- The `standard-config` sample sets a global `permissions` rule that allows shell commands but
  asks before any `git push`.

## Permission basics

V2 replaces the V1 `tools` and `permission` maps with one ordered `permissions` list. Each rule has an `action`, a `resource`, and an `effect` (`allow`, `ask`, or `deny`). The **last matching rule wins**, so write broad rules first and exceptions after them.

```json
"permissions": [
  { "action": "shell", "resource": "*", "effect": "allow" },
  { "action": "shell", "resource": "git push *", "effect": "ask" }
]
```

- The base policy starts with allow-all, so any action no rule mentions is allowed. Reads of `.env` files and access outside the workspace (`external_directory`) ask for approval. A read-only agent therefore starts with a catch-all deny, then allows `read`, `glob`, and `grep`.
- Global `permissions` apply before an agent's own rules, so agent rules can refine them.
- Common actions: `shell` (V1 `bash`), `edit` (covers edit, write, and patch), `subagent` (V1 `task`), `read`, `glob`, `grep`, `webfetch`, `websearch`, `skill`, `external_directory`, and `<server>_<tool>` for MCP tools.
- In Markdown agent frontmatter the same rules are written as a YAML list:

  ```yaml
  permissions:
    - { action: edit, resource: "*", effect: deny }
  ```

## V2 agent notes

- Agents live under `agents` (V1 `agent`) and set their prompt with `system` (V1 `prompt`). A Markdown agent's body is its system prompt.
- A new custom agent defaults to `mode: primary`. Set `mode: subagent` for helper agents.
- `hidden: true` removes an agent from listings and from the subagent catalog. It is not a security control; use `permissions`.
- Models use `provider/model`, optionally with `#variant`.
- Do not set `temperature`. V2 preserves per-agent `request.body` values but does not send them yet.
- MCP servers live under `mcp.servers`, use `disabled` (not `enabled`), and take a `timeout` object (`catalog`, `execution`). Environment variables use `{env:NAME}`.
- `theme` and keybinds belong in `~/.config/opencode/cli.json`, not `opencode.json`.
- The `$schema` URL (`https://opencode.ai/config.json`) still describes V1 and may flag V2 keys. There is no published V2 schema yet.

## Maintenance checklist

When a sample changes, update these in the same change:

- [ ] `docs/harness/opencode/configuration.md`: the walkthrough snippets that quote the sample
- [ ] `docs/harness/opencode/index.md`: the install commands and the subagent name list
- [ ] `docs/mcp/index.md`: the sample table, when an `mcp/` file is added, removed, or renamed
- [ ] The `.jsonc` files in `mcp/`: keep them valid V2 and free of secrets

Before committing, confirm that every path and command in those pages matches the files here,
then run `python scripts/validate_artifact_sync.py` and `mkdocs build --clean --strict`.

See the [Configuration Guide](../../docs/harness/opencode/configuration.md) for the full reference.

---
name: agent-creator-codex
description: Guide for creating custom subagents for OpenAI Codex (standalone TOML files in .codex/agents/ or ~/.codex/agents/, each with name, description, and developer_instructions). Use this skill whenever a user wants to build, configure, review, or modify a Codex agent, choose fields (model, model_reasoning_effort, sandbox_mode, mcp_servers, skills.config, nickname_candidates), tune the [agents] table in config.toml (concurrency, default subagent model), or troubleshoot a Codex agent that is not found, never spawned, on the wrong model, or blocked by sandbox and approvals. ALWAYS load this skill before writing or debugging Codex agent files.
license: MIT
---

# Codex Agent Creator

Codex custom agents ("subagents") are standalone **TOML** files. Each file defines one agent
and is loaded as a configuration layer for the sessions Codex spawns. Unlike Claude Code and
Copilot agents there is no Markdown body: the system prompt is the `developer_instructions`
string inside the TOML.

> [!IMPORTANT]
> Codex only delegates when asked. It never spawns a subagent on its own initiative unless
> the prompt, an applicable `AGENTS.md`, or a skill requests delegation. An agent file that
> loads correctly can still sit unused. See [Invocation](#invocation).

Official docs: <https://developers.openai.com/codex/subagents> (redirects to
`learn.chatgpt.com/docs/agent-configuration/subagents`). Config keys:
<https://developers.openai.com/codex/config-reference>.

---

## When to Use This Skill

- Creating a new Codex agent file
- Choosing or fixing fields, especially `model`, `sandbox_mode`, and `mcp_servers`
- Setting spawn limits and defaults in the `[agents]` table of `config.toml`
- Diagnosing an agent that is not found, never delegated to, or running with the wrong model
  or permissions
- Reviewing an agent file before committing it to a repository

For Codex *settings* generally (approvals, profiles, providers, hooks), read the Codex config
reference. For repository-wide instructions, use `AGENTS.md`, not an agent file.

---

## Quick Decision Guide

| Need | Approach |
|---|---|
| Isolated context, narrower tools, or a different model for a side task | **Custom agent** (this skill) |
| Instructions every session in a repo should follow | `AGENTS.md` |
| Reusable procedure the main agent loads on demand | Skill (`SKILL.md`) |
| Parallel work with no custom behavior | Built-in `default`, `worker`, or `explorer` |
| A role defined next to other config in one file | `[agents.<name>]` table in `config.toml` |

---

## Agent File Format

```toml
name = "pr_explorer"
description = "Read-only codebase explorer for evidence gathering. Use before proposing changes."
model = "gpt-6-luna"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Stay in exploration mode. Trace real execution paths, cite files and symbols,
and avoid proposing fixes. Prefer fast search over broad scans.
"""

[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

Required fields. A file that omits or blanks any of them is **ignored with a warning**, not
rejected loudly (see [Load Failures](#load-failures)):

| Field | Purpose |
|---|---|
| `name` | The identifier Codex uses to spawn or refer to the agent. Authoritative over the filename |
| `description` | Guidance shown when Codex chooses an agent: what it does and when to use it |
| `developer_instructions` | The agent's system-prompt-level instructions. Must not be blank |

Everything else is optional and is any other `config.toml` key applied as a layer over the
parent session. Load `references/config-reference.md` for the full field list, allowed
values, and the `[agents]` table.

Rules that avoid load failures:

1. Valid TOML. Use `"""` multi-line strings for `developer_instructions`.
2. Keep `name` unique across project and personal scope. Use `snake_case` or `kebab-case`
   consistently and match the filename to it (`pr_explorer.toml`).
3. Top-level keys go **before** any `[table]` header. A key placed after `[mcp_servers.x]`
   belongs to that table, not to the agent.
4. Field names are `snake_case`, and unknown keys make the whole file invalid. Do not carry
   over `disallowedTools`, `tools`, or `permissionMode`; Codex has no such keys.

---

## Where Agent Files Live

| Scope | Location |
|---|---|
| Project | `.codex/agents/` (loaded **only when the project is trusted**) |
| Personal | `~/.codex/agents/` (`$CODEX_HOME/agents/`) |
| Config table | `[agents.<name>]` in `config.toml`, with `config_file` pointing at a TOML layer |

Built-in agents `default`, `worker`, and `explorer` can be overridden by defining a custom
agent with the same name.

> [!NOTE]
> Two files with the same `name` in one directory: Codex warns and drops the duplicate.
> The same `name` in project and personal scope raises no warning, and the winner could not
> be observed without a model call. Keep names unique across scopes.

---

## Model and Reasoning Effort

```toml
model = "gpt-6-luna"
model_reasoning_effort = "high"   # low | medium | high | xhigh | max | ultra (model dependent)
```

Resolution order, first match wins:

1. An explicit value given at spawn time
2. `agents.default_subagent_model` / `agents.default_subagent_reasoning_effort` in `config.toml`
3. The value in the agent file
4. The model's built-in default (when only `model` is set)

Note that step 2 outranks the agent file. A `default_subagent_model` in `config.toml`
overrides `model` in every agent file that does not get an explicit spawn value. If an agent
runs on the "wrong" model, check `[agents]` before the agent file.

Valid model names and effort levels depend on the account and Codex build. Run
`codex debug models` to list the catalog.

---

## Sandbox and Approvals

```toml
sandbox_mode = "read-only"   # read-only | workspace-write | danger-full-access
```

- Subagents **inherit the parent's sandbox policy and approval mode**.
- Runtime overrides win over the file. `--yolo` and a live `/permissions` change apply to
  spawned agents even when the agent file sets a stricter `sandbox_mode`.
- Do not rely on `sandbox_mode = "read-only"` as a hard guarantee for a role. It is a default
  for that layer, not a lock. If a role must never write, also say so in
  `developer_instructions` and run the parent session with a matching policy.
- In interactive CLI sessions, approval requests from inactive agent threads can surface in
  the main view. Press `o` to inspect the request before approving.

Apply least privilege: start `read-only`, and use `workspace-write` only for roles that edit.
Avoid `danger-full-access` in any shared agent file.

---

## MCP Servers and Skills

```toml
[mcp_servers.docs]
url = "https://example.com/mcp"
enabled_tools = ["search", "fetch"]   # optional allowlist
```

Servers defined in an agent file are scoped to that agent's layer. Use `enabled_tools` /
`disabled_tools` to narrow a server. Do not hardcode tokens; use `bearer_token_env_var` or
another environment-based field. `skills.config` applies per-skill enablement overrides.

---

## Invocation

Codex delegates when one of these is true:

- **Explicit request.** Ask for it: "Spawn one `pr_explorer` per module and summarize."
- **Instruction-based.** An applicable `AGENTS.md` or skill tells Codex to delegate.
- **ChatGPT Ultra** can proactively delegate suitable independent work.

To make an agent get used, name it in the request or in `AGENTS.md`, and write a
`description` that names the trigger. Good: "Read-only reviewer. Use after any change under
`src/auth/`". Bad: "Helps with code".

Global limits live in `config.toml`:

```toml
[agents]
enabled = true                         # multi-agent tools on/off (default true)
max_concurrent_threads_per_session = 4 # spawned threads, excluding the primary
default_subagent_model = "gpt-6-luna"
default_subagent_reasoning_effort = "medium"
```

`agents.max_threads` is the legacy alias for `max_concurrent_threads_per_session`.
`agents.max_depth` and `agents.job_max_runtime_seconds` are accepted by Codex 0.158.0 but
absent from the public config reference, so their exact semantics are undocumented.

> [!WARNING]
> Under `[agents]`, any key Codex does not know is parsed as a role table. A typo such as
> `max_thread = 3` is a **fatal** startup error (`Error loading config.toml: invalid type:
> integer, expected struct AgentRoleToml`), unlike a bad agent file, which is only skipped.

---

## Writing the Prompt (`developer_instructions`)

The agent sees this text plus whatever the spawn request passes it. It does not see the
parent conversation. Write it so it works from a delegation message alone:

1. **Role** in one sentence.
2. **Scope**: what it reads, what it may change, what it must not touch.
3. **Method**: the steps or checks, in order of importance.
4. **Return format**: exactly what the parent needs back (findings with `path:line`, a diff
   summary, pass/fail).
5. **Stop conditions**: when to return instead of continuing.

Narrow, opinionated agents work best. Split a "does everything" agent into a reader and a
writer. Load `references/agent-examples.md` for complete files.

---

## Creating an Agent: Step-by-Step

### Step 1: Plan

1. One sentence for the role, and what it does **not** do.
2. Scope: project (`.codex/agents/`, committed for the team) or personal (`~/.codex/agents/`).
3. Sandbox first (`read-only` unless it must edit), then model and effort. Cheaper model and
   lower effort for read-heavy exploration; stronger for design and review.

### Step 2: Write the File

Create `.codex/agents/<name>.toml`. Start from `references/agent-examples.md` and delete
fields you do not need. Fewer keys means fewer surfaces that can misbehave.

### Step 3: Validate

```bash
python scripts/validate-agent.py .codex/agents/pr_explorer.toml
python scripts/validate-agent.py .codex/agents/          # a whole directory
python scripts/validate-agent.py .codex/agents/ --strict # warnings fail too
```

The bundled script (path relative to this skill's directory) uses only the Python 3.11+
standard library. It checks that the TOML parses, the three required fields are present and
non-blank, keys are known and correctly cased, enum values are valid, and names are unique
and match the filename.

### Step 4: Test

1. Start a new session so the file is picked up. Load warnings print at session start; a
   non-interactive `codex exec "hi"` shows them without spending a real task.
2. Ask for the agent by name: "Use `pr_explorer` to trace how login is handled."
3. Confirm the model, effort, and sandbox it actually got, using the session's agent view.
4. Give it a task it should refuse or cannot complete and confirm the restrictions hold.

---

## Load Failures

Codex does **not** stop on a bad agent file. It prints
`warning: Ignoring malformed agent role definition: <reason>` and carries on without that
agent, so the agent is simply missing. Verified against codex-cli 0.158.0:

| Defect | Codex message (abridged) |
|---|---|
| TOML syntax error | `failed to parse agent role file ...: TOML parse error at line N` |
| Unknown or camelCase key | `failed to deserialize agent role file ...: unknown field 'key'` |
| `tools = [...]` list | `data did not match any variant of untagged enum WebSearchToolConfigInput` (`tools` is a table in Codex) |
| Bad `sandbox_mode` | `unknown variant 'root', expected one of 'read-only', 'workspace-write', 'danger-full-access'` |
| Missing `name` | `must define a non-empty 'name'` |
| Missing `description` | `agent role 'x' must define a description` |
| Missing or blank `developer_instructions` | `must define 'developer_instructions'` / `cannot be blank` |
| Same `name` twice in one directory | `duplicate agent role name 'x' discovered in <dir>` |
| `[agents.x].config_file` missing | `agents.x.config_file must point to an existing file at <path>` |

Not checked at load: an unrecognized `model_reasoning_effort` value, and a `name` that differs
from the filename. A project-scope file in an **untrusted** project is skipped without any
warning. Run the validator, then confirm with `codex exec "hi"`.

---

## Troubleshooting

Load `references/troubleshooting.md` for the full symptom-to-cause table. Most common:

| Symptom | Likely cause |
|---|---|
| Agent missing, with a `Ignoring malformed agent role definition` warning at start | Bad TOML, unknown key, or missing or blank `name`, `description`, or `developer_instructions` |
| Project agent missing, no warning | The project is not trusted; project-scope agents load only for trusted projects |
| Agent never spawned | Nothing asked for delegation, or `description` is vague. Name the agent in the request or `AGENTS.md` |
| Wrong model or effort | `agents.default_subagent_*` or an explicit spawn value outranks the file |
| Agent wrote files despite `read-only` | Parent runtime policy (`--yolo`, `/permissions`) overrode the layer |
| MCP server missing | Key placed after a `[table]` header, server disabled, or tool not in `enabled_tools` |

---

## Security Considerations

- **Least privilege.** Default to `sandbox_mode = "read-only"`.
- **A file setting is not a lock.** Parent runtime overrides win, so enforce hard limits at
  the session level.
- **Project agents run with the user's authority.** Review `mcp_servers` and any command in an
  agent file you did not write before trusting the repository.
- **Secrets.** Use environment-variable fields, never literal tokens, in `mcp_servers`.

---

## Reference Files

| File | When to Load |
|---|---|
| `references/config-reference.md` | Every field, allowed values, the `[agents]` table, `[agents.<name>]` roles, resolution order |
| `references/agent-examples.md` | Complete read-only, implementer, and config-table role examples |
| `references/troubleshooting.md` | Symptom-to-cause tables for load, delegation, model, sandbox, and MCP problems |
| `scripts/validate-agent.py` | Validator for a file or directory of Codex agent TOML |

---

## Official Documentation

| Resource | URL |
|---|---|
| Subagents | <https://developers.openai.com/codex/subagents> |
| Config reference | <https://developers.openai.com/codex/config-reference> |
| AGENTS.md | <https://developers.openai.com/codex/guides/agents-md> |

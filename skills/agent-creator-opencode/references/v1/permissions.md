# OpenCode V1 Permission Reference

Deep reference for the V1 `permission` key on OpenCode agents.

**Sources (checked 2026-09-24):** <https://opencode.ai/docs/permissions/> ·
<https://opencode.ai/docs/agents/> · <https://opencode.ai/docs/tools/> ·
<https://opencode.ai/config.json>

> [!IMPORTANT]
> This is the **V1** `permission` map. Native V2 uses an ordered `permissions`
> array with renamed actions (`bash` becomes `shell`, `task` becomes `subagent`).
> For V2, load `../v2/permissions.md`.

Load this file when configuring fine-grained tool access, bash patterns, task
delegation rules, or external directory access. For the property overview, load
`properties.md`.

---

## Syntax forms

**Simple form** — same action for all inputs:

```yaml
permission:
  edit: deny
  webfetch: allow
  bash: ask
```

**Whole-config form** — one action for everything:

```json
{ "permission": "allow" }
```

**Wildcard key** — a `"*"` key sets the default, and specific keys override it.
Keys are matched as wildcard patterns against the tool name, so this also works
for custom and MCP tools:

```json
{
  "permission": {
    "*": "ask",
    "bash": "allow",
    "edit": "deny",
    "mymcp_*": "deny"
  }
}
```

**Object form** — different actions per input pattern:

```yaml
permission:
  bash:
    "*": ask
    "git *": allow
    "git commit *": ask
    "git push *": deny
    "rm *": deny
    "grep *": allow
  edit:
    "*": deny
    "src/docs/**": allow
```

---

## Pattern matching rules

- `*` — matches zero or more of any character
- `?` — matches exactly one character
- All other characters match literally
- **Last matching rule wins** — put the catch-all `"*"` first, specific overrides after
- Bash rules match the parsed command, for example `git status --porcelain`
- A bare pattern does not match argument variants: `"grep"` alone does not allow `grep pattern file.txt`, while `"grep *"` does. Use `"git status *"` when arguments may be passed

```yaml
permission:
  bash:
    "*": ask           # default: ask for everything
    "git *": allow     # allow all git subcommands
    "git push *": deny # but block push (overrides the git * rule above)
```

---

## Available permission keys

| Key | What it matches |
|---|---|
| `read` | File path being read |
| `edit` | File path being written/edited/patched (`write`, `edit`, `apply_patch`) |
| `glob` | Glob pattern being used |
| `grep` | Regex being searched |
| `list` | Directory listing (in the schema and agents-page table; no longer a documented tool on the tools page) |
| `bash` | Full shell command string |
| `task` | Subagent name being invoked |
| `external_directory` | Paths outside the project working directory |
| `lsp` | LSP queries (non-granular; the `lsp` tool is experimental and needs `OPENCODE_EXPERIMENTAL_LSP_TOOL=true`) |
| `skill` | Skill name being loaded |
| `todowrite` | Gates `todowrite`/`todoread` (shorthand only) |
| `webfetch` | Gates the `webfetch` tool (shorthand only) |
| `websearch` | Gates the `websearch` tool (shorthand only; tool only available with the OpenCode/OpenCode Go provider or `OPENCODE_ENABLE_EXA`/`OPENCODE_ENABLE_PARALLEL`) |
| `question` | Gates in-session user questions (shorthand only) |
| `doom_loop` | Repeated identical tool call, 3x (safety guard, shorthand only) |

Only `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task`, `external_directory`, `lsp`, and `skill` accept the object (per-pattern) form shown above. The rest accept a plain `allow`/`ask`/`deny` value only — no per-input patterns.

---

## Defaults

- Most permissions: `allow`
- `doom_loop`: `ask`
- `external_directory`: `ask`
- `read` for env files: `deny` (`*.env`, `*.env.*` denied; `*.env.example` allowed)

---

## What "ask" offers

- `once` — approve just this request
- `always` — approve future requests matching the tool's suggested patterns for the rest of the current OpenCode session
- `reject` — deny the request

`opencode --auto` (or `opencode run --auto`) auto-approves requests that would
otherwise ask. Explicit `deny` rules are still enforced.

---

## External directory access

`external_directory` gates any tool that takes a path outside the working directory where OpenCode was started (for example `read`, `edit`, `glob`, `grep`, and many `bash` commands). An allowed directory inherits the workspace defaults, so reads there are allowed unless you add a rule. `~` or `$HOME` at the start of a pattern expands to the home directory (e.g. `~/projects/*` → `/Users/you/projects/*`).

To allow an agent to access files outside the project root:

```yaml
permission:
  external_directory:
    "~/projects/shared/**": allow
  edit:
    "~/projects/shared/**": deny  # read allowed but not edit
```

---

## Task permissions (subagent invocation)

Control which subagents this agent can invoke via the Task tool:

```yaml
permission:
  task:
    "*": deny                 # block all subagent invocation by default
    "orchestrator-*": allow   # allow agents matching this pattern
    "code-reviewer": ask      # ask before invoking this specific agent
```

- `deny`: the subagent is removed from the Task tool description; the model won't attempt to invoke it
- Users can always invoke subagents directly via `@mention` regardless of task permissions
- Rules evaluated in order; last match wins
- Subagents cannot launch further subagents at the default `subagent_depth` of `1`

---

## Merge behavior

Agent permissions are merged with global permissions; **agent rules take precedence**.

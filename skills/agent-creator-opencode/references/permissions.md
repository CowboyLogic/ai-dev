# OpenCode Agent Permission Reference

Deep reference for the `permission` key on OpenCode agents.

**Sources:** https://opencode.ai/docs/permissions/ · https://opencode.ai/docs/agents/

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
- Commands matched against full command string including arguments: `"git status"` matches `git status --porcelain`
- For commands with arguments, use `"git status *"` to also allow argument variants

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
| `edit` | File path being written/edited/patched |
| `glob` | Glob pattern being used |
| `grep` | Regex being searched |
| `list` | Directory listing (`list` tool) |
| `bash` | Full shell command string |
| `task` | Subagent name being invoked |
| `external_directory` | Paths outside the project working directory |
| `lsp` | LSP queries (non-granular) |
| `skill` | Skill name being loaded |
| `todowrite` | Gates `todowrite`/`todoread` (shorthand only) |
| `webfetch` | Gates the `webfetch` tool (shorthand only) |
| `websearch` | Gates the `websearch` tool (shorthand only) |
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

## External directory access

`external_directory` gates any tool that reads or writes paths outside the project working directory. `~` or `$HOME` at the start of a pattern expands to the home directory (e.g. `~/projects/*` → `/Users/you/projects/*`).

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

---

## Merge behavior

Agent permissions are merged with global permissions; **agent rules take precedence**.

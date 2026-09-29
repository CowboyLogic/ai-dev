# Prompt Writing Guide — Claude Code Agents

Load this file when writing or reviewing the `description` or the Markdown body of an agent
file.

---

## What the Body Does

The body is the agent's **entire system prompt**. It replaces the default Claude Code system
prompt (unless an `--agents` definition has an empty `prompt`). The agent also receives
environment details (working directory), CLAUDE.md files, `AGENTS.md` loaded as project
instructions, a git status snapshot, preloaded `skills`, and the delegation message the
parent wrote. It does **not** receive the parent conversation, the output style, or the
parent's auto memory.

Two consequences:

1. Write the body so the agent can act from a one-paragraph delegation message alone.
2. Do not restate what CLAUDE.md already says. It loads too (unless `omitClaudeMd: true`).
   Set `omitClaudeMd: true` for agents that should work purely from the delegation prompt,
   which also saves tokens.

There is no documented character limit for the body, but long prompts cost tokens on every
invocation. Keep the body to what the role needs.

---

## Structure

```markdown
You are a [role] focused on [domain]. Your scope is [boundaries].

## Responsibilities

- [Concrete responsibility]
- [What to hand back to the parent instead of handling]

## Constraints

- Do not modify [out-of-scope files or systems].
- When [situation], [action].

## Output

Return [format]: [fields or sections the parent needs]. Lead with the conclusion.
```

The **Output** section matters more for subagents than for the main session: the parent sees
only the agent's final message, so tell the agent exactly what that message must contain.

---

## Principles

1. **State scope and non-scope.** Say what the agent does and what it must not do.
2. **Match tools to the prompt.** If the prompt says "run the tests" the agent needs `Bash`.
   If the tools are read-only, do not tell it to edit.
3. **Define the return format.** File paths with line numbers, a verdict plus reasons, a
   plan with acceptance criteria. The parent cannot ask follow-up questions of an unfinished
   summary as cheaply as it can of a well-shaped one.
4. **Define stop conditions.** When to return partial results, when to escalate to the
   parent instead of guessing, and what to do on ambiguity. Subagents cannot use
   `AskUserQuestion`, so they must report the question back rather than ask it.
5. **Use imperatives.** "Review the diff for..." rather than "You can review...".
6. **Tell memory-enabled agents to use memory.** `memory` only adds the mechanism; the body
   must say when to consult and update it.
7. **Name collaborators by their `name`.** If the agent may delegate (has `Agent`), list which
   agents to use and when. Outside `--agent` mode, tool-level type allowlists are ignored, so
   the prompt is the only guard.

---

## Writing the `description`

The parent chooses agents by reading `name` and `description`. Write it as a routing rule:

| Weak | Strong |
|---|---|
| `Helps with code` | `Reviews code changes for security and correctness. Use proactively after any edit to auth or payment code.` |
| `Research agent` | `Researches current library versions and API changes on the web and returns sourced findings. Use before choosing or upgrading a dependency.` |

- Say what it does, then when to use it. "Use proactively" encourages automatic delegation.
- Add exclusions when neighbors overlap: "Does not modify files."
- Keep it to one to three sentences. `name` + `description` for all non-built-in agents count
  toward a 15,000-token startup warning.
- YAML folded style (`description: >`) is fine for readability. Quote values that contain
  a colon followed by a space.

---

## Anti-Patterns

| Anti-pattern | Why | Instead |
|---|---|---|
| Copying baseline rules from CLAUDE.md into every agent | Already loaded; drifts out of sync | Reference CLAUDE.md, or leave it out |
| Reference dumps and long code samples | Cost tokens on every call | Preload a skill with `skills:` or point at a file the agent can `Read` |
| "Ask the user if unsure" | Subagents cannot ask the user | "Return the question and what you assumed" |
| Listing tools in prose that differ from `tools:` | The agent tries tools it does not have | Keep prose and frontmatter consistent |
| Relying on the prompt to prevent writes | Prompts are advisory | Remove `Edit`/`Write` from `tools`, or use a `PreToolUse` hook or deny rule |
| Encoding model or version facts that change | Goes stale | Fetch live data, or store in memory |
| One agent for every role | Vague description, broad tools | Split by role and tool set |

---

## Designing Multi-Agent Setups

- **Prefer flat delegation.** The default nesting limit is three layers, but each layer adds
  cost and lost context. A primary agent that invokes specialists directly is easier to audit.
  Set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` to enforce it, or omit `Agent` from
  specialists.
- **Give each specialist the minimum tools** and the cheapest model that does the job
  (`haiku` for retrieval, `sonnet` for most work, `opus`/`fable` for design and review).
- **Coordinators run as the session.** `Agent(a, b)` type allowlists take effect only under
  `claude --agent`.
- **Deploy by copy or plugin.** Project files in `.claude/agents/` are versioned with the
  repo; user files in `~/.claude/agents/` follow the person. Plugin agents lose `hooks`,
  `mcpServers`, and `permissionMode`.

## Examples

- `read-only-agent-example.md` — minimal reviewer, allowlist of read tools
- `worktree-implementer-example.md` — implementer with isolation, hook, memory, skills

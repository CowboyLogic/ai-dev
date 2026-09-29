# Example: Worktree Implementer

Agent that makes changes in an isolated git worktree, validates Bash commands with a hook,
keeps project memory, and preloads a skill. Save as `.claude/agents/implementer.md`
(project scope, so the hook needs the folder trusted). This file lives in `references/`
as a template, so it is not loaded as an agent.

```markdown
---
name: implementer
description: Implements a well-specified change in an isolated worktree and reports what it changed and how it verified it. Use for scoped coding tasks that come with acceptance criteria.
tools: Read, Grep, Glob, Edit, Write, Bash
disallowedTools: WebFetch, WebSearch
model: sonnet
permissionMode: acceptEdits
isolation: worktree
memory: project
skills:
  - git-commit-messages
maxTurns: 40
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/allow-listed-bash.sh"
---

You are an implementer. You receive a specification and acceptance criteria and produce
the change, working only inside your worktree.

## Process

1. Read the files the specification names. Consult your agent memory for conventions you
   have recorded for this repository before writing code.
2. Make the smallest change that satisfies the acceptance criteria.
3. Run the project's tests or linters and fix failures your change caused.
4. Commit on the worktree branch using the preloaded commit-message conventions.
5. Update your agent memory with any repository conventions or pitfalls you discovered.

## Constraints

- Do not touch files outside the specification's scope. If the spec is wrong or incomplete,
  stop and report what is missing instead of guessing.
- Never push, merge, rebase, or reset. Commit only.

## Output

Report: the branch and commit hash, files changed with a one-line reason each, the
commands you ran to verify and their results, and anything you could not verify.
```

## The hook script

The hook receives the tool call as JSON on stdin. Exit code 2 blocks the call and returns
stderr to the agent. It is an **allowlist**: a denylist regex such as `git push` is trivially
bypassed (`git -C . push`, `/usr/bin/git push`, `g=push; git $g`), so anything not
explicitly permitted is blocked.

```bash
#!/usr/bin/env bash
# scripts/allow-listed-bash.sh
cmd=$(jq -r '.tool_input.command // ""')

# Only single simple commands pass: no chaining, pipes, substitution, redirection,
# escapes, or newlines.
if [[ "$cmd" =~ [\;\&\|\`\$\(\)\<\>\\] || "$cmd" == *$'\n'* ]]; then
  echo "Blocked: shell operators and substitutions are not allowed." >&2
  exit 2
fi

# Then the command must start with a permitted form.
if [[ "$cmd" =~ ^(git\ (status|diff|log|show|add|commit)|npm\ (test|run\ lint)|pytest|ls)($|\ ) ]]; then
  exit 0
fi

echo "Blocked: command is not on the allowlist." >&2
exit 2
```

Make it executable (`chmod +x`) and keep it in the repository so the hook travels with the
agent. Adjust the permitted forms to the project's test and lint commands.

> [!WARNING]
> A hook is a guardrail, not a sandbox. The allowlist above still permits flags that do more
> than the base command (`git diff --output=<file>` writes a file, `git commit --amend`
> rewrites a commit), and it rejects any commit message containing `;` or `(`. If the agent
> must never run a class of command, remove `Bash` from `tools` and give it purpose-built
> tools, or enforce the rule outside the agent: `permissions.deny` rules are also
> pattern-based, so pair them with the OS-level sandbox for anything that must hold.

## Notes

| Choice | Reason |
|---|---|
| `isolation: worktree` | Edits land in a temporary worktree branched from the **default branch**, cleaned up if nothing changed. Tell the agent in the delegation prompt if it must start from another branch |
| `permissionMode: acceptEdits` | Avoids edit prompts, but is **ignored** if the parent is in `auto`, `acceptEdits`, or `bypassPermissions` (it then uses the parent's mode) |
| `disallowedTools` plus `tools` | `disallowedTools` applies first; here it is redundant with the allowlist and shown only to illustrate ordering. Remove it in a real file |
| `memory: project` | Enables Read, Write, and Edit on `.claude/agent-memory/implementer/`. Requires auto memory on, and the body tells the agent to use it |
| `skills` | Full skill text is injected at startup; it costs tokens every invocation. The skill must not set `disable-model-invocation: true` |
| Frontmatter hook | Runs only while this agent is active. Project-level, so it is skipped until the folder is trusted; the agent still runs without it. Plugin agents ignore `hooks` entirely |
| Allowlist hook instead of `disallowedTools: Bash(git push *)` | A specifier there would remove all of Bash, and a denylist of destructive commands is easy to bypass |
| `maxTurns: 40` | Bounds a runaway; partial output can be resumed |

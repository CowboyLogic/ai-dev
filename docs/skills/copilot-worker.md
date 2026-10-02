# Copilot Worker

Run GitHub Copilot CLI as a worker from Claude Code. Claude Code plans the work, hands
a bounded research, review, or implementation task to Copilot, and verifies the result
itself. The bulk work is billed to the Copilot subscription instead of Claude tokens.

- **Skill name:** `copilot-worker`
- **Last updated:** 2026-10-01
- **Source:** [skills/copilot-worker](https://github.com/CowboyLogic/ai-dev/tree/main/skills/copilot-worker)

---

## What it does

- **Three kinds of task.** Research and review run read-only in the current checkout.
  Implementation runs in a throwaway Git worktree on its own branch.
- **No server.** Each delegation is a separate background process, so there is nothing
  to install beyond the skill and no client time limit on a run.
- **Evidence for every run.** Each run leaves its task, the worker's final message,
  usage, and a result record for the parent agent to check.
- **A model per task type.** Each mode has a default model, which can be overridden
  for a single run.

## Where it applies

Use it when Claude Code is the planning and verifying agent and you want
implementation, reconnaissance, or an independent review done on Copilot capacity.

> [!WARNING]
> An implementation worker has full shell access apart from a short deny list. The
> worktree isolates the worker's normal edits. It is not a sandbox: a shell command can
> still reach files outside it, including your live checkout.

It requires GitHub Copilot CLI 1.0.89 or later, Git, Python 3.9 or later, and macOS
or Linux.

---

## Install

```bash
# Install globally for Claude Code
npx skills add CowboyLogic/ai-dev --skill copilot-worker --agent claude-code -g

# Preview what would be installed without installing
npx skills add CowboyLogic/ai-dev --skill copilot-worker -g -l
```

### Verify installation

```bash
npx skills ls -g --agent claude-code
```

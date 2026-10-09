# Copilot Worker

Run GitHub Copilot as a worker from Claude Code. Claude Code plans the work, hands
a bounded research, review, or implementation task to Copilot, and verifies the result
itself. The bulk work is billed to the Copilot subscription instead of Claude tokens.

- **Skill name:** `copilot-worker`
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
- **Built on the Copilot SDK.** It drives Copilot through the official SDK, which pins
  its own runtime, so command-line tool updates cannot break it.
- **Pinned versions.** The SDK, its runtime, and every package it needs are pinned to
  exact versions, and the worker refuses to start if the installed ones differ. Upgrading
  is a deliberate change with a documented procedure, linked from the skill's README.
- **Every permission request checked.** File access is confined to the workspace, a
  deny list rejects pushes and the GitHub CLI in their common forms, and neither your
  Copilot hooks nor the repository's run inside a worker.

## Where it applies

Use it when Claude Code is the planning and verifying agent and you want
implementation, reconnaissance, or an independent review done on Copilot capacity.

> [!WARNING]
> An implementation worker has full shell access apart from a short deny list. The
> worktree isolates the worker's normal edits. It is not a sandbox: a shell command can
> still reach files outside it, including your live checkout.

It requires `uv`, a GitHub Copilot login, and Git, on macOS, Linux, or Windows. `uv`
provides Python 3.11 or later and the SDK on first run. On Windows an implementation
worker's shell is PowerShell, and the deny list checks PowerShell and `cmd.exe` commands
as well as POSIX ones.

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

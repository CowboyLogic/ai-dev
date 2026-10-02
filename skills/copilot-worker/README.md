# Copilot Worker

A skill that lets Claude Code run GitHub Copilot CLI as a worker. Claude Code plans the
work, hands a bounded task to Copilot, and verifies the result. The bulk work is billed
to the Copilot subscription instead of Claude tokens.

## What it does

- **Research** and **review** run read-only in the current checkout.
- **Implementation** runs in a throwaway Git worktree on its own branch, which keeps the
  worker's edits off the branch you are on.
- Each run is a separate process that Claude Code starts in the background. There is no
  server to install and no time limit imposed by the client.
- Each run leaves a directory with the task, the worker's final message, usage, and a
  `result.json`.

## Requirements

- GitHub Copilot CLI 1.0.89 or later, authenticated (`copilot login`)
- Git
- Python 3.9 or later
- macOS or Linux

## Install

```bash
npx skills add CowboyLogic/ai-dev --skill copilot-worker --agent claude-code -g
```

## Check the setup

From inside a Git repository:

```bash
python3 ~/.claude/skills/copilot-worker/scripts/copilot_worker.py check --live
```

`check` confirms the binary and repository. `--live` also sends one small prompt to each
default model, which uses Copilot credits.

## Models

| Mode | Default model |
| --- | --- |
| `research` | `gpt-6-luna` |
| `review` | `gpt-6.1-sol` |
| `implement` | `gpt-6.1-sol` |

The defaults are the `DEFAULT_MODELS` constant in
[scripts/copilot_worker.py](scripts/copilot_worker.py). Change them there, or pass
`--model` for one run.

## Safety

> [!WARNING]
> An implementation worker has full shell access apart from a short deny list
> (`git push`, `git remote`, `git worktree`, `gh`, `sudo`). The worktree isolates the
> worker's normal edits. It is not a sandbox: a shell command can still reach files
> outside it, including your live checkout.

See [SKILL.md](SKILL.md) for the full workflow and limits.

## Tests

```bash
python -m unittest skills/copilot-worker/scripts/test_copilot_worker.py
```

The tests use a fake `copilot` binary and spend no credits.

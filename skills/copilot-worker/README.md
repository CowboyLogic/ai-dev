# Copilot Worker

A skill that lets Claude Code run GitHub Copilot as a worker. Claude Code plans the
work, hands a bounded task to Copilot, and verifies the result. The bulk work is billed
to the Copilot subscription instead of Claude tokens.

## What it does

- **Research** and **review** run read-only in the current checkout.
- **Implementation** runs in a throwaway Git worktree on its own branch, which keeps the
  worker's edits off the branch you are on.
- Each run is a separate process that Claude Code starts in the background. There is no
  server to install and no time limit imposed by the client.
- Each run leaves a directory with the task, the worker's final message, usage, a log of
  every tool call it asked for, and a `result.json`.
- It drives Copilot through the official GitHub Copilot SDK, which pins its own Copilot
  runtime. Updates to the `copilot` command-line tool cannot break it.
- The script decides every tool call itself: workers can only read and write inside their
  workspace, and a deny list blocks `git push`, `gh`, and similar commands.

## Requirements

- [`uv`](https://docs.astral.sh/uv/). It installs Python 3.11 or later and the pinned
  `github-copilot-sdk` from the script's header on first run.
- A GitHub Copilot login on the machine (`copilot login`, once)
- Git
- macOS or Linux

The first run downloads the Copilot runtime the SDK pins, into the SDK's cache.

## Install

```bash
npx skills add CowboyLogic/ai-dev --skill copilot-worker --agent claude-code -g
```

## Check the setup

From inside a Git repository:

```bash
uv run ~/.claude/skills/copilot-worker/scripts/copilot_worker.py check --live
```

`check` confirms the SDK, its runtime version, and the repository. `--live` also sends one small prompt to each
default model, which uses Copilot credits.

## Make delegation reliable

A skill description is only a hint, and an agent's standing guidance to do small jobs
itself usually wins over it. If you want delegation to happen consistently in a
repository, add a line like this to that repository's `CLAUDE.md` or `AGENTS.md`, which
is in context on every turn:

```markdown
Codebase research, code review, and implementation that touches more than a file or two
go through the `copilot-worker` skill. Load it before reading three or more files.
```

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
> (`git push`, `git remote`, `git worktree`, `gh`, `sudo`), and its file tools are
> confined to its workspace. The worktree isolates the
> worker's normal edits. It is not a sandbox: a shell command can still reach files
> outside it, including your live checkout.

See [SKILL.md](SKILL.md) for the full workflow and limits.

## Tests

```bash
python -m unittest skills/copilot-worker/scripts/test_copilot_worker.py
python -m unittest skills/copilot-worker/scripts/test_worker_engine.py
```

The tests need Python 3.11 or later but not the SDK. They use a fake engine and spend no
credits.

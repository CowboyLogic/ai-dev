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
- The script decides every permission request itself: workers can only read and write
  inside their workspace, and a deny list rejects `git push`, `gh`, and similar commands
  in their common forms. Neither your Copilot hooks nor the repository's run inside it.

## Requirements

- [`uv`](https://docs.astral.sh/uv/). It installs Python 3.11 or later and the pinned
  `github-copilot-sdk` from the script's header on first run.
- A GitHub Copilot login on the machine. Signing in once with the Copilot CLI
  (`copilot login`) is enough; the worker reuses that login.
- Git
- macOS or Linux

> [!WARNING]
> Windows is not supported, including Git Bash. The supervisor uses POSIX process groups
> and signals that do not exist in Windows Python, and `implement` mode's shell policy
> assumes a POSIX shell. WSL has not been tested.

The first run downloads the Copilot runtime the SDK pins, into the SDK's cache.

The SDK, the runtime it carries, and every package it needs are pinned to exact
versions (`scripts/pins.json` and the header of `scripts/copilot_worker.py`). The worker
refuses to start when the installed versions differ, and `check` reports it. Upgrading is a
deliberate change; [references/upgrading.md](references/upgrading.md) has the procedure.

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
> confined to its workspace. The deny list catches common forms of those commands, not
> code passed to an interpreter. The worktree isolates the
> worker's normal edits. It is not a sandbox: a shell command can still reach files
> outside it, including your live checkout.

See [SKILL.md](SKILL.md) for the full workflow and limits.

## Tests

From the repository root:

```bash
python -m unittest discover -s skills/copilot-worker/scripts -v
```

The unit tests need Python 3.11 or later but not the SDK. They use a fake engine and spend
no credits. `test_sdk_contract.py` checks the installed SDK against the pinned versions and
the names the engine uses, so it needs the SDK: without it those tests skip, and with
`REQUIRE_SDK_CONTRACT=1` they fail instead. CI sets that variable. To run them in the
environment the script header pins, follow step 4 of
[references/upgrading.md](references/upgrading.md).

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
- It drives Copilot through the official Microsoft Copilot SDK, which pins its own Copilot
  runtime. Updates to the `copilot` command-line tool cannot break it.
- The script decides every permission request itself: workers can only read and write
  inside their workspace, and a deny list rejects `git push`, `gh`, and similar commands
  in their common forms. Neither your Copilot hooks nor the repository's run inside it.

## Requirements

- [`uv`](https://docs.astral.sh/uv/). It installs Python 3.11 or later and the pinned
  `microsoft-copilot-sdk` from the script's header on first run.
- A GitHub Copilot login available to the worker. A keychain-backed Copilot CLI
  login may already be available. If the worker reports that it is signed out,
  [sign in using the worker's Copilot home](#sign-in-if-the-worker-is-signed-out).
- Git
- macOS, Linux, or Windows (x64 or ARM64). Inside WSL it runs as it does on Linux.

On Windows the worker runs inside a job object, so ending a run ends every process it
started. An `implement` worker's shell is PowerShell (`pwsh` when it is installed,
otherwise Windows PowerShell), and the deny list reads PowerShell and `cmd.exe` syntax
as well as POSIX shell syntax.

The first run downloads the Copilot runtime the SDK pins, into the SDK's cache.

The SDK, the runtime it carries, and every package it needs are pinned to exact
versions (`scripts/pins.json` and the header of `scripts/copilot_worker.py`). The current
SDK/runtime pair is **2.0.1 / 1.0.114**. The worker
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

`check` confirms the SDK, its runtime version, and the repository. `--live` also checks that the model catalog offers each profile's model and effort, then sends one small prompt
to each of the four profiles, which uses Copilot credits.

## Sign in if the worker is signed out

The worker uses an isolated Copilot home, so it doesn't load the regular CLI's
hooks, skills or MCP configuration. GitHub Copilot CLI normally stores credentials
in your operating system keychain. If the keychain is unavailable, its
[file-backed login](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#copilot-login)
is stored in the CLI's selected configuration directory. Signing in to the default
CLI home does not put those credentials in the worker's home.

Run `check --live` as shown above to initialize the private worker directory and
see the exact path if sign-in is needed. Then run the regular interactive CLI's
`copilot login` from your own terminal with `COPILOT_HOME` set just for the login.
Use the same absolute `COPILOT_WORKER_HOME` as the worker if you configured one.

macOS, Linux or Git Bash:

```bash
COPILOT_HOME="${COPILOT_WORKER_HOME:-$HOME/.copilot-worker}/copilot-home" copilot login
```

Windows PowerShell:

```powershell
$workerState = if ($env:COPILOT_WORKER_HOME) { $env:COPILOT_WORKER_HOME } else { Join-Path $HOME '.copilot-worker' }
$previousCopilotHome = $env:COPILOT_HOME
try {
    $env:COPILOT_HOME = Join-Path $workerState 'copilot-home'
    copilot login
} finally {
    $env:COPILOT_HOME = $previousCopilotHome
}
```

Complete the CLI's sign-in prompts yourself and rerun the check. The worker never
initiates login or copies credentials or settings from your regular Copilot home.

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

Each run uses a profile, which fixes one model and one reasoning effort:

| Profile | Model | Effort |
| --- | --- | --- |
| `light` | `gpt-6-luna` | `medium` |
| `standard` | `gpt-6.1-terra` | `medium` |
| `deep` | `gpt-6.1-sol` | `medium` |
| `heavy` | `gpt-6-astra` | `medium` |

| Mode | Default profile |
| --- | --- |
| `research` | `light` |
| `review` | `deep` |
| `implement` | `standard` |

`review` defaults to a different model from `implement`, so worker-written code is not
reviewed by the model that wrote it. A run off its mode's default needs a `--reason`,
which `result.json` records, and a run that fails verification can be retried one
profile up, at most twice. Effort is capped at `xhigh`.

The profiles and defaults are the `PROFILES` and `DEFAULT_PROFILES` constants in
[scripts/copilot_worker.py](scripts/copilot_worker.py). `check --live` confirms that the
model catalog offers each profile's model and effort before it probes them.

## Safety

> [!WARNING]
> An implementation worker has full shell access apart from a short deny list
> (`git push`, `git remote`, `git worktree`, `gh`, `sudo`, `runas`), and its file tools are
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

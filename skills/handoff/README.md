# Handoff

Carry task state from one Claude Code session to the next without carrying the whole
transcript. `/handoff` writes a short, curated file, and a `SessionStart` hook loads it
into the next session.

Starting fresh is cheaper than continuing a long session, because every turn re-reads the
whole history. A fresh session knows nothing about where the last one stopped, though. This
skill closes that gap with a small file you can read and edit before it is used.

## What's included

- **`SKILL.md`**: the `/handoff` command. It runs only when you invoke it
  (`disable-model-invocation: true`), so its description never loads into a session.
- **`scripts/session-start.sh`**: the hook script that prints the handoff into a new
  session. Plain bash, no `jq`.

## How it works

1. **You run `/handoff`.** The agent checks that `.agent-output/handoff.md` is git-ignored,
   then overwrites that file with task state: goal and current state, decisions with their
   reasons, gotchas and dead ends, the exact next step, in-flight work, and open questions.
   It holds about 100 lines at most and leaves out anything a fresh session can derive from
   `git log` or the code.
2. **You review the file**, then `/clear` or start a new session.
3. **The hook prints the file** at session start, framed as written by a previous session
   and possibly stale. It notes when the recorded branch differs from the current one.

### Ignore check

A handoff can hold proprietary context, so the skill never writes it to a path git would
stage. If `.agent-output/` is not ignored, the skill asks you to choose, and writes nothing
until you answer:

- **A.** Add `.agent-output/` to the repository's `.gitignore`. This is a tracked change
  that every contributor receives.
- **B.** Add it to the local `info/exclude` file. This is untracked and applies to this
  clone only.

Outside a git repository there is nothing to ignore, and the file is written directly.

### One effort at a time

There is a single file, so it belongs to one effort at a time. Two parallel sessions on
different work in the same checkout overwrite each other's handoff. Use separate checkouts
or worktrees for parallel efforts.

### Stale handoffs

The hook skips a handoff older than 7 days and prints nothing. Set
`HANDOFF_MAX_AGE_DAYS` to change the limit, or to `0` to disable it. The printed block also
tells the agent to confirm the handoff still applies before acting on it.

## Install

Install the skill:

```bash
npx skills add CowboyLogic/ai-dev --skill handoff -g
```

Then register the hook in `~/.claude/settings.json`, or in `.claude/settings.json` to scope
it to one project. The command runs the script through `bash`, so a lost executable bit
does not matter. Adjust the path if your install put the skill elsewhere.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/skills/handoff/scripts/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

For a project-scoped install, use
`bash "$CLAUDE_PROJECT_DIR/.claude/skills/handoff/scripts/session-start.sh"` as the command.

The matcher leaves out `resume`, because a resumed session already has its context, and
`fork`, for the same reason. The script also reads `source` from the hook's input and skips
both, so a broader matcher still behaves.

## Verify

Check that the script runs, without starting a session:

```bash
printf '{"source":"startup"}' | bash ~/.claude/skills/handoff/scripts/session-start.sh
```

With no handoff file it prints nothing. After `/handoff` has written one, it prints the
file inside a "Handoff from a previous session" block. Run `/hooks` in Claude Code to
confirm the `SessionStart` entry is registered.

## Size

The hook adds the handoff, plus a four-line frame, to the start of every session it fires
in. The cost is the size of the file:

| Handoff | Lines | Characters | Tokens (estimate) |
|---|---|---|---|
| Sample covering this skill's own build | 45 | 1,734 | about 430 |
| Upper bound (100 lines at the same density) | 100 | about 3,900 | about 1,000 |

> [!NOTE]
> The token figures are estimates (characters divided by four), not measurements. Replace
> them with a measured figure from `/context` in a real session before quoting them
> elsewhere.

The hook prints at most 150 lines and says so when it truncates.

## Limits

- Claude Code only. The hook registration and `disable-model-invocation` are Claude Code
  features. Other harnesses are not covered.
- The script is written in portable shell and was tested under bash 5.2 and dash. It has
  not been run on macOS bash 3.2 or Git Bash on Windows.
- The handoff is only as good as the agent's summary. Read it before relying on it.

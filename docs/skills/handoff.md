# Handoff

Carry task state from one Claude Code session to the next. `/handoff` writes a short,
curated file of what is half done and what comes next, and a `SessionStart` hook loads it
into the next session, so a fresh session starts with context instead of a long transcript.

- **Skill name:** `handoff`
- **Source:** [skills/handoff](https://github.com/CowboyLogic/ai-dev/tree/main/skills/handoff)

---

## What it does

The skill is invoked only by you, never by the model. It checks that the handoff file is
git-ignored, asks how to ignore it if not, and then writes a size-capped file of task state:
the goal, decisions and their reasons, dead ends, the exact next step, and open questions.
The hook script prints that file at the start of the next session, labelled as possibly
stale.

## Where it applies

Use it for work that outlasts one session, in Claude Code. It does not replace the memory
feature, which is for durable facts, or compaction, which keeps one session running.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill handoff -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill handoff --agent <agent> -g
```

### Register the hook

Add the hook to `~/.claude/settings.json`, or to `.claude/settings.json` for one project:

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

### Verify installation

```bash
npx skills ls -g
```

Then run `/hooks` in Claude Code to confirm the `SessionStart` entry is registered. See the
[skill README](https://github.com/CowboyLogic/ai-dev/blob/main/skills/handoff/README.md) for
the ignore check, the stale-handoff cutoff, and the limits.

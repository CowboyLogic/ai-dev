# about-me

A template skill for carrying **durable personal context** into every agent session —
who you are, how you work, and where the line sits between an agent deciding and an
agent asking.

It ships as a template. On first load, an agent notices it has not been customized and
walks you through filling it in.

---

## Why this exists

Agents calibrate constantly — how much to explain, when to ask versus decide, how
formal to be. With no context they calibrate to a generic average, which fits almost
nobody and fails invisibly: the output looks reasonable and quietly does not fit how
you work.

The [Lane Topology](../../agents/lane-topology/README.md) makes this explicit — its
Conductor loads `about-me` as step one of every session, before classifying a single
request, because the first response is the one most likely to be miscalibrated without
it.

---

## Installing it

Copy the skill into your global skills directory so every project sees it:

```bash
# Claude Code
cp -r skills/about-me ~/.claude/skills/about-me

# OpenCode discovers skills from ~/.agents/skills
cp -r skills/about-me ~/.agents/skills/about-me
```

If you use both, keep one real copy and symlink the other so they cannot drift:

```bash
cp -r skills/about-me ~/.claude/skills/about-me
ln -s ~/.claude/skills/about-me ~/.agents/skills/about-me
```

Then start a session and say `customize my about-me skill`. The agent reads the
template, sees it is unfilled, and runs the interview.

---

## Keeping it private

**Your filled-in copy is personal context. Do not commit it.**

The template in this repository is generic on purpose — it contains no one's actual
profile. Once you customize your installed copy it holds real information about you,
your employer, and your constraints. It lives in your home directory rather than in a
project precisely so it does not end up in a repository by accident.

If you want it version-controlled, use a private repository, and check first whether
anything in it would be a problem in a leak.

---

## What belongs in it

| Include | Leave out |
|---|---|
| Preferences with a reason attached | Bare preferences with no *why* |
| Where you want autonomy, and where you do not | Anything the repo's `AGENTS.md` already states |
| Corrections you have had to repeat | Facts about a single task or session |
| Hard constraints — budget, compliance, stack | Credentials, tokens, or secrets of any kind |
| Expertise to assume, and gaps to explain around | Anything you would not want read aloud |

Aim for 40–80 lines. A long profile is worse than a short one — every line competes
for attention with every other line, and the whole file is re-read every session.

**The maintenance rule:** if you catch yourself giving an agent the same correction
twice, that is a line missing from this file.

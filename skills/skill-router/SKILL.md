---
name: skill-router
description: Find an installed skill in the skill library, a folder of skills kept outside the harness's discovery path so their descriptions do not load into every session. Search it BEFORE starting a task that a specialized skill could cover and that no skill already listed in this session fits, and whenever the user names a skill you cannot see or asks what skills are installed. Returns the skill's directory so you can read and follow it.
license: MIT
---

# Skill Router

The skills listed in this session are not all the skills installed. Most live in a
library that the harness does not scan, so that their descriptions cost nothing until
one is needed. Search the library, then load the one skill that fits.

The script is `scripts/skill_router.py` in this skill's directory. It is
standard-library Python. Use `python` where `python3` is not the command name.

## 1. Search

```bash
python3 <this-skill-dir>/scripts/skill_router.py search <words describing the task>
```

Describe the task with the words a skill author would use: the tool, the file type, the
kind of work. `search terraform module review` works better than
`search check my infrastructure code`.

Each result gives a name, a directory, and the start of the description:

```text
1. terraform-module-review
   dir:  /home/me/.skill-library/work-skills/skills/terraform-module-review
   desc: Review a Terraform module for drift, unsafe defaults, and ...
```

Search is by keyword, so a miss can mean the wrong words and not a missing skill. If
nothing fits, search **once more** with different words, such as a synonym, the tool's
name, or a broader term. Two misses mean the library has no skill for this.

Add `--json` for full descriptions when the shortened ones are not enough to choose.

## 2. Load the skill

Pick the result whose description fits the task. If none fits, load none: a poor match
costs more than it saves.

1. Read `SKILL.md` in the result's `dir` and follow it as you would any skill.
2. Treat `dir` as that skill's base directory. Every relative path the skill mentions,
   such as `references/guide.md` or `scripts/run.py`, resolves against `dir`, not against
   your working directory.
3. Run the skill's scripts by their full path under `dir`. Do not change your working
   directory to do it, and do not copy the skill into the workspace.

A result can carry a `note:` line naming text such as `$ARGUMENTS` that a harness fills
in when it loads a skill itself. Here it stays literal. Substitute it yourself:
`$ARGUMENTS` is what the user asked for, and a skill-directory variable is `dir`.

## 3. When nothing fits

Tell the user the library has no skill for the task and carry on without one. Do not
install a skill from a remote source on your own. Adding to the library is the user's
decision.

## Other commands

- `index` refreshes the index and reports on the library: the skill count, skills with
  no description, names used twice, and skills that use harness-only variables. `search`
  refreshes the index itself, so this is for inspection, not a required step.
- `topics` prints the words most common across skill names. `topics --write` puts them at
  the end of this skill's own description, which tells a future session what the library
  covers. Run it only when the user asks.

The library is `~/.skill-library` unless `SKILL_ROUTER_LIBRARY` or `--library <path>`
names another directory.

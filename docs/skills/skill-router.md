# Skill Router

Keep hundreds of skills installed without loading every description into every session.
The skills live in a library directory that no harness scans, and the router is the one
skill the agent sees: it searches the library and hands back the directory of the skill
that fits. It also installs skills into the library, once you approve their source, and
updates and removes them.

- **Skill name:** `skill-router`
- **Source:** [skills/skill-router](https://github.com/CowboyLogic/ai-dev/tree/main/skills/skill-router)

---

## What it does

A harness loads the name and description of every skill it discovers at the start of every
session, and that cost grows with the number of skills. The router replaces those
descriptions with one. When a task might have a skill, the agent runs the router's search
script, which ranks the library by keyword and returns the best matches. The agent then
reads the chosen skill from where it lives, so skills with their own reference files and
scripts keep working. On a miss the agent searches once more, then looks on GitHub through
the GitHub CLI and shows you what it finds. It never installs a skill on its own.

The router also looks after the library. It installs a skill from GitHub into it through
the GitHub CLI, and asks you first whether you trust the source: that one skill, its whole
repository, or its owner. It remembers the answer, including a refusal. It updates
installed skills on request, removes them, and holds back any skill that turns up in the
library without an approval until you have reviewed it.

## Where it applies

Use it when you keep a large library of skills installed globally and most sessions use
few of them. As a rough guide, it earns its place at 50 or more skills; with fewer than
about 50 that you rely on routinely, it may not give you the value it is built for. A skill
you use in every session is better left where the harness discovers it.

It works in any harness that can run a Python script and read files outside the project.
Finding skills on GitHub, installing, and updating need the GitHub CLI (`gh`) with its
`gh skill` commands; searching the library does not.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill skill-router -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill skill-router --agent <agent> -g
```

### Fill the library

The router is the only skill to install where your harness discovers skills. Install the
rest into the library with the router itself, which creates `~/.skill-library` on first
use:

```bash
uv run <skill-dir>/scripts/skill_router.py install <owner>/<repo> <skill>
```

Do not use an installer that can only write to a harness's skill directories: a skill
placed there loads into every session. Skills you already have can be moved into the
library by hand, and a clone of a skill repository works as it is. The library is a plain
folder and does not need to be a git repository.

Set `SKILL_ROUTER_LIBRARY` to use a different directory.

### Verify installation

```bash
npx skills ls -g
uv run <skill-dir>/scripts/skill_router.py index
```

Replace `<skill-dir>` with where your harness installed the skill, such as
`~/.claude/skills/skill-router` for a global Claude Code install. The second command
prints how many skills the library holds. See the
[skill README](https://github.com/CowboyLogic/ai-dev/blob/main/skills/skill-router/README.md)
for the permission setup, the commands, how approval and updates work, how search ranks
results, and the limits.

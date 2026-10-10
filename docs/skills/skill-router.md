# Skill Router

Keep hundreds of skills installed without loading every description into every session.
The skills live in a library directory that no harness scans, and the router is the one
skill the agent sees: it searches the library and hands back the directory of the skill
that fits.

- **Skill name:** `skill-router`
- **Source:** [skills/skill-router](https://github.com/CowboyLogic/ai-dev/tree/main/skills/skill-router)

---

## What it does

A harness loads the name and description of every skill it discovers at the start of every
session, and that cost grows with the number of skills. The router replaces those
descriptions with one. When a task might have a skill, the agent runs the router's search
script, which ranks the library by keyword and returns the best matches. The agent then
reads the chosen skill from where it lives, so skills with their own reference files and
scripts keep working. On a miss the agent searches once more, then reports that nothing is
installed. It never installs a skill on its own.

## Where it applies

Use it when you keep many skills installed globally and most sessions use few of them. It
works in any harness that can run a Python script and read files outside the project. It
is not worth the indirection for a handful of skills, and a skill you use in every session
is better left where the harness discovers it.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill skill-router -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill skill-router --agent <agent> -g
```

### Create the library

```bash
mkdir -p ~/.skill-library
git clone https://github.com/<owner>/<skills-repo> ~/.skill-library/<skills-repo>
```

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
for the permission setup, the commands, how search ranks results, and the limits.

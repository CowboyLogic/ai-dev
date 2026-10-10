# Skill Router

Keep a large set of skills installed without loading every description into every
session. The skills live in a library directory that no harness scans, and this one skill
finds the right one on request.

A harness loads the name and description of every skill it discovers, at the start of
every session. That is cheap for a dozen skills and expensive for hundreds: 200 skills
with descriptions near the 1,024-character limit come to about 51,000 tokens before the
first prompt (an estimate, at four characters per token). With the router, a session
carries one description and pays for a search only when it needs a skill.

## What's included

- **`SKILL.md`**: tells the agent when to search the library and how to load a result.
- **`scripts/skill_router.py`**: the search script. Standard-library Python 3.9 or later,
  with no dependencies, on macOS, Linux, and Windows.
- **`scripts/test_skill_router.py`**: its unit tests.

## How it works

1. **The agent searches.** It runs `skill_router.py search <words>` when a task might have
   a skill and none of the skills it can see fits.
2. **The script ranks the library.** It scores each skill's name and description against
   the query and prints the best five: name, directory, and the start of the description.
3. **The agent loads one skill.** It reads `SKILL.md` in the returned directory and treats
   that directory as the skill's base, so the skill's `references/` and `scripts/` paths
   resolve where the skill lives. Nothing is copied into the workspace.
4. **On a miss, the agent searches once more** with different words, then tells you the
   library has nothing for the task. It does not install anything on its own.

## Set up

Install the skill where your harness discovers skills:

```bash
npx skills add CowboyLogic/ai-dev --skill skill-router -g
```

Create the library and put skills in it. A skill is any directory that holds a `SKILL.md`,
at any depth, so a clone of a skill repository works as it is:

```bash
mkdir -p ~/.skill-library
git clone https://github.com/<owner>/<skills-repo> ~/.skill-library/<skills-repo>
```

Update the library with `git pull` in each clone. There is no install step.

> [!IMPORTANT]
> Put skills in the library with `git clone` or a plain copy, not with a skill installer.
> Installers place skills where the harness discovers them, which is the cost this skill
> exists to avoid. For the same reason, remove library skills from your harness's own
> skill directories once they are in the library.

To keep the library somewhere else, set `SKILL_ROUTER_LIBRARY` to its path, or pass
`--library <path>` before the command.

The library is outside your project, so a harness may ask before reading from it or
running a script in it. Allow the library path once in your harness's permission
settings. In Claude Code, for example:

```json
{
  "permissions": {
    "allow": ["Read(~/.skill-library/**)"]
  }
}
```

## Commands

Run the script with `python3`, or `python` where that is the command name.

| Command | What it does |
|---|---|
| `search <words>` | Print the best matches. `-n <count>` changes how many, and `--json` prints full descriptions. |
| `index` | Refresh the index and report on the library. `--rebuild` discards the cached index first. |
| `topics` | Print the words most common across skill names. `--write` adds them to this skill's description. |

### Check the library

```bash
python3 ~/.claude/skills/skill-router/scripts/skill_router.py index
```

The report gives the skill count and lists three kinds of skill worth a look:

- **No description.** The skill can be found by name only.
- **A name used twice.** Both copies appear in results, told apart by directory.
- **Harness-only variables.** The skill uses text such as `$ARGUMENTS` that a harness
  substitutes when it loads the skill itself. Loaded through the router, the agent has to
  fill the value in, and a search result says so.

### Tell the agent what the library covers

An agent searches only when it suspects a skill exists. To give it a reason, add the
library's most common name words to this skill's own description:

```bash
python3 ~/.claude/skills/skill-router/scripts/skill_router.py topics --write
```

This appends a sentence such as `Library topics include terraform, review, docker.` to the
installed `SKILL.md`. Run it again after the library changes a lot, and after reinstalling
or updating this skill, which restores the shipped description. The command refuses to
write a description longer than 1,024 characters; lower `--max-chars` (default 300) if it
does.

## The index

The script keeps `.skill-router-index.json` at the top of the library: each skill's name,
description, and directory, plus the size and modification time of its `SKILL.md`. Every
command walks the library and re-reads only the `SKILL.md` files whose size or time
changed, so the index never needs a manual rebuild. If the library is read-only, the
script still works and re-reads every file each time.

If the library directory is itself a git clone, the index file shows up there as
untracked. Use a plain directory that holds your clones, or add the file to that clone's
`.git/info/exclude`.

## How search ranks

Search is by keyword, with BM25 scoring. A word in a skill's name counts three times as
much as a word in its description. Results that score under 35% of the best result are
dropped, so a skill that only mentions a query word in passing does not fill the list.

Keyword search does not know synonyms. A search for `k8s` does not find a skill that says
only `Kubernetes`. That is why the skill tells the agent to search a second time with
different words before it concludes nothing is installed.

## Limits

- An agent no longer sees library skills in its session, so it finds one only by searching.
  A skill you rely on in every session is better left where the harness discovers it.
- Library skills cannot be run as `/name` commands, and harness frontmatter such as
  Claude Code's `allowed-tools` or `disable-model-invocation` has no effect on them. The
  agent reads the skill as a file.
- The script reads the subset of YAML that skill frontmatter uses: plain, quoted, folded,
  and literal values. It does not read anchors or flow collections.
- The ranking was tuned against this repository's own skills, not a library of hundreds.
- Finding and installing skills from remote sources is not part of this skill.

## Test

```bash
python3 -m unittest discover -s skills/skill-router/scripts
```

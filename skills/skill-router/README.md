# Skill Router

Keep a large set of skills installed without loading every description into every
session. The skills live in a library directory that no harness scans, and this one skill
finds the right one on request. It also manages the library: it installs skills into it
after you approve their source, keeps them updated, and removes them.

A harness loads the name and description of every skill it discovers, at the start of
every session. That is cheap for a dozen skills and expensive for hundreds: 200 skills
with descriptions near the 1,024-character limit come to about 51,000 tokens before the
first prompt (an estimate, at four characters per token). With the router, a session
carries one description and pays for a search only when it needs a skill.

## What's included

- **`SKILL.md`**: tells the agent when to search the library and how to load a result.
- **`scripts/skill_router.py`**: the script to run. Standard-library Python 3.12 or later,
  with no dependencies, on macOS, Linux, and Windows.
- **`scripts/skill_library.py`**: the install, update, review, and remove commands, loaded
  by the script above. `install` and `update` call the GitHub CLI.
- **`scripts/test_skill_router.py`**, **`scripts/test_skill_library.py`**: the unit tests.

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

That is the only skill to install there. Every other skill goes into the library, with
the router's own `install` command:

```bash
uv run <skill-dir>/scripts/skill_router.py install <owner>/<repo> <skill>
```

The command creates the library on first use, shows you what it is about to install, and
asks whether you trust the source. [Manage the library](#manage-the-library) covers it.

> [!IMPORTANT]
> Install library skills with this command, or with `gh skill install --dir <library>`.
> Do not use an installer that cannot be pointed at a directory of your choosing. Most
> can only write to the places a harness discovers skills, and a skill installed there
> loads its description into every session, which is the cost this skill exists to avoid.
> For the same reason, remove a skill from your harness's own skill directories once it is
> in the library.

The library is a plain folder, `~/.skill-library` unless you say otherwise. It does not
need to be a git repository. A skill is any directory in it that holds a `SKILL.md`, at
any depth.

If you already have skills, move or copy them in before the first command: a library the
router has not seen before is accepted as it stands. A clone of a skill repository works
as it is, and you keep it current with `git pull`:

```bash
mkdir -p ~/.skill-library
git clone https://github.com/<owner>/<skills-repo> ~/.skill-library/<skills-repo>
```

A clone kept elsewhere can be linked in: a symlink placed directly in the library
directory is followed. Symlinks deeper than that are not, and a `SKILL.md` that is itself
a symlink is skipped with a message, so a link checked into a repository cannot lead the
search outside the library.

To keep the library somewhere else, set `SKILL_ROUTER_LIBRARY` to its path, or pass
`--library <path>` before the command.

The library is outside your project, so a harness may ask before reading from it or
running a script in it. These are two separate permissions in most harnesses.

Reading a skill's files is one. In Claude Code, for example, this rule lets the agent
load any library skill without a prompt:

```json
{
  "permissions": {
    "allow": ["Read(~/.skill-library/**)"]
  }
}
```

Running a script is the other, and a read rule does not cover it. That applies to the
router's own script and to any script a library skill ships. Approve those commands
when the harness asks, or add a narrowly scoped rule for them in your harness's
permission settings. Keep such a rule to `search` and `list`. Leave `install`, `review`,
and `remove` to be asked about each time: the harness's prompt is what puts their
approval in front of you and not only the agent.

## Commands

Run the script with `uv run`. The script's header declares that it needs Python 3.12 or
later, and [uv](https://docs.astral.sh/uv/) finds or fetches one, so the system Python does
not matter and no virtual environment is needed. Without `uv`, use a `python3` or `python`
that is 3.12 or later; an older one stops with a message saying so.

In the commands below, `<skill-dir>` is where your harness installed this skill, such as
`~/.claude/skills/skill-router` for a global Claude Code install.

| Command | What it does |
|---|---|
| `search <words>` | Print the best matches. `-n <count>` changes how many, and `--json` prints full descriptions. |
| `list` | Print the name of every skill in the library. |
| `index` | Refresh the index and report on the library. `--rebuild` discards the cached index first. |
| `topics` | Print the words most common across skill names. `--write` adds them to this skill's description. |
| `install <owner/repo> <skill>` | Install a skill from GitHub after you approve its source. `--all` takes every skill in the repository; `--pin <ref>` holds a version. |
| `update` | Update every library skill from its source. `--check` only reports. Name skills to limit it. |
| `review` | List skills that arrived without approval, and approve or delete them. |
| `remove <skill>` | Delete a skill from the library. |
| `status` | Show each skill's source, version, and approval. `--json` prints it as JSON. |

### Check the library

```bash
uv run <skill-dir>/scripts/skill_router.py index
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
uv run <skill-dir>/scripts/skill_router.py topics --write
```

This appends a sentence such as `Library topics include terraform, review, docker.` to the
installed `SKILL.md`. Run it again after the library changes a lot, and after reinstalling
or updating this skill, which restores the shipped description. The command refuses to
write a description longer than 1,024 characters; lower `--max-chars` (default 300) if it
does.

## Manage the library

`install` and `update` hand the fetching to the GitHub CLI's `gh skill` commands, pointed
at the library with `--dir`. You need `gh` on your `PATH`, signed in, and recent enough to
have `gh skill`. Search and the other commands work without it.

### Install, with approval

```bash
uv run <skill-dir>/scripts/skill_router.py install <owner>/<repo> <skill>
```

The skill is first downloaded to a temporary directory outside the library. The command
then shows where it came from, its version, and its files, with scripts marked, and asks
what you want to do:

- **Approve this skill.** Only this one. The right answer for an open-source repository
  with many contributors.
- **Approve the repository.** Every skill in it, now and later, installs without a
  question.
- **Approve the owner.** Every skill in every repository of that GitHub organization or
  account. Meant for an organization you belong to.
- **Deny.** Nothing is installed, and the skill is refused from then on, including as part
  of `--all`. `--reconsider` asks again.

A denial is always for one skill and beats a wider approval, so you can approve an
organization and still refuse one skill in it.

In a terminal the command prompts you. An agent's shell has no terminal, so there the
command stops with exit status 3 and the agent has to ask you, then run it again with
`--approved-by-user`, the scope you chose, and the tree value from the summary. If the
source changed in between, the tree no longer matches and nothing is installed.

> [!WARNING]
> The script cannot tell your approval from an agent that passes `--approved-by-user`
> without asking. The skill's instructions tell the agent to ask, and your harness's
> permission prompt shows you the command. Do not allowlist `install`.

Approval is asked once. It covers what the source serves later, so updates and reinstalls
ask nothing. To hold a skill at a version you have read, install it with `--pin <ref>`.

### The trust record

Decisions are kept in `.skill-router-trust.json` at the top of the library. It records
approvals and denials, not versions; each skill's version is in the `metadata` block that
`gh` writes into its `SKILL.md`.

The first command run on a library that has no trust record accepts every skill already
in it and says so. After that, a skill that turns up without an approval is left out of
search results until you review it:

```bash
uv run <skill-dir>/scripts/skill_router.py review
```

`review` lists those skills. For each, the question is whether you put it there.
`--approve <skill>` and `--approve-all` accept them. `--approve-dir <dir>` accepts
everything under one directory of the library, including skills that arrive there later,
which suits a clone you update with `git pull`. `--delete <skill>` removes the folder of
a skill you did not put there, and denies it if its source is known.

Two things to know about this file:

- Deleting it starts over: everything then in the library is accepted, and every denial
  is forgotten.
- It protects you from surprises, not from code already running as you. Anything that can
  write to the library can also write this file.

### Update

```bash
uv run <skill-dir>/scripts/skill_router.py update --check
uv run <skill-dir>/scripts/skill_router.py update
```

`update --check` reports which skills have a newer version at their source. `update`
applies them. Run it whenever you like; nothing does it for you. Pinned skills are
skipped, and so are skills with no recorded source, such as hand-copied ones and those in
a clone, which you update with `git pull`.

### Remove

```bash
uv run <skill-dir>/scripts/skill_router.py remove <skill>
```

This deletes the skill's folder, after a yes. Its approval stays on record, so installing
it again asks nothing. A skill linked into the library is unlinked, and the files the link
points at are left alone.

## The index

The script keeps `.skill-router-index.json` at the top of the library: each skill's name,
description, directory, and recorded source, plus the size, modification time, and change time of its
`SKILL.md`. Every command walks the library and re-reads only the `SKILL.md` files where
one of those differs, so the index does not need a rebuild in normal use. If the library
is read-only, the script still works and re-reads every file each time.

The change time moves when a file's content or permissions change, so a replaced file is
read again even if its size and modification time were kept, and a skill that has become
unreadable is dropped. Windows reports a file's creation time in that field, so there an
edit that keeps both the size and the modification time is not seen. Run
`index --rebuild` after an update like that.

A cached record that is incomplete or of the wrong shape is discarded and read again from
its `SKILL.md`, and an index file that is damaged is written again. The index is written to a uniquely named temporary file and then moved
into place, so two commands running at once never mix their output.

A skill or directory the script cannot read is skipped with a message on stderr, and the
rest of the library is still searched.

If the library directory is itself a git clone, the index file shows up there as
untracked. Use a plain directory that holds your clones, or add the file to that clone's
`.git/info/exclude`.

## How search ranks

Search is by keyword, with BM25 scoring. A word in a skill's name counts three times as
much as a word in its description. Results that score under 35% of the best result are
dropped, so a skill that only mentions a query word in passing does not fill the list.

A skill whose name is the query comes first, ahead of the ranking, and is marked
`(exact name)`. Case does not matter, and spaces match hyphens, so `commit messages` finds
`commit-messages`. If two skills in the library share that name, both are listed with
their directories.

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
  and literal values, with trailing comments and double-quote escapes. It does not read
  anchors, tags, or flow collections.
- The ranking was tuned against this repository's own skills, not a library of hundreds.
- Finding skills on remote sources is not part of this skill. `install` needs the
  repository and the skill's name.
- `install` takes skills from GitHub only. Put a skill from anywhere else in the library
  by hand and approve it with `review`.
- `gh skill` is a preview feature of the GitHub CLI and can change. `install` and `update`
  depend on it; the rest of the skill does not.
- `update` passes on what `gh` reports. `gh` gives no machine-readable result, so the
  command's exit status does not say whether updates were found.

## Test

```bash
python -m unittest discover -s skills/skill-router/scripts
```

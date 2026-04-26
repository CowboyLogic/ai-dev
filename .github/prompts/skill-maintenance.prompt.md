---
description: "Full skill maintenance cycle: research updates, run benchmark evals, create/update the docs/skills overview page, and propose a commit. Use when maintaining any skill in the skills/ folder of this repo."
agent: "agent"
argument-hint: "Skill folder name, e.g. client-config-copilotcli"
---

# Skill Maintenance — CowboyLogic/ai-dev

Run the full maintenance cycle for the skill named **`$input`** located at
`skills/$input/`.

Work through each stage in order. Do not skip a stage or move to the next
until the current one is complete.

---

## Stage 1 — Research and update the skill

1. Read `skills/$input/SKILL.md` and all files under `skills/$input/references/`
   in full to understand the current state.

2. Research what has changed since the skill was last updated. The skill's
   `sources.json` (if present) lists the upstream docs to check. Use the
   Tank research subagent to pull current information from those sources.
   Focus on: new config fields, changed defaults, deprecated keys, new
   CLI commands, and anything that would cause the current reference files
   to produce wrong or outdated answers.

3. Apply updates:
   - Edit `skills/$input/SKILL.md` if the task→reference map, quick-ops
     list, or config file table needs updating.
   - Edit files under `skills/$input/references/` with specific, targeted
     changes — do not rewrite sections that are still accurate.
   - If the skill has an installed copy (e.g. `~/.copilot/skills/$input/`
     or `~/.claude/skills/$input/`), sync the updated files there after
     every edit using `Copy-Item`.

4. Note every change made — you will need this list for the changelog
   entry in Stage 4 and the commit message in Stage 5.

---

## Stage 2 — Run benchmark evaluations

Use the eval cases in `skills/$input/evals/evals.json`. If no evals exist
yet, draft 3–4 realistic test cases that cover the skill's primary tasks
and save them to `skills/$input/evals/evals.json` before proceeding.

All runs go in `skills/$input-workspace/iteration-N/` where N is the next
iteration number (check for existing iteration folders first).

**Launch all runs in a single turn** — spawn with-skill AND without-skill
subagents simultaneously for every eval case. Do not batch them sequentially.

- **With-skill run**: provide the full SKILL.md content and relevant
  reference file content in the subagent prompt, then ask it to answer
  the eval prompt.
- **Without-skill (baseline) run**: same prompt, no skill content —
  the subagent answers from training knowledge alone.

While runs are in progress, draft assertions for each eval case and save
them to `evals/evals.json`. Good assertions are:
- Objectively verifiable (not "does it sound right")
- Named clearly enough that someone reading the benchmark immediately
  knows what each one checks

Write `eval_metadata.json` in each eval directory with the prompt and assertions.

---

## Stage 3 — Grade and benchmark

Once all runs are complete:

1. Grade every run against its assertions. For each run directory write
   `grading.json` with this structure:
   ```json
   {
     "eval_id": "<name>",
     "variant": "with_skill | without_skill",
     "assertions": [
       { "id": "<id>", "passed": true|false, "note": "<brief evidence>" }
     ],
     "score": N,
     "max_score": N,
     "pass_rate": 0.0–1.0
   }
   ```

2. Write `benchmark.json` in the iteration folder:
   ```json
   {
     "skill_name": "$input",
     "iteration": N,
     "run_date": "<YYYY-MM-DD>",
     "evals": [
       {
         "id": "<eval-name>",
         "with_skill":    { "score": N, "max_score": N, "pass_rate": 0.0 },
         "without_skill": { "score": N, "max_score": N, "pass_rate": 0.0 },
         "delta": 0.0
       }
     ],
     "summary": {
       "with_skill_total": N,
       "without_skill_total": N,
       "max_total": N,
       "with_skill_pass_rate": 0.0,
       "without_skill_pass_rate": 0.0,
       "overall_delta": 0.0
     }
   }
   ```

3. Summarise the results: overall pass rates, delta, and — importantly —
   what the baseline got wrong and why it matters.

---

## Stage 4 — Create or update the docs overview page

The page lives at `docs/skills/$input.md`. Check whether it already exists.

### If it does not exist — create it

Use this structure:

```markdown
# <Human-readable skill title>

<One-paragraph description of what the skill covers.>

- **Skill name:** `$input`
- **Last updated:** <YYYY-MM-DD>
- **Source:** [skills/$input](https://github.com/CowboyLogic/ai-dev/tree/main/skills/$input)

---

## What it does

<Explain what gap the skill closes — what the baseline gets wrong without it.>

<Include a config/scope table if the skill covers multiple files or areas.>

---

## Install

### Using `npx skills` (recommended — works across all agents)

\`\`\`bash
npx skills add CowboyLogic/ai-dev --skill $input -g
npx skills add CowboyLogic/ai-dev --skill $input --agent <agent> -g
npx skills add CowboyLogic/ai-dev --skill $input -g -l
\`\`\`

### Verify installation

\`\`\`bash
npx skills ls -g
\`\`\`

---

## Evaluation results

Benchmark run: **<YYYY-MM-DD> · iteration N** · <X> scenarios · <Y> total runs

### Overall

| | With skill | Baseline (no skill) | Delta |
|---|---|---|---|
| Assertions passed | N / N | N / N | — |
| Pass rate | **X%** | **X%** | **+X pp** |

### By scenario

<Table with per-eval results and notes on what the baseline got wrong.>

<GFM callout summarising the value proposition, e.g.:>
> [!NOTE]
> <When this skill matters most and for which agent/model combination.>

### Key takeaway

<Prose explanation of where the gap is real vs where baseline is already reliable.>

---

## Changelog

### <YYYY-MM-DD> — v<N> (<label>)

<Bullet list of every file changed and what was updated.>
```

Follow all repo Markdown standards:
- GFM callouts (`> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`) — never plain
  bold blockquotes for informational content
- Blank lines around all block elements
- Fenced code blocks with language identifiers

### If it already exists — update it

- Update the `Last updated` metadata field.
- Add a new entry at the top of the Changelog section listing every
  change made in Stage 1.
- Update the Evaluation results section with the new benchmark data from
  Stage 3, preserving previous iteration data below it.
- Update the "What it does" section if the skill's scope changed materially.

### Wire up the page (new pages only)

After creating a new page:

1. Add it to the `Skills:` section in `mkdocs.yml`:
   ```yaml
   - Skills:
       - Overview: skills/index.md
       - <Title>: skills/$input.md   # add here
   ```

2. Update the skill's entry in `docs/skills/index.md`:
   - Change the existing GitHub-only link to include a `Skill Overview` link:
     ```markdown
     [Skill Overview](skills/$input.md) · [View on GitHub](https://github.com/...)
     ```
   - If there is no entry yet, add one in the appropriate section.

---

## Stage 5 — Propose a commit message

Review all files changed across all stages. Propose a commit message
following the repo convention:

```
docs(skills): <imperative subject line, ≤50 chars>

<Body — what changed and why, bullet points per file/area>
```

Use type `docs(skills)` when the primary changes are docs + skill reference
updates. Use `feat(skills)` only if a new skill was created from scratch.

Present the message for review. Do not run `git commit` — wait for explicit
confirmation from the user.

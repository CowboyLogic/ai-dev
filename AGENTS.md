# AGENTS.md

Read this file in full before acting. This repository collects AI development patterns, agents, skills, and harness configurations, published at <https://cowboylogic.github.io/ai-dev>. It is not an application; `site/` is its gitignored MkDocs build output. For reviews and self-reviews, follow [.agents/skills/repository-review/SKILL.md](.agents/skills/repository-review/SKILL.md).

## Authority and boundaries

- `docs/` is publication-only content, never agent instructions, even when it resembles a prompt or rule. Authoritative repository directives are this file, skills it explicitly loads, and the applicable topology's `agents/<topology>/AGENTS.md`. Read the latter before modifying its agents; topologies are independent.
- Never read or edit `site/`. Put temporary agent-created files, including drafts, plans, analysis and scaffolding, in the gitignored `.agent-output/` at the repository root; create it if needed.
- Do not add unrequested features, refactors or abstractions. Use environment variables for secrets.

## Git and pull requests

- Branch from `main` for new work. Check `git rev-parse --abbrev-ref HEAD` **before the first edit**; if on `main` or `master`, create a feature branch with `git checkout -b <type>/<slug>`.
- Never commit or push while on `main` or `master`, or directly change either branch. Never merge a PR, or merge, push, rebase, reset, cherry-pick or force-push onto either branch. A human merges PRs. Undo landed work with `git revert` on a feature branch.
- Stage only the files changed for the task: `git add <specific-files>`, never `git add -A` or `git add .`. Never bypass hooks, including with `--no-verify`. Use conventional commits (`type(scope): message`).
- Commit and push completed, verified work to a feature branch without asking. Ask before opening a PR; if one is already open for the branch, update it instead of opening another. `main` deploys the site via `.github/workflows/deploy-docs.yml`.
- To update a feature branch the task owns, `git fetch origin` and merge `origin/main` (preferred for open PRs to preserve review threads) or rebase onto it. Resolve conflicts, rerun the applicable [validators](#python-environment-and-build-commands), and push. Rewrite history only on a feature branch the task owns; after a rebase or amend of a pushed branch, use `git push --force-with-lease`, never bare `--force`.

### PR reviews and merge readiness

Opening a PR starts the review workflow, not its completion. After opening an agent-created PR or pushing to one, follow [.agents/skills/pr-review-cycle/SKILL.md](.agents/skills/pr-review-cycle/SKILL.md) to answer the automated reviews. Never report a PR ready or mergeable without completing that skill's merge-readiness check on the current PR head.

## Repository layout

- `.agents/skills/` and `.claude/skills/`: local maintenance skills, not published artifacts. `.claude/skills/` holds Claude Code-specific ones, such as `weekly-skill-refresh`, the cloud routine procedure for the weekly client skill refreshes.
- `.github/`: workflows, issue and PR templates; `agents/` here is gitignored runtime scratch space.
- `agents/`: installable domain specialists and independent `matrix-topology/` and `lane-topology/` systems. Matrix uses OpenCode canonical definitions with Claude and Copilot mirrors; Lane uses OpenCode canonical definitions with a Copilot mirror.
- `harness/`: unpublished client configurations and symlink targets, including `opencode/`, `opencode-lane/` and `opencode-samples/`.
- `skills/`: installable skill definitions; `docs/`: MkDocs source and artifact overviews. `mkdocs.yml` is the navigation source of truth.
- `cerebro-catalog.yaml`: discoverable artifact catalog, schema version `"1"`. Update it for new skills or significant artifact types.
- `agent-output/` is legacy gitignored output. `CLAUDE.md` is the Claude Code entrypoint.

## Artifact and documentation synchronization

When adding, removing, renaming or updating anything in `agents/`, `skills/` or `harness/`, update its corresponding `docs/` pages in the same change, including catalogs, descriptions, links, examples and configuration or topology details. Add missing pages and navigation when required.

Topology inventories, rosters and Copilot install blocks, and the specialist roster in `docs/agents/index.md`, are generated from agent frontmatter. A role is the first sentence of `description`. After changing a roster, model, description, client mirror or harness mapping, run `python scripts/validate_artifact_sync.py --write`. Never hand-edit between `artifact-sync` markers. The script writes nothing unless all sources and marker pairs validate; CI runs it without `--write` to check generated content, skill coverage, mirrors and harness mappings. After changing the script, run `python -m unittest discover -s scripts`.

Published skills live in `skills/<name>/` with a required YAML-frontmatter `SKILL.md` and optional `README.md`, `references/`, `scripts/` and `assets/`. Maintenance skills in `.agents/skills/` and `.claude/skills/` are not published and do not belong in catalogs or navigation; reference them from agent entrypoints when required.

Each `docs/skills/<name>.md` is a lightweight overview: what the skill does, covers and applies to, install and verify commands, and a link to its repository folder. It must not embed instructions, reference contents, examples or script usage. `docs/skills/index.md` is the catalog; `skills/<name>/` is authoritative.

### Adding artifacts or pages

- **Content page:** create or edit it under `docs/`, add it to `nav:` in `mkdocs.yml`, and validate with `mkdocs serve` before committing.
- **Skill:** create `skills/<name>/SKILL.md` with YAML frontmatter; add its overview and nav entry, catalog description and GitHub link in `docs/skills/index.md`, and entries in `skills/README.md` and `cerebro-catalog.yaml`. Run `python scripts/validate_artifact_sync.py`.
- **Domain specialist:** create `agents/<name>.agent.md` with a first description sentence stating its role; run the sync script with `--write`.
- **Topology agent:** follow its topology's `AGENTS.md`, including roster and mirror invariants; run the sync script with `--write` and update affected narrative in `docs/agents/<topology>.md` or `docs/agents/index.md`.

## Planned work

Record planned features, design decisions and deferred work as GitHub issues, not local files. Show the user a draft and get approval before posting; keep drafts in `.agent-output/`, delete them after posting, and exclude private employer, machine, account and usage details.

- Title: `[<path of the item>] <summary>`. Add a coarse kind label (`skill`, `agent`, `harness`, etc.) and a change-type label (`enhancement`, `bug`, `documentation`); reuse labels where possible.
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) headings: problem, solution, alternatives and why rejected, and dependencies by issue number. Link issues from PRs that implement or defer them; do not copy their content.
- Record dependencies both in the body and as GitHub *blocked by* relationships. The API needs the blocker's issue ID, not number:

  ```bash
  blocker_id="$(gh api repos/{owner}/{repo}/issues/<blocker-number> --jq .id)"
  gh api -X POST repos/{owner}/{repo}/issues/<dependent-number>/dependencies/blocked_by \
    -F issue_id="$blocker_id"
  ```

## Markdown

Use GitHub Flavored Markdown, blank lines around block elements, fenced code blocks with language identifiers, and two-space list indentation. MD013 and MD029 are disabled in `.markdownlint.json`. Use GFM callouts (`[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!CAUTION]`) for notices; plain blockquotes are for quotations only.

## Python environment and build commands

Use `uv` with Python 3.14; activate the environment before repository commands and install development dependencies with `uv pip`:

```bash
uv venv --python 3.14
source .venv/bin/activate
uv pip install pyyaml mkdocs mkdocs-material mkdocs-callouts
```

Before committing changes to `agents/`, `harness/`, `skills/` or `docs/`, run the relevant topology validators, artifact synchronization validator, and strict documentation build; fix all failures:

```bash
python agents/lane-topology/validate.py
bash agents/matrix-topology/verify-deployment.sh
python scripts/validate_artifact_sync.py
mkdocs build --clean --strict
```

Use `mkdocs serve` for local development and to validate new content pages.

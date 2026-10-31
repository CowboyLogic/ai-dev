# AI-DEV Weekly Maintenance Pull Request

<!-- Open with: gh pr create --body-file <filled copy of this template>, after asking. Fill in every section and delete these comments. -->

## What does this PR do?

<!--
One short paragraph: which skills or agents were refreshed and against what. Link the
tracking issue with `Closes #N`.
-->

Closes #

## Basis

- **Upstream tool and version:** <!-- the latest stable release on the refresh date; say how you confirmed it is the latest -->
- **Refresh date:** <!-- YYYY-MM-DD -->
- **Previous refresh:** <!-- PR number and the version it used -->
- **Window covered:** <!-- previous version through this one; note prereleases that were skipped -->

## Sources checked

<!--
List each source and the date you checked it. Every added claim must trace to one of
these. Say which claims rest on release notes alone, and record conflicts between
sources instead of resolving them silently.
-->

-

## Changes made

<!-- One block per skill, agent, or harness item. Name the file and what changed in it. -->

`skills/NAME` (CHANGELOG vN):

-

`docs/`:

-

## Not changed, and why

<!--
Upstream changes you saw and left out, unresolved source conflicts, and anything you
could not verify (for example a binary blocked by the npm release-age guard, or a
benchmark you did not re-run). Write "None" only if it is true.
-->

-

## Type of change

- [ ] Skill refresh
- [ ] Agent refresh
- [ ] Harness config refresh
- [ ] Documentation update that follows from the refresh

## Checklist

- [ ] Branch was created from `origin/main` (or stacked on a named open refresh PR)
- [ ] `python scripts/validate_artifact_sync.py` is clean
- [ ] `mkdocs build --clean --strict` passes with no warnings
- [ ] Topology validators pass if `agents/` or `harness/` changed
- [ ] markdownlint reports no issues on the changed files
- [ ] Each skill's `CHANGELOG.md` and version/verification dates in `README.md` and `SKILL.md` are updated
- [ ] Matching `docs/skills/` pages and `docs/skills/index.md` are updated; no skill content is copied into them
- [ ] Source URLs were checked and resolve
- [ ] No hardcoded secrets or tokens
- [ ] Only the files this refresh changed are staged

## Verification

<!--
State what you ran and what it reported, with counts where the tool gives them. State
what you did not run.
-->

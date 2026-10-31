---
name: Weekly maintenance
about: Recurring refresh of agents or skills against their upstream tools
title: '[<affected path>] Weekly refresh against <tool> <version>'
labels: documentation
type: Maintenance
assignees: ''

---

<!--
For agents: one issue per refresh. Replace `<affected path>` with the path of the affected
item, as in AGENTS.md "Recording Planned Work": `skills/client-config-codex`,
`agents/matrix-topology`, or `harness/opencode`. When the refresh covers several items for
one client, list them, for example `[skills/client-config-codex, skills/agent-creator-codex]`.
Add the kind label (`skill`, `agent`, or `harness`) when you file it.
-->

## Scope

<!-- Every skill, agent, or harness item this refresh covers, as repo paths. -->

-

## Basis

- **Upstream tool and version:** <!-- e.g. Codex CLI 0.164.0 -->
- **Previous refresh:** <!-- PR number and the version it was based on -->
- **Window to cover:** <!-- previous version through the new one -->

## Before starting

- [ ] No refresh PR for the same client is open. If one is, stack on its branch instead of pushing to it.
- [ ] Work happens in a worktree of its own, not the shared checkout.
- [ ] Branch created from `origin/main` before the first edit.

## Tasks

- [ ] Check every source in `sources.json` (or the skill's upstream docs) and the release notes for the window
- [ ] Update `SKILL.md` and `references/` where claims changed; leave accurate sections alone
- [ ] For each skill: record each change in its `CHANGELOG.md` and update version and verification dates in its `README.md`
- [ ] Update the documentation for every artifact type changed, per AGENTS.md "Documentation Synchronization":
  - skills: `docs/skills/<name>.md` and the `docs/skills/index.md` wording
  - agents: the matching `docs/agents/` pages, then `python scripts/validate_artifact_sync.py --write`
  - harness: the matching `docs/harness/` pages
- [ ] Run the validators from AGENTS.md "Build Commands" that apply

## Out of scope

<!-- Upstream changes deliberately not covered, and why. -->

## Notes

<!-- Known blockers, such as the npm release-age guard blocking a fresh binary. -->

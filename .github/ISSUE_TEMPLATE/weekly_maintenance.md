---
name: Weekly maintenance
about: Recurring refresh of agents or skills against their upstream tools
title: '[skills/<name>] Weekly refresh against <tool> <version>'
labels: documentation
type: Maintenance
assignees: ''

---

<!--
For agents: one issue per refresh. Name the affected item first in the title, as in
AGENTS.md "Recording Planned Work". Add the kind label (`skill`, `agent`, or `harness`)
when you file it. When the refresh covers several skills for one client, name the client
folder family, for example `[skills/client-config-codex, agent-creator-codex]`.
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
- [ ] Record each change in the skill's `CHANGELOG.md`; update version and verification dates in `README.md`
- [ ] Update the matching `docs/skills/<name>.md` pages and `docs/skills/index.md` wording
- [ ] Run the validators from AGENTS.md "Build Commands" that apply

## Out of scope

<!-- Upstream changes deliberately not covered, and why. -->

## Notes

<!-- Known blockers, such as the npm release-age guard blocking a fresh binary. -->

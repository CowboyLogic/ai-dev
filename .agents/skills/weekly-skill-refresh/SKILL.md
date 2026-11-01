---
name: weekly-skill-refresh
description: Run the unattended weekly refresh of one client's agent-creator and client-config skills in CowboyLogic/ai-dev from a fresh cloud clone. Use when a routine names a client (claudecode, codex, copilot, opencode).
---

# Weekly skill refresh

Unattended weekly refresh of one client's two skills against that client's latest stable
release. This is a repository maintenance skill, not an installable artifact. It runs in a
fresh cloud clone: no local worktrees, no `~/projects` paths, no `.venv`, no GraphQL, and no
way to delete remote branches.

**Parameter:** `client`, one of `claudecode`, `codex`, `copilot`, `opencode`. Use the row
below for everything client-specific; every other step is identical.

| client | Skills in scope | Tool and version source | `sources.json` |
|---|---|---|---|
| `claudecode` | `skills/agent-creator-claudecode`, `skills/client-config-claudecode` | npm `@anthropic-ai/claude-code` `latest` dist-tag and `anthropics/claude-code` releases | `skills/client-config-claudecode/assets/sources.json` |
| `codex` | `skills/agent-creator-codex`, `skills/client-config-codex` | `openai/codex` GitHub releases (tag `rust-v<version>`), stable only | `skills/client-config-codex/sources.json` |
| `copilot` | `skills/agent-creator-copilot`, `skills/client-config-copilotcli` | `github/copilot-cli` GitHub releases, stable only | `skills/client-config-copilotcli/sources.json` |
| `opencode` | `skills/agent-creator-opencode`, `skills/client-config-opencode` | `anomalyco/opencode`: V1 from GitHub releases, V2 from git tags (no releases); release notes are the repository `CHANGELOG.md` | `skills/client-config-opencode/sources.json` |

Branch name: `refresh/<client>`. This run owns that branch and nothing else.

## Rules that override this file

Read `AGENTS.md` first. It governs git, documentation and PR rules. Never commit or push
to `main` or `master`, never merge a PR, never bypass hooks, never `git add -A` or
`git add .`, and never edit `site/`. Put scratch files in `.agent-output/`. If anything
below conflicts with `AGENTS.md`, `AGENTS.md` wins, with one standing exception: the
maintainer (Micheal) pre-approved opening **ready-for-review** (not draft) PRs for these
scheduled refresh runs, so the "ask before opening a PR or marking ready" rule is
satisfied for the PR this procedure opens (approval given 2026-11-01 in the project thread
that created this procedure: "READY PR's"). It covers only the one PR per client per run
that section 5 describes. It does not cover merging, issues beyond the tracking issue, or
any other PR.

## 1. Prepare

1. The clone may be shallow. Run `git fetch --unshallow origin 2>/dev/null || git fetch origin`,
   then `git fetch origin main`.
2. Set up tooling from the repo's own instructions (`AGENTS.md`, "Python environment"):

   ```bash
   uv venv --python 3.14
   source .venv/bin/activate
   uv pip install pyyaml mkdocs mkdocs-material mkdocs-callouts
   ```

   markdownlint runs through `npx --yes markdownlint-cli2 <changed files>` (config in
   `.markdownlint.json`). If it cannot be installed, say so in the PR; do not claim it passed.
3. Look for this client's unmerged work with GitHub MCP `list_pull_requests` (state `open`,
   head `CowboyLogic:refresh/<client>`).
   - **Open PR exists:** continue it. `git fetch origin refresh/<client>` and
     `git checkout -B refresh/<client> origin/refresh/<client>`. Take the issue number from the
     `Closes #<n>` line in the PR body. Open no new issue or PR this run.
   - **No open PR:** start fresh. Cloud sessions cannot delete remote branches, so reset
     instead: `git checkout -B refresh/<client> origin/main`. If `refresh/<client>` exists on
     origin (abandoned work with no open PR), the first push is
     `git push --force-with-lease=refresh/<client>:<sha-you-fetched> -u origin refresh/<client>`,
     where the sha is `git rev-parse origin/refresh/<client>`. Force only here, only on this
     branch, only when no open PR exists. If the branch is not on origin, plain
     `git push -u origin refresh/<client>`.
4. Before the first edit, confirm `git rev-parse --abbrev-ref HEAD` is `refresh/<client>`.

## 2. Establish the basis

1. Find the latest **stable** release from the table's source. Skip alpha, beta, rc and
   other prereleases.
2. Find the basis recorded by the previous refresh in each skill's `README.md`, `SKILL.md`
   and `CHANGELOG.md` (agent-creator skills may have no `CHANGELOG.md`).
3. The window is the previous basis through the new version.

## 3. Open the tracking issue (every run, even if nothing changed)

Skip when step 1.3 found an open PR; use the issue it closes.

1. Read `.github/ISSUE_TEMPLATE/weekly_maintenance.md`, drop its frontmatter, and fill in
   every section from what you know now. Tick only what is true. In "Before starting", the
   worktree line is satisfied by this run's fresh clone; say so.
2. Create it with GitHub MCP `issue_write` (method `create`), title
   `[<skill 1>, <skill 2>] Weekly refresh against <Tool> <version>`, issue type
   `Maintenance`, labels `documentation` and `skill`. If the MCP tool cannot set the type,
   use `gh api -X POST repos/CowboyLogic/ai-dev/issues ... -f type=Maintenance`.
3. Keep the number. If the issue cannot be created, stop and report why.

## 4. Refresh the skills

1. Read both skills in full (`SKILL.md`, everything under `references/`, `README.md`,
   `CHANGELOG.md` where present) and the sources in the client's `sources.json`.
2. Check the vendor's release notes for the window and the published documentation for each
   source. Use authoritative sources only.
3. Make targeted edits. Do not rewrite sections that are still accurate.
4. Keep every change verifiable. If a claim cannot be checked against a source, do not make
   it. Label a claim that rests on release notes alone. Record conflicts between sources
   instead of resolving them.
5. Update the version basis and verification date in each skill's `README.md` and
   `SKILL.md`. Add a `CHANGELOG.md` entry per skill that has one; where a skill has none
   (the agent-creator skills), do not create one: record the change in the PR and the
   client-config entry. A refresh with no content change still gets the entry, saying what
   was verified and that no content changed.
6. Update the matching `docs/` pages per `AGENTS.md` "Artifact and documentation
   synchronization". Docs link to the skill folder and never copy its content.
7. Run, with the venv active, and fix every failure:

   ```bash
   python scripts/validate_artifact_sync.py
   mkdocs build --clean --strict
   npx --yes markdownlint-cli2 <changed .md files>
   ```

8. If `npm` blocks installing a version this new (release-age guard), do not override it.
   Verify from the release docs and source, and say in the README and the PR that the
   binary was not run.

## 5. Record the outcome

Every run produces a PR, because the verification date and basis change every run.

1. Commit in logical units, conventional style (`docs(skills): ...`), staging exact paths.
2. Push `refresh/<client>` per step 1.3. Otherwise never force-push.
3. Continuing an open PR: the push updates it. Comment on the PR with what this run added,
   then go to section 6. Otherwise open the PR with GitHub MCP `create_pull_request`
   (head `refresh/<client>`, base `main`), body filled from
   `.github/PULL_REQUEST_TEMPLATE/weekly_maintenance.md`, with `Closes #<issue>`. Title:
   `docs(skills): weekly <Tool> skills refresh against <Tool> <version> (<YYYY-MM-DD>)`.
   The body is the maintainer's review surface, since the maintainer reads it before
   merging. It must summarize, in plain terms: what changed per skill and why (with the
   source for each claim), what was verified with no change, what was deliberately left out
   or could not be verified, and which claims rest on release notes alone. A date-only
   refresh says so under "Changes made" and lists the sources checked. Begin the
   body with any attribution block the routine or session context requires.
4. Comment on the issue with the PR link. Leave it open; it closes when the PR merges.
5. Only if there is no diff at all (dates already match today), skip the PR: comment on the
   issue with the basis and sources checked, then close it as completed.

## 6. Answer the review

Opening the PR starts the review; it is not the end. Copilot reviews once and does not
re-review. Codex reviews code and security and re-reviews after each push. Work in rounds
and stop after 3 rounds in total. Wait at most 10 minutes in total for any one review; if
it has not landed, stop waiting, report the PR link, and say the review is pending. Never
call the PR clean in that case.

GraphQL is blocked in cloud. Use GitHub MCP `pull_request_read` (methods for review
comments, reviews and review threads) to read; `add_reply_to_pull_request_comment` to
reply; `resolve_review_thread` to resolve. REST via `gh api repos/CowboyLogic/ai-dev/pulls/<n>/...`
is the fallback. Page through every result.

Each round is one pass, with one push at the end:

1. Wait 2 to 3 minutes after the PR opens or after a push, then read all reviews: inline
   threads and findings that appear only in a review summary.
2. Classify every finding before changing anything, checking each against the code:
   - **Valid:** fix it in its own commit, with the validator or test that covers it.
     Findings with one cause are one fix and one commit.
   - **Invalid or inapplicable:** no change; note what you checked.
   - **Valid but out of scope:** no change; note why. Follow `AGENTS.md` "Planned work"
     (draft the issue in `.agent-output/`, and because no human is present to approve,
     report it as a deferral in the final report instead of posting it; do not resolve that
     thread until an issue exists, and say so).
3. Run the applicable validators on the final tree, then push once. Never amend or rebase
   reviewed commits. Never push while a review is pending or while findings from the same
   round are unaddressed.
4. Reply on every thread (name the fix commit, or give the reason), then resolve it,
   except as noted for deferrals. Check resolution state, not comment presence.
5. If Codex reviews the push with new findings, that is the next round, up to 3 total.
   After the third round's push, check the resulting review but do not respond to a fourth;
   report its findings or pending status for human direction.

## 7. Merge-readiness bar

Before reporting, verify on the current PR head (`pull_request_read` get and
status methods; `gh api repos/CowboyLogic/ai-dev/pulls/<n>` as fallback):

- Not a draft unless the routine said draft; `mergeable` is true and `mergeable_state` is
  `clean`; required checks pass. Unknown, pending or failing is unverified, not clean.
- **Rebaseable onto `main` with no conflicts.** `git fetch origin main` and check
  `git merge-tree --write-tree origin/main HEAD` exits 0. If `main` moved and conflicts,
  merge `origin/main` into `refresh/<client>` (never rebase a reviewed branch), resolve,
  rerun the validators, push, and repeat sections 6 and 7 on the new head. Pushes count
  toward the 3-round cap.
- **No unresolved review threads from any reviewer**, outdated ones included, every page.

If a condition cannot be met within this procedure, report the exact blocker and the PR
link as unfinished. Never claim mergeable or ready while anything is unresolved or
unverified. Never merge.

## 8. Final report

Also post this as a final comment on the PR (the maintainer reads the PR, not the session),
and update the PR body if the review rounds changed its content.
State: client and version, issue and PR links, whether the PR is draft or ready, rounds
used, fixes (with commits), refutations, deferrals, and the merge-readiness result with
anything unverified.

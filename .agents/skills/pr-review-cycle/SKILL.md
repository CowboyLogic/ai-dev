---
name: pr-review-cycle
description: Answer automated reviews on an agent-created pull request in CowboyLogic/ai-dev and verify merge readiness. Use after opening a PR or pushing to an existing one, when handling Copilot or Codex review threads, and before reporting any PR as ready or mergeable.
---

# PR review cycle

Follow this procedure for PRs in CowboyLogic/ai-dev. It is a repository maintenance
skill, not an installable artifact in the public library. Git rules, validators and
[Planned work](../../../AGENTS.md#planned-work) live in [AGENTS.md](../../../AGENTS.md);
this skill does not override them. Review judgment for findings is in
[repository-review](../repository-review/SKILL.md).

## Reviewers

Copilot automatically reviews each PR once; do not request or wait for another Copilot review. Codex automatically reviews each PR and re-reviews every push. Opening a PR starts the review workflow, not its completion. All review threads must be resolved before merge.

Copilot review effort is controlled by the user, normally **Balanced**. Never change repository settings; check the review overview and report any other effort.

## Review cycle

1. After opening an agent-created PR or pushing to its existing PR, check for the applicable reviews, including inline threads and summary-only findings. Wait at most 10 minutes per review cycle; stop waiting sooner when all expected reviewers clearly indicate their reviews are complete, including approval indications where available. If a review is still pending at the limit, report the PR link and which review is pending; do not call the PR clean.
2. Read each complete review and classify every finding before changing anything. Check each against the code; do not blindly apply or dismiss suggestions. For each comment, fix the issue, refute it with a reason grounded in what was checked, or defer a valid out-of-scope finding to a tracked GitHub issue. Explain why it is out of scope and follow [Planned work](../../../AGENTS.md#planned-work), including approval before posting an issue. Do not resolve the thread until the issue exists.
3. Commit each distinct fix separately, including an applicable test or validator; findings sharing a cause are one fix. Do not amend or rebase reviewed commits. After all findings in the available reviews are addressed, run applicable [validators](../../../AGENTS.md#python-environment-and-build-commands) on the final tree and push fixes together, not one push per finding or while a review is pending.
4. Reply to every thread with the fix commit, the reason for refuting it, or the linked issue and reason for deferral, then resolve it. Check thread resolution state rather than comment presence. Address summary-only findings too. Check all threads, including those from other reviewers; unresolved threads block merging.
5. Each push triggers another Codex review, so every push to the PR, including a merge from the base branch, starts a new cycle. Follow this process for at most three review cycles, counting the initial review as cycle one. After a third cycle fix push, check the resulting review but do not respond to a fourth cycle; stop and report its findings or pending status and any unresolved threads for human direction. Stop earlier when the latest push has been reviewed and all threads are resolved. Do not wait for, read or answer a second Copilot review.
6. After the final push and reviews, verify [merge readiness](#merge-readiness) on the current PR head. Report the PR link, fixes, refutations, deferrals and any remaining blockers. Work is not done until every thread is resolved and the PR is clean to merge. The cycle cap and review timeout still require stopping and reporting unfinished work, not calling it ready; merging remains a human action.

## Merge readiness

Before reporting a PR ready to merge, verify its latest head on GitHub, not just the local branch or an earlier review:

- Inspect all review threads, including outdated threads and every page of results. Each must be resolved after a fix, a reasoned refutation, or an approved, linked issue for a valid out-of-scope deferral. Do not resolve a thread without its required reply.
- Run `gh pr view <number> --json isDraft,headRefOid,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup` and inspect the PR's merge requirements and checks. Confirm it is not a draft, `mergeable` is `MERGEABLE`, `mergeStateStatus` is `CLEAN`, required reviews and checks are satisfied, and no other GitHub-reported merge restriction or conflict remains. Investigate the specific blockers in the PR and its checks; a clean Git diff or successful local tests alone is insufficient.
- Treat unknown, pending, stale, failing, blocked or unavailable status as unverified, not clean. Wait for GitHub to calculate status and for required checks to finish, then recheck. Fix merge conflicts by updating the task-owned feature branch from the base, resolve other actionable blockers, validate, push, and repeat the review and readiness checks on the new head. Do not bypass protections or merge the PR.
- If a blocker cannot be resolved within the authorized workflow, including when a review is pending at the timeout or the review-cycle cap is reached, report the precise blocker and PR link as unfinished. Never claim it is mergeable or ready while any thread or merge condition remains unresolved or unverified.

## Thread commands

List and resolve threads with `gh api graphql` (paginate if needed). Where GraphQL is unavailable, use the environment's GitHub tools that list, reply to and resolve review threads, paging through every result. REST can list and reply to review comments but cannot resolve threads; if no available tool can resolve them, report the unresolved threads as a blocker.

```bash
gh api graphql -F owner='{owner}' -F repo='{repo}' \
  -F pr="$(gh pr view --json number --jq .number)" -f query='
  query($owner: String!, $repo: String!, $pr: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $pr) {
        reviewThreads(first: 100) {
          nodes { id isResolved comments(first: 1) { nodes { author { login } path line body } } }
        }
      }
    }
  }'

gh api graphql -f threadId='PRRT_xxxxxxxx' -f query='
  mutation($threadId: ID!) {
    resolveReviewThread(input: { threadId: $threadId }) { thread { isResolved } }
  }'
```

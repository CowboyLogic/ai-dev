---
description: "REVERT lane — undo something already committed. git revert only, on a branch, verified before it ships. Never resets or rewrites history."
agent: conductor
---
REVERT LANE. Run the REVERT lane procedure from your agent file.

TARGET: $ARGUMENTS

1. Resolve the target to an exact commit SHA using git log / git show. If it is ambiguous, ask me — do not guess.
2. STATE THE SHA AND ITS SUBJECT BACK TO ME before touching anything. Reverting the wrong commit is the one expensive mistake in this lane.
3. Determine where it landed. If it is unmerged on a feature branch, ask whether I would rather you close the PR and start over. If it is on main, run the branch check — the revert gets its own branch and its own PR.
4. `git revert --no-edit <sha>`. Several commits get reverted individually, in reverse chronological order.
5. On conflict: `git revert --abort`, report the conflicting paths, and re-lane to DIRECT. Never resolve a revert conflict by hand.
6. Dispatch Verifier. A clean revert can still break the build if later work depended on what it removed. Not skippable.
7. On PASS, ship — commit, push, open the PR, never merge — and report the link.

Cap: one. If the revert fails verification, stop and escalate to me with the failure output. Do not attempt a second revert or a fix on top of it.

Never reset, rebase, force-push, or `git checkout -- <path>` in this lane. Undoing is a new commit, always.

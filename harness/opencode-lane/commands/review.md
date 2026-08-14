---
description: "REVIEW lane — draft a maintainer review for a PR you didn't author or brief. Reviewer infers intent from the PR itself, checks it against repo conventions, and drafts a comment. Never approves or runs the PR's code."
agent: conductor
---
REVIEW LANE. Run the REVIEW lane procedure from your agent file.

PR: $ARGUMENTS

1. Resolve the target to a PR number against the repository I'm currently working in. If it's ambiguous, ask me — do not guess.
2. Dispatch Reviewer with the PR number and, if one exists, a path to CONTRIBUTING.md or this repo's style convention.
3. Read SECURITY SURFACE from the PR REVIEW block: CRITICAL dispatches the Adversary alongside Reviewer; ADJACENT or NONE proceeds with Reviewer's findings alone.
4. Do not dispatch the Verifier against the PR's own code unless I explicitly ask for it in this request, or the repo's AGENTS.md names contributors it trusts by default. Running a contributor's code before it's been reviewed is never automatic.
5. On COMMENT or REQUEST_CHANGES, you may post it (`gh pr comment` or `gh pr review --comment` / `--request-changes`) without waiting for my approval — the same autonomy DIRECT and MECHANICAL already have over my own branch.
6. On APPROVE_RECOMMENDED, show me the recommendation and the findings. Do not post an approval — `gh pr review --approve` is not in your grant, and it isn't in mine either. That one's always mine to post.
7. On a Reviewer escalation (bad faith, unclear intent, a critical surface with no findings yet) — surface it to me directly. Do not draft or post anything for that PR until I've seen it.

This lane never reaches the branch check and never ships — it's reviewing a PR, not opening one.

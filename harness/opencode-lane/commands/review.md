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
5. On COMMENT, you may post it (`gh pr comment` or `gh pr review --comment`) without waiting for my approval — the same autonomy DIRECT and MECHANICAL already have over my own branch. Comments carry no gating weight over the PR.
6. On REQUEST_CHANGES or APPROVE_RECOMMENDED, show me the recommendation and the findings. Never post either on the verdict alone — both gate the PR, and both require an explicit ask from me in this session before you run `gh pr review --request-changes` or `gh pr review --approve`. Once I ask, post it and confirm it landed.
7. On a Reviewer escalation (bad faith, unclear intent, a critical surface with no findings yet) — surface it to me directly. Do not draft or post anything for that PR until I've seen it.

This lane never reaches the branch check and never ships — it's reviewing a PR, not opening one.

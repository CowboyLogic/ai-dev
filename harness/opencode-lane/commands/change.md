---
description: "DIRECT lane — a small, well-scoped change. Builder implements, Verifier independently runs the tests. Skips classification."
agent: conductor
---
DIRECT LANE. Run the DIRECT lane procedure from your agent file. Do not re-classify unless a hard trigger fires (new architectural decision, public contract change, or security-critical surface) — in that case tell me and take the heavier lane.

REQUEST: $ARGUMENTS

1. Run the branch check from your Shipping section before dispatching Builder.
2. State your understanding in one line and proceed. Non-blocking.
3. Determine the security band (CRITICAL / ADJACENT / NONE).
4. Dispatch Builder. Include the security band and the verification command in the brief.
5. Dispatch Verifier — and Adversary if the band is CRITICAL. The Verifier RUNS the build and tests itself; the Builder's claim of green is not evidence.
6. Act on the verdict: PASS -> ship (commit, push, open the PR — never merge) and report the link. FIX -> one Builder cycle, max two. ESCALATE -> re-lane or surface to me.

Keep it lean. The diff is the artifact, and there is no full ledger or Facts Protocol bookkeeping unless something escalates — but Shipping needs the branch name, the one-line INTENT, and the PR link to compose the commit and the PR body, so track at least that much.

---
description: "BUILD lane — full lifecycle for net-new work. Planner produces a Design Brief with ADs and REQ-### requirements, Builder writes tests first, Scribe documents."
agent: conductor
---
BUILD LANE. Run the BUILD lane procedure from your agent file.

REQUEST: $ARGUMENTS

1. Run the PLAN lane first. The Planner's artifact is a DESIGN BRIEF: user-facing FLOW first, then STRUCTURE with AD-### Architecture Decisions, then numbered testable REQ-### requirements in RFC 2119 language.
2. Verifier + Adversary review the Design Brief. Loop to PASS before any code is written.
3. Run the branch check from your Shipping section before dispatching Builder.
4. Dispatch Builder with the Design Brief. Tests against the REQ-### numbers first, then implementation, then green.
5. Verifier runs the suite independently and checks REQ-### coverage. Adversary reviews if the band is CRITICAL. Loop to PASS.
6. Dispatch Scribe to document what was actually built.
7. Ship: commit the code and docs together, push, open the PR — never merge — and report the link to me.
8. Maintain the ledger at .agent-output/<project>/ledger.md throughout — this lane is long enough to lose to a compaction event.

Run independent subsystems in parallel. Do not serialize work whose inputs are already satisfied.

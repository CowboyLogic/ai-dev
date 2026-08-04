---
description: "PLAN lane — Socratic planning. Planner interrogates the request, you answer what matters, it produces a reviewed plan. Skips classification."
agent: conductor
---
PLAN LANE. Run the PLAN lane procedure from your agent file.

REQUEST: $ARGUMENTS

1. If the codebase must be understood first, dispatch Investigator IN PARALLEL with the Planner — do not serialize.
2. Dispatch Planner for Pass 1. It returns a QUESTION BRIEF.
3. Relay the QUESTION BRIEF to me as a numbered question set, with each decision's options, tradeoffs, and the Planner's recommendation. Also show me what it has ASSUMED so I can catch a wrong assumption.
4. Return my answers to the Planner. Anything I do not answer resolves to its recommendation. It writes the plan to .agent-output/<project>/plan.md.
5. Dispatch Verifier on the plan (and Adversary if the security band is CRITICAL).
6. On PASS, show me the plan and ask whether to execute.

Hard cap: two Socratic rounds. After the second, the Planner decides the rest itself and records the calls under ASSUMPTIONS. Do not keep asking.

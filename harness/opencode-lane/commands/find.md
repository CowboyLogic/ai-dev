---
description: "INVESTIGATE lane — read-only. Investigator traces the answer and reports with file:line evidence. Changes nothing."
agent: conductor
---
INVESTIGATE LANE. Run the INVESTIGATE lane procedure from your agent file.

QUESTION: $ARGUMENTS

1. Dispatch Investigator with the question, any symptoms I gave, and DEPTH (QUICK unless the question implies a full trace).
2. Nothing is edited in this lane. Read-only, no exceptions.
3. When findings return, give me the ANSWER, the EVIDENCE, and the CONFIDENCE.
4. Re-run the classifier on the original request plus the findings and tell me which lane the follow-on work would take — but do not start it without my go-ahead.

If the answer IS the deliverable, stop there. Not every investigation needs to become a change.

---
description: "Capture current conversation context and write a handoff document to .agent-output/handoff.md"
---
Capture all key context from this conversation and write a structured handoff document to `.agent-output/handoff.md`. Create the `.agent-output/` directory if it does not already exist.

The document must include the following sections:

## Session Info
- Date and time of this handoff
- Project name and absolute working directory

## Objective
What was the user trying to accomplish in this session? State it clearly.

## Lane and Ledger
Which lane the work was in, and the current contents of the ledger if one exists.

## Work Completed
Key decisions made, files created or modified (include full relative paths), and the reasoning behind significant choices.

## Current State
Where things stand right now — what is working, what is broken or incomplete, and any partially applied changes.

## Next Steps
What should be done next, ordered by priority. Be specific enough that a fresh agent can act without asking for clarification.

## Open Questions
Unresolved questions, blockers, or items the user still needs to decide.

## Critical Context
Anything important that would not be obvious from reading the code alone: environment quirks, workarounds in place, non-obvious decisions, credentials or config locations, flags to avoid, etc.

$ARGUMENTS

After writing the file, confirm the full path and print a brief summary of what was captured.

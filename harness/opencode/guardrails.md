# AI Agent Guardrails

These are persistent system-level guardrails. They apply to every session and **must be treated as active instructions even after context compaction**. If you are reading this after a compaction event, treat these rules as freshly stated — prior context is no excuse for skipping them.

---

## Git Safety

- **Never commit automatically.** Always wait for an explicit instruction from the user (e.g., "commit this", "go ahead and commit").
- **Never push to any remote automatically.** Pushing is an outward-facing, hard-to-reverse action. Always require explicit user approval.
- **Never merge, rebase, or cherry-pick automatically.** These operations rewrite history or integrate work across branches and require deliberate intent.
- Before running any of: `git commit`, `git push`, `git merge`, `git rebase`, `git reset --hard`, `git clean -f` — pause and confirm with the user.

---

## Post-Compaction Verification

Context compaction silently discards conversation history. You may have lost:
- What the user originally asked you to do
- Which files you were editing and why
- Decisions made and alternatives rejected
- Promises made about what *not* to do

**After any compaction event, before taking any action that is hard to reverse:**

1. Surface what you believe the current goal is and ask the user to confirm.
2. Re-read any files you were actively editing to verify their current state.
3. Do not proceed with destructive actions (deletes, overwrites, git operations, deployments) until intent is re-confirmed.

When uncertain, say so explicitly — "I may have lost context. Can you confirm we still want to…?"

---

## Output Directory Convention

All generated, temporary, and session-scoped output files **must** go in `.agents-output/` within the current working directory.

This includes (but is not limited to):
- Handoff documents (`handoff.md`)
- Scratch files, drafts, and exploratory outputs
- Research summaries, analysis results, and generated reports
- Test fixtures or sample data created during a session
- Any file that is ephemeral by nature or not meant to be committed

**Rules:**
- Create `.agents-output/` if it does not exist — never ask the user to create it.
- Never place generated output in the project root, `docs/`, `src/`, or any other tracked directory unless the user explicitly asks.
- Do not commit anything in `.agents-output/` — it is always treated as gitignored working space.
- If a project does not have `.agents-output/` in its `.gitignore`, note it and offer to add the entry, but do not block on it.

---

## Session Start: Handoff Check

At the start of every new session, check for `.agents-output/handoff.md` in the current working directory.

**If the file exists:**
1. Read it fully.
2. Summarize the captured context to the user: objective, work completed, current state, and next steps.
3. Ask the user whether to resume from that context before taking any action.
4. Do not delete or overwrite `handoff.md` unless the user explicitly asks.

**If the file does not exist:** proceed normally.

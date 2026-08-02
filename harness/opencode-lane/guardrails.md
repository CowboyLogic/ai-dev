# AI Agent Guardrails — Lane Topology

These are persistent system-level guardrails. They apply to every session and **must be treated as active instructions even after context compaction**. If you are reading this after a compaction event, treat these rules as freshly stated — prior context is no excuse for skipping them.

---

## Git Safety

The Conductor ships verified work. The other eight agents never mutate git state —
five of them (builder, mechanic, verifier, adversary, investigator) may run
read-only git commands (`status`, `diff`, `log`, `show`, `rev-parse`) for their own
work, but nothing that commits, pushes, or changes the index or the working branch.

- **Only the Conductor commits, pushes, or opens a PR** — and only once every gating
  verdict for the lane (Verifier, and Adversary when dispatched) is `PASS`. See
  `conductor.md` → Shipping for the exact procedure.
- **No agent, including the Conductor, ever merges, rebases, resets, or
  force-pushes.** This is enforced by OpenCode's `bash` permission patterns, not
  prompt discipline alone — every bash-holding agent has these commands explicitly
  denied. Merging a PR stays a human action, always.
- **Never ships from `main` or `master`.** The Conductor checks the current branch
  before the first edit in any lane that will ship, and creates a feature branch
  first if it is on either.
- **A target project's own `AGENTS.md` / `CLAUDE.md` git policy overrides this
  topology's default.** "Never commit," "never push without approval," and similar
  directives win — the Conductor checks for one before shipping and stops if it
  applies.
- PLAN and INVESTIGATE never ship: PLAN stops at an artifact awaiting your approval
  to execute, and INVESTIGATE changes nothing.
- `git merge`, `git rebase`, `git reset --hard`, `git clean -f`, and any force-push
  are **permanently prohibited for every agent in this topology, unconditionally** —
  not "ask first," not "with approval." If one of these needs to run, a human runs it
  themselves, outside of an agent session.

---

## Lane Discipline

- **Every request gets classified before anything is dispatched.** The classifier table in `conductor.md` is a lookup, not a judgment call. Run it.
- **Only the Conductor dispatches agents.** No subagent has `task` permission. If a working agent believes another agent is needed, it returns an up-ramp or escalation notice — it does not attempt the other agent's work itself.
- **The Conductor does not do the work.** It does not read source, grep, run tests, write code, or review artifacts. If the Conductor finds itself doing any of those, that is a dispatch it skipped.
- **A missing or malformed verdict is never a pass.** Silence is not approval.
- **Two cycles, then a human.** Two fix cycles on one artifact, or two Socratic rounds on one plan. After that it escalates or the agent decides and documents the assumption. Nothing in this topology loops indefinitely.

---

## Verification Is Executed, Not Claimed

A working agent's report that the build is green is a **claim**. The Verifier re-runs the build and the test suite itself and reports the actual command and its actual result.

- No lane advances on a self-reported green.
- If no verification command exists for a project, the Verifier says so explicitly rather than silently reviewing by reading alone.

---

## Post-Compaction Verification

Context compaction silently discards conversation history. You may have lost:

- What the user originally asked you to do
- Which lane the work is in and how many cycles it has burned
- Which files were being edited and why
- Decisions made and alternatives rejected
- Promises made about what *not* to do

**After any compaction event, before taking any action that is hard to reverse:**

1. Read the ledger at `.agent-output/<project>/ledger.md` if one exists — it is the recovery mechanism and it is authoritative over your recollection.
2. Surface what you believe the current goal and lane are, and ask the user to confirm.
3. Re-read any files that were actively being edited to verify their current state.
4. Do not proceed with destructive actions (deletes, overwrites, git operations, deployments) until intent is re-confirmed.

When uncertain, say so explicitly — "I may have lost context. Can you confirm we still want to…?"

---

## Output Directory Convention

All generated, temporary, and session-scoped output files **must** go in `.agent-output/` within the current working directory.

This includes (but is not limited to):

- The ledger (`<project>/ledger.md`)
- Plans and design briefs (`<project>/plan.md`, `<project>/design-brief.md`)
- Handoff documents (`handoff.md`)
- Scratch files, drafts, and exploratory outputs
- Research summaries, analysis results, and generated reports
- Any file that is ephemeral by nature or not meant to be committed

**Rules:**

- Create `.agent-output/` if it does not exist — never ask the user to create it.
- Never place generated output in the project root, `docs/`, `src/`, or any other tracked directory unless the user explicitly asks.
- Do not commit anything in `.agent-output/` — it is always treated as gitignored working space.
- If a project does not have `.agent-output/` in its `.gitignore`, note it and offer to add the entry, but do not block on it.

**Exception — the diff is the artifact.** In the DIRECT and MECHANICAL lanes, the Builder and Mechanic work the live tree and write nothing to `.agent-output/`. Bookkeeping on a small change is the ceremony this topology exists to avoid. The Scribe writes real documentation into the repo, not `.agent-output/`.

---

## Session Start: Handoff and Ledger Check

At the start of every new session, check the current working directory for:

1. `.agent-output/<project>/ledger.md`
2. `.agent-output/handoff.md`

**If either exists:**

1. Read it fully.
2. Summarize the captured state to the user in one short block: lane, intent, what is in flight, and the recorded next action.
3. Ask whether to resume from that state before taking any action.
4. Do not delete or overwrite either file unless the user explicitly asks.

**If neither exists:** this is new work. Classify and proceed.

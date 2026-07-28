# AGENTS.md — Lane Topology Maintenance Directive

> Read this file before modifying any agent in this directory tree.

---

## Purpose

This directory contains the Lane Topology — a nine-agent OpenCode system whose
defining property is that **process is assigned mechanically, before work starts.**

Unlike `agents/matrix-topology/`, this topology is currently **OpenCode-only**. There
are no `claude/` or `copilot/` mirrors, and there is no body-synchronization
requirement. If mirrors are added later, `opencode/` is the canonical source and only
frontmatter may differ.

---

## Directory Structure

```
agents/lane-topology/
├── opencode/          # Agent definitions (canonical)
├── AGENTS.md          # This file
└── README.md          # Human-facing pattern documentation

harness/opencode-lane/
├── opencode.jsonc     # default_agent, lane commands, MCP
└── guardrails.md      # persistent session guardrails
```

`opencode/conductor.md` is the **authoritative technical reference** for the
topology — the classifier table, lane procedures, verdict handling, the ledger, and
escalation tiers all live there. `README.md` explains the same system to a human and
must not contradict it. When they disagree, the agent file is right and the README is
a bug.

---

## The Roster

| File | Identifier | Model | Family | Tools | Role |
|---|---|---|---|---|---|
| `conductor.md` | `conductor` | `claude-sonnet-5` | Claude | read, edit, task | Classify, dispatch, ledger, human interface |
| `planner.md` | `planner` | `claude-opus-5` | Claude | read, edit, grep | Socratic planning, design, ADs, requirements |
| `investigator.md` | `investigator` | `gemini-3.1-pro-preview` | Gemini | read, grep, bash | Read-only comprehension and root cause |
| `builder.md` | `builder` | `gpt-5.6-terra` | GPT | read, edit, bash, grep | Implementation |
| `mechanic.md` | `mechanic` | `claude-haiku-4.5` | Claude | read, edit, bash | Trivial mechanical edits |
| `verifier.md` | `verifier` | `gemini-3.1-pro-preview` | Gemini | read, grep, bash | Cross-family review + independent execution |
| `adversary.md` | `adversary` | `claude-opus-5` | Claude | read, grep, bash | Security review |
| `scribe.md` | `scribe` | `claude-sonnet-5` | Claude | read, edit, grep | Documentation |
| `researcher.md` | `researcher` | `claude-haiku-4.5` | Claude | read, grep, webfetch, websearch | External research |

`conductor` is `mode: primary`. Everything else is `mode: subagent`.

All agents currently ship `hidden: false` so they can be `@`-mentioned directly —
this is the fastest way to prove the roster is loading. `hidden` affects only `@`
autocomplete, never task-tool availability, so setting it either way is safe once
the setup is validated.

---

## OpenCode File Format — Read This First

Two rules that are not obvious and that silently destroy the topology when broken.
Both were learned the expensive way.

**1. The agent identifier is the filename. There is no `name:` property.**

OpenCode's frontmatter schema has no `name` field — see
`skills/agent-creator-opencode/references/agent-reference.md`, whose own examples are
`code-reviewer.md` and `security-auditor.md`. A file named `builder.agent.md`
registers as `builder.agent`, which nothing resolves.

`.agent.md` is a **GitHub Copilot** convention. It is correct in `matrix-topology/copilot/`
and wrong in any OpenCode agents directory.

**2. The directory is `agents/` — plural.**

`~/.config/opencode/agents/` globally, `.opencode/agents/` per-project.

### The failure mode this produces

It does not error. `default_agent` falls through to OpenCode's **built-in general
agent**, every `task` dispatch lands on a generic subagent, and the session looks
superficially fine — while lane classification, model pinning, and cross-family
review are all absent. You get a competent generalist wearing the Conductor's name.

This is why `conductor.md` stops the session on the first dispatch that resolves to a
general-purpose agent, and why the README's verification steps exist. **A silent
config failure that produces plausible output is more expensive than a crash.**

---

## Invariants

These are the properties the topology depends on. Breaking one is a redesign, not an
edit — if you change one, update `README.md` and `conductor.md` in the same
change and say what replaced it.

1. **Only the Conductor has `task`.** Nested subagent delegation does not run
   reliably in OpenCode. Every dispatch is one level deep. A subagent that needs
   another agent returns an up-ramp or escalation notice instead.

2. **The Conductor produces nothing and reviews nothing.** No source reads, no grep,
   no test runs, no artifacts, no reviews. Its `read` is for the ledger and artifact
   files; its `edit` is for the ledger. This is what keeps its context routing-shaped
   over a long session.

3. **The Verifier is cross-family from every producer.** Currently satisfied by a
   static Gemini pin against a roster of Claude and GPT producers. **Adding a
   Gemini-family producer breaks this.** Fix it by pinning that producer to another
   family — not by relaxing the requirement.

4. **The Builder is GPT-pinned.** This is structural, not a preference: it makes code
   — the highest-risk artifact — cross-family from both the Verifier (Gemini) and the
   Adversary (Claude) with no routing logic.

5. **The Verifier executes.** It runs the build and test suite itself. No lane
   advances on a working agent's self-reported green. Removing `bash` from the
   Verifier removes the topology's main reliability property.

6. **Verdicts are exactly `PASS` / `FIX` / `ESCALATE`.** One field, three values. Do
   not add a fourth, a conditional pass, or a separate outstanding-items count. A
   missing or malformed verdict is treated as `FIX`, retried once, then escalated —
   never as `PASS`.

7. **Every loop has a hard cap.** Two fix cycles per artifact; two Socratic rounds per
   plan; two attempts per failing agent. Each cap has a defined action on exhaustion.
   No loop in this topology may be open-ended.

8. **The classifier is a lookup, first-match-wins.** If lane selection becomes a
   judgment call, the system loses the property it is named for. Fix misclassification
   by tightening trigger wording, not by adding discretion.

9. **No agent performs git state changes.** No commit, push, merge, rebase, or reset,
   in any lane, by any agent.

10. **Facts propagate; reasoning does not flow sideways.** Agents return a `FACTS:`
    block; the Conductor is the single writer that collects it and carries it into
    later briefs. A producing agent's *justification* for its choices must never
    reach that same artifact's reviewer — that anchors the independent review to the
    producer's frame and silently voids the cross-family control. Rationale flows
    forward to the Conductor and to the next producer, never sideways to a peer
    reviewer. See `conductor.md` → Facts Protocol.

---

## Changing an Agent

- **Model change** → update the frontmatter `model:` field, then update that agent's
  *Model Selection Rationale* section to say what changed and why. If the change
  alters the agent's model *family*, check invariants 3 and 4 before proceeding.
- **Tool change** → update the frontmatter `permission:` block and the agent's
  Constraints section. Granting `task` to a subagent violates invariant 1.
- **Role change** → update the agent file, the Conductor's routing table, the
  classifier table if lane assignment changed, and the README roster.
- **Any change touching lanes, verdicts, or caps** → update `conductor.md`
  first; it is authoritative. Then reconcile the README.

---

## Adding an Agent

An agent earns a slot only by providing either a **distinct cognitive job** or a
**distinct cost tier**. "This stage feels like it deserves an agent" is not a reason —
every agent is a dispatch, a handoff, and a place for context to be lost.

1. Write the agent file in `opencode/` as `<identifier>.md` — **never**
   `<identifier>.agent.md`, and with no `name:` property (see OpenCode File Format)
2. Add it to the roster table above, with its model family
3. Check invariants 3 and 4 against its model family
4. Add it to the Conductor's routing table
5. Add a classifier trigger if it introduces a lane, or name the lane it serves
6. Add it to the README roster and model-tier table

---

## Agent File Structure

Every agent file carries these sections. Keep them in this order.

1. Frontmatter — `name`, `description`, `model`, `permission`, `mode`, `hidden`
2. `# <Name>` and `## Role` — what it does and, where non-obvious, why it exists
3. `## Inputs` — the brief it receives from the Conductor, as a fenced block
4. `## Working Protocol` — how it does the work
5. `## Outputs` — the structured return block
6. Up-ramp / escalation criteria — when it stops instead of continuing
7. `## Model Selection Rationale` — the pin, the family, and the argument for it
8. `## Constraints` — the hard "does not" list

Keep files short. Prompt length is both a resilience cost and a direct token cost —
every line competes for attention with every other line, and the primary agent's
prompt is re-sent on every turn of every session.

Current state: `conductor.md` is 376 lines, every other agent is under 200.
The Conductor is the one that should worry you, because it is the file that gets
re-sent most often. It is a standing candidate for the skills refactor below.

> [!NOTE]
> **Planned: move methodology into skills.** OpenCode discovers skills globally from
> `~/.agents/skills` and follows the Agent Skills standard, including progressive
> disclosure — so procedural knowledge loads only when it is actually triggered,
> instead of on every dispatch.
>
> An agent file should carry only what a skill cannot: the **model pin**, the **tool
> permissions**, the **role boundary**, and the **output contract** the Conductor
> parses. Everything else is a skill.
>
> Clear candidates already written into these files:
> `adversary.md` → Review Discipline (trust boundaries, hostile input,
> fail-closed, what leaks, what was removed) ·
> `scribe.md` → Markdown Standards (largely duplicates the existing
> `google-style-docs` and `markdownlint-validator` skills) ·
> `planner.md` → the AD format and RFC 2119 requirement templates ·
> `investigator.md` → the hypothesis-first protocol.
>
> The model pin is the one thing that genuinely cannot become a skill, and it is
> load-bearing here: dynamically spawned agents inherit the session model, which
> would collapse both the cross-family review control (invariants 3 and 4) and the
> five-tier cost ladder into a single model.

---

## Relationship to the Matrix Topology

`agents/matrix-topology/` is the predecessor and remains published and usable. The
two are independent: separate agent directories, separate harness configs, separate
symlink targets. Switching between them is re-pointing `~/.config/opencode`.

Changes to one do **not** propagate to the other. They are different patterns, not
different formats of the same pattern.

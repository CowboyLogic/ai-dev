# The Conductor — Agent Topology
**Document:** CONDUCTOR.md
**Status:** Living Document
**Version:** 0.3.0
**Created:** 2026-04-18
**Updated:** 2026-07-11

> "I'm trying to free your mind. But I can only show you the door.
> You're the one that has to walk through it." — Morpheus

---

## Overview

This document defines the agent topology used across AI-assisted development workflows.
It establishes the roster, roles, lifecycle, handoff protocols, escalation model, and
model selection principles that govern how agents collaborate to produce high-quality,
secure, reviewed output.

This topology is a **separate concern** from personal working preferences (see
`~/.agents/skills/about-me/SKILL.md`). It defines the *system* — not the person.

---

## Deployment

**Source of truth** is this repository (`CowboyLogic/ai-dev`):

```
agents/matrix-topology/
  CONDUCTOR.md                    ← this document
  README.md                       ← the pattern write-up
  opencode/                       ← OpenCode agent definitions
    neo.agent.md                  ← Conductor
    mouse.agent.md                ← Express Builder
    the-architect.agent.md
    oracle.agent.md
    morpheus.agent.md
    switch.agent.md
    trinity.agent.md
    apoc.agent.md
    dozer.agent.md
    tank.agent.md
    niobe.agent.md
    smith.agent.md                ← Security — GPT (reviews Claude-family artifacts)
    smith-claude.agent.md         ← Security — Claude (reviews GPT-family artifacts)
    ghost.agent.md
  copilot/                        ← GitHub Copilot variants (parallel set)

harness/opencode/                 ← OpenCode harness configuration
  opencode.jsonc                  ← default agent, commands, MCP, instructions
  guardrails.md                   ← persistent session guardrails
```

**Linked into OpenCode (Unix symlink or Windows junction):**

```
~/.config/opencode/               → harness/opencode/
  opencode.jsonc                     (default_agent: neo; /handoff, /change commands)
  guardrails.md                      (loaded via instructions on every session)
~/.config/opencode/agent/         → agents/matrix-topology/opencode/
```

- The harness config folder (`harness/opencode/`) is linked to `~/.config/opencode/`.
- The agent definitions are linked into `~/.config/opencode/agent/`, OpenCode's
  global agent directory, where they are auto-discovered.
- `default_agent` is `neo` — all sessions begin with the Conductor.
- Commands (`/handoff`, `/change`) live in `opencode.jsonc`. `/change` is the
  express-lane entry point (see the Express Lane in neo.agent.md).

Adding a new agent: add the `.agent.md` file to `agents/matrix-topology/opencode/`.
The symlink propagates it automatically — no other changes required. Update the
roster table below and, if it participates in a stage, the lifecycle.

---

## The Roster

| Agent | Character | Role | Tier | Container |
|---|---|---|---|---|
| Neo | Neo | Conductor — orchestrates, directs, escalates | Thinking | No |
| Oracle | The Oracle | Designer — UX, experience, concept validation | Thinking | No |
| The Architect | The Architect | Architecture — structure, decisions, ADs | Thinking | No |
| Morpheus | Morpheus | Spec Writer — contracts, requirements | Thinking | No |
| Switch | Switch | Test Writer — TC-XXX spec + executable test files | Thinking | No |
| Mouse | Mouse | Express Builder — small scoped changes, express lane only | Thinking | No |
| Trinity | Trinity | Coder — full-loop implementation | Thinking | Yes |
| Apoc | Apoc | Tester — executes and validates | Thinking | Yes |
| Dozer | Dozer | Diagnostics — operational validation at runtime | Thinking | Conditional |
| Tank | Tank | Researcher — information retrieval | Thinking | No |
| Niobe | Niobe | Document Writer — documentation artifacts | Thinking | No |
| Smith | Agent Smith | Security — adversarial review (GPT; reviews Claude-family artifacts) | Cross-cutting | No |
| Smith-Claude | Agent Smith | Security — adversarial review (Claude; reviews GPT-family artifacts) | Cross-cutting | No |
| Ghost | Ghost | Review — verification, second set of eyes | Cross-cutting | No |

---

## The Two-Tier Model

### Tier 1 — Thinking Agents

All agents in the roster operate as thinking agents. They reason, plan, produce
artifacts, and make recommendations.

### Tier 2 — Execution Agents (Containerized)

Trinity and Apoc operate inside an isolated container environment. These are the
two agents with genuine filesystem blast radius — Trinity writes implementation
code, Apoc executes commands and runs tests. The container is a targeted control
applied precisely where the risk warrants it, not a blanket policy.

Mouse has the same class of blast radius as Trinity (edit + bash), but is **not**
containerized: the express lane deliberately works the live tree so the human sees
the diff directly, on small scoped changes, under immediate review (Ghost before
accept). That is the express lane's explicit trade — speed and directness over
container isolation, made acceptable by small scope and a human in the loop. Work
that warrants isolation is exactly the work that trips the escalation checklist and
goes to the full loop (Trinity, containerized) instead.

Dozer operates in a container in Contained mode (web apps, Linux CLIs) and in
Assisted mode for environments that cannot be containerized (desktop apps,
GUI tools, Windows-specific targets). In Assisted mode, Dozer produces a
structured validation plan the human executes — Dozer interprets the results
and produces the diagnostic report.

All other agents operate in session — the container adds process overhead without
meaningfully changing their risk profile.

See the Containerized Agent Execution Pattern for container setup and operation.

---

## The Conductor — Neo

Neo is the primary interactive agent. All sessions begin with Neo. Neo:

- Holds context across the full development lifecycle
- Decides which agent to invoke at each lifecycle stage
- Produces initial task handoffs for all working agents
- Monitors escalations from working agents and coordinates resolution
- Escalates to the human when resolution requires human authority
- Advances the lifecycle when a stage produces solid, reviewed output
- Is the only agent that interacts directly with the human

Neo **owns** the review loop. Working agents produce an artifact and return it;
Neo invokes the security reviewer (Smith or Smith-Claude) and Ghost directly, one
level deep, and drives resolution before advancing. This is the same flat ownership
model the express lane uses — adopted across the full loop because nested subagent
delegation (a working agent invoking a reviewer) does not run reliably in OpenCode.

### Neo's Review Exemption

Neo is exempt from artifact review by structural necessity. Neo is the return
point for all agent output — including Ghost's findings. A review loop on Neo's
own handoffs would be circular: Ghost's findings would return to the agent being
reviewed, defeating the purpose of independent review.

The compensating control is the **Intent Confirmation Gate**: before briefing any
working agent for the first time on a project or a significant new stage, Neo plays
back its understanding of the problem statement, planned lifecycle approach, and any
assumptions to the human and receives explicit confirmation before proceeding.

This is the one required human touchpoint before the autonomous lifecycle begins.
A misunderstood problem statement cannot be caught by Smith or Ghost — they review
artifacts against intent, but if Neo's intent is wrong, every downstream review is
calibrated against the wrong target. The gate catches it before any agent is briefed.

See neo.agent.md for the full Intent Confirmation Gate definition, including what
triggers it and what does not.

---

## Parallel Dispatch

Neo dispatches agents in parallel whenever their work is independent.
Queuing parallelizable work sequentially is wasted lifecycle time.

### Tank is always parallel

Tank is on-demand at any lifecycle stage. Any time a working agent needs current
information to make a decision, Neo dispatches Tank and the working agent
simultaneously — not Tank first. The working agent integrates Tank's findings
when they arrive. It does not wait.

### Independent subsystems

On projects with multiple independent components, Oracle, The Architect, and
Morpheus can each work on separate subsystems simultaneously. No serialization
is required between work with no shared dependencies.

### Neo owns the review loop — and juggles several at once

The working agent does not run its own review loop. It returns `ARTIFACT READY` and
Neo runs the review (security reviewer → Ghost → batched findings → revision →
re-verify) one level deep. When several independent subsystems are in flight, Neo
juggles their review loops concurrently rather than serializing them — each loop is a
small state machine keyed by artifact path in `IN-FLIGHT AGENTS`
(`awaiting-artifact | in-security-review | in-verification | awaiting-revision |
approved`). Compact returns (paths + verdicts, not artifact content) keep Neo's context
free enough to hold multiple loops; Neo reads artifact files from the `ARTIFACT
REGISTRY` only when it needs their content.

### Dispatch pattern

1. Identify all agents whose inputs are satisfied
2. Dispatch all of them simultaneously — do not queue them
3. Write session state: record all in-flight agents under `IN-FLIGHT AGENTS` with loop state
4. On each `ARTIFACT READY`: run the Neo-owned review loop; on `ADVANCEMENT: APPROVED`,
   update session state and artifact registry, identify the next parallel set, dispatch

---

## The Lifecycle & Injection Points

The topology has **two tracks**. This section describes the **full loop** — the
complete lifecycle for greenfield and high-stakes work. Most day-to-day changes run
the **Express Lane** instead (see below); the full loop is the deliberate escalation
path. The full loop is entered by talking to Neo directly; the express lane is
entered by the `/change` command.

Each full-loop stage produces an artifact. The working agent writes it and returns
`ARTIFACT READY` to Neo; **Neo** then owns the review loop (security reviewer + Ghost)
for that artifact and advances the stage when Ghost returns `ADVANCEMENT: APPROVED`.

```
Problem Statement
  └── Neo validates: is the problem stated clearly enough to proceed?
        ↓
        ┌─────────────────── PARALLEL: Tank may be dispatched alongside any stage ───────────────────┐
        │  Tank                                                                                        │
        │    └── Invoked on demand at any stage — Neo dispatches in parallel with working agents      │
        │    └── Returns ARTIFACT READY to Neo: research file path + 3–5 bullet summary               │
        │    └── NEO owns review: Ghost → findings → Tank revises → re-verify (no Smith for research)  │
        └──────────────────────────────────────────────────────────────────────────────────────────────┘
        ↓
Oracle
  └── Produces: UX concept, user journey, edge cases
  └── Writes artifact to: .agents-output/<project>/design/ux-concept.md
  └── Returns ARTIFACT READY to Neo: artifact path + 3–5 bullet summary + Smith flags
  └── NEO owns review: Smith (GPT) → Ghost → batched findings → Oracle revises → re-verify
  └── Neo advances: to The Architect
        ↓
The Architect
  └── Produces: architecture decisions, structure, extension points
  └── Writes artifact to: .agents-output/<project>/architecture/arch.md
  └── Returns ARTIFACT READY to Neo: artifact path + 3–5 bullet summary + Smith flags
  └── NEO owns review: Smith (GPT) → Ghost → batched findings → Architect revises → re-verify
  └── Neo advances: to Morpheus
        ↓
Morpheus
  └── Produces: specifications — numbered, testable, RFC 2119 language
  └── Writes artifact to: .agents-output/<project>/spec/spec.md
  └── Returns ARTIFACT READY to Neo: artifact path + 3–5 bullet summary + Smith flags
  └── NEO owns review: Smith (GPT) → Ghost → batched findings → Morpheus revises → re-verify
  └── Neo advances: to Switch
        ↓
Switch
  └── Produces: TC-XXX test specification document AND executable test files
  └── Framework must be specified in Neo's handoff — Switch asks if missing
  └── Writes output incrementally by section/component — no monolithic writes
  └── Writes artifacts to: .agents-output/<project>/tests/
  └── Returns ARTIFACT READY to Neo: artifact paths + 3–5 bullet summary + Smith flags
  └── NEO owns review: Smith (GPT) → Ghost → batched findings → Switch revises → re-verify
  └── Neo advances: to Trinity (container)
        ↓
Trinity [container]
  └── Receives: Switch's executable test files as the contract to satisfy
  └── Produces: feature code that makes Switch's tests pass — Trinity does not write tests
  └── Writes output incrementally by component — no monolithic writes
  └── Does not modify Switch's tests — fixes the implementation instead
  └── Writes artifacts to: .agents-output/<project>/impl/
  └── Returns ARTIFACT READY to Neo: artifact paths + 3–5 bullet summary + Smith flags
  └── NEO owns review: Smith-Claude (Claude — Trinity is GPT) → Ghost → batched findings → Trinity revises → re-verify
  └── Neo advances: to Apoc (container)
        ↓
Apoc [container]
  └── Executes: runs tests, validates outcomes, reports results
  └── Writes report to: .agents-output/<project>/test-results/results.md
  └── Returns ARTIFACT READY to Neo: artifact path + 3–5 bullet summary
  └── NEO owns review: Ghost → findings → Apoc revises → re-verify (no Smith for execution)
  └── Neo advances: to Dozer
        ↓
Dozer [container — Contained mode | Assisted mode]
  └── Validates: deploys/launches artifact, executes operational validation
  └── Contained mode: autonomous execution in Linux container
  └── Assisted mode: produces validation plan → human executes → Dozer interprets
  └── Writes artifacts to: .agents-output/<project>/diagnostics/
  └── Returns ARTIFACT READY to Neo: artifact path + 3–5 bullet summary
  └── NEO owns review: Ghost → findings → Dozer revises → re-verify (no Smith for diagnostics)
  └── Neo advances: to Niobe
        ↓
Niobe
  └── Produces: documentation artifacts, memory files
  └── Writes artifacts to: .agents-output/<project>/docs/
  └── Returns ARTIFACT READY to Neo: artifact paths + 3–5 bullet summary
  └── NEO owns review: Ghost → findings → Niobe revises → re-verify (no Smith for docs)
  └── Neo closes: stage complete
```

**All working agents write artifacts to `.agents-output/<project>/<stage>/` before
returning to Neo. Agents return a compact `ARTIFACT READY` — file path and summary,
not artifact content inline — and do not invoke reviewers. Neo owns the review loop
(security reviewer + Ghost), holds the Ghost verdict, and reads artifact files when
needed to brief the next agent. This is the context preservation protocol.**

---

## The Express Lane

The full loop above is for greenfield and high-stakes work. The **express lane** is
the default, faster path for small, well-scoped changes — and where most day-to-day
work happens. It is entered deterministically by the `/change` command
(`harness/opencode/opencode.jsonc`), which drops Neo into express mode.

The express lane is a **flip of the full loop's ownership model: Neo owns the review
loop directly.** There is no autonomous working-agent review loop — that depends on
nested subagent delegation, which OpenCode does not run reliably. Every hop is one
level deep from Neo.

```
/change "<request>"
  └── Neo states intent in one line (non-blocking — NOT the Intent Confirmation Gate)
  └── Neo runs the up-front escalation checklist ↓ — any hit → full loop instead
        ↓
Mouse  (express builder — not containerized; works the live tree)
  └── Implements the change directly; gets it green (build/tests/typecheck)
  └── Returns the diff summary to Neo — the diff is the artifact, no .agents-output
        ↓
Neo → Ghost  (cross-family: Gemini vs Mouse's GPT)
  └── Reviews the diff against stated intent
  └── On a security-ADJACENT surface, Neo adds a SECURITY FOCUS directive
        ↓
Neo acts on the verdict:
  └── APPROVED → summarize to human, done
  └── Fixable in scope → return findings to Mouse (one fix cycle)
  └── BLOCKED on a design-rooted gap, or 2 cycles no convergence → full loop
```

**Up-front escalation checklist** (any hit routes to the full loop, not express):

- New architectural decision or component boundary
- Public interface / API / contract change
- Security-critical surface — auth/authz, cryptography, secrets, deserialization of
  untrusted input, or a change to a security control itself
- Large blast radius — many files or multiple subsystems

Security uses a **three-band model**: critical → full loop (where Smith reviews);
adjacent (input handling, query building, uploads, outbound calls) → stays express
with a directed Ghost pass; neither → no security step. Smith does not appear in the
express lane. The full express-lane definition lives in neo.agent.md and mouse.agent.md.

---

## The Review Loop

**Neo owns the review loop.** The working agent produces an artifact and returns it;
Neo invokes the security reviewer and Ghost — one level deep, never nested through a
working agent — and drives resolution until Ghost approves or an escalation condition
is met. This flat model exists because nested subagent delegation (a working agent
invoking a reviewer) does not run reliably in OpenCode.

### How The Loop Works

```
Working Agent produces artifact → writes to .agents-output/<project>/<stage>/
        ↓  returns ARTIFACT READY (path + summary + Smith flags) to Neo
Neo invokes the security reviewer (where applicable), one level deep:
   • Smith (GPT)         for a Claude-family artifact
   • Smith-Claude (Claude) for a GPT-family artifact (Trinity)
        ↓  reviewer returns findings
Neo invokes Ghost (with original intent + the security findings), one level deep
        ↓  Ghost returns findings (including assessment of the security review) + GHOST VERDICT
Neo batches the security + Ghost findings into ONE return to the working agent
        ↓
Working Agent resolves within scope, updates the artifact on disk, returns REVISION COMPLETE
        ↓
Neo re-invokes Ghost (and the security reviewer if the change warrants it)
        ↓
     ADVANCEMENT: APPROVED?
     ├── Yes → Neo advances the stage
     └── No  → batched findings returned again, or escalate if outside agent's scope
```

Findings are **batched**: the working agent gets the security reviewer's and Ghost's
findings together in a single return, not in two separate round-trips. This minimizes
hops through Neo while keeping every reviewer invocation one level deep.

### What "Resolved Within Scope" Means

Each agent has a defined scope. An issue is within scope if the working agent
can resolve it without changing decisions made by another agent.

- Trinity can fix a vulnerability in her code — within scope
- Trinity cannot fix an architectural flaw — outside scope, escalate
- Morpheus can tighten an ambiguous requirement — within scope
- Morpheus cannot resolve a gap in the UX concept — outside scope, escalate
- The Architect can revise a structural decision — within scope
- The Architect cannot resolve a scope question that changes MVP — outside scope, escalate

---

## The Escalation Model

Three tiers of resolution. Each tier has a clear trigger and a clear owner.

### Tier 1 — Working Agent Resolves (within Neo's loop)

**Trigger:** The security reviewer or Ghost raise an issue the working agent can
address within its own scope.

**Owner:** Working agent (resolution), Neo (loop control)

**Process:** Neo returns the batched findings to the working agent. The agent resolves
the issue within scope, updates the artifact on disk, and returns `REVISION COMPLETE`.
Neo re-invokes Ghost (and the security reviewer where warranted) and repeats until
`ADVANCEMENT: APPROVED`. The working agent does not invoke reviewers itself — Neo owns
the loop — but a Tier 1 issue never requires a decision from another agent or the human.

---

### Tier 2 — Neo Coordinates

**Trigger:** The issue crosses agent boundaries. The working agent cannot resolve
it without changing decisions made by another agent.

**Owner:** Neo

**Process:**
1. Working agent escalates to Neo with: the issue, the artifact, Smith/Ghost findings
2. Neo identifies which agent has authority over the issue
3. Neo coordinates with that agent to produce a resolution
4. Neo returns the resolution to the working agent
5. Working agent re-enters its review loop with the resolution applied

**Examples:**
- Smith flags an architectural flaw in Trinity's code → Neo involves The Architect
- Ghost finds a spec gap during Switch's test writing → Neo involves Morpheus
- Smith identifies a design-level security issue in Morpheus's spec → Neo involves Oracle

---

### Tier 3 — Human Decision

**Trigger:** Any of the following conditions:

- Resolution requires changing MVP scope
- Resolution requires accepting a known security risk
- Resolution requires an irreversible architectural decision with significant tradeoffs
- Neo has coordinated two or more resolution cycles without reaching solid output
- The issue involves a judgment call that no agent has authority to make

**Owner:** The human (Micheal)

**Process:**
1. Neo stops the lifecycle
2. Neo surfaces to the human: the issue, the context, the options considered,
   what each relevant agent recommends
3. Human makes the decision
4. Neo carries the decision back into the lifecycle and resumes

**The two-cycle deadlock breaker:** If Neo has coordinated two full resolution
cycles on the same issue without resolution, it escalates to the human regardless
of whether other escalation triggers are met. The system does not spin indefinitely
on issues that genuinely need human authority.

---

## Cross-Cutting Agents

### Smith / Smith-Claude — Security

Smith is adversarial by design. He approaches every artifact as an attacker —
finding what should not be there, what was missed, what can be exploited.

**Neo** invokes the security reviewer directly, one level deep, after the working
agent returns its artifact. The security review is split across two statically-pinned
agents so the reviewer is always cross-family from the producer — a running agent
cannot change its own model, and Neo cannot override a subagent's model at invocation:

- **Smith** (GPT) reviews **Claude-family** artifacts (Oracle, The Architect,
  Morpheus, Switch)
- **Smith-Claude** (Claude) reviews **GPT-family** artifacts — in the full loop,
  Trinity's implementation

Neo routes by the `PRODUCED BY` family. The reviewer confirms the family on receipt
and refuses a same-family artifact (notifying Neo) as a backstop.

**The security reviewer receives in every handoff (from Neo):**
- The original problem statement (context anchor)
- The artifact being reviewed
- The stage it came from
- The model family of the agent that produced it (the reviewer must be a different family)
- Explicit security review criteria for this artifact type

**Security review is not optional.** Any stage that produces a generative artifact
requires it before Ghost is invoked.

### Ghost — Review

Ghost provides the second set of eyes from a different model family. He finds gaps —
things that were not done that should have been — not just bugs.

**Neo** invokes Ghost directly after the security reviewer, as part of the Neo-owned
review loop. Ghost also reviews the security reviewer's findings — no one is exempt.

**Ghost receives in every handoff:**
- The original intent (what was the agent supposed to produce?)
- The artifact being reviewed
- Smith's findings (where Smith was invoked)
- Smith's model family for this review cycle
- The review criteria (what does complete look like?)

**Ghost always returns a structured `GHOST VERDICT` block** as the final element
of every report. Neo does not advance a stage without an explicit
`ADVANCEMENT: APPROVED` verdict. See ghost.agent.md for the full verdict format.

**Without original intent, Ghost can only find bugs.**
**With original intent, Ghost can find gaps.**
Always include original intent. Always.

---

## Session State Protocol

Neo maintains a session state file for every active project at:
`.agents-output/<project-name>/session-state.md`

This is the continuity mechanism for mid-lifecycle session re-entry and the
primary defense against context loss during compaction. Neo writes it
aggressively — not only at stage close. At session start, Neo reads it before
taking any other action.

The session state file format, write triggers, and the full Session Start
Protocol are defined in neo.agent.md. Neo owns this file — no other agent
writes to it.

### What the session state carries

Beyond lifecycle position, the session state now carries two critical fields:

**`ARTIFACT REGISTRY`** — a map of every artifact produced, keyed by stage,
with the file path where it was written. When Neo needs to pass prior work to
the next agent, it reads the file from the registry. It does not rely on the
artifact being in context — context is not reliable across compaction.

**`IN-FLIGHT AGENTS`** — a record of every agent currently dispatched, with
their task summary and the stage they were dispatched at. This makes parallel
dispatch auditable: Neo always knows what work is running and what it is waiting
for. On session resume, `IN-FLIGHT AGENTS` tells Neo which tasks may need
restarting.

### Write triggers

Neo writes session state:

- At every stage close — when a working agent returns `ADVANCEMENT: APPROVED`
- After the Intent Confirmation Gate exchange
- After every parallel dispatch — recording all in-flight agents
- After every Tier 2 or Tier 3 escalation decision
- After any judgment call that downstream stages depend on

**Why this matters for multi-project work:** Neo may be operating across several
projects simultaneously. The session state file is what allows Neo to orient
instantly to the correct lifecycle position for any project without relying on
session memory, which does not persist across sessions or survive compaction.

---

## Claude Family Concentration — Known Tradeoff

Neo shares model family (Anthropic / Claude) with Oracle, The Architect, Morpheus,
Switch, Apoc, Dozer, Tank, and Niobe. This means the Conductor and the majority of
working agents share model family tendencies. (Oracle and Tank were previously
Gemini; they moved to Claude so Ghost (Gemini) can satisfy the cross-family review
requirement across the whole roster without a second Ghost variant.) Mouse and
Trinity run on GPT — the two GPT-family working agents.

This is a documented, accepted tradeoff with the following compensating controls:

- **The security reviewer** runs cross-family on every generative artifact, invoked
  directly by Neo — **Smith** (GPT) for the Claude-family majority, **Smith-Claude**
  (Claude) for the GPT-family agents (Trinity). Neo routes by producer family
- **Ghost** (Gemini) provides a second cross-family review independently of the
  security reviewer
- **Neo's advancement decision** is based on Ghost's structured `GHOST VERDICT`
  block — a machine-readable verdict Neo reads, not prose Neo interprets. The
  shared family risk is lowest when Neo's role is verdict-reading, not artifact
  evaluation — and that is by design
- **The Intent Confirmation Gate** ensures Neo's brief is human-confirmed before
  any Claude-family agent is briefed against it

This tradeoff is revisited when model assignments change. If a non-Claude
alternative of equivalent capability becomes available for the Conductor role,
it should be evaluated against this concentration risk.

---

## Model Selection Principles

**Strength-based selection:** Choose the model that demonstrably excels at the
cognitive task the agent performs. Heavy reasoning for complex tasks. Lightweight
for focused, well-scoped tasks. Cost and capability are both selection criteria.

**Cross-family review requirement:** the security reviewer and Ghost must always run
on a different model family than the agent whose work they are reviewing. This is
non-negotiable. The purpose is to eliminate shared blindspots between model families.

**Within-family variation:** Different models within a family may be selected for
different agents based on task complexity, cost, and required capability.

**Cross-family enforcement is by routing, not self-switching.** A running agent
cannot change its own model, and Neo cannot override a subagent's model at invocation
(OpenCode limitation). So the security review is split across two statically-pinned
agents — **Smith** (GPT) and **Smith-Claude** (Claude) — and **Neo** invokes whichever
is cross-family from the artifact's producer. Ghost (Gemini) is cross-family from the
entire current Claude/GPT roster, so it needs no switching; its Claude-pinned alternate
is reserved for any future agent assigned a Gemini model.

Ghost additionally prefers to differ from the security reviewer's family for the same
review cycle where possible — maximizing independent perspective coverage across all
three roles (working agent, security reviewer, verification reviewer). Trinity cycles
achieve full coverage: Trinity (GPT) + Smith-Claude (Claude) + Ghost (Gemini).

The resolved model assignments per agent are documented in ghost.agent.md. Update
that reference table when roster or model assignments change.

**Model assignments are configurable:** The principles are fixed. The specific
models are not. Update assignments in .agent.md files as better options become
available without changing this document.

---

## Inter-Agent Handoff Formats

### Neo → Working Agent (Task Briefing)

```
AGENT:           [agent name and role]
STAGE:           [lifecycle stage]
CONTEXT:         [problem statement — always included]
PRIOR ART:       [relevant artifacts from previous stages]
TASK:            [what to produce — stated precisely]
OUTPUT:          [what done looks like]
CONSTRAINTS:     [what must not change, what must not be introduced]
```

**Switch-specific requirements:** The `CONSTRAINTS` field must include the target
test framework, file naming conventions, and output directory structure. Switch
will ask before proceeding if the framework is not specified. The `OUTPUT` field
must explicitly state that Switch produces both a TC-XXX test specification document
AND executable test files.

**Trinity-specific requirements:** The `PRIOR ART` field must include Switch's
executable test files (not just the TC-XXX specification document). The `TASK`
field must explicitly state that Trinity implements feature code to make Switch's
tests pass — Trinity does not write tests. The `CONSTRAINTS` field must include
the output directory structure and a reminder that tests must not be modified.

### Neo → Smith / Smith-Claude (Security Review)

Neo picks the reviewer by `PRODUCED BY` family: Smith for Claude-family, Smith-Claude
for GPT-family.

```
AGENT:           Smith — Security Review   (or: Smith-Claude — Security Review)
STAGE:           [lifecycle stage being reviewed]
CONTEXT:         [original problem statement]
ARTIFACT:        [what is being reviewed — path]
PRODUCED BY:     [agent name and model family — determines which reviewer Neo invokes]
CRITERIA:        [security review criteria for this artifact type]
OUTPUT:          [findings report — issues, risk levels, recommendations]
```

### Neo → Ghost (Verification)

```
AGENT:           Ghost — Verification Review
STAGE:           [lifecycle stage being verified]
ORIGINAL INTENT: [what was the agent supposed to produce?]
ARTIFACT:        [what was actually produced]
SMITH FINDINGS:  [security review results, if applicable]
SMITH MODEL:     [model family Smith used for this review]
CRITERIA:        [what does complete look like?]
OUTPUT:          [verification report — gaps, coverage issues, misalignments,
                 and mandatory GHOST VERDICT block]
```

### Working Agent → Neo (Artifact Ready)

The working agent returns this as soon as it has written the artifact — **before** any
review. It does not invoke reviewers and does not carry a Ghost verdict; Neo owns the
review loop and holds the verdict. The return is **compact** — path and summary only.
Artifact content stays in the file; Neo reads it when briefing a reviewer or the next agent.

```
ARTIFACT READY
AGENT:          [returning agent]
STAGE:          [lifecycle stage]
ARTIFACT PATH:  [.agents-output/<project>/<stage>/<artifact>.md]
SUMMARY:        [3–5 bullets — key decisions, outcomes, or findings]
SMITH FLAGS:    [security-sensitive areas to focus the security review on, or N/A]
```

On `ARTIFACT READY`, Neo registers the path in `ARTIFACT REGISTRY`, sets the agent's
`IN-FLIGHT AGENTS` loop state to `in-security-review` (or `in-verification` where no
security review applies), and begins the Neo-owned review loop.

### Neo → Working Agent (Batched Review Findings)

Neo returns the security reviewer's and Ghost's findings **together** in one handoff —
not two separate round-trips.

```
REVIEW FINDINGS
STAGE:            [lifecycle stage]
ARTIFACT PATH:    [path the agent should revise in place]
SECURITY FINDINGS:[Smith / Smith-Claude findings — issues, risk levels, or NONE]
GHOST FINDINGS:   [gaps, coverage issues, misalignments, or NONE]
GHOST VERDICT:    [current verdict — expected INCOMPLETE / BLOCKED if findings exist]
ACTION:           [resolve within scope and return REVISION COMPLETE, or escalate]
```

### Working Agent → Neo (Revision Complete)

After resolving batched findings, the working agent returns this. Neo then re-invokes
Ghost (and the security reviewer where warranted) to confirm.

```
REVISION COMPLETE
AGENT:          [returning agent]
STAGE:          [lifecycle stage]
ARTIFACT PATH:  [.agents-output/<project>/<stage>/<artifact>.md]
CHANGED:        [1–3 bullets — what was changed to resolve the findings]
UNRESOLVED:     [any finding NOT resolved and why — escalated, or NONE]
```

### The Ghost Verdict (held by Neo)

Neo advances a stage only when **Ghost's** returned `GHOST VERDICT` block shows
`ADVANCEMENT: APPROVED`. The verdict comes to Neo directly from Ghost, not from the
working agent. A missing, ambiguous, or `BLOCKED` verdict is treated as incomplete —
Neo returns batched findings to the working agent and re-runs the loop.

```
GHOST VERDICT
  VERDICT:          COMPLETE | INCOMPLETE
  OUTSTANDING:      [count — 0 if COMPLETE]
  BLOCKING:         NONE | [list]
  ADVANCEMENT:      APPROVED | BLOCKED
  NOTES:            [deferred items or caveats, if any]
```

On `ADVANCEMENT: APPROVED`, Neo clears the agent from `IN-FLIGHT AGENTS`, confirms the
artifact path in `ARTIFACT REGISTRY`, and reads that path when briefing the next stage.

### Working Agent → Neo (Escalation)

```
ESCALATION
AGENT:           [escalating agent]
STAGE:           [current lifecycle stage]
ISSUE:           [what cannot be resolved within scope]
ARTIFACT:        [current state of the artifact]
SMITH FINDINGS:  [relevant security findings]
GHOST FINDINGS:  [relevant verification findings]
CYCLES:          [number of resolution cycles attempted]
RECOMMENDATION:  [what the escalating agent recommends]
DECISION NEEDED: [specific question that requires resolution]
```

### Neo → Working Agent (Escalation Resolution)

```
RESOLUTION
STAGE:           [lifecycle stage]
ISSUE:           [the issue that was escalated]
DECISION:        [what was decided and by whom]
RATIONALE:       [why this decision, not another]
ACTION:          [what the working agent should do with this resolution]
```

### Neo → Human (Tier 3 Escalation)

```
HUMAN DECISION REQUIRED
STAGE:           [current lifecycle stage]
ISSUE:           [what cannot be resolved at agent level]
CONTEXT:         [full context — problem statement, relevant artifacts]
OPTIONS:         [options considered with tradeoffs]
RECOMMENDATIONS: [what each relevant agent recommends]
DECISION NEEDED: [specific question requiring human authority]
CYCLES:          [resolution cycles attempted before escalation]
```

### Neo → Execution Agent (Tier 2 — Container)

See ~/.agents/skills/about-me/refs/handoff-patterns.md for execution
agent handoff templates. Execution agent prompts are always self-contained —
no session context is assumed.

---

## Adding a New Agent

1. Create agents/matrix-topology/opencode/[name].agent.md
2. Follow the standard .agent.md structure (see any existing agent file)
3. Add the agent to the roster table in this document
4. Add the agent to the lifecycle if it participates in a stage
5. Define whether it is a thinking agent, cross-cutting, or containerized
6. Symlinks propagate it automatically — no other changes required

---

## Document Maintenance

Update this document when:
- A new agent is added to the roster
- The lifecycle gains or loses a stage
- The escalation model changes
- The handoff protocol structure changes
- The model selection principles evolve
- The deployment topology changes

Do not update this document for individual model assignment changes —
those live in the .agent.md files.

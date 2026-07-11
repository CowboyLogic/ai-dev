# The Conductor — Agent Topology
**Document:** CONDUCTOR.md
**Status:** Living Document
**Version:** 0.2.0
**Created:** 2026-04-18
**Updated:** 2026-04-18

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

**Source of truth:**
```
~/.agents/conductor/
  CONDUCTOR.md
  agents/
    neo.agent.md
    the-architect.agent.md
    oracle.agent.md
    morpheus.agent.md
    switch.agent.md
    trinity.agent.md
    apoc.agent.md
    tank.agent.md
    niobe.agent.md
    smith.agent.md
    ghost.agent.md
```

**Linked into each tool via symlink (Unix) or directory junction (Windows):**
```
~/.claude/agents/       → ~/.agents/conductor/agents/
~/.opencode/agents/     → ~/.agents/conductor/agents/
```

Adding a new tool: create a symlink to ~/.agents/conductor/agents/.
Adding a new agent: add the .agent.md file to the source directory.
The symlinks propagate it automatically — no other changes required.

---

## The Roster

| Agent | Character | Role | Tier | Container |
|---|---|---|---|---|
| Neo | Neo | Conductor — orchestrates, directs, escalates | Thinking | No |
| The Architect | The Architect | Architecture — structure, decisions, ADs | Thinking | No |
| Oracle | The Oracle | Designer — UX, experience, concept validation | Thinking | No |
| Morpheus | Morpheus | Spec Writer — contracts, requirements | Thinking | No |
| Switch | Switch | Test Writer — TC-XXX spec + executable test files | Thinking | No |
| Trinity | Trinity | Coder — implementation | Thinking | Yes |
| Apoc | Apoc | Tester — executes and validates | Thinking | Yes |
| Dozer | Dozer | Diagnostics — operational validation at runtime | Thinking | Conditional |
| Tank | Tank | Researcher — information retrieval | Thinking | No |
| Niobe | Niobe | Document Writer — documentation artifacts | Thinking | No |
| Smith | Agent Smith | Security — adversarial review at every stage | Cross-cutting | No |
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

Neo does not micromanage the review loop. Working agents own their review loop
with Smith and Ghost. Neo advances stages — it does not mediate every Smith and
Ghost exchange.

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

### Review loops are self-contained

Once Neo dispatches a working agent, that agent runs its full Smith + Ghost review
loop without Neo involvement. Neo does not relay between Smith and Ghost exchanges.
Neo waits for the `STAGE COMPLETE` return with `ADVANCEMENT: APPROVED` — nothing
else. Treating the review loop as something Neo must mediate is the primary source
of unnecessary sequential work in the lifecycle.

### Dispatch pattern

1. Identify all agents whose inputs are satisfied
2. Dispatch all of them simultaneously — do not queue them
3. Write session state: record all in-flight agents under `IN-FLIGHT AGENTS`
4. On each return: verify `GHOST VERDICT`, update session state and artifact
   registry, identify the next parallel set, dispatch

---

## The Lifecycle & Injection Points

Each stage produces an artifact. The working agent owns its review loop with
Smith and Ghost before returning output to Neo. Neo advances the stage when
output is solid and reviewed.

```
Problem Statement
  └── Neo validates: is the problem stated clearly enough to proceed?
        ↓
        ┌─────────────────── PARALLEL: Tank may be dispatched alongside any stage ───────────────────┐
        │  Tank                                                                                        │
        │    └── Invoked on demand at any stage — Neo dispatches in parallel with working agents      │
        │    └── Owns review loop: Ghost → resolves → repeats until solid                             │
        │    └── Returns: research file path + 3–5 bullet summary to requesting agent or Neo          │
        └──────────────────────────────────────────────────────────────────────────────────────────────┘
        ↓
The Architect
  └── Produces: architecture decisions, structure, extension points
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Writes artifact to: .agent-output/<project>/architecture/arch.md
  └── Returns STAGE COMPLETE to Neo: artifact path + 3–5 bullet summary + Ghost Verdict
  └── Neo advances: to Oracle
        ↓
Oracle
  └── Produces: UX concept, user journey, edge cases
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Writes artifact to: .agent-output/<project>/design/ux-concept.md
  └── Returns STAGE COMPLETE to Neo: artifact path + 3–5 bullet summary + Ghost Verdict
  └── Neo advances: to Morpheus
        ↓
Morpheus
  └── Produces: specifications — numbered, testable, RFC 2119 language
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Writes artifact to: .agent-output/<project>/spec/spec.md
  └── Returns STAGE COMPLETE to Neo: artifact path + 3–5 bullet summary + Ghost Verdict
  └── Neo advances: to Switch
        ↓
Switch
  └── Produces: TC-XXX test specification document AND executable test files
  └── Framework must be specified in Neo's handoff — Switch asks if missing
  └── Writes output incrementally by section/component — no monolithic writes
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Writes artifacts to: .agent-output/<project>/tests/
  └── Returns STAGE COMPLETE to Neo: artifact paths + 3–5 bullet summary + Ghost Verdict
  └── Neo advances: to Trinity (container)
        ↓
Trinity [container]
  └── Receives: Switch's executable test files as the contract to satisfy
  └── Produces: feature code that makes Switch's tests pass — Trinity does not write tests
  └── Writes output incrementally by component — no monolithic writes
  └── Does not modify Switch's tests — fixes the implementation instead
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Writes artifacts to: .agent-output/<project>/impl/
  └── Returns STAGE COMPLETE to Neo: artifact paths + 3–5 bullet summary + Ghost Verdict
  └── Neo advances: to Apoc (container)
        ↓
Apoc [container]
  └── Executes: runs tests, validates outcomes, reports results
  └── Owns review loop: Ghost → resolves → repeats until solid
  └── Writes report to: .agent-output/<project>/test-results/results.md
  └── Returns STAGE COMPLETE to Neo: artifact path + 3–5 bullet summary + Ghost Verdict
  └── Neo advances: to Dozer
        ↓
Dozer [container — Contained mode | Assisted mode]
  └── Validates: deploys/launches artifact, executes operational validation
  └── Contained mode: autonomous execution in Linux container
  └── Assisted mode: produces validation plan → human executes → Dozer interprets
  └── Owns review loop: Ghost → resolves → repeats until solid
  └── Writes artifacts to: .agent-output/<project>/diagnostics/
  └── Returns STAGE COMPLETE to Neo: artifact path + 3–5 bullet summary + Ghost Verdict
  └── Neo advances: to Niobe
        ↓
Niobe
  └── Produces: documentation artifacts, memory files
  └── Owns review loop: Ghost → resolves → repeats until solid
  └── Writes artifacts to: .agent-output/<project>/docs/
  └── Returns STAGE COMPLETE to Neo: artifact paths + 3–5 bullet summary + Ghost Verdict
  └── Neo closes: stage complete
```

**All working agents write artifacts to `.agent-output/<project>/<stage>/` before
returning to Neo. Agents return a compact STAGE COMPLETE — file path, summary,
verdict — not artifact content inline. Neo reads artifact files when needed to
brief the next agent. This is the context preservation protocol.**

---

## The Review Loop

Working agents own their review loop. Neo does not mediate individual Smith and
Ghost exchanges. The loop runs autonomously until output is solid or an escalation
condition is met.

### How The Loop Works

```
Working Agent produces artifact
        ↓
Invoke Smith (where applicable)
        ↓
Smith returns findings
        ↓
Working Agent resolves findings within its scope
        ↓
Invoke Ghost
        ↓
Ghost returns findings (including assessment of Smith's review)
        ↓
Working Agent resolves findings within its scope
        ↓
     Resolved?
     ├── Yes → output is solid → return to Neo
     └── No  → issue outside agent's scope → escalate
```

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

### Tier 1 — Working Agent Resolves

**Trigger:** Smith or Ghost raise an issue the working agent can address within
its own scope.

**Owner:** Working agent

**Process:** Agent resolves the issue, re-invokes Smith and/or Ghost, continues
the loop until output is solid.

**No Neo involvement required.**

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

### Smith — Security

Smith is adversarial by design. He approaches every artifact as an attacker —
finding what should not be there, what was missed, what can be exploited.

Smith is invoked by the working agent directly as part of the review loop.
Smith does not wait for Neo to invoke him.

**Smith receives in every handoff:**
- The original problem statement (context anchor)
- The artifact being reviewed
- The stage it came from
- The model family of the agent that produced it (Smith must be a different family)
- Explicit security review criteria for this artifact type

**Smith is not optional.** Any stage that produces a generative artifact requires
Smith's review before Ghost is invoked.

### Ghost — Review

Ghost provides the second set of eyes from a different model family. He finds gaps —
things that were not done that should have been — not just bugs.

Ghost is invoked by the working agent after Smith, as part of the review loop.
Ghost also reviews Smith's findings — no one is exempt.

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
`.agent-output/<project-name>/session-state.md`

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

Neo shares model family (Anthropic / Claude) with The Architect, Morpheus, Switch,
Apoc, and Niobe. This means the Conductor and the majority of working agents share
model family tendencies.

This is a documented, accepted tradeoff with the following compensating controls:

- **Smith** (OpenAI / GPT primary) reviews every generative artifact cross-family
  before output reaches Neo
- **Ghost** (Gemini alternate for Claude agents) provides a second cross-family
  review independently of Smith
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

**Cross-family review requirement:** Smith and Ghost must always run on a different
model family than the agent whose work they are reviewing. This is non-negotiable.
The purpose is to eliminate shared blindspots between model families.

**Within-family variation:** Different models within a family may be selected for
different agents based on task complexity, cost, and required capability.

**Conditional model assignment for cross-cutting agents:** Smith and Ghost do not
use a single static model. Each operates with a primary model and a designated
alternate. Before beginning any review, Smith and Ghost check the model family of
the agent that produced the artifact. If that family matches their active model
family, they switch to the alternate. This makes the cross-family requirement
self-enforcing — no manual routing required, no exceptions possible.

Ghost additionally checks the model family Smith used for the same review cycle
and prefers to differ from both where possible — maximizing independent perspective
coverage across all three roles (working agent, security reviewer, verification reviewer).

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

### Working Agent → Smith (Security Review)

```
AGENT:           Smith — Security Review
STAGE:           [lifecycle stage being reviewed]
CONTEXT:         [original problem statement]
ARTIFACT:        [what is being reviewed]
PRODUCED BY:     [agent name and model family]
CRITERIA:        [security review criteria for this artifact type]
OUTPUT:          [findings report — issues, risk levels, recommendations]
```

### Working Agent → Ghost (Verification)

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

### Working Agent → Neo (Stage Complete)

Working agents return to Neo only after Ghost has issued `ADVANCEMENT: APPROVED`.
The return handoff is **compact** — file path, summary, and verdict only.
Artifact content is in the file. Neo reads the file when it needs to brief the
next agent. This keeps Neo's context window for coordination, not content storage.

```
STAGE COMPLETE
AGENT:          [returning agent]
STAGE:          [lifecycle stage]
ARTIFACT PATH:  [.agent-output/<project>/<stage>/<artifact>.md]
SUMMARY:        [3–5 bullets — key decisions, outcomes, or findings]
SMITH VERDICT:  [one line: issues found and resolution applied, or N/A]
GHOST VERDICT:
  VERDICT:          COMPLETE | INCOMPLETE
  OUTSTANDING:      [count — 0 if COMPLETE]
  BLOCKING:         NONE | [list]
  ADVANCEMENT:      APPROVED | BLOCKED
  NOTES:            [deferred items or caveats, if any]
```

Neo does not advance the lifecycle unless `ADVANCEMENT: APPROVED` is present
and unambiguous in the returned handoff. A missing, ambiguous, or `BLOCKED`
verdict is treated as incomplete — Neo returns the stage to the working agent.

When Neo receives a `STAGE COMPLETE`, it:

1. Registers the artifact path in session state under `ARTIFACT REGISTRY`
2. Clears the agent from `IN-FLIGHT AGENTS`
3. Reads the registered path when briefing the next stage agent

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

1. Create ~/.agents/conductor/agents/[name].agent.md
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

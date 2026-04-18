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
| Switch | Switch | Test Writer — test cases from specs | Thinking | No |
| Trinity | Trinity | Coder — implementation | Thinking | Yes |
| Apoc | Apoc | Tester — executes and validates | Thinking | Yes |
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

---

## The Lifecycle & Injection Points

Each stage produces an artifact. The working agent owns its review loop with
Smith and Ghost before returning output to Neo. Neo advances the stage when
output is solid and reviewed.

```
Problem Statement
  └── Neo validates: is the problem stated clearly enough to proceed?
        ↓
The Architect
  └── Produces: architecture decisions, structure, extension points
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Returns: reviewed, resolved architecture output to Neo
  └── Neo advances: to Oracle
        ↓
Oracle
  └── Produces: UX concept, user journey, edge cases
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Returns: reviewed, resolved design output to Neo
  └── Neo advances: to Morpheus
        ↓
Morpheus
  └── Produces: specifications — numbered, testable, RFC 2119 language
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Returns: reviewed, resolved specification to Neo
  └── Neo advances: to Switch
        ↓
Switch
  └── Produces: test cases derived from specs
  └── Owns review loop: Ghost → resolves → repeats until solid
  └── Returns: reviewed, resolved test suite to Neo
  └── Neo advances: to Trinity (container)
        ↓
Trinity [container]
  └── Produces: implementation — makes the tests pass
  └── Owns review loop: Smith → Ghost → resolves → repeats until solid
  └── Output lands in agents-output/ for Neo review
  └── Neo advances: to Apoc (container)
        ↓
Apoc [container]
  └── Executes: runs tests, validates outcomes, reports results
  └── Owns review loop: Ghost → resolves → repeats until solid
  └── Output lands in agents-output/ for Neo review
  └── Neo advances: to Niobe
        ↓
Tank
  └── Invoked on demand at any stage — not a linear stage
  └── Owns review loop: Ghost → resolves → repeats until solid
  └── Returns: research findings to requesting agent or Neo
        ↓
Niobe
  └── Produces: documentation artifacts, memory files
  └── Owns review loop: Ghost → resolves → repeats until solid
  └── Returns: reviewed documentation to Neo
  └── Neo closes: stage complete
```

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
- The review criteria (what does complete look like?)

**Without original intent, Ghost can only find bugs.**
**With original intent, Ghost can find gaps.**
Always include original intent. Always.

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
CRITERIA:        [what does complete look like?]
OUTPUT:          [verification report — gaps, coverage issues, misalignments]
```

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

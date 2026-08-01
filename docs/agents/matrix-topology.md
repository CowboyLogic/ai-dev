# The Matrix Agent Topology

A multi-agent AI development pattern for disciplined, production-quality software work.

> "Unfortunately, no one can be told what the Matrix is. You have to see it for yourself." — Morpheus

All agent files for this topology live at
[`agents/matrix-topology/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology)
in the repository. `opencode/` is the canonical source; the GitHub Copilot format
used by the install commands below lives in the parallel
[`copilot/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology/copilot)
directory.

---

## What Problem Does This Solve?

Single-agent workflows hit a ceiling. The agent is capable — but without structured review gates,
problems compound silently. You review three hours of work and find something fundamental went wrong
at step two. Everything built on top of it is wrong too.

The Matrix Topology prevents this by applying **role separation and structured handoffs**:
each agent has one job in the lifecycle, and a different agent verifies the output before
the next stage begins. Problems are caught at the cheapest possible moment — before they compound.

---

## Agent Roster

14 agents. `neo` is the primary conductor; every other agent is a subagent it dispatches.

| Agent | Role | File |
|---|---|---|
| **Neo** | The Conductor. Orchestrates the full lifecycle, holds context, makes all judgment calls. | [neo.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/neo.agent.md) |
| **Mouse** | Express-lane builder for small, well-scoped changes that skip the full lifecycle. | [mouse.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/mouse.agent.md) |
| **The Architect** | Produces system architecture, key decisions, and extension points. | [the-architect.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/the-architect.agent.md) |
| **Oracle** | Defines user experience and surfaces edge cases before implementation. | [oracle.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/oracle.agent.md) |
| **Morpheus** | Writes formal specifications, contracts, and testable requirements. | [morpheus.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/morpheus.agent.md) |
| **Switch** | Produces test cases from specifications — every requirement gets a test. | [switch.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/switch.agent.md) |
| **Trinity** | Implements code precisely to specification. | [trinity.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/trinity.agent.md) |
| **Apoc** | Executes tests and validates outcomes against specifications. | [apoc.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/apoc.agent.md) |
| **Dozer** | Operational diagnostics — validates the built product actually works at runtime, not just that tests pass. | [dozer.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/dozer.agent.md) |
| **Tank** | Researcher. Retrieves information and surfaces findings that inform decisions. | [tank.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/tank.agent.md) |
| **Niobe** | Documentation writer. Captures what was built and why. | [niobe.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/niobe.agent.md) |
| **Smith** | Adversarial security reviewer (GPT). Reviews Claude-family artifacts, cross-cutting. | [smith.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/smith.agent.md) |
| **Smith-Claude** | Adversarial security reviewer (Claude). Reviews GPT-family artifacts — Trinity's implementation. | [smith-claude.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/smith-claude.agent.md) |
| **Ghost** | Cross-cutting verification reviewer. Provides a second model family's perspective after every stage. | [ghost.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/copilot/ghost.agent.md) |

---

## Development Lifecycle

```
Research (Tank) → Design (Oracle) → Architecture (The Architect)
    → Specs (Morpheus) → Tests (Switch) → Implementation (Trinity)
    → Test Execution (Apoc) → Operational Validation (Dozer)
    → Documentation (Niobe)
```

Smith / Smith-Claude and Ghost are **cross-cutting** — Neo invokes the correctly-familied
security reviewer and Ghost after every generative stage, not just implementation.

Most day-to-day work does not run the full lifecycle. The **express lane** —
Mouse, reviewed by Ghost — is the default, faster path for small, well-scoped
changes, and where Neo spends most of its time.

Neo conducts the entire session: invoking agents in sequence, holding context across handoffs,
and making all judgment calls when the path is ambiguous.

---

## Conductor Guide

The full conductor protocol — how to start a session, how to hand off between agents,
and how to handle edge cases — is documented in
[`agents/matrix-topology/CONDUCTOR.md`](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/CONDUCTOR.md).

---

## Installing the Topology

```bash
# Install all Matrix Topology agents
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/neo.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/mouse.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/the-architect.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/oracle.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/morpheus.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/switch.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/trinity.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/apoc.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/dozer.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/tank.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/niobe.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/smith.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/smith-claude.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/ghost.agent.md
```

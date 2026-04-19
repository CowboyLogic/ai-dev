# The Matrix Agent Topology

A multi-agent AI development pattern for disciplined, production-quality software work.

> "Unfortunately, no one can be told what the Matrix is. You have to see it for yourself." — Morpheus

All agent files for this topology live at
[`agents/matrix-topology/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology)
in the repository and can be installed using the GitHub Copilot CLI.

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

| Agent | Role | File |
|---|---|---|
| **Neo** | The Conductor. Orchestrates the full lifecycle, holds context, makes all judgment calls. | [neo.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/neo.agent.md) |
| **The Architect** | Produces system architecture, key decisions, and extension points. | [the-architect.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/the-architect.agent.md) |
| **Oracle** | Defines user experience and surfaces edge cases before implementation. | [oracle.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/oracle.agent.md) |
| **Morpheus** | Writes formal specifications, contracts, and testable requirements. | [morpheus.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/morpheus.agent.md) |
| **Trinity** | Implements code precisely to specification. | [trinity.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/trinity.agent.md) |
| **Switch** | Produces test cases from specifications — every requirement gets a test. | [switch.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/switch.agent.md) |
| **Apoc** | Executes tests and validates outcomes against specifications. | [apoc.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/apoc.agent.md) |
| **Smith** | Adversarial security reviewer. Invoked after every generative artifact, without exception. | [smith.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/smith.agent.md) |
| **Ghost** | Cross-cutting verification reviewer. Provides a second model family's perspective after every stage. | [ghost.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/ghost.agent.md) |
| **Tank** | Researcher. Retrieves information and surfaces findings that inform decisions. | [tank.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/tank.agent.md) |
| **Niobe** | Documentation writer. Captures what was built and why. | [niobe.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/niobe.agent.md) |

---

## Development Lifecycle

```
Research (Tank) → Architecture (The Architect) → Design (Oracle)
    → Specs (Morpheus) → Tests (Switch) → Implementation (Trinity)
    → Test Execution (Apoc) → Security Review (Smith) → Verification (Ghost)
    → Documentation (Niobe)
```

Smith and Ghost are **cross-cutting** — they review every stage's output, not just implementation.

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
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/neo.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/the-architect.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/oracle.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/morpheus.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/trinity.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/switch.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/apoc.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/smith.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/ghost.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/tank.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/niobe.agent.md
```

# The Matrix Agent Topology

A multi-agent AI development pattern for disciplined, production-quality software work.

> "Unfortunately, no one can be told what the Matrix is. You have to see it for yourself." — Morpheus

All agent files for this topology live at
[`agents/matrix-topology/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology)
in the repository. It ships in three client formats: OpenCode is canonical, with
derived mirrors for Claude Code and GitHub Copilot. Agent bodies are identical
across formats; only client-specific frontmatter differs.

<!-- artifact-sync:inventory:start -->
| Kind | Name | Status | Source |
|---|---|---|---|
| Client | OpenCode | Canonical | [opencode/](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology/opencode) |
| Client | Claude Code | Derived mirror | [claude/](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology/claude) |
| Client | GitHub Copilot | Derived mirror | [copilot/](https://github.com/CowboyLogic/ai-dev/tree/main/agents/matrix-topology/copilot) |
| Harness | OpenCode | Runtime configuration | [opencode/](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode) |
<!-- artifact-sync:inventory:end -->

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

<!-- artifact-sync:roster:start -->
| Agent | Model | Job | Source |
|---|---|---|---|
| **Neo** | `github-copilot/claude-sonnet-5` | The Conductor. Primary interactive agent. Orchestrates the full development lifecycle, directs all other agents, holds context across stages, and makes all judgment calls. Invoke Neo for any task — Neo decides what happens next. | [neo.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/neo.agent.md) |
| **Apoc** | `github-copilot/claude-sonnet-5` | Tester agent. Invoked to execute tests and validate outcomes against specifications. Invoke when implementation is complete and test execution is the next step. Apoc is methodical — every test runs, every result is recorded, every failure is investigated. | [apoc.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/apoc.agent.md) |
| **Dozer** | `github-copilot/claude-sonnet-5` | Diagnostics agent. Invoked after implementation is tested and verified to validate that the built product actually works at runtime — not just that tests pass. Dozer operates in two modes: Contained (autonomous execution in a Linux container for web apps and CLIs) and Assisted (structured validation plan for environments that cannot be containerized). Invoke when Apoc has cleared the test suite and operational validation is the next step. | [dozer.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/dozer.agent.md) |
| **Ghost** | `github-copilot/gemini-3.1-pro-preview` | Review agent. Cross-cutting verification agent invoked after every agent that produces an artifact — including after Smith. Ghost provides the second set of eyes from a different model family. Invoke Ghost after every lifecycle stage, without exception. Ghost finds gaps, not just bugs. | [ghost.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/ghost.agent.md) |
| **Morpheus** | `github-copilot/claude-sonnet-5` | Spec writer agent. Invoked to produce specifications from architecture and design artifacts. Invoke when contracts, interfaces, and testable requirements need to be formally defined. Morpheus does not write code — he defines what code must do and what it must not do. | [morpheus.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/morpheus.agent.md) |
| **Mouse** | `github-copilot/gpt-5.6-terra` | Express-lane builder. Invoked by Neo for small, well-scoped changes that do not warrant the full lifecycle. Mouse implements the change directly in the working tree, gets it green (build/tests/typecheck), and returns to Neo for review. Mouse does not design, does not write specs, and does not invoke reviewers — Neo owns the express review loop. | [mouse.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/mouse.agent.md) |
| **Niobe** | `github-copilot/claude-sonnet-5` | Document writer agent. Invoked to produce documentation artifacts from completed lifecycle stages. Invoke when implementation is verified and documentation needs to reflect the current state of the system. Niobe does not invent — she captures what was built and why. | [niobe.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/niobe.agent.md) |
| **Oracle** | `github-copilot/claude-opus-4.8` | Designer agent. Invoked at the design stage to define the user experience, validate the concept, and surface edge cases before any technical decisions are made. Invoke when defining what something does, how it feels, and what the user encounters at every step. | [oracle.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/oracle.agent.md) |
| **Smith** | `github-copilot/gpt-5.6-terra` | Security agent. Cross-cutting adversarial reviewer invoked after every agent that produces a generative artifact. Invoke Smith after architecture, design, specifications, and implementation — every time, without exception. Smith finds what should not be there. | [smith.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/smith.agent.md) |
| **Smith-Claude** | `github-copilot/claude-sonnet-5` | Security agent — Claude-family variant. Identical in role to Smith, but pinned to a Claude model so it can review GPT-family artifacts cross-family. Neo invokes Smith-Claude in place of Smith whenever the artifact was produced by a GPT-family agent (in the full loop, that is Trinity). Smith-Claude finds what should not be there. | [smith-claude.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/smith-claude.agent.md) |
| **Switch** | `github-copilot/claude-sonnet-5` | Test writer agent. Invoked to produce test cases from specifications. Invoke when specs are complete and test coverage needs to be defined. Switch is exacting — every requirement gets a test, no exceptions. Switch produces both the test specification document AND the executable test code. Trinity does not write tests. | [switch.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/switch.agent.md) |
| **Tank** | `github-copilot/claude-haiku-4.5` | Researcher agent. Invoked to retrieve information, investigate options, and surface findings that inform decisions at any lifecycle stage. Invoke when current information is needed before a decision can be made. Tank finds what is needed — he does not make decisions with it. | [tank.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/tank.agent.md) |
| **The Architect** | `github-copilot/claude-opus-4.8` | Architecture agent. Invoked at the architecture stage of the development lifecycle to produce structure, key decisions, and extension points. Invoke when designing system structure, making significant technical decisions, or defining how components relate. | [the-architect.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/the-architect.agent.md) |
| **Trinity** | `github-copilot/gpt-5.6-terra` | Coder agent. Invoked to implement feature code that makes Switch's tests pass. Invoke when specs, architecture, and executable tests exist and implementation is the next step. Trinity does not design, does not write tests — she builds what has been designed, precisely, against tests already written. | [trinity.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/trinity.agent.md) |
<!-- artifact-sync:roster:end -->

---

## Development Lifecycle

```text
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

### OpenCode

Clone the repository, then link the harness files and canonical agents into a real
OpenCode configuration directory:

```bash
git clone https://github.com/CowboyLogic/ai-dev ~/src/ai-dev

mkdir -p ~/.config/opencode
ln -sfn ~/src/ai-dev/harness/opencode/opencode.jsonc ~/.config/opencode/opencode.jsonc
ln -sfn ~/src/ai-dev/harness/opencode/guardrails.md  ~/.config/opencode/guardrails.md
ln -sfn ~/src/ai-dev/agents/matrix-topology/opencode ~/.config/opencode/agents
```

The harness sets `default_agent` to `neo` and loads `guardrails.md` in every
session.

### Claude Code

The Claude Code mirror preserves every agent body and translates the frontmatter
to Claude Code tools and model aliases:

```bash
git clone https://github.com/CowboyLogic/ai-dev ~/src/ai-dev

mkdir -p ~/.claude/agents
ln -sfn ~/src/ai-dev/agents/matrix-topology/claude/*.agent.md ~/.claude/agents/
```

Agents assigned to GPT or Gemini in the canonical topology use `model: inherit`
because Claude Code cannot enforce those cross-family model assignments.

### GitHub Copilot

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

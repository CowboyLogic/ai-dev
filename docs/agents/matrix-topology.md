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
| Agent | Model | Role | Source |
|---|---|---|---|
| **Neo** | `github-copilot/claude-sonnet-5` | The Conductor | [neo.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/neo.md) |
| **Apoc** | `github-copilot/claude-sonnet-5` | Tester agent | [apoc.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/apoc.md) |
| **Dozer** | `github-copilot/claude-sonnet-5` | Diagnostics agent | [dozer.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/dozer.md) |
| **Ghost** | `github-copilot/gemini-3.8-flash` | Review agent | [ghost.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/ghost.md) |
| **Morpheus** | `github-copilot/claude-sonnet-5` | Spec writer agent | [morpheus.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/morpheus.md) |
| **Mouse** | `github-copilot/gpt-6-sol` | Express-lane builder | [mouse.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/mouse.md) |
| **Niobe** | `github-copilot/claude-sonnet-5` | Document writer agent | [niobe.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/niobe.md) |
| **Oracle** | `github-copilot/claude-opus-5.5` | Designer agent | [oracle.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/oracle.md) |
| **Smith** | `github-copilot/gpt-6-sol` | Security agent | [smith.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/smith.md) |
| **Smith-Claude** | `github-copilot/claude-sonnet-5` | Security agent — Claude-family variant | [smith-claude.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/smith-claude.md) |
| **Switch** | `github-copilot/claude-sonnet-5` | Test writer agent | [switch.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/switch.md) |
| **Tank** | `github-copilot/gpt-6-luna` | Researcher agent | [tank.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/tank.md) |
| **The Architect** | `github-copilot/claude-opus-5.5` | Architecture agent | [the-architect.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/the-architect.md) |
| **Trinity** | `github-copilot/gpt-6-sol` | Coder agent | [trinity.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/matrix-topology/opencode/trinity.md) |
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
ln -sfn ~/src/ai-dev/harness/opencode/guardrails.md  ~/.config/opencode/AGENTS.md
ln -sfn ~/src/ai-dev/agents/matrix-topology/opencode ~/.config/opencode/agents
```

The harness sets `default_agent` to `neo`. `guardrails.md` is linked as the global
`~/.config/opencode/AGENTS.md`, which OpenCode V2 loads in every session; V2 does not
load the `instructions` field.

> [!IMPORTANT]
> The `opencode/` agents use native **OpenCode V2** frontmatter (an ordered
> `permissions` rule list) and are named `<id>.md`, because V2 derives the agent ID
> from the filename. Subagents ship `hidden: false`: in V2, `hidden: true` removes an
> agent from the subagent catalog Neo dispatches from. Do not point an OpenCode V1
> client at these files.

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

<!-- artifact-sync:install:start -->
```bash
# Install all 14 agents
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/neo.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/apoc.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/dozer.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/ghost.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/morpheus.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/mouse.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/niobe.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/oracle.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/smith.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/smith-claude.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/switch.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/tank.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/the-architect.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/matrix-topology/copilot/trinity.agent.md
```
<!-- artifact-sync:install:end -->

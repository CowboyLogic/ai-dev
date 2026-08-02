# AI Agents

This repository provides two topologies of AI agents:

- **Lane Topology** — a multi-agent system that classifies each request into a lane
  and sizes process to match, from a seconds-long mechanical edit to a full
  plan-build-verify lifecycle. OpenCode-native, with a GitHub Copilot mirror.
- **Matrix Topology** — the predecessor multi-agent system: a fixed nine-stage
  lifecycle for production-quality development work. OpenCode-native (canonical),
  with Claude Code and GitHub Copilot mirrors.

Agent installations are topology-specific. Each topology provides installation
instructions for its OpenCode and GitHub Copilot formats.

---

## Installing Agents

- **[Lane Topology](lane-topology.md#installing-it-opencode)** — the recommended pattern
  for new projects, with proportional process sizing.
- **[Matrix Topology](matrix-topology.md#installing-the-topology)** — the structured
  lifecycle pattern, still published and usable.

---

## Lane Topology

The Lane Topology classifies every request into one of five lanes — MECHANICAL,
INVESTIGATE, DIRECT, PLAN, or BUILD — by table lookup, and dispatches only the
agents that lane needs. It is the successor to the Matrix Topology below, built to
close three gaps in that pattern: no middle ground between a trivial change and the
full lifecycle, no mode for Socratic planning, and self-reported (not independently
executed) test results.

See the [Lane Topology](lane-topology.md) page for the full pattern, lane table, and
installation for both OpenCode (canonical) and GitHub Copilot (mirror).

| Agent | Role |
|---|---|
| **Conductor** | Classifies requests into lanes, dispatches specialists, holds the ledger, talks to you |
| **Planner** | Socratic planning — interrogates the request, then produces a plan or design brief |
| **Investigator** | Read-only codebase comprehension and root-cause analysis |
| **Builder** | Implementation — writes code and gets it green |
| **Mechanic** | Trivial mechanical edits — typos, version bumps, config values |
| **Verifier** | Cross-family review that runs the build and tests itself, not just reads the diff |
| **Adversary** | Security review, dispatched whenever the change touches a critical surface |
| **Scribe** | Documentation — describes what the code actually does |
| **Researcher** | External research — library APIs, protocol details, current information |

---

## Matrix Topology

The predecessor to the Lane Topology above, and still published and usable: a
structured multi-agent pattern for disciplined, lifecycle-driven development. Every
request runs the same fixed nine-stage lifecycle — each agent has a defined role,
and agents hand off to one another in a prescribed order rather than a single agent
doing everything end-to-end.

See the [Matrix Topology](matrix-topology.md) page for the full pattern description, roster, and conductor guide.

| Agent | Role |
|---|---|
| **Neo** | The Conductor — orchestrates the full lifecycle, holds context, makes judgment calls |
| **Mouse** | Express-lane builder for small, well-scoped changes |
| **The Architect** | Produces system architecture and key technical decisions |
| **Oracle** | Defines user experience and surfaces edge cases before implementation |
| **Morpheus** | Writes formal specifications and testable requirements |
| **Trinity** | Implements code that satisfies specifications and passes tests |
| **Switch** | Produces test cases from specifications — every requirement gets a test |
| **Apoc** | Executes tests and validates outcomes against specifications |
| **Dozer** | Operational diagnostics — validates the product works at runtime, not just that tests pass |
| **Smith** / **Smith-Claude** | Adversarial security reviewers — cross-family, invoked after every generative artifact |
| **Ghost** | Cross-cutting verification reviewer — provides a second model family's eyes |
| **Tank** | Researcher — retrieves information and surfaces findings for decisions |
| **Niobe** | Documentation writer — captures what was built and why |

---

---

## Agent Configuration

For the full frontmatter reference (properties, tool aliases, platform compatibility),
see the [Copilot Agent Creator](../skills/index.md#copilot-agent-creator) skill.

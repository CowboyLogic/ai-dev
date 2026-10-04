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

## Domain Specialists

Single-file agents that stand alone, outside any topology. They use the VS Code and GitHub Copilot
`.agent.md` format, and the three coordinators call the others as subagents. Each is a real file in
[`agents/`](https://github.com/CowboyLogic/ai-dev/blob/main/agents), so the file is the authoritative definition.

| [**code-reviewer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/code-reviewer.agent.md) | Reviews code for correctness, security, maintainability, and test coverage. Read-only |
| [**test-engineer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/test-engineer.agent.md) | Writes and runs automated tests, and reports the actual results |
| [**security-auditor**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/security-auditor.agent.md) | Audits code and configuration against the OWASP Top 10. Read-only |
| [**performance-reviewer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/performance-reviewer.agent.md) | Finds inefficient algorithms, N+1 queries, and memory growth. Read-only |
| [**docs-writer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/docs-writer.agent.md) | Writes and updates READMEs, API references, and how-to guides |
| [**api-designer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/api-designer.agent.md) | Designs REST APIs and OpenAPI specifications |
| [**react-developer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/react-developer.agent.md) | Builds and refactors React components with TypeScript |
| [**architecture-coordinator**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/architecture-coordinator.agent.md) | Coordinator: delegates to `api-designer`, `security-auditor`, and `performance-reviewer` |
| [**feature-lead**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/feature-lead.agent.md) | Coordinator: delegates to `api-designer`, `react-developer`, `test-engineer`, `code-reviewer`, and `docs-writer` |
| [**review-coordinator**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/review-coordinator.agent.md) | Coordinator: delegates to `code-reviewer`, `security-auditor`, and `performance-reviewer` |

Install one with the GitHub CLI:

```bash
gh copilot agent install CowboyLogic/ai-dev/agents/code-reviewer.agent.md
```

A coordinator only delegates to agents it can find, so install the specialists it names alongside it. See
[Agent Examples](../harness/vscode/agent-examples.md) for what each one demonstrates, and
[Subagents](../harness/vscode/subagent-tool.md) for how delegation works.

---

## Agent Configuration

For the full frontmatter reference (properties, tool aliases, platform compatibility),
see the [Copilot Agent Creator](../skills/index.md#copilot-agent-creator) skill.

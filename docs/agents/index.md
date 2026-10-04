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

See the [Lane Topology](lane-topology.md) page for the full pattern, lane table,
[agent roster](lane-topology.md#agent-roster), and installation for both OpenCode
(canonical) and GitHub Copilot (mirror).

---

## Matrix Topology

The predecessor to the Lane Topology above, and still published and usable: a
structured multi-agent pattern for disciplined, lifecycle-driven development. Every
request runs the same fixed nine-stage lifecycle — each agent has a defined role,
and agents hand off to one another in a prescribed order rather than a single agent
doing everything end-to-end.

See the [Matrix Topology](matrix-topology.md) page for the full pattern description,
[agent roster](matrix-topology.md#agent-roster), and conductor guide.

---

## Domain Specialists

Single-file agents that stand alone, outside any topology. They use the VS Code and GitHub Copilot
`.agent.md` format, and the three coordinators call the others as subagents. Each is a real file in
[`agents/`](https://github.com/CowboyLogic/ai-dev/blob/main/agents), so the file is the authoritative definition.

<!-- artifact-sync:specialists:start -->
| Agent | Role |
|---|---|
| [**api-designer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/api-designer.agent.md) | Designs REST APIs and OpenAPI specifications covering resource modeling, status codes, error shape, pagination, and versioning |
| [**code-reviewer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/code-reviewer.agent.md) | Reviews code for correctness, security, maintainability, and test coverage |
| [**docs-writer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/docs-writer.agent.md) | Writes and updates technical documentation such as READMEs, API references, and how-to guides, describing what the code actually does |
| [**performance-reviewer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/performance-reviewer.agent.md) | Finds performance problems such as inefficient algorithms, N+1 queries, and memory growth, and recommends fixes backed by measurements |
| [**react-developer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/react-developer.agent.md) | Builds and refactors React components with TypeScript, following the project's existing patterns, accessibility rules, and test conventions |
| [**security-auditor**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/security-auditor.agent.md) | Audits code and configuration for security vulnerabilities against the OWASP Top 10 and reports prioritized findings |
| [**test-engineer**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/test-engineer.agent.md) | Writes and runs automated tests |
| [**architecture-coordinator**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/architecture-coordinator.agent.md) | Designs system architecture by delegating API, security, and performance questions to specialist subagents and synthesizing their answers into one design |
| [**feature-lead**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/feature-lead.agent.md) | Leads a feature from design through review by delegating API design, UI work, tests, review, and documentation to specialist subagents |
| [**review-coordinator**](https://github.com/CowboyLogic/ai-dev/blob/main/agents/review-coordinator.agent.md) | Runs a multi-angle code review by delegating to the code, security, and performance specialists and merging their findings into one prioritized report |
<!-- artifact-sync:specialists:end -->

Install one with the GitHub CLI:

```bash
gh copilot agent install CowboyLogic/ai-dev/agents/code-reviewer.agent.md
```

A coordinator only delegates to agents it can find, so install the specialists it names alongside it. See
[Agent Examples](../harness/vscode/agent-examples.md) for what each one demonstrates, and
[Subagents](../harness/vscode/subagent-tool.md) for how delegation works.

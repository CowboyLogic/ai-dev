# AI Agents

This repository provides three tiers of AI agents:

- **Lane Topology** — a multi-agent system that classifies each request into a lane
  and sizes process to match, from a seconds-long mechanical edit to a full
  plan-build-verify lifecycle. OpenCode-native, with a GitHub Copilot mirror.
- **Matrix Topology** — the predecessor multi-agent system: a fixed nine-stage
  lifecycle for production-quality development work. OpenCode-native (canonical),
  with Claude Code and GitHub Copilot mirrors.
- **Domain Specialists** — focused single-purpose agents for scoped, task-level
  assistance. GitHub Copilot (VS Code).

All agent files live at the root of the repository under [`agents/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents).
Copilot-format agents can be installed directly using the GitHub Copilot CLI; the
Lane Topology's OpenCode format is installed by symlinking into `~/.config/opencode/`
— see its page for both.

---

## Installing Agents

```bash
# Install a specific agent
gh copilot agent install CowboyLogic/ai-dev/agents/<agent-file>.agent.md

# Browse all agents
gh copilot agent list CowboyLogic/ai-dev
```

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

Single-agent tools for focused, domain-specific tasks within GitHub Copilot.
Useful when you need quick, scoped assistance without running a full topology session.

| Agent | Domain | Source |
|---|---|---|
| **API Specialist (.NET)** | .NET REST API design and implementation | [api-dotnet.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/api-dotnet.agent.md) |
| **Architect** | Multi-tier system design (React/.NET/PostgreSQL) | [architect-react-dotnet-postgres.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/architect-react-dotnet-postgres.agent.md) |
| **Cloud Specialist (GCP)** | GCP infrastructure and deployment | [cloud-gcp.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/cloud-gcp.agent.md) |
| **Code Reviewer** | Code quality, security, and architecture review | [code-reviewer.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/code-reviewer.agent.md) |
| **Database Specialist** | PostgreSQL schema and EF Core migrations | [database-postgres-ef.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/database-postgres-ef.agent.md) |
| **DevOps** | GitHub Actions CI/CD and container builds | [devops.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/devops.agent.md) |
| **Documentation** | Technical docs following Google style | [documentation.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/documentation.agent.md) |
| **Performance** | Performance analysis and optimization | [performance.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/performance.agent.md) |
| **Plan** | Feature planning and cross-agent coordination | [plan.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/plan.agent.md) |
| **Security Analyst** | OWASP analysis and security review | [security-analyst.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/security-analyst.agent.md) |
| **Testing Specialist** | Unit, integration, and E2E test creation | [testing-specialist.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/testing-specialist.agent.md) |
| **UX/UI Specialist** | React components and Tailwind CSS | [uxui-nodejs.agent.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/uxui-nodejs.agent.md) |

---

## Agent Configuration

For the full frontmatter reference (properties, tool aliases, platform compatibility),
see the [Copilot Agent Creator](../skills/index.md#copilot-agent-creator) skill.

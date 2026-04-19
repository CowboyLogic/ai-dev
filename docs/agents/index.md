# AI Agents

This repository provides two tiers of AI agents for GitHub Copilot (VS Code):

- **Matrix Topology** — a disciplined multi-agent system for production-quality development work
- **Domain Specialists** — focused single-purpose agents for scoped, task-level assistance

All agent files live at the root of the repository under [`agents/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents)
and can be installed directly using the GitHub Copilot CLI.

---

## Installing Agents

```bash
# Install a specific agent
gh copilot agent install CowboyLogic/ai-dev/agents/<agent-file>.agent.md

# Browse all agents
gh copilot agent list CowboyLogic/ai-dev
```

---

## Matrix Topology

The Matrix Topology is a structured multi-agent pattern for disciplined, lifecycle-driven development.
Each agent has a defined role, and agents hand off to one another in a prescribed order rather than
a single agent doing everything end-to-end.

See the [Matrix Topology](matrix-topology.md) page for the full pattern description, roster, and conductor guide.

| Agent | Role |
|---|---|
| **Neo** | The Conductor — orchestrates the full lifecycle, holds context, makes judgment calls |
| **The Architect** | Produces system architecture and key technical decisions |
| **Oracle** | Defines user experience and surfaces edge cases before implementation |
| **Morpheus** | Writes formal specifications and testable requirements |
| **Trinity** | Implements code that satisfies specifications and passes tests |
| **Switch** | Produces test cases from specifications — every requirement gets a test |
| **Apoc** | Executes tests and validates outcomes against specifications |
| **Smith** | Adversarial security reviewer — invoked after every generative artifact |
| **Ghost** | Cross-cutting verification reviewer — provides a second model's eyes |
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

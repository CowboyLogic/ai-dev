# AI Agents Overview

This directory contains documentation for custom AI agents used in AI-assisted development workflows.
Two complete multi-agent topologies live here, plus a set of single-agent domain specialists.

---

## Agent Architecture

Agents in this repository operate at two levels: full topologies and domain specialists.

### Multi-Agent Topologies

Both define complete multi-agent systems for disciplined development work, where each agent
has a distinct role and agents collaborate through structured handoffs rather than one agent
doing everything. They are **independent patterns** — pick one; changes do not propagate
between them.

| Topology | Clients | Organizing idea |
|---|---|---|
| [Lane Topology](lane-topology/README.md) | OpenCode | 9 agents. A mechanical lane classifier sizes process to the task before work starts — mechanical, investigate, direct, plan (Socratic), or full build. Reviewers execute the tests themselves. |
| [Matrix Topology](matrix-topology/README.md) | OpenCode, Claude Code, Copilot | 14 agents. A staged lifecycle (design → architecture → spec → tests → code → validation → docs) with an express lane for small changes. |

The Lane Topology is the newer of the two and was built from what the Matrix Topology taught.
See [lane-topology/README.md](lane-topology/README.md) for the comparison.

Authoritative technical references: [lane-topology/opencode/conductor.agent.md](lane-topology/opencode/conductor.agent.md)
and [matrix-topology/CONDUCTOR.md](matrix-topology/CONDUCTOR.md).

### Domain Specialists (Supplementary)

The agents below are **single-agent tools** designed for focused, domain-specific tasks within GitHub Copilot (VS Code).
They are useful when you need quick, scoped assistance without running a full topology session.
Each specialist loads one or more skills for domain knowledge rather than embedding it inline.

| Agent | Domain | Skills Used |
|---|---|---|
| [API Specialist (.NET)](api-dotnet.agent.md) | .NET REST API design and implementation | — |
| [Architect](architect-react-dotnet-postgres.agent.md) | Multi-tier system design (React/.NET/PostgreSQL) | — |
| [Cloud Specialist (GCP)](cloud-gcp.agent.md) | GCP infrastructure and deployment | — |
| [Code Reviewer](code-reviewer.agent.md) | Code quality, security, and architecture review | — |
| [Database Specialist](database-postgres-ef.agent.md) | PostgreSQL schema and EF Core migrations | — |
| [DevOps](devops.agent.md) | GitHub Actions CI/CD and container builds | `docker-image-management` |
| [Documentation](documentation.agent.md) | Technical docs following Google style | `google-style-docs`, `mkdocs-site-management` |
| [Performance](performance.agent.md) | Performance analysis and optimization | — |
| [Plan](plan.agent.md) | Feature planning and cross-agent coordination | — |
| [Security Analyst](security-analyst.agent.md) | OWASP analysis and security review | — |
| [Testing Specialist](testing-specialist.agent.md) | Unit, integration, and E2E test creation | — |
| [UX/UI Specialist](uxui-nodejs.agent.md) | React components and Tailwind CSS | — |

---

## Agent Configuration

For the full frontmatter reference (properties, tool aliases, platform compatibility), see the [Frontmatter Reference](../skills/agent-creator-copilot/references/frontmatter-reference.md).

## Skills

Skills provide domain knowledge that agents load at session start. See the [Skills](../skills/README.md) directory
for the full catalog of available skills.
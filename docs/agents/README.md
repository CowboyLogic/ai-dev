# AI Agents Overview

This directory contains documentation for custom AI agents used in AI-assisted development workflows.
For the authoritative guide to how these agents work together, see the [Matrix Topology](matrix-topology/README.md).

---

## Two-Tier Agent Architecture

Agents in this repository operate at two levels:

### Matrix Topology (Primary)

The `matrix-topology/` folder defines a **multi-agent system** for disciplined, production-quality development work.
Each agent has a distinct role in the lifecycle — planning, design, implementation, security review, and quality verification.
Agents collaborate through structured handoffs rather than a single agent doing everything.

See [matrix-topology/README.md](matrix-topology/README.md) and [matrix-topology/CONDUCTOR.md](matrix-topology/CONDUCTOR.md)
for the full roster, lifecycle, and handoff protocols.

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
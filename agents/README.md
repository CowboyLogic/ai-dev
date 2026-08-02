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

Authoritative technical references: [lane-topology/opencode/conductor.md](lane-topology/opencode/conductor.md)
and [matrix-topology/CONDUCTOR.md](matrix-topology/CONDUCTOR.md).

---

## Agent Configuration

For the full frontmatter reference (properties, tool aliases, platform compatibility), see the [Frontmatter Reference](../skills/agent-creator-copilot/references/frontmatter-reference.md).

## Skills

Skills provide domain knowledge that agents load at session start. See the [Skills](../skills/README.md) directory
for the full catalog of available skills.
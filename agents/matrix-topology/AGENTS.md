# AGENTS.md — Matrix Topology Agent Synchronization Directive

> Read this file before modifying any agent file in this directory tree.

---

## Purpose

This directory contains the Matrix Topology multi-agent system — a 12-agent
orchestration pattern for AI-assisted software development. The topology is
published across three AI client formats. This file defines the synchronization
rules that keep all three formats consistent.

---

## Directory Structure

```
agents/matrix-topology/
├── opencode/        # Canonical source — OpenCode CLI format
├── claude/          # Claude Code format (derived from opencode/)
├── copilot/         # GitHub Copilot format (derived from opencode/)
├── AGENTS.md        # This file — synchronization directive
├── CONDUCTOR.md     # Authoritative technical topology reference
└── README.md        # Human-facing overview
```

---

## The Golden Rule

**`opencode/` is the canonical source of truth.**

Every agent body (everything after the frontmatter `---`) must be
character-for-character identical across all three folders.

Only frontmatter differs. If you change the body of any agent, you must
update it in all three folders simultaneously. A body that diverges across
folders is a bug — not a variant.

---

## The 12 Agents

| Agent | Role | Model Family |
|---|---|---|
| `neo` | Conductor / Orchestrator | Anthropic / Claude |
| `the-architect` | Architecture | Anthropic / Claude |
| `oracle` | Design / UX | Google / Gemini |
| `morpheus` | Specification | Anthropic / Claude |
| `switch` | Test writer | Anthropic / Claude |
| `trinity` | Implementation | OpenAI / GPT |
| `apoc` | Test execution | Anthropic / Claude |
| `dozer` | Operational diagnostics | Anthropic / Claude |
| `tank` | Research | Google / Gemini |
| `niobe` | Documentation | Anthropic / Claude |
| `smith` | Security review (cross-cutting) | OpenAI / GPT (primary) |
| `ghost` | Verification review (cross-cutting) | Google / Gemini (alternate) |

---

## Frontmatter Differences by Format

Only the frontmatter block (`---` to `---`) differs across the three formats.
The body is identical in all three.

### OpenCode (`opencode/`)

```yaml
---
name: Agent Name
description: >
  One-line description.
model: github-copilot/<model-id>
permission:
  read: allow
  edit: allow       # where applicable
  bash: allow       # where applicable
  grep: allow       # where applicable
  webfetch: allow   # where applicable
  websearch: allow  # where applicable
  task: allow       # Neo only
mode: subagent      # all except Neo
# mode: primary     # Neo only
hidden: true        # all except Neo
---
```

### Claude Code (`claude/`)

```yaml
---
name: Agent Name
description: >
  One-line description.
tools: Read, Edit, Bash, Grep    # comma-separated, Title Case
model: sonnet                    # sonnet | opus | haiku | inherit | full model ID
# disallowedTools: Bash          # where applicable
---
```

Claude Code tool names: `Read`, `Edit`, `Bash`, `Grep`, `Glob`, `Task`, `WebFetch`

Model aliases resolve to whichever Claude model is currently in that tier. Use `inherit`
for agents whose designated model family (GPT, Gemini) cannot be served by Claude Code —
they will run on the main conversation's model instead.

#### Claude Code model assignments

| Agent | `model` value | Reason |
|---|---|---|
| `neo` | `sonnet` | Primary conductor — heavy reasoning, frequent invocation |
| `the-architect` | `opus` | Highest-stakes decisions; runs infrequently — cost justified |
| `oracle` | `opus` | Designated Gemini — cannot be honored; falls back to Opus model |
| `morpheus` | `sonnet` | Precision spec writing requires solid reasoning |
| `switch` | `sonnet` | Test design + executable code generation |
| `trinity` | `inherit` | Designated GPT — cannot be honored; falls back to session model |
| `apoc` | `sonnet` | Methodical but needs solid reasoning for root cause analysis |
| `dozer` | `sonnet` | Full-stack diagnostic reasoning |
| `tank` | `haiku` | High-frequency research and retrieval — lightweight is correct here |
| `niobe` | `sonnet` | Documentation requires accurate comprehension of full context |
| `smith` | `inherit` | Designated GPT — cannot be honored; falls back to session model |
| `ghost` | `inherit` | Designated Gemini (alternate) — cannot be honored; falls back to session model |

### GitHub Copilot (`copilot/`)

```yaml
---
description: >
  One-line description.
tools: ["read", "edit", "run", "search", "web", "agent"]  # YAML array, lowercase
model: Model Name (copilot)
user-invocable: false    # all except Neo
agents:                  # Neo only
  - agent-filename-without-extension
---
```

Copilot tool aliases: `read`, `edit`, `run` (bash), `search` (grep), `web` (fetch/search), `agent` (task/subagent)

---

## Tool Mapping Reference

| OpenCode permission | Claude Code tool | Copilot tool |
|---|---|---|
| `read` | `Read` | `"read"` |
| `edit` | `Edit` | `"edit"` |
| `bash` | `Bash` | `"run"` |
| `grep` | `Grep` | `"search"` |
| `webfetch` / `websearch` | `WebFetch` | `"web"` |
| `task` | `Task` | `"agent"` |

---

## Model Name Mapping Reference

| OpenCode model ID | Claude Code `model` | Copilot display name |
|---|---|---|
| `github-copilot/claude-opus-4.7` | `opus` | `Claude Opus 4.7 (copilot)` |
| `github-copilot/claude-sonnet-4.6` | `sonnet` | `Claude Sonnet 4.6 (copilot)` |
| `github-copilot/gpt-5.3-codex` | `inherit` *(GPT — not available)* | `GPT-5.3-Codex (copilot)` |
| `github-copilot/gpt-5.4` | `inherit` *(GPT — not available)* | `GPT-5.4 (copilot)` |
| `github-copilot/gemini-3.1-pro-preview` | `inherit` *(Gemini — not available)* | `Gemini 3.1 Pro (copilot)` |
| `github-copilot/gemini-3.1-flash` | `inherit` *(Gemini — not available)* | `Gemini 3.1 Flash (copilot)` |

> [!NOTE]
> Claude Code only serves Claude models. Agents designated for GPT or Gemini families
> (`oracle`, `trinity`, `tank`, `smith`, `ghost`) use `model: inherit` — they run on
> whatever model the main session is using. The cross-family separation those agents
> depend on is not enforceable in Claude Code.

---

## Synchronization Checklist

When modifying any agent:

- [ ] Identified which file is changing — body, frontmatter, or both
- [ ] If **body change**: updated the body in all three folders (`opencode/`, `claude/`, `copilot/`)
- [ ] If **frontmatter change**: applied the correct format for each folder per the rules above
- [ ] Verified the description field is identical across all three folders
- [ ] No folder has a body that diverges from `opencode/` (spot-check: compare opening lines after frontmatter)

---

## Adding a New Agent

1. Write the canonical agent in `opencode/` with full OpenCode frontmatter and body
2. Copy the body verbatim to `claude/` — apply Claude Code frontmatter only
3. Copy the body verbatim to `copilot/` — apply Copilot frontmatter only
4. Add the agent to the roster table in this file
5. Add the agent to Neo's `agents:` list in `copilot/neo.agent.md`
6. Update `CONDUCTOR.md` with the new agent's role, model, and lifecycle position
7. Update `README.md` with a brief description for human readers

---

## Authoritative References

- **Topology rules and lifecycle:** `CONDUCTOR.md` in this directory
- **OpenCode frontmatter schema:** `skills/agent-creator-opencode/references/agent-reference.md`
- **Copilot frontmatter schema:** `skills/agent-creator-copilot/references/frontmatter-reference.md`
- **Claude Code frontmatter schema:** See the `claude/` section above (no separate reference file)

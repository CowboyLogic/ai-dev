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

## The 14 Agents

| Agent | Role | Model Family |
|---|---|---|
| `neo` | Conductor / Orchestrator | Anthropic / Claude |
| `mouse` | Express-lane builder | OpenAI / GPT |
| `the-architect` | Architecture | Anthropic / Claude |
| `oracle` | Design / UX | Anthropic / Claude |
| `morpheus` | Specification | Anthropic / Claude |
| `switch` | Test writer | Anthropic / Claude |
| `trinity` | Implementation | OpenAI / GPT |
| `apoc` | Test execution | Anthropic / Claude |
| `dozer` | Operational diagnostics | Anthropic / Claude |
| `tank` | Research | Anthropic / Claude |
| `niobe` | Documentation | Anthropic / Claude |
| `smith` | Security review (cross-cutting) | OpenAI / GPT |
| `smith-claude` | Security review of GPT-family artifacts | Anthropic / Claude |
| `ghost` | Verification review (cross-cutting) | Google / Gemini |

> [!IMPORTANT]
> **The roster is closed.** These fourteen are the only legal dispatch targets.
> `general`, `explore`, and every other built-in or all-purpose subagent are banned
> unconditionally in `neo.agent.md`. A `general` dispatch means the roster left the
> request with no legal move — that is a **roster gap, not a config failure**. Fix it
> by adding a capability or an explicit decomposition path, never by relaxing the ban.
>
> **Any two agents must compose without a third.** When adding or narrowing an agent,
> check the roster for a plausible request no single agent can serve. If one exists,
> either Neo has an explicit decomposition path for it, or the gap gets filled by
> `general` the first time it comes up.

### Everything flows through Neo — no subagent-to-subagent handoff

A subagent returns to Neo and stops. There is no channel by which one subagent hands
anything to another: working agents hold no `task` permission, and a running subagent
cannot receive a message from a peer. Nested delegation is unreliable in OpenCode, and
this is the same constraint seen from the input side.

**Never write an agent body that expects input to arrive from another agent.** If B
needs what A produced, A completes, returns to Neo, and Neo puts the artifact path into
B's brief. Neo is the single writer of context.

This failure is silent, which is why it survived several revisions. The consuming agent
does not error and does not wait — it runs to completion on training knowledge and
returns a confident, complete-looking artifact. Phrases to treat as bugs during review:

- "…integrates X's findings when they arrive"
- "…return to Neo **or the requesting agent**"
- any parallel dispatch where one agent consumes the other's output

Before marking two agents parallel, apply the dependency test: **does producing A
require knowing what is in B?** Yes → sequence. No → parallel.

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
| `mouse` | `inherit` | Designated GPT — cannot be honored; falls back to session model |
| `the-architect` | `opus` | Highest-stakes decisions; runs infrequently — cost justified |
| `oracle` | `opus` | Design work at the front of the lifecycle — errors here propagate |
| `morpheus` | `sonnet` | Precision spec writing requires solid reasoning |
| `switch` | `sonnet` | Test design + executable code generation |
| `trinity` | `inherit` | Designated GPT — cannot be honored; falls back to session model |
| `apoc` | `sonnet` | Methodical but needs solid reasoning for root cause analysis |
| `dozer` | `sonnet` | Full-stack diagnostic reasoning |
| `tank` | `haiku` | High-frequency research and retrieval — lightweight is correct here |
| `niobe` | `sonnet` | Documentation requires accurate comprehension of full context |
| `smith` | `inherit` | Designated GPT — cannot be honored; falls back to session model |
| `smith-claude` | `sonnet` | Claude by design — the pin is honored |
| `ghost` | `inherit` | Designated Gemini — cannot be honored; falls back to session model |

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

Only the five model IDs actually in use across the roster appear here. Add a row when
a new pin is introduced — do not leave retired IDs in the table.

| OpenCode model ID | Claude Code `model` | Copilot display name |
|---|---|---|
| `github-copilot/claude-opus-4.8` | `opus` | `Claude Opus 4.8 (copilot)` |
| `github-copilot/claude-sonnet-5` | `sonnet` | `Claude Sonnet 5 (copilot)` |
| `github-copilot/claude-haiku-4.5` | `haiku` | `Claude Haiku 4.5 (copilot)` |
| `github-copilot/gpt-5.6-terra` | `inherit` *(GPT — not available)* | `GPT-5.6-Terra (copilot)` |
| `github-copilot/gemini-3.1-pro-preview` | `inherit` *(Gemini — not available)* | `Gemini 3.1 Pro (copilot)` |

> [!NOTE]
> Claude Code only serves Claude models. Agents designated for GPT or Gemini families
> (`mouse`, `trinity`, `smith`, `ghost`) use `model: inherit` — they run on whatever
> model the main session is using. The cross-family separation those agents depend on
> is not enforceable in Claude Code.

The Copilot column carries a separate caveat.

> [!WARNING]
> **Copilot display names are not verified from this repo.** They are the documented
> mapping, not a tested one. If a Copilot agent silently falls back to a default model,
> check the display string against Copilot's model picker first.

### Scoped permissions: catch-all first, overrides after

OpenCode evaluates permission patterns in order and **the last matching rule wins**.
The catch-all `"*"` therefore goes **first**, with specific grants after it:

```yaml
permission:
  edit:
    "*": deny                    # catch-all FIRST
    ".agent-output/**": allow   # specific override AFTER
```

Written the other way round, `"*": deny` is the last match for every path and the
agent can edit **nothing** — including the directory it was just granted. The block
still looks correct at a glance, and OpenCode raises no error. `tank` and `dozer`
both shipped this inversion once; check the order whenever you touch a scoped grant.

> [!NOTE]
> Authoritative source: `skills/agent-creator-opencode/references/agent-reference.md`
> → *Pattern matching rules*. Load that skill before editing any OpenCode frontmatter.

### Scoped `edit` does not port

`tank` and `dozer` hold `edit` scoped to `.agent-output/**` in OpenCode — they write
their own artifacts without touching the working tree. Neither Claude Code nor Copilot
can express a path-scoped tool grant: both get an unscoped `Edit` / `"edit"`.

The scope is preserved by prompt discipline in the body (both name their exact output
path) but is **not harness-enforced outside OpenCode**. Do not read the `Edit` in
`claude/tank.agent.md` as a licence to widen the role.

---

## Synchronization Checklist

When modifying any agent:

- [ ] Identified which file is changing — body, frontmatter, or both
- [ ] If **body change**: updated the body in all three folders (`opencode/`, `claude/`, `copilot/`)
- [ ] If **frontmatter change**: applied the correct format for each folder per the rules above
- [ ] Verified the description field is identical across all three folders
- [ ] No folder has a body that diverges from `opencode/`
- [ ] **Body/frontmatter agreement:** every capability the body tells the agent to use is
      actually granted in the frontmatter of *all three* formats. An agent told to write a
      file needs `edit`. OpenCode defaults unlisted permissions to **allow**, so this class
      of bug is invisible there and hard-fails in Claude Code and Copilot, where `tools:`
      is a strict allowlist.
- [ ] **Roster closure:** no plausible request is left with no legal single agent — or Neo
      has an explicit decomposition path for it
- [ ] Bumped `TOPOLOGY VERSION` in `opencode/neo.agent.md` (and re-synced it to the other
      two formats) if any agent body changed
- [ ] Ran `./verify-deployment.sh --update` to regenerate `MANIFEST.sha256` — **last step,
      after every other change is final**

Do not spot-check body parity by eye. Verify it mechanically:

```bash
cd agents/matrix-topology
for f in opencode/*.agent.md; do a=$(basename "$f" .agent.md)
  for d in claude copilot; do
    diff -q <(sed -n '/^---$/,$p' "$f" | sed '1,/^---$/d') \
            <(sed -n '/^---$/,$p' "$d/$a.agent.md" | sed '1,/^---$/d') >/dev/null \
      || echo "DRIFT: $a vs $d"
  done
done
```

---

## Versioning and Deployment Staleness

Agents are deployed **by copy, not symlink** (symlinks were judged unreliable on the
Windows work box). A `git pull` therefore does **not** update the deployed agents —
they must be re-copied after every pull. This is the single most likely explanation
for a topology behaving like an older revision.

Two reporting mechanisms, deliberately advisory — nothing blocks a stale run:

**1. `TOPOLOGY VERSION` in Neo's body.** A dated line at the top of `neo.agent.md`,
which Neo states verbatim in its session-start summary. This is body content, not
frontmatter, because **an agent cannot see its own frontmatter** — frontmatter is
harness config, the body is the prompt. It lives in Neo alone: Neo is the only agent
the human talks to, and Neo's file is re-sent every turn, so paying those tokens in
all fourteen would buy nothing.

**Bump the date whenever any agent body changes.** Use a date, not semver — semver
invites a judgment call about whether a change is "major," and the answer here is
always "re-copy the files."

**2. `MANIFEST.sha256` + `verify-deployment.sh`.** Neo's line only proves *Neo* is
current; Tank could still be stale. The manifest covers all 42 agent files across the
three formats and costs zero tokens, since it never enters a prompt.

```bash
./verify-deployment.sh                  # is this repo self-consistent?
./verify-deployment.sh <dir> [format]   # is a deployed copy current? (default: opencode)
./verify-deployment.sh --update         # regenerate after changing any agent
```

Deployed files are matched by **basename**, so a flattened deploy directory works, and
the `.agent.md` → `.md` rename some deploys use is tolerated. Exit code is non-zero on
any stale or missing file.

> [!IMPORTANT]
> `--update` is part of changing an agent, not a separate chore. A manifest that
> silently drifts from the files is worse than no manifest — it reports OK on a stale
> deployment. The synchronization checklist below ends with it for that reason.

---

## Adding a New Agent

1. Write the canonical agent in `opencode/` with full OpenCode frontmatter and body
2. Confirm the frontmatter grants every capability the body assumes — in all three formats
3. Copy the body verbatim to `claude/` — apply Claude Code frontmatter only
4. Copy the body verbatim to `copilot/` — apply Copilot frontmatter only
5. Add the agent to the roster table in this file
6. Add the agent to Neo's `agents:` list in `copilot/neo.agent.md`
7. Add the agent to Neo's routing table in `opencode/neo.agent.md` — **all three formats**,
   since that table is body content and is what closes the roster
8. Update `CONDUCTOR.md` with the new agent's role, model, and lifecycle position
9. Update `README.md` with a brief description for human readers
10. Re-run the roster-closure check: does the new agent's role boundary create a request
    that no single agent can now serve?
11. Bump `TOPOLOGY VERSION` in `opencode/neo.agent.md`, then run
    `./verify-deployment.sh --update` to regenerate the manifest

---

## Authoritative References

- **Topology rules and lifecycle:** `CONDUCTOR.md` in this directory
- **OpenCode frontmatter schema:** `skills/agent-creator-opencode/references/agent-reference.md`
- **Copilot frontmatter schema:** `skills/agent-creator-copilot/references/frontmatter-reference.md`
- **Claude Code frontmatter schema:** See the `claude/` section above (no separate reference file)

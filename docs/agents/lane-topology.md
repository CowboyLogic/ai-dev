# The Lane Topology

A multi-agent development pattern that sizes itself to the work: process is assigned
**mechanically, before any work starts**, instead of every task running the same
lifecycle.

All agent files for this topology live at
[`agents/lane-topology/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/lane-topology)
in the repository. It ships in two client formats — [OpenCode](#installing-it-opencode)
(canonical) and [GitHub Copilot](#installing-it-github-copilot) (derived, same
prompts, translated frontmatter).

---

## What Problem Does This Solve?

It is the successor to the [Matrix Topology](matrix-topology.md), built on the same
core ideas — separate the producer from the reviewer, review cross-family, keep
delegation one level deep — and fixing what made that pattern expensive to use
day-to-day:

1. **There was no middle.** Work was either a two-line express change or a
   nine-stage lifecycle. A real bugfix, a refactor, or "how should I approach this"
   got the wrong one.
2. **Nothing asked questions.** There was no mode for "I know what I want, I don't
   know how to get there" — where a lot of real work actually lives.
3. **Green was self-reported.** The reviewer was read-only. Nobody independently
   confirmed the tests actually ran.

---

## The Lanes

Every request is classified into one of five lanes by a **table lookup, not a
judgment call** — first match wins.

| Lane | Trigger | Agents | Feels like |
|---|---|---|---|
| **MECHANICAL** | Textual/config change, no logic, no new dependency | Mechanic → Verifier | Seconds |
| **INVESTIGATE** | A question, or a bug with unknown cause | Investigator | Read-only, ends in an answer |
| **DIRECT** | Scope understood, approach obvious, bounded blast radius | Builder → Verifier | Minutes |
| **PLAN** | Goal known, approach isn't; a tradeoff; a contract change | Planner (Socratic) → Verifier | One question round, then a plan |
| **BUILD** | Net-new with no existing shape to follow | Planner → Builder → Verifier → Scribe | The full lifecycle |

When two lanes both apply, the Conductor takes the lighter one — except a new
architectural decision, a public contract change, or a security-critical surface
always takes the heavier lane, no matter how small the diff looks.

An INVESTIGATE lane ends in findings, not a change. The Conductor then re-classifies
the original request plus the findings, so "the fix is a one-line guard" becomes
DIRECT and "the whole session model is wrong" becomes PLAN.

See the [Lane Topology README](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/README.md)
for the full pattern — the Socratic planning protocol, verification-by-execution,
cross-family review, security bands, and the Facts Protocol that carries durable
findings between agents without re-deriving them.

---

## Agent Roster

| Agent | Model | Job | File |
|---|---|---|---|
| **Conductor** | Claude Sonnet 5 | Classifies, dispatches, holds the ledger, talks to you. Nothing else. | [conductor](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/conductor.md) |
| **Planner** | Claude Opus 5 | Socratic planning → design → Architecture Decisions → numbered requirements | [planner](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/planner.md) |
| **Investigator** | Gemini 3.1 Pro | Read-only comprehension and root-cause work | [investigator](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/investigator.md) |
| **Builder** | GPT-5.6-Terra | Implementation | [builder](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/builder.md) |
| **Mechanic** | Claude Haiku 4.5 | Trivial mechanical edits | [mechanic](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/mechanic.md) |
| **Verifier** | Gemini 3.1 Pro | Cross-family review **+ runs the tests itself** | [verifier](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/verifier.md) |
| **Adversary** | Claude Opus 5 | Security review, dispatched by risk band | [adversary](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/adversary.md) |
| **Scribe** | Claude Sonnet 5 | Documentation | [scribe](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/scribe.md) |
| **Researcher** | Claude Haiku 4.5 | External research | [researcher](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/researcher.md) |

The Conductor is the only agent you talk to and the only one with dispatch
authority (`mode: primary`); the other eight are subagents it routes work to. It
does not read source, write code, or review anything itself — every one of those is
a dispatch, which is what keeps its context small enough to stay coherent over a
long session.

---

## Verification Is Executed, Not Claimed

The Verifier **runs the build and the test suite itself** before reviewing anything
— a working agent's "it's green" is a claim, and the Verifier is where it becomes
evidence. It also hunts gaps before bugs: the unhandled case, the requirement with
no test, the error path that returns success.

Every review resolves to exactly one of three verdicts — `PASS`, `FIX`, or
`ESCALATE` — so a verdict can never half-agree with itself, and a missing verdict is
always treated as `FIX`, never as an implicit pass.

Reviewers run cross-family from whoever produced the artifact: the Verifier is
statically pinned to Gemini, and the Builder — the highest-risk artifact producer —
is pinned to GPT, so code is cross-family from both of its reviewers by
construction.

---

## Installing It — OpenCode

OpenCode is the canonical format. Symlink the harness config and the agent
directory into a **real** `~/.config/opencode/` directory — do not replace the
directory itself, OpenCode keeps its own state there.

```bash
git clone https://github.com/CowboyLogic/ai-dev ~/src/ai-dev

mkdir -p ~/.config/opencode
ln -sfn ~/src/ai-dev/harness/opencode-lane/opencode.jsonc  ~/.config/opencode/opencode.jsonc
ln -sfn ~/src/ai-dev/harness/opencode-lane/guardrails.md   ~/.config/opencode/guardrails.md
ln -sfn ~/src/ai-dev/agents/lane-topology/opencode          ~/.config/opencode/agents
```

`default_agent` is `conductor`. See the
[README's Deploying It section](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/README.md#deploying-it)
for the Windows junction commands and the two verification checks worth running
after every re-point.

---

## Installing It — GitHub Copilot

The [`copilot/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/lane-topology/copilot)
directory mirrors the same nine agents for GitHub Copilot (VS Code and the cloud
agent). Same prompts as the OpenCode originals — only the frontmatter is translated
(`permission` → `tools`, `mode` → `user-invocable`, model IDs → Copilot display
names). See
[`agents/lane-topology/AGENTS.md`](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/AGENTS.md#copilot-format--synchronization)
for the full mapping.

```bash
# Install the Conductor and all eight subagents
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/conductor.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/planner.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/investigator.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/builder.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/mechanic.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/verifier.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/adversary.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/scribe.agent.md
gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/researcher.agent.md
```

> Model pins and tool permissions are per-format frontmatter, not portable prompt
> content — installing the Copilot mirror gets you the same lane discipline and
> review loop, translated to what Copilot's agent schema can express. Path-scoped
> `edit` grants (Investigator and Researcher, scoped to `.agent-output/**` in
> OpenCode) do not port; see the AGENTS.md mapping linked above for the tradeoff.

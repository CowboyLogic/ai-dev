# The Lane Topology

A multi-agent development pattern that sizes itself to the work: process is assigned
**mechanically, before any work starts**, instead of every task running the same
lifecycle.

All agent files for this topology live at
[`agents/lane-topology/`](https://github.com/CowboyLogic/ai-dev/tree/main/agents/lane-topology)
in the repository. It ships in two client formats — [OpenCode](#installing-it-opencode)
(canonical) and [GitHub Copilot](#installing-it-github-copilot) (derived, same
prompts, translated frontmatter).

<!-- artifact-sync:inventory:start -->
| Kind | Name | Status | Source |
|---|---|---|---|
| Client | OpenCode | Canonical | [opencode/](https://github.com/CowboyLogic/ai-dev/tree/main/agents/lane-topology/opencode) |
| Client | GitHub Copilot | Derived mirror | [copilot/](https://github.com/CowboyLogic/ai-dev/tree/main/agents/lane-topology/copilot) |
| Harness | OpenCode | Runtime configuration | [opencode-lane/](https://github.com/CowboyLogic/ai-dev/tree/main/harness/opencode-lane) |
<!-- artifact-sync:inventory:end -->

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

Every request is classified into one of six lanes by a **table lookup, not a
judgment call** — first match wins.

| Lane | Trigger | Agents | Feels like |
|---|---|---|---|
| **REVERT** | Undo something already committed or shipped | Conductor + Verifier | Seconds — a revert commit on a branch |
| **MECHANICAL** | Textual/config change, no logic, no new dependency | Mechanic → Verifier | Seconds |
| **INVESTIGATE** | A question, or a bug with unknown cause | Investigator | Read-only, ends in an answer |
| **DIRECT** | Scope understood, approach obvious, bounded blast radius | Builder → Verifier | Minutes |
| **PLAN** | Goal known, approach isn't; a tradeoff; a contract change | Planner (Socratic) → Verifier | One question round, then a plan |
| **BUILD** | Net-new with no existing shape to follow | Planner → Builder → Verifier → Scribe → Verifier | The full lifecycle |

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

<!-- artifact-sync:roster:start -->
| Agent | Model | Job | Source |
|---|---|---|---|
| **Conductor** | `github-copilot/claude-sonnet-4.6` | Primary interactive agent. Classifies every request into a lane, dispatches the right specialist, holds the ledger, and talks to the human. The Conductor never reads source, never produces artifacts, and never reviews. It routes. On a clean PASS in a lane that produced a diff, it also commits, pushes, and opens the pull request — it never merges. | [conductor.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/conductor.md) |
| **Adversary** | `github-copilot/claude-opus-5` | Security review. Approaches every artifact as an attacker would — what should not be there, what was missed, what can be reached, what fails open. Dispatched into whatever lane the work is already in whenever the security band is critical. Returns PASS / FIX / ESCALATE with findings by severity. | [adversary.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/adversary.md) |
| **Builder** | `github-copilot/gpt-5.6-terra` | Implementation. Writes code in the working tree against a stated intent (DIRECT lane) or a Design Brief (BUILD lane), and gets it green. Does not design, does not decide architecture, does not review its own work. Up-ramps instead of guessing. | [builder.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/builder.md) |
| **Investigator** | `github-copilot/gpt-5.6-terra` | Codebase comprehension and root-cause analysis. Answers "why", "where", "how does this work", and "what does this touch". Reads widely, returns compactly. Never modifies the working tree; writes findings only to .agent-output/. The context firewall between the codebase and the Conductor. | [investigator.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/investigator.md) |
| **Mechanic** | `github-copilot/gpt-5.6-terra` | Trivial mechanical edits — typos, version bumps, config values, formatting, comments, log lines, mechanical renames. No logic changes, no control flow, no new dependencies. Fast and cheap by design. Stops the moment a change requires thought. | [mechanic.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/mechanic.md) |
| **Planner** | `github-copilot/gpt-5.6-sol` | Socratic planning, design, and specification. Interrogates the request before answering it — returns a QUESTION BRIEF of the decisions that must be made, then produces a Plan (PLAN lane) or a Design Brief with Architecture Decisions and numbered requirements (BUILD lane). Does not write code. | [planner.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/planner.md) |
| **Researcher** | `github-copilot/gpt-5.6-luna` | External information retrieval. Current library APIs, protocol details, version compatibility, error messages, vendor documentation. Returns findings with sources. Does not decide anything and does not touch the codebase. | [researcher.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/researcher.md) |
| **Scribe** | `github-copilot/gpt-5.6-luna` | Documentation. Writes docs that describe what the code actually does, not what it was supposed to do. Runs at the close of the BUILD lane or on demand. Reads the implementation before writing a word about it. | [scribe.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/scribe.md) |
| **Verifier** | `github-copilot/gemini-3.6-flash` | Cross-family review of every artifact and diff that leaves a lane. Unlike a pure reader, the Verifier runs the build and the tests itself — a working agent's "it's green" is a claim, and the Verifier is where it becomes evidence. Finds gaps, not just bugs. Returns PASS / FIX / ESCALATE. | [verifier.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/opencode/verifier.md) |
<!-- artifact-sync:roster:end -->

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

## Installing It: OpenCode

OpenCode is the canonical format. Symlink the harness config and the agent
directory into a **real** `~/.config/opencode/` directory — do not replace the
directory itself, OpenCode keeps its own state there.

```bash
git clone https://github.com/CowboyLogic/ai-dev ~/src/ai-dev

mkdir -p ~/.config/opencode
ln -sfn ~/src/ai-dev/harness/opencode-lane/opencode.jsonc  ~/.config/opencode/opencode.jsonc
ln -sfn ~/src/ai-dev/harness/opencode-lane/guardrails.md   ~/.config/opencode/guardrails.md
ln -sfn ~/src/ai-dev/harness/opencode-lane/commands         ~/.config/opencode/commands
ln -sfn ~/src/ai-dev/agents/lane-topology/opencode          ~/.config/opencode/agents
```

`default_agent` is `conductor`. See the
[README's Deploying It section](https://github.com/CowboyLogic/ai-dev/blob/main/agents/lane-topology/README.md#deploying-it)
for the Windows junction commands and the two verification checks worth running
after every re-point.

---

## Installing It: GitHub Copilot

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

> [!NOTE]
> Model pins and tool permissions are per-format frontmatter, not portable prompt
> content — installing the Copilot mirror gets you the same lane discipline and
> review loop, translated to what Copilot's agent schema can express. Path-scoped
> `edit` grants (Investigator and Researcher, scoped to `.agent-output/**` in
> OpenCode) do not port; see the AGENTS.md mapping linked above for the tradeoff.

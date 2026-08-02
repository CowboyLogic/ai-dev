# The Lane Topology

## A Multi-Agent Pattern That Sizes Itself to the Work

**Author:** Micheal Schexnayder
**Repository:** github.com/CowboyLogic/ai-dev
**Status:** Living Document
**Version:** 1.0.0
**Harness:** OpenCode

---

## What This Is

A nine-agent development topology for OpenCode, built around one idea: **the amount
of process a task gets should be determined mechanically, before any work starts.**

It is a successor to the [Matrix Topology](../matrix-topology/README.md) in the same
repository. That pattern established the ideas this one is built on — separate the
producer from the reviewer, review cross-family, keep delegation one level deep
because OpenCode does not run nested delegation reliably. The Lane Topology keeps all
of that and fixes the three things that made the Matrix version expensive to actually
use:

1. **There was no middle.** Work was either a two-line express change or a nine-stage
   lifecycle. Everything in between — a real bugfix, a refactor, "how should I
   approach this" — got the wrong one.
2. **Nothing asked questions.** There was no mode for "I know what I want, I don't
   know how to get there," which is where a lot of real work lives.
3. **Green was self-reported.** The reviewer was read-only. Nobody independently
   confirmed the tests actually ran.

---

## The Core Idea: Lanes

Every request is classified into one of five lanes by a **table lookup, not a
judgment call.** First match wins. This is what lets the system know the difference
between a task you want done and a task you want thought about — without you having
to say which.

| Lane | Trigger | Agents | Feels like |
|---|---|---|---|
| **MECHANICAL** | Textual/config change, no logic, no new dependency | Mechanic → Verifier | Seconds |
| **INVESTIGATE** | A question, or a bug with unknown cause | Investigator | Read-only, ends in an answer |
| **DIRECT** | Scope understood, approach obvious, bounded blast radius | Builder → Verifier | Minutes |
| **PLAN** | Goal known, approach isn't; a tradeoff; a contract change | Planner (Socratic) → Verifier | One question round, then a plan |
| **BUILD** | Net-new with no existing shape to follow | Planner → Builder → Verifier → Scribe | The full lifecycle |

MECHANICAL, DIRECT, and BUILD also commit, push, and open the PR once their verdict is
`PASS` — see [Shipping](#shipping--autonomous-but-merging-stays-yours). PLAN and
INVESTIGATE never do; one stops at an artifact awaiting your approval, the other
changes nothing.

### The tie-break rule

When two lanes both apply, **take the lighter one.** A DIRECT that up-ramps costs one
wasted dispatch. A PLAN that wasn't needed costs a human exchange and a heavy model
run.

**Except** — never down-lane past a hard trigger: a new architectural decision, a
public contract change, or a security-critical surface. Those always take the heavier
lane no matter how small the diff looks.

### Investigation re-classifies

INVESTIGATE ends in findings, not a change. The Conductor then re-runs the classifier
on the request *plus* the findings. "The fix is a one-line guard in `auth.go:88`"
becomes DIRECT. "The whole session model is wrong" becomes PLAN. This is the lane the
Matrix topology was missing entirely, and it is the one that makes the others land in
the right place.

---

## The Socratic Lane

This is the answer to "know the difference between a small task and a planning task."
Small tasks get done. Planning tasks get **interrogated first.**

The Planner runs in two passes:

**Pass 1 — the QUESTION BRIEF.** Before producing anything, the Planner returns:

- `UNDERSTOOD` — what the request unambiguously asks for
- `ASSUMED` — decisions it has already made and will run with unless overruled
- `DECISIONS` — three to five forks that genuinely change the shape of the work, each
  with options, tradeoffs, and **the Planner's recommendation**
- `UNKNOWN` — what it could not determine, and what would resolve it

The Conductor relays that to you as a numbered question set. You answer what you care
about. **Anything you don't answer resolves to the recommendation** — you can reply
"you pick" and still get a good plan.

**Pass 2 — the artifact.** Your answers go back and the Planner writes the plan.

**Hard cap: two rounds.** If your answers open new forks, the Planner may ask once
more. After that it makes every remaining call itself and records each one under
`ASSUMPTIONS`. A wrong assumption that is written down and reviewable is cheaper than
a third round of questions. Endless questioning is the hand-holding this lane exists
to eliminate.

A decision only earns a slot in `DECISIONS` if the answers lead to materially
different work. Preferences with an obvious default go in `ASSUMED`. A brief with
fifteen questions isn't thorough — it's the Planner offloading its job onto you.

---

## The Crew

Nine agents, five model tiers. Every role earns its slot on either a distinct
cognitive job or a distinct cost tier.

| Agent | Model | Job |
|---|---|---|
| **Conductor** | `claude-sonnet-5` | Classifies, dispatches, holds the ledger, talks to you. Nothing else. |
| **Planner** | `claude-opus-5` | Socratic planning → design → Architecture Decisions → numbered requirements |
| **Investigator** | `gemini-3.1-pro` | Read-only comprehension and root-cause work |
| **Builder** | `gpt-5.6-terra` | Implementation |
| **Mechanic** | `claude-haiku-4.5` | Trivial mechanical edits |
| **Verifier** | `gemini-3.1-pro` | Cross-family review **+ runs the tests itself** |
| **Adversary** | `claude-opus-5` | Security review, dispatched by risk band |
| **Scribe** | `claude-sonnet-5` | Documentation |
| **Researcher** | `claude-haiku-4.5` | External research |

### The Conductor does not do the work

It does not read source. It does not grep. It does not run tests. It does not write
code, plans, or docs. It does not review anything.

**Shipping is the one exception.** Once a lane's gating verdict is `PASS`, committing,
pushing, and opening the PR is git/gh plumbing, not a cognitive job — see
[Shipping](#shipping--autonomous-but-merging-stays-yours) below.

That is not modesty — it is the resilience mechanism. The Conductor's context must
stay routing-shaped. The moment it fills with file contents and test output, it stops
routing well and everything downstream degrades with it. When the Conductor needs to
know something about the codebase, it dispatches the Investigator and gets back a
compact answer.

### Context isolation is why there are multiple agents

The Investigator and the Researcher are **context firewalls.** Investigation and web
research burn enormous context on file contents, search results, and page dumps. All
of that stays inside those agents. What comes back is a short answer with `file:line`
references or sources.

This is the actual argument for a multi-agent system on long sessions — not role
specialization alone, but keeping the orchestrator's context clean enough to still be
making good decisions in hour three.

---

## Verification Is Executed, Not Claimed

The Verifier **runs the build and the test suite itself** before it reviews anything.
A working agent's report that it's green is a claim; the Verifier is where it becomes
evidence.

This is the single most important reliability property here, and it is what the
Matrix topology's read-only reviewer could not provide. Reading a diff does not catch
a suite that was never run.

The Verifier also hunts **gaps before bugs.** Any reviewer finds bugs. The valuable
finding is what *wasn't* done — the unhandled case, the requirement with no test, the
error path that returns success. Gap-finding requires the original intent, which is
why the Verifier refuses to review without it.

### Three verdict values

`PASS` · `FIX` · `ESCALATE`

One field, three values, so a verdict cannot half-agree with itself. There is no
conditional pass and no pass-with-outstanding-items.

- **`FIX`** — specific, actionable, inside the producing agent's scope. **Cap: two
  cycles.** On the third, it goes to you with both prior cycles' findings.
- **`ESCALATE`** — rooted outside the work's scope. Never handed back to the agent
  that couldn't resolve it.
- **Malformed or missing verdict** → treated as `FIX`, one retry, then escalated.
  Never treated as `PASS`. Silence is not approval.

Nothing in this topology loops indefinitely. Every loop has a hard cap and a defined
action on exhaustion.

---

## Shipping — Autonomous, But Merging Stays Yours

This topology is built to run without you in the loop for well-defined work, and
that includes the last step. Once MECHANICAL, DIRECT, or BUILD reaches a clean `PASS`
— the Verifier alone, or the Verifier and the Adversary on a critical surface — the
**Conductor** commits, pushes, and opens the pull request. You get a link, not a diff
to apply yourself.

**Merging is the one thing that stays manual, always.** No agent, including the
Conductor, ever merges, rebases, resets, or force-pushes — in any lane, under any
circumstance. Opening the PR is the full extent of this topology's authority over the
remote. That line is deliberate: it is the one decision in the whole system that is
expensive to unwind and visible to everyone else on the project the moment it is
wrong, so it is the one decision that is never automated.

**Never ships from `main` or `master`.** Before the first edit in any shipping lane,
the Conductor checks the current branch and creates a feature branch first if it is on
either. By the time a commit happens, `HEAD` cannot be a protected branch.

**A stricter project policy always wins.** If the repository's own `AGENTS.md` or
`CLAUDE.md` says "never commit" or "never push without approval," that overrides this
topology's default — the Conductor checks for it before shipping anything and stops,
verdict in hand, if it applies.

**The boundary is technically enforced, not just written down.** OpenCode's `bash`
permission supports per-command patterns, so the eight agents that are not the
Conductor have every git-mutation command (`commit`, `push`, `merge`, `rebase`,
`reset`, `cherry-pick`) and `gh pr create`/`gh pr merge` explicitly denied at the
permission layer. The Conductor's own `bash` grant is the inverse: everything denied
by default, with only the specific git/gh commands shipping requires allowed back in.
Neither is achievable in the Copilot format, which grants tools as an unscoped
boolean — see `AGENTS.md` → *Scoped bash does not port* for that tradeoff.

---

## Security Scales by Agent, Not by Ceremony

Three bands, and none of them change the lane:

- **Critical** — auth/authz logic; crypto, secrets, keys, tokens; deserialization of
  untrusted input; a change to a security control itself → **the Adversary is
  dispatched into whatever lane the work is already in.**
- **Adjacent** — reads a request param; builds a query/command/path from input;
  handles an upload; makes an outbound call → the Verifier gets a `SECURITY FOCUS`
  directive naming the surface.
- **Neither** — no security step.

A two-line change to a token check gets a full adversarial review. It does not get
dragged through a design lifecycle to earn one. That matters because **ceremony is
what makes people skip security review.**

---

## Cross-Family Review

Reviewers run on a different model family than whoever produced the artifact. Models
within a family share training approaches and inherent tendencies; the flaw a Claude
agent missed is disproportionately the flaw a Claude reviewer also misses. A different
family is a genuinely different lens, and that difference is the control.

This topology enforces it **by static pinning rather than routing:**

- **Verifier is Gemini** — cross-family from every producer in the roster, with no
  exceptions. One pin, no routing table, no gaps to track.
- **Builder is GPT** — so the highest-risk artifact in the system, code, is
  cross-family from *both* of its reviewers: the Verifier (Gemini) and the Adversary
  (Claude).

**The known trade:** the Adversary is Claude-pinned, so on Claude-family *documents*
(plans, design briefs) it shares a family with the producer. Those artifacts still get
a cross-family pass from the Verifier, and the Adversary's value on a design document
is adversarial posture and domain knowledge more than family independence. If that
proves wrong in practice, the fix is additive — add a GPT-pinned second Adversary and
route by producer family. Nothing else changes.

> **If the roster ever gains a Gemini-family producer,** the Verifier's guarantee
> breaks for it. Fix that by pinning the producer to another family, not by relaxing
> the requirement.

---

## Model Sizing

Five tiers, assigned by consequence and frequency — not by seniority.

| Tier | Model | Who | Why |
|---|---|---|---|
| Heavy reasoning | `claude-opus-5` | Planner, Adversary | Expensive to be wrong, infrequent to run |
| Balanced reasoning | `claude-sonnet-5` | Conductor, Scribe | Constant use, moderate cognitive load |
| Agentic coding | `gpt-5.6-terra` | Builder | Long tool loops, iterate to green |
| Long-context review | `gemini-3.1-pro` | Verifier, Investigator | Holds intent + artifact + full output at once |
| Fast and cheap | `claude-haiku-4.5` | Mechanic, Researcher | High frequency, fully specified work |

Two of these are worth calling out because they invert the obvious choice:

**The Conductor is not the biggest model.** It runs on every turn and holds the
longest-lived context, so it must be cheap and fast. Its actual cognitive load is low
by design — table lookup, brief writing, verdict reading. If it misclassifies in
practice, **tighten the classifier table before reaching for a bigger model.**

**The Mechanic exists purely as a cost tier.** Typo fixes and version bumps don't need
a coding model, and they run many times a day. The risk of a light model is that it
attempts something beyond its depth, which is why its scope is a hard checklist and
its default on any doubt is to stop with `NOT MECHANICAL` and re-lane.

---

## Resilience

Concretely, what makes this survive a long session:

1. **Independent execution** — no lane advances on a self-reported green
2. **Hard loop caps** — two fix cycles, two Socratic rounds, then a human or a
   documented assumption
3. **Three-value verdicts** — a verdict cannot contradict itself; a missing one is
   never a pass
4. **The ledger** — `.agent-output/<project>/ledger.md`, written at every dispatch,
   return, verdict, and decision. Survives compaction and is authoritative over
   recollection
5. **Context isolation** — the Conductor never touches source; the Investigator and
   Researcher absorb the expensive context
6. **Up-ramps everywhere** — every working agent can stop and return a lane-change
   notice rather than grinding on something too big for it
7. **Explicit failure handling** — an agent that errors or returns off-format twice
   stops the lane and surfaces to you by name. The Conductor never quietly does the
   work itself to cover a gap
8. **A permission-enforced git boundary** — merge, rebase, reset, and force-push are
   denied at the OpenCode permission layer for every agent, not just written into a
   prompt. Only the Conductor can commit, push, or open a PR, and only after `PASS`

Point 7 matters more than it looks. Filling a failed agent's gap with the
orchestrator's own output is exactly how a routing agent turns back into the
generalist agent this whole pattern exists to replace.

---

## The Facts Protocol — and Why Handoffs Stay Lossy

Every dispatch throws away almost everything the agent learned. That is *mostly*
correct: the compression is what keeps the orchestrator's context small, and small
context is the whole token economy of this system.

But two kinds of loss are pure waste, and the Facts Protocol recovers them.

**Facts propagate.** Agents return a `FACTS:` block — the real build command, how long
the suite takes, required env vars, where things actually live, what was tried and
failed. The Conductor collects it (single writer, so parallel dispatches can't clobber
a shared file) and carries it into later briefs. The Investigator's `file:line` map
goes into the Builder's brief **and** the Verifier's — re-deriving a map that already
exists is the most common avoidable cost in the system.

**Reasoning does not flow sideways.** A producing agent's justification for its choices
never reaches that artifact's reviewer. If the Builder's argument for skipping a case
lands in the Verifier's brief, the independent reviewer has been anchored to the
producer's frame — the exact shared-blindspot failure the cross-family pin exists to
prevent. Paying Gemini rates for a second opinion and then handing it the first
opinion is worse than not reviewing, because it looks like coverage.

So the Builder discloses `DEVIATIONS` as bare facts — "REQ-004 not implemented" — with
no defense attached. Disclosure is required, because an undisclosed deviation produces
a false finding and burns a cycle. Arguing it was correct is not disclosure.

**Durable facts get promoted.** "The suite takes four minutes and needs
`TESTCONTAINERS_RAM=4g`" is still true next month. It is not session state. When the
Conductor sees a fact that is a property of the *project* rather than the task, it
offers to add it to the project's own `AGENTS.md` — which every agent loads in every
future session, whether or not anyone remembers the ledger exists.

That promotion step is the highest-leverage token saving in the topology. A ledger has
to be read to help. Project instructions get loaded automatically.

The protocol runs in **PLAN and BUILD** and in any long session. It is skipped in
MECHANICAL and DIRECT, where the bookkeeping costs more than the rediscovery — except
promotion, which is always worth it, because that cost is paid once and recovered
forever.

---

## Escalation

Three tiers, same as its predecessor, because the model was right.

**Tier 1 — the agent resolves it.** A `FIX` inside the working agent's scope. No human
involvement.

**Tier 2 — the Conductor re-lanes it.** An `ESCALATE` rooted in a design gap, or a
working agent's up-ramp. The Conductor moves the work and continues. No human
involvement.

**Tier 3 — you decide.** Scope changes; accepting a known security risk; an
irreversible decision with real tradeoffs; two fix cycles that didn't converge; an
agent that failed twice; a plan awaiting approval to execute.

Tier 3 surfaces the issue, the options, what each agent recommends, and a specific
question. Not a status dump — a decision request.

---

## Deploying It

This section covers the OpenCode deployment — the canonical format and the one the
rest of this document describes. A GitHub Copilot mirror also ships in
`agents/lane-topology/copilot/`, with the same nine bodies and translated
frontmatter; see [`AGENTS.md`](AGENTS.md#copilot-format--synchronization) in this
directory for the frontmatter mapping and how to install it as Copilot custom
agents.

> [!IMPORTANT]
> **The two formats are not interchangeable at the frontmatter level.** OpenCode's
> `model`, `permission`, `mode`, and `hidden` properties have no equivalent in
> Copilot's agent schema — each format carries its own translated frontmatter, and
> only the body (the prompt) is shared between them.
>
> Subagents in `opencode/` ship `hidden: false` so you can `@`-mention them to
> confirm the roster loaded. `hidden` controls user selection only — it does not
> affect the Conductor's ability to dispatch them, so either value is safe.

```bash
git clone https://github.com/CowboyLogic/ai-dev ~/src/ai-dev
```

Symlink the three config entries individually into a **real** `~/.config/opencode/`
directory. Do not replace the directory itself — OpenCode keeps its own state there.

**Unix / WSL / macOS:**

```bash
mkdir -p ~/.config/opencode
ln -sfn ~/src/ai-dev/harness/opencode-lane/opencode.jsonc  ~/.config/opencode/opencode.jsonc
ln -sfn ~/src/ai-dev/harness/opencode-lane/guardrails.md   ~/.config/opencode/guardrails.md
ln -sfn ~/src/ai-dev/agents/lane-topology/opencode         ~/.config/opencode/agents
```

**Windows (directory junction for the agents folder, symlinks for the files):**

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\opencode"
New-Item -ItemType SymbolicLink -Force `
  -Path "$env:USERPROFILE\.config\opencode\opencode.jsonc" `
  -Target "$env:USERPROFILE\src\ai-dev\harness\opencode-lane\opencode.jsonc"
New-Item -ItemType SymbolicLink -Force `
  -Path "$env:USERPROFILE\.config\opencode\guardrails.md" `
  -Target "$env:USERPROFILE\src\ai-dev\harness\opencode-lane\guardrails.md"
New-Item -ItemType Junction -Force `
  -Path "$env:USERPROFILE\.config\opencode\agents" `
  -Target "$env:USERPROFILE\src\ai-dev\agents\lane-topology\opencode"
```

The agents directory is `agents/` — **plural**. `default_agent` is `conductor`, which
resolves to `agents/conductor.md`.

### Verify before you trust it

Two checks, both under a minute, and worth doing every time you re-point the symlinks:

1. **`@builder` in a session.** If it autocompletes and resolves, the roster is
   loading. If it doesn't, nothing below matters. (All agents ship with
   `hidden: false` so they're `@`-mentionable for exactly this check.)
2. **Ask the Conductor to name its roster.** It should list the eight lowercase
   identifiers. If it describes generic capabilities instead, you are talking to the
   built-in agent, not the Conductor.

The Conductor also self-checks on its first dispatch of every session and stops with
a configuration error if a dispatch resolves to a general-purpose agent. That is
deliberate: a general agent returning plausible output is the most expensive failure
mode here, because the system looks like it is working while lane discipline, model
pinning, and cross-family review are all silently absent.

The harness lives in `harness/opencode-lane/`, kept separate from `harness/opencode/`
so the Matrix setup is untouched — re-point the symlinks to switch between the two.

### Commands

The Conductor classifies automatically. These are deterministic overrides for when you
already know the lane:

| Command | Lane |
|---|---|
| `/change <request>` | DIRECT |
| `/plan <request>` | PLAN — Socratic |
| `/find <question>` | INVESTIGATE — read-only |
| `/build <request>` | BUILD — full lifecycle |
| `/handoff` | Write a session handoff document |

Just talking to it works too. The commands exist for when you want to skip
classification, not as the normal way in.

---

## Growing It

The roster is deliberately small. Add only when a role earns its slot on a distinct
cognitive job or a distinct cost tier.

**Documented growth paths:**

- **Split the Planner** into Designer / Architect / Spec Writer when projects get big
  enough that one artifact with three sections stops being enough. Purely additive.
- **Add a GPT-pinned Adversary** and route security review by producer family, if the
  same-family document review proves to be a real gap.
- **Add a dedicated operational validator** — "tests pass" and "the app works" are
  different statements, and if that gap bites in practice it wants its own agent with
  container access.
- **Add domain specialists** — database, infrastructure, compliance — as roles the
  Conductor routes to inside an existing lane.

**Do not** add an agent because a stage feels like it deserves one. Every agent is a
dispatch, a handoff, and a place for context to be lost.

---

## License

MIT. Use it, adapt it, share it. Attribution appreciated but not required.

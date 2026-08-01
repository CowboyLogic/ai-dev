# AGENTS.md — Lane Topology Maintenance Directive

> Read this file before modifying any agent in this directory tree.

---

## Purpose

This directory contains the Lane Topology — a nine-agent system whose defining
property is that **process is assigned mechanically, before work starts.**

It ships in two client formats: `opencode/` (canonical) and `copilot/` (derived).
There is no `claude/` mirror yet — add one only when it is actually requested, not
speculatively. `opencode/` is the canonical source; `copilot/` frontmatter is adapted
per the mapping below, but **the body (everything after the frontmatter `---`) must
be character-for-character identical between the two.** A body that diverges is a
bug, not a variant — see Frontmatter Differences below for the synchronization rule
this implies.

---

## Directory Structure

```
agents/lane-topology/
├── opencode/          # Agent definitions (canonical)
├── copilot/           # GitHub Copilot format (derived from opencode/)
├── AGENTS.md          # This file
└── README.md          # Human-facing pattern documentation

harness/opencode-lane/
├── opencode.jsonc     # default_agent, lane commands, MCP
└── guardrails.md      # persistent session guardrails
```

`opencode/conductor.md` is the **authoritative technical reference** for the
topology — the classifier table, lane procedures, verdict handling, the ledger, and
escalation tiers all live there. `README.md` explains the same system to a human and
must not contradict it. When they disagree, the agent file is right and the README is
a bug.

---

## The Roster

| File | Identifier | Model | Family | Tools | Role |
|---|---|---|---|---|---|
| `conductor.md` | `conductor` | `claude-sonnet-5` | Claude | read, edit, task | Classify, dispatch, ledger, human interface |
| `planner.md` | `planner` | `claude-opus-5` | Claude | read, edit, grep | Socratic planning, design, ADs, requirements |
| `investigator.md` | `investigator` | `gemini-3.1-pro-preview` | Gemini | read, grep, bash, edit→`.agent-output/**` | Read-only comprehension and root cause |
| `builder.md` | `builder` | `gpt-5.6-terra` | GPT | read, edit, bash, grep | Implementation |
| `mechanic.md` | `mechanic` | `claude-haiku-4.5` | Claude | read, edit, bash | Trivial mechanical edits |
| `verifier.md` | `verifier` | `gemini-3.1-pro-preview` | Gemini | read, grep, bash | Cross-family review + independent execution |
| `adversary.md` | `adversary` | `claude-opus-5` | Claude | read, grep, bash | Security review |
| `scribe.md` | `scribe` | `claude-sonnet-5` | Claude | read, edit, grep | Documentation |
| `researcher.md` | `researcher` | `claude-haiku-4.5` | Claude | read, grep, webfetch, websearch, edit→`.agent-output/**` | External research |

`conductor` is `mode: primary`. Everything else is `mode: subagent`.

All agents currently ship `hidden: false` so they can be `@`-mentioned directly —
this is the fastest way to prove the roster is loading. `hidden` affects only `@`
autocomplete, never task-tool availability, so setting it either way is safe once
the setup is validated.

---

## External Dependency — the `about-me` skill

The Conductor loads a skill named **`about-me`** as step 1 of its Session Start
sequence. It carries the working context and philosophy of the person running the
session, and it shapes brief construction, question framing, and escalation tone.

**It is not shipped in this repository.** It lives in the global skills directory
(`~/.agents/skills/about-me/`) and is installed per machine. On a machine without it,
the Conductor prints a one-line notice and runs without personal context — degraded,
not broken.

Why it is loaded explicitly rather than left to discovery: skills use **progressive
disclosure**, so a skill loads when the model judges it relevant. `about-me` is always
relevant, and its relevance is never visible from the request text — so nothing would
ever trigger it. An always-on skill has to be named at session start.

> [!NOTE]
> `planner` is the other candidate for this skill — it is the only other agent that
> addresses the human directly, and its QUESTION BRIEF would be better calibrated with
> personal context. It is deliberately *not* loaded there yet: it would cost tokens on
> every PLAN run, and the Conductor relays those questions anyway. Revisit if the
> Planner's questions read as poorly pitched.

---

## OpenCode Discovery Notes

**These agents are harness-specific and not portable.** The body is shareable across
clients; the frontmatter is not. OpenCode's `model`, `permission`, `mode`, and
`hidden` properties have no equivalent in the Copilot agent schema, so a file that
runs here will not run there with its model pin or permissions intact. File naming is
therefore not a compatibility concern — `.md` and `.agent.md` both load in OpenCode.
Do not maintain a naming convention for cross-client portability that the frontmatter
already makes impossible.

**Discovery:** `~/.config/opencode/agents/<name>.md` globally, `.opencode/agents/`
per-project. The directory is `agents/` — plural. There is no `name:` property; the
identifier is the filename.

**`default_agent` must name a `primary`-mode agent.** It is `conductor` here. The
OpenCode default is the built-in `build` agent.

### Verified behavior — do not re-derive these from the schema docs

Each of these was established against a running OpenCode install, and each one
contradicts a plausible reading of the reference documentation. Trust this list over
the schema.

| Behavior | Status |
|---|---|
| `.agent.md` and `.md` both load | Both work. Naming is not load-bearing. |
| `hidden: true` blocks agent-to-agent dispatch | **False.** It only removes the agent from user selection. The Matrix topology's primary dispatches hidden subagents without issue. |
| Agents are portable across clients | **False.** `model`, `permission`, `mode`, and `hidden` have no Copilot equivalent. Bodies are shareable; frontmatter is not. |
| `default_agent` may name a subagent | **False.** It must name a `primary`-mode agent. |
| A `general` dispatch means the roster failed to load | **False.** The roster loaded and the Conductor *chose* `general`, because no single agent covered the request. See Roster Closure. |

> [!IMPORTANT]
> **A `general` dispatch is a roster problem, not a config problem.** That was the
> original misdiagnosis and it cost several rounds. The roster loads fine; `general`
> gets chosen when the eight leave a request with no legal move.
>
> When a dispatch problem appears, ask the Conductor to list its available subagents
> by identifier. If it names the eight, the configuration is sound and the cause is
> in the roster or the prompt — do not go looking at file names, `hidden`, or
> symlinks.

---

## Copilot Format & Synchronization

`opencode/` is canonical. `copilot/` is derived from it: same nine bodies, character
for character, with frontmatter translated per the tables below. This is the same
rule `agents/matrix-topology/` uses for its three formats — see that directory's
`AGENTS.md` for the fuller version of this discipline if a `claude/` mirror is ever
added here.

### Frontmatter mapping

| OpenCode | Copilot | Note |
|---|---|---|
| `name` | *(derived from filename)* | Copilot has no `name:` requirement; the filename (`<identifier>.agent.md`) carries it. |
| `description` | `description` | Copied verbatim. |
| `model` | `model` | See Model Name Mapping below. |
| `permission` | `tools` | See Tool Mapping below. |
| `mode: primary` | *(omit `user-invocable`, defaults to shown)* | Only `conductor` is primary. |
| `mode: subagent` | `user-invocable: false` | All eight subagents. |
| `hidden` | *(no equivalent — omit)* | OpenCode's `hidden` only affects `@`-mention autocomplete; Copilot's nearest concept, `user-invocable`, is already carrying the primary/subagent distinction above. |
| — | `agents:` | `conductor` only — the list of the eight subagent identifiers it may dispatch. Requires `"agent"` in `conductor`'s `tools`. |

### Tool mapping

Only the aliases this roster actually uses:

| OpenCode permission | Copilot tool alias |
|---|---|
| `read` | `"read"` |
| `edit` | `"edit"` |
| `bash` | `"run"` |
| `grep` | `"search"` |
| `webfetch` / `websearch` | `"web"` |
| `task` | `"agent"` |
| `skill` | *(no equivalent — omit)* |

### Model name mapping

| OpenCode `model` | Copilot `model` |
|---|---|
| `github-copilot/claude-sonnet-5` | `Claude Sonnet 5 (copilot)` |
| `github-copilot/claude-opus-5` | `Claude Opus 5 (copilot)` |
| `github-copilot/claude-haiku-4.5` | `Claude Haiku 4.5 (copilot)` |
| `github-copilot/gpt-5.6-terra` | `GPT-5.6-Terra (copilot)` |
| `github-copilot/gemini-3.1-pro-preview` | `Gemini 3.1 Pro (copilot)` |

### Scoped `edit` does not port

`investigator` and `researcher` hold `edit` scoped to `.agent-output/**` in OpenCode
— they write their own artifacts without touching the working tree. Copilot cannot
express a path-scoped tool grant, so both get an unscoped `"edit"`. The scope is
preserved by prompt discipline in the body (both name their exact output path) but is
**not harness-enforced in the Copilot format.** Do not read the unscoped `"edit"` in
`copilot/investigator.agent.md` or `copilot/researcher.agent.md` as license to widen
either role — the Constraints section in the body is still the actual boundary.

### Synchronization checklist

When modifying any agent body:

- [ ] Updated the body in both `opencode/` and `copilot/` — identical, character for
      character
- [ ] If frontmatter changed: applied the correct translation per the tables above
- [ ] Verified `description` is identical across both folders
- [ ] Body/frontmatter agreement: every capability the body assumes is actually
      granted in `tools` (Copilot) and `permission` (OpenCode) — OpenCode defaults
      unlisted permissions to allow, so a missing grant is invisible there and a hard
      failure in Copilot, where `tools:` is a strict allowlist

Verify body parity mechanically rather than by eye:

```bash
cd agents/lane-topology
for f in opencode/*.md; do a=$(basename "$f" .md)
  diff -q <(sed -n '/^---$/,$p' "$f" | sed '1,/^---$/d') \
          <(sed -n '/^---$/,$p' "copilot/$a.agent.md" | sed '1,/^---$/d') \
    || echo "DRIFT: $a"
done
```

---

## Invariants

These are the properties the topology depends on. Breaking one is a redesign, not an
edit — if you change one, update `README.md` and `conductor.md` in the same
change and say what replaced it.

1. **Only the Conductor has `task`.** Nested subagent delegation does not run
   reliably in OpenCode. Every dispatch is one level deep. A subagent that needs
   another agent returns an up-ramp or escalation notice instead.

2. **The Conductor produces nothing and reviews nothing.** No source reads, no grep,
   no test runs, no artifacts, no reviews. Its `read` is for the ledger and artifact
   files; its `edit` is for the ledger. This is what keeps its context routing-shaped
   over a long session.

3. **The Verifier is cross-family from every producer.** Currently satisfied by a
   static Gemini pin against a roster of Claude and GPT producers. **Adding a
   Gemini-family producer breaks this.** Fix it by pinning that producer to another
   family — not by relaxing the requirement.

4. **The Builder is GPT-pinned.** This is structural, not a preference: it makes code
   — the highest-risk artifact — cross-family from both the Verifier (Gemini) and the
   Adversary (Claude) with no routing logic.

5. **The Verifier executes.** It runs the build and test suite itself. No lane
   advances on a working agent's self-reported green. Removing `bash` from the
   Verifier removes the topology's main reliability property.

6. **Verdicts are exactly `PASS` / `FIX` / `ESCALATE`.** One field, three values. Do
   not add a fourth, a conditional pass, or a separate outstanding-items count. A
   missing or malformed verdict is treated as `FIX`, retried once, then escalated —
   never as `PASS`.

7. **Every loop has a hard cap.** Two fix cycles per artifact; two Socratic rounds per
   plan; two attempts per failing agent. Each cap has a defined action on exhaustion.
   No loop in this topology may be open-ended.

8. **The classifier is a lookup, first-match-wins.** If lane selection becomes a
   judgment call, the system loses the property it is named for. Fix misclassification
   by tightening trigger wording, not by adding discretion.

9. **No agent performs git state changes.** No commit, push, merge, rebase, or reset,
   in any lane, by any agent.

10. **Facts propagate; reasoning does not flow sideways.** Agents return a `FACTS:`
    block; the Conductor is the single writer that collects it and carries it into
    later briefs. A producing agent's *justification* for its choices must never
    reach that same artifact's reviewer — that anchors the independent review to the
    producer's frame and silently voids the cross-family control. Rationale flows
    forward to the Conductor and to the next producer, never sideways to a peer
    reviewer. See `conductor.md` → Facts Protocol.

---

## Roster Closure — the failure this topology actually hit

OpenCode always offers `general` (full tool access, no role constraint). It is
permanently available as an escape hatch, and it will be taken whenever the roster
leaves a request with no legal move.

**Observed in real use.** A request combined external research with writing a file.
`researcher` had web access but no `edit`; `scribe` had `edit` but no web access.
No single agent could do it, so the Conductor dispatched `general` — which then
ignored the brief and did its own thing. Asked afterward, it explained the correct
decomposition perfectly. **The reasoning was available in retrospect and not at the
decision point.**

Two rules follow, and both are load-bearing.

**1. Close the escape hatch explicitly.** `conductor.md` bans `general` and `explore`
unconditionally — not "if the roster fails to load," which was the original and
useless framing. A rule stated as a diagnostic for a *config* problem does not fire
when the config is healthy and the agent simply finds the roster inconvenient.

**2. Any two agents must compose without a third.** When adding or narrowing an
agent, check the roster for a plausible request that no single agent can serve. If
one exists, either the Conductor has an explicit decomposition path for it, or the
gap gets filled by `general` the first time it comes up.

This is why `researcher` and `investigator` hold `edit` scoped to
`.agent-output/**`. It is not a relaxation of their read-only role — the working
tree is still off limits — it is what lets them hand a large artifact to the next
agent by path instead of pushing it through the Conductor's context, which is re-sent
on every turn.

> [!WARNING]
> **Rule order matters, and the failure is silent.** OpenCode evaluates permission
> patterns in order and **the last matching rule wins**, so the catch-all `"*"` goes
> **first** and the specific grant after it:
>
> ```yaml
> edit:
>   "*": deny                    # catch-all FIRST
>   ".agent-output/**": allow   # specific override AFTER
> ```
>
> Both agents originally shipped this inverted — `".agent-output/**": allow` first,
> `"*": deny` last — which made `"*"` the last match for every path and denied them
> **all** edits, including the directory the grant was written for. The roster-closure
> fix was therefore inert: `researcher` still could not write, and the two-concern
> request that caused the original `general` dispatch would have reproduced exactly.
>
> This is the same lesson one layer down. The block *reads* correct, OpenCode raises
> no error, and nothing surfaces until an agent quietly fails to produce its artifact.
> Authoritative source:
> `skills/agent-creator-opencode/references/agent-reference.md` → *Pattern matching
> rules*. Load that skill before editing any OpenCode frontmatter.

Both failures above share one root, and it generalises past agent selection.

> [!IMPORTANT]
> **A rule that requires reasoning at the decision point will lose to a convenient
> default.** Prefer closed sets, lookups, and unconditional prohibitions over
> guidance the agent has to weigh. This is the same principle the lane classifier is
> built on; agent selection needed it too and did not have it.

### The same gap, in the other direction: fan-out

The roster gap made the Conductor reach for one agent that was *too broad*. The
absence of a fan-out rule made it use one agent where several were needed — a
request producing six independent files was handled by a single dispatch.

Both are the same missing question: **how many dispatches does this request need?**
The original design only ever answered "which agent," never "how many."

`conductor.md` now carries a dependency test — *does producing A require knowing the
contents of B?* Yes means one artifact and one dispatch; no means separate artifacts
and separate dispatches. The Conductor states the count out loud before dispatching,
because an unstated count defaults to one.

Note that this is a **context-quality** rule, not a concurrency rule. An agent
producing many independent outputs in one run degrades on the later ones. That is
true whether or not the harness runs dispatches in parallel, which remains
unverified and does not matter to the decision.

---

## Changing an Agent

- **Body change** (anything after the frontmatter `---`) → update it in both
  `opencode/<name>.md` and `copilot/<name>.agent.md`, identically. A body that
  diverges between the two is a bug.
- **Model change** → update the `model:` field in both formats (see Model Name
  Mapping), then update that agent's *Model Selection Rationale* section (body — so
  update it once, in both files). If the change alters the agent's model *family*,
  check invariants 3 and 4 before proceeding.
- **Tool change** → update `permission:` in `opencode/` and `tools:` in `copilot/`
  (see Tool Mapping), and the agent's Constraints section in the body. Granting
  `task` (`"agent"` in Copilot) to a subagent violates invariant 1.
- **Role change** → update the agent file in both formats, the Conductor's routing
  table (body — updates both automatically once synced), the classifier table if
  lane assignment changed, and the README roster.
- **Any change touching lanes, verdicts, or caps** → update `conductor.md` /
  `conductor.agent.md` first; it is authoritative. Then reconcile the README.
- Run the synchronization checklist above before considering the change done.

---

## Adding an Agent

An agent earns a slot only by providing either a **distinct cognitive job** or a
**distinct cost tier**. "This stage feels like it deserves an agent" is not a reason —
every agent is a dispatch, a handoff, and a place for context to be lost.

1. Write the canonical agent in `opencode/` as `<identifier>.md` — the filename is
   the dispatch identifier, and there is no `name:` property. Ship `hidden: false`
   (see OpenCode Discovery Notes)
2. Copy the body verbatim to `copilot/<identifier>.agent.md`, applying the Copilot
   frontmatter mapping above. Add it to `conductor.agent.md`'s `agents:` list
3. Add it to the roster table above, with its model family
4. Check invariants 3 and 4 against its model family
5. Add it to the Conductor's routing table (body — covers both formats once synced)
6. Add a classifier trigger if it introduces a lane, or name the lane it serves
7. Add it to the README roster and model-tier table

---

## Agent File Structure

Every agent file carries these sections. Keep them in this order.

1. Frontmatter — `name`, `description`, `model`, `permission`, `mode`, `hidden`
2. `# <Name>` and `## Role` — what it does and, where non-obvious, why it exists
3. `## Inputs` — the brief it receives from the Conductor, as a fenced block
4. `## Working Protocol` — how it does the work
5. `## Outputs` — the structured return block
6. Up-ramp / escalation criteria — when it stops instead of continuing
7. `## Model Selection Rationale` — the pin, the family, and the argument for it
8. `## Constraints` — the hard "does not" list

Keep files short. Prompt length is both a resilience cost and a direct token cost —
every line competes for attention with every other line, and the primary agent's
prompt is re-sent on every turn of every session.

Current state: `conductor.md` is 376 lines, every other agent is under 200.
The Conductor is the one that should worry you, because it is the file that gets
re-sent most often. It is a standing candidate for the skills refactor below.

> [!NOTE]
> **Planned: move methodology into skills.** OpenCode discovers skills globally from
> `~/.agents/skills` and follows the Agent Skills standard, including progressive
> disclosure — so procedural knowledge loads only when it is actually triggered,
> instead of on every dispatch.
>
> An agent file should carry only what a skill cannot: the **model pin**, the **tool
> permissions**, the **role boundary**, and the **output contract** the Conductor
> parses. Everything else is a skill.
>
> Clear candidates already written into these files:
> `adversary.md` → Review Discipline (trust boundaries, hostile input,
> fail-closed, what leaks, what was removed) ·
> `scribe.md` → Markdown Standards (largely duplicates the existing
> `google-style-docs` and `markdownlint-validator` skills) ·
> `planner.md` → the AD format and RFC 2119 requirement templates ·
> `investigator.md` → the hypothesis-first protocol.
>
> The model pin is the one thing that genuinely cannot become a skill, and it is
> load-bearing here: dynamically spawned agents inherit the session model, which
> would collapse both the cross-family review control (invariants 3 and 4) and the
> five-tier cost ladder into a single model.

---

## Relationship to the Matrix Topology

`agents/matrix-topology/` is the predecessor and remains published and usable. The
two are independent: separate agent directories, separate harness configs, separate
symlink targets. Switching between them is re-pointing `~/.config/opencode`.

Changes to one do **not** propagate to the other. They are different patterns, not
different formats of the same pattern.

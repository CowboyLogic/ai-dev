---
name: about-me
description: Durable personal context about the person running this session — their background, tooling, constraints, and how they want agents to work with them. Load at the start of every session, and whenever calibrating tone, autonomy, technical depth, or workflow. This is a template; if it has not been filled in yet, walk the user through customizing it.
license: MIT
---

# About Me

> [!IMPORTANT]
> **STATUS: TEMPLATE — NOT YET CUSTOMIZED.**
>
> This file still contains its shipped placeholder content. Do not treat anything
> below the *Working Style* heading as fact about the current user — it is
> illustrative scaffolding, not their profile.
>
> **When you load this file and this notice is still present**, say so in one line and
> offer to fill it in. Follow [Customizing This File](#customizing-this-file) below.
> Then delete this entire callout — its presence is the only signal that the file is
> still a template.

---

## What This Skill Is For

Agents calibrate constantly: how much to explain, when to ask versus decide, how
formal to be, whether to show working. Without context they calibrate to a generic
average, which is wrong for almost everyone and wrong in a way that is invisible —
the output looks fine and quietly does not fit.

This file is the fix. It carries the facts about one person that are **durable**
(true next month, not just this task) and **not derivable** from the repository, the
code, or the conversation so far.

**Why it must be loaded explicitly.** Skills use progressive disclosure — they load
when a model judges them relevant to the request. That heuristic fails completely
here: this skill is *always* relevant, and its relevance is never visible in the text
of any request. Nothing would ever trigger it. An always-on skill has to be named at
session start, which is why the agents that use it name it as step one rather than
waiting for something to match.

**What does not belong here:** anything the repo already states (that belongs in
`AGENTS.md`), anything true of one task only, credentials or secrets of any kind, and
anything the user would not want an agent to read aloud.

---

## Customizing This File

**Run this as a conversation, not a form.** The goal is a short, high-signal file —
roughly 40 to 80 lines. A long profile is worse than a short one: every line competes
for attention with every other line, and it is re-read on every session.

### How to run the interview

1. **Ask what is already written down.** A CV, a bio, an existing `AGENTS.md`, a
   README they wrote. Offer to draft from that instead of asking questions they have
   already answered elsewhere.
2. **Work through the sections below in order**, one at a time. Show the user what you
   are writing as you go — do not interview them for ten minutes and then produce a
   file.
3. **Ask for the *why*, not just the *what*.** "Prefers concise answers" is weak.
   "Prefers concise answers because they are usually reading on a phone between
   meetings" tells an agent what to do in a case nobody anticipated. Preferences with
   a reason attached generalize; bare preferences do not.
4. **Push back on vagueness.** "Be professional" and "write good code" are not
   calibration — every agent already believes it is doing both. Ask what specifically
   went wrong the last time an assistant got it wrong. Corrections are the highest
   signal content available, because they mark where the generic default missed.
5. **Let them skip anything.** A section with nothing worth saying should be deleted,
   not filled with filler. An empty section costs tokens and teaches nothing.
6. **Delete the STATUS callout at the top** when the file is genuinely customized.
   That callout is the only marker distinguishing a real profile from this template.

### Good questions to draw on

Offer a few of these at a time rather than all at once:

- What do you do, and what is the technical depth you want assumed?
- What are you usually building, and in what stack?
- Which tools do you actually work in day to day? Do different tools mean different
  constraints — cost ceilings, offline work, an approval process, no network?
- When should an agent just decide, and when must it stop and ask you?
- What does a good answer look like — the conclusion first, or the reasoning?
- What has an AI assistant repeatedly gotten wrong with you?
- Is there anything you want agents to never do without asking first?
- Are there hard constraints — a token or cost budget, compliance rules, a language
  or license you cannot use?

### After it is written

Read it back and ask one question: *if an agent knew only this, would it behave
noticeably differently?* If not, it is too generic — go back for the specifics.

Then tell the user where it lives and that it should be revised whenever they catch
themselves giving the same correction twice. **A correction repeated is a line
missing from this file.**

---

## Template

Everything from here down is placeholder. Replace it. The headings are a starting
point, not a required schema — cut what does not apply and add what does.

### Working Style

<!-- How this person wants to be worked with. The most valuable section — write it
     first and make it specific. -->

- **Directness:** e.g. *No preamble. Lead with the answer, then the reasoning. Do not
  open by restating the question.*
- **Disagreement:** e.g. *Challenge my assumptions. If I am wrong about a premise, say
  so before answering — do not answer the question I should have asked while pretending
  it was the one I asked.*
- **Praise:** e.g. *Skip it. "Great question" is noise.*
- **Length:** e.g. *Short by default. Expand when I ask, or when the detail changes a
  decision.*
- **Uncertainty:** e.g. *Say "I don't know" plainly. A confident wrong answer costs me
  more than an admitted gap.*

### Autonomy

<!-- Where the line sits between deciding and asking. Vague answers here produce
     agents that either pester or overreach. -->

- **Decide without asking:** e.g. *Anything reversible. Formatting, naming, structure,
  which library to reach for in a spike.*
- **Ask first:** e.g. *Anything that touches production, costs money, sends an email,
  or is hard to undo.*
- **Never without explicit instruction:** e.g. *Commit, push, merge, force-push,
  delete a branch, or modify CI.*

### Background

<!-- Only what changes how an agent should explain things. Job title alone rarely
     does; what they are expert in and what they are new to always does. -->

- **Role:** e.g. *Platform engineer, twelve years, mostly infrastructure.*
- **Assume fluency in:** e.g. *Go, Kubernetes, SQL, distributed systems.*
- **Explain more carefully:** e.g. *Frontend, anything CSS, ML internals.*

### Tooling and Environment

<!-- Where the work actually happens, and any constraint that follows from it. -->

- **Editors / agents:** e.g. *Claude Code at home, OpenCode at work.*
- **Stack:** e.g. *Python 3.14 with uv, Postgres, Terraform.*
- **Platform:** e.g. *macOS, zsh.*
- **Constraints:** e.g. *Hard monthly token ceiling at work — cost is a design
  constraint, not an afterthought. Prefer cheap models for mechanical work.*

### Current Focus

<!-- Optional, and the section most likely to go stale. Include it only if it is worth
     maintaining. Use absolute dates, never "recently" or "this quarter". -->

- e.g. *Through March 2026: migrating the billing service off the legacy queue.*

### Hard Rules

<!-- Non-negotiables. Keep this list genuinely short — a long list of absolutes gets
     treated as a long list of suggestions. -->

- e.g. *Never hardcode a secret, even in an example.*
- e.g. *Never invent a citation, a benchmark number, or an API that might not exist.*

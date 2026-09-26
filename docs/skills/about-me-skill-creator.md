# About-Me Skill Creator

Generate a private `about-me` skill that tells agents how to work with you: your durable
background, tooling constraints, communication preferences, and autonomy boundaries. The
skill is a **generator**, not a profile template. It runs a short conversational wizard and
writes a personal `about-me/SKILL.md` outside any shared repository.

- **Skill name:** `about-me-skill-creator`
- **Last updated:** 2026-08-06
- **Source:** [skills/about-me-skill-creator](https://github.com/CowboyLogic/ai-dev/tree/main/skills/about-me-skill-creator)

---

## What it does

Agents that know nothing about the person running a session fall back to generic defaults
for tone, depth, and how much to do without asking. A short, specific profile loaded at the
start of every session fixes that. This skill interviews you and drafts that profile.

**Wizard steps:**

1. **Select a mode** — create a new profile, refresh an existing one, or draft from material
   you provide (a CV, bio, README, or existing instructions).
2. **Select a destination** — `~/.claude/skills/about-me` (default), `~/.agents/skills/about-me`,
   or a custom absolute path. The wizard confirms before replacing an existing file.
3. **Gather the profile** — working style, autonomy, background, tooling and constraints,
   hard rules, and an optional dated current-focus section.
4. **Draft and review** — show the draft, remove generic statements, confirm, then write
   `<destination>/SKILL.md`.

**Generated profile sections:**

| Section | What it captures |
|---------|------------------|
| Working Style | Directness, answer length, reasoning depth, how to handle disagreement |
| Autonomy | Decide without asking / ask first / never without explicit instruction |
| Background | Role, fluencies to assume, areas that need more explanation |
| Tooling and Environment | Editors, agent clients, stack, platform, budget or compliance limits |
| Current Focus | Optional, dated, kept only if you intend to maintain it |
| Hard Rules | A short list of non-negotiable practices |

The wizard asks for the reason behind each preference so agents can generalize from it, and
challenges vague input such as "be professional". The target length is 40–80 lines.

> [!IMPORTANT]
> The generated profile is personal context. Do not commit it to a shared repository, and
> never include credentials, tokens, or anything you would not want an agent to repeat.

The [Lane Topology](../agents/lane-topology.md) Conductor loads the `about-me` profile as
step one of every session.

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill about-me-skill-creator -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill about-me-skill-creator --agent <agent> -g
```

### Verify installation

```bash
npx skills ls -g
```

For OpenCode, write the profile to `~/.agents/skills/about-me`, or symlink that location to
the Claude Code copy so both tools share one profile.

---

## Maintenance

Refresh the profile when you give an agent the same correction twice. A repeated correction
is the strongest signal that a durable instruction is missing. In refresh mode the wizard
reads the existing profile first, keeps entries that are still accurate, and removes stale
ones rather than accumulating contradictions.

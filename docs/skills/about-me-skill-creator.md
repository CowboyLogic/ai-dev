# About-Me Skill Creator

Generate a private `about-me` skill that tells agents how to work with you: your durable
background, tooling constraints, communication preferences, and autonomy boundaries. The
skill is a **generator**, not a profile template. It runs a short conversational wizard and
writes a personal `about-me/SKILL.md` outside any shared repository.

- **Skill name:** `about-me-skill-creator`
- **Source:** [skills/about-me-skill-creator](https://github.com/CowboyLogic/ai-dev/tree/main/skills/about-me-skill-creator)

---

## What it does

Agents that know nothing about the person running a session fall back to generic defaults
for tone, depth, and how much to do without asking. A short, specific profile loaded at the
start of every session fixes that. This skill interviews you and drafts that profile.

The wizard can create a new profile, refresh an existing one, or draft from material you
provide, such as a CV, bio, README, or existing instructions. It writes the result to a
destination you choose, `~/.claude/skills/about-me` by default. The profile covers working
style, autonomy, background, tooling and environment, current focus, and hard rules.

> [!IMPORTANT]
> The generated profile is personal context. Do not commit it to a shared repository, and
> never include credentials, tokens, or anything you would not want an agent to repeat.

## Where it applies

Use it once to create your profile, and again whenever it goes stale. It works in any
client that loads skills.

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

## Related

- [Lane Topology](../agents/lane-topology.md) — its Conductor loads the `about-me` profile as
  step one of every session

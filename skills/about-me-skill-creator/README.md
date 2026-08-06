# About-Me Skill Creator

Creates a private, personalized `about-me` skill that tells agents how to work with
the person running a session: their durable context, tooling constraints, preferred
communication style, and autonomy boundaries.

This repository skill is a **generator**, not a profile template. The generated skill
is named `about-me` and belongs in a personal global-skills directory, outside any
shared repository.

## Use

Install or invoke `about-me-skill-creator`, then ask it to create or refresh an
about-me profile. It runs a short wizard that:

1. Selects create, refresh, or draft-from-material mode.
2. Collects high-signal personal context in small conversational steps.
3. Drafts and reviews a concise `about-me/SKILL.md`.
4. Asks where to write it, defaulting to `~/.claude/skills/about-me`.

The wizard also offers `~/.agents/skills/about-me` and a custom absolute path. It
resolves the path and asks for confirmation before replacing an existing profile.

## Generated Skill

The creator writes one file:

```text
<selected destination>/SKILL.md
```

For Claude Code, the default result is:

```text
~/.claude/skills/about-me/SKILL.md
```

For OpenCode, select `~/.agents/skills/about-me`, or symlink that location to the
Claude Code copy if both tools should use the same profile.

## Privacy

Your generated profile is personal context. Do not commit it to a shared repository.
It must never include credentials, tokens, secrets, or information you would not want
an agent to repeat aloud.

Include durable preferences and constraints, not facts already owned by a project’s
`AGENTS.md` or temporary task details. Keep it to roughly 40–80 lines. A correction
you have had to give twice is a strong candidate for a new profile entry.

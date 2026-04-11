# OpenCode — Agent Skills

> Source: <https://opencode.ai/docs/skills/>  
> Last updated: April 10, 2026

Agent skills let OpenCode discover reusable instructions from your repo or home directory. Skills are loaded on-demand via the native `skill` tool — agents see available skills and load the full content when needed.

---

## File Locations

Create one folder per skill name with a `SKILL.md` inside. OpenCode searches:

| Scope | Path |
|-------|------|
| Project | `.opencode/skills/<name>/SKILL.md` |
| Global | `~/.config/opencode/skills/<name>/SKILL.md` |
| Project (Claude-compatible) | `.claude/skills/<name>/SKILL.md` |
| Global (Claude-compatible) | `~/.claude/skills/<name>/SKILL.md` |
| Project (agent-compatible) | `.agents/skills/<name>/SKILL.md` |
| Global (agent-compatible) | `~/.agents/skills/<name>/SKILL.md` |

OpenCode walks up from the current directory to the git worktree root, loading matching skills along the way.

---

## SKILL.md Frontmatter

Each `SKILL.md` must start with YAML frontmatter:

```markdown
---
name: git-release
description: Create consistent releases and changelogs
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
  workflow: github
---

## What I do

- Draft release notes from merged PRs
- Propose a version bump
- Provide a copy-pasteable `gh release create` command

## When to use me

Use this when you are preparing a tagged release.
Ask clarifying questions if the target versioning scheme is unclear.
```

### Recognized Frontmatter Fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Must match the directory name |
| `description` | Yes | 1–1024 characters; be specific for correct agent selection |
| `license` | No | |
| `compatibility` | No | |
| `metadata` | No | String-to-string map |

### Name Rules

- 1–64 characters
- Lowercase alphanumeric with single hyphens
- No leading/trailing hyphens, no consecutive `--`
- Must match the directory name
- Pattern: `^[a-z0-9]+(-[a-z0-9]+)*$`

---

## How the Agent Uses Skills

OpenCode lists available skills in the `skill` tool description:

```xml
<available_skills>
  <skill>
    <name>git-release</name>
    <description>Create consistent releases and changelogs</description>
  </skill>
</available_skills>
```

The agent loads a skill by calling:

```
skill({ name: "git-release" })
```

---

## Permissions

Control which skills agents can access:

```jsonc
{
  "permission": {
    "skill": {
      "*": "allow",
      "pr-review": "allow",
      "internal-*": "deny",
      "experimental-*": "ask"
    }
  }
}
```

| Value | Behavior |
|-------|----------|
| `allow` | Skill loads immediately |
| `deny` | Skill hidden from agent, access rejected |
| `ask` | User prompted before loading |

Patterns support wildcards: `internal-*` matches `internal-docs`, `internal-tools`, etc.

### Per-Agent Override

In agent frontmatter:

```yaml
---
permission:
  skill:
    "documents-*": "allow"
---
```

In `opencode.json` for built-in agents:

```jsonc
{
  "agent": {
    "plan": {
      "permission": {
        "skill": {
          "internal-*": "allow"
        }
      }
    }
  }
}
```

### Disable the Skill Tool Entirely

For custom agents (frontmatter):

```yaml
---
tools:
  skill: false
---
```

For built-in agents (`opencode.json`):

```jsonc
{
  "agent": {
    "plan": {
      "tools": {
        "skill": false
      }
    }
  }
}
```

---

## Troubleshooting

If a skill doesn't appear:

- Verify `SKILL.md` is spelled in all caps
- Check frontmatter has `name` and `description`
- Ensure skill names are unique across all locations
- Check permissions — skills with `deny` are hidden from agents

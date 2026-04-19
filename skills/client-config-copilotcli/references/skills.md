# Skills Reference

Skills are Markdown files that give Copilot specialized instructions and resources for specific tasks.

## Storage locations

### Personal (global across projects)
```
~/.copilot/skills/<skill-name>/SKILL.md
~/.agents/skills/<skill-name>/SKILL.md
```

### Project-specific
```
.github/skills/<skill-name>/SKILL.md
.claude/skills/<skill-name>/SKILL.md
.agents/skills/<skill-name>/SKILL.md
```

Each skill lives in its own subdirectory. Directory names must be **lowercase with hyphens** (e.g., `frontend-design`, `api-reviewer`).

---

## SKILL.md structure

```markdown
---
name: my-skill-name
description: What this skill does and when Copilot should use it automatically.
license: MIT
allowed-tools:
  - shell
---

# Skill Title

Instructions, guidelines, context, and examples that Copilot follows when this skill is active.

## Usage examples

Describe when and how to use this skill.

## Steps

1. Step one
2. Step two
```

### Frontmatter fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier — lowercase, hyphens for spaces |
| `description` | Yes | What the skill does; used for automatic activation matching |
| `license` | No | License info (useful for shared/published skills) |
| `allowed-tools` | No | Pre-approves tools (e.g., `shell`) without confirmation prompts — use only for reviewed, trusted skills |

---

## Skill activation

**Automatic**: Copilot loads relevant skills based on your prompt context, matching against the `description` field.

**Manual / forced**: Reference a skill explicitly inside a session:
```
/frontend-design skill    ← force-activates the frontend-design skill
```

---

## CLI management commands (inside sessions)

| Command | Purpose |
|---------|---------|
| `/skills list` | Display all available skills |
| `/skills` | Interactively enable/disable specific skills |
| `/skills info` | View skill details and file location |
| `/skills add` | Add an alternative storage location |
| `/skills reload` | Refresh newly added or modified skills |
| `/skills remove SKILL-DIR` | Delete a custom skill |

---

## Skills vs custom instructions

| | Skills | Custom instructions |
|---|--------|---------------------|
| Best for | Specialized, context-dependent tasks | Broad project guidelines |
| Activation | Automatic or explicit `/skill-name` | Always active |
| Scope | Task-specific detailed guidance | Repository-wide rules |
| Can include scripts | Yes (with `allowed-tools`) | No |

---

## Example: code-review skill

**File**: `~/.copilot/skills/code-review/SKILL.md`

```markdown
---
name: code-review
description: Perform thorough code reviews focusing on security, performance, and readability. Use when the user asks to review, audit, or check code.
---

# Code Review Skill

When reviewing code:

1. Check for security vulnerabilities (injection, auth flaws, exposed secrets)
2. Identify performance bottlenecks
3. Flag readability and maintainability issues
4. Suggest specific improvements with code examples
5. Note what's done well

Format output as:
- **Security**: ...
- **Performance**: ...
- **Readability**: ...
- **Suggestions**: ...
```

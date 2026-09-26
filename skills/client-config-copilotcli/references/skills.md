# Skills Reference

Skills are folders of instructions, scripts, and resources. Copilot injects a skill's `SKILL.md`
when the prompt matches its `description`, or when invoked as `/SKILL-NAME`. All files in the
skill's directory are available to the agent.

## Locations (priority order — first found wins for a duplicate name)

| Location | Scope |
|----------|-------|
| `.github/skills/<name>/SKILL.md` | Project |
| `.agents/skills/<name>/SKILL.md` | Project |
| `.claude/skills/<name>/SKILL.md` | Project (Claude-compatible) |
| Parent directories' `.github/skills/` | Inherited (monorepos) |
| `~/.copilot/skills/<name>/SKILL.md` | Personal |
| `~/.agents/skills/<name>/SKILL.md` | Personal |
| Plugin `skills/` directories | Plugin |
| `COPILOT_SKILLS_DIRS` (comma-separated) and the `skillDirectories` setting | Custom |
| `.github/skills/` under `--add-dir` / `/add-dir` directories | Added root (trusted like project skills) |
| Bundled with the CLI | Built-in (lowest) |
| Org/enterprise remote skills | Remote (fetched on invocation) |

`~/.claude/skills/` is not a documented location — only the project-level `.claude/skills/` is.
Skill directory names should be lowercase with hyphens. Two plugins with the same skill name
coexist as `/plugin-a/search` and `/plugin-b/search`.

**Commands** (alternative format): individual `.md` files in `.claude/commands/`; the filename is
the command name; they support `argument-hint`, `description`, `allowed-tools`, and
`disable-model-invocation`. Skills beat commands with the same name.

---

## SKILL.md

```markdown
---
name: image-convert
description: Converts SVG images to PNG. Use when asked to convert SVG files.
allowed-tools: shell
---

When asked to convert an SVG to PNG, run `convert-svg-to-png.sh` from this skill's base
directory, passing the input SVG path as the first argument.
```

### Frontmatter fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Letters, numbers, hyphens; max 64 chars; usually matches the directory |
| `description` | string | Yes | What it does and when to use it; max 1024 chars; drives auto-activation |
| `license` | string | No | License text or identifier |
| `argument-hint` | string | No | Hint shown in the skill picker, e.g. `"[target] [mode]"` |
| `allowed-tools` | string or string[] | No | Tools auto-allowed while the skill is active (comma list or YAML array; `"*"` for all) |
| `user-invocable` | boolean | No | Allow `/SKILL-NAME` (default `true`) |
| `disable-model-invocation` | boolean | No | Prevent automatic invocation (default `false`) |

> [!WARNING]
> Only pre-approve `shell` or `bash` in `allowed-tools` for skills (and scripts) you have reviewed
> and trust. It removes the confirmation step for terminal commands.

---

## Using skills

- Automatic: Copilot matches the prompt against `description`.
- Explicit: `Use the /frontend-design skill to ...` or just `/frontend-design`.
- Disable without deleting: `disabledSkills` setting (user or repo), `/skills` toggle, or
  `copilot skill disable NAME`.
- `dynamicRetrieval: { "skills": false }` turns off embeddings-based retrieval for skills.

## Management

### In a session

| Command | Purpose |
|---------|---------|
| `/skills` | Plugins dashboard on the Skills tab (enable/disable) |
| `/skills list` | List available skills |
| `/skills info NAME` | Details, including file location and source plugin |
| `/skills add [--project] <FILE\|URL\|DIRECTORY>` | Add a skill; `--project` scopes a file/URL install to this repo |
| `/skills remove <NAME\|DIRECTORY>` | Remove a skill, or unregister a custom directory |
| `/skills reload` | Reload without restarting |

### In the terminal

```bash
copilot skill list [--json]                  # rows: { name, description, source, path, enabled }
copilot skill add ./my-skill/SKILL.md        # personal (default)
copilot skill add --project ./my-skill/SKILL.md   # into .github/skills (file or URL only)
copilot skill enable my-skill
copilot skill disable my-skill
copilot skill remove my-skill
```

- Adding a **directory** registers it as a custom skill source (no copy). Adding a **file or URL**
  copies it into the personal or project skills directory.
- Only personal/project skills you added can be removed; plugin and built-in skills can only be
  disabled.
- `gh skill` (GitHub CLI) can also search, install, update, and publish skills.
- The retired `copilot plugins install --skill` / `--skill` flags are replaced by `copilot skill`.

---

## Skills vs custom instructions

| | Skills | Custom instructions |
|---|--------|---------------------|
| Best for | Detailed, task-specific guidance | Rules relevant to almost every task |
| Loaded | When relevant, or `/skill-name` | Always |
| Can bundle scripts | Yes | No |

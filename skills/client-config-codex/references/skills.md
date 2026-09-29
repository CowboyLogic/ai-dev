# Skills Reference

A skill is a directory with a `SKILL.md` plus optional scripts and references. Codex starts with
each skill's name, description, and file path, then loads the full `SKILL.md` only when it decides
to use the skill (progressive disclosure). Skills follow the open agent skills standard
(<https://agentskills.io>). Standalone skills work in Codex CLI and the IDE extension; skills
bundled in plugins reach more surfaces.

## Layout

```text
my-skill/
├── SKILL.md            # required: instructions + metadata
├── scripts/            # optional: executable code
├── references/         # optional: documentation
├── assets/             # optional: templates, resources
└── agents/
    └── openai.yaml     # optional: UI metadata, invocation policy, dependencies
```

## SKILL.md

```markdown
---
name: skill-name
description: Explain exactly when this skill should and should not trigger.
---

Skill instructions for Codex to follow.
```

- `name` and `description` are the only documented required frontmatter fields. The docs describe
  no others (no `allowed-tools`, no invocation toggles). Invocation policy lives in
  `agents/openai.yaml`.
- Implicit matching depends on `description`. Keep it concise, state scope and boundaries, and
  front-load the key use case and trigger words so it survives shortening.
- Keep each skill focused on one job. Prefer instructions over scripts unless you need
  deterministic behavior. Write imperative steps with explicit inputs and outputs.
- Codex detects skill changes automatically. If an update does not appear, restart Codex.

### Catalog budget

The initial skills list is capped at 2% of the model's context window (8,000 characters when the
window is unknown). Codex shortens descriptions first, then may omit skills and show a warning.
Set `[skills] max_context_tokens` in `config.toml` to change the token budget (positive integer,
capped at `10000`). This applies only to the initial list. A selected skill still loads in full.

## Where Codex loads skills

Codex reads repository, user, admin, and system locations. For repositories it scans
`.agents/skills` in **every directory from the current working directory up to the repository
root**.

| Scope | Location |
|-------|----------|
| `REPO` | `$CWD/.agents/skills` |
| `REPO` | `$CWD/../.agents/skills` (a folder above CWD, inside a Git repo) |
| `REPO` | `$REPO_ROOT/.agents/skills` (topmost repo folder; root skills for every subfolder) |
| `USER` | `$HOME/.agents/skills` |
| `ADMIN` | `/etc/codex/skills` |
| `SYSTEM` | Bundled with Codex (for example `skill-creator` and plan skills) |

- Same-`name` skills are **not merged**. Both can appear in skill selectors. The docs state no
  precedence order, so avoid duplicate names across scopes.
- Symlinked skill folders are supported. Codex follows the link target when scanning.
- Plugins can also carry skills. See [agents-plugins.md](agents-plugins.md).

> [!NOTE]
> The docs do not list `$CODEX_HOME/skills` (`~/.codex/skills`) as a scan location. On 0.158.0 it
> exists and holds the bundled system skills under `.system/` (`imagegen`, `openai-docs`,
> `plugin-creator`, `review-agent`, `skill-creator`, `skill-installer`), and the bundled
> `$skill-installer` installs into `$CODEX_HOME/skills`. Put your own skills in `~/.agents/skills`
> or a repo's `.agents/skills`, which the docs do document.

## Invoking skills

- **Explicit:** run `/skills` in the CLI (or IDE) to pick one, or type `$` to mention a skill by
  name (`$skill-creator`). `/skills` inserts the selected skill's context so the next request
  follows it.
- **Implicit:** Codex chooses a skill when the task matches its `description`.
- To stop implicit use of one skill, set `allow_implicit_invocation: false` in its
  `agents/openai.yaml`. Explicit `$skill` still works.

## Optional metadata: `agents/openai.yaml`

Sets UI metadata for the ChatGPT desktop app, invocation policy, and tool dependencies.

```yaml
interface:
  display_name: "Optional user-facing name"
  short_description: "Optional user-facing description"
  icon_small: "./assets/small-logo.svg"
  icon_large: "./assets/large-logo.png"
  brand_color: "#3B82F6"
  default_prompt: "Optional surrounding prompt to use the skill with"

policy:
  allow_implicit_invocation: false   # default true

dependencies:
  tools:
    - type: "mcp"
      value: "openaiDeveloperDocs"
      description: "OpenAI Docs MCP server"
      transport: "streamable_http"
      url: "https://developers.openai.com/mcp"
```

## Enable or disable a skill

Disable without deleting by adding an entry to `~/.codex/config.toml`, then restart Codex:

```toml
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```

> [!NOTE]
> The docs disagree on `path`: the skills guide and sample config use the `SKILL.md` file path, the
> config reference says "path to a skill folder containing `SKILL.md`". Use the `SKILL.md` path as
> shown. It could not be verified locally (no `[[skills.config]]` entry exists on this machine).

Custom agent files can also carry `skills.config` disables. See
[agents-plugins.md](agents-plugins.md).

## Install and create

- **Curated skills:** `$skill-installer <name>` (for example `$skill-installer linear`). You can
  prompt it to download skills from other repositories. Codex detects new skills automatically;
  restart if one does not appear. Curated sources: <https://github.com/openai/skills>.
- **Create:** `$skill-creator` asks what the skill does, when it triggers, and whether it stays
  instruction-only (the default) or includes scripts. Or hand-write `SKILL.md`.
- **Distribute:** for anything reusable beyond one repo, or two or more skills together, or a
  skill plus a connector, package a plugin instead. Direct skill folders are for local authoring
  and repo-scoped workflows.
- **Check:** confirm the skill appears in `/skills`, and test prompts against the `description`
  to confirm the right trigger behavior.

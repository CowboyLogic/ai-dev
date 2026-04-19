---
name: agent-creator-opencode
description: Guide for creating custom agents for the OpenCode CLI. Use this skill whenever a user wants to build, configure, or modify an OpenCode agent — including writing agent Markdown files, configuring agents in opencode.json, setting up permissions, designing primary/subagent workflows, or structuring multi-agent orchestration patterns. ALWAYS load this skill before working on OpenCode agent files.
---

# OpenCode Agent Creator

Custom agents for the OpenCode CLI let you build focused AI assistants with specific prompts, models, tool permissions, and delegation patterns. Agents are defined either as Markdown files or as entries in `opencode.json`.

> **Official docs:** https://opencode.ai/docs/agents/

---

## Quick Decision Guide

| Goal | Approach |
|---|---|
| User-selectable, always-available agent | **Primary agent** (`mode: primary`) |
| Specialist invoked via delegation or `@mention` | **Subagent** (`mode: subagent`) |
| Works as both primary and subagent | `mode: all` (default when `mode` is omitted) |
| Internal helper hidden from `@` autocomplete | Subagent + `hidden: true` |
| Shared across all projects | Markdown in `~/.config/opencode/agents/` |
| Scoped to one project | Markdown in `.opencode/agents/` |
| Customizing a built-in agent | JSON in `opencode.json` under `agent.<name>` |
| Just want a quick scaffold | Run `opencode agent create` in the terminal |

---

## Format Choice

### Markdown (preferred for new agents)

Place in `.opencode/agents/<name>.md` (project) or `~/.config/opencode/agents/<name>.md` (global). The file name becomes the agent name.

```markdown
---
description: Reviews code for quality and best practices
mode: subagent
model: anthropic/claude-sonnet-4-20250514
temperature: 0.1
permission:
  edit: deny
  bash: deny
  webfetch: deny
---

You are a code reviewer. Focus on:

- Security vulnerabilities
- Performance issues
- Code clarity and maintainability

Provide specific, actionable feedback. Do not make changes.
```

### JSON (for built-in customization or shared configs)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "agent": {
    "code-reviewer": {
      "description": "Reviews code for best practices and potential issues",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-20250514",
      "prompt": "You are a code reviewer. Focus on security, performance, and maintainability.",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      }
    }
  }
}
```

---

## File Locations

| Scope | Location |
|---|---|
| Project (Markdown) | `.opencode/agents/<name>.md` |
| Global (Markdown) | `~/.config/opencode/agents/<name>.md` |
| Project (JSON) | `opencode.json` → `agent.<name>` |
| Global (JSON) | `~/.config/opencode/opencode.json` → `agent.<name>` |

Project-level agents override global agents with the same name. Markdown file names must be lowercase with hyphens (e.g., `code-reviewer.md` → `@code-reviewer`).

---

## Minimal Working Examples

### Read-only analyst (subagent)

```markdown
---
description: Analyzes code architecture and explains design patterns without making changes
mode: subagent
permission:
  edit: deny
  bash: deny
  webfetch: allow
---

You are an architecture analyst. Explain what the code does, why it is structured this way, and what trade-offs it makes. Never modify files.
```

### Orchestrator (primary agent)

```markdown
---
description: Coordinates multi-step workflows by delegating to specialized subagents
mode: primary
model: anthropic/claude-sonnet-4-20250514
temperature: 0.2
permission:
  bash:
    "*": ask
    "git status": allow
    "git log*": allow
---

You are a project coordinator. Break complex tasks into subtasks and delegate them to appropriate subagents using the Task tool. Always review subagent output before proceeding to the next step.
```

### Hidden internal helper

```markdown
---
description: Validates test coverage. Internal use only — invoked by orchestrator agents.
mode: subagent
hidden: true
permission:
  edit: deny
  bash:
    "pytest*": allow
    "*": deny
---

You are a test coverage validator. Run the test suite and report which files lack adequate coverage. Do not modify code.
```

---

## Permission Model

Permissions control what each agent can do. Use `permission` (the `tools` boolean map is deprecated as of v1.1.1).

```yaml
permission:
  edit: deny           # file editing: allow | ask | deny
  bash: ask            # shell commands: allow | ask | deny | per-command map
  webfetch: allow      # web requests: allow | ask | deny
```

**Per-command bash control** — rules are evaluated in order; last match wins:

```yaml
permission:
  bash:
    "*": ask             # default: ask for everything
    "git status": allow  # exact match
    "git log*": allow    # glob pattern
    "git push*": deny    # always block
    "rm -rf*": deny
```

Put the catch-all `"*"` first, then specific overrides after.

**Task permissions** — control which subagents this agent can invoke:

```yaml
permission:
  task:
    "*": deny
    "reviewer": allow
    "security-*": ask
```

**All available permission keys:**

| Key | What it controls |
|---|---|
| `read` | File reads (matches file path) |
| `edit` | All file writes/edits/patches |
| `glob` | File globbing (matches glob pattern) |
| `grep` | Content search (matches regex) |
| `bash` | Shell commands (matches command string) |
| `webfetch` | URL fetching (matches URL) |
| `task` | Subagent invocation (matches subagent name) |
| `skill` | Skill loading (matches skill name) |
| `external_directory` | Access to paths outside project root |
| `doom_loop` | Repeated identical tool calls |

Default behavior: most permissions are `allow`. `doom_loop` and `external_directory` default to `ask`. `.env` files are denied by default.

---

## Built-in Agents (Do Not Recreate)

These ship with OpenCode. Override them in `opencode.json` if you need different behavior — do not recreate them from scratch.

| Agent | Mode | Purpose |
|---|---|---|
| `build` | primary | Default — all tools enabled |
| `plan` | primary | Read-only analysis — edit/bash default to `ask` |
| `general` | subagent | Full-access general-purpose subagent |
| `explore` | subagent | Read-only, fast codebase exploration |

Hidden system agents (do not override): `compaction`, `title`, `summary`.

---

## Creating an Agent: Step-by-Step

### Step 1 — Decide mode and scope

- **Primary**: user selects it with Tab or switches to it explicitly
- **Subagent**: invoked by primary agents via Task tool or by user via `@mention`
- Scope: project (`.opencode/agents/`) for repo-specific, global (`~/.config/opencode/agents/`) for personal tools

### Step 2 — Write the prompt

- Open with one sentence stating the agent's role
- List what the agent does and what it does NOT do
- Be specific about output format and behavior constraints
- Aim for under 2000 tokens

### Step 3 — Configure permissions

- Start restrictive: `edit: deny`, `bash: deny`
- Grant only what the role requires
- Use per-command bash rules for surgical control (pattern-match the command + args)

### Step 4 — Choose the model

- Format: `provider/model-id` (e.g., `anthropic/claude-sonnet-4-20250514`, `openai/gpt-4o`)
- Omit to inherit: subagents inherit from their invoking primary agent; primary agents use the global config
- Use lighter models for planning/analysis; stronger models for code generation

### Step 5 — Create the file

- Markdown: `.opencode/agents/<kebab-case-name>.md`
- Invoke manually: `@agent-name` in the chat
- Let primary agents discover and invoke subagents automatically based on their `description`

### Step 6 — Test it

```bash
# Scaffold with interactive prompts
opencode agent create

# Then test manually in the TUI
@my-agent-name do something specific
```

---

## Prompt Writing Tips

- **Role first**: "You are a database migration specialist."
- **Explicit negatives**: "Do not create files. Do not run migrations automatically."
- **Output format**: Describe what a good response looks like
- **Context injection**: Use `{file:./path/to/prompt.txt}` to load an external prompt file
- **Scope creep prevention**: State the agent's boundaries — what is out-of-scope

---

## Model ID Format

```
provider/model-id
```

Examples:
- `anthropic/claude-sonnet-4-20250514`
- `anthropic/claude-haiku-4-20250514`
- `openai/gpt-4o`
- `openai/gpt-5`
- `opencode/gpt-5.1-codex` (OpenCode Zen)

Run `opencode models` to list all available model IDs for your configured providers.

---

## Temperature Guide

| Range | Behavior | Good for |
|---|---|---|
| `0.0–0.2` | Focused, deterministic | Code analysis, security review, planning |
| `0.3–0.5` | Balanced | General development tasks |
| `0.6–1.0` | Creative, varied | Brainstorming, documentation, exploration |

---

> For the complete property reference (all YAML/JSON keys, types, defaults, and edge cases), load `references/agent-reference.md`.

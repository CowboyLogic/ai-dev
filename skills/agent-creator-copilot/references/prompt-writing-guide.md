# Prompt Writing Guide — Custom Agent Profiles

Load this file when writing or reviewing the Markdown body of an agent profile.

---

## What the Prompt Body Does

The Markdown body of an agent profile holds the agent's instructions. In VS Code it is prepended to the user's chat prompt when the agent is selected, and on GitHub.com and in Copilot CLI it is the agent's prompt when the agent is selected or run as a subagent. It defines the agent's persona, scope, and behavioral rules. Write it as if briefing a skilled teammate who needs to know exactly what to do and what to stay out of.

**Limit: 30,000 characters.** Stay well under it — long prompts degrade response quality.

---

## Effective Prompt Structure

```markdown
# Agent Name

You are a [role] focused on [domain]. Your scope is limited to [specific boundaries].

## Responsibilities

- [Concrete responsibility 1]
- [Concrete responsibility 2]
- [What to hand off, not handle directly]

## Constraints

- Do not modify [out-of-scope files/systems]
- Always [required behavior]
- When [situation], [action]

## Output Format

- [Expected format, level of detail, or structure for responses]
```

---

## Prompt Writing Principles

1. **State scope explicitly.** Define what the agent does AND what it does not do. Ambiguity leads to scope creep.
2. **Use imperative language.** "Review the code for..." not "You can review code..." Directives are clearer than permissions.
3. **Define handoff conditions.** When should the agent stop and hand off vs. proceed? Name the next agent explicitly. `handoffs` buttons only exist in VS Code / IDEs, so on GitHub.com state escalation in the response.
4. **Keep it grounded.** Reference tools, file paths, and conventions specific to the project — generic prompts produce generic results.
5. **Use headings** for complex agents to organize behavior by category (Responsibilities, Constraints, Output Format).
6. **Prefer negation for boundaries.** "Do not modify files outside `src/`" is more reliable than listing what is allowed.

---

## Write the `description` for Inference

GitHub.com and Copilot CLI choose custom agents by matching the task against `description`. State what the agent is expert in **and when it should be used**, including trigger words if you want them ("Use when a security review is requested"). A vague description means the agent is never inferred, and an over-broad one means it gets picked for unrelated work.

---

## What NOT to Include in the Prompt

| Anti-pattern | Why | Alternative |
|---|---|---|
| Exhaustive API reference material | Inflates prompt without adding precision | Load a skill (`SKILL.md`) at session start |
| Code examples as reference | Takes up character budget with low value | Reference a `references/` file instead |
| Baseline behaviors (tone, format, safety) | Belongs in `copilot-instructions.md` / `AGENTS.md`, not per-agent | Use the repo-level instructions file. In Copilot CLI, a custom agent run as a subagent only reads it with `include-custom-instructions: true` |
| Step-by-step instructions for well-known tasks | The model already knows — repetition wastes budget | Describe the outcome, not each micro-step |
| Version-specific facts that change frequently | Will become stale | Fetch live data (`#tool:web/fetch` in VS Code; the `web` alias doesn't apply on the cloud agent) |

---

## Examples

See the `references/` folder for full agent profile examples:

- `workspace-agent-example.agent.md` — Full-featured agent with tools, handoffs, and structured prompt
- `user-profile-agent-example.agent.md` — Minimal personal agent
- `cloud-agent-with-mcp-example.agent.md` — Cloud agent with MCP config and metadata

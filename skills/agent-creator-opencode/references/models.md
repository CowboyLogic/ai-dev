# OpenCode Agent Model ID Reference

Model ID format and common provider values for OpenCode agents.

**Sources:**

- https://docs.github.com/en/copilot/reference/ai-models/supported-models
- https://docs.github.com/en/copilot/reference/ai-models/model-comparison
- https://opencode.ai/docs/agents/

Load this file when choosing or validating a `model` value. For the `model`
property behavior and inheritance rules, load `properties.md`.

---

## Format

```text
provider/model-id
```

Run `opencode models` to list all model IDs for your configured providers.
Availability depends on your Copilot plan, org model policy, and provider auth.

---

## GitHub Copilot models

Auth via GitHub OAuth — use `/connect` inside opencode to authenticate. No API
key required. OpenCode IDs use the `github-copilot/` provider prefix.

> [!NOTE]
> Model availability changes over time. The table below reflects GitHub's
> supported AI models docs plus IDs currently returned by `opencode models` for
> the GitHub Copilot provider. Always re-check with `opencode models` before
> hard-coding a model on an agent.

| Model ID | Display name | Release | Best for |
|---|---|---|---|
| `github-copilot/gpt-5-mini` | GPT-5 mini | GA | Fast, cheap subagents; completions and explanations |
| `github-copilot/gpt-5.3-codex` | GPT-5.3-Codex | GA | Agentic software development and code-focused agents |
| `github-copilot/gpt-5.4` | GPT-5.4 | GA | Deep reasoning, debugging, architecture-level analysis |
| `github-copilot/gpt-5.4-mini` | GPT-5.4 mini | GA | Fast subagents; codebase exploration |
| `github-copilot/gpt-5.4-nano` | GPT-5.4 nano | GA | High-volume lightweight subagents |
| `github-copilot/gpt-5.5` | GPT-5.5 | GA | Deep reasoning and multi-step problem solving |
| `github-copilot/gpt-5.6-luna` | GPT-5.6 Luna | GA | Quick, cost-efficient simple or repetitive tasks |
| `github-copilot/gpt-5.6-sol` | GPT-5.6 Sol | GA | Complex reasoning over large codebases; long agentic work |
| `github-copilot/gpt-5.6-terra` | GPT-5.6 Terra | GA | Balanced everyday interactive and agentic coding |
| `github-copilot/claude-haiku-4.5` | Claude Haiku 4.5 | GA | Fast, cheap analysis and lightweight subagents |
| `github-copilot/claude-opus-4.5` | Claude Opus 4.5 | GA | Heavyweight analysis and complex reasoning |
| `github-copilot/claude-opus-4.6` | Claude Opus 4.6 | GA | Heavyweight analysis and complex reasoning |
| `github-copilot/claude-opus-4.7` | Claude Opus 4.7 | GA | Highest-quality reasoning and architecture agents |
| `github-copilot/claude-opus-4.8` | Claude Opus 4.8 | GA | Highest-quality reasoning and architecture agents |
| `github-copilot/claude-opus-5` | Claude Opus 5 | GA | Highest-quality reasoning and architecture agents |
| `github-copilot/claude-sonnet-4.5` | Claude Sonnet 4.5 | GA | General-purpose coding and agent tasks |
| `github-copilot/claude-sonnet-4.6` | Claude Sonnet 4.6 | GA | Orchestrators, complex code generation |
| `github-copilot/claude-sonnet-5` | Claude Sonnet 5 | GA | Orchestrators, general coding and agent tasks |
| `github-copilot/gemini-3.1-pro-preview` | Gemini 3.1 Pro | Public preview | Architecture, design, edit-then-test loops |
| `github-copilot/gemini-3.5-flash` | Gemini 3.5 Flash | GA | Fast, cheap analysis subagents |
| `github-copilot/gemini-3.6-flash` | Gemini 3.6 Flash | GA | Fast, cheap analysis subagents |
| `github-copilot/mai-code-1-flash-picker` | MAI-Code-1-Flash | GA | Fast code completions and explanations |
| `github-copilot/kimi-k2.7-code` | Kimi K2.7 Code | GA | Code-focused agents |
| `github-copilot/grok-4.5` | Grok 4.5 | GA | General-purpose coding and agent tasks |

### Extreme-cost models — do not auto-select

> [!CAUTION]
> **NEVER automatically use these models.** They are intentionally **omitted**
> from the recommended tables above.
>
> | Model ID | Display name | Why gated |
> |---|---|---|
> | `github-copilot/claude-opus-4.7-fast` | Claude Opus 4.7 (fast mode) | Extreme cost vs standard Opus |
> | `github-copilot/claude-opus-4.8-fast` | Claude Opus 4.8 (fast mode) | Extreme cost vs standard Opus |
> | `github-copilot/claude-fable-5` | Claude Fable 5 | Extreme cost; long-horizon premium model (org enablement may also be required) |
> | Any future `*-opus-*-fast` / “Opus (fast mode)” ID | — | Same fast-mode cost class |
> | Any future `claude-fable-*` ID | — | Same Fable cost class |
>
> Rules for this skill:
>
> 1. **Never** pick Opus fast-mode or Fable by default, as a “performance” or
>    “strongest model” upgrade, or because it appears in `opencode models`.
> 2. **Never** write an agent config that uses one of these `model` values unless
>    the user has **explicitly named that model** and **confirmed they accept
>    the extreme cost**.
> 3. If the user asks for “faster Opus,” “Opus fast,” “Fable,” or similar without
>    clear cost acceptance, **stop and require confirmation** before proceeding.
>    Explain that these are premium cost multipliers, not free upgrades.
> 4. Prefer standard Opus IDs (`claude-opus-4.7`, `claude-opus-4.8`,
>    `claude-opus-5`) or a Sonnet / GPT alternative unless the user opts in.
>
> Required confirmation (user must clearly accept cost) before any use:
>
> - They want that **specific** model ID (fast-mode or Fable — not a vague “best”)
> - They understand it can incur **extreme cost** vs standard alternatives
> - They still want that ID written into the agent config

### Also in GitHub docs / OpenCode catalog

These appear in GitHub's supported-models list or OpenCode's provider catalog,
but may not show for every account in `opencode models` (plan, policy, or
retirement):

| Model ID | Display name | Notes |
|---|---|---|
| `github-copilot/claude-sonnet-4` | Claude Sonnet 4 | Older Sonnet; still in OpenCode catalog |
| `github-copilot/gemini-2.5-pro` | Gemini 2.5 Pro | Older Gemini Pro; still in OpenCode catalog |
| `github-copilot/gemini-3-flash-preview` | Gemini 3 Flash Preview | Superseded by Gemini 3.5/3.6 Flash in many accounts |
| `github-copilot/gpt-4.1` | GPT-4.1 | Older GPT; still in OpenCode catalog |
| `github-copilot/gpt-5.2` | GPT-5.2 | Older GPT-5.x; still in OpenCode catalog |
| `github-copilot/gpt-5.2-codex` | GPT-5.2 Codex | Older Codex; prefer `gpt-5.3-codex` |
| Raptor mini | Raptor mini | Listed by GitHub (fine-tuned GPT-5 mini); confirm ID via `opencode models` |

### Recommended picks by agent role

| Agent role | Good starting models |
|---|---|
| Orchestrator / primary | `claude-sonnet-5`, `claude-sonnet-4.6`, `gpt-5.6-terra` |
| Complex reasoning / architecture | `claude-opus-5`, `claude-opus-4.8`, `gpt-5.6-sol` |
| Code generation / agentic coding | `gpt-5.3-codex`, `claude-sonnet-5` |
| Fast / cheap subagent | `claude-haiku-4.5`, `gpt-5.6-luna`, `gemini-3.6-flash` |
| Read-only review / analysis | `gpt-5.6-terra`, `claude-sonnet-4.6`, `gemini-3.1-pro-preview` |

---

## Other common providers

| Provider | Example model IDs |
|---|---|
| Anthropic | `anthropic/claude-sonnet-4-20250514` |
| Anthropic | `anthropic/claude-haiku-4-20250514` |
| OpenAI | `openai/gpt-4o` |
| OpenAI | `openai/gpt-5` |
| OpenCode Zen | `opencode/gpt-5.1-codex` |

---

## When to specify model per-agent

**Default for this skill: always set `model` on new agents** unless the user
explicitly says to omit it and inherit. Be intentional — choose a model that
fits the agent's role rather than relying on ambient defaults.

- Different capability tiers for different roles — match the role table above (for example: haiku/luna/flash for cheap subagents, codex/sonnet for coding, terra/sonnet for orchestrators, opus/sol for deep reasoning)
- Specific provider features (reasoning effort, extended context)
- Subagents that should keep a fixed model regardless of which primary invokes them

---

## Inheritance defaults

Inheritance applies only when `model` is omitted (and only when the user asked
for that):

- **Primary agents:** use the globally configured model when `model` is omitted
- **Subagents:** inherit the model from the primary agent that invoked them when `model` is omitted

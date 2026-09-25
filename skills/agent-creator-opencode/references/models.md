# OpenCode Agent Model ID Reference

Model ID format, variants, and common provider values for OpenCode agents. Applies
to both V1 and V2; syntax differences are called out.

**Sources (checked 2026-09-24):**

- <https://docs.github.com/en/copilot/reference/ai-models/supported-models>
- <https://docs.github.com/en/copilot/reference/ai-models/model-comparison>
- <https://models.dev/api.json> (the catalog OpenCode uses)
- <https://opencode.ai/docs/models/> (V1) · <https://opencode.ai/v2/docs/models/> (V2)

Load this file when choosing or validating a `model` value. For the `model`
property behavior and inheritance rules, load `v2/agents.md` or
`v1/properties.md`.

---

## Format

| Version | Agent `model` syntax | Variant |
|---|---|---|
| V1 | `provider/model-id` | Separate `variant: high` field |
| V2 | `provider/model-id#variant` | Joined after `#`; no separate field |

- The provider ends at the first `/`. The model ID may contain further `/`
  (for example `openrouter/anthropic/claude-sonnet-4.5`). IDs are case-sensitive.
- V2 JSON also accepts `{ "providerID": "...", "model": "...", "variant": "..." }`.
- List IDs with `opencode models` (V1 CLI) or `/models` inside a session (V1 and
  V2). Availability depends on plan, org model policy, and provider auth.

## Variants

Variants are named per-model option sets, often reasoning effort.

- V1 built-in examples: Anthropic `high` (default) and `max`; OpenAI roughly
  `none`, `minimal`, `low`, `medium`, `high`, `xhigh` (varies by model); Google
  `low` and `high`. Not every model has every variant.
- V2: variant names come from the model's catalog metadata; an **unknown variant
  is a model-resolution error**. Confirm it exists before writing `#variant`.
- Custom variants:
  - V1: an object under `provider.<id>.models.<model>.variants`, keyed by name.
  - V2: an array under `providers.<id>.models.<model>.variants`, each entry with
    `id` and any of `settings`, `headers`, `body`. Applied after provider and
    model values.

```jsonc
// V2: define a variant, then use model: "openai/gpt-5.2#deep" on an agent
{
  "providers": {
    "openai": {
      "models": {
        "gpt-5.2": {
          "variants": [
            { "id": "deep", "settings": { "reasoningEffort": "high" } }
          ]
        }
      }
    }
  }
}
```

> [!NOTE]
> In V2, per-agent `request.body` (where `temperature` now lives) is preserved but
> not yet sent. A variant is the documented way to change request settings per
> agent today. Whether a given option such as `temperature` belongs in a variant's
> `settings` or `body` depends on the provider package; the V2 docs do not give a
> temperature example.

---

## GitHub Copilot models

Auth via GitHub OAuth: use `/connect` inside OpenCode. No API key required.
OpenCode IDs use the `github-copilot/` provider prefix.

> [!NOTE]
> The table lists models on GitHub's supported-models page whose IDs also appear
> under `github-copilot` in the models.dev catalog (2026-09-24). Model
> availability changes often. Re-check with `/models` or `opencode models`
> before hard-coding a model on an agent.

| Model ID | Display name | Best for (GitHub model comparison) |
|---|---|---|
| `github-copilot/gpt-5-mini` | GPT-5 mini | Fast, cheap subagents; completions and explanations |
| `github-copilot/gpt-5.3-codex` | GPT-5.3-Codex | Agentic software development; GitHub's LTS fallback model |
| `github-copilot/gpt-5.4` | GPT-5.4 | Deep reasoning, debugging, architecture-level analysis |
| `github-copilot/gpt-5.4-mini` | GPT-5.4 mini | Codebase exploration with grep-style tools |
| `github-copilot/gpt-5.4-nano` | GPT-5.4 nano | GitHub lists it for the Codex VS Code extension only (Pro+); may not appear |
| `github-copilot/gpt-5.5` | GPT-5.5 | Deep reasoning and multi-step problem solving |
| `github-copilot/gpt-5.6-luna` | GPT-5.6 Luna | Quick, cost-efficient simple or repetitive tasks |
| `github-copilot/gpt-5.6-sol` | GPT-5.6 Sol | Complex reasoning over large codebases; long agentic work |
| `github-copilot/gpt-5.6-terra` | GPT-5.6 Terra | Balanced everyday interactive and agentic coding |
| `github-copilot/gpt-6-luna` | GPT-6 Luna | Quick, cost-efficient smaller tasks |
| `github-copilot/gpt-6-sol` | GPT-6 Sol | Development tasks that need careful multistep validation |
| `github-copilot/claude-haiku-4.5` | Claude Haiku 4.5 | Fast, cheap analysis and lightweight subagents |
| `github-copilot/claude-opus-4.8` | Claude Opus 4.8 | Deep reasoning and debugging |
| `github-copilot/claude-opus-5` | Claude Opus 5 | Deep reasoning and debugging |
| `github-copilot/claude-opus-5.5` | Claude Opus 5.5 | Long-running agentic coding and knowledge work |
| `github-copilot/claude-sonnet-5` | Claude Sonnet 5 | Orchestrators, general coding and agent tasks |
| `github-copilot/gemini-3.7-flash` | Gemini 3.7 Flash | Fast, cheap analysis subagents |
| `github-copilot/gemini-3.8-flash` | Gemini 3.8 Flash | Fast, cheap analysis subagents |
| `github-copilot/mai-code-1.1-flash` | MAI-Code-1.1-Flash | Fast code completions, explanations, tool use |
| `github-copilot/kimi-k3` | Kimi K3 | Agentic coding and long-context work (open-weight; disabled by default for Business/Enterprise) |
| `github-copilot/grok-4.5` | Grok 4.5 | General-purpose coding and agent tasks |
| `github-copilot/grok-4.6` | Grok 4.6 | General-purpose coding and agent tasks |
| `github-copilot/grok-4.7` | Grok 4.7 | Agentic coding and complex multistep workflows |

### Retiring or retired — avoid for new agents

| Model ID | Status on GitHub (2026-09-24) | Suggested replacement |
|---|---|---|
| `github-copilot/claude-opus-4.7` | Retires 2026-10-02 | `claude-opus-5` |
| `github-copilot/gemini-3.5-flash` | Retires 2026-10-02 | `gemini-3.8-flash` |
| `github-copilot/gemini-3.6-flash` | Retires 2026-10-02 | `gemini-3.8-flash` |
| `github-copilot/kimi-k2.7-code` | Retires 2026-10-02 | `kimi-k3` |
| `github-copilot/claude-sonnet-4.6` | Retired 2026-09-01 except annual Pro/Pro+ subscribers | `claude-sonnet-5` |
| `github-copilot/mai-code-1-flash-picker` | MAI-Code-1-Flash retired 2026-09-10 | `mai-code-1.1-flash` |
| `claude-opus-4.5`, `claude-opus-4.6`, `claude-sonnet-4.5`, `gemini-3.1-pro-preview` | Retired 2026-09-01 | `claude-opus-5`, `claude-sonnet-5`, `gemini-3.6-flash` |
| `gpt-4.1`, `gpt-5.2`, `gpt-5.2-codex`, `claude-sonnet-4`, `gemini-2.5-pro`, Raptor mini | Retired | See GitHub's retirement table |

### Extreme-cost models — do not auto-select

> [!CAUTION]
> **NEVER automatically use these models.** They are intentionally **omitted**
> from the recommended tables above.
>
> | Model | Why gated |
> |---|---|
> | Claude Opus 4.8 (fast mode) (preview) | Fast-mode cost class. Not in the models.dev `github-copilot` catalog; confirm the exact ID with `/models`. |
> | `github-copilot/claude-fable-5` | Extreme cost; not under GitHub's ZDR agreement; org enablement required |
> | `github-copilot/claude-fable-5.1` | Same as Fable 5 |
> | `github-copilot/gpt-6-astra` | Priced at the Fable level in models.dev ($10/$50 per M tokens, higher above 272K context) |
> | Any future `*-opus-*-fast` / "Opus (fast mode)" ID | Same fast-mode cost class |
> | Any future `claude-fable-*` ID | Same Fable cost class |
>
> Rules for this skill:
>
> 1. **Never** pick a gated model by default, as a "performance" or "strongest
>    model" upgrade, or because it appears in the model list.
> 2. **Never** write an agent config that uses one of these `model` values unless
>    the user has **explicitly named that model** and **confirmed they accept
>    the extreme cost**.
> 3. If the user asks for "faster Opus," "Opus fast," "Fable," or similar without
>    clear cost acceptance, **stop and require confirmation** before proceeding.
>    Explain that these are premium cost multipliers, not free upgrades.
> 4. Prefer standard Opus IDs (`claude-opus-4.8`, `claude-opus-5`,
>    `claude-opus-5.5`) or a Sonnet / GPT alternative unless the user opts in.
>
> Required confirmation (user must clearly accept cost) before any use:
>
> - They want that **specific** model ID (not a vague "best")
> - They understand it can incur **extreme cost** vs standard alternatives
> - They still want that ID written into the agent config

### Recommended picks by agent role

| Agent role | Good starting models |
|---|---|
| Orchestrator / primary | `claude-sonnet-5`, `gpt-5.6-terra` |
| Complex reasoning / architecture | `claude-opus-5`, `claude-opus-5.5`, `gpt-5.6-sol` |
| Code generation / agentic coding | `gpt-5.3-codex`, `claude-sonnet-5` |
| Fast / cheap subagent | `claude-haiku-4.5`, `gpt-5.6-luna`, `gemini-3.8-flash` |
| Read-only review / analysis | `gpt-5.6-terra`, `claude-sonnet-5`, `gpt-5.4-mini` |

---

## Other common providers

IDs below appear in the models.dev catalog on 2026-09-24.

| Provider | Example model IDs |
|---|---|
| Anthropic | `anthropic/claude-sonnet-5`, `anthropic/claude-sonnet-4-5`, `anthropic/claude-haiku-4-5` |
| OpenAI | `openai/gpt-5.5`, `openai/gpt-5.3-codex`, `openai/gpt-5-mini` |
| OpenCode Zen | `opencode/gpt-5.3-codex`, `opencode/claude-sonnet-5` |
| Local (V2 auto-discovery) | `ollama/<model>`, `lmstudio/<model>`, `vllm/<model>` |

The same extreme-cost rules apply to Fable and fast-mode IDs from any provider.

---

## When to specify model per-agent

**Default for this skill: always set `model` on new agents** unless the user
explicitly says to omit it and inherit. Be intentional: choose a model that
fits the agent's role rather than relying on ambient defaults.

- Different capability tiers for different roles: match the role table above
- Specific provider features (reasoning effort, extended context), via a variant
- Subagents that should keep a fixed model regardless of which primary invokes them

---

## Inheritance defaults

Inheritance applies only when `model` is omitted (and only when the user asked
for that):

- **Primary agents:** use the configured default model (V2: the session's
  selected model takes precedence over the configured default)
- **Subagents:** inherit the model of the invoking primary agent (V1) or the
  parent session (V2)

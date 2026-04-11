# OpenCode — Models

> Source: <https://opencode.ai/docs/models/>  
> Last updated: April 10, 2026

OpenCode uses the [AI SDK](https://ai-sdk.dev/) and [Models.dev](https://models.dev/) to support 75+ LLM providers plus local models.

---

## Select a Model

After configuring a provider, run:

```
/models
```

---

## Recommended Models

Models that work well with OpenCode (good at code generation + tool calling):

- GPT 5.2
- GPT 5.1 Codex
- Claude Opus 4.5
- Claude Sonnet 4.5
- Minimax M2.1
- Gemini 3 Pro

---

## Set a Default Model

```jsonc
// opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5"
}
```

Format: `provider_id/model_id`.

For [OpenCode Zen](https://opencode.ai/docs/zen), use `opencode/gpt-5.1-codex`.  
For custom providers, use the key from the `provider` config section.

---

## Loading Order

When OpenCode starts, it selects a model in this priority:

1. `--model` / `-m` CLI flag
2. `model` key in config
3. Last used model
4. Internal priority fallback

---

## Configure a Model

Set global options for a specific model:

```jsonc
{
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {
          "options": {
            "reasoningEffort": "high",
            "textVerbosity": "low",
            "reasoningSummary": "auto",
            "include": ["reasoning.encrypted_content"]
          }
        }
      }
    },
    "anthropic": {
      "models": {
        "claude-sonnet-4-5-20250929": {
          "options": {
            "thinking": {
              "type": "enabled",
              "budgetTokens": 16000
            }
          }
        }
      }
    }
  }
}
```

Built-in provider/model names come from [Models.dev](https://models.dev/).

---

## Model Variants

Many models support variants with different configurations.

### Built-in variants

| Provider | Variants |
|----------|---------|
| Anthropic | `high` (high thinking budget), `max` (max thinking budget) |
| OpenAI | `none`, `minimal`, `low`, `medium`, `high`, `xhigh` (reasoning effort tiers) |
| Google | `low`, `high` (effort/token budget) |

### Custom variants

Define or override variants in your config:

```jsonc
{
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {
          "variants": {
            "thinking": {
              "reasoningEffort": "high",
              "textVerbosity": "low"
            },
            "fast": { "disabled": true }
          }
        }
      }
    }
  }
}
```

### Cycle variants

Use the `variant_cycle` keybind (default `ctrl+t`) to switch variants.

---

## Small Model

A separate lighter model for lightweight tasks (title generation, etc.):

```jsonc
{
  "small_model": "anthropic/claude-haiku-4-5"
}
```

Defaults to a cheaper model from your configured provider if available.

---

## Provider Timeout Options

```jsonc
{
  "provider": {
    "anthropic": {
      "options": {
        "timeout": 600000,       // request timeout ms (default 300000)
        "chunkTimeout": 30000,   // stream chunk timeout ms
        "setCacheKey": true      // ensure cache key is always set
      }
    }
  }
}
```

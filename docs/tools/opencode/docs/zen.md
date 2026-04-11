# OpenCode — Zen

> Source: <https://opencode.ai/docs/zen/>  
> Last updated: April 10, 2026

OpenCode Zen is a curated AI gateway providing tested, verified models for coding agents. It is currently in beta.

Zen is completely optional — you can use any other provider with OpenCode.

---

## Background

Most providers are configured very differently, leading to inconsistent performance. OpenCode Zen:

1. Tested a select group of models for coding agent use
2. Worked with providers to ensure correct serving
3. Benchmarked model/provider combinations
4. Gives you access to a vetted, high-quality list

Using Zen (vs. OpenRouter for example) ensures you get the best version of the model, not a cheaper route.

---

## How It Works

1. Sign in at [opencode.ai/auth](https://opencode.ai/auth), add billing details, copy your API key
2. Run `/connect` in the TUI, select **OpenCode Zen**, paste your API key
3. Run `/models` to see recommended models

You're charged per request. Add credits to your account.

---

## API Endpoints

The model ID format in config is `opencode/<model-id>`.

### Anthropic Models

| Model | ID | Endpoint SDK |
|-------|----|-------------|
| Claude Opus 4.6 | `claude-opus-4-6` | `@ai-sdk/anthropic` |
| Claude Opus 4.5 | `claude-opus-4-5` | `@ai-sdk/anthropic` |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | `@ai-sdk/anthropic` |
| Claude Sonnet 4.5 | `claude-sonnet-4-5` | `@ai-sdk/anthropic` |
| Claude Haiku 4.5 | `claude-haiku-4-5` | `@ai-sdk/anthropic` |

Endpoint: `https://opencode.ai/zen/v1/messages`

### OpenAI Models

| Model | ID |
|-------|----|
| GPT 5.4 | `gpt-5.4` |
| GPT 5.4 Pro | `gpt-5.4-pro` |
| GPT 5.4 Mini | `gpt-5.4-mini` |
| GPT 5.4 Nano | `gpt-5.4-nano` |
| GPT 5.3 Codex | `gpt-5.3-codex` |
| GPT 5.1 Codex Mini | `gpt-5.1-codex-mini` |

Endpoint: `https://opencode.ai/zen/v1/responses` (SDK: `@ai-sdk/openai`)

### Google Models

| Model | ID |
|-------|----|
| Gemini 3.1 Pro | `gemini-3.1-pro` |
| Gemini 3 Flash | `gemini-3-flash` |

Endpoint: `https://opencode.ai/zen/v1/models/<model-id>` (SDK: `@ai-sdk/google`)

### Other Models

| Model | ID |
|-------|----|
| Kimi K2.5 | `kimi-k2.5` |
| MiniMax M2.5 | `minimax-m2.5` |
| MiniMax M2.5 Free | `minimax-m2.5-free` |
| GLM 5.1 | `glm-5.1` |
| GLM 5 | `glm-5` |
| Qwen3 Coder 480B | `qwen3-coder-480b` |
| Big Pickle | `big-pickle` |
| Qwen3.6 Plus Free | `qwen3.6-plus-free` |
| Nemotron 3 Super Free | `nemotron-3-super-free` |

Endpoint: `https://opencode.ai/zen/v1/chat/completions` (SDK: `@ai-sdk/openai-compatible`)

Full model list: `https://opencode.ai/zen/v1/models`

---

## Pricing

Pay-as-you-go per 1M tokens. Free models available:

- **Big Pickle** — free (limited time, data collected for training)
- **Qwen3.6 Plus Free** — free (limited time)
- **Nemotron 3 Super Free** — free (NVIDIA trial terms, prompts logged by NVIDIA)
- **MiniMax M2.5 Free** — free (limited time)

Sample paid pricing (per 1M tokens, input/output/cache read/cache write):

| Model | Input | Output |
|-------|-------|--------|
| Claude Sonnet 4.6 | $3.00 | $15.00 |
| Claude Haiku 4.5 | $1.00 | $5.00 |
| Gemini 3 Flash | $0.50 | $3.00 |
| GPT 5.4 | $2.50 | $15.00 |
| GPT 5.4 Nano | $0.20 | $1.25 |

Credit card fees: 4.4% + $0.30 per transaction.

### Auto-reload

If balance drops below $5, Zen automatically reloads $20. Configurable or can be disabled entirely.

### Monthly Limits

Set a monthly usage cap per workspace or per team member.

---

## Privacy

- All models hosted in the US
- Providers follow zero-retention policy (no training data use), **except**:
  - Free/beta models during their free period may have data used for improvement
  - Nemotron 3 Super Free: NVIDIA logs prompts/outputs per their Trial Terms
  - OpenAI APIs: 30-day retention per OpenAI's Data Policies
  - Anthropic APIs: 30-day retention per Anthropic's Data Policies

---

## For Teams

Workspaces are currently free for teams (beta).

### Roles

| Role | Permissions |
|------|-------------|
| Admin | Manage models, members, API keys, billing, spend limits |
| Member | Manage only their own API keys |

### Model Access

Admins can enable/disable specific models for the workspace. Useful for preventing use of data-collecting models.

### Bring Your Own Key

Use your own OpenAI or Anthropic API key — tokens billed directly by the provider, not by Zen.

---

## Goals

- Benchmark best models/providers for coding agents
- Provide highest quality options without routing to cheaper alternatives
- Pass along price drops (sell at cost, only charge processing fees)
- No lock-in — use Zen alongside any other provider

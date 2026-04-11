# OpenCode — Providers

> Source: <https://opencode.ai/docs/providers/>  
> Last updated: April 10, 2026

OpenCode uses the [AI SDK](https://ai-sdk.dev/) and [Models.dev](https://models.dev/) to support 75+ LLM providers plus local models.

---

## Quick Setup

1. Run `/connect` in the TUI to add API keys for a provider.
2. Run `/models` to select the model you want to use.

API keys are stored in `~/.local/share/opencode/auth.json`.

---

## OpenCode Zen

OpenCode Zen is a curated, tested model list provided by the OpenCode team.

```
/connect   # select "OpenCode Zen"
```

Sign in at [opencode.ai/auth](https://opencode.ai/auth), add billing details, and paste your API key.

---

## Provider Directory

### Anthropic

```
/connect   # select "Anthropic"
```

Sign in with Claude Pro/Max via browser, or manually enter an API key.

### OpenAI

```
/connect   # select "OpenAI" → ChatGPT Plus/Pro or API key
```

### GitHub Copilot

```
/connect   # select "GitHub Copilot"
```

Navigate to `github.com/login/device` and enter the displayed code.

### Amazon Bedrock

**Environment variables (quick start):**

```bash
# Option 1: Access keys
AWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=YYY opencode

# Option 2: Named profile
AWS_PROFILE=my-profile opencode

# Option 3: Bearer token
AWS_BEARER_TOKEN_BEDROCK=XXX opencode
```

**Config file (recommended):**

```jsonc
{
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile",
        "endpoint": "https://bedrock-runtime.us-east-1.vpce-xxxxx.amazonaws.com"
      }
    }
  }
}
```

Authentication precedence: bearer token > AWS credential chain (profile, access keys, IRSA, instance metadata).

### Azure OpenAI

```
/connect   # search "Azure"
```

Set `AZURE_RESOURCE_NAME` env var or add to your bash profile.

```bash
export AZURE_RESOURCE_NAME=XXX
```

### Google Vertex AI

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_LOCATION=global   # optional, defaults to global
```

### GitLab Duo

```
/connect   # select "GitLab" → OAuth (recommended) or Personal Access Token
```

Requires Premium or Ultimate GitLab subscription. Available on GitLab.com and Self-Managed.

**Self-hosted:**

```bash
export GITLAB_INSTANCE_URL=https://gitlab.company.com
export GITLAB_TOKEN=glpat-...
```

**Configuration:**

```jsonc
{
  "provider": {
    "gitlab": {
      "options": {
        "instanceUrl": "https://gitlab.com"
      }
    }
  }
}
```

### Google Gemini / Vertex

Use `GOOGLE_CLOUD_PROJECT` + `GOOGLE_APPLICATION_CREDENTIALS` for Vertex AI.

### Groq

```
/connect   # search "Groq"
```

### DeepSeek

```
/connect   # search "DeepSeek"
```

### OpenRouter

```
/connect   # search "OpenRouter"
```

Add extra models through config:

```jsonc
{
  "provider": {
    "openrouter": {
      "models": {
        "somecoolnewmodel": {}
      }
    }
  }
}
```

### Together AI, Fireworks AI, Cerebras, Groq, etc.

```
/connect   # search by provider name
```

Each follows the same pattern: get API key, run `/connect`, run `/models`.

---

## Local Models

### Ollama

```jsonc
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "llama2": { "name": "Llama 2" }
      }
    }
  }
}
```

> Ollama can auto-configure itself. See [Ollama integration docs](https://docs.ollama.com/integrations/opencode).

### LM Studio

```jsonc
{
  "provider": {
    "lmstudio": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LM Studio (local)",
      "options": {
        "baseURL": "http://127.0.0.1:1234/v1"
      },
      "models": {
        "google/gemma-3n-e4b": { "name": "Gemma 3n-e4b (local)" }
      }
    }
  }
}
```

### llama.cpp

```jsonc
{
  "provider": {
    "llama.cpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama-server (local)",
      "options": {
        "baseURL": "http://127.0.0.1:8080/v1"
      },
      "models": {
        "qwen3-coder:a3b": {
          "name": "Qwen3-Coder (local)",
          "limit": { "context": 128000, "output": 65536 }
        }
      }
    }
  }
}
```

---

## Custom Providers (OpenAI-compatible)

```
/connect   # scroll to "Other" → enter provider ID
```

Then configure in `opencode.json`:

```jsonc
{
  "provider": {
    "myprovider": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My AI Provider",
      "options": {
        "baseURL": "https://api.myprovider.com/v1",
        "apiKey": "{env:MY_PROVIDER_API_KEY}",
        "headers": {
          "Authorization": "Bearer custom-token"
        }
      },
      "models": {
        "my-model-name": {
          "name": "My Model",
          "limit": { "context": 200000, "output": 65536 }
        }
      }
    }
  }
}
```

**npm package options:**
- `@ai-sdk/openai-compatible` — for `/v1/chat/completions` endpoints
- `@ai-sdk/openai` — for `/v1/responses` endpoints

---

## Customize Base URL

Override the base URL for any provider:

```jsonc
{
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.anthropic.com/v1"
      }
    }
  }
}
```

---

## Disabled / Enabled Providers

```jsonc
{
  "disabled_providers": ["openai", "gemini"],
  "enabled_providers": ["anthropic"]
}
```

`disabled_providers` takes priority.

---

## Troubleshooting

```bash
opencode auth list    # check credentials
```

For custom providers, verify:
- Provider ID in `/connect` matches the key in `opencode.json`
- Correct npm package (`@ai-sdk/openai-compatible` vs `@ai-sdk/openai`)
- Correct `options.baseURL`

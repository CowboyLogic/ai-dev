# Providers Reference

## Structure in opencode.json

```json
{
  "provider": {
    "provider-id": {
      "npm": "@ai-sdk/package-name",
      "name": "Display Name",
      "options": {
        "baseURL": "https://api.example.com/v1",
        "apiKey": "{env:MY_API_KEY}"
      },
      "models": {
        "model-id": {
          "name": "Model Display Name",
          "limit": {
            "context": 200000,
            "output": 65536
          }
        }
      }
    }
  }
}
```

## Model selection syntax

Models are always referenced as `provider/model-id`:
```json
{ "model": "anthropic/claude-sonnet-4-5" }
{ "small_model": "openai/gpt-4o-mini" }
```

## Authentication

Credentials are stored in `~/.local/share/opencode/auth.json` — managed by the CLI, not edited directly.

```bash
/connect               # interactive credential setup inside opencode
opencode auth list     # list stored credentials
```

## Built-in providers

### Anthropic
```json
{
  "provider": {
    "anthropic": {
      "options": {
        "apiKey": "{env:ANTHROPIC_API_KEY}"
      }
    }
  }
}
```
Also supports Claude Pro/Max OAuth via `/connect`.

### OpenAI
```json
{
  "provider": {
    "openai": {
      "options": {
        "apiKey": "{env:OPENAI_API_KEY}"
      }
    }
  }
}
```
Also supports ChatGPT Plus/Pro OAuth via `/connect`.

### Amazon Bedrock
```json
{
  "provider": {
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile"
      }
    }
  }
}
```

> [!NOTE]
> Provider ID is `amazon-bedrock` (not `bedrock`).

Auth precedence:
1. Bearer token — `AWS_BEARER_TOKEN_BEDROCK` env var or token from `/connect`
2. AWS credential chain — profile, access keys, shared credentials, IAM roles, Web Identity Tokens (EKS IRSA), instance metadata

A bearer token, once set, takes precedence over all AWS credential chain methods including configured profiles.

Provider-specific fields: `region` (default: `AWS_REGION` or `us-east-1`), `profile` (default: `AWS_PROFILE`), `endpoint` (VPC endpoint; alias for `baseURL`, takes precedence if both set)

For custom inference profiles, set `models.<key>.id` to the profile ARN.

### Google Vertex AI
```json
{
  "provider": {
    "vertex": {
      "options": {
        "project": "{env:GOOGLE_CLOUD_PROJECT}"
      }
    }
  }
}
```

- Requires `GOOGLE_CLOUD_PROJECT` env var
- Optional: `VERTEX_LOCATION` (defaults to global)
- Auth: `GOOGLE_APPLICATION_CREDENTIALS` (service account JSON path) or `gcloud auth application-default login`

> [!NOTE]
> There is no separate "Google AI / Gemini" provider in the current docs — Gemini models are accessed through Vertex AI.

### GitLab Duo
```json
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

- Auth via `/connect` → OAuth (recommended) or Personal Access Token (`glpat-...`, scope `api`); or set `GITLAB_TOKEN` env var
- Models: `duo-chat-haiku-4-5` (default), `duo-chat-sonnet-4-5`, `duo-chat-opus-4-5`; `duo-workflow-*` models route tool calls through GitLab's Duo Workflow Service instead
- Self-hosted: set `GITLAB_INSTANCE_URL` + `GITLAB_TOKEN` env vars (add `GITLAB_AI_GATEWAY_URL` for a custom AI Gateway); OAuth needs `GITLAB_OAUTH_CLIENT_ID`
- To lock to your own instance, set `"small_model": "gitlab/duo-chat-haiku-4-5"` and `"share": "disabled"` (default small_model is Zen-hosted `gpt-5-nano`)
- Optional: `{ "plugin": ["opencode-gitlab-plugin"] }` for MR/issue/pipeline tools
- Requires GitLab Duo + Agent Platform enabled on a Premium/Ultimate subscription

### GitHub Copilot

Auth via GitHub OAuth — no API key required. Connect with `/connect` inside opencode.

```bash
/connect   # select "GitHub Copilot", then authorize via github.com/login/device
```

Model IDs use the `github-copilot/` prefix (e.g. `github-copilot/claude-sonnet-4.6`). Some models require a Copilot Pro+ subscription.

> [!TIP]
> There is no fixed model list — run `/models` inside opencode after connecting to see the live list available for your subscription.

### xAI

Three auth methods via `/connect` → search "xAI":
- SuperGrok OAuth (browser) — any Grok/X Premium plan with Grok API access
- SuperGrok device-code — for headless/VPS/CI hosts; prints a URL + code to approve from another device
- API key — pay-as-you-go key from the xAI console

### Helicone (AI Gateway with caching)
```json
{
  "provider": {
    "helicone": {
      "options": {
        "baseURL": "https://gateway.helicone.ai",
        "headers": {
          "Helicone-Auth": "Bearer {env:HELICONE_API_KEY}"
        }
      }
    }
  }
}
```

### OpenRouter
```json
{
  "provider": {
    "openrouter": {
      "options": {
        "apiKey": "{env:OPENROUTER_API_KEY}",
        "baseURL": "https://openrouter.ai/api/v1"
      }
    }
  }
}
```

- Use `/connect` or set `apiKey` in config
- Provider routing: set `provider.order` and `allow_fallbacks` in model options

## Custom / OpenAI-compatible providers

Any provider not offered by `/connect` can be added manually — pick a unique provider ID, add a credential via `/connect` → "Other" (or set `apiKey` in config), then define it in `opencode.json` with `npm`, `name`, `options.baseURL`, and `models`.

`npm` package selection: use `@ai-sdk/openai-compatible` for `/v1/chat/completions` APIs (the common case); use `@ai-sdk/openai` if the provider/model uses `/v1/responses`. Can be overridden per-model via `provider.npm` for mixed setups.

## Local / self-hosted providers

### Ollama
```json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "llama3.2": { "name": "Llama 3.2" },
        "mistral": { "name": "Mistral 7B" }
      }
    }
  }
}
```

### llama.cpp
```json
{
  "provider": {
    "llamacpp": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "llama.cpp",
      "options": {
        "baseURL": "http://127.0.0.1:8080/v1"
      },
      "models": {
        "my-model": {
          "name": "My GGUF Model",
          "limit": { "context": 8192, "output": 2048 }
        }
      }
    }
  }
}
```

### LM Studio / llama.cpp / any OpenAI-compatible
```json
{
  "provider": {
    "local": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Local",
      "options": {
        "baseURL": "http://localhost:1234/v1",
        "apiKey": "not-needed"
      },
      "models": {
        "my-model": { "name": "My Local Model" }
      }
    }
  }
}
```

## Provider options reference

| Option | Description |
|--------|-------------|
| `baseURL` | Override default API endpoint |
| `apiKey` | Inline key or `{env:VAR_NAME}` reference |
| `headers` | Custom HTTP request headers object |
| `region` | AWS/cloud region (amazon-bedrock, vertex) |
| `profile` | Named AWS credential profile (amazon-bedrock) |
| `endpoint` | VPC / custom endpoint (amazon-bedrock) |
| `timeout` | Request timeout in milliseconds (default: 300000) |
| `chunkTimeout` | Streaming response timeout in ms |
| `setCacheKey` | Ensure cache key is set on requests |
| `enterpriseUrl` | Enterprise API endpoint override |

## Model fields reference

Custom fields available per model under `provider.<id>.models.<model-id>`:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name |
| `limit.context` | number | Context window size (tokens) |
| `limit.output` | number | Max output tokens |
| `family` | string | Model family grouping |
| `release_date` | string | Release date string |
| `attachment` | boolean | Supports file attachments |
| `reasoning` | boolean | Supports reasoning / chain-of-thought |
| `temperature` | boolean | Supports temperature parameter |
| `tool_call` | boolean | Supports tool/function calling |
| `interleaved` | boolean / object | Interleaved reasoning content (`{"field": "reasoning_content"}`) |
| `modalities` | object | `{"input": [...], "output": [...]}` — `"text"`, `"audio"`, `"image"`, `"video"`, `"pdf"` |
| `experimental` | boolean | Mark as experimental |
| `status` | enum | `"alpha"` \| `"beta"` \| `"deprecated"` |
| `variants` | object | Variant configs (e.g., `"thinking": {"disabled": false}`) |
| `timeout` | number | Per-model request timeout (ms) |
| `headers` | object | Per-model HTTP headers |

## Model whitelist / blacklist

Filter which models are visible for a provider:

```json
{
  "provider": {
    "openrouter": {
      "whitelist": ["anthropic/claude-opus-4-5", "openai/gpt-4o"],
      "blacklist": ["meta-llama/llama-3-8b-instruct"]
    }
  }
}
```

## Provider management

```json
{ "enabled_providers": ["anthropic", "openai"] }   // only these providers
{ "disabled_providers": ["amazon-bedrock", "vertex"] }     // exclude these providers
```

## Using /models

Inside opencode, run `/models` to browse and select from all configured models. Models from all enabled providers appear here.

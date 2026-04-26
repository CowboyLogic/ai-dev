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
    "bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "my-aws-profile"
      }
    }
  }
}
```

Auth options (checked in order):
1. `AWS_BEARER_TOKEN_BEDROCK` env var
2. Named profile (`AWS_PROFILE` or `profile` config field)
3. `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
4. IAM roles / Web Identity

Provider-specific fields: `region`, `profile`, `endpoint` (VPC endpoint alias)

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
- Auth: service account JSON or `gcloud auth application-default login`

### Google AI (Gemini)
```json
{
  "provider": {
    "google": {
      "options": {
        "apiKey": "{env:GOOGLE_AI_API_KEY}"
      }
    }
  }
}
```

### GitLab Duo
```json
{
  "provider": {
    "gitlab": {
      "options": {
        "apiKey": "{env:GITLAB_TOKEN}"
      }
    }
  }
}
```

- OAuth or Personal Access Token (PAT)
- Self-hosted: set `GITLAB_INSTANCE_URL` and `GITLAB_TOKEN` env vars
- Use `small_model` for `gitlab/gpt-5-nano`

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
| `region` | AWS/cloud region (Bedrock, Vertex) |
| `profile` | Named AWS credential profile (Bedrock) |
| `endpoint` | VPC / custom endpoint (Bedrock) |
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
{ "disabled_providers": ["bedrock", "vertex"] }     // exclude these providers
```

## Using /models

Inside opencode, run `/models` to browse and select from all configured models. Models from all enabled providers appear here.

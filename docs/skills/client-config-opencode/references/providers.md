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

## Provider management

```json
{ "enabled_providers": ["anthropic", "openai"] }   // only these providers
{ "disabled_providers": ["bedrock", "vertex"] }     // exclude these providers
```

## Using /models

Inside opencode, run `/models` to browse and select from all configured models. Models from all enabled providers appear here.

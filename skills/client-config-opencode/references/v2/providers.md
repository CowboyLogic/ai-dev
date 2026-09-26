# V2 Providers and Models Reference

Sources: <https://opencode.ai/v2/docs/providers/>, <https://opencode.ai/v2/docs/models/>,
<https://opencode.ai/v2/docs/cli/providers/>.

## Credentials

Connect first, then pick a model:

```text
/connect
/models
```

```bash
opencode auth login                      # interactive picker
opencode auth login anthropic --method key
opencode auth list
opencode auth switch anthropic work      # switch active saved account
opencode auth logout anthropic work
```

Saved keys and OAuth tokens live in the server's SQLite database (usually `~/.local/share/opencode/opencode.db`;
`opencode debug paths db` prints it). V2 imports the legacy `auth.json` once and never writes back to it. Never
edit the database — use `/connect` or `opencode auth`.

Environment credentials must reach the **server process**:

```bash
opencode service set env ANTHROPIC_API_KEY sk-ant-...   # shared background server (restarts it)
ANTHROPIC_API_KEY=sk-ant-... opencode --standalone      # private server
```

A saved account takes precedence over an environment connection.

## Provider entry

The `providers` map (plural) is keyed by the provider ID used in model references (`acme/qwen3-coder`).

```jsonc
{
  "providers": {
    "acme": {
      "name": "Acme",
      "env": ["ACME_API_KEY"],
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "https://llm.acme.example/v1" },
      "headers": { "X-Gateway-Tenant": "engineering" },
      "body": { "metadata": { "application": "opencode" } },
      "models": {
        "qwen3-coder": { "name": "Qwen 3 Coder" },
      },
    },
  },
}
```

| Field | Purpose |
|-------|---------|
| `name` | Display name |
| `env` | Ordered env var names that can supply the credential |
| `package` | Runtime provider package |
| `canonical` | Built-in provider ID whose catalog defaults this provider inherits |
| `settings` | Typed OpenCode controls and JSON options passed to the package (e.g. `baseURL`, `apiKey`); package-specific |
| `headers` | String HTTP headers on every request |
| `body` | JSON merged into every request body |
| `models` | Models to add or override, keyed by OpenCode model ID |

Other documented `settings` keys: `transport` (`"websocket"` \| `"http"` for OpenAI, xAI, supported Azure
Responses), `compaction.type` (`"native"` \| `"summary"`), plus provider-specific keys below.

## Packages

Native packages:

```text
@opencode/ai/providers/openai            @opencode/ai/providers/openai/chat
@opencode/ai/providers/openai/responses  @opencode/ai/providers/openai-compatible
@opencode/ai/providers/openai-compatible/responses
@opencode/ai/providers/anthropic         @opencode/ai/providers/anthropic-compatible
@opencode/ai/providers/google            @opencode/ai/providers/google-vertex
@opencode/ai/providers/google-vertex/gemini   @opencode/ai/providers/google-vertex/chat
@opencode/ai/providers/google-vertex/responses @opencode/ai/providers/google-vertex/messages
@opencode/ai/providers/azure             @opencode/ai/providers/azure/chat
@opencode/ai/providers/azure/responses   @opencode/ai/providers/amazon-bedrock
@opencode/ai/providers/amazon-bedrock/mantle   @opencode/ai/providers/amazon-bedrock/mantle/chat
@opencode/ai/providers/amazon-bedrock/mantle/responses
@opencode/ai/providers/openrouter        @opencode/ai/providers/xai
```

Also accepted: an npm package (`@acme/opencode-provider`) or an absolute `file://` URL. When migrating a V1 `npm`
AI SDK package, the migration guide shows the `aisdk:` prefix (`"package": "aisdk:@ai-sdk/openai-compatible"`).

> [!NOTE]
> The providers/models pages use `@opencode/ai/providers/openai-compatible` for new OpenAI-compatible providers,
> while the migration guide converts V1 `npm` values to `aisdk:@ai-sdk/...`. Both forms appear in official docs;
> prefer the native package for new configs.

## Models

```jsonc
{
  "model": "openai/coding-default",
  "providers": {
    "openai": {
      "models": {
        "coding-default": {
          "modelID": "gpt-5.2",
          "name": "Coding default",
          "capabilities": { "tools": true, "input": ["text", "image"], "output": ["text"] },
          "limit": { "context": 200000, "output": 32000 },
          "settings": { "reasoningEffort": "medium" },
          "variants": [
            { "id": "fast", "settings": { "reasoningEffort": "low" } },
            { "id": "deep", "settings": { "reasoningEffort": "high" } },
          ],
        },
        "legacy-model": { "disabled": true },
      },
    },
  },
}
```

| Field | Purpose |
|-------|---------|
| `modelID` | ID sent to the provider (map key is the OpenCode ID) |
| `name` | Display name |
| `family` | Grouping |
| `package` | Per-model runtime override |
| `settings` / `headers` / `body` | Per-model request options |
| `capabilities` | `tools`, `input`, `output` media types |
| `compatibility` | e.g. `reasoningField` (`reasoning`, `reasoning_content`, `reasoning_text`, or custom) |
| `variants` | **Array** of `{ id, settings?, headers?, body? }` |
| `cost` | Input/output and optional `cache.read`/`cache.write` per million tokens |
| `limit` | `context`, `input`, `output` |
| `disabled` | Hide from selection |

Unknown models default to tools on, text+image in, text out, 200,000 context, 32,000 output — set real values.
Options apply provider → model → variant; `settings` and `body` deep-merge, arrays/scalars replace, headers match
case-insensitively.

## Model references

```text
openai/gpt-5.2
openai/gpt-5.2#high
openrouter/anthropic/claude-sonnet-4.5#high
```

Provider ends at the first `/`; model may contain `/`; `#variant` is optional; IDs are case-sensitive. Root, agent,
and command `model` fields also accept `{ "providerID": "...", "model": "..." }`. The root `model` does **not**
retain a variant — select variants per run (`opencode run --model x/y#high`), agent, or command.

## Provider recipes

### Endpoint override (keep the catalog provider)

```jsonc
{ "providers": { "anthropic": { "settings": { "baseURL": "https://llm-proxy.example.com/anthropic" } } } }
```

### Amazon Bedrock

```jsonc
{ "providers": { "amazon-bedrock": { "settings": { "profile": "work", "region": "us-west-2" } } } }
```

A profile, `AWS_PROFILE`, `AWS_ACCESS_KEY_ID`, web identity token file, or container credential URI activates the
provider — a region alone does not. Region falls back to `AWS_REGION`, `AWS_DEFAULT_REGION`, then `us-east-1`.
VPC endpoint: `settings.baseURL`. Bedrock API keys use `AWS_BEARER_TOKEN_BEDROCK`.

### Google Vertex

```jsonc
{ "providers": { "google-vertex": { "settings": { "project": "my-project", "location": "us-central1" } } } }
```

Auth via ADC (`gcloud auth application-default login` or `GOOGLE_APPLICATION_CREDENTIALS`). Project env fallback:
`GOOGLE_VERTEX_PROJECT`, `GOOGLE_CLOUD_PROJECT`, `GCP_PROJECT`, `GCLOUD_PROJECT`. Location fallback:
`GOOGLE_VERTEX_LOCATION`, `GOOGLE_CLOUD_LOCATION`, `VERTEX_LOCATION`, default `us-central1`. One `google-vertex` ID
covers Gemini, Anthropic, and OpenAI-compatible Vertex models; `google-vertex-anthropic` is rejected in V2.

### Azure

```jsonc
{ "providers": { "azure": { "settings": { "resourceName": "my-models" }, "models": { "gpt-5-mini": { "modelID": "gpt-production" } } } } }
```

Or `AZURE_RESOURCE_NAME` (legacy `AZURE_COGNITIVE_SERVICES_RESOURCE_NAME`). Entra ID via `az login`, then choose
Microsoft Entra ID in `/connect`. The V1 ID `azure-cognitive-services` is rejected — use `azure`.

### GitHub Copilot

Device OAuth only: `/connect` → GitHub Copilot → GitHub.com or GitHub Enterprise → `/models`. Needs Copilot Chat access.

### OpenRouter

```jsonc
{ "model": "openrouter/anthropic/claude-sonnet-4" }
```

Use `OPENROUTER_API_KEY` or `/connect`. Keep the native package when overriding `settings.baseURL`.

### Local runtimes (auto-discovered)

| Provider ID | Default endpoint | Disable discovery |
|-------------|------------------|-------------------|
| `ollama` | `http://127.0.0.1:11434` | `"plugins": ["-opencode.provider.ollama"]` |
| `lmstudio` | `http://127.0.0.1:1234/v1` | `"plugins": ["-opencode.provider.lmstudio"]` |
| `vllm` | `http://127.0.0.1:8000/v1` | `"plugins": ["-opencode.provider.vllm"]` |

Point elsewhere with `settings.baseURL` (include `/v1`) and optional `settings.apiKey`. Discovered vLLM models start
with tools disabled.

### Any other OpenAI-compatible server

```jsonc
{
  "model": "local/coder",
  "providers": {
    "local": {
      "name": "Local server",
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "http://127.0.0.1:1234/v1", "apiKey": "{env:LOCAL_API_KEY}" },
      "models": {
        "coder": {
          "modelID": "model-name-on-server",
          "capabilities": { "tools": true, "input": ["text"], "output": ["text"] },
          "limit": { "context": 32768, "output": 8192 },
        },
      },
    },
  },
}
```

## Restricting providers

V2 has no native `enabled_providers` / `disabled_providers`; use `provider.use` policies (see
[permissions.md](permissions.md#policies)). The V1 fields still load and are converted internally.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| `Model unavailable: provider/model` | Provider inactive, model ID absent/disabled; for aliases check the map key, not `modelID` |
| `NAME is required to resolve the provider endpoint` | A `${NAME}` placeholder remains in `baseURL`; set it on the server |
| `Azure resource name is missing` | Set `settings.resourceName`, `AZURE_RESOURCE_NAME`, or a full `baseURL` |
| Vertex/Bedrock missing | Needs a resolvable project / a credential-chain input, not just ADC or a region |

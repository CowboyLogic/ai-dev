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
(umask 077; rm -f creds.json; opencode auth export > creds.json)   # stored credentials, INCLUDING SECRETS
opencode auth import creds.json          # import a file produced by `auth export` (reads stdin when omitted)
```

`auth export` takes an optional integration ID or name (all integrations when omitted). `auth import` needs a file
argument or piped stdin (`opencode auth export | opencode auth import`). Both appear in `opencode auth --help` on
2.0.27 but not in the V2 docs. Treat the exported file as a secret and delete it after use. Create it owner-only
(the `umask 077` above): a plain `>` uses the caller's umask, often `022`, which makes the file world-readable. The
`rm -f` matters on a rerun, because redirecting onto an existing file keeps that file's mode.

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
| `compatibility` | Request/response compatibility defaults inherited by every model of the provider; a model's `compatibility` overrides individual fields (see [Compatibility](#compatibility)) |
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
| `compatibility` | Per-model overrides of the provider's `compatibility` (see [Compatibility](#compatibility)) |
| `variants` | **Array** of `{ id, settings?, headers?, body? }` |
| `cost` | Input/output and optional `cache.read`/`cache.write` per million tokens |
| `limit` | `context`, `input`, `output` |
| `disabled` | Hide from selection |

Unknown models default to tools on, text+image in, text out, 200,000 context, 32,000 output — set real values.
Options apply provider → model → variant; `settings` and `body` deep-merge, arrays/scalars replace, headers match
case-insensitively.

## Timeouts

Requests wait up to five minutes for response headers and up to fifteen minutes between streamed chunks. The 2.0.28
release notes raised the default streamed-chunk timeout from 5 to 15 minutes and the 2.0.29 source sets it to
`900_000` ms, but the 2.0.29 providers docs page still says five, so set `chunkTimeout` explicitly if you depend on a
value. Set these on the provider's `settings` (provider-wide; not per model or variant), in milliseconds, or `false`
to disable a limit:

```jsonc
{ "providers": { "anthropic": { "settings": { "headerTimeout": 600000, "chunkTimeout": false } } } }
```

| Setting | Default | What it limits |
|---------|---------|----------------|
| `headerTimeout` | 5 minutes | Wait for response headers |
| `chunkTimeout` | 15 minutes since 2.0.28 (30 minutes on a WebSocket transport, where it bounds the gap between frames) | Gap between streamed chunks |
| `timeout` | none | The whole request, from send until the response completes |

A request that exceeds a limit fails with a transport error; OpenCode retries a timed-out request up to three times.

## Compatibility

`compatibility` adjusts how OpenCode talks to an OpenAI-compatible or otherwise non-standard endpoint. Set it on a
provider to apply to all its models, or on a model to override single fields. Fields (from the 2.0.29 config schema):

| Field | Values | Purpose |
|-------|--------|---------|
| `reasoningField` | `reasoning`, `reasoning_content`, `reasoning_text`, or a custom string | Field that carries reasoning text |
| `requireReasoning` | boolean | Require every assistant message to include its reasoning field, even when empty |
| `maxTokensField` | `max_completion_tokens` \| `max_tokens` | Request field that carries the output limit; detected from the provider and `baseURL` when unset (OpenAI-compatible chat protocol) |
| `requireFinishReason` | boolean | OpenAI-compatible chat: a stream that ends without `finish_reason` is an error (default `true`); set `false` for endpoints that omit it |
| `requireAssistantAfterTool` | boolean | OpenAI-compatible chat: append a `Done.` assistant message when the last message is a tool result (default on only for Mistral) |
| `supportsPromptCacheKey` | boolean | Send a prompt cache key (V1 `options.setCacheKey` migrates here) |
| `cacheFormat` | `anthropic` \| `alibaba` | Prompt-cache marker syntax the endpoint accepts |
| `supportsThinkingBlockBinding`, `supportsEffortUpdates` | boolean | **Model-only**; override model-ID detection |

`cacheFormat` is for Claude models behind an OpenAI-compatible proxy such as LiteLLM, where OpenCode cannot tell that
Anthropic-style `cache_control` breakpoints are needed. It marks the last tool definition, the system prompt, and the
latest message with `cache_control: { "type": "ephemeral" }` (the endpoint's default five-minute lifetime).
`alibaba` uses the same markers but skips tool definitions. Routes known to need breakpoints, such as Anthropic, get
them automatically.

```jsonc
{
  "providers": {
    "litellm": {
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": { "baseURL": "https://litellm.example.com/v1" },
      "models": {
        "claude-sonnet-5": { "compatibility": { "cacheFormat": "anthropic" } },
      },
    },
  },
}
```

## Request encoding

`settings.encoding` compresses HTTP request bodies with `"zstd"` or `"gzip"`, or sends plain JSON with `"none"`. Set it
on a provider, model, or variant; the most specific value wins. Only enable an encoding the endpoint decodes: most
providers and gateways reject compressed bodies. OpenAI defaults to `"zstd"` when signed in with ChatGPT and no custom
`baseURL` is configured; API keys send plain JSON. WebSocket messages are unaffected (2.0.28 release notes and the
2.0.29 providers page).

```jsonc
{ "providers": { "openai": { "settings": { "encoding": "none" } } } }
```

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

Auth via ADC (`gcloud auth application-default login` or `GOOGLE_APPLICATION_CREDENTIALS`). Since 2.0.26 `/connect` →
Vertex also offers **Google Cloud credentials (gcloud auth or environment)**, which uses ADC and lets you pick or
enter the project and location (2.0.26 release notes; the V2 providers page does not mention it). ADC also works when
`CLOUDSDK_CONFIG` points to a custom gcloud configuration directory (fixed in 2.0.27, per its release notes). Project env
fallback:
`GOOGLE_VERTEX_PROJECT`, `GOOGLE_CLOUD_PROJECT`, `GCP_PROJECT`, `GCLOUD_PROJECT`. Location fallback:
`GOOGLE_VERTEX_LOCATION`, `GOOGLE_CLOUD_LOCATION`, `VERTEX_LOCATION`, default `us-central1`. One `google-vertex` ID
covers Gemini, Anthropic, and OpenAI-compatible Vertex models; `google-vertex-anthropic` is rejected in V2.

### Azure

```jsonc
{ "providers": { "azure": { "settings": { "resourceName": "my-models" } } } }
```

Or `AZURE_RESOURCE_NAME` (legacy `AZURE_COGNITIVE_SERVICES_RESOURCE_NAME`). Entra ID via `az login`, then choose
Microsoft Entra ID (Azure CLI) in `/connect`; it uses the account selected in the Azure CLI, so select a tenant and
subscription explicitly (`az login --tenant`, `az account set --subscription`) for another one. A resource name
entered when connecting is saved with the connection and takes precedence over configuration; connect again to
change it. The V1 ID `azure-cognitive-services` is rejected — use `azure`.

**Deployments.** Azure serves a model only through a deployment, so OpenCode lists your resource's deployments in
the background (after startup, connecting, and switching accounts) and shows those instead of the whole catalog.
The whole catalog stays available until the list loads or if it fails. Deployment names become lowercase model IDs
(`azure/gpt-production`); a deployment named after its model (`gpt-5-mini`) keeps the catalog ID. Restart OpenCode
or connect again to pick up a new deployment. A custom `settings.baseURL` keeps the catalog.

Configure a deployment explicitly when its model is not in the catalog (a fine-tuned model), or to map a model ID to
a deployment yourself; explicitly configured models are always kept:

```jsonc
{ "providers": { "azure": { "models": { "gpt-5-mini": { "modelID": "gpt-production" } } } } }
```

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

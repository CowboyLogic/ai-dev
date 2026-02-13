# Claude Code with Google Cloud VertexAI

Configure Claude Code CLI to use Google Cloud VertexAI as the model provider instead of Anthropic's API. This is ideal for enterprise environments that prefer to manage model access through Google Cloud Platform.

## Overview

Claude Code supports multiple model providers through configuration. By configuring VertexAI as the provider, you can:

- Route all Claude model requests through your Google Cloud project
- Leverage existing GCP infrastructure and billing
- Meet enterprise compliance requirements for API access
- Maintain audit trails within Google Cloud Console
- Use VPC Service Controls and private endpoints

## License

Claude Code is proprietary software owned by Anthropic PBC. Use is subject to [Anthropic's Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms). See the [LICENSE.md](https://github.com/anthropics/claude-code/blob/main/LICENSE.md) in the Claude Code repository for complete terms.

**Key points:**

- Proprietary software, not open source
- Use is governed by Anthropic's Commercial Terms of Service
- Free to use, but subject to Anthropic's terms and conditions
- Separate billing applies for Claude model usage through VertexAI (charged by Google Cloud)
- No additional license fee for the CLI tool itself, but usage rights are controlled by Anthropic

## Prerequisites

### Required Tools

1. **Claude Code CLI** — Install from [claude.ai/code](https://claude.ai/code)
2. **Google Cloud SDK** — Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Google Cloud Project** — With VertexAI API enabled

### Google Cloud Setup

#### 1. Enable VertexAI API

```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Enable VertexAI API
gcloud services enable aiplatform.googleapis.com --project=$GCP_PROJECT_ID
```

#### 2. Configure Authentication

Choose one of the following authentication methods:

**Option A: Application Default Credentials (Recommended for Development)**

```bash
# Authenticate with your user account
gcloud auth application-default login

# Set default project
gcloud config set project $GCP_PROJECT_ID
```

**Option B: Service Account (Recommended for Production)**

```bash
# Create service account
gcloud iam service-accounts create claude-code-vertexai \
  --display-name="Claude Code VertexAI Access" \
  --project=$GCP_PROJECT_ID

# Grant Vertex AI User role
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:claude-code-vertexai@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/claude-vertexai-key.json \
  --iam-account=claude-code-vertexai@${GCP_PROJECT_ID}.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/claude-vertexai-key.json"
```

#### 3. Verify Access

```bash
# Test VertexAI access
gcloud ai models list \
  --region=us-central1 \
  --project=$GCP_PROJECT_ID
```

If this command succeeds, your authentication is configured correctly.

## Claude Code Configuration

### Configuration File Location

Claude Code stores configuration in `~/.claude/config.json` (Linux/macOS) or `%USERPROFILE%\.claude\config.json` (Windows).

### Basic Configuration

Create or edit your Claude Code configuration file:

```json
{
  "provider": "vertex",
  "vertex": {
    "projectId": "your-project-id",
    "region": "us-central1"
  },
  "model": "claude-opus-4-6@vertex"
}
```

### Full Configuration Example

```json
{
  "provider": "vertex",
  "vertex": {
    "projectId": "your-project-id",
    "region": "us-central1",
    "credentialsPath": "/path/to/service-account-key.json"
  },
  "model": "claude-opus-4-6@vertex",
  "temperature": 0.7,
  "maxTokens": 4096,
  "timeout": 60000,
  "retries": 3
}
```

### Configuration Options

#### Provider Settings

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `provider` | string | Yes | Set to `"vertex"` for VertexAI |
| `vertex.projectId` | string | Yes | Your Google Cloud project ID |
| `vertex.region` | string | Yes | VertexAI region (e.g., `us-central1`, `europe-west4`) |
| `vertex.credentialsPath` | string | No | Path to service account JSON key (if not using ADC) |
| `vertex.endpoint` | string | No | Custom VertexAI endpoint (for VPC/private endpoints) |

#### Model Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `claude-opus-4-6@vertex` | Claude model to use |
| `temperature` | number | 0.7 | Sampling temperature (0.0-1.0) |
| `maxTokens` | number | 4096 | Maximum tokens in response |
| `timeout` | number | 60000 | Request timeout in milliseconds |
| `retries` | number | 3 | Number of retry attempts for failed requests |

### Available Models

Claude models available through VertexAI (as of February 2026):

| Model ID | Description | Use Case |
|----------|-------------|----------|
| `claude-opus-4-6@vertex` | Most capable model | Complex reasoning, code generation |
| `claude-sonnet-4-5@vertex` | Balanced performance/cost | General development tasks |
| `claude-haiku-4-5@vertex` | Fast, efficient | Quick edits, documentation |

> [!NOTE]
> Model availability varies by region. Check [Google Cloud documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/models) for your region's model catalog.

## Environment Variables

Claude Code supports environment variable overrides for sensitive configuration:

```bash
# Google Cloud Project
export VERTEX_PROJECT_ID="your-project-id"

# Service Account Credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# VertexAI Region
export VERTEX_REGION="us-central1"

# Claude Code Model Override
export CLAUDE_MODEL="claude-opus-4-6@vertex"
```

These environment variables take precedence over values in `config.json`.

## Enterprise Configuration

### Multi-Region Setup

For global teams, configure region-specific endpoints:

```json
{
  "provider": "vertex",
  "vertex": {
    "projectId": "your-project-id",
    "regions": {
      "primary": "us-central1",
      "fallback": ["us-east1", "europe-west4"],
      "preferredRegion": "auto"
    }
  },
  "failover": {
    "enabled": true,
    "retryDelayMs": 1000
  }
}
```

### VPC Private Endpoints

For secure enterprise deployments using VPC Service Controls:

```json
{
  "provider": "vertex",
  "vertex": {
    "projectId": "your-project-id",
    "region": "us-central1",
    "endpoint": "https://us-central1-aiplatform.private.googleapis.com",
    "network": "projects/your-project-id/global/networks/your-vpc"
  }
}
```

### Workload Identity (GKE/Cloud Run)

When running Claude Code in Google Kubernetes Engine or Cloud Run:

```json
{
  "provider": "vertex",
  "vertex": {
    "projectId": "your-project-id",
    "region": "us-central1",
    "useWorkloadIdentity": true,
    "serviceAccountEmail": "claude-code@your-project-id.iam.gserviceaccount.com"
  }
}
```

Ensure the Kubernetes service account is bound to the GCP service account:

```bash
# Bind Kubernetes SA to GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  claude-code@your-project-id.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:your-project-id.svc.id.goog[namespace/ksa-name]"
```

### Quota and Rate Limiting

Configure quota management for enterprise usage:

```json
{
  "provider": "vertex",
  "vertex": {
    "projectId": "your-project-id",
    "region": "us-central1",
    "quotas": {
      "requestsPerMinute": 60,
      "tokensPerMinute": 40000,
      "concurrentRequests": 5
    }
  },
  "rateLimiting": {
    "enabled": true,
    "strategy": "token-bucket"
  }
}
```

## Usage Examples

### Basic Usage

After configuration, use Claude Code normally:

```bash
# Start interactive session
claude-code

# One-off command
claude-code "refactor this function to use async/await"

# Work with specific files
claude-code "add error handling to api.js"
```

### Verify VertexAI Connection

```bash
# Enable debug logging
export CLAUDE_DEBUG=true

# Run Claude Code with verbose output
claude-code --verbose "hello"

# Check logs for VertexAI endpoint confirmation
# Expected output: "Using provider: vertex (us-central1)"
```

### Switch Models Dynamically

```bash
# Use Opus for complex task
CLAUDE_MODEL=claude-opus-4-6@vertex claude-code "architect a microservices system"

# Use Haiku for quick edits
CLAUDE_MODEL=claude-haiku-4-5@vertex claude-code "fix typos in README.md"
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Error:** `Permission denied: Unable to access VertexAI`

**Solutions:**

```bash
# Verify authentication
gcloud auth application-default login

# Check project configuration
gcloud config get-value project

# Verify VertexAI API is enabled
gcloud services list --enabled --filter="aiplatform.googleapis.com"
```

#### 2. Region Availability

**Error:** `Model not available in region`

**Solution:** Check model availability in your region:

```bash
# List available models
gcloud ai models list --region=us-central1 --filter="claude"

# Try alternative regions
gcloud ai models list --region=us-east1 --filter="claude"
gcloud ai models list --region=europe-west4 --filter="claude"
```

Update configuration to use available region:

```json
{
  "vertex": {
    "region": "us-east1"
  }
}
```

#### 3. Quota Exceeded

**Error:** `Quota exceeded for VertexAI requests`

**Solutions:**

1. Check current quota:

```bash
gcloud compute project-info describe --project=your-project-id
```

2. Request quota increase in [Google Cloud Console](https://console.cloud.google.com/iam-admin/quotas)

3. Implement rate limiting in configuration (see [Quota and Rate Limiting](#quota-and-rate-limiting))

#### 4. Service Account Permissions

**Error:** `Service account lacks required permissions`

**Solution:** Grant necessary IAM roles:

```bash
# Vertex AI User (minimum required)
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:your-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

# For advanced features (model tuning, monitoring)
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:your-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.admin"
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug environment variables
export CLAUDE_DEBUG=true
export GOOGLE_CLOUD_DEBUG=true

# Run with verbose output
claude-code --verbose --log-level=debug "test command"

# Logs saved to: ~/.claude/logs/
```

### Validate Configuration

Create a test script to validate your setup:

```bash
#!/bin/bash
# validate-vertex-config.sh

echo "Validating VertexAI Configuration..."

# 1. Check gcloud authentication
echo "1. Checking gcloud authentication..."
gcloud auth application-default print-access-token > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✓ gcloud authenticated"
else
  echo "   ✗ gcloud authentication failed"
  exit 1
fi

# 2. Verify project access
echo "2. Verifying project access..."
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -n "$PROJECT_ID" ]; then
  echo "   ✓ Project: $PROJECT_ID"
else
  echo "   ✗ No project configured"
  exit 1
fi

# 3. Check VertexAI API
echo "3. Checking VertexAI API..."
gcloud services list --enabled --filter="aiplatform.googleapis.com" --format="value(name)" 2>/dev/null | grep -q aiplatform
if [ $? -eq 0 ]; then
  echo "   ✓ VertexAI API enabled"
else
  echo "   ✗ VertexAI API not enabled"
  exit 1
fi

# 4. Test model access
echo "4. Testing model access..."
gcloud ai models list --region=us-central1 --limit=1 > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "   ✓ Model access successful"
else
  echo "   ✗ Cannot access models"
  exit 1
fi

# 5. Verify Claude Code config
echo "5. Verifying Claude Code configuration..."
if [ -f ~/.claude/config.json ]; then
  echo "   ✓ Config file exists"
  # Validate JSON
  python3 -m json.tool ~/.claude/config.json > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    echo "   ✓ Config is valid JSON"
  else
    echo "   ✗ Config has JSON syntax errors"
    exit 1
  fi
else
  echo "   ✗ Config file not found"
  exit 1
fi

echo ""
echo "✓ All validations passed! VertexAI configuration is ready."
```

Run the validation script:

```bash
chmod +x validate-vertex-config.sh
./validate-vertex-config.sh
```

## Security Best Practices

### 1. Credential Management

**Do:**

- Use service accounts with minimal required permissions
- Store credentials securely (Google Secret Manager, HashiCorp Vault)
- Rotate service account keys regularly (every 90 days)
- Use Workload Identity for GKE/Cloud Run deployments

**Don't:**

- Commit service account keys to version control
- Share credentials across environments
- Use personal accounts for production workloads
- Grant `roles/owner` or `roles/editor` roles

### 2. Network Security

**Production Setup:**

```json
{
  "vertex": {
    "projectId": "your-project-id",
    "region": "us-central1",
    "endpoint": "https://us-central1-aiplatform.private.googleapis.com",
    "network": "projects/your-project-id/global/networks/prod-vpc",
    "vpcServiceControls": {
      "enabled": true,
      "perimeterName": "projects/123456789/accessPolicies/policy-id/servicePerimeters/perimeter-name"
    }
  }
}
```

### 3. Audit Logging

Enable Cloud Audit Logs for VertexAI:

```bash
# Enable Data Access audit logs
gcloud projects set-iam-policy your-project-id policy.yaml
```

**policy.yaml:**

```yaml
auditConfigs:
- service: aiplatform.googleapis.com
  auditLogConfigs:
  - logType: ADMIN_READ
  - logType: DATA_READ
  - logType: DATA_WRITE
```

Monitor logs in Cloud Logging:

```bash
# View VertexAI audit logs
gcloud logging read "resource.type=aiplatform.googleapis.com" \
  --project=your-project-id \
  --limit=50
```

### 4. Cost Management

**Set up budget alerts:**

```bash
# Create budget
gcloud billing budgets create \
  --billing-account=012345-6789AB-CDEF01 \
  --display-name="VertexAI Monthly Budget" \
  --budget-amount=1000 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

**Configure cost controls in Claude Code:**

```json
{
  "vertex": {
    "costControls": {
      "maxMonthlySpend": 1000,
      "alertThresholds": [500, 750, 900],
      "quotas": {
        "maxRequestsPerDay": 10000,
        "maxTokensPerRequest": 4096
      }
    }
  }
}
```

## Migration from Anthropic API

If you're migrating from Anthropic's direct API to VertexAI:

### 1. Update Configuration

**Before (Anthropic):**

```json
{
  "provider": "anthropic",
  "anthropic": {
    "apiKey": "sk-ant-..."
  },
  "model": "claude-opus-4-6"
}
```

**After (VertexAI):**

```json
{
  "provider": "vertex",
  "vertex": {
    "projectId": "your-project-id",
    "region": "us-central1"
  },
  "model": "claude-opus-4-6@vertex"
}
```

### 2. Model Name Mapping

| Anthropic API | VertexAI |
|---------------|----------|
| `claude-opus-4-6` | `claude-opus-4-6@vertex` |
| `claude-sonnet-4-5` | `claude-sonnet-4-5@vertex` |
| `claude-haiku-4-5` | `claude-haiku-4-5@vertex` |

### 3. Behavior Differences

**Rate Limits:**

- Anthropic: Per-API-key limits
- VertexAI: Per-project quotas (generally higher for enterprise)

**Regional Availability:**

- Anthropic: Global endpoint
- VertexAI: Region-specific (requires explicit region configuration)

**Pricing:**

- Anthropic: Pay-per-token with volume discounts
- VertexAI: GCP committed use discounts available, integrated billing

### 4. Testing Migration

Create a test configuration to verify behavior:

```bash
# Test with small prompt
echo '{"provider":"vertex","vertex":{"projectId":"your-project-id","region":"us-central1"},"model":"claude-haiku-4-5@vertex"}' > ~/.claude/config-test.json

# Run test command
CLAUDE_CONFIG=~/.claude/config-test.json claude-code "echo hello"

# Compare output with Anthropic API version
```

## Reference

### Official Documentation

- [Google Cloud VertexAI](https://cloud.google.com/vertex-ai/docs)
- [Claude on VertexAI](https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/claude)
- [VertexAI Authentication](https://cloud.google.com/vertex-ai/docs/authentication)
- [Claude Code CLI](https://claude.ai/code)

### Configuration Schema

Full JSON schema for Claude Code VertexAI configuration:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["provider", "vertex"],
  "properties": {
    "provider": {
      "type": "string",
      "enum": ["vertex"]
    },
    "vertex": {
      "type": "object",
      "required": ["projectId", "region"],
      "properties": {
        "projectId": { "type": "string" },
        "region": { "type": "string" },
        "credentialsPath": { "type": "string" },
        "endpoint": { "type": "string", "format": "uri" },
        "useWorkloadIdentity": { "type": "boolean" },
        "serviceAccountEmail": { "type": "string", "format": "email" }
      }
    },
    "model": {
      "type": "string",
      "pattern": "^claude-.+@vertex$"
    },
    "temperature": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "maxTokens": {
      "type": "integer",
      "minimum": 1,
      "maximum": 200000
    }
  }
}
```

### Support

For issues specific to:

- **Claude Code CLI:** [GitHub Issues](https://github.com/anthropics/claude-code/issues)
- **VertexAI Integration:** [Google Cloud Support](https://cloud.google.com/support)
- **IAM/Authentication:** [Google Cloud IAM Documentation](https://cloud.google.com/iam/docs)

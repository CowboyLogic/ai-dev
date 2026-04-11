# OpenCode — Enterprise

> Source: <https://opencode.ai/docs/enterprise/>  
> Last updated: April 10, 2026

OpenCode Enterprise is for organizations that want to ensure code and data never leave their infrastructure. It uses a centralized config integrating with your SSO and internal AI gateway.

**OpenCode does not store any of your code or context data.**

To get started:

1. Do a trial internally with your team
2. [Contact us](mailto:contact@anoma.ly) to discuss pricing and implementation

---

## Trial

OpenCode is open source and does not store code or context data, so developers can simply get started and carry out a trial immediately.

### Data Handling

All processing happens locally or through direct API calls to your AI provider. The only exception is the optional `/share` feature.

**Sharing conversations:** If a user enables `/share`, conversation data is sent to and served from OpenCode's CDN edge network.

Disable sharing for your trial:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "share": "disabled"
}
```

See [share.md](../integrations/share.md) for more.

### Code Ownership

You own all code produced by OpenCode. No licensing restrictions or ownership claims.

---

## Pricing

Per-seat model. If you have your own LLM gateway, there is no token charge.

[Contact us](mailto:contact@anoma.ly) for pricing details.

---

## Deployment

After completing your trial, [contact us](mailto:contact@anoma.ly) to discuss implementation options.

### Central Config

OpenCode can be configured with a single central config for your entire organization, integrating with your SSO provider.

### SSO Integration

Through the central config, OpenCode can integrate with your organization's identity management system to obtain credentials for your internal AI gateway.

### Internal AI Gateway

Configure OpenCode to use only your internal AI gateway, disabling all other AI providers to ensure all requests go through your approved infrastructure.

### Self-Hosting

Self-hosted share pages are on the roadmap. [Contact us](mailto:contact@anoma.ly) if interested.

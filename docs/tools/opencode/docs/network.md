# OpenCode — Network

> Source: <https://opencode.ai/docs/network/>  
> Last updated: April 10, 2026

Configure proxies and custom certificates for enterprise network environments.

---

## Proxy

OpenCode respects standard proxy environment variables:

```bash
# HTTPS proxy (recommended)
export HTTPS_PROXY=https://proxy.example.com:8080

# HTTP proxy (if HTTPS not available)
export HTTP_PROXY=http://proxy.example.com:8080

# Bypass proxy for local server (required)
export NO_PROXY=localhost,127.0.0.1
```

> The TUI communicates with a local HTTP server. You **must** bypass the proxy for this connection to prevent routing loops.

Configure the server's port and hostname using [CLI flags](cli.md#global-flags).

### Authentication

Include credentials in the proxy URL:

```bash
export HTTPS_PROXY=http://username:password@proxy.example.com:8080
```

Avoid hardcoding passwords — use environment variables or secure credential storage.

For proxies requiring NTLM or Kerberos, consider using an LLM Gateway that supports your authentication method.

---

## Custom Certificates

If your enterprise uses custom CAs for HTTPS connections:

```bash
export NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem
```

This applies to both proxy connections and direct API access.

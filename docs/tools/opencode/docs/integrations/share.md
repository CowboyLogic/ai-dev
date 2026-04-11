# OpenCode — Share

> Source: <https://opencode.ai/docs/share/>  
> Last updated: April 10, 2026

OpenCode's share feature creates public links to conversations for collaboration or getting help.

> **Warning:** Shared conversations are publicly accessible to anyone with the link.

---

## How It Works

When you share a conversation, OpenCode:

1. Creates a unique public URL: `opncd.ai/s/<share-id>`
2. Syncs your conversation history to OpenCode's servers
3. Makes the conversation accessible via the link

---

## Sharing Modes

### Manual (default)

Sessions are not shared automatically. Share on demand:

```
/share
```

A unique URL is generated and copied to your clipboard.

To explicitly configure manual mode:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "share": "manual"
}
```

### Auto-share

Every new conversation is automatically shared:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "share": "auto"
}
```

### Disabled

Disable sharing entirely:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "share": "disabled"
}
```

Add to your project's `opencode.json` and commit to Git to enforce this across your team.

---

## Un-sharing

Remove a conversation from public access:

```
/unshare
```

This removes the share link and **deletes the conversation data** from OpenCode's servers.

---

## Privacy

### Data Retention

Shared conversations remain accessible until you explicitly unshare them, including:

- Full conversation history
- All messages and responses
- Session metadata

### Recommendations

- Only share conversations without sensitive information
- Review content before sharing
- Unshare when collaboration is complete
- Avoid sharing conversations with proprietary code or confidential data
- For sensitive projects, disable sharing entirely

---

## For Enterprises

For enterprise deployments, sharing can be:

- Disabled entirely for security compliance
- Restricted to SSO-authenticated users only
- Self-hosted on your own infrastructure

See [enterprise.md](../configuration/enterprise.md) for more.

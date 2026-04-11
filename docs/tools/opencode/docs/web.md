# OpenCode — Web Interface

> Source: <https://opencode.ai/docs/web/>  
> Last updated: April 10, 2026

OpenCode can run as a web application in your browser, providing the same AI coding experience without a dedicated terminal.

---

## Getting Started

```bash
opencode web
```

Starts a local server on `127.0.0.1` with a random available port and opens OpenCode in your default browser.

> If `OPENCODE_SERVER_PASSWORD` is not set, the server is unsecured. Fine for local use; set it for network access.

> On Windows, run from [WSL](windows-wsl.md) for proper file system access and terminal integration.

---

## Configuration

### Port

```bash
opencode web --port 4096
```

### Hostname

Bind to all interfaces (for network access):

```bash
opencode web --hostname 0.0.0.0
```

OpenCode displays both local and network addresses:

```
Local access:   http://localhost:4096
Network access: http://192.168.1.100:4096
```

### mDNS Discovery

Make the server discoverable on the local network:

```bash
opencode web --mdns
```

Advertises the server as `opencode.local`. Customize the domain:

```bash
opencode web --mdns --mdns-domain myproject.local
```

### CORS

Allow additional origins (for custom frontends):

```bash
opencode web --cors https://example.com
```

### Authentication

Protect access with HTTP basic auth:

```bash
OPENCODE_SERVER_PASSWORD=secret opencode web
```

Username defaults to `opencode`; override with `OPENCODE_SERVER_USERNAME`.

---

## Config File

Configure server settings in `opencode.json`:

```jsonc
{
  "server": {
    "port": 4096,
    "hostname": "0.0.0.0",
    "mdns": true,
    "cors": ["https://example.com"]
  }
}
```

Command-line flags take precedence over config file settings.

---

## Using the Web Interface

- **Sessions:** View and manage sessions from the homepage; start new ones
- **Server Status:** Click "See Servers" to view connected servers and status

---

## Attaching a Terminal

Attach a TUI to a running web server so you can use both simultaneously:

```bash
# Start the web server
opencode web --port 4096

# In another terminal, attach the TUI
opencode attach http://localhost:4096
```

Both interfaces share the same sessions and state.

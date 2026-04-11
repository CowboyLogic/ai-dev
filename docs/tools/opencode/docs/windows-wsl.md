# OpenCode — Windows (WSL)

> Source: <https://opencode.ai/docs/windows-wsl/>  
> Last updated: April 10, 2026

While OpenCode can run directly on Windows, using [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install) is recommended for better file system performance, full terminal support, and tool compatibility.

---

## Setup

**Step 1: Install WSL**

Follow the [official Microsoft guide](https://learn.microsoft.com/en-us/windows/wsl/install).

**Step 2: Install OpenCode in WSL**

Open your WSL terminal:

```bash
curl -fsSL https://opencode.ai/install | bash
```

**Step 3: Use OpenCode**

Navigate to your project (Windows files are accessible via `/mnt/c/`, `/mnt/d/`, etc.):

```bash
cd /mnt/c/Users/YourName/project
opencode
```

---

## Desktop App + WSL Server

Run the server in WSL and connect the Desktop app to it:

**In WSL:**

```bash
# Use --hostname 0.0.0.0 to allow external connections
opencode serve --hostname 0.0.0.0 --port 4096

# Secure with a password when using 0.0.0.0
OPENCODE_SERVER_PASSWORD=your-password opencode serve --hostname 0.0.0.0
```

**In the Desktop app:** Connect to `http://localhost:4096`

If `localhost` doesn't work, use the WSL IP address: run `hostname -I` in WSL and connect to `http://<wsl-ip>:4096`.

---

## Web Client + WSL

Run `opencode web` from WSL for the best browser experience:

```bash
opencode web --hostname 0.0.0.0
```

Access from Windows browser at `http://localhost:<port>` (OpenCode prints the URL).

---

## Accessing Windows Files

All Windows drives are accessible via `/mnt/`:

| Windows | WSL path |
|---------|----------|
| `C:\` | `/mnt/c/` |
| `D:\` | `/mnt/d/` |

Example:

```bash
cd /mnt/c/Users/YourName/Documents/project
opencode
```

For the smoothest experience, clone repos into the WSL filesystem (e.g., `~/code/`) and run OpenCode there.

---

## Tips

- Keep OpenCode running in WSL for projects stored on Windows drives — file access is seamless
- Use VS Code's [WSL extension](https://code.visualstudio.com/docs/remote/wsl) alongside OpenCode for an integrated workflow
- OpenCode config and sessions are stored in the WSL environment at `~/.local/share/opencode/`

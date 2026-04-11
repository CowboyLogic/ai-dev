# OpenCode — Troubleshooting

> Source: <https://opencode.ai/docs/troubleshooting/>  
> Last updated: April 10, 2026

---

## Logs

Log files are written to:

- **macOS/Linux:** `~/.local/share/opencode/log/`
- **Windows:** Press `WIN+R` and paste `%USERPROFILE%\.local\share\opencode\log`

Files are named with timestamps (e.g., `2025-01-09T123456.log`). The most recent 10 log files are kept.

Increase log verbosity:

```
opencode --log-level DEBUG
```

---

## Storage

OpenCode stores data at:

- **macOS/Linux:** `~/.local/share/opencode/`
- **Windows:** `%USERPROFILE%\.local\share\opencode`

Contents:

| Path | Description |
|------|-------------|
| `auth.json` | API keys, OAuth tokens |
| `log/` | Application logs |
| `project/` | Session and message data |

---

## Common Issues

### OpenCode Won't Start

- Check the logs for error messages
- Run with `--print-logs` to see output in the terminal
- Ensure you have the latest version: `opencode upgrade`

### Authentication Issues

- Re-authenticate with `/connect` in the TUI
- Check that your API keys are valid
- Ensure your network allows connections to the provider's API

### Model Not Available

- Check that you've authenticated with the provider
- Verify the model name format: `<providerId>/<modelId>` (e.g., `openai/gpt-4.1`)
- Run `opencode models` to see available models
- Some models may require specific access or subscriptions

### ProviderInitError

1. Verify your provider setup following the providers guide
2. Clear stored configuration:
   - **macOS/Linux:** `rm -rf ~/.local/share/opencode`
   - **Windows:** Delete `%USERPROFILE%\.local\share\opencode`
3. Re-authenticate with `/connect`

### AI_APICallError / Provider Package Issues

Clear the provider package cache (forces reinstall of latest versions):

- **macOS/Linux:** `rm -rf ~/.cache/opencode`
- **Windows:** Delete `%USERPROFILE%\.cache\opencode`

Then restart OpenCode.

### Copy/Paste Not Working on Linux

Install clipboard utilities:

```bash
# X11
apt install -y xclip
# or
apt install -y xsel

# Wayland
apt install -y wl-clipboard

# Headless
apt install -y xvfb
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
export DISPLAY=:99.0
```

---

## Desktop App Issues

The Desktop app runs the `opencode-cli` sidecar in the background. Most issues are caused by a misbehaving plugin, corrupted cache, or bad server setting.

### Quick Checks

- Fully quit and relaunch the app
- If the app shows an error screen, click **Restart** and copy the error details
- **macOS only:** OpenCode menu → Reload Webview (for blank/frozen UI)

### Disable Plugins

**In config:** Remove or empty the `plugin` key in your config file:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": []
}
```

**Config file locations:**

- macOS/Linux: `~/.config/opencode/opencode.jsonc`
- Windows: `%USERPROFILE%\.config\opencode\opencode.jsonc`

**Plugin directories:** Temporarily rename to disable:

- Global: `~/.config/opencode/plugins/`
- Project: `<project>/.opencode/plugins/`

Re-enable plugins one at a time to find the culprit.

### Clear the Cache

1. Quit OpenCode Desktop completely
2. Delete the cache directory:
   - **macOS:** `~/.cache/opencode`
   - **Linux:** `~/.cache/opencode`
   - **Windows:** `%USERPROFILE%\.cache\opencode`
3. Restart OpenCode Desktop

### Fix Server Connection Issues

If you see "Connection Failed" or the app stalls at the splash screen:

1. **Clear the default server URL:** From Home screen, click the server name → Server picker → Default server → Clear
2. **Remove `server.port`/`server.hostname`** from `opencode.json` and restart
3. **Check `OPENCODE_PORT`:** If set, unset it or pick a free port

### Linux: Wayland / X11 Issues

- Try launching with `OC_ALLOW_WAYLAND=1`
- If that fails, try an X11 session instead

### Windows: WebView2 Runtime

OpenCode Desktop requires the Microsoft Edge WebView2 Runtime. Install/update WebView2 if the app opens to a blank window.

### Windows: General Performance

Use [WSL](configuration/windows-wsl.md) for better file system performance, full terminal support, and tool compatibility.

### Notifications Not Showing

Notifications only show when:
- Notifications are enabled for OpenCode in OS settings, **and**
- The app window is not focused

### Reset Desktop App Storage (Last Resort)

1. Quit OpenCode Desktop
2. Delete these files in the app data directory:
   - `opencode.settings.dat` — default server URL
   - `opencode.global.dat` and `opencode.workspace.*.dat` — UI state
3. **Find the directory:**
   - macOS: Finder → `Cmd+Shift+G` → `~/Library/Application Support`
   - Linux: search under `~/.local/share`
   - Windows: `WIN+R` → `%APPDATA%`

---

## Getting Help

- **GitHub Issues:** [github.com/anomalyco/opencode/issues](https://github.com/anomalyco/opencode/issues)
- **Discord:** [opencode.ai/discord](https://opencode.ai/discord)

#!/usr/bin/env python3
"""
show-settings.py — Pretty-print Claude Code settings across scopes (read-only).
Usage: python show-settings.py [--json] [--settings PATH]

Shows managed settings (if present), user settings ($CLAUDE_CONFIG_DIR/settings.json
when set, else ~/.claude/settings.json, or PATH), MCP servers from
~/.claude.json (user scope and local scope for the current directory), and the
current directory's .claude/settings.json and .claude/settings.local.json.
"""
import json
import os
import sys
from pathlib import Path

# CLAUDE_CONFIG_DIR relocates the user configuration home (settings.json, history,
# plugins). The docs do not say where .claude.json goes when it is set, so prefer a
# copy inside CLAUDE_CONFIG_DIR only when one exists.
_CONFIG_DIR = os.environ.get("CLAUDE_CONFIG_DIR")
CONFIG_HOME = Path(_CONFIG_DIR).expanduser() if _CONFIG_DIR else Path.home() / ".claude"
SETTINGS_PATH = CONFIG_HOME / "settings.json"
CLAUDE_JSON_PATH = Path.home() / ".claude.json"
if _CONFIG_DIR and (CONFIG_HOME / ".claude.json").exists():
    CLAUDE_JSON_PATH = CONFIG_HOME / ".claude.json"
MANAGED_DIRS = {
    "darwin": Path("/Library/Application Support/ClaudeCode"),
    "linux": Path("/etc/claude-code"),
    "win32": Path("C:/Program Files/ClaudeCode"),
}

FIELD_NOTES = {
    "permissions": "Tool access rules (allow/deny/ask) and permission mode",
    "hooks": "Handlers (command/http/mcp_tool/prompt/agent) run on lifecycle events",
    "autoUpdatesChannel": '"latest" (default) or "stable" (~1 week old, skips major regressions)',
    "model": "Model new sessions start with",
    "effortLevel": "Default effort for models with no saved level: low | medium | high | xhigh",
    "modelSettings": "Per-model effortLevel / maxEffortLevel (what /effort writes)",
    "maxEffortLevel": "Effort cap: low | medium | high | xhigh | max (no cap)",
    "language": "Claude response language",
    "env": "Environment variables injected each session",
    "defaultMode": "Permission mode: default (manual) | acceptEdits | plan | auto | dontAsk | bypassPermissions",
    "disableAllHooks": "Emergency hook kill switch",
    "autoMode": "Auto mode classifier configuration",
    "sandbox": "OS-level Bash/PowerShell isolation (macOS/Linux/WSL2 only)",
    "mcpServers": "NOTE: MCP servers live in ~/.claude.json, not settings.json",
    "attribution": "Git commit/PR attribution text",
    "cleanupPeriodDays": "Delete session files older than N days (default: 30)",
    "outputStyle": "Output style for system prompt",
    "alwaysThinkingEnabled": "Enable extended thinking by default",
    "showThinkingSummaries": "Show thinking block summaries",
    "tui": "Terminal UI: default | fullscreen",
    "viewMode": "Transcript view: default | verbose | focus",
    "statusLine": "Custom status line command",
    "enabledPlugins": "Plugins enabled/disabled by plugin@marketplace",
    "voice": "Voice dictation: enabled, mode (hold | tap), autoSubmit (hold only)",
    "voiceEnabled": "DEPRECATED: use voice.enabled",
    "includeCoAuthoredBy": "DEPRECATED: use attribution",
    "disableArtifact": "DEPRECATED: use enableArtifact: false",
    "keybindingFlavor": "DEPRECATED: no effect since v2.1.261",
    "taskOutputMaxChars": "REMOVED in v2.1.277: no effect",
}

def load_json(path):
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: {path} has invalid JSON: {e}", file=sys.stderr)
        return None

def print_settings(data, path, label):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  {path}")
    print(f"{'='*60}")

    if data is None:
        print("  (file not found)")
        return
    if not data:
        print("  (empty — no settings configured)")
        return

    if "--json" in sys.argv:
        print(json.dumps(data, indent=2))
        return

    for key, value in data.items():
        note = FIELD_NOTES.get(key, "")
        note_str = f"  # {note}" if note else ""

        if isinstance(value, dict):
            print(f"\n  [{key}]{note_str}")
            if key == "permissions":
                for pkey in ["defaultMode", "allow", "deny", "ask", "additionalDirectories", "blockReadsOutsideWorkingDirectories", "disableBypassPermissionsMode", "disableAutoMode"]:
                    if pkey in value:
                        v = value[pkey]
                        if isinstance(v, list):
                            print(f"    {pkey}: ({len(v)} rules)")
                            for rule in v[:5]:
                                print(f"      - {rule}")
                            if len(v) > 5:
                                print(f"      ... and {len(v)-5} more")
                        else:
                            print(f"    {pkey}: {v}")
            elif key == "hooks":
                for event, handlers in value.items():
                    print(f"    {event}: {len(handlers)} handler group(s)")
            elif key == "env":
                for ekey, evalue in value.items():
                    masked = evalue[:4] + "..." if len(str(evalue)) > 8 and any(s in ekey.upper() for s in ["KEY", "TOKEN", "SECRET", "PASSWORD", "PASS"]) else evalue
                    print(f"    {ekey}={masked}")
            else:
                preview = json.dumps(value)
                if len(preview) > 80:
                    preview = preview[:77] + "..."
                print(f"    {preview}")
        elif isinstance(value, list):
            print(f"\n  {key}: [{len(value)} items]{note_str}")
            for item in value[:3]:
                print(f"    - {item}")
            if len(value) > 3:
                print(f"    ... and {len(value)-3} more")
        else:
            print(f"\n  {key}: {value}{note_str}")

def main():
    settings_path = SETTINGS_PATH
    if "--settings" in sys.argv:
        idx = sys.argv.index("--settings")
        if idx + 1 >= len(sys.argv):
            print("ERROR: --settings requires a path", file=sys.stderr)
            return 2
        settings_path = Path(sys.argv[idx + 1]).expanduser()

    managed_dir = MANAGED_DIRS.get(sys.platform)
    if managed_dir:
        managed_path = managed_dir / "managed-settings.json"
        if managed_path.exists():
            print_settings(load_json(managed_path), managed_path, "MANAGED SETTINGS (highest precedence)")
        dropin_dir = managed_dir / "managed-settings.d"
        if dropin_dir.is_dir():
            for dropin in sorted(dropin_dir.glob("*.json")):
                print_settings(load_json(dropin), dropin, "MANAGED DROP-IN")

    settings = load_json(settings_path)
    print_settings(settings, settings_path, f"USER SETTINGS ({settings_path})")

    # Show MCP hint from ~/.claude.json
    claude_json = load_json(CLAUDE_JSON_PATH) or {}
    local_servers = (claude_json.get("projects", {}).get(str(Path.cwd()), {}) or {}).get("mcpServers", {})
    for label, servers in (("user scope", claude_json.get("mcpServers", {})),
                           (f"local scope, {Path.cwd()}", local_servers)):
        if not servers:
            continue
        print(f"\n{'='*60}")
        print(f"  MCP SERVERS ({CLAUDE_JSON_PATH}, {label})")
        print(f"{'='*60}")
        for name, config in servers.items():
            transport = config.get("type", "stdio")
            cmd = config.get("command", config.get("url", "?"))
            print(f"  - {name} ({transport}): {cmd}")
    project_mcp = load_json(Path.cwd() / ".mcp.json")
    if project_mcp and project_mcp.get("mcpServers"):
        print(f"\n{'='*60}")
        print(f"  MCP SERVERS (.mcp.json, project scope)")
        print(f"{'='*60}")
        for name, config in project_mcp["mcpServers"].items():
            print(f"  - {name} ({config.get('type', 'stdio')}): {config.get('command', config.get('url', '?'))}")

    # Check for project settings (only if different from user settings)
    project_settings_path = Path.cwd() / ".claude" / "settings.json"
    if project_settings_path.exists() and project_settings_path.resolve() != settings_path.resolve():
        project_settings = load_json(project_settings_path)
        print_settings(project_settings, project_settings_path, "PROJECT SETTINGS (.claude/settings.json)")

    local_settings_path = Path.cwd() / ".claude" / "settings.local.json"
    if local_settings_path.exists() and local_settings_path.resolve() != settings_path.resolve():
        local_settings = load_json(local_settings_path)
        print_settings(local_settings, local_settings_path, "LOCAL SETTINGS (.claude/settings.local.json)")

    print()

if __name__ == "__main__":
    sys.exit(main())

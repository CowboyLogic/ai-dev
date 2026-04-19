#!/usr/bin/env python3
"""
show-settings.py — Pretty-print ~/.claude/settings.json with annotations.
Usage: python show-settings.py [--json]
"""
import json
import os
import sys
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
CLAUDE_JSON_PATH = Path.home() / ".claude.json"

FIELD_NOTES = {
    "permissions": "Tool access rules (allow/deny/ask) and permission mode",
    "hooks": "Shell commands triggered by lifecycle events",
    "autoUpdatesChannel": '"latest" (default) or "stable" (1 week behind, safer)',
    "model": "Default model override",
    "effortLevel": "Thinking effort: low | medium | high | xhigh",
    "language": "Claude response language",
    "env": "Environment variables injected each session",
    "defaultMode": "Permission mode: default | acceptEdits | plan | auto | dontAsk | bypassPermissions",
    "disableAllHooks": "Emergency hook kill switch",
    "autoMode": "Auto mode classifier configuration",
    "sandbox": "OS-level bash isolation (macOS/Linux/WSL2 only)",
    "mcpServers": "NOTE: MCP servers live in ~/.claude.json, not settings.json",
    "attribution": "Git commit/PR attribution text",
    "cleanupPeriodDays": "Delete session files older than N days (default: 30)",
    "outputStyle": "Output style for system prompt",
    "alwaysThinkingEnabled": "Enable extended thinking by default",
    "showThinkingSummaries": "Show thinking block summaries",
    "tui": "Terminal UI: default | fullscreen",
    "viewMode": "Transcript view: default | verbose | focus",
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
                for pkey in ["defaultMode", "allow", "deny", "ask", "additionalDirectories"]:
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
    settings = load_json(SETTINGS_PATH)
    print_settings(settings, SETTINGS_PATH, "USER SETTINGS (~/.claude/settings.json)")

    # Show MCP hint from ~/.claude.json
    claude_json = load_json(CLAUDE_JSON_PATH)
    if claude_json and "mcpServers" in claude_json:
        servers = claude_json["mcpServers"]
        print(f"\n{'='*60}")
        print(f"  MCP SERVERS (~/.claude.json)")
        print(f"{'='*60}")
        for name, config in servers.items():
            transport = config.get("type", "stdio")
            cmd = config.get("command", config.get("url", "?"))
            print(f"  - {name} ({transport}): {cmd}")

    # Check for project settings (only if different from user settings)
    project_settings_path = Path.cwd() / ".claude" / "settings.json"
    if project_settings_path.exists() and project_settings_path.resolve() != SETTINGS_PATH.resolve():
        project_settings = load_json(project_settings_path)
        print_settings(project_settings, project_settings_path, "PROJECT SETTINGS (.claude/settings.json)")

    local_settings_path = Path.cwd() / ".claude" / "settings.local.json"
    if local_settings_path.exists() and local_settings_path.resolve() != SETTINGS_PATH.resolve():
        local_settings = load_json(local_settings_path)
        print_settings(local_settings, local_settings_path, "LOCAL SETTINGS (.claude/settings.local.json)")

    print()

if __name__ == "__main__":
    main()

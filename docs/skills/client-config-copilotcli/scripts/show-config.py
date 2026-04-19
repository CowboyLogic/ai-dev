#!/usr/bin/env python3
"""
show-config.py — Display all GitHub Copilot CLI config files with annotations.
Usage: python show-config.py [--json]
"""
import json
import os
import sys
from pathlib import Path

COPILOT_HOME = Path(os.environ.get("COPILOT_HOME", Path.home() / ".copilot"))
CONFIG_FILE = COPILOT_HOME / "config.json"
MCP_FILE = COPILOT_HOME / "mcp-config.json"
SKILLS_DIR = COPILOT_HOME / "skills"
INSTRUCTIONS_FILE = COPILOT_HOME / "copilot-instructions.md"

BYOK_VARS = [
    "COPILOT_PROVIDER_BASE_URL",
    "COPILOT_PROVIDER_TYPE",
    "COPILOT_PROVIDER_API_KEY",
    "COPILOT_MODEL",
    "COPILOT_OFFLINE",
]
AUTH_VARS = [
    "COPILOT_GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_TOKEN",
]

def load_json(path):
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"  ERROR: invalid JSON in {path}: {e}")
        return {}

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def main():
    as_json = "--json" in sys.argv
    print(f"Copilot CLI config directory: {COPILOT_HOME}")

    # --- config.json ---
    section(f"CORE CONFIG ({CONFIG_FILE})")
    config = load_json(CONFIG_FILE)
    if config is None:
        print("  (file not found — no trusted folders configured yet)")
    elif not config:
        print("  (empty)")
    else:
        if as_json:
            print(json.dumps(config, indent=2))
        else:
            trusted = config.get("trusted_folders", [])
            print(f"  trusted_folders: ({len(trusted)} entries)")
            for folder in trusted:
                print(f"    - {folder}")
            for key, val in config.items():
                if key != "trusted_folders":
                    print(f"  {key}: {val}")

    # --- mcp-config.json ---
    section(f"MCP SERVERS ({MCP_FILE})")
    mcp = load_json(MCP_FILE)
    if mcp is None:
        print("  (file not found — no MCP servers configured)")
    else:
        servers = mcp.get("mcpServers", {})
        if not servers:
            print("  (no servers configured)")
        else:
            print(f"  {len(servers)} server(s):")
            for name, cfg in servers.items():
                transport = cfg.get("type", "local")
                endpoint = cfg.get("command", cfg.get("url", "?"))
                tools = cfg.get("tools", [])
                tool_str = "*" if tools == ["*"] else ", ".join(tools[:3])
                print(f"    [{name}]  type={transport}  endpoint={endpoint}")
                print(f"      tools: {tool_str}")
                if "env" in cfg:
                    print(f"      env vars: {list(cfg['env'].keys())}")

    # --- skills ---
    section(f"PERSONAL SKILLS ({SKILLS_DIR})")
    if not SKILLS_DIR.exists():
        print("  (directory not found — no personal skills)")
    else:
        skill_dirs = [d for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        if not skill_dirs:
            print("  (no skills found)")
        else:
            for skill_dir in sorted(skill_dirs):
                skill_file = skill_dir / "SKILL.md"
                # Read name and description from frontmatter
                try:
                    content = skill_file.read_text(encoding="utf-8")
                    name = description = None
                    if content.startswith("---"):
                        end = content.find("---", 3)
                        if end != -1:
                            fm = content[3:end]
                            for line in fm.splitlines():
                                if line.startswith("name:"):
                                    name = line.split(":", 1)[1].strip()
                                elif line.startswith("description:"):
                                    description = line.split(":", 1)[1].strip()[:60]
                    print(f"    [{skill_dir.name}]  name={name or '?'}  desc={description or '?'}...")
                except Exception:
                    print(f"    [{skill_dir.name}]  (could not read SKILL.md)")

    # --- custom instructions ---
    section(f"PERSONAL INSTRUCTIONS ({INSTRUCTIONS_FILE})")
    if INSTRUCTIONS_FILE.exists():
        size = INSTRUCTIONS_FILE.stat().st_size
        print(f"  Found ({size} bytes)")
        if not as_json:
            preview = INSTRUCTIONS_FILE.read_text(encoding="utf-8")[:200].strip()
            print(f"  Preview: {preview[:120]}...")
    else:
        print("  (file not found)")

    # --- project config files ---
    cwd = Path.cwd()
    project_files = [
        (cwd / ".github" / "copilot-instructions.md", "Project instructions"),
        (cwd / "AGENTS.md", "AGENTS.md (project-wide)"),
        (cwd / ".github" / "hooks" / "hooks.json", "Hooks"),
        (cwd / ".github" / "skills", "Project skills dir"),
    ]
    found_any = any(f.exists() for f, _ in project_files)
    if found_any:
        section(f"PROJECT CONFIG (in {cwd})")
        for path, label in project_files:
            if path.exists():
                if path.is_dir():
                    items = list(path.iterdir())
                    print(f"  {label}: {len(items)} item(s) in {path}")
                else:
                    size = path.stat().st_size
                    print(f"  {label}: {path} ({size} bytes)")

    # --- env vars ---
    section("ENVIRONMENT VARIABLES")
    print("  Auth (checked in order):")
    found_auth = False
    for var in AUTH_VARS:
        val = os.environ.get(var)
        if val:
            print(f"    {var}={val[:8]}... (set)")
            found_auth = True
            break
    if not found_auth:
        print("    (none set — using keychain or gh auth)")

    print("  BYOK / custom provider:")
    any_byok = False
    for var in BYOK_VARS:
        val = os.environ.get(var)
        if val:
            masked = val[:8] + "..." if "KEY" in var and len(val) > 8 else val
            print(f"    {var}={masked}")
            any_byok = True
    if not any_byok:
        print("    (none set — using GitHub-hosted models)")

    print()

if __name__ == "__main__":
    main()

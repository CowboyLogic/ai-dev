#!/usr/bin/env python3
"""Display all Gemini CLI configuration files with annotations."""

import json
import os
from pathlib import Path

# Config locations
GEMINI_HOME = Path(os.environ.get("GEMINI_CLI_HOME", Path.home() / ".gemini"))
USER_SETTINGS = GEMINI_HOME / "settings.json"
USER_GEMINI_MD = GEMINI_HOME / "GEMINI.md"
TRUSTED_FOLDERS = GEMINI_HOME / "trustedFolders.json"
USER_COMMANDS = GEMINI_HOME / "commands"
PROJECT_DIR = Path.cwd() / ".gemini"
PROJECT_SETTINGS = PROJECT_DIR / "settings.json"
PROJECT_GEMINI_MD = Path.cwd() / "GEMINI.md"
PROJECT_COMMANDS = PROJECT_DIR / "commands"

BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")


def note(msg):
    print(f"  {DIM}{msg}{RESET}")


def show_json_file(path, label):
    if not path.exists():
        note(f"{label}: not found ({path})")
        return
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        print(f"\n{GREEN}{label}{RESET} ({path})")
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError as e:
        print(f"\n{YELLOW}{label}{RESET} ({path}) — parse error: {e}")
        with open(path, encoding="utf-8") as f:
            print(f.read())


def show_text_preview(path, label, max_lines=15):
    if not path.exists():
        note(f"{label}: not found ({path})")
        return
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    print(f"\n{GREEN}{label}{RESET} ({path}) — {len(lines)} lines")
    preview = "".join(lines[:max_lines])
    print(preview, end="")
    if len(lines) > max_lines:
        print(f"\n  {DIM}... ({len(lines) - max_lines} more lines){RESET}")


def show_commands_dir(directory, label):
    if not directory.exists():
        note(f"{label}: not found ({directory})")
        return
    files = sorted(directory.rglob("*.toml"))
    if not files:
        note(f"{label}: empty ({directory})")
        return
    print(f"\n{GREEN}{label}{RESET} ({directory})")
    for f in files:
        rel = f.relative_to(directory)
        parts = list(rel.parts)
        parts[-1] = parts[-1].replace(".toml", "")
        cmd = ":".join(parts)
        print(f"  /{cmd}  {DIM}({f.name}){RESET}")


def show_env_vars():
    header("Environment Variables")
    auth_vars = [
        ("GEMINI_API_KEY", "Gemini API authentication"),
        ("GEMINI_MODEL", "Default model override"),
        ("GEMINI_CLI_HOME", "Config root directory override"),
        ("GOOGLE_API_KEY", "Google Cloud API"),
        ("GOOGLE_CLOUD_PROJECT", "GCP project for Vertex AI"),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Path to GCP credentials JSON"),
        ("GOOGLE_GENAI_API_VERSION", "API version override"),
    ]
    found = False
    for var, desc in auth_vars:
        val = os.environ.get(var)
        if val:
            masked = val[:4] + "..." + val[-2:] if len(val) > 8 else "***"
            print(f"  {var}={masked}  {DIM}({desc}){RESET}")
            found = True
    if not found:
        note("No Gemini CLI env vars set")


def main():
    print(f"{BOLD}Gemini CLI Configuration Summary{RESET}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Gemini home: {GEMINI_HOME}")

    # User settings
    header("User Settings (~/.gemini/settings.json)")
    show_json_file(USER_SETTINGS, "settings.json")

    # Project settings
    header("Project Settings (.gemini/settings.json)")
    if PROJECT_SETTINGS.resolve() == USER_SETTINGS.resolve():
        note("Same as user settings (running from home directory)")
    else:
        show_json_file(PROJECT_SETTINGS, "settings.json")

    # GEMINI.md context files
    header("Context Files (GEMINI.md)")
    show_text_preview(USER_GEMINI_MD, "~/.gemini/GEMINI.md")
    show_text_preview(PROJECT_GEMINI_MD, "GEMINI.md (project root)")

    # Trusted folders
    header("Trusted Folders")
    show_json_file(TRUSTED_FOLDERS, "trustedFolders.json")

    # Custom commands
    header("Custom Commands")
    show_commands_dir(USER_COMMANDS, "Global (~/.gemini/commands/)")
    show_commands_dir(PROJECT_COMMANDS, "Project (.gemini/commands/)")

    # Extensions
    extensions_dir = GEMINI_HOME / "extensions"
    project_extensions_dir = PROJECT_DIR / "extensions"
    if extensions_dir.exists() or project_extensions_dir.exists():
        header("Extensions")
        for ext_dir in [extensions_dir, project_extensions_dir]:
            if ext_dir.exists():
                dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                if dirs:
                    label = "Global" if ext_dir == extensions_dir else "Project"
                    print(f"  {label}: {', '.join(d.name for d in dirs)}")

    # Environment variables
    show_env_vars()

    print()


if __name__ == "__main__":
    main()

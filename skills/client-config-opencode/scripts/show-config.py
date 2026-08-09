#!/usr/bin/env python3
"""Display all opencode configuration files with annotations."""

import json
import os
import sys
from pathlib import Path

# Config locations
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "opencode"


def find_project_root(start):
    """Find the nearest OpenCode config or Git repository from the working directory."""
    current = start.resolve()
    for directory in (current, *current.parents):
        if (directory / "opencode.json").exists() or (directory / ".git").exists():
            return directory
    return current


PROJECT_ROOT = find_project_root(Path.cwd())
PROJECT_DIR = PROJECT_ROOT / ".opencode"
OPENCODE_JSON = CONFIG_DIR / "opencode.json"
PROJECT_OPENCODE_JSON = PROJECT_ROOT / "opencode.json"
TUI_JSON = Path(os.environ.get("OPENCODE_TUI_CONFIG", CONFIG_DIR / "tui.json")).expanduser()
PROJECT_TUI_JSON = PROJECT_ROOT / "tui.json"
AGENTS_DIR = CONFIG_DIR / "agents"
PROJECT_AGENTS_DIR = PROJECT_DIR / "agents"
COMMANDS_DIR = CONFIG_DIR / "commands"
PROJECT_COMMANDS_DIR = PROJECT_DIR / "commands"
CONFIG_OVERRIDE = os.environ.get("OPENCODE_CONFIG")
CONFIG_CONTENT_OVERRIDE = os.environ.get("OPENCODE_CONFIG_CONTENT")
CONFIG_DIRECTORY_OVERRIDE = os.environ.get("OPENCODE_CONFIG_DIR")

BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

def header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")

def subheader(title):
    print(f"\n{BOLD}{title}{RESET}")

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

def show_json_content(content, label):
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"\n{YELLOW}{label}{RESET} — parse error: {e}")
        return
    print(f"\n{GREEN}{label}{RESET}")
    print(json.dumps(data, indent=2))

def show_md_file(path, label):
    if not path.exists():
        return
    print(f"\n  {GREEN}{label}{RESET}: {path}")
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    # Show frontmatter + first few lines
    preview = "".join(lines[:10])
    if len(lines) > 10:
        preview += f"  {DIM}... ({len(lines)} lines total){RESET}\n"
    print(preview, end="")

def show_directory_contents(directory, label, extension=".md"):
    if not directory.exists():
        note(f"{label}: directory not found ({directory})")
        return
    files = sorted(directory.glob(f"*{extension}"))
    if not files:
        note(f"{label}: empty ({directory})")
        return
    print(f"\n{GREEN}{label}{RESET} ({directory})")
    for f in files:
        show_md_file(f, f.stem)

def show_env_vars():
    header("Environment Variables")
    provider_vars = [
        ("ANTHROPIC_API_KEY", "Anthropic provider auth"),
        ("OPENAI_API_KEY", "OpenAI provider auth"),
        ("GOOGLE_API_KEY", "Google AI provider auth"),
        ("AWS_ACCESS_KEY_ID", "AWS Bedrock auth"),
        ("AWS_SECRET_ACCESS_KEY", "AWS Bedrock auth"),
        ("AWS_REGION", "AWS Bedrock region"),
        ("GOOGLE_CLOUD_PROJECT", "Vertex AI project"),
        ("GOOGLE_CLOUD_REGION", "Vertex AI region"),
        ("OPENAI_API_ENDPOINT", "Custom OpenAI-compatible endpoint"),
        ("OLLAMA_BASE_URL", "Ollama base URL override"),
    ]
    found = False
    for var, desc in provider_vars:
        val = os.environ.get(var)
        if val:
            masked = val[:4] + "..." + val[-2:] if len(val) > 8 else "***"
            print(f"  {var}={masked}  {DIM}({desc}){RESET}")
            found = True
    if not found:
        note("No provider env vars set")

def main():
    print(f"{BOLD}opencode Configuration Summary{RESET}")
    print(f"Working directory: {Path.cwd()}")

    # User-level config
    header(f"User Config ({OPENCODE_JSON})")
    show_json_file(OPENCODE_JSON, "opencode.json")

    # Project-level config
    header(f"Project Config ({PROJECT_OPENCODE_JSON})")
    if PROJECT_OPENCODE_JSON.resolve() == OPENCODE_JSON.resolve():
        note("Same as user config (running from home directory)")
    else:
        show_json_file(PROJECT_OPENCODE_JSON, "opencode.json")

    # Environment-provided config overrides
    if CONFIG_OVERRIDE or CONFIG_CONTENT_OVERRIDE:
        header("Configuration Overrides")
        if CONFIG_OVERRIDE:
            show_json_file(Path(CONFIG_OVERRIDE).expanduser(), "OPENCODE_CONFIG")
        if CONFIG_CONTENT_OVERRIDE:
            show_json_content(CONFIG_CONTENT_OVERRIDE, "OPENCODE_CONFIG_CONTENT")

    # TUI config
    header(f"TUI Config ({TUI_JSON})")
    show_json_file(TUI_JSON, "tui.json")
    if PROJECT_TUI_JSON != TUI_JSON:
        header(f"Project TUI Config ({PROJECT_TUI_JSON})")
        show_json_file(PROJECT_TUI_JSON, "tui.json")

    # Agents
    header("Custom Agents")
    show_directory_contents(AGENTS_DIR, f"Global agents ({AGENTS_DIR})")
    if PROJECT_AGENTS_DIR.exists():
        show_directory_contents(PROJECT_AGENTS_DIR, "Project agents (.opencode/agents/)")

    # Custom commands
    header("Custom Commands")
    show_directory_contents(COMMANDS_DIR, f"Global commands ({COMMANDS_DIR})")
    if PROJECT_COMMANDS_DIR.exists():
        show_directory_contents(PROJECT_COMMANDS_DIR, "Project commands (.opencode/commands/)")

    if CONFIG_DIRECTORY_OVERRIDE:
        custom_dir = Path(CONFIG_DIRECTORY_OVERRIDE).expanduser()
        header(f"Custom Config Directory ({custom_dir})")
        show_directory_contents(custom_dir / "agents", "Custom agents")
        show_directory_contents(custom_dir / "commands", "Custom commands")

    # Themes
    themes_dir = CONFIG_DIR / "themes"
    project_themes_dir = PROJECT_DIR / "themes"
    if themes_dir.exists() or project_themes_dir.exists():
        header("Custom Themes")
        if themes_dir.exists():
            files = list(themes_dir.glob("*.json"))
            if files:
                print(f"  Global: {', '.join(f.stem for f in files)}")
        if project_themes_dir.exists():
            files = list(project_themes_dir.glob("*.json"))
            if files:
                print(f"  Project: {', '.join(f.stem for f in files)}")

    # Environment variables
    show_env_vars()

    print()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Display all opencode configuration files (V1 and V2) with annotations.

Parsed config is redacted before printing (secret-like keys at any depth, every
value under `env`/`headers`, token-shaped strings), and a file that fails to
parse is reported by position only, never echoed raw.
"""

import json
import os
import re
from pathlib import Path

# Config locations
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "opencode"
CONFIG_NAMES = ("opencode.json", "opencode.jsonc")


def find_project_root(start):
    """Find the nearest OpenCode config or Git repository from the working directory."""
    current = start.resolve()
    for directory in (current, *current.parents):
        if any((directory / name).exists() for name in CONFIG_NAMES):
            return directory
        if (directory / ".opencode").is_dir() or (directory / ".git").exists():
            return directory
    return current


PROJECT_ROOT = find_project_root(Path.cwd())
PROJECT_DIR = PROJECT_ROOT / ".opencode"
TUI_JSON = Path(os.environ.get("OPENCODE_TUI_CONFIG", CONFIG_DIR / "tui.json")).expanduser()
PROJECT_TUI_JSON = PROJECT_ROOT / "tui.json"
CLI_JSON = CONFIG_DIR / "cli.json"  # V2: global only, no project-local file
AGENTS_DIR = CONFIG_DIR / "agents"
PROJECT_AGENTS_DIR = PROJECT_DIR / "agents"
COMMANDS_DIR = CONFIG_DIR / "commands"
PROJECT_COMMANDS_DIR = PROJECT_DIR / "commands"
CONFIG_OVERRIDE = os.environ.get("OPENCODE_CONFIG")
CONFIG_CONTENT_OVERRIDE = os.environ.get("OPENCODE_CONFIG_CONTENT")
CONFIG_DIRECTORY_OVERRIDE = os.environ.get("OPENCODE_CONFIG_DIR")
CLI_CONTENT_OVERRIDE = os.environ.get("OPENCODE_CLI_CONFIG_CONTENT")

BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"

# Top-level keys that only appear in one format (see references/v2/migration.md).
V2_KEYS = {"permissions", "agents", "providers", "commands", "plugins", "snapshots", "media",
           "update", "warming", "websearch", "worktree"}
V1_KEYS = {"permission", "agent", "provider", "command", "plugin", "snapshot", "attachment",
           "autoupdate", "autoshare", "mode", "tools", "small_model", "enabled_providers",
           "disabled_providers", "logLevel", "server", "subagent_depth", "reference", "layout"}

SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "AUTH", "CREDENTIAL")
# Maps whose values are credentials regardless of key name (e.g. an "Authorization" header).
SECRET_MAPS = ("env", "environment", "headers")
TOKEN_VALUE = re.compile(r"^(gh[opsur]_|github_pat_|sk-|xox[abp]-|Bearer\s)", re.I)
# {env:NAME} and {file:path} are references, not secrets; show them as written.
REFERENCE_VALUE = re.compile(r"^\{(env|file):[^}]+\}$")


def header(title):
    print(f"\n{BOLD}{CYAN}=== {title} ==={RESET}")


def note(msg):
    print(f"  {DIM}{msg}{RESET}")


def strip_jsonc(text):
    """Remove // and /* */ comments (outside strings) and trailing commas."""
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 1
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
            out.append(ch)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        else:
            out.append(ch)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def redact(value, key="", in_secret_map=False):
    """Recursively mask secrets in parsed config before it is printed."""
    if isinstance(value, dict):
        return {
            k: redact(v, k, in_secret_map or k.lower() in SECRET_MAPS) for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v, key, in_secret_map) for v in value]
    if isinstance(value, str) and not REFERENCE_VALUE.match(value) and (
        in_secret_map
        or any(marker in key.upper() for marker in SECRET_MARKERS)
        or TOKEN_VALUE.match(value)
    ):
        return "***"
    return value


def parse_jsonc(text):
    return json.loads(strip_jsonc(text))


def detect_format(data):
    """Return ('V1' | 'V2' | 'mixed' | 'neutral', v1_markers, v2_markers) for an opencode config."""
    if not isinstance(data, dict):
        return "neutral", [], []
    v2 = sorted(k for k in data if k in V2_KEYS)
    v1 = sorted(k for k in data if k in V1_KEYS)
    mcp = data.get("mcp")
    if isinstance(mcp, dict):
        if isinstance(mcp.get("servers"), dict) or isinstance(mcp.get("timeout"), dict):
            v2.append("mcp.servers/mcp.timeout")
        if any(isinstance(v, dict) and "type" in v for k, v in mcp.items() if k not in ("servers", "timeout")):
            v1.append("mcp.<name>")
    compaction = data.get("compaction")
    if isinstance(compaction, dict):
        if "keep" in compaction or "buffer" in compaction:
            v2.append("compaction.keep/buffer")
        if {"reserved", "prune", "tail_turns", "preserve_recent_tokens"} & compaction.keys():
            v1.append("compaction.reserved/prune/tail_turns")
    skills = data.get("skills")
    if isinstance(skills, list):
        v2.append("skills[]")
    elif isinstance(skills, dict):
        v1.append("skills{paths,urls}")
    if v1 and v2:
        kind = "mixed"
    elif v2:
        kind = "V2"
    elif v1:
        kind = "V1"
    else:
        kind = "neutral"
    return kind, v1, v2


def mcp_servers(data):
    mcp = data.get("mcp")
    if not isinstance(mcp, dict):
        return []
    names = []
    servers = mcp.get("servers")
    if isinstance(servers, dict):
        names += [f"{k} (V2)" for k in servers]
    names += [f"{k} (V1)" for k, v in mcp.items()
              if k not in ("servers", "timeout") and isinstance(v, dict)]
    return names


def summarize(data):
    """Print a short structural summary without assuming either format."""
    kind, v1, v2 = detect_format(data)
    colour = YELLOW if kind == "mixed" else GREEN
    print(f"  {colour}Detected format: {kind}{RESET}")
    if v2:
        note(f"V2 markers: {', '.join(v2)}")
    if v1:
        note(f"V1 markers: {', '.join(v1)}")
    if kind == "mixed":
        note("Mixed is allowed at top level; keep each nested agent/provider/command/model in one format.")
    rules = data.get("permissions")
    if isinstance(rules, list):
        note(f"permissions: {len(rules)} rule(s), last match wins")
    perm = data.get("permission")
    if isinstance(perm, (dict, str)):
        note(f"permission (V1): {perm if isinstance(perm, str) else ', '.join(perm)}")
    for key in ("agents", "agent", "providers", "provider", "commands", "command"):
        value = data.get(key)
        if isinstance(value, dict) and value:
            note(f"{key}: {', '.join(value)}")
    servers = mcp_servers(data)
    if servers:
        note(f"mcp servers: {', '.join(servers)}")
    for key in ("plugins", "plugin"):
        value = data.get(key)
        if isinstance(value, list) and value:
            names = [v if isinstance(v, str)
                     else v.get("package") if isinstance(v, dict)
                     else v[0] if isinstance(v, list) and v
                     else "?"
                     for v in value]
            note(f"{key}: {', '.join(str(x) for x in names)}")


def load_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def show_json_text(text, label, source=None, with_summary=True):
    where = f" ({source})" if source else ""
    try:
        data = parse_jsonc(text)
    except json.JSONDecodeError as e:
        # Report the position only: the raw text may hold credentials.
        print(f"\n{YELLOW}{label}{RESET}{where} — parse error: {e}")
        note("Raw contents not shown. Open the file directly to fix it.")
        return
    print(f"\n{GREEN}{label}{RESET}{where}")
    if with_summary:
        summarize(data)
    print(json.dumps(redact(data), indent=2))


def show_json_file(path, label, with_summary=True):
    if not path.exists():
        note(f"{label}: not found ({path})")
        return
    show_json_text(load_file(path), label, path, with_summary)


def show_config_variants(directory, label):
    """Show opencode.json and opencode.jsonc in a directory (either may exist)."""
    found = False
    for name in CONFIG_NAMES:
        path = directory / name
        if path.exists():
            show_json_file(path, f"{label} {name}")
            found = True
    if not found:
        note(f"{label}: no opencode.json(c) in {directory}")


def show_md_file(path, label):
    if not path.exists():
        return
    print(f"\n  {GREEN}{label}{RESET}: {path}")
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    preview = "".join(lines[:10])
    if len(lines) > 10:
        preview += f"  {DIM}... ({len(lines)} lines total){RESET}\n"
    print(preview, end="")


def show_directory_contents(directory, label, extension=".md"):
    if not directory.exists():
        note(f"{label}: directory not found ({directory})")
        return
    files = sorted(directory.rglob(f"*{extension}"))
    if not files:
        note(f"{label}: empty ({directory})")
        return
    print(f"\n{GREEN}{label}{RESET} ({directory})")
    for f in files:
        show_md_file(f, str(f.relative_to(directory).with_suffix("")))


def show_env_vars():
    header("Environment Variables")
    provider_vars = [
        ("ANTHROPIC_API_KEY", "Anthropic provider auth"),
        ("OPENAI_API_KEY", "OpenAI provider auth"),
        ("OPENROUTER_API_KEY", "OpenRouter provider auth"),
        ("AWS_ACCESS_KEY_ID", "AWS Bedrock auth"),
        ("AWS_SECRET_ACCESS_KEY", "AWS Bedrock auth"),
        ("AWS_PROFILE", "AWS Bedrock profile"),
        ("AWS_REGION", "AWS Bedrock region"),
        ("AWS_BEARER_TOKEN_BEDROCK", "AWS Bedrock API key"),
        ("GOOGLE_CLOUD_PROJECT", "Vertex AI project"),
        ("GOOGLE_APPLICATION_CREDENTIALS", "Vertex AI service account"),
        ("VERTEX_LOCATION", "Vertex AI location"),
        ("AZURE_RESOURCE_NAME", "Azure resource (V2)"),
        ("OPENCODE_LOG_LEVEL", "V2 log level"),
        ("OPENCODE_DB", "V2 database path override"),
    ]
    found = False
    for var, desc in provider_vars:
        val = os.environ.get(var)
        if val:
            masked = val[:4] + "..." + val[-2:] if len(val) > 8 else "***"
            print(f"  {var}={masked}  {DIM}({desc}){RESET}")
            found = True
    if not found:
        note("No provider env vars set in this shell")
    note("V2 note: the shared background server has its own env — see `opencode service get env`.")


def main():
    print(f"{BOLD}opencode Configuration Summary{RESET}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Project root: {PROJECT_ROOT}")

    header(f"User Config ({CONFIG_DIR})")
    show_config_variants(CONFIG_DIR, "global")

    header(f"Project Config ({PROJECT_ROOT})")
    if PROJECT_ROOT.resolve() == CONFIG_DIR.resolve():
        note("Same as user config directory")
    else:
        show_config_variants(PROJECT_ROOT, "project")
        show_config_variants(PROJECT_DIR, "project .opencode/")
        note("V2 merges direct configs first, then .opencode/ configs (which override them).")

    if CONFIG_OVERRIDE or CONFIG_CONTENT_OVERRIDE:
        header("Configuration Overrides (V1-documented env vars)")
        if CONFIG_OVERRIDE:
            show_json_file(Path(CONFIG_OVERRIDE).expanduser(), "OPENCODE_CONFIG")
        if CONFIG_CONTENT_OVERRIDE:
            show_json_text(CONFIG_CONTENT_OVERRIDE, "OPENCODE_CONFIG_CONTENT")

    if CONFIG_DIRECTORY_OVERRIDE:
        # An additional layer, not a replacement root: it is searched like a
        # .opencode/ directory and loads after global and .opencode/ configs, so
        # its settings override theirs. cli.json/tui.json stay global.
        custom_dir = Path(CONFIG_DIRECTORY_OVERRIDE).expanduser()
        header(f"Custom Config Directory ({custom_dir})")
        note("OPENCODE_CONFIG_DIR (V1-documented) loads after global and .opencode/ configs.")
        show_config_variants(custom_dir, "OPENCODE_CONFIG_DIR")
        show_directory_contents(custom_dir / "agents", "Custom agents")
        show_directory_contents(custom_dir / "commands", "Custom commands")
        show_directory_contents(custom_dir / "modes", "Custom modes")
        for plugin_dir in (custom_dir / "plugins", custom_dir / "plugin"):
            if plugin_dir.exists():
                names = sorted(f.name for f in plugin_dir.iterdir() if f.is_file())
                print(f"\n{GREEN}Custom plugins{RESET} ({plugin_dir}): {', '.join(names) or 'empty'}")

    header(f"V2 CLI Config ({CLI_JSON})")
    show_json_file(CLI_JSON, "cli.json", with_summary=False)
    if CLI_CONTENT_OVERRIDE:
        show_json_text(CLI_CONTENT_OVERRIDE, "OPENCODE_CLI_CONFIG_CONTENT", with_summary=False)

    header(f"V1 TUI Config ({TUI_JSON})")
    show_json_file(TUI_JSON, "tui.json", with_summary=False)
    if PROJECT_TUI_JSON != TUI_JSON:
        show_json_file(PROJECT_TUI_JSON, "project tui.json", with_summary=False)
    if CLI_JSON.exists() and TUI_JSON.exists():
        note("Both exist: V2 reads cli.json; tui.json is only used by V1.")

    header("Custom Agents")
    show_directory_contents(AGENTS_DIR, f"Global agents ({AGENTS_DIR})")
    if PROJECT_AGENTS_DIR.exists():
        show_directory_contents(PROJECT_AGENTS_DIR, "Project agents (.opencode/agents/)")

    header("Custom Commands")
    show_directory_contents(COMMANDS_DIR, f"Global commands ({COMMANDS_DIR})")
    if PROJECT_COMMANDS_DIR.exists():
        show_directory_contents(PROJECT_COMMANDS_DIR, "Project commands (.opencode/commands/)")

    themes_dir = CONFIG_DIR / "themes"
    project_themes_dir = PROJECT_DIR / "themes"
    if themes_dir.exists() or project_themes_dir.exists():
        header("Custom Themes")
        for label, directory in (("Global", themes_dir), ("Project", project_themes_dir)):
            files = sorted(directory.glob("*.json")) if directory.exists() else []
            if files:
                print(f"  {label}: {', '.join(f.stem for f in files)}")

    show_env_vars()
    print()


if __name__ == "__main__":
    main()

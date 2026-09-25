#!/usr/bin/env python3
"""
show-config.py — Display all GitHub Copilot CLI config files with annotations.
Usage: python show-config.py [--json]

Reads $COPILOT_HOME (default ~/.copilot) and project config in the current directory.
Secrets are never printed: config.json values (which can hold a plaintext auth token) are
reduced to key names, and token/key-like environment variables are masked.
"""
import json
import os
import re
import sys
from pathlib import Path

COPILOT_HOME = Path(os.environ.get("COPILOT_HOME", Path.home() / ".copilot"))
CONFIG_FILE = COPILOT_HOME / "config.json"
SETTINGS_FILE = COPILOT_HOME / "settings.json"
PERMISSIONS_FILE = COPILOT_HOME / "permissions-config.json"
MCP_FILE = COPILOT_HOME / "mcp-config.json"
LSP_FILE = COPILOT_HOME / "lsp-config.json"
PROVIDERS_FILE = Path(os.environ.get("COPILOT_PROVIDERS_CONFIG", COPILOT_HOME / "providers.json"))
SKILLS_DIR = COPILOT_HOME / "skills"
AGENTS_DIR = COPILOT_HOME / "agents"
HOOKS_DIR = COPILOT_HOME / "hooks"
EXTENSIONS_DIR = COPILOT_HOME / "extensions"
PLUGINS_DIR = COPILOT_HOME / "installed-plugins"
INSTRUCTIONS_DIR = COPILOT_HOME / "instructions"
INSTRUCTIONS_FILE = COPILOT_HOME / "copilot-instructions.md"

BYOK_VARS = [
    "COPILOT_PROVIDERS_CONFIG",
    "COPILOT_PROVIDER_BASE_URL",
    "COPILOT_PROVIDER_TYPE",
    "COPILOT_PROVIDER_API_KEY",
    "COPILOT_PROVIDER_API_KEY_COMMAND",
    "COPILOT_PROVIDER_BEARER_TOKEN",
    "COPILOT_PROVIDER_WIRE_API",
    "COPILOT_PROVIDER_AZURE_API_VERSION",
    "COPILOT_PROVIDER_MODEL_ID",
    "COPILOT_PROVIDER_WIRE_MODEL",
    "COPILOT_PROVIDER_MAX_PROMPT_TOKENS",
    "COPILOT_PROVIDER_MAX_OUTPUT_TOKENS",
    "COPILOT_MODEL",
    "COPILOT_OFFLINE",
]
AUTH_VARS = [
    "COPILOT_GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_TOKEN",
]
OTHER_VARS = [
    "COPILOT_HOME",
    "COPILOT_CACHE_HOME",
    "COPILOT_GH_HOST",
    "GH_HOST",
    "COPILOT_ALLOW_ALL",
    "COPILOT_AUTO_UPDATE",
    "COPILOT_CUSTOM_INSTRUCTIONS_DIRS",
    "COPILOT_SKILLS_DIRS",
]
SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD")


def strip_jsonc(text):
    """Remove // and /* */ comments outside strings, plus trailing commas (settings.json is JSONC)."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def load_json(path, jsonc=False):
    """Return parsed JSON, None if missing, or {} (after printing an error) if invalid."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(strip_jsonc(text) if jsonc else text)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ERROR: could not parse {path}: {e}")
        return {}


def mask(name, value):
    value = str(value)
    if any(marker in name.upper() for marker in SECRET_MARKERS):
        return value[:4] + "..." if len(value) > 4 else "***"
    return value


def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def frontmatter(path):
    """Return a dict of simple top-level `key: value` frontmatter lines."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    fields = {}
    for line in content[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, val = line.split(":", 1)
            fields[key.strip()] = val.strip().strip("'\"")
    return fields


def describe_mcp(servers):
    """servers: dict of name -> config. Handles both wrapped and bare formats."""
    if not servers:
        print("    (no servers configured)")
        return
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            continue
        transport = cfg.get("type", "local")
        endpoint = cfg.get("command", cfg.get("url", "?"))
        tools = cfg.get("tools", [])
        tool_str = "*" if tools == ["*"] else ", ".join(map(str, tools[:3])) or "(none listed)"
        print(f"    [{name}]  type={transport}  endpoint={endpoint}")
        print(f"      tools: {tool_str}")
        if cfg.get("env"):
            print(f"      env vars: {list(cfg['env'].keys())}")
        if cfg.get("headers"):
            print(f"      headers: {list(cfg['headers'].keys())}")


def mcp_servers(data):
    if not isinstance(data, dict):
        return {}
    return data.get("mcpServers", data if "mcpServers" not in data else {})


def list_dir(path, pattern, label):
    items = sorted(path.glob(pattern)) if path.exists() else []
    if not items:
        print(f"  (no {label} found)")
    for item in items:
        print(f"  {item.relative_to(path)}")


def show_settings(path, as_json):
    settings = load_json(path, jsonc=True)
    if settings is None:
        print("  (file not found — defaults apply)")
    elif not settings:
        print("  (empty)")
    elif as_json:
        print(json.dumps(settings, indent=2))
    else:
        for key, value in settings.items():
            shown = json.dumps(value) if isinstance(value, (dict, list)) else value
            print(f"  {key}: {mask(key, shown)}")


def main():
    as_json = "--json" in sys.argv
    print(f"Copilot CLI config directory: {COPILOT_HOME}")

    # --- settings.json ---
    section(f"USER SETTINGS ({SETTINGS_FILE})")
    show_settings(SETTINGS_FILE, as_json)

    # --- config.json (managed state; only trustedFolders is user-editable) ---
    section(f"APP STATE / TRUSTED FOLDERS ({CONFIG_FILE})")
    config = load_json(CONFIG_FILE)
    if config is None:
        print("  (file not found — no trusted folders configured yet)")
    elif not config:
        print("  (empty)")
    else:
        trusted = config.get("trustedFolders", [])
        print(f"  trustedFolders: ({len(trusted)} entries)")
        for folder in trusted:
            print(f"    - {folder}")
        other = [k for k in config if k != "trustedFolders"]
        if other:
            print(f"  managed keys (values hidden): {', '.join(other)}")

    # --- permissions-config.json ---
    section(f"SAVED PERMISSIONS ({PERMISSIONS_FILE})")
    perms = load_json(PERMISSIONS_FILE)
    if perms is None:
        legacy = COPILOT_HOME / "permissions-config"
        print("  (file not found" + (" — legacy permissions-config present)" if legacy.exists() else ")"))
    elif as_json:
        print(json.dumps(perms, indent=2))
    else:
        locations = perms.get("locations", {}) if isinstance(perms, dict) else {}
        if not locations:
            print("  (no saved approvals)")
        for loc, entry in locations.items():
            approvals = entry.get("tool_approvals", [])
            kinds = ", ".join(sorted({a.get("kind", "?") for a in approvals})) or "none"
            dirs = entry.get("allowed_directories", [])
            print(f"  {loc}: {len(approvals)} approval(s) [{kinds}], {len(dirs)} extra dir(s)")

    # --- mcp-config.json ---
    section(f"MCP SERVERS ({MCP_FILE})")
    mcp = load_json(MCP_FILE)
    if mcp is None:
        print("  (file not found — no user-level MCP servers)")
    else:
        describe_mcp(mcp_servers(mcp))

    # --- lsp-config.json ---
    section(f"LSP SERVERS ({LSP_FILE})")
    lsp = load_json(LSP_FILE)
    if lsp is None:
        print("  (file not found — no user-level LSP servers)")
    else:
        servers = lsp.get("lspServers", {}) if isinstance(lsp, dict) else {}
        if not servers:
            print("  (no servers configured)")
        for name, cfg in servers.items():
            exts = ", ".join(cfg.get("fileExtensions", {}).keys()) if isinstance(cfg, dict) else ""
            print(f"    [{name}]  command={cfg.get('command', '?')}  extensions={exts}")

    # --- providers.json ---
    section(f"BYOK PROVIDERS ({PROVIDERS_FILE})")
    providers = load_json(PROVIDERS_FILE)
    if providers is None:
        print("  (file not found)")
    elif isinstance(providers, dict):
        for key in ("providers", "models"):
            val = providers.get(key)
            count = len(val) if isinstance(val, (list, dict)) else 0
            print(f"  {key}: {count} entr{'y' if count == 1 else 'ies'}")

    # --- skills ---
    section(f"PERSONAL SKILLS ({SKILLS_DIR})")
    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if (d / "SKILL.md").exists()) if SKILLS_DIR.exists() else []
    if not skill_dirs:
        print("  (no skills found)")
    for skill_dir in skill_dirs:
        fm = frontmatter(skill_dir / "SKILL.md")
        if fm is None:
            print(f"    [{skill_dir.name}]  (could not read SKILL.md)")
            continue
        desc = (fm.get("description") or "?")[:60]
        print(f"    [{skill_dir.name}]  name={fm.get('name', '?')}  desc={desc}...")

    # --- agents ---
    section(f"PERSONAL CUSTOM AGENTS ({AGENTS_DIR})")
    agent_files = sorted(AGENTS_DIR.glob("*.md")) if AGENTS_DIR.exists() else []
    if not agent_files:
        print("  (no agents found)")
    for agent_file in agent_files:
        fm = frontmatter(agent_file) or {}
        agent_id = agent_file.name.removesuffix(".md").removesuffix(".agent")
        print(f"    [{agent_id}]  model={fm.get('model', '(inherit)')}  desc={(fm.get('description') or '?')[:50]}...")

    # --- hooks, instructions, extensions, plugins ---
    section(f"PERSONAL HOOKS ({HOOKS_DIR})")
    list_dir(HOOKS_DIR, "*.json", "hook files")

    section(f"PERSONAL INSTRUCTIONS ({INSTRUCTIONS_FILE})")
    if INSTRUCTIONS_FILE.exists():
        print(f"  Found ({INSTRUCTIONS_FILE.stat().st_size} bytes)")
        if not as_json:
            preview = INSTRUCTIONS_FILE.read_text(encoding="utf-8").strip().replace("\n", " ")
            print(f"  Preview: {preview[:120]}...")
    else:
        print("  (file not found)")

    section(f"PERSONAL PATH-SPECIFIC INSTRUCTIONS ({INSTRUCTIONS_DIR})")
    list_dir(INSTRUCTIONS_DIR, "**/*.instructions.md", "path-specific instruction files")

    section(f"EXTENSIONS ({EXTENSIONS_DIR})")
    list_dir(EXTENSIONS_DIR, "*", "extensions")

    section(f"INSTALLED PLUGINS ({PLUGINS_DIR})")
    plugin_dirs = sorted(p for p in PLUGINS_DIR.glob("*/*") if p.is_dir()) if PLUGINS_DIR.exists() else []
    if not plugin_dirs:
        print("  (no plugins installed)")
    for plugin_dir in plugin_dirs:
        print(f"  {plugin_dir.parent.name}/{plugin_dir.name}")

    # --- project config files ---
    cwd = Path.cwd()
    project_files = [
        (cwd / ".github" / "copilot" / "settings.json", "Repository settings"),
        (cwd / ".github" / "copilot" / "settings.local.json", "Local settings"),
        (cwd / ".github" / "allowed_models.txt", "Model allowlist"),
        (cwd / ".github" / "copilot-instructions.md", "Project instructions"),
        (cwd / "AGENTS.md", "AGENTS.md"),
        (cwd / "CLAUDE.md", "CLAUDE.md"),
        (cwd / "GEMINI.md", "GEMINI.md"),
        (cwd / ".github" / "instructions", "Path-specific instructions"),
        (cwd / ".mcp.json", "Project MCP (.mcp.json)"),
        (cwd / ".github" / "mcp.json", "Project MCP (.github/mcp.json)"),
        (cwd / ".vscode" / "mcp.json", "VS Code MCP (NOT read by Copilot CLI)"),
        (cwd / ".github" / "lsp.json", "Project LSP servers"),
        (cwd / ".github" / "hooks", "Project hooks"),
        (cwd / ".github" / "skills", "Project skills (.github)"),
        (cwd / ".agents" / "skills", "Project skills (.agents)"),
        (cwd / ".claude" / "skills", "Project skills (.claude)"),
        (cwd / ".github" / "agents", "Project agents (.github)"),
        (cwd / ".claude" / "agents", "Project agents (.claude)"),
    ]
    if any(path.exists() for path, _ in project_files):
        section(f"PROJECT CONFIG (in {cwd})")
        for path, label in project_files:
            if not path.exists():
                continue
            if path.is_dir():
                print(f"  {label}: {len(list(path.iterdir()))} item(s) in {path}")
            else:
                print(f"  {label}: {path} ({path.stat().st_size} bytes)")
                if path.name in ("mcp.json", ".mcp.json") and path.parent.name != ".vscode":
                    describe_mcp(mcp_servers(load_json(path) or {}))
                elif path.name.startswith("settings") and path.suffix == ".json":
                    show_settings(path, as_json)

    # --- env vars ---
    section("ENVIRONMENT VARIABLES")
    print("  Auth (first set wins):")
    active = next((v for v in AUTH_VARS if os.environ.get(v)), None)
    if active:
        print(f"    {active}={mask(active, os.environ[active])} (active)")
    else:
        print("    (none set — using keychain or gh auth)")

    print("  BYOK / custom provider:")
    byok = [v for v in BYOK_VARS if os.environ.get(v)]
    for var in byok:
        print(f"    {var}={mask(var, os.environ[var])}")
    if not byok:
        print("    (none set — using GitHub-hosted models)")

    print("  Other:")
    other = [v for v in OTHER_VARS if os.environ.get(v)]
    for var in other:
        print(f"    {var}={mask(var, os.environ[var])}")
    if not other:
        print("    (none set)")

    print()


if __name__ == "__main__":
    main()

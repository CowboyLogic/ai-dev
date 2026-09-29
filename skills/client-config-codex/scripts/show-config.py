#!/usr/bin/env python3
"""
show-config.py — Display all OpenAI Codex CLI config files with annotations.
Usage: python show-config.py [--json]

Reads $CODEX_HOME (default ~/.codex) and project config in the current directory.
Secrets are never printed: auth.json is only reported as present or absent, config.toml
is redacted recursively in both output modes (secret-like keys at any depth, every value
under `env`/`http_headers`, token-shaped strings), and token/key-like environment
variables are masked. Requires Python 3.11+ (tomllib).
"""
import json
import os
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
CONFIG_FILE = CODEX_HOME / "config.toml"
if os.name == "nt":
    SYSTEM_DIR = Path(os.environ.get("ProgramData", r"C:\ProgramData")) / "OpenAI" / "Codex"
else:
    SYSTEM_DIR = Path("/etc/codex")
SYSTEM_CONFIG_FILE = SYSTEM_DIR / "config.toml"
REQUIREMENTS_FILE = SYSTEM_DIR / "requirements.toml"
# Legacy managed defaults (Unix only) override user config and even CLI flags, so a diagnostic
# that omits them can miss the file controlling a value.
MANAGED_CONFIG_FILE = None if os.name == "nt" else SYSTEM_DIR / "managed_config.toml"  # Unix only; see references/config-schema.md
AUTH_FILE = CODEX_HOME / "auth.json"
HOOKS_FILE = CODEX_HOME / "hooks.json"
RULES_DIR = CODEX_HOME / "rules"
AGENTS_DIR = CODEX_HOME / "agents"
SKILLS_DIRS = [
    ("USER SKILLS", Path.home() / ".agents" / "skills"),
    ("ADMIN SKILLS", SYSTEM_DIR / "skills"),
    ("CODEX_HOME SKILLS (bundled system skills live under .system/)", CODEX_HOME / "skills"),
]
INSTRUCTION_NAMES = ("AGENTS.override.md", "AGENTS.md")

AUTH_VARS = ["CODEX_ACCESS_TOKEN", "CODEX_API_KEY", "OPENAI_API_KEY"]
OTHER_VARS = [
    "CODEX_HOME",
    "CODEX_SQLITE_HOME",
    "OPENAI_BASE_URL",
    "OPENAI_ORG_ID",
    "OPENAI_PROJECT_ID",
    "CODEX_CA_CERTIFICATE",
    "SSL_CERT_FILE",
    "HTTPS_PROXY",
    "https_proxy",
    "HTTP_PROXY",
    "http_proxy",
    "ALL_PROXY",
    "NO_PROXY",
]
SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "AUTH", "CREDENTIAL")
# Keys whose value names an environment variable rather than holding a credential.
ENV_NAME_SUFFIXES = ("_env_var", "_env_vars", "env_key", "env_http_headers")
# Maps whose values are credentials regardless of key name (e.g. an "Authorization" header).
SECRET_MAPS = ("env", "http_headers", "headers", "set")  # "set" = shell_environment_policy.set
TOKEN_VALUE = re.compile(r"^(sk-|ghp_|github_pat_|xox[abp]-|Bearer\s)", re.I)
PROXY_NAME = re.compile(r"^(https?|all)_proxy$", re.I)  # not NO_PROXY, which is a host list
URL_VALUE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
DISCOVERY_KEYS = ("project_root_markers", "project_doc_fallback_filenames")
PROJECT_ROOT_MARKERS = (".git",)  # Codex default; override with project_root_markers in config


def load_toml(path):
    """Return parsed TOML, None if missing, or {} (after printing an error) if invalid."""
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as e:
        print(f"  ERROR: could not parse {path}: {e}")
        return {}


def load_json(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ERROR: could not parse {path}: {e}")
        return {}


def scrub_url(value):
    """Keep only scheme, host, and port: userinfo, path, query, and fragment can all carry credentials."""
    try:
        parts = urlsplit(value)
        host = parts.hostname or ""
        if parts.port:
            host = f"{host}:{parts.port}"
        cleaned = urlunsplit((parts.scheme, host, "", "", ""))
    except ValueError:
        return "***"
    if cleaned != value.rstrip("/"):
        cleaned += "/...  (path and credentials hidden)"
    return cleaned


def mask(name, value):
    value = str(value)
    if URL_VALUE.match(value):
        return scrub_url(value)
    if PROXY_NAME.match(name) or ("@" in value and "/" not in value.split("@", 1)[0]):
        # Scheme-less user:password@host[:port]/path forms: scrub like a URL, then drop the scheme.
        return scrub_url("http://" + value).removeprefix("http://")
    if any(marker in name.upper() for marker in SECRET_MARKERS):
        return value[:4] + "..." if len(value) > 4 else "***"
    return value


def redact(value, key="", in_secret_map=False):
    """Recursively mask secrets in parsed config before it is printed, in any mode."""
    if isinstance(value, dict):
        return {
            k: redact(v, k, in_secret_map or k.lower() in SECRET_MAPS) for k, v in value.items()
        }
    if isinstance(value, list):
        return [redact(v, key, in_secret_map) for v in value]
    if isinstance(value, str):
        if URL_VALUE.match(value):
            return scrub_url(value)
        names_env_var = key.lower().endswith(ENV_NAME_SUFFIXES)
        if in_secret_map or TOKEN_VALUE.match(value):
            return "***"
        if not names_env_var and any(marker in key.upper() for marker in SECRET_MARKERS):
            return "***"
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
    if not servers:
        print("    (no servers configured)")
        return
    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            continue
        transport = "http" if "url" in cfg else "stdio"
        endpoint = scrub_url(cfg["url"]) if "url" in cfg else cfg.get("command", "?")
        flags = []
        if cfg.get("enabled") is False:
            flags.append("disabled")
        if cfg.get("required"):
            flags.append("required")
        suffix = f"  ({', '.join(flags)})" if flags else ""
        print(f"    [{name}]  transport={transport}  endpoint={endpoint}{suffix}")
        if cfg.get("env"):
            print(f"      env vars: {list(cfg['env'].keys())}")
        if cfg.get("http_headers"):
            print(f"      headers: {list(cfg['http_headers'].keys())}")


def show_config(path, as_json):
    """Print config.toml with secrets redacted. Returns the parsed (unredacted) data."""
    config = load_toml(path)
    if config is None:
        print("  (file not found — defaults apply)")
    elif not config:
        print("  (empty)")
    elif as_json:
        print(json.dumps(redact(config), indent=2))
    else:
        for key, value in redact(config).items():
            if isinstance(value, dict):
                print(f"  [{key}]  ({len(value)} entr{'y' if len(value) == 1 else 'ies'}: "
                      f"{', '.join(list(value)[:6])}{'...' if len(value) > 6 else ''})")
            else:
                print(f"  {key} = {json.dumps(value)}")
    return config or {}


def active_instruction_file(directory, extra_names=()):
    """Codex reads at most one instruction file per directory: the first non-empty of
    AGENTS.override.md, AGENTS.md, then project_doc_fallback_filenames, in that order."""
    # Codex ignores fallback entries that are not plain filenames (paths, "..", absolute paths).
    plain = [n for n in extra_names if isinstance(n, str) and n not in ("", ".", "..") and Path(n).name == n and "\\" not in n]
    for name in (*INSTRUCTION_NAMES, *plain):
        path = directory / name
        try:
            if path.is_file() and path.stat().st_size > 0:
                return path
        except OSError:
            continue
    return None


def trust_level(config, *paths):
    """trust_level recorded under [projects."<path>"] for the first path that has an entry."""
    # Codex lowercases trust keys on Windows; normcase is a no-op elsewhere.
    projects = {os.path.normcase(str(k)): v for k, v in config.get("projects", {}).items()}
    for path in paths:
        entry = projects.get(os.path.normcase(str(path)))
        if isinstance(entry, dict) and entry.get("trust_level"):
            return entry["trust_level"]
    return None


def list_dir(path, pattern, label):
    items = sorted(path.glob(pattern)) if path.exists() else []
    if not items:
        print(f"  (no {label} found)")
    for item in items:
        print(f"  {item.relative_to(path)}")


def show_skills(directory):
    skill_dirs = sorted(d for d in directory.iterdir() if (d / "SKILL.md").exists()) if directory.exists() else []
    if not skill_dirs:
        print("  (no skills found)")
    for skill_dir in skill_dirs:
        fm = frontmatter(skill_dir / "SKILL.md")
        if fm is None:
            print(f"    [{skill_dir.name}]  (could not read SKILL.md)")
            continue
        desc = (fm.get("description") or "?")[:60]
        print(f"    [{skill_dir.name}]  name={fm.get('name', '?')}  desc={desc}...")


def show_hooks(path):
    hooks = load_json(path)
    if hooks is None:
        print("  (file not found)")
        return
    events = hooks.get("hooks", hooks) if isinstance(hooks, dict) else {}
    if not events:
        print("  (no hooks defined)")
    for event, groups in events.items():
        if not isinstance(groups, list):
            continue
        handlers = sum(len(g.get("hooks", [])) for g in groups if isinstance(g, dict))
        print(f"    {event}: {len(groups)} matcher group(s), {handlers} handler(s)")


def main():
    as_json = "--json" in sys.argv
    print(f"Codex config directory: {CODEX_HOME}")

    section(f"USER CONFIG ({CONFIG_FILE})")
    config = show_config(CONFIG_FILE, as_json)

    section(f"MCP SERVERS (from {CONFIG_FILE.name})")
    describe_mcp(config.get("mcp_servers", {}))

    section("PROJECT TRUST (projects.*)")
    projects = config.get("projects", {})
    if not projects:
        print("  (no project entries)")
    for path, entry in projects.items():
        level = entry.get("trust_level", "?") if isinstance(entry, dict) else "?"
        print(f"    {path}: trust_level={level}")

    section("PROFILES, PROVIDERS, PLUGINS")
    profile_files = sorted(p.name.removesuffix(".config.toml") for p in CODEX_HOME.glob("*.config.toml"))
    print(f"  profile files (--profile): {', '.join(profile_files) or '(none)'}")
    print(f"  model_providers: {', '.join(config.get('model_providers', {})) or '(none)'}")
    plugins = config.get("plugins", {})
    enabled = [n for n, v in plugins.items() if isinstance(v, dict) and v.get("enabled")]
    print(f"  plugins enabled: {len(enabled)} of {len(plugins)}")
    for name in enabled:
        print(f"    {name}")

    section(f"SYSTEM CONFIG ({SYSTEM_CONFIG_FILE})")
    system_config = show_config(SYSTEM_CONFIG_FILE, as_json)

    managed_config = {}
    if MANAGED_CONFIG_FILE:
        section(f"LEGACY MANAGED DEFAULTS ({MANAGED_CONFIG_FILE})")
        managed_config = show_config(MANAGED_CONFIG_FILE, as_json)

    section(f"ADMIN REQUIREMENTS ({REQUIREMENTS_FILE})")
    show_config(REQUIREMENTS_FILE, as_json)

    section("AUTH")
    print(f"  {AUTH_FILE}: {'present (contents never shown)' if AUTH_FILE.exists() else 'not found (keyring or not signed in)'}")

    section(f"USER HOOKS ({HOOKS_FILE})")
    show_hooks(HOOKS_FILE)

    section(f"RULES ({RULES_DIR})")
    list_dir(RULES_DIR, "*.rules", "rules files")

    for label, skills_dir in SKILLS_DIRS:
        section(f"{label} ({skills_dir})")
        show_skills(skills_dir)

    section(f"USER CUSTOM AGENTS ({AGENTS_DIR})")
    list_dir(AGENTS_DIR, "**/*.toml", "agent files")

    section("GLOBAL INSTRUCTIONS")
    active = active_instruction_file(CODEX_HOME)
    if active:
        # Contents are deliberately not previewed: instruction files can hold pasted secrets.
        print(f"  {active} ({active.stat().st_size} bytes, active)")
    else:
        print("  (no non-empty AGENTS.override.md or AGENTS.md in CODEX_HOME)")

    # --- project config files: every layer from the project root down to cwd ---
    cwd = Path.cwd().resolve()
    # Discovery settings come from the merged system, user, and legacy managed layers
    # (later wins), not from the user file alone.
    discovery = {}
    for layer in (system_config, config, managed_config):
        discovery.update({k: v for k, v in layer.items() if k in DISCOVERY_KEYS})
    markers = discovery.get("project_root_markers", PROJECT_ROOT_MARKERS)
    fallbacks = tuple(discovery.get("project_doc_fallback_filenames", []))
    root = next((d for d in (cwd, *cwd.parents) if any((d / m).exists() for m in markers)), cwd)
    chain = [cwd]
    while chain[-1] != root:
        chain.append(chain[-1].parent)
    chain.reverse()
    trust = trust_level(config, root, cwd)
    trusted = trust == "trusted"
    printed_header = False
    for directory in chain:
        project_files = [
            (directory / ".codex" / "config.toml", "Project config"),
            (directory / ".codex" / "hooks.json", "Project hooks"),
            (directory / ".codex" / "agents", "Project agents"),
            (directory / ".codex" / "rules", "Project rules"),
            (directory / ".agents" / "skills", "Project skills"),
        ]
        instructions = active_instruction_file(directory, fallbacks)
        if instructions:
            project_files.append((instructions, "Instructions (active file)"))
        found = [(path, label) for path, label in project_files if path.exists()]
        if not found:
            continue
        if not printed_header:
            section(f"PROJECT CONFIG (root {root} down to {cwd})")
            print(f"  project trust_level: {trust or 'not set'}"
                  + ("" if trusted else "  -> project .codex/ layers below are INACTIVE"))
            printed_header = True
        print(f"  -- {directory}")
        for path, label in found:
            gated = path.relative_to(directory).parts[0] == ".codex"  # instructions and .agents/skills are not trust-gated
            inactive = gated and not trusted
            skipped = trust == "untrusted" and path == instructions  # explicit untrusted skips project AGENTS.md
            tag = "  [INACTIVE: project not trusted, Codex skips it]" if inactive else (
                "  [SKIPPED: project is explicitly untrusted]" if skipped else "")
            if path.is_dir():
                print(f"  {label}: {len(list(path.iterdir()))} item(s) in {path}{tag}")
            else:
                print(f"  {label}: {path} ({path.stat().st_size} bytes){tag}")
                if path.name == "config.toml" and not inactive:
                    project_config = show_config(path, as_json)
                    describe_mcp(project_config.get("mcp_servers", {}))

    # --- env vars ---
    section("ENVIRONMENT VARIABLES")
    print("  Auth:")
    active = [v for v in AUTH_VARS if os.environ.get(v)]
    for var in active:
        print(f"    {var}={mask(var, os.environ[var])}")
    if not active:
        print("    (none set — using stored login)")

    print("  Other:")
    other = [v for v in OTHER_VARS if os.environ.get(v)]
    for var in other:
        print(f"    {var}={mask(var, os.environ[var])}")
    if not other:
        print("    (none set)")

    print()


if __name__ == "__main__":
    main()

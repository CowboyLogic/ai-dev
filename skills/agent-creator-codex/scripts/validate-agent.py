#!/usr/bin/env python3
"""Validate Codex custom agent TOML files.

Usage:
    validate-agent.py <file-or-directory> [...] [--strict]

Checks that each file parses as TOML, has non-blank `name`, `description`, and
`developer_instructions`, uses known snake_case keys, has valid enum values, and that names are
unique across the scanned set. Uses only the standard library (Python 3.11+).
Exit status is 1 when any error is found (or any warning with --strict).

Field list last verified September 2026 against
https://developers.openai.com/codex/subagents and codex-cli 0.158.0.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:  # pragma: no cover
    sys.exit("Python 3.11+ is required (tomllib)")

REQUIRED = ("name", "description", "developer_instructions")
# Keys documented for agent files, plus common config.toml keys that layers may carry.
KNOWN_KEYS = set(REQUIRED) | {
    "nickname_candidates", "model", "model_reasoning_effort", "sandbox_mode",
    "mcp_servers", "skills", "approval_policy", "model_verbosity", "web_search",
    "personality", "model_provider", "model_reasoning_summary", "features",
    "shell_environment_policy", "sandbox_workspace_write", "tools",
}
SANDBOX_MODES = {"read-only", "workspace-write", "danger-full-access"}
EFFORTS = {"low", "medium", "high", "xhigh", "max", "ultra"}
APPROVAL_POLICIES = {"on-request", "never"}
# Fields from other agent tools that Codex does not have.
FOREIGN = {
    "tools": "Codex has no tool allowlist; use sandbox_mode and mcp_servers.enabled_tools",
    "disallowedTools": "Claude Code field; Codex has no equivalent",
    "permissionMode": "Claude Code field; use sandbox_mode",
    "permission": "OpenCode field; use sandbox_mode",
    "mode": "OpenCode field",
    "temperature": "OpenCode field",
    "tools_list": "not a Codex field",
    "maxTurns": "Claude Code field",
    "disable-model-invocation": "Copilot field",
    "user-invocable": "Copilot field",
    "handoffs": "Copilot field",
}
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class Result:
    def __init__(self) -> None:
        self.errors = 0
        self.warnings = 0

    def error(self, path: Path, msg: str) -> None:
        self.errors += 1
        print(f"ERROR   {path}: {msg}")

    def warn(self, path: Path, msg: str) -> None:
        self.warnings += 1
        print(f"WARNING {path}: {msg}")


def suggest(key: str) -> str:
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", key).replace("-", "_").lower()
    if snake in KNOWN_KEYS and snake != key:
        return f" (did you mean `{snake}`?)"
    close = difflib.get_close_matches(key, KNOWN_KEYS, n=1, cutoff=0.75)
    return f" (did you mean `{close[0]}`?)" if close else ""


def check_string(res: Result, path: Path, data: dict, key: str) -> None:
    if key not in data:
        res.error(path, f"missing required `{key}`")
    elif not isinstance(data[key], str):
        res.error(path, f"`{key}` must be a string")
    elif not data[key].strip():
        res.error(path, f"`{key}` must not be blank")


def validate_file(path: Path, names: dict[str, Path], res: Result) -> None:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        res.error(path, f"TOML does not parse: {exc}")
        return
    except OSError as exc:
        res.error(path, f"cannot read: {exc}")
        return

    for key in REQUIRED:
        check_string(res, path, data, key)

    name = data.get("name")
    if isinstance(name, str) and name.strip():
        if not NAME_RE.match(name):
            res.warn(path, f"name `{name}` has characters other than letters, digits, `_`, `-`")
        if name in names:
            res.error(path, f"duplicate name `{name}` (also in {names[name]})")
        else:
            names[name] = path
        if path.stem != name:
            res.warn(path, f"filename `{path.stem}` does not match name `{name}`")

    for key in data:
        if key == "tools" and not isinstance(data[key], dict):
            res.error(path, f"`tools`: {FOREIGN['tools']}")
            continue
        if key in KNOWN_KEYS:
            continue
        if key in FOREIGN:
            res.error(path, f"`{key}`: {FOREIGN[key]}")
        else:
            res.warn(path, f"unknown key `{key}`{suggest(key)}")

    sandbox = data.get("sandbox_mode")
    if sandbox is not None and sandbox not in SANDBOX_MODES:
        res.error(path, f"sandbox_mode `{sandbox}` not one of {sorted(SANDBOX_MODES)}")
    if sandbox == "danger-full-access":
        res.warn(path, "sandbox_mode is danger-full-access; avoid in shared agent files")

    effort = data.get("model_reasoning_effort")
    if effort is not None and effort not in EFFORTS:
        res.error(path, f"model_reasoning_effort `{effort}` not one of {sorted(EFFORTS)}")

    approval = data.get("approval_policy")
    if isinstance(approval, str) and approval not in APPROVAL_POLICIES:
        res.warn(path, f"approval_policy `{approval}` is not one of {sorted(APPROVAL_POLICIES)}")

    nick = data.get("nickname_candidates")
    if nick is not None and not (isinstance(nick, list) and all(isinstance(n, str) for n in nick)):
        res.error(path, "nickname_candidates must be an array of strings")

    servers = data.get("mcp_servers")
    if servers is not None and not isinstance(servers, dict):
        res.error(path, "mcp_servers must be a table of [mcp_servers.<id>] tables")
    elif isinstance(servers, dict):
        for sid, cfg in servers.items():
            if not isinstance(cfg, dict):
                res.error(path, f"mcp_servers.{sid} must be a table")
                continue
            for k, v in cfg.items():
                if k.lower().endswith(("token", "secret", "password")) and isinstance(v, str):
                    res.error(path, f"mcp_servers.{sid}.{k} looks like a hardcoded secret; "
                                    "use bearer_token_env_var or another env-based field")

    body = data.get("developer_instructions")
    if isinstance(body, str) and 0 < len(body.strip()) < 40:
        res.warn(path, "developer_instructions is very short; state role, scope, and return format")


def collect(target: Path) -> list[Path]:
    if target.is_dir():
        return sorted(target.glob("*.toml"))
    return [target]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    res = Result()
    names: dict[str, Path] = {}
    files: list[Path] = []
    for p in args.paths:
        if not p.exists():
            res.error(p, "path does not exist")
            continue
        files.extend(collect(p))
    if not files and not res.errors:
        print("No .toml files found")
        return 1
    for f in files:
        validate_file(f, names, res)

    print(f"\n{len(files)} file(s), {res.errors} error(s), {res.warnings} warning(s)")
    return 1 if res.errors or (args.strict and res.warnings) else 0


if __name__ == "__main__":
    sys.exit(main())

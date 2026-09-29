#!/usr/bin/env python3
"""Validate Claude Code agent (subagent) frontmatter.

Usage:
    validate-agent.py <file-or-directory> [...] [--plugin] [--strict]

Reports the conditions under which Claude Code silently skips an agent file, plus
unknown or mis-cased fields, bad enum values, and fields ignored in a given scope.
Requires PyYAML. Exit status is 1 when any error is found (or any warning with --strict).

Field list last verified September 2026 against
https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: uv pip install pyyaml")

KNOWN_FIELDS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode",
    "maxTurns", "skills", "mcpServers", "hooks", "memory", "background",
    "omitClaudeMd", "effort", "isolation", "color", "initialPrompt", "experimental",
}
PLUGIN_IGNORED = {"hooks", "mcpServers", "permissionMode", "initialPrompt"}
MODEL_ALIASES = {"sonnet", "opus", "haiku", "fable", "inherit"}
PERMISSION_MODES = {"default", "manual", "acceptEdits", "auto", "dontAsk",
                    "bypassPermissions", "plan"}
MEMORY_SCOPES = {"user", "project", "local"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
# Fields other tools use that Claude Code ignores; worth a targeted hint.
FOREIGN_FIELDS = {
    "handoffs": "Copilot field, ignored by Claude Code",
    "user-invocable": "Copilot field, ignored by Claude Code",
    "disable-model-invocation": "Copilot/skill field, ignored in agent files",
    "infer": "Copilot field, ignored by Claude Code",
    "target": "Copilot field, ignored by Claude Code",
    "argument-hint": "Copilot field, ignored by Claude Code",
    "agents": "Copilot field; restrict spawning with tools: Agent(a, b) under --agent",
    "mode": "OpenCode field, ignored by Claude Code",
    "temperature": "OpenCode field, ignored by Claude Code",
    "permission": "OpenCode field; Claude Code uses permissionMode / tools",
    "steps": "OpenCode field; Claude Code uses maxTurns",
    "hidden": "OpenCode field, ignored by Claude Code",
    "prompt": "only valid in --agents JSON; in a file the Markdown body is the prompt",
    "allowed-tools": "skill field; agent files use tools",
    "allowedTools": "agent files use tools",
}
MIN_VERSIONS = {
    "omitClaudeMd": "v2.1.271",
    "experimental": "v2.1.248",
}
TOOL_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\(.*\))?$")
CASE_INSENSITIVE = {f.lower(): f for f in KNOWN_FIELDS}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def split_frontmatter(text: str) -> tuple[str | None, str, bool]:
    """Return (frontmatter text, body, closed).

    Frontmatter is None if line 1 is not '---'. `closed` is False when no closing
    '---' line exists.
    """
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        return None, text, False
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:]), True
    return "\n".join(lines[1:]), "", False


def tool_list(value: object) -> list[str] | None:
    if isinstance(value, str):
        return [t.strip() for t in value.split(",") if t.strip()]
    if isinstance(value, list) and all(isinstance(t, str) for t in value):
        return [t.strip() for t in value]
    return None


def check_tools(field: str, value: object, rep: Report) -> None:
    items = tool_list(value)
    if items is None:
        rep.error(f"{field}: must be a comma-separated string or a YAML list of strings")
        return
    if field == "tools" and value in ([], "") :
        rep.warn("tools: empty value launches the agent with NO tools; omit the field to "
                 "inherit all tools")
    for item in items:
        if not TOOL_NAME.match(item):
            rep.warn(f"{field}: '{item}' does not look like a tool name")
        if item.lower() in {"read", "grep", "glob", "edit", "write", "bash"} and item[0].islower():
            rep.error(f"{field}: '{item}' is lowercase; tool names are case-sensitive "
                      f"(use '{item.capitalize()}')")
        if field == "disallowedTools" and re.match(r"^\w+\(.+\)$", item) and not item.startswith("mcp__"):
            rep.warn(f"disallowedTools: '{item}' removes the WHOLE tool, not just the "
                     "matching commands; use permissions.deny or a PreToolUse hook instead")
        if item == "Skill" and field == "tools":
            rep.warn("tools: listing 'Skill' does not preload skills; use the 'skills' field")


def validate(path: Path, plugin: bool) -> Report:
    rep = Report()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        rep.error(f"cannot read file: {exc}")
        return rep

    if text.startswith("﻿"):
        rep.error("file starts with a byte-order mark; the opening '---' must be the first "
                  "character of the file")
        text = text.lstrip("﻿")

    fm_text, body, closed = split_frontmatter(text)
    if fm_text is None:
        rep.error("opening '---' is not the first line: Claude Code treats this file as "
                  "documentation, not an agent")
        return rep
    if not closed:
        rep.error("no closing '---': the body would be read as YAML")

    if "\t" in fm_text:
        rep.warn("frontmatter contains a tab character; YAML indentation must use spaces")

    try:
        data = yaml.safe_load(fm_text)
    except yaml.YAMLError as exc:
        rep.error(f"YAML does not parse, so Claude Code reads no fields and skips the "
                  f"file: {str(exc).splitlines()[0] if str(exc) else exc}")
        hint = re.search(r"^\s*description:\s*[^>|'\"\n][^\n]*:\s", fm_text, re.M)
        if hint:
            rep.error("hint: 'description' contains ': ' unquoted; quote the value or use "
                      "folded style (description: >)")
        return rep
    if data is None:
        data = {}
    if not isinstance(data, dict):
        rep.error("frontmatter is not a YAML mapping")
        return rep

    # --- required fields and name rules -------------------------------------------
    name = data.get("name")
    if name is None:
        rep.error("no 'name': Claude Code treats this file as documentation, not an agent"
                  + (" (a plugin agent would load under its filename)" if plugin else ""))
    elif not isinstance(name, str) or not name.strip():
        rep.error("name: must be a non-empty string")
    else:
        if name.startswith("-"):
            rep.error(f"name '{name}' starts with '-': the file is skipped")
        if ":" in name:
            rep.error(f"name '{name}' contains ':' (reserved for plugin scoping): the file "
                      "is skipped (v2.1.218+)")
        if re.search(r"[^\w .-]", name) and ":" not in name:
            rep.warn(f"name '{name}' has unusual characters; prefer lowercase-with-hyphens")

    desc = data.get("description")
    if desc is None or (isinstance(desc, str) and not desc.strip()):
        rep.error("no 'description': Claude Code skips the file (reason only in the debug log)")
    elif not isinstance(desc, str):
        rep.error("description: must be a string")
    else:
        if len(desc) > 1200:
            rep.warn(f"description is {len(desc)} characters; all descriptions together "
                     "over ~15,000 tokens trigger a startup warning")
        if len(desc.split()) < 6:
            rep.warn("description is very short; Claude decides delegation from it, so "
                     "say what the agent does and when to use it")

    # --- unknown / mis-cased fields -----------------------------------------------
    for key in data:
        if key in KNOWN_FIELDS:
            continue
        if key in FOREIGN_FIELDS:
            rep.warn(f"'{key}': {FOREIGN_FIELDS[key]}")
            continue
        lowered = re.sub(r"[-_\s]", "", str(key)).lower()
        if lowered in CASE_INSENSITIVE:
            rep.error(f"unknown field '{key}': ignored silently. Did you mean "
                      f"'{CASE_INSENSITIVE[lowered]}'? (fields are camelCase and case-sensitive)")
            continue
        close = difflib.get_close_matches(str(key), KNOWN_FIELDS, n=1, cutoff=0.7)
        hint = f" Did you mean '{close[0]}'?" if close else ""
        rep.warn(f"unknown field '{key}': Claude Code ignores it without an error.{hint}")

    # --- tools ---------------------------------------------------------------------
    if "tools" in data:
        check_tools("tools", data["tools"], rep)
    if "disallowedTools" in data:
        check_tools("disallowedTools", data["disallowedTools"], rep)
    t, d = tool_list(data.get("tools")), tool_list(data.get("disallowedTools"))
    if t and d:
        both = sorted(set(t) & set(d))
        if both:
            rep.warn(f"tools listed in both tools and disallowedTools are removed: {both}")
        if not set(t) - set(d):
            rep.error("disallowedTools removes every entry in tools: the agent launches "
                      "with no tools")
    if t:
        for entry in t:
            m = re.match(r"^(Agent|Task)\((.*)\)$", entry)
            if m:
                rep.warn(f"tools: '{entry}' type allowlist only applies when this file runs "
                         "as the main session (claude --agent); it is ignored in a subagent")
        if all(e.split("(")[0] in {"Agent", "Task"} for e in t):
            rep.warn("tools contains only Agent: at the nesting depth limit it resolves to "
                     "no tools and launch is refused; add at least one other tool")
        if "memory" in data and not {"Read", "Write", "Edit"} <= set(t):
            rep.warn("memory is set: Read, Write, and Edit are enabled automatically for "
                     "the memory directory even though tools omits them")

    # --- enums and scalars -----------------------------------------------------------
    model = data.get("model")
    if model is not None:
        if not isinstance(model, str):
            rep.error("model: must be a string")
        elif model not in MODEL_ALIASES and not model.startswith(
                ("claude-", "us.", "eu.", "anthropic.", "arn:")):
            rep.warn(f"model: '{model}' is not an alias or a claude-* ID; check it against "
                     "the values `claude --model` accepts")

    pm = data.get("permissionMode")
    if pm is not None:
        if pm not in PERMISSION_MODES:
            rep.error(f"permissionMode: '{pm}' invalid; use one of {sorted(PERMISSION_MODES)}")
        elif pm == "manual":
            rep.warn("permissionMode 'manual' alias needs Claude Code v2.1.200+; 'default' "
                     "works everywhere")
        elif pm == "bypassPermissions":
            rep.warn("permissionMode bypassPermissions only takes effect when the parent "
                     "session is already in that mode; avoid it in shared agent files")
        if pm in PERMISSION_MODES and pm != "bypassPermissions":
            rep.warn("permissionMode is overridden when the parent session is in auto, "
                     "acceptEdits, or bypassPermissions (the agent uses the parent's mode)")

    mt = data.get("maxTurns")
    if mt is not None and (isinstance(mt, bool) or not isinstance(mt, int) or mt < 1):
        rep.error("maxTurns: must be a positive integer")

    for field in ("background", "omitClaudeMd"):
        if field in data and not isinstance(data[field], bool):
            rep.error(f"{field}: must be true or false (unquoted)")

    mem = data.get("memory")
    if mem is not None and mem not in MEMORY_SCOPES:
        rep.error(f"memory: '{mem}' invalid; use one of {sorted(MEMORY_SCOPES)}")

    eff = data.get("effort")
    if eff is not None and eff not in EFFORTS:
        rep.error(f"effort: '{eff}' invalid; use one of {sorted(EFFORTS)}")

    iso = data.get("isolation")
    if iso is not None and iso != "worktree":
        rep.error(f"isolation: '{iso}' invalid; the only value is 'worktree'")

    col = data.get("color")
    if col is not None and col not in COLORS:
        rep.error(f"color: '{col}' invalid; use one of {sorted(COLORS)}")

    skills = data.get("skills")
    if skills is not None and not (isinstance(skills, list) and all(isinstance(s, str) for s in skills)):
        rep.error("skills: must be a YAML list of skill names")

    mcp = data.get("mcpServers")
    if mcp is not None:
        if not isinstance(mcp, list):
            rep.error("mcpServers: must be a list of server names or one-key inline definitions")
        else:
            for entry in mcp:
                if isinstance(entry, dict) and len(entry) != 1:
                    rep.error("mcpServers: an inline definition must be a one-key mapping "
                              "{server-name: config}")
                elif not isinstance(entry, (str, dict)):
                    rep.error(f"mcpServers: unsupported entry {entry!r}")

    hooks = data.get("hooks")
    if hooks is not None:
        if not isinstance(hooks, dict):
            rep.error("hooks: must be a mapping of event name to a list of matcher groups")
        else:
            for event, groups in hooks.items():
                if event == "Stop":
                    rep.warn("hooks.Stop is converted to SubagentStop when run as a subagent")
                if not isinstance(groups, list):
                    rep.error(f"hooks.{event}: must be a list")
                    continue
                for g in groups:
                    if not isinstance(g, dict) or "hooks" not in g:
                        rep.error(f"hooks.{event}: each entry needs a 'hooks' list "
                                  "(matcher is optional)")
        if not plugin:
            rep.warn("hooks in a project-level agent are skipped until the folder containing "
                     "this file is trusted (the agent still runs)")

    exp = data.get("experimental")
    if exp is not None:
        if not isinstance(exp, dict):
            rep.error("experimental: must be a mapping, e.g. experimental: {cacheTtl: 5m}")
        elif exp.get("cacheTtl") not in (None, "5m", "1h"):
            rep.warn("experimental.cacheTtl: only '5m' or '1h' are honoured; anything else "
                     "is ignored")
    if "cacheTtl" in data:
        rep.error("cacheTtl must be nested under 'experimental', not top-level")

    for f, ver in MIN_VERSIONS.items():
        if f in data:
            rep.warn(f"'{f}' requires Claude Code {ver} or later; older versions ignore it")

    if plugin:
        for f in sorted(PLUGIN_IGNORED & set(data)):
            rep.warn(f"'{f}' is ignored for plugin agents; copy the file to .claude/agents/ "
                     "if you need it")

    # --- body ------------------------------------------------------------------------
    if not body.strip():
        rep.warn("empty prompt body: the agent gets no system prompt of its own")
    if "initialPrompt" in data:
        rep.warn("initialPrompt only fires when this file runs as the main session "
                 "(claude --agent); it does nothing for a delegated subagent")
    return rep


def collect(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        elif p.is_file():
            files.append(p)
        else:
            sys.exit(f"not found: {p}")
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("paths", nargs="+", help="agent file(s) or directory of agent files")
    ap.add_argument("--plugin", action="store_true",
                    help="treat the files as plugin agents (hooks, mcpServers, permissionMode ignored)")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    args = ap.parse_args()

    n_err = n_warn = 0
    files = collect(args.paths)
    if not files:
        print("no .md files found")
        return 0
    seen: dict[str, Path] = {}
    for f in files:
        rep = validate(f, args.plugin)
        # duplicate-name detection across the scanned set
        try:
            fm, _, _ = split_frontmatter(f.read_text(encoding="utf-8"))
            nm = (yaml.safe_load(fm) or {}).get("name") if fm is not None else None
        except Exception:
            nm = None
        if isinstance(nm, str):
            if nm in seen:
                rep.error(f"duplicate name '{nm}' also used by {seen[nm]}: only one loads")
            else:
                seen[nm] = f
        status = "FAIL" if rep.errors else ("WARN" if rep.warnings else "ok")
        print(f"[{status}] {f}")
        for m in rep.errors:
            print(f"    error: {m}")
        for m in rep.warnings:
            print(f"    warn:  {m}")
        n_err += len(rep.errors)
        n_warn += len(rep.warnings)
    print(f"\n{len(files)} file(s), {n_err} error(s), {n_warn} warning(s)")
    return 1 if n_err or (args.strict and n_warn) else 0


if __name__ == "__main__":
    sys.exit(main())

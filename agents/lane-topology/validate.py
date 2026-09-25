#!/usr/bin/env python3
"""Validate the Lane Topology agent definitions.

Every check here exists because the corresponding mistake was actually made in this
repository and was not visible by reading the files. None of them are schema checks
for their own sake.

    python3 agents/lane-topology/validate.py

Exits 0 when clean, 1 on any FAIL. Requires PyYAML (already a MkDocs dependency).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML not found. Activate the repo venv: source .venv/bin/activate")

ROOT = Path(__file__).resolve().parent
OPENCODE, COPILOT = ROOT / "opencode", ROOT / "copilot"

# The one agent allowed to hold each otherwise-forbidden capability.
SOLE_HOLDER = {"subagent": "conductor", "webfetch": "researcher", "websearch": "researcher"}

# Agents that must not hold shell at all.
NO_BASH = {"planner", "scribe", "researcher"}

# Commands no agent may run, in bare and wrapped form. Checked by resolving them
# through the real pattern semantics rather than grepping for pattern strings —
# a deny that is present but shadowed by a later rule is exactly the failure mode
# this repository already hit once.
FORBIDDEN_CMDS = [
    "git merge origin/x", "git rebase -i HEAD~2", "git reset --hard HEAD~1",
    "git cherry-pick abc123", "git push --force origin topic",
    "git push origin +topic", "gh pr merge 1",
    "cd sub && git merge origin/x", "true; git reset --hard HEAD~1",
    "ls | gh pr merge 1",
]

# Agents whose `edit` must not reach the working tree, and the path that proves it.
SANDBOXED_EDIT = {"planner", "investigator", "researcher"}

# OpenCode V2 permission action -> Copilot tool alias, per AGENTS.md.
TOOL_MAP = {
    "read": "read",
    "edit": "edit",
    "shell": "execute",
    "grep": "search",
    "webfetch": "web",
    "websearch": "web",
    "subagent": "agent",
}

# OpenCode V2 base policy. Every agent starts with it, and agent rules are appended
# after it — so an action no agent rule mentions is ALLOWED. This is the default-allow
# trap, and V2 kept it: it is now an explicit first rule instead of an implicit default.
BASE_POLICY = [
    {"action": "*", "resource": "*", "effect": "allow"},
    {"action": "external_directory", "resource": "*", "effect": "ask"},
    {"action": "read", "resource": "*.env", "effect": "ask"},
    {"action": "read", "resource": "*.env.*", "effect": "ask"},
    {"action": "read", "resource": "*.env.example", "effect": "allow"},
]

# V1 fields and action names. The agents are native V2; a V1 field that slips back
# in is either silently translated or ignored, and neither is what the file says.
LEGACY_FIELDS = {"permission", "tools", "name", "prompt", "disable", "maxSteps",
                 "temperature", "top_p", "variant"}
LEGACY_ACTIONS = {"bash": "shell", "task": "subagent", "write": "edit",
                  "patch": "edit", "list": "glob"}

# The V2 shell scanner checks each command of a compound command separately.
SHELL_SEPARATORS = re.compile(r"\s*(?:&&|\|\||;|\|)\s*")

failures: list[str] = []
checks_run = 0


def check(ok: bool, label: str, detail: str = "") -> None:
    global checks_run
    checks_run += 1
    if not ok:
        failures.append(f"{label}{': ' + detail if detail else ''}")


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit(f"FATAL: no frontmatter in {path}")
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def pattern_matches(pattern: str, value: str, shell: bool = False) -> bool:
    """V2 whole-value wildcards: `*` is zero or more characters including `/`, `?`
    is exactly one. A shell pattern ending in ` *` also matches the bare command."""
    regex = "".join(
        "." if c == "?" else ".*" if c == "*" else re.escape(c) for c in pattern
    )
    if re.fullmatch(regex, value, re.S):
        return True
    return shell and pattern.endswith(" *") and pattern_matches(pattern[:-2], value)


def resolve(rules: list, action: str, value: str) -> str:
    """Resolve one (action, resource) check the way OpenCode V2 does.

    LAST matching rule wins (so the catch-all goes first), starting from the base
    policy, whose first rule allows everything.
    """
    verdict = "ask"  # V2's no-match default; unreachable while the base policy leads
    for rule in BASE_POLICY + rules:
        if pattern_matches(rule["action"], action) and pattern_matches(
            rule["resource"], value, shell=(action == "shell")
        ):
            verdict = rule["effect"]
    return verdict


def resolve_shell(rules: list, command: str, split: bool) -> str:
    """Whole-string resolution (split=False), or per-command as the V2 scanner does
    (split=True): any deny denies, otherwise any ask asks, otherwise allow."""
    parts = SHELL_SEPARATORS.split(command) if split else [command]
    verdicts = {resolve(rules, "shell", part) for part in parts if part}
    for effect in ("deny", "ask"):
        if effect in verdicts:
            return effect
    return "allow"


def mentions(rules: list, action: str) -> bool:
    return any(rule["action"] == action for rule in rules)


def granted(rules: list, action: str) -> bool:
    """True if `action` is allowed for at least one resource.

    The base policy allows every action, so an action no rule mentions is granted.
    Three agents once held unrestricted shell and all eight could dispatch subagents,
    purely by omission, and no file said so. Otherwise: the last catch-all rule for
    the action sets the baseline, and any specific allow AFTER it re-opens the action
    for that resource. Specific rules before the catch-all are shadowed by it.
    """
    baseline, after = True, []
    for rule in rules:
        if not pattern_matches(rule["action"], action):
            continue
        if rule["resource"] == "*":
            baseline, after = rule["effect"] == "allow", []
        else:
            after.append(rule)
    return baseline or any(rule["effect"] == "allow" for rule in after)


def main() -> int:
    oc_files = sorted(OPENCODE.glob("*.md"))
    if not oc_files:
        sys.exit(f"FATAL: no agents found in {OPENCODE}")

    agents = {p.stem: frontmatter(p) for p in oc_files}

    # 1. Copilot mirror exists, and bodies are character-identical.
    for name, (_, body) in agents.items():
        mirror = COPILOT / f"{name}.agent.md"
        check(mirror.exists(), "missing Copilot mirror", name)
        if mirror.exists():
            check(frontmatter(mirror)[1] == body, "body drift (opencode vs copilot)", name)

    # 2. Exactly one primary, and the harness points at it.
    primaries = [n for n, (fm, _) in agents.items() if fm.get("mode") == "primary"]
    check(primaries == ["conductor"], "expected exactly one primary (conductor)", str(primaries))

    harness = ROOT.parent.parent / "harness" / "opencode-lane" / "opencode.jsonc"
    if harness.exists():
        m = re.search(r'"default_agent"\s*:\s*"([^"]+)"', harness.read_text())
        check(bool(m), "no default_agent in harness config")
        if m:
            check(
                m.group(1) in primaries,
                "default_agent must name a primary-mode agent",
                m.group(1),
            )

    # 2b. Native V2 frontmatter: an ordered `permissions` list of well-formed rules,
    #     and no V1 field or action name that V2 would translate or ignore.
    rules_of: dict[str, list] = {}
    for name, (fm, _) in agents.items():
        for field in sorted(LEGACY_FIELDS & set(fm)):
            check(False, f"{name}: V1 field '{field}'", "use the V2 equivalent")
        rules = fm.get("permissions")
        check(isinstance(rules, list) and bool(rules), f"{name}: no 'permissions' list")
        rules = rules if isinstance(rules, list) else []
        for rule in rules:
            ok = isinstance(rule, dict) and set(rule) == {"action", "resource", "effect"}
            check(ok, f"{name}: malformed rule", repr(rule))
            if ok:
                check(rule["effect"] in ("allow", "ask", "deny"), f"{name}: bad effect", repr(rule))
                legacy = LEGACY_ACTIONS.get(rule["action"])
                check(not legacy, f"{name}: V1 action '{rule['action']}'", f"use '{legacy}'")
        rules_of[name] = [r for r in rules if isinstance(r, dict) and "action" in r]

    # 3. The default-allow trap: capabilities must be denied by NAME, not by omission.
    for name in agents:
        for key, holder in SOLE_HOLDER.items():
            if name != holder:
                check(not granted(rules_of[name], key), f"{name} holds '{key}'", "deny it explicitly")

    # 3b. Shell: the three non-shell agents hold none, and nobody can mutate git.
    #     Forbidden commands must be denied BOTH whole-string and per-command. The V2
    #     scanner splits compound commands, but a command it cannot split is checked
    #     whole — and then only the wrapped denies (`* git *`) stand in the way.
    for name in agents:
        rules = rules_of[name]
        if name in NO_BASH:
            check(not granted(rules, "shell"), f"{name} must deny 'shell'")
            continue
        for cmd in FORBIDDEN_CMDS:
            for split in (False, True):
                check(
                    resolve_shell(rules, cmd, split) == "deny",
                    f"{name} can run", f"{cmd!r} ({'per-command' if split else 'whole string'})",
                )

    # 3c. Sandboxed edit really is sandboxed — and the grant is not shadowed.
    #     Rule order was inverted here once, denying every path including the one
    #     the grant existed for, with no error raised anywhere.
    for name in SANDBOXED_EDIT:
        if name not in agents:
            continue
        rules = rules_of[name]
        check(resolve(rules, "edit", "src/main.py") == "deny", f"{name} can edit the working tree")
        check(
            resolve(rules, "edit", ".agent-output/notes.md") == "allow",
            f"{name} cannot write .agent-output",
            "catch-all '*' must come FIRST, specific grant after",
        )

    # 3d. The Conductor ships, so its allowlist is the one that must be exact.
    cond_rules = rules_of["conductor"]
    for cmd, want in [
        ("git checkout -b fix/x", "allow"),
        ("git checkout -- .", "deny"),          # discards work as surely as reset
        ("git commit -m msg", "allow"),
        ("git commit --amend -m msg", "deny"),  # rewrites history
        ("git add src/a.py", "allow"),
        # Every stage-everything form. `git add .` alone is not enough — `./`, `:/`,
        # `-u` and the `--` separator all stage broadly and every one of them fell
        # through the allow base until it was checked here.
        ("git add -A", "deny"),                 # contradicts "exactly the CHANGED list"
        ("git add --all", "deny"),
        ("git add .", "deny"),
        ("git add ./", "deny"),
        ("git add :/", "deny"),
        ("git add -u", "deny"),
        ("git add --update", "deny"),
        ("git add -- .", "deny"),
        ("git push origin fix/x", "allow"),
        ("git revert --no-edit abc123", "allow"),
        ("gh pr create --title x", "allow"),
        ("npm test", "deny"),                   # the Conductor does not run tests
    ]:
        for split in (False, True):
            check(
                resolve_shell(cond_rules, cmd, split) == want,
                f"conductor: {cmd!r} should be {want}",
                "per-command" if split else "whole string",
            )

    # 4. Subagents declare hidden; every agent declares a model.
    for name, (fm, _) in agents.items():
        check("model" in fm, "no model pin", name)
        if fm.get("mode") == "subagent":
            check("hidden" in fm, "subagent missing 'hidden'", name)

    # 4b. The Copilot frontmatter label and the body's "Current model:" agree.
    #     These drifted apart on the two GPT agents — spaces in the header, hyphens
    #     in the rationale — which is invisible until someone scans one and trusts it.
    for name in agents:
        mirror = COPILOT / f"{name}.agent.md"
        if not mirror.exists():
            continue
        cfm, body = frontmatter(mirror)
        label = str(cfm.get("model", "")).replace(" (copilot)", "").strip()
        m = re.search(r"^\*\*(?:Current model|Model):\*\*\s*([^·\n]+)", body, re.M)
        if m and label:
            check(
                m.group(1).strip() == label,
                f"{name}: frontmatter model '{label}'",
                f"body says '{m.group(1).strip()}'",
            )

    # 5. Cross-family review (invariants 3 and 4). The Investigator counts as a
    #    producer: its MAP enters the Verifier's brief and the Verifier is told not to
    #    rebuild it, so a same-family map would void the independence.
    def family(model: str) -> str:
        m = model.lower()
        for token, fam in (
            ("claude", "claude"), ("gpt", "gpt"), ("gemini", "gemini"),
        ):
            if token in m:
                return fam
        return "unknown"

    fams = {n: family(fm.get("model", "")) for n, (fm, _) in agents.items()}
    verifier_family = fams.get("verifier")
    check(verifier_family != "unknown", "cannot determine verifier family")
    for producer in ("planner", "builder", "mechanic", "scribe", "investigator"):
        if producer in fams:
            check(
                fams[producer] != verifier_family,
                f"{producer} shares the Verifier's family ({verifier_family})",
                "pin it to another family — do not relax the requirement",
            )
    check(fams.get("builder") == "gpt", "builder must stay GPT-pinned (invariant 4)")

    # 6. Copilot tools list agrees with the OpenCode grants it mirrors.
    for name, (fm, _) in agents.items():
        mirror = COPILOT / f"{name}.agent.md"
        if not mirror.exists():
            continue
        cfm, _ = frontmatter(mirror)
        tools = set(cfm.get("tools") or [])
        rules = rules_of[name]
        for key, alias in TOOL_MAP.items():
            if not mentions(rules, key):
                continue  # unlisted in OpenCode; nothing asserted to mirror
            if granted(rules, key):
                check(alias in tools, f"{name}: '{key}' allowed but Copilot lacks '{alias}'")
            elif not any(granted(rules, k) for k, a in TOOL_MAP.items() if a == alias):
                check(alias not in tools, f"{name}: '{key}' denied but Copilot grants '{alias}'")

    # 7. The Conductor's routing table only names agents that exist.
    conductor_body = agents["conductor"][1]
    section = re.search(r"## Routing Table(.*?)^## ", conductor_body, re.S | re.M)
    check(bool(section), "cannot locate Routing Table in conductor.md")
    if section:
        listed = set(re.findall(r"^\|\s*`([a-z]+)`\s*\|", section.group(1), re.M))
        check(bool(listed), "routing table parsed but empty")
        for ident in listed:
            check(ident in agents, "routing table names a nonexistent agent", ident)
        for name in agents:
            if name != "conductor":
                check(name in listed, "agent missing from routing table", name)

    # 8. Roster table in AGENTS.md matches the real model pins.
    doc = (ROOT / "AGENTS.md").read_text()
    rows = re.findall(r"^\|\s*`(\w+)\.md`\s*\|\s*`(\w+)`\s*\|\s*`([^`]+)`\s*\|", doc, re.M)
    check(bool(rows), "cannot parse roster table in AGENTS.md")
    documented = {ident: model for _, ident, model in rows}
    for name, (fm, _) in agents.items():
        actual = fm.get("model", "").split("/")[-1]
        if name in documented:
            check(
                documented[name] == actual,
                f"AGENTS.md roster says {name} is '{documented[name]}'",
                f"frontmatter says '{actual}'",
            )
        else:
            check(False, "agent missing from AGENTS.md roster table", name)

    print(f"lane-topology: {checks_run} checks across {len(agents)} agents")
    if failures:
        print(f"\n{len(failures)} FAILED:\n")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("all clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

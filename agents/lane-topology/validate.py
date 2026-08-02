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
SOLE_HOLDER = {"task": "conductor", "webfetch": "researcher", "websearch": "researcher"}

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

# OpenCode permission -> Copilot tool alias, per AGENTS.md.
TOOL_MAP = {
    "read": "read",
    "edit": "edit",
    "bash": "execute",
    "grep": "search",
    "webfetch": "web",
    "websearch": "web",
    "task": "agent",
}

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


def resolve(rules, value: str) -> str:
    """Resolve `value` against an OpenCode permission block.

    Two semantics matter and both have burned this repo: LAST matching rule wins
    (so the catch-all goes first), and patterns match the ENTIRE command string
    (so a deny anchored at the start is evaded by any prefix).
    """
    if not isinstance(rules, dict):
        return rules if isinstance(rules, str) else "allow"
    verdict = "allow"  # absent block == granted
    for pattern, action in rules.items():
        regex = "".join(
            "." if c == "?" else ".*" if c == "*" else re.escape(c) for c in pattern
        )
        if re.fullmatch(regex, value):
            verdict = action
    return verdict


def granted(perm: dict, key: str) -> bool:
    """True if `key` is effectively allowed.

    OpenCode defaults UNLISTED keys to allow. This default is the single most
    expensive thing about the format: three agents once held unrestricted shell and
    all eight could dispatch subagents, purely by omission, and no file said so.
    """
    if key not in perm:
        return True  # absent == granted
    v = perm[key]
    if isinstance(v, dict):
        return any(a == "allow" for a in v.values())
    return v == "allow"


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

    # 3. The default-allow trap: capabilities must be denied by NAME, not by omission.
    for name, (fm, _) in agents.items():
        perm = fm.get("permission") or {}
        for key, holder in SOLE_HOLDER.items():
            if name != holder:
                check(not granted(perm, key), f"{name} holds '{key}'", "deny it explicitly")

    # 3b. Shell: the three non-shell agents hold none, and nobody can mutate git.
    for name, (fm, _) in agents.items():
        perm = fm.get("permission") or {}
        bash = perm.get("bash", {})
        if name in NO_BASH:
            check(not granted(perm, "bash"), f"{name} must have 'bash: deny'")
            continue
        for cmd in FORBIDDEN_CMDS:
            check(resolve(bash, cmd) == "deny", f"{name} can run", repr(cmd))

    # 3c. Sandboxed edit really is sandboxed — and the grant is not shadowed.
    #     Rule order was inverted here once, denying every path including the one
    #     the grant existed for, with no error raised anywhere.
    for name in SANDBOXED_EDIT:
        if name not in agents:
            continue
        edit = (agents[name][0].get("permission") or {}).get("edit", {})
        check(resolve(edit, "src/main.py") == "deny", f"{name} can edit the working tree")
        check(
            resolve(edit, ".agent-output/notes.md") == "allow",
            f"{name} cannot write .agent-output",
            "catch-all '*' must come FIRST, specific grant after",
        )

    # 3d. The Conductor ships, so its allowlist is the one that must be exact.
    cond_bash = (agents["conductor"][0].get("permission") or {}).get("bash", {})
    for cmd, want in [
        ("git checkout -b fix/x", "allow"),
        ("git checkout -- .", "deny"),          # discards work as surely as reset
        ("git commit -m msg", "allow"),
        ("git commit --amend -m msg", "deny"),  # rewrites history
        ("git add src/a.py", "allow"),
        ("git add -A", "deny"),                 # contradicts "exactly the CHANGED list"
        ("git push origin fix/x", "allow"),
        ("git revert --no-edit abc123", "allow"),
        ("gh pr create --title x", "allow"),
        ("npm test", "deny"),                   # the Conductor does not run tests
    ]:
        check(resolve(cond_bash, cmd) == want, f"conductor: {cmd!r} should be {want}")

    # 4. Subagents declare hidden; every agent declares a model.
    for name, (fm, _) in agents.items():
        check("model" in fm, "no model pin", name)
        if fm.get("mode") == "subagent":
            check("hidden" in fm, "subagent missing 'hidden'", name)

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
        perm = fm.get("permission") or {}
        for key, alias in TOOL_MAP.items():
            if key not in perm:
                continue  # unlisted in OpenCode; nothing asserted to mirror
            if granted(perm, key):
                check(alias in tools, f"{name}: '{key}' allowed but Copilot lacks '{alias}'")
            elif not any(granted(perm, k) for k, a in TOOL_MAP.items() if a == alias):
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

#!/usr/bin/env python3
"""Validate documentation coverage for repository agents, harnesses, and skills.

Run with ``--write`` after changing an agent roster or client format to refresh
the generated inventory, roster, and install blocks in the topology pages and the
domain specialist roster in ``docs/agents/index.md``. CI runs in check mode (the
default) and fails when generated content or catalog coverage is stale.

``--write`` is all or nothing: it validates every source and every destination first,
and rewrites documentation only when the whole run is clean.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML not found. Activate the repo venv: source .venv/bin/activate")


SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[1]
GITHUB_ROOT = "https://github.com/CowboyLogic/ai-dev"


@dataclass(frozen=True)
class Topology:
    name: str
    canonical: str
    formats: dict[str, str]
    harness: str
    documentation: str


TOPOLOGIES = {
    "lane-topology": Topology(
        name="lane-topology",
        canonical="opencode",
        formats={"opencode": "*.md", "copilot": "*.agent.md"},
        harness="opencode-lane",
        documentation="docs/agents/lane-topology.md",
    ),
    "matrix-topology": Topology(
        name="matrix-topology",
        canonical="opencode",
        formats={
            "opencode": "*.md",
            "claude": "*.agent.md",
            "copilot": "*.agent.md",
        },
        harness="opencode",
        documentation="docs/agents/matrix-topology.md",
    ),
}

CLIENT_NAMES = {
    "opencode": "OpenCode",
    "claude": "Claude Code",
    "copilot": "GitHub Copilot",
}

failures: list[str] = []
checks_run = 0
# Regenerated documentation, held back until every validation has passed.
# Each entry is (text as validated, regenerated text).
pending_writes: dict[Path, tuple[str, str]] = {}


def check(ok: bool, label: str, detail: str = "") -> None:
    global checks_run
    checks_run += 1
    if not ok:
        failures.append(f"{label}{': ' + detail if detail else ''}")


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"no YAML frontmatter in {path.relative_to(ROOT)}")
    data = yaml.safe_load(match.group(1))
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError(
            f"frontmatter in {path.relative_to(ROOT)} must be a mapping, "
            f"not {type(data).__name__}"
        )
    return data, text[match.end() :]


def agent_id(path: Path) -> str:
    return path.name.removesuffix(".agent.md").removesuffix(".md")


def markdown_cell(value: object) -> str:
    return " ".join(str(value).split()).replace("|", r"\|")


def has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def strip_jsonc(text: str) -> str:
    """Remove comments and trailing commas from JSONC, leaving string contents alone."""

    def string_end(source: str, start: int) -> int:
        i = start + 1
        while i < len(source) and source[i] != '"':
            i += 2 if source[i] == "\\" else 1
        return min(i + 1, len(source))

    without_comments: list[str] = []
    i = 0
    while i < len(text):
        if text[i] == '"':
            end = string_end(text, i)
            without_comments.append(text[i:end])
            i = end
        elif text.startswith("//", i):
            while i < len(text) and text[i] != "\n":
                i += 1
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end == -1:
                raise ValueError("unterminated block comment")
            # A comment separates tokens: tru/**/e must not become true.
            without_comments.append(" ")
            i = end + 2
        else:
            without_comments.append(text[i])
            i += 1
    stripped = "".join(without_comments)

    result: list[str] = []
    i = 0
    while i < len(stripped):
        if stripped[i] == '"':
            end = string_end(stripped, i)
            result.append(stripped[i:end])
            i = end
        elif stripped[i] == ",":
            k = i + 1
            while k < len(stripped) and stripped[k].isspace():
                k += 1
            if not (k < len(stripped) and stripped[k] in "}]"):
                result.append(",")
            i += 1
        else:
            result.append(stripped[i])
            i += 1
    return "".join(result)


def reject_constant(name: str) -> None:
    raise ValueError(f"{name} is not valid JSON")


def load_jsonc(path: Path) -> dict:
    relative = path.relative_to(ROOT)
    try:
        # json.loads accepts NaN and Infinity by default; JSON does not.
        data = json.loads(
            strip_jsonc(path.read_text(encoding="utf-8-sig")),
            parse_constant=reject_constant,
        )
    except ValueError as error:
        raise ValueError(f"{relative}: invalid JSONC ({error})") from error
    if not isinstance(data, dict):
        raise ValueError(f"{relative}: top level must be an object")
    return data


def role_summary(description: object) -> str:
    """Short role label: the first sentence of an agent description."""
    text = " ".join(str(description).split())
    match = re.match(r"(.+?[.!?])(?=\s|$)", text)
    return (match.group(1) if match else text).rstrip(".")


def display_name(identifier: str, metadata: dict, topology: Topology) -> str:
    # OpenCode V2 frontmatter has no `name`; fall back to a mirror that carries one.
    if metadata.get("name"):
        return str(metadata["name"])
    for format_name, pattern in topology.formats.items():
        mirror = ROOT / "agents" / topology.name / format_name / pattern.replace("*", identifier)
        if format_name != topology.canonical and mirror.is_file():
            name = frontmatter(mirror)[0].get("name")
            if name:
                return str(name)
    return identifier.replace("-", " ").title()


def topology_agents(topology: Topology) -> dict[str, tuple[Path, dict, str]]:
    folder = ROOT / "agents" / topology.name / topology.canonical
    pattern = topology.formats[topology.canonical]
    agents: dict[str, tuple[Path, dict, str]] = {}
    for path in sorted(folder.glob(pattern)):
        metadata, body = frontmatter(path)
        agents[agent_id(path)] = (path, metadata, body)
    return agents


def render_inventory(topology: Topology) -> str:
    lines = [
        "<!-- artifact-sync:inventory:start -->",
        "| Kind | Name | Status | Source |",
        "|---|---|---|---|",
    ]
    ordered_formats = [topology.canonical] + sorted(
        name for name in topology.formats if name != topology.canonical
    )
    for format_name in ordered_formats:
        status = "Canonical" if format_name == topology.canonical else "Derived mirror"
        source = f"agents/{topology.name}/{format_name}"
        lines.append(
            f"| Client | {CLIENT_NAMES[format_name]} | {status} | "
            f"[{format_name}/]({GITHUB_ROOT}/tree/main/{source}) |"
        )
    harness_source = f"harness/{topology.harness}"
    lines.append(
        f"| Harness | OpenCode | Runtime configuration | "
        f"[{topology.harness}/]({GITHUB_ROOT}/tree/main/{harness_source}) |"
    )
    lines.append("<!-- artifact-sync:inventory:end -->")
    return "\n".join(lines)


def render_roster(
    topology: Topology, agents: dict[str, tuple[Path, dict, str]]
) -> str:
    lines = [
        "<!-- artifact-sync:roster:start -->",
        "| Agent | Model | Role | Source |",
        "|---|---|---|---|",
    ]
    for identifier, (path, metadata, _) in ordered_agents(agents):
        name = markdown_cell(display_name(identifier, metadata, topology))
        model = markdown_cell(metadata.get("model", "Not pinned"))
        role = markdown_cell(role_summary(metadata.get("description", "")))
        relative_path = path.relative_to(ROOT).as_posix()
        lines.append(
            f"| **{name}** | `{model}` | {role} | "
            f"[{path.name}]({GITHUB_ROOT}/blob/main/{relative_path}) |"
        )
    lines.append("<!-- artifact-sync:roster:end -->")
    return "\n".join(lines)


def ordered_agents(
    agents: dict[str, tuple[Path, dict, str]]
) -> list[tuple[str, tuple[Path, dict, str]]]:
    return sorted(
        agents.items(),
        key=lambda item: (item[1][1].get("mode") != "primary", item[0]),
    )


def render_install(
    topology: Topology, agents: dict[str, tuple[Path, dict, str]]
) -> str:
    pattern = topology.formats["copilot"]
    lines = [
        "<!-- artifact-sync:install:start -->",
        "```bash",
        f"# Install all {len(agents)} agents",
    ]
    for identifier, _ in ordered_agents(agents):
        file_name = pattern.replace("*", identifier)
        lines.append(
            f"gh copilot agent install CowboyLogic/ai-dev/agents/"
            f"{topology.name}/copilot/{file_name}"
        )
    lines.extend(["```", "<!-- artifact-sync:install:end -->"])
    return "\n".join(lines)


def specialist_agents() -> dict[str, tuple[Path, dict, str]]:
    agents: dict[str, tuple[Path, dict, str]] = {}
    for path in sorted((ROOT / "agents").glob("*.agent.md")):
        metadata, body = frontmatter(path)
        agents[agent_id(path)] = (path, metadata, body)
    return agents


def render_specialists(agents: dict[str, tuple[Path, dict, str]]) -> str:
    lines = [
        "<!-- artifact-sync:specialists:start -->",
        "| Agent | Role |",
        "|---|---|",
    ]
    # Single-skill agents first, then the coordinators that delegate to them.
    ordered = sorted(agents.items(), key=lambda item: ("agents" in item[1][1], item[0]))
    for identifier, (path, metadata, _) in ordered:
        role = markdown_cell(role_summary(metadata.get("description", "")))
        relative_path = path.relative_to(ROOT).as_posix()
        lines.append(f"| [**{identifier}**]({GITHUB_ROOT}/blob/main/{relative_path}) | {role} |")
    lines.append("<!-- artifact-sync:specialists:end -->")
    return "\n".join(lines)


def block_span(text: str, block_name: str) -> tuple[int, int]:
    """Span of the one generated block, markers included; raise unless the markers are sound."""
    start_marker = f"<!-- artifact-sync:{block_name}:start -->"
    end_marker = f"<!-- artifact-sync:{block_name}:end -->"
    starts = [m.start() for m in re.finditer(re.escape(start_marker), text)]
    ends = [m.start() for m in re.finditer(re.escape(end_marker), text)]
    if len(starts) != 1 or len(ends) != 1:
        raise ValueError(
            f"artifact-sync:{block_name} needs exactly one start and one end marker, "
            f"found {len(starts)} start and {len(ends)} end"
        )
    if starts[0] > ends[0]:
        raise ValueError(f"artifact-sync:{block_name} end marker precedes its start marker")
    return starts[0], ends[0] + len(end_marker)


def generated_block(text: str, block_name: str) -> str:
    start, end = block_span(text, block_name)
    return text[start:end]


def replace_generated_block(text: str, block_name: str, replacement: str) -> str:
    start, end = block_span(text, block_name)
    return text[:start] + replacement + text[end:]


def sync_blocks(doc_path: Path, expected: dict[str, str], write: bool) -> None:
    """Check each generated block in a page, or stage its regeneration for --write.

    Malformed markers fail in both modes. Stale content fails only in check mode,
    because refreshing it is what --write is for. Nothing is written here: the staged
    page is written by main() once the whole run has validated.
    """
    label = doc_path.relative_to(ROOT).as_posix()
    original = text = doc_path.read_text(encoding="utf-8")
    try:
        spans = sorted((*block_span(text, name), name) for name in expected)
    except ValueError as error:
        check(False, f"{label}: {error}")
        return
    for (_, previous_end, previous), (start, _, name) in zip(spans, spans[1:]):
        if start < previous_end:
            check(False, f"{label}: artifact-sync:{name} block overlaps artifact-sync:{previous}")
            return
    for block_name, replacement in expected.items():
        try:
            if write:
                text = replace_generated_block(text, block_name, replacement)
                check(True, label)
            else:
                check(
                    generated_block(text, block_name) == replacement,
                    f"{label}: stale generated {block_name}",
                    f"run {SCRIPT.relative_to(ROOT)} --write",
                )
        except ValueError as error:
            check(False, f"{label}: {error}")
            return
    if write:
        pending_writes[doc_path] = (original, text)


def flush_writes(pending: dict[Path, tuple[str, str]]) -> list[str]:
    """Write staged pages, unless one changed on disk since it was validated.

    Every page is re-read first, so a page edited mid-run aborts the whole write
    rather than being overwritten. If a write itself fails, the pages already
    written are restored, so no page is left half refreshed.
    """
    errors: list[str] = []
    for path, (validated, _) in pending.items():
        try:
            if path.read_text(encoding="utf-8") != validated:
                errors.append(f"{path} changed while the validator was running; rerun it")
        except OSError as error:
            errors.append(f"cannot re-read {path}: {error}")
    if errors:
        return errors
    written: list[Path] = []
    try:
        for path, (validated, regenerated) in pending.items():
            if regenerated != validated:
                path.write_text(regenerated, encoding="utf-8")
                written.append(path)
    except OSError as error:
        errors.append(f"write failed, restoring the pages already written: {error}")
        for path in written:
            try:
                path.write_text(pending[path][0], encoding="utf-8")
            except OSError as restore_error:
                errors.append(f"could not restore {path}: {restore_error}")
    return errors


def validate_topology(topology: Topology, write: bool) -> None:
    topology_root = ROOT / "agents" / topology.name
    agents = topology_agents(topology)
    check(bool(agents), f"{topology.name}: canonical roster is empty")
    for identifier, (path, metadata, _) in agents.items():
        check(
            has_text(metadata.get("description")),
            f"{topology.name}: {identifier} needs a non-empty string description",
            path.relative_to(ROOT).as_posix(),
        )

    canonical_ids = set(agents)
    for format_name, pattern in topology.formats.items():
        folder = topology_root / format_name
        files = {agent_id(path): path for path in folder.glob(pattern)}
        check(
            set(files) == canonical_ids,
            f"{topology.name}: {format_name} roster drift",
            f"expected {sorted(canonical_ids)}, found {sorted(files)}",
        )
        if format_name == topology.canonical:
            continue
        for identifier in sorted(canonical_ids & set(files)):
            metadata, body = frontmatter(files[identifier])
            canonical_metadata = agents[identifier][1]
            check(
                body == agents[identifier][2],
                f"{topology.name}: {identifier} body differs in {format_name}",
            )
            check(
                metadata.get("description") == canonical_metadata.get("description"),
                f"{topology.name}: {identifier} description differs in {format_name}",
            )

    harness = ROOT / "harness" / topology.harness
    check(harness.is_dir(), f"{topology.name}: missing harness", str(harness))
    harness_config = harness / "opencode.jsonc"
    check(harness_config.is_file(), f"{topology.name}: missing opencode.jsonc")
    if harness_config.is_file():
        default_agent = load_jsonc(harness_config).get("default_agent")
        check(
            has_text(default_agent),
            f"{topology.name}: harness has no top-level default_agent string",
        )
        if has_text(default_agent):
            check(
                default_agent in canonical_ids,
                f"{topology.name}: harness default_agent is not in the roster",
                default_agent,
            )

    sync_blocks(
        ROOT / topology.documentation,
        {
            "inventory": render_inventory(topology),
            "roster": render_roster(topology, agents),
            "install": render_install(topology, agents),
        },
        write,
    )


def validate_specialists(write: bool) -> None:
    agents = specialist_agents()
    check(bool(agents), "domain specialist roster is empty")
    for identifier, (path, metadata, _) in agents.items():
        check(
            has_text(metadata.get("description")),
            f"domain specialist {identifier} needs a non-empty string description",
            str(path.relative_to(ROOT)),
        )
    sync_blocks(
        ROOT / "docs/agents/index.md", {"specialists": render_specialists(agents)}, write
    )


class _MkdocsLoader(yaml.SafeLoader):
    """Safe loader that tolerates mkdocs.yml's custom tags (!!python/name and friends)."""


_MkdocsLoader.add_multi_constructor("", lambda loader, suffix, node: None)


def nav_files(node: object) -> set[str]:
    """Every page path named anywhere in a MkDocs nav tree."""
    if isinstance(node, str):
        return {node}
    if isinstance(node, list):
        return set().union(*(nav_files(item) for item in node)) if node else set()
    if isinstance(node, dict):
        return set().union(*(nav_files(item) for item in node.values())) if node else set()
    return set()


def validate_skills() -> None:
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    skill_ids = {path.parent.name for path in skill_files}
    check(bool(skill_ids), "skill inventory is empty")
    for path in skill_files:
        try:
            metadata, _ = frontmatter(path)
        except ValueError as error:
            check(False, f"skill frontmatter is invalid: {error}")
            continue
        check(
            metadata.get("name") == path.parent.name,
            "skill frontmatter name does not match directory",
            str(path.relative_to(ROOT)),
        )

    docs_text = (ROOT / "docs/skills/index.md").read_text()
    documented = set(
        re.findall(
            rf"{re.escape(GITHUB_ROOT)}/tree/main/skills/([a-z0-9-]+)", docs_text
        )
    )
    check(
        documented == skill_ids,
        "docs/skills/index.md skill coverage drift",
        f"expected {sorted(skill_ids)}, found {sorted(documented)}",
    )

    mkdocs = yaml.load((ROOT / "mkdocs.yml").read_text(), Loader=_MkdocsLoader)
    nav = nav_files(mkdocs.get("nav", []) if isinstance(mkdocs, dict) else [])
    for identifier in sorted(skill_ids):
        page = f"skills/{identifier}.md"
        check(
            (ROOT / "docs" / page).is_file(),
            f"skill {identifier} has no overview page",
            f"docs/{page}",
        )
        check(
            page in nav,
            f"skill {identifier} overview page is not in the mkdocs.yml nav",
            page,
        )

    readme_text = (ROOT / "skills/README.md").read_text()
    readme_links = set(
        re.findall(r"\]\(([a-z0-9-]+)/(?:README|SKILL)\.md\)", readme_text)
    )
    check(
        readme_links == skill_ids,
        "skills/README.md skill coverage drift",
        f"expected {sorted(skill_ids)}, found {sorted(readme_links)}",
    )

    catalog = yaml.safe_load((ROOT / "cerebro-catalog.yaml").read_text())
    if catalog is None:
        catalog = {}
    if not isinstance(catalog, dict):
        check(False, "cerebro-catalog.yaml must be a mapping")
        return
    artifacts = catalog.get("artifacts", [])
    if not isinstance(artifacts, list):
        check(False, "cerebro-catalog.yaml artifacts must be a list")
        return
    skill_artifacts = []
    for position, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            check(False, f"cerebro-catalog.yaml artifact {position} must be a mapping")
        elif artifact.get("type") == "skill":
            if has_text(artifact.get("id")):
                skill_artifacts.append(artifact)
            else:
                check(
                    False,
                    f"cerebro-catalog.yaml skill artifact {position} needs a non-empty string id",
                    repr(artifact.get("id")),
                )
    catalog_ids = [artifact["id"] for artifact in skill_artifacts]
    check(
        len(catalog_ids) == len(set(catalog_ids)),
        "cerebro-catalog.yaml contains duplicate skill ids",
    )
    check(
        set(catalog_ids) == skill_ids,
        "cerebro-catalog.yaml skill coverage drift",
        f"expected {sorted(skill_ids)}, found {sorted(catalog_ids)}",
    )
    for artifact in skill_artifacts:
        identifier = artifact["id"]
        check(
            artifact.get("source") == f"skills/{identifier}",
            f"cerebro-catalog.yaml has stale source for {identifier}",
            str(artifact.get("source")),
        )


def validate_discovery() -> None:
    discovered_topologies = {
        path.name for path in (ROOT / "agents").glob("*-topology") if path.is_dir()
    }
    check(
        discovered_topologies == set(TOPOLOGIES),
        "topology validator configuration drift",
        f"expected {sorted(TOPOLOGIES)}, found {sorted(discovered_topologies)}",
    )
    # opencode-samples holds sample configs for readers, not a topology harness.
    discovered_harnesses = {
        path.name
        for path in (ROOT / "harness").glob("opencode*")
        if path.is_dir() and path.name != "opencode-samples"
    }
    configured_harnesses = {topology.harness for topology in TOPOLOGIES.values()}
    check(
        discovered_harnesses == configured_harnesses,
        "harness validator configuration drift",
        f"expected {sorted(configured_harnesses)}, found {sorted(discovered_harnesses)}",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="refresh generated roster, inventory, and install blocks",
    )
    args = parser.parse_args()

    validate_discovery()
    for topology in TOPOLOGIES.values():
        try:
            validate_topology(topology, args.write)
        except (OSError, ValueError, yaml.YAMLError) as error:
            failures.append(f"{topology.name}: {error}")
    try:
        validate_specialists(args.write)
    except (OSError, ValueError, yaml.YAMLError) as error:
        failures.append(f"domain specialists: {error}")
    try:
        validate_skills()
    except (OSError, ValueError, yaml.YAMLError) as error:
        failures.append(f"skills: {error}")

    print(f"artifact-sync: {checks_run} checks")
    if failures:
        print(f"\n{len(failures)} FAILED:\n")
        for failure in failures:
            print(f"  - {failure}")
        if args.write:
            print("\nno documentation was changed")
        return 1
    if args.write:
        errors = flush_writes(pending_writes)
        if errors:
            print("\n".join(f"  - {error}" for error in errors))
            print("\nno documentation was changed")
            return 1
        print("generated documentation blocks refreshed")
    else:
        print("all clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

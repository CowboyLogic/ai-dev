#!/usr/bin/env python3
"""Validate documentation coverage for repository agents, harnesses, and skills.

Run with ``--write`` after changing a topology roster or client format to refresh
the generated inventory and roster blocks in the corresponding documentation page.
CI runs in check mode (the default) and fails when generated content or catalog
coverage is stale.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML not found. Activate the repo venv: source .venv/bin/activate")


ROOT = Path(__file__).resolve().parents[1]
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
            "opencode": "*.agent.md",
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
    data = yaml.safe_load(match.group(1)) or {}
    return data, text[match.end() :]


def agent_id(path: Path) -> str:
    return path.name.removesuffix(".agent.md").removesuffix(".md")


def markdown_cell(value: object) -> str:
    return " ".join(str(value).split()).replace("|", r"\|")


def display_name(identifier: str, metadata: dict) -> str:
    return str(metadata.get("name") or identifier.replace("-", " ").title())


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
        "| Agent | Model | Job | Source |",
        "|---|---|---|---|",
    ]
    ordered = sorted(
        agents.items(),
        key=lambda item: (item[1][1].get("mode") != "primary", item[0]),
    )
    for identifier, (path, metadata, _) in ordered:
        name = markdown_cell(display_name(identifier, metadata))
        model = markdown_cell(metadata.get("model", "Not pinned"))
        description = markdown_cell(metadata.get("description", ""))
        relative_path = path.relative_to(ROOT).as_posix()
        lines.append(
            f"| **{name}** | `{model}` | {description} | "
            f"[{path.name}]({GITHUB_ROOT}/blob/main/{relative_path}) |"
        )
    lines.append("<!-- artifact-sync:roster:end -->")
    return "\n".join(lines)


def generated_block(text: str, block_name: str) -> str | None:
    pattern = re.compile(
        rf"<!-- artifact-sync:{block_name}:start -->.*?"
        rf"<!-- artifact-sync:{block_name}:end -->",
        re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(0) if match else None


def replace_generated_block(text: str, block_name: str, replacement: str) -> str:
    current = generated_block(text, block_name)
    if current is None:
        raise ValueError(f"missing artifact-sync:{block_name} markers")
    return text.replace(current, replacement)


def validate_topology(topology: Topology, write: bool) -> None:
    topology_root = ROOT / "agents" / topology.name
    agents = topology_agents(topology)
    check(bool(agents), f"{topology.name}: canonical roster is empty")

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
        match = re.search(
            r'"default_agent"\s*:\s*"([^"]+)"', harness_config.read_text()
        )
        check(bool(match), f"{topology.name}: harness has no default_agent")
        if match:
            check(
                match.group(1) in canonical_ids,
                f"{topology.name}: harness default_agent is not in the roster",
                match.group(1),
            )

    doc_path = ROOT / topology.documentation
    text = doc_path.read_text()
    expected = {
        "inventory": render_inventory(topology),
        "roster": render_roster(topology, agents),
    }
    if write:
        for block_name, replacement in expected.items():
            text = replace_generated_block(text, block_name, replacement)
        doc_path.write_text(text)
    else:
        for block_name, replacement in expected.items():
            check(
                generated_block(text, block_name) == replacement,
                f"{topology.name}: stale or missing generated {block_name}",
                f"run {Path(__file__).relative_to(ROOT)} --write",
            )


def validate_skills() -> None:
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    skill_ids = {path.parent.name for path in skill_files}
    check(bool(skill_ids), "skill inventory is empty")
    for path in skill_files:
        metadata, _ = frontmatter(path)
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

    readme_text = (ROOT / "skills/README.md").read_text()
    readme_links = set(
        re.findall(r"\]\(([a-z0-9-]+)/(?:README|SKILL)\.md\)", readme_text)
    )
    check(
        readme_links == skill_ids,
        "skills/README.md skill coverage drift",
        f"expected {sorted(skill_ids)}, found {sorted(readme_links)}",
    )

    catalog = yaml.safe_load((ROOT / "cerebro-catalog.yaml").read_text()) or {}
    skill_artifacts = [
        artifact
        for artifact in catalog.get("artifacts", [])
        if artifact.get("type") == "skill"
    ]
    catalog_ids = [artifact.get("id") for artifact in skill_artifacts]
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
        identifier = artifact.get("id")
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
        f"expected {sorted(discovered_topologies)}, configured {sorted(TOPOLOGIES)}",
    )
    discovered_harnesses = {
        path.name for path in (ROOT / "harness").glob("opencode*") if path.is_dir()
    }
    configured_harnesses = {topology.harness for topology in TOPOLOGIES.values()}
    check(
        discovered_harnesses == configured_harnesses,
        "harness validator configuration drift",
        f"expected {sorted(discovered_harnesses)}, configured {sorted(configured_harnesses)}",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="refresh generated topology inventory and roster blocks",
    )
    args = parser.parse_args()

    validate_discovery()
    for topology in TOPOLOGIES.values():
        try:
            validate_topology(topology, args.write)
        except (OSError, ValueError, yaml.YAMLError) as error:
            failures.append(f"{topology.name}: {error}")
    try:
        validate_skills()
    except (OSError, ValueError, yaml.YAMLError) as error:
        failures.append(f"skills: {error}")

    print(f"artifact-sync: {checks_run} checks")
    if failures:
        print(f"\n{len(failures)} FAILED:\n")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    if args.write:
        print("generated documentation blocks refreshed")
    else:
        print("all clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

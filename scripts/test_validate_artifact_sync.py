"""Regression tests for scripts/validate_artifact_sync.py.

Each test runs the script as a subprocess inside a throwaway copy of the files it
reads, so it checks the real exit status, output, and whether any file changed.

    python -m unittest discover -s scripts -v
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPT_NAME = "validate_artifact_sync.py"

LANE_DOC = "docs/agents/lane-topology.md"
INDEX_DOC = "docs/agents/index.md"
LANE_CANONICAL = "agents/lane-topology/opencode/conductor.md"
LANE_MIRROR = "agents/lane-topology/copilot/conductor.agent.md"
LANE_HARNESS = "harness/opencode-lane/opencode.jsonc"


def build_template(dest: Path) -> None:
    """Copy just the files the validator reads."""
    for rel in ("agents", "harness/opencode", "harness/opencode-lane", "docs/agents", "docs/skills"):
        shutil.copytree(REPO / rel, dest / rel)
    for skill in (REPO / "skills").glob("*/SKILL.md"):
        target = dest / "skills" / skill.parent.name / "SKILL.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill, target)
    for rel in ("skills/README.md", "mkdocs.yml", "cerebro-catalog.yaml"):
        shutil.copy2(REPO / rel, dest / rel)
    (dest / "scripts").mkdir()
    shutil.copy2(REPO / "scripts" / SCRIPT_NAME, dest / "scripts" / SCRIPT_NAME)


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


class ValidatorTest(unittest.TestCase):
    template: Path
    _template_dir: tempfile.TemporaryDirectory

    @classmethod
    def setUpClass(cls) -> None:
        cls._template_dir = tempfile.TemporaryDirectory()
        cls.template = Path(cls._template_dir.name)
        build_template(cls.template)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._template_dir.cleanup()

    def setUp(self) -> None:
        self._work = tempfile.TemporaryDirectory()
        self.addCleanup(self._work.cleanup)
        self.root = Path(self._work.name) / "repo"
        shutil.copytree(self.template, self.root)

    # -- helpers ------------------------------------------------------------

    def load_module(self):
        sys.path.insert(0, str(REPO / "scripts"))
        try:
            import validate_artifact_sync as module
        finally:
            sys.path.remove(str(REPO / "scripts"))
        return module

    def run_validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / SCRIPT_NAME), *args],
            cwd=self.root,
            capture_output=True,
            text=True,
        )

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        (self.root / rel).write_text(text, encoding="utf-8")

    def edit_frontmatter(self, rel: str, change) -> None:
        text = self.read(rel)
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        data = yaml.safe_load(match.group(1))
        change(data)
        dumped = yaml.safe_dump(data, sort_keys=False, width=10_000)
        self.write(rel, f"---\n{dumped}---\n{text[match.end():]}")

    def assert_fails_cleanly(self, result: subprocess.CompletedProcess[str]) -> None:
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, output)
        self.assertNotIn("Traceback", output)
        self.assertIn("FAILED", result.stdout)

    def assert_write_changes_nothing(self, *, expect_fail: bool = True) -> subprocess.CompletedProcess[str]:
        before = snapshot(self.root)
        result = self.run_validator("--write")
        self.assertEqual(snapshot(self.root), before, "--write changed files")
        if expect_fail:
            self.assert_fails_cleanly(result)
        return result

    # -- baseline -----------------------------------------------------------

    def test_clean_repo_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("all clean", result.stdout)

    def test_runs_through_a_symlinked_path(self) -> None:
        link = self.root.parent / "linked"
        os.symlink(self.root, link)
        result = subprocess.run(
            [sys.executable, str(link / "scripts" / SCRIPT_NAME)],
            cwd=link,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # -- 1. write mode must not change docs when inputs are invalid ----------

    def test_write_refuses_when_canonical_roster_is_missing(self) -> None:
        shutil.rmtree(self.root / "agents/lane-topology/opencode")
        self.assert_write_changes_nothing()

    def test_write_writes_nothing_when_a_later_section_fails(self) -> None:
        # Stale generated block (fixable) plus a skills coverage failure (not fixable by --write).
        self.write(LANE_DOC, self.read(LANE_DOC).replace("| Model | Role |", "| Model | Job |"))
        index = self.read("docs/skills/index.md")
        self.write("docs/skills/index.md", index.replace("tree/main/skills/google-style-docs", "tree/main/skills/zzz"))
        self.assert_write_changes_nothing()

    def test_write_refreshes_stale_blocks_and_is_idempotent(self) -> None:
        self.write(LANE_DOC, self.read(LANE_DOC).replace("| Model | Role |", "| Model | Job |"))
        self.write(INDEX_DOC, self.read(INDEX_DOC).replace("| Agent | Role |", "| Agent | Job |"))
        self.assertEqual(self.run_validator().returncode, 1)

        result = self.run_validator("--write")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.run_validator().returncode, 0)
        self.assertIn("## What Problem Does This Solve?", self.read(LANE_DOC))

        refreshed = snapshot(self.root)
        self.assertEqual(self.run_validator("--write").returncode, 0)
        self.assertEqual(snapshot(self.root), refreshed)

    def test_edited_install_line_fails_and_write_restores_it(self) -> None:
        line = "gh copilot agent install CowboyLogic/ai-dev/agents/lane-topology/copilot/conductor.agent.md"
        self.assertIn(line, self.read(LANE_DOC))
        self.write(LANE_DOC, self.read(LANE_DOC).replace(line, line.replace("conductor", "wrong")))
        self.assertEqual(self.run_validator().returncode, 1)
        self.assertEqual(self.run_validator("--write").returncode, 0)
        self.assertIn(line, self.read(LANE_DOC))

    def test_new_topology_agent_appears_in_roster_and_install_blocks(self) -> None:
        shutil.copy2(self.root / LANE_CANONICAL, self.root / "agents/lane-topology/opencode/zeta.md")
        shutil.copy2(self.root / LANE_MIRROR, self.root / "agents/lane-topology/copilot/zeta.agent.md")
        self.assertEqual(self.run_validator().returncode, 1)
        self.assertEqual(self.run_validator("--write").returncode, 0)
        doc = self.read(LANE_DOC)
        self.assertIn("lane-topology/copilot/zeta.agent.md", doc)
        self.assertIn("[zeta.md]", doc)
        self.assertRegex(doc, r"# Install all \d+ agents")
        self.assertEqual(self.run_validator().returncode, 0)

    def test_write_refuses_a_page_edited_after_validation(self) -> None:
        module = self.load_module()
        page = self.root / "page.md"
        page.write_text("validated\n")
        pending = {page: ("validated\n", "regenerated\n")}
        page.write_text("edited by someone else\n")
        errors = module.flush_writes(pending)
        self.assertEqual(len(errors), 1, errors)
        self.assertEqual(page.read_text(), "edited by someone else\n")

    def test_failed_write_restores_pages_already_written(self) -> None:
        module = self.load_module()
        first, second = self.root / "first.md", self.root / "second.md"
        first.write_text("one\n")
        second.write_text("two\n")
        second.chmod(0o444)
        self.addCleanup(second.chmod, 0o644)
        if os.access(second, os.W_OK):
            self.skipTest("file permissions are not enforced for this user")
        pending = {first: ("one\n", "ONE\n"), second: ("two\n", "TWO\n")}
        errors = module.flush_writes(pending)
        self.assertTrue(errors)
        self.assertEqual(first.read_text(), "one\n")
        self.assertEqual(second.read_text(), "two\n")

    def test_page_deleted_after_validation_is_reported_not_raised(self) -> None:
        module = self.load_module()
        page = self.root / "gone.md"
        errors = module.flush_writes({page: ("x\n", "y\n")})
        self.assertEqual(len(errors), 1, errors)

    # -- 2. unexpected YAML shapes -------------------------------------------

    def test_list_frontmatter_is_reported_not_a_traceback(self) -> None:
        self.write(LANE_CANONICAL, "---\n- list-instead-of-mapping\n---\nBody\n")
        result = self.run_validator()
        self.assert_fails_cleanly(result)
        self.assertIn("conductor.md", result.stdout)
        self.assert_write_changes_nothing()

    def test_null_skill_id_in_catalog_is_reported(self) -> None:
        catalog = yaml.safe_load(self.read("cerebro-catalog.yaml"))
        next(a for a in catalog["artifacts"] if a.get("type") == "skill")["id"] = None
        self.write("cerebro-catalog.yaml", yaml.safe_dump(catalog, sort_keys=False))
        self.assert_fails_cleanly(self.run_validator())
        self.assert_write_changes_nothing()

    def test_catalog_that_is_not_a_mapping_is_reported(self) -> None:
        self.write("cerebro-catalog.yaml", "- just\n- a list\n")
        self.assert_fails_cleanly(self.run_validator())

    # -- 3. harness default_agent must come from the active top-level key ----

    def test_commented_default_agent_does_not_shadow_the_active_value(self) -> None:
        self.write(LANE_HARNESS, '{\n  // "default_agent": "conductor",\n  "default_agent": "does-not-exist"\n}\n')
        result = self.run_validator()
        self.assert_fails_cleanly(result)
        self.assertIn("does-not-exist", result.stdout)

    def test_nested_default_agent_does_not_satisfy_the_top_level_setting(self) -> None:
        self.write(LANE_HARNESS, '{\n  "agent": { "default_agent": "conductor" }\n}\n')
        self.assert_fails_cleanly(self.run_validator())

    def test_malformed_jsonc_is_reported(self) -> None:
        self.write(LANE_HARNESS, '{\n  "default_agent": "conductor"\n')
        self.assert_fails_cleanly(self.run_validator())

    def test_non_string_default_agent_is_reported(self) -> None:
        self.write(LANE_HARNESS, '{ "default_agent": 7 }\n')
        self.assert_fails_cleanly(self.run_validator())

    def test_non_standard_json_constants_are_rejected(self) -> None:
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                self.write(
                    LANE_HARNESS,
                    '{ "default_agent": "conductor", "limit": %s }\n' % constant,
                )
                result = self.run_validator()
                self.assert_fails_cleanly(result)
                self.assertIn(constant, result.stdout)

    def test_block_comment_cannot_join_two_halves_of_a_token(self) -> None:
        self.write(
            LANE_HARNESS,
            '{ "default_agent": "conductor", "limit": tru/*note*/e }\n',
        )
        self.assert_fails_cleanly(self.run_validator())

    def test_jsonc_comments_urls_and_trailing_commas_still_parse(self) -> None:
        self.write(
            LANE_HARNESS,
            '{\n  "$schema": "https://example.test/a//b", // trailing note\n'
            '  /* block */ "default_agent": "conductor",\n  "list": [1, 2,],\n}\n',
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # -- 4. marker structure --------------------------------------------------

    def test_nested_blocks_fail_and_write_changes_nothing(self) -> None:
        def marker(name: str, edge: str) -> str:
            return f"<!-- artifact-sync:{name}:{edge} -->"

        text = self.read(LANE_DOC)
        for edge in ("start", "end"):
            text = text.replace(marker("install", edge), "")
        text = text.replace(marker("roster", "start"), marker("install", "start") + marker("roster", "start"))
        text = text.replace(marker("roster", "end"), marker("roster", "end") + marker("install", "end"))
        self.write(LANE_DOC, text)
        self.assert_fails_cleanly(self.run_validator())
        self.assert_write_changes_nothing()

    def test_duplicate_block_with_different_content_fails(self) -> None:
        stale = "\n<!-- artifact-sync:roster:start -->\nSTALE DUPLICATE\n<!-- artifact-sync:roster:end -->\n"
        self.write(LANE_DOC, self.read(LANE_DOC) + stale)
        self.assert_fails_cleanly(self.run_validator())
        self.assert_write_changes_nothing()

    def test_duplicate_block_with_identical_content_fails(self) -> None:
        text = self.read(LANE_DOC)
        block = re.search(
            r"<!-- artifact-sync:roster:start -->.*?<!-- artifact-sync:roster:end -->", text, re.DOTALL
        ).group(0)
        self.write(LANE_DOC, text + "\n" + block + "\n")
        self.assert_fails_cleanly(self.run_validator())

    def test_reversed_markers_fail(self) -> None:
        text = self.read(LANE_DOC)
        swapped = text.replace("roster:start", "roster:TMP").replace("roster:end", "roster:start").replace("roster:TMP", "roster:end")
        self.write(LANE_DOC, swapped)
        self.assert_fails_cleanly(self.run_validator())
        self.assert_write_changes_nothing()

    def test_missing_end_marker_fails(self) -> None:
        self.write(LANE_DOC, self.read(LANE_DOC).replace("<!-- artifact-sync:install:end -->", ""))
        self.assert_fails_cleanly(self.run_validator())
        self.assert_write_changes_nothing()

    def test_write_preserves_text_outside_the_block(self) -> None:
        text = self.read(LANE_DOC)
        self.write(LANE_DOC, text.replace("| Model | Role |", "| Model | Job |"))
        self.assertEqual(self.run_validator("--write").returncode, 0)
        self.assertEqual(self.read(LANE_DOC), text)

    # -- 5. skill overview pages and navigation -------------------------------

    def test_missing_overview_page_fails(self) -> None:
        (self.root / "docs/skills/git-commit-messages.md").unlink()
        result = self.run_validator()
        self.assert_fails_cleanly(result)
        self.assertIn("git-commit-messages", result.stdout)

    def test_overview_page_missing_from_nav_fails(self) -> None:
        lines = self.read("mkdocs.yml").splitlines(keepends=True)
        kept = [line for line in lines if "skills/git-commit-messages.md" not in line]
        self.assertLess(len(kept), len(lines))
        self.write("mkdocs.yml", "".join(kept))
        result = self.run_validator()
        self.assert_fails_cleanly(result)
        self.assertIn("git-commit-messages", result.stdout)

    def test_mkdocs_custom_yaml_tags_are_tolerated(self) -> None:
        self.write("mkdocs.yml", self.read("mkdocs.yml") + "\nextra_probe: !!python/name:material.extensions.emoji.twemoji\n")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    # -- 6. descriptions -------------------------------------------------------

    def assert_description_rejected(self) -> None:
        # Refresh the generated blocks first, as the review's reproduction does, so a
        # stale block cannot be what makes the check fail.
        self.run_validator("--write")
        result = self.run_validator()
        self.assert_fails_cleanly(result)
        self.assertIn("description", result.stdout)

    def test_topology_agent_without_a_description_fails_even_when_mirrors_match(self) -> None:
        for rel in (LANE_CANONICAL, LANE_MIRROR):
            self.edit_frontmatter(rel, lambda data: data.pop("description"))
        self.assert_description_rejected()

    def test_whitespace_only_description_fails(self) -> None:
        for rel in (LANE_CANONICAL, LANE_MIRROR):
            self.edit_frontmatter(rel, lambda data: data.update(description="   "))
        self.assert_description_rejected()

    def test_non_string_specialist_description_fails(self) -> None:
        self.edit_frontmatter("agents/code-reviewer.agent.md", lambda data: data.update(description=["a", "b"]))
        self.assert_description_rejected()

    def test_valid_description_generates_a_first_sentence_role(self) -> None:
        for rel in (LANE_CANONICAL, LANE_MIRROR):
            self.edit_frontmatter(rel, lambda data: data.update(description="Routes work. Never writes code."))
        self.assertEqual(self.run_validator("--write").returncode, 0)
        self.assertIn("| Routes work |", self.read(LANE_DOC))
        self.assertEqual(self.run_validator().returncode, 0)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Unit tests for the skill router script, run against libraries built in a temp directory."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import skill_router as router  # noqa: E402


def add_skill(root: Path, relative: str, frontmatter: str | None, body: str = "# Body\n") -> Path:
    skill_dir = root / relative
    skill_dir.mkdir(parents=True, exist_ok=True)
    text = body if frontmatter is None else f"---\n{frontmatter}\n---\n\n{body}"
    (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
    return skill_dir


def run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = router.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class LibraryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()


class FrontmatterTests(unittest.TestCase):
    def test_plain_scalars(self) -> None:
        fields = router.read_frontmatter("---\nname: demo\ndescription: Does a thing.\n---\nbody\n")
        self.assertEqual(fields, {"name": "demo", "description": "Does a thing."})

    def test_quoted_scalars(self) -> None:
        text = "---\nname: 'it''s'\ndescription: \"Say \\\"hi\\\": now\"\n---\n"
        fields = router.read_frontmatter(text)
        self.assertEqual(fields["name"], "it's")
        self.assertEqual(fields["description"], 'Say "hi": now')

    def test_double_quoted_whitespace_escapes_become_spaces(self) -> None:
        fields = router.read_frontmatter('---\ndescription: "First.\\nSecond\\tthird.\\n"\n---\n')
        self.assertEqual(fields["description"], "First. Second third.")

    def test_folded_and_literal_blocks_collapse_to_one_line(self) -> None:
        for indicator in (">", ">-", "|", "|+"):
            with self.subTest(indicator=indicator):
                text = f"---\nname: demo\ndescription: {indicator}\n  First line\n  second line.\n\n  Third.\nlicense: MIT\n---\n"
                fields = router.read_frontmatter(text)
                self.assertEqual(fields["description"], "First line second line. Third.")
                self.assertEqual(fields["license"], "MIT")

    def test_plain_scalar_continues_on_indented_lines(self) -> None:
        fields = router.read_frontmatter("---\ndescription: First\n  second\nname: demo\n---\n")
        self.assertEqual(fields["description"], "First second")

    def test_plain_scalar_drops_a_trailing_comment(self) -> None:
        fields = router.read_frontmatter("---\nname: demo # the name\ndescription: Fix issue#5\n---\n")
        self.assertEqual(fields["name"], "demo")
        self.assertEqual(fields["description"], "Fix issue#5")

    def test_nested_mapping_does_not_leak_into_other_fields(self) -> None:
        text = "---\nname: demo\nmetadata:\n  description: nested\n  version: 1\ndescription: Real.\n---\n"
        self.assertEqual(router.read_frontmatter(text)["description"], "Real.")

    def test_byte_order_mark_and_crlf(self) -> None:
        fields = router.read_frontmatter("﻿---\r\nname: demo\r\ndescription: Works.\r\n---\r\nbody\r\n")
        self.assertEqual(fields, {"name": "demo", "description": "Works."})

    def test_missing_or_unclosed_frontmatter_is_empty(self) -> None:
        self.assertEqual(router.read_frontmatter("# Just a heading\n"), {})
        self.assertEqual(router.read_frontmatter("---\nname: demo\n"), {})
        self.assertEqual(router.read_frontmatter(""), {})


class IndexTests(LibraryTestCase):
    def test_finds_skills_at_any_depth(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        add_skill(self.root, "repo/skills/beta", "name: beta\ndescription: B.")
        skills = router.refresh_index(self.root)
        self.assertEqual([(s["name"], s["dir"]) for s in skills], [("alpha", "alpha"), ("beta", "repo/skills/beta")])

    def test_does_not_descend_into_a_skill_or_pruned_directories(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        add_skill(self.root, "alpha/references/nested", "name: nested\ndescription: N.")
        add_skill(self.root, "repo/.git/hidden", "name: hidden\ndescription: H.")
        add_skill(self.root, "repo/node_modules/pkg", "name: pkg\ndescription: P.")
        self.assertEqual([s["name"] for s in router.refresh_index(self.root)], ["alpha"])

    def test_name_falls_back_to_the_directory(self) -> None:
        add_skill(self.root, "no-frontmatter", None)
        add_skill(self.root, "no-name", "description: Has a description.")
        skills = {s["name"]: s for s in router.refresh_index(self.root)}
        self.assertEqual(skills["no-frontmatter"]["description"], "")
        self.assertEqual(skills["no-name"]["description"], "Has a description.")

    def test_records_harness_variables(self) -> None:
        add_skill(self.root, "args", "name: args\ndescription: A.", "Run $ARGUMENTS from ${CLAUDE_SKILL_DIR}.\n")
        add_skill(self.root, "plain", "name: plain\ndescription: P.", "Run scripts/go.py with $1.\n")
        skills = {s["name"]: s for s in router.refresh_index(self.root)}
        self.assertEqual(skills["args"]["harness_variables"], ["$ARGUMENTS", "${CLAUDE_SKILL_DIR}"])
        self.assertEqual(skills["plain"]["harness_variables"], [])

    def test_unchanged_skills_are_served_from_the_index(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        router.refresh_index(self.root)
        with patch.object(router, "build_entry", side_effect=AssertionError("re-read")):
            self.assertEqual([s["name"] for s in router.refresh_index(self.root)], ["alpha"])

    def test_changed_added_and_removed_skills_are_picked_up(self) -> None:
        alpha = add_skill(self.root, "alpha", "name: alpha\ndescription: Old.")
        add_skill(self.root, "beta", "name: beta\ndescription: B.")
        router.refresh_index(self.root)

        (alpha / "SKILL.md").write_text("---\nname: alpha\ndescription: New and longer.\n---\n", encoding="utf-8")
        (self.root / "beta" / "SKILL.md").unlink()
        add_skill(self.root, "gamma", "name: gamma\ndescription: G.")
        skills = {s["name"]: s["description"] for s in router.refresh_index(self.root)}
        self.assertEqual(skills, {"alpha": "New and longer.", "gamma": "G."})

        stored = json.loads((self.root / router.INDEX_NAME).read_text(encoding="utf-8"))
        self.assertEqual([s["name"] for s in stored["skills"]], ["alpha", "gamma"])

    def test_corrupt_or_outdated_index_is_rebuilt(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        index_path = self.root / router.INDEX_NAME
        for content in ("not json", json.dumps({"version": 0, "skills": [{"dir": "alpha"}]}), "[]"):
            with self.subTest(content=content):
                index_path.write_text(content, encoding="utf-8")
                self.assertEqual([s["name"] for s in router.refresh_index(self.root)], ["alpha"])
                self.assertEqual(json.loads(index_path.read_text(encoding="utf-8"))["version"], router.INDEX_VERSION)

    def test_unwritable_index_still_returns_skills(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        err = io.StringIO()
        with patch.object(router.os, "replace", side_effect=OSError("read-only")), contextlib.redirect_stderr(err):
            skills = router.refresh_index(self.root)
        self.assertEqual([s["name"] for s in skills], ["alpha"])
        self.assertIn("could not write", err.getvalue())

    @unittest.skipIf(os.name == "nt", "creating symlinks needs elevation on Windows")
    def test_symlinked_checkout_is_indexed_and_loops_end(self) -> None:
        with tempfile.TemporaryDirectory() as elsewhere:
            add_skill(Path(elsewhere), "skills/linked", "name: linked\ndescription: L.")
            os.symlink(elsewhere, self.root / "checkout")
            os.symlink(self.root, self.root / "loop")
            skills = router.refresh_index(self.root)
        self.assertEqual([(s["name"], s["dir"]) for s in skills], [("linked", "checkout/skills/linked")])


class SearchTests(LibraryTestCase):
    def setUp(self) -> None:
        super().setUp()
        add_skill(self.root, "terraform-review", "name: terraform-review\ndescription: Review Terraform modules for drift and unsafe defaults.")
        add_skill(self.root, "docker-images", "name: docker-images\ndescription: Build and publish container images. Mentions terraform once.")
        add_skill(self.root, "commit-messages", "name: commit-messages\ndescription: Write git commit messages in the conventional style.")
        self.skills = router.refresh_index(self.root)

    def names(self, query: str, limit: int = 5) -> list[str]:
        return [skill["name"] for _, skill in router.search(self.skills, query, limit)]

    def test_name_match_outranks_a_passing_mention(self) -> None:
        with patch.object(router, "RELATIVE_FLOOR", 0):
            self.assertEqual(self.names("terraform"), ["terraform-review", "docker-images"])

    def test_passing_mentions_far_below_the_best_result_are_dropped(self) -> None:
        filler = " ".join(f"word{number}" for number in range(150))
        add_skill(self.root, "wordy", f"name: wordy\ndescription: {filler} terraform.")
        self.skills = router.refresh_index(self.root)
        self.assertEqual(self.names("terraform review"), ["terraform-review"])
        with patch.object(router, "RELATIVE_FLOOR", 0):
            self.assertIn("wordy", self.names("terraform review"))

    def test_plural_and_case_do_not_matter(self) -> None:
        self.assertEqual(self.names("Docker IMAGE"), ["docker-images"])
        self.assertEqual(self.names("reviews of modules"), ["terraform-review"])

    def test_limit_caps_the_results(self) -> None:
        with patch.object(router, "RELATIVE_FLOOR", 0):
            self.assertEqual(self.names("terraform", limit=1), ["terraform-review"])

    def test_no_match_is_empty(self) -> None:
        self.assertEqual(self.names("kubernetes"), [])

    def test_query_of_only_stopwords_is_an_error(self) -> None:
        with self.assertRaises(router.RouterError):
            router.search(self.skills, "how do I use this", 5)

    def test_empty_library_matches_nothing(self) -> None:
        self.assertEqual(router.search([], "terraform", 5), [])


class CommandTests(LibraryTestCase):
    def setUp(self) -> None:
        super().setUp()
        add_skill(self.root, "repo/terraform-review", "name: terraform-review\ndescription: Review Terraform modules.", "Use $ARGUMENTS.\n")
        add_skill(self.root, "docker-images", "name: docker-images\ndescription: " + "Build container images. " * 30)
        self.library = ("--library", str(self.root))

    def test_search_prints_the_absolute_skill_directory(self) -> None:
        code, out, _ = run(*self.library, "search", "terraform", "review")
        self.assertEqual(code, 0)
        self.assertIn("1. terraform-review", out)
        self.assertIn(f"dir:  {(self.root / 'repo/terraform-review').as_posix()}", out)
        self.assertIn("note: uses $ARGUMENTS", out)

    def test_search_truncates_long_descriptions(self) -> None:
        _, out, _ = run(*self.library, "search", "docker")
        line = next(line for line in out.splitlines() if line.strip().startswith("desc:"))
        self.assertTrue(line.endswith(" ..."))
        self.assertLess(len(line), router.SNIPPET_CHARS + 20)

    def test_search_miss_says_to_search_again(self) -> None:
        code, out, _ = run(*self.library, "search", "kubernetes")
        self.assertEqual(code, 0)
        self.assertIn('No skill in the library matches "kubernetes" (2 indexed', out)
        self.assertIn("different words", out)

    def test_search_json_carries_full_descriptions(self) -> None:
        _, out, _ = run(*self.library, "search", "--json", "docker")
        data = json.loads(out)
        self.assertEqual(data["indexed"], 2)
        self.assertEqual(data["results"][0]["name"], "docker-images")
        self.assertGreater(len(data["results"][0]["description"]), router.SNIPPET_CHARS)
        self.assertEqual(data["results"][0]["dir"], (self.root / "docker-images").as_posix())

    def test_library_comes_from_the_environment(self) -> None:
        with patch.dict(os.environ, {router.LIBRARY_ENV: str(self.root)}):
            code, out, _ = run("search", "terraform")
        self.assertEqual(code, 0)
        self.assertIn("terraform-review", out)

    def test_missing_library_is_reported(self) -> None:
        code, out, err = run("--library", str(self.root / "absent"), "search", "terraform")
        self.assertEqual(code, 2)
        self.assertEqual(out, "")
        self.assertIn("no skill library at", err)
        self.assertIn(router.LIBRARY_ENV, err)

    def test_unsearchable_query_is_reported(self) -> None:
        code, _, err = run(*self.library, "search", "the")
        self.assertEqual(code, 2)
        self.assertIn("no searchable words", err)

    def test_index_reports_problems(self) -> None:
        add_skill(self.root, "copy/terraform-review", "name: terraform-review\ndescription: Another.")
        add_skill(self.root, "bare", None)
        code, out, _ = run(*self.library, "index", "--rebuild")
        self.assertEqual(code, 0)
        self.assertIn("4 skills indexed", out)
        self.assertIn("1 with no description", out)
        self.assertIn("terraform-review: copy/terraform-review, repo/terraform-review", out)
        self.assertIn("repo/terraform-review: $ARGUMENTS", out)


class TopicsTests(LibraryTestCase):
    BASE = "Find an installed skill in the library."

    def setUp(self) -> None:
        super().setUp()
        for name in ("terraform-plan", "terraform-review", "docker-skill", "review-helper"):
            add_skill(self.root, name, f"name: {name}\ndescription: D.")
        self.skill_md = self.root / "router-SKILL.md"
        self.skill_md.write_text(f"---\nname: skill-router\ndescription: {self.BASE}\n---\n\n# Body\n", encoding="utf-8")

    def test_topics_are_ordered_by_frequency_then_name(self) -> None:
        topics = router.library_topics(router.refresh_index(self.root), 300)
        self.assertEqual(topics, ["review", "terraform", "docker", "plan"])

    def test_topics_stop_at_the_length_budget(self) -> None:
        topics = router.library_topics(router.refresh_index(self.root), len("review, terraform"))
        self.assertEqual(topics, ["review", "terraform"])

    def test_write_appends_then_replaces_the_sentence(self) -> None:
        router.write_topics(self.skill_md, ["docker", "terraform"])
        description = router.write_topics(self.skill_md, ["review"])
        self.assertEqual(description, f"{self.BASE} Library topics include review.")
        text = self.skill_md.read_text(encoding="utf-8")
        self.assertEqual(router.read_frontmatter(text)["description"], description)
        self.assertTrue(text.endswith("---\n\n# Body\n"))

    def test_write_with_no_topics_removes_the_sentence(self) -> None:
        router.write_topics(self.skill_md, ["docker"])
        self.assertEqual(router.write_topics(self.skill_md, []), self.BASE)

    def test_write_keeps_crlf_line_endings(self) -> None:
        self.skill_md.write_bytes(f"---\r\nname: skill-router\r\ndescription: {self.BASE}\r\n---\r\n".encode())
        router.write_topics(self.skill_md, ["docker"])
        expected = f"---\r\nname: skill-router\r\ndescription: {self.BASE} Library topics include docker.\r\n---\r\n"
        self.assertEqual(self.skill_md.read_bytes(), expected.encode())

    def test_write_refuses_an_over_length_description(self) -> None:
        before = self.skill_md.read_text(encoding="utf-8")
        with self.assertRaises(router.RouterError):
            router.write_topics(self.skill_md, ["x" * router.DESCRIPTION_LIMIT])
        self.assertEqual(self.skill_md.read_text(encoding="utf-8"), before)

    def test_write_refuses_a_block_or_quoted_description(self) -> None:
        for value in (">-\n  Folded.", '"Quoted."'):
            with self.subTest(value=value):
                self.skill_md.write_text(f"---\nname: skill-router\ndescription: {value}\n---\n", encoding="utf-8")
                with self.assertRaises(router.RouterError):
                    router.write_topics(self.skill_md, ["docker"])

    def test_topics_command_prints_the_list(self) -> None:
        code, out, _ = run("--library", str(self.root), "topics")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "review, terraform, docker, plan")

    def test_shipped_description_accepts_a_full_topics_list(self) -> None:
        shipped = Path(__file__).resolve().parent.parent / "SKILL.md"
        self.skill_md.write_text(shipped.read_text(encoding="utf-8"), encoding="utf-8")
        description = router.write_topics(self.skill_md, ["x" * 300])
        self.assertLessEqual(len(description), router.DESCRIPTION_LIMIT)


if __name__ == "__main__":
    unittest.main()

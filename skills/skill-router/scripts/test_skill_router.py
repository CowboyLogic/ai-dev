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
import threading
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

    def test_quoted_values_keep_hashes_and_drop_trailing_comments(self) -> None:
        cases = {
            "'Review code # Kubernetes deployments' # editorial": "Review code # Kubernetes deployments",
            '"Review code # Kubernetes deployments" # editorial': "Review code # Kubernetes deployments",
            "'It''s # fine' # note": "It's # fine",
            '"Say \\"hi\\" # loudly" # note': 'Say "hi" # loudly',
            '"Ends with a backslash \\\\" # note': "Ends with a backslash \\",
            "'No comment # here'": "No comment # here",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                fields = router.read_frontmatter(f"---\ndescription: {raw}\nname: demo\n---\n")
                self.assertEqual(fields, {"description": expected, "name": "demo"})

    def test_double_quoted_character_escapes_are_decoded(self) -> None:
        text = '---\ndescription: "Review \\u0052 \\x43 \\U0001F600 \\/ code\\0 \\ud83d."\n---\n'
        self.assertEqual(router.read_frontmatter(text)["description"], "Review R C \U0001F600 / code .")

    def test_unterminated_quote_is_read_as_plain_text(self) -> None:
        fields = router.read_frontmatter("---\ndescription: 'Unfinished value\n---\n")
        self.assertEqual(fields["description"], "'Unfinished value")

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

    def temporary_files(self) -> list[str]:
        return sorted(path.name for path in self.root.glob(router.INDEX_NAME + ".*"))

    def test_malformed_records_are_rebuilt_from_source(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        add_skill(self.root, "beta", "name: beta\ndescription: B.")
        good = router.refresh_index(self.root)
        index_path = self.root / router.INDEX_NAME
        broken = {
            "missing description": {k: v for k, v in good[0].items() if k != "description"},
            "missing name": {k: v for k, v in good[0].items() if k != "name"},
            "empty name": {**good[0], "name": ""},
            "description not text": {**good[0], "description": None},
            "unhashable dir": {**good[0], "dir": ["alpha"]},
            "variables not a list": {**good[0], "harness_variables": "$ARGUMENTS"},
            "variable not text": {**good[0], "harness_variables": [1]},
            "size not a number": {**good[0], "size": "12"},
            "time is a boolean": {**good[0], "mtime_ns": True},
            "record not a mapping": "alpha",
        }
        for label, record in broken.items():
            with self.subTest(label):
                index_path.write_text(
                    json.dumps({"version": router.INDEX_VERSION, "skills": [record, good[1]]}), encoding="utf-8"
                )
                original = router.build_entry
                with patch.object(router, "build_entry", side_effect=original) as rebuilt:
                    self.assertEqual(router.refresh_index(self.root), good)
                # Only the malformed record is read again; the valid one stays cached.
                self.assertEqual([call.args[1].name for call in rebuilt.call_args_list], ["alpha"])
                self.assertEqual(router.load_index(index_path), good)

    def test_commands_tolerate_a_malformed_index(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        index_path = self.root / router.INDEX_NAME
        expected = {("search", "alpha"): "1. alpha", ("index",): "1 skills indexed", ("topics",): "alpha"}
        for command, output in expected.items():
            with self.subTest(command=command):
                router.refresh_index(self.root)
                stored = json.loads(index_path.read_text(encoding="utf-8"))
                del stored["skills"][0]["description"]
                index_path.write_text(json.dumps(stored), encoding="utf-8")
                code, out, err = run("--library", str(self.root), *command)
                self.assertEqual((code, err), (0, ""))
                self.assertIn(output, out)

    def test_unwritable_index_still_returns_skills(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        for target in ("replace", "fdopen"):
            with self.subTest(target=target):
                err = io.StringIO()
                failure = patch.object(router.os, target, side_effect=OSError("read-only"))
                with failure, contextlib.redirect_stderr(err):
                    skills = router.refresh_index(self.root, rebuild=True)
                self.assertEqual([s["name"] for s in skills], ["alpha"])
                self.assertIn("could not write", err.getvalue())
                self.assertEqual(self.temporary_files(), [])

    def test_uncreatable_temporary_file_still_returns_skills(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        err = io.StringIO()
        failure = patch.object(router.tempfile, "mkstemp", side_effect=OSError("read-only"))
        with failure, contextlib.redirect_stderr(err):
            skills = router.refresh_index(self.root)
        self.assertEqual([s["name"] for s in skills], ["alpha"])
        self.assertIn("could not write", err.getvalue())

    @unittest.skipIf(os.name == "nt", "creating symlinks needs elevation on Windows")
    def test_symlink_at_a_predictable_temporary_path_is_not_followed(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        unrelated = self.root / "unrelated.txt"
        unrelated.write_text("keep me", encoding="utf-8")
        os.symlink(unrelated, self.root / (router.INDEX_NAME + ".tmp"))
        router.refresh_index(self.root)
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep me")
        index_path = self.root / router.INDEX_NAME
        self.assertFalse(index_path.is_symlink())
        self.assertEqual([s["name"] for s in router.load_index(index_path)], ["alpha"])

    def test_overlapping_writers_publish_one_complete_payload(self) -> None:
        index_path = self.root / router.INDEX_NAME
        payloads = [
            [{"name": f"writer-{number}", "description": str(number) * 50_000, "dir": "d",
              "harness_variables": [], "mtime_ns": 1, "size": 1}]
            for number in range(4)
        ]

        def write_repeatedly(skills: list[dict]) -> None:
            for _ in range(25):
                router.write_index(index_path, skills)

        threads = [threading.Thread(target=write_repeatedly, args=(payload,)) for payload in payloads]
        # On Windows a replace can lose to a concurrent one; that is reported, not fatal.
        with contextlib.redirect_stderr(io.StringIO()):
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
        stored = json.loads(index_path.read_text(encoding="utf-8"))
        self.assertIn(stored["skills"], payloads)
        self.assertEqual(self.temporary_files(), [])

    def test_skill_that_vanishes_before_it_is_read_is_skipped(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: A.")
        add_skill(self.root, "beta", "name: beta\ndescription: B.")
        original = router.build_entry

        def vanish(root: Path, skill_dir: Path, stat: os.stat_result) -> dict:
            if skill_dir.name == "beta":
                raise FileNotFoundError(2, "No such file or directory")
            return original(root, skill_dir, stat)

        err = io.StringIO()
        with patch.object(router, "build_entry", side_effect=vanish), contextlib.redirect_stderr(err):
            skills = router.refresh_index(self.root)
        self.assertEqual([s["name"] for s in skills], ["alpha"])
        self.assertIn("skipped beta/SKILL.md: No such file or directory", err.getvalue())

    @unittest.skipIf(os.name == "nt" or not hasattr(os, "geteuid") or os.geteuid() == 0, "needs file permissions that bind")
    def test_unreadable_skill_and_subtree_are_reported_not_fatal(self) -> None:
        add_skill(self.root, "alpha", "name: alpha\ndescription: Healthy terraform skill.")
        locked_file = add_skill(self.root, "beta", "name: beta\ndescription: Terraform too.") / "SKILL.md"
        locked_dir = add_skill(self.root, "gamma/inner", "name: inner\ndescription: Terraform three.").parent
        locked_file.chmod(0)
        locked_dir.chmod(0)
        self.addCleanup(locked_dir.chmod, 0o700)
        code, out, err = run("--library", str(self.root), "search", "--json", "terraform")
        self.assertEqual(code, 0)
        self.assertEqual([result["name"] for result in json.loads(out)["results"]], ["alpha"])
        self.assertIn("skipped beta/SKILL.md: Permission denied", err)
        self.assertIn(f"cannot read {locked_dir}", err)

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

    def test_exact_name_comes_first(self) -> None:
        add_skill(self.root, "review", "name: review\ndescription: Summarize a document.")
        add_skill(self.root, "copy/review", "name: Review\ndescription: A second copy.")
        self.skills = router.refresh_index(self.root)
        ranked = router.search(self.skills, "review", 5)
        self.assertEqual([(score, skill["dir"]) for score, skill in ranked[:2]],
                         [(float("inf"), "copy/review"), (float("inf"), "review")])
        self.assertEqual([skill["name"] for _, skill in ranked[2:]], ["terraform-review"])

    def test_exact_name_matches_spaced_words_and_stopword_names(self) -> None:
        add_skill(self.root, "how-to", "name: how-to\ndescription: Guides.")
        self.skills = router.refresh_index(self.root)
        self.assertEqual(self.names("Commit Messages")[0], "commit-messages")
        self.assertEqual(self.names("how to"), ["how-to"])

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

    def test_search_marks_an_exact_name(self) -> None:
        _, out, _ = run(*self.library, "search", "terraform-review")
        self.assertIn("1. terraform-review (exact name)", out)
        _, out, _ = run(*self.library, "search", "--json", "terraform-review")
        first = json.loads(out)["results"][0]
        self.assertEqual((first["exact_name"], first["score"]), (True, None))
        _, out, _ = run(*self.library, "search", "--json", "docker")
        first = json.loads(out)["results"][0]
        self.assertFalse(first["exact_name"])
        self.assertGreater(first["score"], 0)

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

    def test_index_reports_names_that_differ_only_by_case(self) -> None:
        add_skill(self.root, "upper", "name: Docker-Images\ndescription: Another.")
        _, out, _ = run(*self.library, "index")
        self.assertIn("1 names used by more than one skill", out)
        self.assertIn("docker-images: upper, docker-images", out)
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

    def test_topics_command_tells_an_empty_list_from_an_empty_library(self) -> None:
        _, out, _ = run("--library", str(self.root), "topics", "--max-chars", "1")
        self.assertIn("no topic words fit in 1 characters", out)
        with tempfile.TemporaryDirectory() as empty:
            _, out, _ = run("--library", empty, "topics")
        self.assertEqual(out.strip(), "(the library is empty)")

    def test_shipped_description_accepts_a_full_topics_list(self) -> None:
        shipped = Path(__file__).resolve().parent.parent / "SKILL.md"
        self.skill_md.write_text(shipped.read_text(encoding="utf-8"), encoding="utf-8")
        description = router.write_topics(self.skill_md, ["x" * 300])
        self.assertLessEqual(len(description), router.DESCRIPTION_LIMIT)


if __name__ == "__main__":
    unittest.main()

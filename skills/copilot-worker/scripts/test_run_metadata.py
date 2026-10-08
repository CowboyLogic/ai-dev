"""Run provenance and offline discovery, including records from older skill versions."""

import contextlib
import io
import json
from pathlib import Path
from unittest.mock import patch

from test_copilot_worker import WorkerTestCase
import copilot_worker as worker


class MetadataTests(WorkerTestCase):
    def test_all_modes_record_the_original_branch_and_commit(self):
        self.git("switch", "-c", "feature/nested")
        commit = self.git("rev-parse", "HEAD")
        for mode in worker.MODES:
            with self.subTest(mode=mode):
                result = worker.execute_run(mode=mode, task="Objective: Fix the parser", cwd=self.repo)
                self.assertEqual(result["baseBranch"], "feature/nested")
                self.assertEqual(result["baseCommit"], commit)
                self.assertEqual(result["repoName"], self.repo.name)
                self.assertEqual(result["repoRoot"], str(self.repo))
                self.assertEqual(result["label"], "Fix the parser")
                self.assertEqual(result["skillCommit"], worker.skill_commit())
                if mode == "implement":
                    self.assertNotEqual(result["branch"], result["baseBranch"])
                else:
                    self.assertIsNone(result["branch"])

    def test_metadata_is_saved_before_the_engine_and_survives_branch_changes(self):
        def engine(_command, run_dir, _timeout):
            saved = json.loads((run_dir / "metadata.json").read_text())
            self.assertEqual(saved["baseBranch"], "main")
            self.assertEqual(saved["label"], "Explicit label")
            self.assertEqual(saved["mode"], "research")
            self.assertIn("startedAt", saved)
            self.git("switch", "-c", "later-branch")
            (run_dir / "response.md").write_text("done")
            return 0, "exit"

        with patch.object(worker, "run_engine", side_effect=engine):
            result = worker.execute_run(mode="research", task="Look", cwd=self.repo, label="Explicit label")
        self.assertEqual(result["baseBranch"], "main")

    def test_detached_head_records_exact_commit(self):
        commit = self.git("rev-parse", "HEAD")
        self.git("checkout", "--detach")
        result = worker.execute_run(mode="research", task="Look", cwd=self.repo)
        self.assertEqual(result["baseBranch"], "HEAD")
        self.assertEqual(result["baseCommit"], commit)

    def test_research_still_works_before_the_first_commit(self):
        empty = self.repo.parent / "unborn"
        empty.mkdir()
        worker.git(["init", "-b", "new-branch"], empty)
        result = worker.execute_run(mode="research", task="Look", cwd=empty)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["baseBranch"], "new-branch")
        self.assertIsNone(result["baseCommit"])

    def test_objective_forms_and_fallback(self):
        for text in ("Objective: Repair parsing", "**Objective:** Repair parsing", "# Review task\n\n## Objective\n\nRepair parsing"):
            with self.subTest(text=text):
                self.assertEqual(worker.short_label(text), "Repair parsing")
        self.assertEqual(worker.short_label("# Generic task\n\nDo the actual work"), "Do the actual work")
        self.assertEqual(worker.short_label("Objective mismatch"), "Objective mismatch")
        self.assertEqual(worker.short_label("# Task heading only"), "Unlabelled task")
        self.assertEqual(worker.short_label("x", " custom\n label "), "custom label")
        self.assertEqual(len(worker.short_label("Objective: " + "x" * 500)), worker.MAX_LABEL_CHARS)

    def test_empty_explicit_label_is_rejected_before_creating_run_state(self):
        with self.assertRaisesRegex(worker.WorkerError, "--label"):
            worker.execute_run(mode="research", task="Look", cwd=self.repo, label=" \n")
        self.assertFalse(self.home.exists())
        self.assertEqual(self.calls(), [])

    def test_skill_version_comes_from_tracked_source_not_the_task_repo(self):
        source = self.repo / "skills" / "copilot-worker"
        (source / "scripts").mkdir(parents=True)
        (source / "SKILL.md").write_text("skill")
        (source / "scripts" / "copilot_worker.py").write_text("script")
        self.assertIsNone(worker.skill_commit(source))
        self.git("add", "skills/copilot-worker/SKILL.md", "skills/copilot-worker/scripts/copilot_worker.py")
        self.git("commit", "-m", "add skill")
        expected = self.git("rev-parse", "HEAD")
        (self.repo / "README.md").write_text("unrelated change")
        self.git("add", "README.md")
        self.git("commit", "-m", "unrelated")
        self.assertNotEqual(self.git("rev-parse", "HEAD"), expected)
        self.assertEqual(worker.skill_commit(source), expected)
        self.assertIsNone(worker.skill_commit(self.repo.parent))

    def test_cli_label_reaches_the_result(self):
        task = self.repo / "task.md"
        task.write_text("Objective: Derived label")
        self.addCleanup(task.unlink)
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = worker.main(["run", "--mode", "research", "--task-file", str(task), "--label", "CLI label"], cwd=self.repo)
        self.assertEqual(code, 0, stderr.getvalue())
        result = worker.list_runs()[0]
        self.assertEqual(result["label"], "CLI label")


class ListTests(WorkerTestCase):
    def record(self, suffix, **values):
        directory = self.home / "runs" / f"20261008-100000-{suffix}"
        directory.mkdir(parents=True)
        (directory / "result.json").write_text(json.dumps({
            "repoRoot": str(self.repo), "mode": "research", "status": "completed", **values,
        }))
        return directory

    def listing(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = worker.main(["list", *args], cwd=self.repo.parent)
        self.assertEqual(code, 0, stderr.getvalue())
        self.assertEqual(self.calls(), [])
        return stdout.getvalue()

    def test_missing_store_does_not_create_anything(self):
        self.assertEqual(self.listing(), "No matching runs.\n")
        self.assertFalse(self.home.exists())

    def test_unreadable_store_reports_a_short_error(self):
        self.home.mkdir()
        (self.home / "runs").write_text("not a directory")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = worker.main(["list"], cwd=self.repo.parent)
        self.assertEqual(code, 2)
        self.assertIn("cannot read the run store", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_list_orders_newest_first_and_filters_by_name_path_and_branch(self):
        self.record("0001", repoName="same", repoRoot="/one/same", baseBranch="feature/a", label="First")
        second = self.record("0002", repoName="same", repoRoot="/two/same", baseBranch="feature/b", label="Second")
        (second / "usage.json").write_text('{"aiCredits": 2.75}')
        listing = self.listing()
        self.assertLess(listing.index("0002"), listing.index("0001"))
        self.assertIn("2.75", listing)
        self.assertIn("CREDITS", listing)
        self.assertIn("Second", self.listing("--repo", "same", "--branch", "feature/b"))
        self.assertNotIn("First", self.listing("--repo", "/two/same"))
        self.assertIn("First", self.listing("--repo", "/one/same"))
        self.assertEqual(self.listing("--repo", "missing"), "No matching runs.\n")

    def test_legacy_backfill_is_read_only_and_never_guesses_branch(self):
        directory = self.record("0001", branch="copilot/old-run", currentBranch="copilot/old-run")
        before = (directory / "result.json").read_bytes()
        listing = self.listing()
        self.assertIn(self.repo.name, listing)
        self.assertIn("unknown", listing)
        self.assertNotIn("copilot/old-run", listing)
        self.assertEqual(worker.list_runs()[0].get("baseBranch"), None)
        self.assertEqual((directory / "result.json").read_bytes(), before)
        self.assertEqual(self.listing("--branch", "main"), "No matching runs.\n")

    def test_snapshot_without_result_is_visible_without_claiming_it_is_running(self):
        directory = self.record("0001")
        (directory / "result.json").unlink()
        (directory / "metadata.json").write_text(json.dumps({"repoName": "snapshot", "baseBranch": "topic", "label": "In flight"}))
        self.assertIn("unfinished", self.listing())
        self.assertIn("In flight", self.listing())

    def test_detached_run_can_be_filtered_and_displays_commit(self):
        self.record("0001", baseBranch="HEAD", baseCommit="a" * 40)
        self.assertIn("detached:" + "a" * 12, self.listing("--branch", "HEAD"))

    def test_bad_json_and_unrelated_entries_do_not_hide_valid_runs(self):
        good = self.record("0001", label="Valid run")
        for name, contents in (("0002", "{"), ("0003", "[]"), ("0004", "\udcff")):
            bad = self.home / "runs" / f"20261008-100000-{name}"
            bad.mkdir()
            (bad / "result.json").write_bytes(contents.encode("utf-8", errors="surrogateescape"))
        (self.home / "runs" / "not-a-run").mkdir()
        (good / "usage.json").write_text("null")
        self.assertEqual(len(worker.list_runs()), 1)
        self.assertIn("Valid run", self.listing())

    def test_credits_remain_unknown_when_invalid_or_missing(self):
        directory = self.record("0001")
        for value in (None, True, "2.0", -1, float("nan"), float("inf"), 10**400):
            with self.subTest(value=value):
                (directory / "usage.json").write_text(json.dumps({"aiCredits": value}))
                self.assertIsNone(worker.list_runs()[0]["aiCredits"])
        (directory / "usage.json").write_text('{"aiCredits": 0}')
        self.assertEqual(worker.list_runs()[0]["aiCredits"], 0)

    def test_terminal_controls_are_not_printed_from_record_fields(self):
        self.record("0001", label="bad\x1b[31m\nlabel\tmore", repoName="repo\x1b")
        listing = self.listing()
        self.assertNotIn("\x1b", listing)
        self.assertNotIn("\t", listing)
        self.assertEqual(len(listing.splitlines()), 2)

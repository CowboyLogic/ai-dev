#!/usr/bin/env python3
"""Unit tests for the Copilot worker script, run against a fake copilot binary."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import copilot_worker as worker  # noqa: E402

SCRIPT = Path(__file__).parent / "copilot_worker.py"

# One assistant message in the shape Copilot CLI 1.0.89 emits with --output-format json.
RECORDED_EVENT = json.dumps({
    "type": "assistant.message",
    "id": "sanitized-assistant-message",
    "timestamp": "2026-09-19T00:00:00.000Z",
    "data": {"messageId": "sanitized-message", "content": "Recorded final answer", "toolRequests": []},
})

FAKE_COPILOT = r'''
import json, os, sys, time

args = sys.argv[1:]
if args == ["--version"]:
    print("GitHub Copilot CLI 0.0.0-fake")
    sys.exit(0)
log = os.environ.get("FAKE_COPILOT_ARGV")
if log:
    with open(log, "a") as handle:
        handle.write(json.dumps(args) + "\n")
behavior = os.environ.get("FAKE_COPILOT_BEHAVIOR", "ok")
if behavior == "sleep":
    time.sleep(60)
if behavior == "slow":
    time.sleep(1.5)
if behavior == "fail":
    sys.stderr.write("model rejected\n")
    sys.exit(1)
workspace = args[args.index("-C") + 1]
if "--allow-all-tools" in args:
    with open(os.path.join(workspace, "worker_output.txt"), "w") as handle:
        handle.write("written by worker\n")
with open(args[args.index("--usage-output-file") + 1], "w") as handle:
    json.dump({"premiumRequests": 1}, handle)
if behavior != "silent":
    print(json.dumps({"type": "assistant.message", "data": {"content": "worker final answer"}}))
'''


class WorkerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name).resolve()
        self.home = base / "home"
        self.repo = base / "my repo"
        self.repo.mkdir()
        fake = base / "fake_copilot.py"
        fake.write_text(FAKE_COPILOT, encoding="utf-8")
        self.argv_log = base / "argv.jsonl"
        self.env = {
            "COPILOT_WORKER_HOME": str(self.home),
            "COPILOT_WORKER_BIN": f"{shlex.quote(sys.executable)} {shlex.quote(str(fake))}",
            "FAKE_COPILOT_ARGV": str(self.argv_log),
            "FAKE_COPILOT_BEHAVIOR": "ok",
        }
        patcher = patch.dict(os.environ, self.env)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "commit.gpgsign", "false")
        (self.repo / "README.md").write_text("hello\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "init")

    def git(self, *args: str) -> str:
        done = subprocess.run(
            ["git", *args], cwd=self.repo, check=True, capture_output=True, text=True
        )
        return done.stdout.strip()

    def behavior(self, name: str) -> None:
        os.environ["FAKE_COPILOT_BEHAVIOR"] = name

    def calls(self) -> list[list[str]]:
        if not self.argv_log.exists():
            return []
        return [json.loads(line) for line in self.argv_log.read_text().splitlines()]


class CommandTests(WorkerTestCase):
    def command(self, mode: str, **overrides: object) -> list[str]:
        options = {
            "mode": mode,
            "workspace": self.repo,
            "prompt": "do the thing",
            "model": worker.DEFAULT_MODELS[mode],
            "effort": None,
            "credits": 30,
            "usage_file": self.home / "usage.json",
        }
        options.update(overrides)
        return worker.build_command(**options)

    def test_default_models_match_the_design(self) -> None:
        self.assertEqual(
            worker.DEFAULT_MODELS,
            {"research": "gpt-6-luna", "review": "gpt-6.1-sol", "implement": "gpt-6.1-sol"},
        )

    def test_implement_command_carries_every_deny_rule(self) -> None:
        command = self.command("implement")
        self.assertIn("--allow-all-tools", command)
        for pattern in (
            "shell(git push)", "shell(git remote)", "shell(git worktree)",
            "shell(gh:*)", "shell(sudo)",
        ):
            self.assertIn(f"--deny-tool={pattern}", command)

    def test_no_command_grants_all_paths_or_urls(self) -> None:
        for mode in worker.MODES:
            command = self.command(mode)
            for flag in ("--allow-all-paths", "--allow-all-urls", "--allow-all", "--yolo"):
                self.assertNotIn(flag, command)

    def test_read_only_command_exposes_only_the_view_tool(self) -> None:
        for mode in ("research", "review"):
            command = self.command(mode)
            self.assertIn("--available-tools=view", command)
            self.assertIn("--allow-tool=read", command)
            self.assertNotIn("--allow-all-tools", command)

    def test_effort_is_passed_only_when_given(self) -> None:
        self.assertNotIn("--reasoning-effort", self.command("implement"))
        command = self.command("implement", effort="high")
        self.assertEqual(command[command.index("--reasoning-effort") + 1], "high")

    def test_prompt_starting_with_a_dash_stays_one_argument(self) -> None:
        prompt = "- fix the \"quoted\" thing\n- then the 'other' thing"
        command = self.command("research", prompt=prompt)
        self.assertIn(f"--prompt={prompt}", command)

    def test_review_prompt_attaches_the_working_diff(self) -> None:
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        prompt = worker.build_prompt("review", "Review this.", self.repo)
        self.assertIn("+changed", prompt)

    def test_review_prompt_says_when_there_are_no_changes(self) -> None:
        prompt = worker.build_prompt("review", "Review this.", self.repo)
        self.assertIn("[no tracked changes]", prompt)

    def test_review_prompt_truncates_a_large_diff(self) -> None:
        (self.repo / "README.md").write_text("x" * 300_000 + "\n", encoding="utf-8")
        prompt = worker.build_prompt("review", "Review this.", self.repo)
        self.assertIn("[diff truncated by copilot-worker]", prompt)
        self.assertLess(len(prompt), 205_000)

    def test_research_prompt_has_no_diff(self) -> None:
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        prompt = worker.build_prompt("research", "Look around.", self.repo)
        self.assertNotIn("+changed", prompt)
        self.assertTrue(prompt.startswith("Look around."))

    def test_extract_response_reads_the_recorded_event_shape(self) -> None:
        events = "not json\n" + RECORDED_EVENT + "\n"
        self.assertEqual(worker.extract_response(events), "Recorded final answer")

    def test_extract_response_returns_the_last_non_empty_message(self) -> None:
        first = json.dumps({"type": "assistant.message", "data": {"content": "progress note"}})
        last = json.dumps({"type": "assistant.message", "content": "legacy shape answer"})
        blank = json.dumps({"type": "assistant.message", "data": {"content": "  "}})
        self.assertEqual(
            worker.extract_response("\n".join([first, last, blank])), "legacy shape answer"
        )

    def test_extract_response_is_empty_without_an_assistant_message(self) -> None:
        self.assertEqual(worker.extract_response('{"type":"session.start"}\n'), "")


class RunTests(WorkerTestCase):
    def run_mode(self, mode: str, **options: object) -> dict:
        return worker.execute_run(mode=mode, task="Do the task.", cwd=self.repo, **options)

    def cli(self, *args: str, **popen: object) -> subprocess.Popen:
        return subprocess.Popen(
            [sys.executable, str(SCRIPT), *args],
            cwd=self.repo, env={**os.environ}, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, **popen,
        )

    def task_file(self, text: str = "Do the task.") -> str:
        path = self.repo.parent / "task.md"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def results(self) -> list[dict]:
        return [
            json.loads(path.read_text())
            for path in sorted((self.home / "runs").glob("*/result.json"))
        ]

    def test_research_run_completes_in_the_live_checkout(self) -> None:
        result = self.run_mode("research")
        run_dir = Path(result["runDir"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["terminationReason"], "exit")
        self.assertEqual(result["exitCode"], 0)
        self.assertEqual(result["workspace"], str(self.repo))
        self.assertIsNone(result["branch"])
        self.assertIsNone(result["baseCommit"])
        self.assertEqual(result["changedFiles"], {"uncommitted": [], "commits": []})
        self.assertEqual(result["copilotVersion"], "GitHub Copilot CLI 0.0.0-fake")
        self.assertRegex(result["runId"], worker.RUN_ID_PATTERN)
        self.assertEqual((run_dir / "response.md").read_text(), "worker final answer")
        self.assertEqual(json.loads((run_dir / "usage.json").read_text()), {"premiumRequests": 1})
        self.assertTrue((run_dir / "task.md").read_text().startswith("Do the task."))
        self.assertEqual(json.loads((run_dir / "result.json").read_text()), result)

    def test_each_mode_uses_its_default_model_and_limits(self) -> None:
        for mode in worker.MODES:
            result = self.run_mode(mode)
            call = self.calls()[-1]
            self.assertEqual(call[call.index("--model") + 1], worker.DEFAULT_MODELS[mode])
            self.assertEqual(result["maxAiCredits"], worker.DEFAULT_CREDITS[mode])
            self.assertEqual(result["timeoutSeconds"], worker.DEFAULT_TIMEOUTS[mode])

    def test_model_override_replaces_the_default(self) -> None:
        result = self.run_mode("research", model="gpt-5-mini")
        call = self.calls()[-1]
        self.assertEqual(call[call.index("--model") + 1], "gpt-5-mini")
        self.assertEqual(result["model"], "gpt-5-mini")

    def test_implement_runs_in_a_worktree_and_leaves_the_live_checkout_alone(self) -> None:
        head = self.git("rev-parse", "HEAD")
        result = self.run_mode("implement")
        workspace = Path(result["workspace"])
        self.assertEqual(result["status"], "completed")
        self.assertEqual(workspace.parent, self.home / "worktrees")
        self.assertEqual(result["branch"], f"copilot/{result['runId']}")
        self.assertEqual(result["baseCommit"], head)
        self.assertTrue((workspace / "worker_output.txt").exists())
        self.assertEqual(result["changedFiles"]["uncommitted"], ["?? worker_output.txt"])
        self.assertEqual(result["changedFiles"]["commits"], [])
        # Invariants 1 and 6: nothing changed in the live checkout or on its branch.
        self.assertFalse((self.repo / "worker_output.txt").exists())
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "main")
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_implement_warns_when_the_live_checkout_is_dirty(self) -> None:
        (self.repo / "README.md").write_text("uncommitted\n", encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = self.run_mode("implement")
        self.assertEqual(result["status"], "completed")
        self.assertIn("uncommitted changes", stderr.getvalue())
        self.assertEqual(
            (Path(result["workspace"]) / "README.md").read_text(), "hello\n"
        )

    def test_exit_zero_without_a_message_is_completed_no_response(self) -> None:
        self.behavior("silent")
        self.assertEqual(self.run_mode("research")["status"], "completed_no_response")

    def test_non_zero_exit_is_failed_and_keeps_stderr(self) -> None:
        self.behavior("fail")
        result = self.run_mode("research")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["exitCode"], 1)
        self.assertEqual(result["terminationReason"], "exit")
        self.assertIn("model rejected", (Path(result["runDir"]) / "stderr.log").read_text())

    def test_timeout_kills_the_worker_and_records_the_reason(self) -> None:
        self.behavior("sleep")
        started = time.monotonic()
        result = self.run_mode("research", timeout=1)
        self.assertLess(time.monotonic() - started, 15)
        self.assertEqual(result["status"], "timed_out")
        self.assertEqual(result["terminationReason"], "timeout")
        self.assertIsNone(result["exitCode"])

    def test_missing_binary_is_recorded_as_a_spawn_error(self) -> None:
        os.environ["COPILOT_WORKER_BIN"] = str(self.home / "no-such-copilot")
        result = self.run_mode("research")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["terminationReason"], "spawn_error")
        self.assertEqual(result["copilotVersion"], "unknown")
        self.assertTrue((Path(result["runDir"]) / "result.json").exists())

    def test_invalid_requests_are_rejected_before_anything_runs(self) -> None:
        with self.assertRaises(worker.WorkerError):
            worker.execute_run(mode="research", task="  \n", cwd=self.repo)
        with self.assertRaises(worker.WorkerError):
            self.run_mode("research", credits=29)
        with self.assertRaises(worker.WorkerError):
            self.run_mode("research", timeout=0)
        with self.assertRaises(worker.WorkerError):
            worker.execute_run(mode="research", task="x", cwd=self.repo.parent)
        self.assertEqual(self.calls(), [])

    def test_cli_run_exits_zero_and_prints_a_short_summary(self) -> None:
        process = self.cli("run", "--mode", "research", "--task-file", self.task_file())
        stdout, _ = process.communicate(timeout=30)
        self.assertEqual(process.returncode, 0)
        self.assertIn("status: completed", stdout)
        self.assertLessEqual(len(stdout.splitlines()), 20)

    def test_cli_run_exits_one_when_the_worker_fails(self) -> None:
        self.behavior("fail")
        process = self.cli("run", "--mode", "research", "--task-file", self.task_file())
        stdout, _ = process.communicate(timeout=30)
        self.assertEqual(process.returncode, 1)
        self.assertIn("status: failed", stdout)

    def test_cli_run_exits_two_for_an_empty_task_file(self) -> None:
        process = self.cli("run", "--mode", "research", "--task-file", self.task_file(""))
        _, stderr = process.communicate(timeout=30)
        self.assertEqual(process.returncode, 2)
        self.assertIn("error:", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_run_completes_after_the_callers_stdin_closes(self) -> None:
        # Invariant 4: the broker died here; this script must not.
        self.behavior("slow")
        process = self.cli(
            "run", "--mode", "research", "--task-file", self.task_file(),
            stdin=subprocess.PIPE,
        )
        process.stdin.close()
        process.communicate(timeout=30)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(self.results()[0]["status"], "completed")

    def test_two_runs_overlap_instead_of_queueing(self) -> None:
        # Invariant 7.
        self.behavior("slow")
        task = self.task_file()
        first = self.cli("run", "--mode", "research", "--task-file", task)
        second = self.cli("run", "--mode", "implement", "--task-file", task)
        for process in (first, second):
            process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0)
        one, two = self.results()
        self.assertNotEqual(one["runId"], two["runId"])
        self.assertLess(one["startedAt"], two["endedAt"])
        self.assertLess(two["startedAt"], one["endedAt"])

    def test_sigterm_kills_the_worker_and_still_writes_a_result(self) -> None:
        # Invariant 5.
        self.behavior("sleep")
        process = self.cli("run", "--mode", "research", "--task-file", self.task_file())
        deadline = time.monotonic() + 10
        while not list((self.home / "runs").glob("*/events.jsonl")):
            self.assertLess(time.monotonic(), deadline, "worker never started")
            time.sleep(0.05)
        time.sleep(0.3)
        process.send_signal(signal.SIGTERM)
        process.communicate(timeout=30)
        self.assertEqual(process.returncode, 1)
        result = self.results()[0]
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["terminationReason"], f"signal:{int(signal.SIGTERM)}")


if __name__ == "__main__":
    unittest.main()

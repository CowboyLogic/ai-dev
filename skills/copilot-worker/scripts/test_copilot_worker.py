#!/usr/bin/env python3
"""Unit tests for the Copilot worker script, run against a fake copilot binary."""

from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import copilot_worker as worker  # noqa: E402

SCRIPT = Path(__file__).parent / "copilot_worker.py"
WINDOWS = os.name == "nt"


def process_alive(pid: int) -> bool:
    if WINDOWS:
        # os.kill(pid, 0) would send Ctrl+C on Windows; ask for the exit code instead.
        import ctypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.restype = ctypes.c_void_p
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            kernel32.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(code))
            return code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(ctypes.c_void_p(handle))
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def signal_self(signum: int) -> None:
    # On Windows os.kill would terminate this process; raise_signal runs its handler.
    if WINDOWS:
        signal.raise_signal(signum)
    else:
        os.kill(os.getpid(), signum)


# Stands in for worker_engine.py: same arguments, same files in, same files out.
FAKE_ENGINE = r"""
import json, os, signal, subprocess, sys, time

args = sys.argv[1:]
if args == ["--version"]:
    print("github-copilot-sdk 0.0.0-fake (runtime fake)")
    sys.exit(0)
if args == ["--check-pins"]:
    if os.environ.get("FAKE_COPILOT_PINS") == "mismatch":
        print("pin mismatch: runtime is fake, pinned to other")
        sys.exit(1)
    print("pins ok")
    sys.exit(0)
if args[:1] == ["--list-models"]:
    models = os.environ.get("FAKE_COPILOT_MODELS")
    if models == "fail":
        sys.stderr.write("not signed in\n")
        sys.exit(1)
    print(models or json.dumps([
        {"id": "gpt-6-luna", "supportedReasoningEfforts": ["low", "medium", "high"]},
        {"id": "gpt-6.1-terra", "supportedReasoningEfforts": ["low", "medium", "high", "xhigh"]},
        {"id": "gpt-6.1-sol", "supportedReasoningEfforts": ["low", "medium", "high", "xhigh", "max"]},
        {"id": "gpt-6-astra", "supportedReasoningEfforts": ["low", "medium", "high", "xhigh", "max"]},
    ]))
    sys.exit(0)
run_dir = args[0]
config = json.load(open(os.path.join(run_dir, "engine.json")))
log = os.environ.get("FAKE_COPILOT_ARGV")
if log:
    with open(log, "a") as handle:
        handle.write(json.dumps({"argv": args, **config}) + "\n")
with open(os.environ["FAKE_COPILOT_PID"], "w") as handle:
    handle.write(str(os.getpid()))
with open(os.environ["FAKE_COPILOT_STDIN"], "w") as handle:
    handle.write(open(os.path.join(run_dir, "task.md")).read())
workspace = config["workspace"]
behavior = os.environ.get("FAKE_COPILOT_BEHAVIOR", "ok")
if behavior == "stubborn":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(60)
if behavior in ("grandchild", "lingering"):
    # A child that ignores SIGTERM and outlives this process, like a watch-mode test runner.
    child_pid = os.environ["FAKE_COPILOT_CHILD_PID"]
    subprocess.Popen([
        sys.executable, "-c",
        "import os, signal, sys, time\n"
        "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        "open(sys.argv[1], 'w').write(str(os.getpid()))\n"
        "time.sleep(60)\n",
        child_pid,
    ])
    while not (os.path.exists(child_pid) and os.path.getsize(child_pid)):
        time.sleep(0.02)
if behavior == "grandchild":
    time.sleep(60)
if behavior == "switch":
    subprocess.run(["git", "checkout", "-q", "-b", "worker-own-branch"], cwd=workspace, check=True)
if behavior == "wreck":
    os.remove(os.path.join(workspace, ".git"))
if behavior == "sleep":
    time.sleep(60)
if behavior == "slow":
    time.sleep(1.5)
if behavior == "fail":
    sys.stderr.write("model rejected\n")
    sys.exit(1)
if config["mode"] == "implement":
    with open(os.path.join(workspace, "worker_output.txt"), "w") as handle:
        handle.write("written by worker\n")
with open(os.path.join(run_dir, "usage.json"), "w") as handle:
    json.dump({"aiCredits": 1.0}, handle)
with open(os.path.join(run_dir, "runtime.json"), "w") as handle:
    json.dump({"sdkVersion": "0.0.0-fake", "runtimeVersion": "fake"}, handle)
if behavior != "silent":
    with open(os.path.join(run_dir, "response.md"), "w") as handle:
        handle.write("worker final answer")
"""


class WorkerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        base = Path(tmp.name).resolve()
        self.home = base / "home"
        self.repo = base / "my repo"
        self.repo.mkdir()
        fake = base / "fake_engine.py"
        fake.write_text(FAKE_ENGINE, encoding="utf-8")
        self.argv_log = base / "argv.jsonl"
        self.pid_file = base / "worker.pid"
        self.child_pid_file = base / "grandchild.pid"
        self.env = {
            "COPILOT_WORKER_HOME": str(self.home),
            "COPILOT_WORKER_ENGINE": f"{shlex.quote(sys.executable)} {shlex.quote(str(fake))}",
            "FAKE_COPILOT_ARGV": str(self.argv_log),
            "FAKE_COPILOT_PID": str(self.pid_file),
            "FAKE_COPILOT_STDIN": str(base / "stdin.txt"),
            "FAKE_COPILOT_CHILD_PID": str(self.child_pid_file),
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

    def assert_process_gone(self, pid_file: Path) -> None:
        pid = int(pid_file.read_text())
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if not process_alive(pid):
                return
            time.sleep(0.05)
        os.kill(pid, getattr(signal, "SIGKILL", signal.SIGTERM))
        self.fail(f"process {pid} from {pid_file.name} is still running")

    def calls(self) -> list[dict]:
        if not self.argv_log.exists():
            return []
        return [json.loads(line) for line in self.argv_log.read_text().splitlines()]


class PromptAndConfigTests(WorkerTestCase):
    def test_profiles_match_the_design_in_cost_order(self) -> None:
        self.assertEqual(
            worker.PROFILES,
            {
                "light": {"model": "gpt-6-luna", "effort": "medium"},
                "standard": {"model": "gpt-6.1-terra", "effort": "medium"},
                "deep": {"model": "gpt-6.1-sol", "effort": "medium"},
                "heavy": {"model": "gpt-6-astra", "effort": "medium"},
            },
        )
        self.assertEqual(list(worker.PROFILES), ["light", "standard", "deep", "heavy"])

    def test_default_profiles_match_the_design(self) -> None:
        self.assertEqual(
            worker.DEFAULT_PROFILES,
            {"research": "light", "review": "deep", "implement": "standard"},
        )

    def test_review_defaults_to_a_different_model_from_implement(self) -> None:
        model = {mode: worker.PROFILES[worker.DEFAULT_PROFILES[mode]]["model"] for mode in worker.MODES}
        self.assertNotEqual(model["review"], model["implement"])

    def test_no_profile_uses_an_effort_above_the_cap(self) -> None:
        self.assertNotIn("max", worker.EFFORTS)
        for profile in worker.PROFILES.values():
            self.assertIn(profile["effort"], (None, *worker.EFFORTS))

    def test_engine_config_carries_the_run_settings(self) -> None:
        result = worker.execute_run(mode="implement", task="Do it.", cwd=self.repo)
        config = json.loads((Path(result["runDir"]) / "engine.json").read_text())
        self.assertEqual(config["mode"], "implement")
        self.assertEqual(config["model"], "gpt-6.1-terra")
        self.assertEqual(config["credits"], 60)
        self.assertEqual(config["timeout"], 1800)
        self.assertEqual(config["effort"], "medium")
        self.assertEqual(config["workspace"], result["workspace"])

    def test_every_profile_sets_medium_effort(self) -> None:
        for profile in worker.PROFILES.values():
            self.assertEqual(profile["effort"], "medium")

    def test_effort_override_reaches_the_engine(self) -> None:
        worker.execute_run(mode="research", task="x", cwd=self.repo, effort="high", reason="user asked")
        self.assertEqual(self.calls()[-1]["effort"], "high")

    def test_engine_uses_a_private_copilot_home_inside_the_state_directory(self) -> None:
        previous = os.umask(0o022)
        self.addCleanup(os.umask, previous)
        worker.execute_run(mode="research", task="x", cwd=self.repo)
        home = Path(self.calls()[-1]["copilotHome"])
        self.assertEqual(home, self.home / "copilot-home")
        self.assertTrue(home.is_dir())
        if not WINDOWS:
            self.assertEqual(self.home.stat().st_mode & 0o077, 0)

    def test_task_reaches_the_engine_by_file_and_never_in_argv(self) -> None:
        # Argv is visible to other local users through the process list.
        task = "- fix the \"quoted\" thing\n- then the 'other' thing"
        result = worker.execute_run(mode="research", task=task, cwd=self.repo)
        sent = (Path(result["runDir"]) / "task.md").read_text()
        self.assertTrue(sent.startswith(task))
        self.assertEqual(Path(os.environ["FAKE_COPILOT_STDIN"]).read_text(), sent)
        for argument in self.calls()[-1]["argv"]:
            self.assertNotIn("quoted", argument)

    def test_review_prompt_attaches_the_working_diff(self) -> None:
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        prompt = worker.build_prompt("review", "Review this.", self.repo)
        self.assertIn("+changed", prompt)

    def test_review_prompt_says_when_there_are_no_changes(self) -> None:
        prompt = worker.build_prompt("review", "Review this.", self.repo)
        self.assertIn("[no tracked changes]", prompt)

    def test_review_prompt_truncates_a_large_diff(self) -> None:
        # Multi-byte text: the cap must hold in bytes, not characters.
        (self.repo / "README.md").write_text("é" * 150_000 + "\n", encoding="utf-8")
        prompt = worker.build_prompt("review", "Review this.", self.repo)
        self.assertIn("[diff truncated by copilot-worker]", prompt)
        self.assertLess(len(prompt.encode("utf-8")), 131_072)

    def test_review_prompt_survives_non_utf8_bytes_in_the_diff(self) -> None:
        (self.repo / "README.md").write_bytes(b"caf\xe9 latin-1\n")
        prompt = worker.build_prompt("review", "Review this.", self.repo)
        self.assertIn("latin-1", prompt)

    def test_research_prompt_has_no_diff(self) -> None:
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        prompt = worker.build_prompt("research", "Look around.", self.repo)
        self.assertNotIn("+changed", prompt)
        self.assertTrue(prompt.startswith("Look around."))

    def test_the_script_declares_its_sdk_dependency_for_uv(self) -> None:
        header = SCRIPT.read_text().split("# ///", 2)[1]
        pins = json.loads((SCRIPT.parent / "pins.json").read_text(encoding="utf-8"))
        self.assertIn('requires-python = ">=3.11"', header)
        self.assertIn(f'"github-copilot-sdk=={pins["sdk"]}"', header)

    def test_every_dependency_in_the_script_header_is_pinned_exactly(self) -> None:
        header = SCRIPT.read_text().split("# ///", 2)[1]
        declared = re.findall(r'^#\s+"([^"]+)",?$', header, re.MULTILINE)
        self.assertGreater(len(declared), 1)
        for requirement in declared:
            self.assertRegex(requirement, r"^[A-Za-z0-9._-]+==[A-Za-z0-9.!+_-]+$", requirement)

    def test_pins_file_names_a_sdk_and_a_runtime(self) -> None:
        pins = json.loads((SCRIPT.parent / "pins.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(pins), ["runtime", "sdk"])
        for value in pins.values():
            self.assertRegex(value, r"^\d+\.\d+\.\d+(-\d+)?$")


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
        self.assertEqual(result["copilotVersion"], "github-copilot-sdk 0.0.0-fake (runtime fake)")
        self.assertRegex(result["runId"], worker.RUN_ID_PATTERN)
        self.assertEqual((run_dir / "response.md").read_text(), "worker final answer")
        self.assertEqual(json.loads((run_dir / "usage.json").read_text()), {"aiCredits": 1.0})
        self.assertTrue((run_dir / "task.md").read_text().startswith("Do the task."))
        self.assertEqual(json.loads((run_dir / "result.json").read_text()), result)

    @unittest.skipIf(WINDOWS, "Windows has no mode bits; the directory keeps its inherited ACL")
    def test_listing_models_creates_the_state_directory_private_to_the_owner(self) -> None:
        # check --live lists models before any run creates the state root.
        previous = os.umask(0o022)
        self.addCleanup(os.umask, previous)
        worker.available_models()
        self.assertEqual(self.home.stat().st_mode & 0o077, 0)

    @unittest.skipIf(WINDOWS, "Windows has no mode bits; the directory keeps its inherited ACL")
    def test_state_directory_is_private_to_the_owner(self) -> None:
        # Task text, diffs, responses, and worktrees live here; other users must not read them.
        previous = os.umask(0o022)
        self.addCleanup(os.umask, previous)
        self.run_mode("implement")
        self.assertEqual(self.home.stat().st_mode & 0o077, 0)

    def test_each_mode_uses_its_default_profile_and_limits(self) -> None:
        for mode in worker.MODES:
            result = self.run_mode(mode)
            call = self.calls()[-1]
            profile = worker.PROFILES[worker.DEFAULT_PROFILES[mode]]
            self.assertEqual(call["model"], profile["model"])
            self.assertEqual(call["effort"], profile["effort"])
            self.assertEqual(result["profile"], worker.DEFAULT_PROFILES[mode])
            self.assertEqual(result["defaultProfile"], worker.DEFAULT_PROFILES[mode])
            self.assertEqual(result["attempt"], 1)
            self.assertIsNone(result["retryOf"])
            self.assertIsNone(result["reason"])
            self.assertEqual(result["maxAiCredits"], worker.DEFAULT_CREDITS[mode])
            self.assertEqual(result["timeoutSeconds"], worker.DEFAULT_TIMEOUTS[mode])

    def test_model_override_replaces_the_default(self) -> None:
        result = self.run_mode("research", model="gpt-5-mini", reason="user named it")
        call = self.calls()[-1]
        self.assertEqual(call["model"], "gpt-5-mini")
        self.assertEqual(result["model"], "gpt-5-mini")
        self.assertEqual(result["reason"], "user named it")

    def test_a_named_profile_sets_model_and_effort_and_records_the_reason(self) -> None:
        result = self.run_mode("implement", profile="deep", reason="cross-module change")
        call = self.calls()[-1]
        self.assertEqual((call["model"], call["effort"]), ("gpt-6.1-sol", "medium"))
        self.assertEqual(result["profile"], "deep")
        self.assertEqual(result["defaultProfile"], "standard")
        self.assertEqual(result["reason"], "cross-module change")
        stored = json.loads((Path(result["runDir"]) / "result.json").read_text())
        self.assertEqual(stored["reason"], "cross-module change")

    def test_naming_the_default_profile_needs_no_reason(self) -> None:
        result = self.run_mode("implement", profile="standard")
        self.assertEqual(result["profile"], "standard")

    def test_an_off_default_run_without_a_reason_is_rejected_before_it_starts(self) -> None:
        for options in ({"profile": "deep"}, {"model": "gpt-5-mini"}, {"effort": "low"},
                        {"profile": "light", "reason": "   "}):
            with self.subTest(options=options), self.assertRaisesRegex(worker.WorkerError, "--reason"):
                self.run_mode("implement", **options)
        self.assertEqual(self.calls(), [])

    def test_effort_max_is_rejected_even_with_a_reason(self) -> None:
        with self.assertRaisesRegex(worker.WorkerError, "max is not allowed"):
            self.run_mode("implement", effort="max", reason="hard task")
        self.assertEqual(self.calls(), [])

    def test_an_unknown_profile_is_rejected(self) -> None:
        with self.assertRaisesRegex(worker.WorkerError, "unknown profile"):
            self.run_mode("implement", profile="ultra", reason="x")

    def test_a_retry_steps_up_one_profile_and_counts_the_attempt(self) -> None:
        first = self.run_mode("implement")
        second = self.run_mode("implement", retry_of=first["runId"], reason="tests failed")
        self.assertEqual((second["profile"], second["attempt"], second["retryOf"]),
                         ("deep", 2, first["runId"]))
        self.assertEqual(self.calls()[-1]["model"], "gpt-6.1-sol")
        third = self.run_mode("implement", retry_of=second["runId"], reason="still failing")
        self.assertEqual((third["profile"], third["attempt"]), ("heavy", 3))
        self.assertEqual(self.calls()[-1]["model"], "gpt-6-astra")

    def test_a_run_that_was_already_retried_cannot_be_retried_again(self) -> None:
        # Forking the chain from an older run would restart the attempt count and dodge the cap.
        first = self.run_mode("implement")
        self.run_mode("implement", retry_of=first["runId"], reason="tests failed")
        with self.assertRaisesRegex(worker.WorkerError, "already retried as"):
            self.run_mode("implement", retry_of=first["runId"], reason="tests failed again")

    def test_concurrent_retries_of_one_run_cannot_both_claim_it(self) -> None:
        first = self.run_mode("implement")
        worker.claim_retry(first["runId"], "20260101-000000-abcd")
        with self.assertRaisesRegex(worker.WorkerError, "already retried"):
            worker.claim_retry(first["runId"], "20260101-000001-abcd")

    def test_a_run_is_retried_at_most_twice(self) -> None:
        first = self.run_mode("research")
        second = self.run_mode("research", retry_of=first["runId"], reason="wrong citations")
        third = self.run_mode("research", retry_of=second["runId"], reason="wrong citations")
        self.assertEqual(third["profile"], "deep")
        with self.assertRaisesRegex(worker.WorkerError, "already retried 2 times"):
            self.run_mode("research", retry_of=third["runId"], reason="wrong citations")

    def test_a_run_on_the_top_profile_cannot_be_retried(self) -> None:
        first = self.run_mode("review")
        second = self.run_mode("review", retry_of=first["runId"], reason="missed a bug")
        self.assertEqual(second["profile"], "heavy")
        with self.assertRaisesRegex(worker.WorkerError, "top profile"):
            self.run_mode("review", retry_of=second["runId"], reason="missed a bug")

    def test_a_retry_needs_a_reason(self) -> None:
        first = self.run_mode("implement")
        with self.assertRaisesRegex(worker.WorkerError, "--reason"):
            self.run_mode("implement", retry_of=first["runId"])

    def test_a_retry_keeps_the_mode_and_picks_its_own_profile(self) -> None:
        first = self.run_mode("research")
        with self.assertRaisesRegex(worker.WorkerError, "not implement"):
            self.run_mode("implement", retry_of=first["runId"], reason="x")
        with self.assertRaisesRegex(worker.WorkerError, "do not pass --profile"):
            self.run_mode("research", retry_of=first["runId"], profile="deep", reason="x")
        with self.assertRaisesRegex(worker.WorkerError, "no such run"):
            self.run_mode("research", retry_of="20260101-000000-abcd", reason="x")

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

    def test_a_worker_that_switches_branch_fails_the_run(self) -> None:
        # Its commits would be on the other branch, so merging copilot/<run-id> would miss them.
        self.behavior("switch")
        result = self.run_mode("implement")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["currentBranch"], "worker-own-branch")
        self.assertEqual(result["branch"], f"copilot/{result['runId']}")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            worker.print_summary(result)
        self.assertIn("worker-own-branch", stdout.getvalue())

    def test_an_implement_run_records_that_it_stayed_on_its_branch(self) -> None:
        result = self.run_mode("implement")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["currentBranch"], result["branch"])

    def test_implement_summary_reports_the_change_counts(self) -> None:
        result = self.run_mode("implement")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            worker.print_summary(result)
        self.assertIn("changes: 1 uncommitted, 0 commits\n", stdout.getvalue())
        self.assertIn("  ?? worker_output.txt\n", stdout.getvalue())

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
        self.assert_process_gone(self.pid_file)

    def test_timeout_also_kills_a_grandchild_that_ignores_sigterm(self) -> None:
        self.behavior("grandchild")
        result = self.run_mode("research", timeout=2)
        self.assertEqual(result["status"], "timed_out")
        self.assert_process_gone(self.pid_file)
        self.assert_process_gone(self.child_pid_file)

    def test_a_process_the_worker_leaves_running_is_killed_on_normal_exit(self) -> None:
        # Otherwise it could keep changing the worktree after result.json says the run is over.
        self.behavior("lingering")
        result = self.run_mode("implement")
        self.assertEqual(result["status"], "completed")
        self.assert_process_gone(self.child_pid_file)

    def test_second_signal_during_the_kill_still_writes_a_result(self) -> None:
        # A stubborn worker keeps the script in its kill grace period when signal two lands.
        # Windows has no grace period, so there signal two can land after the run ends; the
        # handler the script restores then must not end the test process.
        self.behavior("stubborn")
        self.addCleanup(signal.signal, signal.SIGTERM, signal.signal(signal.SIGTERM, lambda *_: None))

        def signal_twice() -> None:
            deadline = time.monotonic() + 10
            while not self.pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            time.sleep(0.2)
            signal_self(signal.SIGTERM)
            time.sleep(0.3)
            signal_self(signal.SIGTERM)

        sender = threading.Thread(target=signal_twice)
        with patch.object(worker, "KILL_GRACE_SECONDS", 1):
            sender.start()
            try:
                result = self.run_mode("research")
            finally:
                sender.join()
        self.assertEqual(result["terminationReason"], f"signal:{int(signal.SIGTERM)}")
        self.assertEqual(result["status"], "failed")
        self.assertTrue((Path(result["runDir"]) / "result.json").exists())
        self.assert_process_gone(self.pid_file)

    def test_result_is_written_when_the_worker_destroys_its_worktree(self) -> None:
        self.behavior("wreck")
        result = self.run_mode("implement")
        self.assertEqual(result["status"], "completed")
        self.assertIsNone(result["changedFiles"])
        self.assertTrue((Path(result["runDir"]) / "result.json").exists())
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            worker.print_summary(result)
            # The run is still recorded, so clean can find and remove what is left.
            code = worker.main(["clean", result["runId"]], cwd=self.repo)
        self.assertEqual(code, 0)
        self.assertIn("changes: unavailable", stdout.getvalue())
        self.assertFalse(Path(result["workspace"]).exists())
        self.assertEqual(self.git("branch", "--list", result["branch"]), "")
        self.assertNotIn(result["workspace"], self.git("worktree", "list"))

    def test_missing_binary_is_recorded_as_a_spawn_error(self) -> None:
        os.environ["COPILOT_WORKER_ENGINE"] = str(self.home / "no-such-copilot")
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

    def test_cli_run_takes_profile_and_reason(self) -> None:
        process = self.cli("run", "--mode", "implement", "--task-file", self.task_file(),
                           "--profile", "deep", "--reason", "touches three modules")
        stdout, _ = process.communicate(timeout=30)
        self.assertEqual(process.returncode, 0)
        self.assertIn("profile: deep (attempt 1)", stdout)
        self.assertIn("model: gpt-6.1-sol (effort medium)", stdout)

    def test_cli_run_exits_two_for_effort_max_and_says_why(self) -> None:
        process = self.cli("run", "--mode", "implement", "--task-file", self.task_file(),
                           "--effort", "max", "--reason", "hard")
        _, stderr = process.communicate(timeout=30)
        self.assertEqual(process.returncode, 2)
        self.assertIn("max is not allowed", stderr)

    def test_cli_run_exits_two_for_an_off_default_run_without_a_reason(self) -> None:
        process = self.cli("run", "--mode", "implement", "--task-file", self.task_file(),
                           "--profile", "deep")
        _, stderr = process.communicate(timeout=30)
        self.assertEqual(process.returncode, 2)
        self.assertIn("--reason", stderr)

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
        process.stdin = None  # Python 3.9's communicate() would flush the closed pipe.
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

    def wait_for_worker(self) -> None:
        deadline = time.monotonic() + 10
        while not (self.pid_file.exists() and self.pid_file.read_text()):
            self.assertLess(time.monotonic(), deadline, "worker never started")
            time.sleep(0.05)
        time.sleep(0.3)

    def test_sigterm_kills_the_worker_and_still_writes_a_result(self) -> None:
        # Invariant 5. Windows cannot deliver SIGTERM to another process; Ctrl+Break is
        # the stop signal a console process there can catch.
        self.behavior("sleep")
        if WINDOWS:
            process = self.cli("run", "--mode", "research", "--task-file", self.task_file(),
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            stop, received = signal.CTRL_BREAK_EVENT, signal.SIGBREAK
        else:
            process = self.cli("run", "--mode", "research", "--task-file", self.task_file())
            stop = received = signal.SIGTERM
        self.wait_for_worker()
        process.send_signal(stop)
        process.communicate(timeout=30)
        self.assertEqual(process.returncode, 1)
        result = self.results()[0]
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["terminationReason"], f"signal:{int(received)}")
        self.assert_process_gone(self.pid_file)

    @unittest.skipUnless(WINDOWS, "a job object holds the worker only on Windows")
    def test_a_stop_before_the_worker_joins_the_job_still_ends_it(self) -> None:
        # A signal can land between Popen and started(), while the worker is suspended
        # and outside the job. Stopping must end it rather than wait on it forever.
        job = worker._JobObject()
        self.addCleanup(job.close)
        process = subprocess.Popen(
            [sys.executable, "-c", "pass"], stdin=subprocess.DEVNULL, **job.popen_options)
        stopper = threading.Thread(target=job.stop, args=(process,), daemon=True)
        stopper.start()
        stopper.join(timeout=10)
        self.assertFalse(stopper.is_alive(), "stop() hung on a worker outside the job")
        self.assertIsNotNone(process.poll())

    @unittest.skipUnless(WINDOWS, "a job object holds the worker only on Windows")
    def test_killing_the_supervisor_also_kills_the_worker_on_windows(self) -> None:
        # The job closes with the supervisor, so no worker runs on without anyone recording it.
        self.behavior("grandchild")
        process = self.cli("run", "--mode", "research", "--task-file", self.task_file())
        self.wait_for_worker()
        process.kill()
        process.communicate(timeout=30)
        self.assert_process_gone(self.pid_file)
        self.assert_process_gone(self.child_pid_file)


class CleanAndCheckTests(WorkerTestCase):
    def main(self, *args: str, cwd: Path | None = None) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = worker.main(list(args), cwd=cwd or self.repo)
        return code, stdout.getvalue(), stderr.getvalue()

    def implement(self) -> dict:
        return worker.execute_run(mode="implement", task="Do the task.", cwd=self.repo)

    def test_clean_removes_the_worktree_and_branch_but_keeps_the_run(self) -> None:
        result = self.implement()
        code, _, _ = self.main("clean", result["runId"])
        self.assertEqual(code, 0)
        self.assertFalse(Path(result["workspace"]).exists())
        self.assertEqual(self.git("branch", "--list", result["branch"]), "")
        self.assertNotIn(result["workspace"], self.git("worktree", "list"))
        self.assertTrue((Path(result["runDir"]) / "result.json").exists())
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "HEAD"), "main")

    def test_clean_twice_succeeds(self) -> None:
        result = self.implement()
        self.assertEqual(self.main("clean", result["runId"])[0], 0)
        self.assertEqual(self.main("clean", result["runId"])[0], 0)

    def test_clean_succeeds_after_the_worktree_was_deleted_by_hand(self) -> None:
        result = self.implement()
        shutil.rmtree(result["workspace"])
        self.assertEqual(self.main("clean", result["runId"])[0], 0)
        self.assertEqual(self.git("branch", "--list", result["branch"]), "")

    def test_clean_rejects_a_malformed_run_id(self) -> None:
        for bad in ("main", "../x", "20261001-120000-zzzz", ""):
            code, _, stderr = self.main("clean", bad)
            self.assertEqual(code, 2)
            self.assertIn("error:", stderr)

    def test_clean_rejects_an_unknown_run(self) -> None:
        code, _, stderr = self.main("clean", "20200101-000000-abcd")
        self.assertEqual(code, 2)
        self.assertIn("no such run", stderr)

    def test_clean_of_a_read_only_run_does_nothing(self) -> None:
        result = worker.execute_run(mode="research", task="Look.", cwd=self.repo)
        code, stdout, _ = self.main("clean", result["runId"])
        self.assertEqual(code, 0)
        self.assertIn("nothing to clean", stdout)

    def test_check_reports_the_version_and_repository(self) -> None:
        code, stdout, _ = self.main("check")
        self.assertEqual(code, 0)
        self.assertIn("github-copilot-sdk 0.0.0-fake (runtime fake)", stdout)
        self.assertIn("pins: pins ok", stdout)
        self.assertIn(str(self.repo), stdout)
        self.assertEqual(self.calls(), [])

    def test_check_fails_when_the_sdk_or_runtime_is_not_the_pinned_one(self) -> None:
        with patch.dict(os.environ, {"FAKE_COPILOT_PINS": "mismatch"}):
            code, stdout, _ = self.main("check")
        self.assertEqual(code, 1)
        self.assertIn("pins: pin mismatch", stdout)

    def test_check_fails_when_the_binary_is_missing(self) -> None:
        os.environ["COPILOT_WORKER_ENGINE"] = str(self.home / "no-such-copilot")
        code, stdout, _ = self.main("check")
        self.assertEqual(code, 1)
        self.assertIn("copilot sdk: NOT AVAILABLE", stdout)

    def test_check_fails_outside_a_repository(self) -> None:
        code, stdout, _ = self.main("check", cwd=self.repo.parent)
        self.assertEqual(code, 1)
        self.assertIn("repository: NOT A GIT REPOSITORY", stdout)

    def test_check_live_checks_the_catalog_then_probes_each_profile_once(self) -> None:
        code, stdout, _ = self.main("check", "--live")
        self.assertEqual(code, 0)
        self.assertIn("profile deep (gpt-6.1-sol, effort medium): offered", stdout)
        probes = [(call["model"], call["effort"]) for call in self.calls()]
        self.assertEqual(probes, [
            ("gpt-6-luna", "medium"), ("gpt-6.1-terra", "medium"),
            ("gpt-6.1-sol", "medium"), ("gpt-6-astra", "medium"),
        ])
        for name in worker.PROFILES:
            self.assertIn(f"probe {name}: ok", stdout)

    def test_check_live_fails_without_probing_when_a_model_is_not_offered(self) -> None:
        os.environ["FAKE_COPILOT_MODELS"] = json.dumps([
            {"id": "gpt-6-luna", "supportedReasoningEfforts": ["medium"]},
            {"id": "gpt-6.1-sol", "supportedReasoningEfforts": ["medium"]},
            {"id": "gpt-6-astra", "supportedReasoningEfforts": ["medium"]},
        ])
        code, stdout, _ = self.main("check", "--live")
        self.assertEqual(code, 1)
        self.assertIn("profile standard (gpt-6.1-terra, effort medium): NOT OFFERED: no model gpt-6.1-terra", stdout)
        self.assertIn("profile light (gpt-6-luna, effort medium): offered", stdout)
        self.assertEqual(self.calls(), [])

    def test_check_live_fails_when_a_profile_effort_is_not_supported(self) -> None:
        os.environ["FAKE_COPILOT_MODELS"] = json.dumps([
            {"id": "gpt-6-luna", "supportedReasoningEfforts": ["low", "medium"]},
            {"id": "gpt-6.1-terra", "supportedReasoningEfforts": ["low", "medium", "high"]},
            {"id": "gpt-6.1-sol", "supportedReasoningEfforts": ["low", "high"]},
            {"id": "gpt-6-astra", "supportedReasoningEfforts": ["medium"]},
        ])
        code, stdout, _ = self.main("check", "--live")
        self.assertEqual(code, 1)
        self.assertIn("gpt-6.1-sol does not support effort medium (supports: low, high)", stdout)
        self.assertIn("profile standard (gpt-6.1-terra, effort medium): offered", stdout)

    def test_check_live_fails_when_the_models_cannot_be_listed(self) -> None:
        os.environ["FAKE_COPILOT_MODELS"] = "fail"
        code, stdout, _ = self.main("check", "--live")
        self.assertEqual(code, 1)
        self.assertIn("models: could not list them: not signed in", stdout)
        self.assertEqual(self.calls(), [])

    def test_check_live_fails_when_a_probe_is_rejected(self) -> None:
        self.behavior("fail")
        code, stdout, _ = self.main("check", "--live")
        self.assertEqual(code, 1)
        self.assertIn("probe light: failed", stdout)


if __name__ == "__main__":
    unittest.main()

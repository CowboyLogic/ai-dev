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


if __name__ == "__main__":
    unittest.main()

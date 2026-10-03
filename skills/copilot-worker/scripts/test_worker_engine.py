#!/usr/bin/env python3
"""Unit tests for the worker engine's policy and helpers. They need no SDK."""

from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import worker_engine as engine  # noqa: E402


class PolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        # Deliberately unresolved: on macOS this is under /var, which is a symlink to /private/var.
        self.workspace = os.path.join(tmp.name, "my repo")
        os.mkdir(self.workspace)

    def shell(self, *segments: str, mode: str = "implement") -> tuple[bool, str]:
        return engine.decide("shell", {"segments": list(segments)}, self.workspace, mode)

    def test_ordinary_shell_commands_are_allowed_in_implement(self) -> None:
        for command in ("git status --short", "npm test", "python -m unittest", "git commit -m x"):
            self.assertTrue(self.shell(command)[0], command)

    def test_denied_commands_are_rejected(self) -> None:
        for command in (
            "gh --version", "gh pr create", "sudo rm -rf /", "git push", "git push origin main",
            "git remote add x y", "git worktree add ../x",
        ):
            allowed, reason = self.shell(command)
            self.assertFalse(allowed, command)
            self.assertIn("denied", reason)

    def test_wrappers_assignments_and_paths_do_not_hide_a_denied_command(self) -> None:
        for command in (
            "/usr/local/bin/gh auth status", "GH_TOKEN=x gh api user", "env gh --version",
            "command git push", "nohup git push &", "time sudo ls", "exec gh repo view",
            "env FOO=1 BAR=2 git push", "git -C ../other push", "git -c user.name=x push",
        ):
            self.assertFalse(self.shell(command)[0], command)

    def test_a_denied_command_anywhere_in_a_compound_line_is_rejected(self) -> None:
        for command in ("git status && git push", "ls; gh pr list", "echo x | gh api -", "true || sudo ls"):
            self.assertFalse(self.shell(command)[0], command)

    def test_any_denied_segment_rejects_the_request(self) -> None:
        self.assertFalse(self.shell("git status", "git push")[0])

    def test_lookalike_commands_are_not_denied(self) -> None:
        for command in ("ghc --version", "git pushd", "echo gh", "git log --grep=push"):
            self.assertTrue(self.shell(command)[0], command)

    def test_unparseable_shell_text_is_still_checked(self) -> None:
        self.assertFalse(self.shell("gh 'unterminated")[0])

    def test_shell_is_rejected_outside_implement(self) -> None:
        for mode in ("research", "review"):
            self.assertFalse(self.shell("git status", mode=mode)[0])

    def test_shell_request_without_any_command_text_is_rejected(self) -> None:
        self.assertFalse(self.shell()[0])

    def test_writes_inside_the_workspace_are_allowed_in_implement(self) -> None:
        for path in ("new.txt", os.path.join(self.workspace, "src", "a.py")):
            self.assertTrue(engine.decide("write", {"path": path}, self.workspace, "implement")[0], path)

    def test_writes_are_rejected_outside_implement(self) -> None:
        path = os.path.join(self.workspace, "a.txt")
        for mode in ("research", "review"):
            self.assertFalse(engine.decide("write", {"path": path}, self.workspace, mode)[0])

    def test_reads_and_writes_outside_the_workspace_are_rejected(self) -> None:
        sibling = self.workspace + "-other"
        for path in ("/etc/hosts", os.path.join(sibling, "x.txt"), os.path.join(self.workspace, "..", "x"), None, ""):
            for kind in ("read", "write"):
                allowed, reason = engine.decide(kind, {"path": path}, self.workspace, "implement")
                self.assertFalse(allowed, f"{kind} {path!r}")

    def test_containment_compares_resolved_paths(self) -> None:
        # The SDK reports /private/var/... while the workspace may be configured as /var/...
        resolved = os.path.join(os.path.realpath(self.workspace), "inside.txt")
        self.assertTrue(engine.decide("read", {"path": resolved}, self.workspace, "research")[0])
        self.assertTrue(
            engine.decide("read", {"path": os.path.join(self.workspace, "inside.txt")},
                          os.path.realpath(self.workspace), "research")[0]
        )

    def test_a_symlink_inside_the_workspace_that_points_outside_is_rejected(self) -> None:
        link = os.path.join(self.workspace, "escape")
        os.symlink("/etc", link)
        self.assertFalse(engine.decide("read", {"path": os.path.join(link, "hosts")}, self.workspace, "research")[0])

    def test_reading_the_workspace_root_itself_is_allowed(self) -> None:
        self.assertTrue(engine.decide("read", {"path": self.workspace}, self.workspace, "research")[0])

    def test_unknown_request_kinds_are_rejected(self) -> None:
        for kind in ("mcp", "url", "memory", "custom-tool", "extension", "something-new"):
            self.assertFalse(engine.decide(kind, {}, self.workspace, "implement")[0], kind)


if __name__ == "__main__":
    unittest.main()

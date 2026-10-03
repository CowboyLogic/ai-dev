#!/usr/bin/env python3
"""Unit tests for the worker engine's policy and helpers. They need no SDK."""

from __future__ import annotations

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import unittest.mock

sys.path.insert(0, str(Path(__file__).parent))
import worker_engine as engine  # noqa: E402


class PinTests(unittest.TestCase):
    PINS = {"sdk": "1.0.14", "runtime": "1.0.85"}

    def test_matching_versions_are_not_a_problem(self) -> None:
        info = {"sdkVersion": "1.0.14", "runtimeVersion": "1.0.85"}
        self.assertIsNone(engine.pin_problem(info, self.PINS))

    def test_a_different_sdk_is_reported(self) -> None:
        info = {"sdkVersion": "1.0.15", "runtimeVersion": "1.0.85"}
        problem = engine.pin_problem(info, self.PINS)
        self.assertIn("github-copilot-sdk is 1.0.15, pinned to 1.0.14", problem)
        self.assertNotIn("runtime", problem)

    def test_a_different_runtime_is_reported(self) -> None:
        info = {"sdkVersion": "1.0.14", "runtimeVersion": "1.0.86"}
        self.assertIn("runtime is 1.0.86, pinned to 1.0.85", engine.pin_problem(info, self.PINS))

    def test_both_differences_are_reported_together(self) -> None:
        info = {"sdkVersion": "2.0.0", "runtimeVersion": "2.0.1"}
        problem = engine.pin_problem(info, self.PINS)
        self.assertIn("github-copilot-sdk", problem)
        self.assertIn("runtime", problem)

    def test_a_pins_file_missing_a_key_is_a_problem_not_a_pass(self) -> None:
        info = {"sdkVersion": "1.0.14", "runtimeVersion": "1.0.85"}
        self.assertIsNotNone(engine.pin_problem(info, {"sdk": "1.0.14"}))

    def run_main(self, info: dict, argv: list[str]) -> tuple[int, str, str, unittest.mock.MagicMock]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(engine, "versions", return_value=info), \
                unittest.mock.patch.object(engine, "load_pins", return_value=self.PINS), \
                unittest.mock.patch.object(engine, "drive", new=unittest.mock.MagicMock()), \
                unittest.mock.patch.object(engine.asyncio, "run") as run, \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = engine.main(argv)
        return code, stdout.getvalue(), stderr.getvalue(), run

    def test_a_run_refuses_to_start_on_mismatched_pins(self) -> None:
        info = {"sdkVersion": "9.9.9", "runtimeVersion": "1.0.85"}
        code, _, stderr, run = self.run_main(info, ["/some/run/dir"])
        self.assertEqual(code, 3)
        self.assertIn("pin mismatch", stderr)
        self.assertIn("references/upgrading.md", stderr)
        run.assert_not_called()

    def test_a_run_starts_when_the_pins_match(self) -> None:
        info = {"sdkVersion": "1.0.14", "runtimeVersion": "1.0.85"}
        code, _, _, run = self.run_main(info, ["/some/run/dir"])
        self.assertEqual(code, 0)
        run.assert_called_once()

    def test_check_pins_reports_and_never_starts_a_run(self) -> None:
        bad = {"sdkVersion": "1.0.14", "runtimeVersion": "9.9.9"}
        code, stdout, _, run = self.run_main(bad, ["--check-pins"])
        self.assertEqual((code, "pin mismatch" in stdout), (1, True))
        good = {"sdkVersion": "1.0.14", "runtimeVersion": "1.0.85"}
        code, stdout, _, run = self.run_main(good, ["--check-pins"])
        self.assertEqual((code, stdout.strip()), (0, "pins ok"))
        run.assert_not_called()

    def test_the_shipped_pins_file_loads(self) -> None:
        self.assertEqual(sorted(engine.load_pins()), ["runtime", "sdk"])


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

    def test_case_does_not_hide_a_denied_command(self) -> None:
        # macOS file systems are case-insensitive: GH and Git run gh and git.
        for command in ("GH pr list", "Gh pr list", "Git push", "git Push", "SUDO ls", "/usr/bin/Git push"):
            self.assertFalse(self.shell(command)[0], command)

    def test_wrapper_options_and_more_wrappers_do_not_hide_a_denied_command(self) -> None:
        for command in (
            "env -u FOO gh pr list", "env -P /opt/homebrew/bin gh pr list", "exec -a nice gh pr list",
            "xargs gh pr list", "echo pr list | xargs gh", "timeout 30 gh pr create",
            "nice gh pr list", "nice -n 5 git push", "caffeinate gh pr list", "eval gh pr list",
            "stdbuf -oL gh pr list", "doas ls",
        ):
            self.assertFalse(self.shell(command)[0], command)

    def test_wrapper_options_that_take_a_separate_value_do_not_hide_a_denied_command(self) -> None:
        for command in (
            "xargs --max-args 1 gh", "xargs --max-procs 2 gh pr list", "xargs --delimiter , gh",
            "stdbuf -o L gh", "stdbuf --output L gh", "stdbuf -i0 -e L git push",
            "nice --adjustment 5 gh", "env -a name gh pr list", "env --argv0 name gh",
            "time -o out.txt gh pr list", "time --format %e git push",
        ):
            self.assertFalse(self.shell(command)[0], command)

    def test_compound_payloads_in_quotes_are_checked_whole(self) -> None:
        for command in (
            "bash -c 'echo ok; git push'", "eval 'echo ok; git push'", 'sh -c "echo ok; gh pr create"',
            "bash -c 'cd x && git push origin main'", "bash -lc 'ls | gh auth token'",
            'echo "$(true)"; git push', 'echo "$(gh auth token)"', "echo \"`gh auth token`\"",
            "echo 'a'; git push", 'echo "a" && gh pr list', "bash -c 'echo \\'; git push",
        ):
            self.assertFalse(self.shell(command)[0], command)
        for command in (
            "echo 'a; b'", 'echo "a; b"', "git commit -m 'fix; thing'", "bash -c 'echo ok; ls'",
            'echo "$(date)"', "echo 'it'\\''s; fine'",
        ):
            self.assertTrue(self.shell(command)[0], command)

    def test_a_denied_looking_command_inside_quotes_is_only_text(self) -> None:
        for command in (
            "echo 'safe; gh pr list'", 'git commit -m "fix; git push handling"',
            "echo 'a && gh auth token'", "grep -n 'x | gh' file.txt",
        ):
            self.assertTrue(self.shell(command)[0], command)
        for command in ("echo 'a; b'; git push", "gh 'unterminated", 'echo "oops; git push'):
            self.assertFalse(self.shell(command)[0], command)

    def test_environment_injected_git_config_is_denied(self) -> None:
        for command in (
            "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=alias.p GIT_CONFIG_VALUE_0=push git p",
            "env GIT_CONFIG_KEY_0=alias.p GIT_CONFIG_VALUE_0=push GIT_CONFIG_COUNT=1 git p",
            "GIT_CONFIG_PARAMETERS=\"'alias.p=push'\" git p",
            "GIT_CONFIG_GLOBAL=./evil.cfg git p", "GIT_CONFIG_SYSTEM=evil.cfg git status",
            "export GIT_CONFIG_KEY_0=alias.p", "declare -x GIT_CONFIG_GLOBAL=./evil.cfg",
        ):
            self.assertFalse(self.shell(command)[0], command)
        for command in (
            "GIT_CONFIG_GLOBAL=/dev/null git status", "GIT_CONFIG_NOSYSTEM=1 git log",
            "GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.pager GIT_CONFIG_VALUE_0=cat git log",
            "export PATH=/usr/bin", "export GIT_AUTHOR_NAME=x",
        ):
            self.assertTrue(self.shell(command)[0], command)

    def test_clustered_short_options_do_not_hide_a_denied_command(self) -> None:
        for command in (
            "script -qc 'git push' /tmp/log", "script -qc'gh pr list' /dev/null",
            "env -iS 'gh --version'", "env -iSgh", "env -i -S 'git push'",
            "xargs -tn1 gh", "xargs -tI{} gh pr list {}", "stdbuf -oL -eL gh",
        ):
            self.assertFalse(self.shell(command)[0], command)
        for command in ("env -i ls", "script -q /dev/null", "xargs -t echo", "stdbuf -oL ls"):
            self.assertTrue(self.shell(command)[0], command)

    def test_line_continuations_do_not_hide_a_denied_command(self) -> None:
        for command in ("git \\\npush --dry-run", "gh \\\n pr list", "g\\\nh pr list", "env \\\n  gh pr list"):
            self.assertFalse(self.shell(command)[0], repr(command))
        self.assertTrue(self.shell("echo a \\\n b")[0])

    def test_bsd_xargs_value_options_do_not_hide_a_denied_command(self) -> None:
        for command in ("xargs -J % gh --version %", "xargs -R 1 gh", "xargs -S 255 gh pr list"):
            self.assertFalse(self.shell(command)[0], command)

    def test_shell_reserved_words_do_not_hide_a_denied_command(self) -> None:
        for command in (
            "! gh --version", "echo a && ! git push", "if gh pr list; then echo ok; fi",
            "while gh pr list; do :; done", "until gh auth status; do sleep 1; done",
            "if true; then gh pr create; fi", "coproc gh pr list",
        ):
            self.assertFalse(self.shell(command)[0], command)
        self.assertTrue(self.shell("if true; then echo ok; fi")[0])

    def test_shell_and_eval_payloads_are_checked(self) -> None:
        for command in ("bash -c 'gh pr create'", 'sh -c "git push"', "zsh -c 'sudo ls'", "bash -lc 'gh auth token'"):
            self.assertFalse(self.shell(command)[0], command)

    def test_redirections_grouping_and_substitution_do_not_hide_a_denied_command(self) -> None:
        for command in (
            ">/dev/null gh pr create", "</dev/null gh pr create", "2>/dev/null gh pr list",
            "(gh pr list)", "{ gh pr list; }", "(git push origin main)",
            "echo $(gh auth token)", "echo `gh auth token`", "x=$(git push)",
        ):
            self.assertFalse(self.shell(command)[0], command)

    def test_git_routes_to_push_or_change_remotes_are_denied(self) -> None:
        for command in (
            "git -c alias.p=push p", "git -c 'alias.x=!gh pr create' x", "git send-pack --all origin",
            "git config remote.origin.url https://example.com/x", "git config --add remote.x.url y",
            "git-push origin main", "/opt/homebrew/opt/git/libexec/git-core/git-push origin main",
        ):
            self.assertFalse(self.shell(command)[0], command)

    def test_git_config_env_aliases_are_denied(self) -> None:
        for command in ("FOO=push git --config-env=alias.p=FOO p", "git --config-env alias.p=FOO p"):
            self.assertFalse(self.shell(command)[0], command)
        self.assertTrue(self.shell("git --config-env=core.pager=PAGER log")[0])

    def test_configuring_a_git_alias_is_denied(self) -> None:
        for command in (
            "git config alias.p push", "git config --global alias.p push", "git config --add alias.p push",
            "git -C sub config alias.p 'push origin main'",
        ):
            self.assertFalse(self.shell(command)[0], command)

    def test_a_subcommand_that_is_a_configured_alias_is_denied(self) -> None:
        aliases = frozenset({"p", "ship"})
        for command in ("git p origin main", "git -C sub ship", "git P origin main", "env git p"):
            allowed, reason = engine.decide(
                "shell", {"segments": [command]}, self.workspace, "implement", aliases)
            self.assertFalse(allowed, command)
            self.assertIn("git alias", reason)
        self.assertTrue(engine.decide(
            "shell", {"segments": ["git status"]}, self.workspace, "implement", aliases)[0])

    def test_configured_aliases_are_read_from_the_repository_config(self) -> None:
        subprocess.run(["git", "init", "-q", self.workspace], check=True)
        subprocess.run(["git", "-C", self.workspace, "config", "alias.p", "push"], check=True)
        self.assertIn("p", engine.configured_aliases(self.workspace))

    def test_configured_aliases_is_empty_outside_a_repository(self) -> None:
        env = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
        with unittest.mock.patch.dict(os.environ, env):
            self.assertEqual(engine.configured_aliases(self.workspace), frozenset())

    def test_commands_carried_in_wrapper_option_values_are_checked(self) -> None:
        for command in (
            "env -S 'gh --version'", "env --split-string='git push'", "env -S'gh pr list'",
            "script -c 'git push' /tmp/log", "script --command='gh pr list' /dev/null",
        ):
            self.assertFalse(self.shell(command)[0], command)

    def test_ordinary_git_config_and_options_are_still_allowed(self) -> None:
        for command in ("git config user.name x", "git -c core.pager=cat log", "git config --get user.email"):
            self.assertTrue(self.shell(command)[0], command)

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

    def test_home_and_variable_paths_are_rejected(self) -> None:
        for path in ("~/.ssh/id_rsa", "~", "$HOME/.ssh/id_rsa", "${HOME}/x", "a/$X/b"):
            self.assertFalse(engine.decide("read", {"path": path}, self.workspace, "research")[0], path)

    def test_reading_the_workspace_root_itself_is_allowed(self) -> None:
        self.assertTrue(engine.decide("read", {"path": self.workspace}, self.workspace, "research")[0])

    def test_unknown_request_kinds_are_rejected(self) -> None:
        for kind in ("mcp", "url", "memory", "custom-tool", "extension", "something-new"):
            self.assertFalse(engine.decide(kind, {}, self.workspace, "implement")[0], kind)


class PermissionRequestShell:
    def __init__(self, full_command_text=None, command_segments=(), commands=()):
        self.full_command_text = full_command_text
        self.command_segments = list(command_segments)
        self.commands = list(commands)


class PermissionRequestWrite:
    def __init__(self, resolved_path=None, file_name=None):
        self.resolved_path = resolved_path
        self.file_name = file_name


class PermissionRequestRead:
    def __init__(self, resolved_path=None, path=None):
        self.resolved_path = resolved_path
        self.path = path


class PermissionRequestMcp:
    pass


class Part:
    def __init__(self, full_command_text=None, identifier=None):
        self.full_command_text = full_command_text
        self.identifier = identifier


class HelperTests(unittest.TestCase):
    config = {
        "mode": "implement", "model": "gpt-6.1-sol", "effort": None, "credits": 60,
        "timeout": 1800, "workspace": "/w", "copilotHome": "/home/state/copilot-home",
    }

    def test_request_kinds_map_from_sdk_class_names(self) -> None:
        self.assertEqual(engine.request_kind(PermissionRequestShell()), "shell")
        self.assertEqual(engine.request_kind(PermissionRequestWrite()), "write")
        self.assertEqual(engine.request_kind(PermissionRequestRead()), "read")
        self.assertEqual(engine.request_kind(PermissionRequestMcp()), "mcp")

    def test_shell_fields_collect_every_command_text_the_sdk_offers(self) -> None:
        request = PermissionRequestShell(
            "git status && gh pr list",
            command_segments=[Part("git status"), Part(None, "gh pr list")],
            commands=[Part(identifier="git status")],
        )
        segments = engine.request_fields(request)["segments"]
        for text in ("git status && gh pr list", "git status", "gh pr list"):
            self.assertIn(text, segments)

    def test_path_fields_prefer_the_resolved_path(self) -> None:
        self.assertEqual(engine.request_fields(PermissionRequestWrite("/w/a", "a"))["path"], "/w/a")
        self.assertEqual(engine.request_fields(PermissionRequestWrite(None, "a"))["path"], "a")
        self.assertEqual(engine.request_fields(PermissionRequestRead(None, "/w/b"))["path"], "/w/b")

    def test_tools_per_mode(self) -> None:
        self.assertEqual(engine.TOOLS["research"], ("view", "rg", "glob"))
        self.assertEqual(engine.TOOLS["review"], ("view", "rg", "glob"))
        self.assertEqual(
            engine.TOOLS["implement"],
            ("view", "rg", "glob", "apply_patch",
             "bash", "read_bash", "stop_bash", "list_bash"),
        )

    def test_session_options(self) -> None:
        options = engine.session_options(self.config)
        self.assertEqual(options["model"], "gpt-6.1-sol")
        self.assertEqual(options["working_directory"], "/w")
        self.assertEqual(options["session_limits"], {"max_ai_credits": 60})
        self.assertEqual(options["available_tools"], engine.TOOLS["implement"])
        self.assertIs(options["enable_skills"], False)
        # Repository .github/hooks would otherwise run, and could settle permissions first.
        self.assertIs(options["enable_file_hooks"], False)
        self.assertEqual(options["disabled_mcp_servers"], ["github-mcp-server"])
        self.assertNotIn("reasoning_effort", options)
        with_effort = engine.session_options({**self.config, "effort": "high"})
        self.assertEqual(with_effort["reasoning_effort"], "high")

    def test_session_kwargs_wire_in_our_handler_events_and_tool_set(self) -> None:
        def on_permission(request, invocation):
            return None

        def on_event(event):
            return None

        sentinel_tools = object()
        kwargs = engine.session_kwargs(self.config, on_permission, on_event, sentinel_tools)
        self.assertIs(kwargs["on_permission_request"], on_permission)
        self.assertIs(kwargs["on_event"], on_event)
        self.assertIs(kwargs["available_tools"], sentinel_tools)
        self.assertIs(kwargs["enable_file_hooks"], False)

    def test_environment_is_scrubbed_of_copilot_overrides(self) -> None:
        # COPILOT_ALLOW_ALL could pre-approve tools; COPILOT_CLI_PATH would replace the pinned runtime.
        scrubbed = engine.scrub_environment({
            "PATH": "/bin", "HOME": "/h", "GH_TOKEN": "t", "COPILOT_GITHUB_TOKEN": "c",
            "COPILOT_ALLOW_ALL": "true", "COPILOT_CLI_PATH": "/tmp/evil", "COPILOT_HOME": "/x",
            "COPILOT_CLI_EXTRACT_DIR": "/tmp/cache", "COPILOT_SKIP_CLI_DOWNLOAD": "1",
            "COPILOT_WORKER_ENGINE": "fake",
        })
        self.assertEqual(
            scrubbed, {"PATH": "/bin", "HOME": "/h", "GH_TOKEN": "t", "COPILOT_GITHUB_TOKEN": "c"}
        )

    def test_client_gets_the_scrubbed_environment(self) -> None:
        env = {"PATH": "/bin"}
        self.assertIs(engine.client_options(self.config, env)["env"], env)

    def test_client_uses_the_isolated_copilot_home(self) -> None:
        options = engine.client_options(self.config, {})
        self.assertEqual(options["base_directory"], "/home/state/copilot-home")
        self.assertEqual(options["working_directory"], "/w")

    def test_send_never_uses_the_sdk_default_sixty_second_timeout(self) -> None:
        self.assertGreater(engine.send_options(self.config)["timeout"], self.config["timeout"])
        self.assertGreater(engine.send_options({**self.config, "timeout": 30})["timeout"], 60)

    def test_usage_is_summed_across_model_calls(self) -> None:
        usage = engine.summarize_usage([
            {"totalNanoAiu": 1_500_000_000, "inputTokens": 10, "outputTokens": 2,
             "cacheReadTokens": 100, "cacheWriteTokens": 5, "model": "gpt-6.1-sol"},
            {"totalNanoAiu": 500_000_000, "inputTokens": 3, "outputTokens": 1,
             "cacheReadTokens": 0, "cacheWriteTokens": 0, "model": "gpt-6.1-sol"},
        ])
        self.assertEqual(usage["aiCredits"], 2.0)
        self.assertEqual(usage["totalNanoAiu"], 2_000_000_000)
        self.assertEqual(usage["inputTokens"], 13)
        self.assertEqual(usage["outputTokens"], 3)
        self.assertEqual(usage["cacheReadTokens"], 100)
        self.assertEqual(usage["modelCalls"], 2)

    def test_usage_of_a_run_with_no_model_calls_is_zero(self) -> None:
        self.assertEqual(engine.summarize_usage([])["aiCredits"], 0)


if __name__ == "__main__":
    unittest.main()

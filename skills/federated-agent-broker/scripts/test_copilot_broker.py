#!/usr/bin/env python3
"""Focused unit tests for the dependency-free Copilot MCP broker."""

from __future__ import annotations

import json
from io import BytesIO
import os
from pathlib import Path
import select
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import copilot_broker as broker  # noqa: E402


class CopilotBrokerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = tempfile.TemporaryDirectory()
        self.addCleanup(self.state.cleanup)
        environment = patch.dict(os.environ, {"FEDERATED_BROKER_STATE_DIR": self.state.name})
        environment.start()
        self.addCleanup(environment.stop)

    def test_tools_list_exposes_the_bounded_surface(self) -> None:
        result = broker.McpServer().handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        )
        assert result is not None
        self.assertEqual(
            [tool["name"] for tool in result["result"]["tools"]],
            ["copilot_research", "copilot_review", "copilot_implement", "broker_status", "broker_receipt"],
        )

    def test_implementation_rejects_unbounded_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(broker.BrokerError, "relative paths"):
                broker.parse_request(
                    "implement",
                    {
                        "task": "Change one file",
                        "workspace": temporary_directory,
                        "writable_paths": ["../outside.py"],
                    },
                )

    def test_implementation_rejects_an_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            Path(temporary_directory, "src").mkdir()
            with self.assertRaisesRegex(broker.BrokerError, "existing directories"):
                broker.parse_request(
                    "implement",
                    {
                        "task": "Change one file",
                        "workspace": temporary_directory,
                        "writable_paths": ["src"],
                    },
                )

    def test_implementation_rejects_a_trailing_directory_separator(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(broker.BrokerError, "name files"):
                broker.parse_request(
                    "implement",
                    {
                        "task": "Change one file",
                        "workspace": temporary_directory,
                        "writable_paths": ["new-directory/"],
                    },
                )

    def test_implementation_rejects_a_symlinked_parent_outside_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with tempfile.TemporaryDirectory() as outside_directory:
                Path(temporary_directory, "out").symlink_to(outside_directory, target_is_directory=True)
                with self.assertRaisesRegex(broker.BrokerError, "resolve within the workspace"):
                    broker.parse_request(
                        "implement",
                        {
                            "task": "Change one file",
                            "workspace": temporary_directory,
                            "writable_paths": ["out/result.py"],
                        },
                    )

    def test_read_only_modes_reject_write_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(broker.BrokerError, "only for implementation"):
                broker.parse_request(
                    "research",
                    {
                        "task": "Inspect this code",
                        "workspace": temporary_directory,
                        "writable_paths": ["src/file.py"],
                    },
                )

    def test_implementation_rejects_permission_syntax_in_a_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(broker.BrokerError, "permission-syntax"):
                broker.parse_request(
                    "implement",
                    {
                        "task": "Change one file",
                        "workspace": temporary_directory,
                        "writable_paths": ["file),shell(git push"],
                    },
                )

    def test_model_rejects_option_syntax(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(broker.BrokerError, "letters, numbers"):
                broker.parse_request(
                    "research",
                    {
                        "task": "Inspect this code",
                        "workspace": temporary_directory,
                        "model": "--allow-all",
                    },
                )

    def test_profile_resolves_model_effort_context_and_budget(self) -> None:
        policy = {
            "defaultProfile": "work-review",
            "modeProfiles": {
                "research": "work-review",
                "review": "work-review",
                "implement": "work-review",
            },
            "profiles": {
                "work-review": {
                    "model": "gpt-5.4",
                    "effort": "high",
                    "context": "long_context",
                    "maxAiCredits": 30,
                    "timeoutSeconds": 420,
                }
            },
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            policy_path = Path(temporary_directory, "policy.json")
            policy_path.write_text(json.dumps(policy))
            old_policy = os.environ.get("FEDERATED_BROKER_POLICY")
            os.environ["FEDERATED_BROKER_POLICY"] = str(policy_path)
            try:
                request = broker.parse_request(
                    "review", {"task": "Review the proposed change", "workspace": temporary_directory}
                )
                tools = broker.tool_definitions()
            finally:
                if old_policy is None:
                    del os.environ["FEDERATED_BROKER_POLICY"]
                else:
                    os.environ["FEDERATED_BROKER_POLICY"] = old_policy
            self.assertEqual(request.profile, "work-review")
            self.assertEqual(request.model, "gpt-5.4")
            self.assertEqual(request.effort, "high")
            self.assertEqual(request.context, "long_context")
            self.assertEqual(request.max_ai_credits, 30)
            self.assertEqual(request.timeout_seconds, 420)
            self.assertEqual(
                tools[0]["inputSchema"]["properties"]["profile"]["enum"], ["work-review"]
            )
            command = broker._copilot_base_command(request, broker.build_prompt(request))
            self.assertEqual(command[command.index("--context") + 1], "long_context")

    def test_invalid_profile_value_returns_a_broker_error(self) -> None:
        policy = {
            "defaultProfile": "invalid",
            "modeProfiles": {
                "research": "invalid",
                "review": "invalid",
                "implement": "invalid",
            },
            "profiles": {
                "invalid": {
                    "model": "auto",
                    "effort": ["high"],
                    "context": {"tier": "default"},
                    "maxAiCredits": 30,
                    "timeoutSeconds": 180,
                }
            },
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            policy_path = Path(temporary_directory, "policy.json")
            policy_path.write_text(json.dumps(policy))
            old_policy = os.environ.get("FEDERATED_BROKER_POLICY")
            os.environ["FEDERATED_BROKER_POLICY"] = str(policy_path)
            try:
                with self.assertRaisesRegex(broker.BrokerError, "invalid.effort"):
                    broker.parse_request(
                        "research", {"task": "Inspect this code", "workspace": temporary_directory}
                    )
            finally:
                if old_policy is None:
                    del os.environ["FEDERATED_BROKER_POLICY"]
                else:
                    os.environ["FEDERATED_BROKER_POLICY"] = old_policy

    def test_research_uses_read_only_copilot_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            request = broker.parse_request(
                "research", {"task": "Explain this repository", "workspace": temporary_directory}
            )
            command = broker._copilot_base_command(request, broker.build_prompt(request))
            self.assertIn("--available-tools", command)
            self.assertIn("view", command)
            self.assertIn("read", command)
            self.assertNotIn("create", command)
            self.assertNotIn("edit", command)
            self.assertNotIn("apply_patch", command)
            self.assertNotIn("shell", command)

    def test_implementation_passes_one_exact_permission_per_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            request = broker.parse_request(
                "implement",
                {
                    "task": "Update the focused test",
                    "workspace": temporary_directory,
                    "writable_paths": ["tests/test_broker.py"],
                },
            )
            command = broker._copilot_base_command(request, broker.build_prompt(request))
            permissions = [
                command[index + 1]
                for index, value in enumerate(command)
                if value == "--allow-tool"
            ]
            self.assertEqual(
                permissions,
                ["read", "write(tests/test_broker.py)"],
            )
            self.assertIn("view,create,edit,apply_patch", command)
            self.assertNotIn("shell", command)

    def test_credit_caps_below_copilot_minimum_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(broker.BrokerError, "from 30 through 100"):
                broker.parse_request(
                    "research",
                    {
                        "task": "Inspect this code",
                        "workspace": temporary_directory,
                        "max_ai_credits": 29,
                    },
                )

    def test_credit_cap_at_copilot_minimum_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            request = broker.parse_request(
                "research",
                {
                    "task": "Inspect this code",
                    "workspace": temporary_directory,
                    "max_ai_credits": 30,
                },
            )
            self.assertEqual(request.max_ai_credits, 30)

    def test_profile_credit_below_copilot_minimum_is_rejected(self) -> None:
        policy = {
            "defaultProfile": "invalid-credit",
            "modeProfiles": {
                "research": "invalid-credit",
                "review": "invalid-credit",
                "implement": "invalid-credit",
            },
            "profiles": {
                "invalid-credit": {
                    "model": "auto",
                    "effort": "low",
                    "context": "default",
                    "maxAiCredits": 29,
                    "timeoutSeconds": 180,
                }
            },
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            policy_path = Path(temporary_directory, "policy.json")
            policy_path.write_text(json.dumps(policy))
            old_policy = os.environ.get("FEDERATED_BROKER_POLICY")
            os.environ["FEDERATED_BROKER_POLICY"] = str(policy_path)
            try:
                with self.assertRaisesRegex(broker.BrokerError, "invalid-credit.maxAiCredits"):
                    broker.parse_request(
                        "research", {"task": "Inspect this code", "workspace": temporary_directory}
                    )
            finally:
                if old_policy is None:
                    del os.environ["FEDERATED_BROKER_POLICY"]
                else:
                    os.environ["FEDERATED_BROKER_POLICY"] = old_policy

    def test_delegation_returns_a_structured_receipt_from_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            fake_copilot = root / "fake_copilot.py"
            fake_copilot.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                "print(json.dumps({'type': 'assistant.message', 'content': 'review complete'}))\n"
            )
            fake_copilot.chmod(fake_copilot.stat().st_mode | stat.S_IXUSR)
            old_binary = os.environ.get("FEDERATED_BROKER_COPILOT_BIN")
            os.environ["FEDERATED_BROKER_COPILOT_BIN"] = f"{sys.executable} {fake_copilot}"
            try:
                request = broker.parse_request(
                    "research", {"task": "Find the root cause", "workspace": temporary_directory}
                )
                receipt = broker.run_delegation(request)
            finally:
                if old_binary is None:
                    del os.environ["FEDERATED_BROKER_COPILOT_BIN"]
                else:
                    os.environ["FEDERATED_BROKER_COPILOT_BIN"] = old_binary
            self.assertEqual(receipt["status"], "completed")
            full = broker.broker_receipt(receipt["requestId"])
            self.assertEqual(full["events"][0]["content"], "review complete")
            self.assertEqual(full["command"][full["command"].index("-p") + 1], "[delegation prompt omitted]")
            self.assertNotIn("events", receipt)
            self.assertEqual([item.name for item in root.iterdir()], ["fake_copilot.py"])

    def test_delegation_preserves_final_message_after_large_tool_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            fake_copilot = root / "fake_copilot.py"
            fake_copilot.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                "print(json.dumps({'type': 'tool.execution_complete', 'content': 'x' * 70000, 'detailedContent': 'y' * 70000}))\n"
                "print(json.dumps({'type': 'assistant.message', 'data': {'content': 'Windows review complete', 'encryptedContent': 'z' * 50000, 'reasoningOpaque': 'z' * 50000, 'reasoningBlocks': ['opaque'], 'toolRequests': []}}))\n"
                "print(json.dumps({'type': 'result', 'data': {'sessionId': 'sanitized-session'}}))\n"
            )
            fake_copilot.chmod(fake_copilot.stat().st_mode | stat.S_IXUSR)
            old_binary = os.environ.get("FEDERATED_BROKER_COPILOT_BIN")
            os.environ["FEDERATED_BROKER_COPILOT_BIN"] = f"{sys.executable} {fake_copilot}"
            try:
                request = broker.parse_request(
                    "review", {"task": "Review Windows compatibility", "workspace": temporary_directory}
                )
                receipt = broker.run_delegation(request)
            finally:
                if old_binary is None:
                    del os.environ["FEDERATED_BROKER_COPILOT_BIN"]
                else:
                    os.environ["FEDERATED_BROKER_COPILOT_BIN"] = old_binary
            self.assertEqual(receipt["status"], "completed")
            self.assertTrue(receipt["outputCompacted"])
            self.assertTrue(receipt["finalResponseAvailable"])
            self.assertEqual(receipt["finalResponse"], "Windows review complete")
            full = broker.broker_receipt(receipt["requestId"])
            self.assertEqual(full["events"][1]["data"]["content"], "Windows review complete")
            self.assertNotIn("encryptedContent", full["events"][1]["data"])
            self.assertEqual(full["sessionId"], "sanitized-session")
            self.assertTrue(full["sessionLogPath"].endswith("sanitized-session/events.jsonl"))
            tool_event = full["events"][0]
            self.assertEqual(tool_event["content"], "[omitted by broker]")
            self.assertEqual(tool_event["detailedContent"], "[omitted by broker]")

    def test_nested_assistant_fixture_survives_streaming_capture(self) -> None:
        fixture = Path(__file__).parent / "fixtures" / "copilot-cli-assistant-message.jsonl"
        capture: dict[str, object] = {
            "buffer": bytearray(),
            "truncated": False,
            "events": [],
            "event_bytes": 0,
        }
        broker._drain_copilot_jsonl(BytesIO(fixture.read_bytes()), capture, broker.MAX_CAPTURED_OUTPUT_CHARS)
        events = [item[0] for item in capture["events"]]
        self.assertEqual(broker._final_assistant_response(events), "Nested Copilot review text")
        message = events[0]
        self.assertEqual(message["data"]["content"], "Nested Copilot review text")
        self.assertNotIn("encryptedContent", message["data"])
        self.assertNotIn("reasoningOpaque", message["data"])
        self.assertNotIn("reasoningBlocks", message["data"])
        self.assertNotIn("toolRequests", message["data"])

    def test_missing_final_response_is_not_reported_as_completed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            fake_copilot = root / "fake_copilot.py"
            fake_copilot.write_text(
                "#!/usr/bin/env python3\n"
                "import json\n"
                "print(json.dumps({'type': 'assistant.message', 'data': {'reasoningOpaque': 'opaque'}}))\n"
            )
            fake_copilot.chmod(fake_copilot.stat().st_mode | stat.S_IXUSR)
            old_binary = os.environ.get("FEDERATED_BROKER_COPILOT_BIN")
            os.environ["FEDERATED_BROKER_COPILOT_BIN"] = f"{sys.executable} {fake_copilot}"
            try:
                request = broker.parse_request(
                    "review", {"task": "Review this code", "workspace": temporary_directory}
                )
                receipt = broker.run_delegation(request)
            finally:
                if old_binary is None:
                    del os.environ["FEDERATED_BROKER_COPILOT_BIN"]
                else:
                    os.environ["FEDERATED_BROKER_COPILOT_BIN"] = old_binary
            self.assertEqual(receipt["status"], "completed_no_response")
            self.assertFalse(receipt["finalResponseAvailable"])
            self.assertTrue(any("Do not retry automatically" in item for item in receipt["limitations"]))

    def test_review_diff_includes_staged_and_unstaged_tracked_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            request = broker.parse_request(
                "review", {"task": "Review this diff", "workspace": temporary_directory}
            )
            result = broker.ProcessResult(0, "diff --git a/a b/a\n", "", False, False, False)
            with patch.object(broker, "_run_bounded_process", return_value=result) as run_process:
                broker._read_working_diff(request)
            self.assertIn("HEAD", run_process.call_args.args[0])

    def test_bounded_process_output_does_not_exceed_its_receipt_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            producer = Path(temporary_directory, "producer.py")
            producer.write_text("import sys\nsys.stdout.write('x' * 10000)\n")
            result = broker._run_bounded_process(
                [sys.executable, str(producer)], Path(temporary_directory), 15, 100
            )
            self.assertEqual(result.exit_code, 0)
            self.assertTrue(result.stdout_truncated)
            self.assertLessEqual(len(result.stdout.encode()), 100)

    def test_status_reports_malformed_copilot_command_without_crashing(self) -> None:
        old_binary = os.environ.get("FEDERATED_BROKER_COPILOT_BIN")
        os.environ["FEDERATED_BROKER_COPILOT_BIN"] = "'"
        try:
            status = broker.broker_status()
        finally:
            if old_binary is None:
                del os.environ["FEDERATED_BROKER_COPILOT_BIN"]
            else:
                os.environ["FEDERATED_BROKER_COPILOT_BIN"] = old_binary
        self.assertEqual(status["copilotCommand"], [])
        self.assertIn("not valid shell syntax", status["error"])

    def test_initialize_rejects_an_unsupported_protocol_version(self) -> None:
        response = broker.McpServer().handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2099-01-01"},
            }
        )
        assert response is not None
        self.assertEqual(response["error"]["code"], -32602)

    def test_task_class_schema_and_validation(self) -> None:
        tools = broker.tool_definitions()
        for tool in tools[:3]:
            self.assertEqual(tool["inputSchema"]["properties"]["task_class"]["enum"], list(broker.TASK_CLASSES))
        with tempfile.TemporaryDirectory() as workspace:
            with self.assertRaisesRegex(broker.BrokerError, "task_class must be one of"):
                broker.parse_request("research", {"task": "Inspect", "workspace": workspace, "task_class": "pr-review"})

    def test_execution_surfaces_are_rejected_before_spawn(self) -> None:
        paths = [
            ".git/hooks/pre-commit", ".GIT/hooks/x", ".claude/settings.json", ".Claude/settings.json",
            ".opencode/config", ".codex/config", ".github/workflows/ci.yml", ".GitHub/Workflows/ci.yml",
            "nested/.github/workflows/ci.yml",
            ".vscode/tasks.json", ".idea/workspace.xml", ".devcontainer/devcontainer.json", ".husky/pre-commit",
            ".envrc", ".env", ".npmrc", ".pypirc", ".gitmodules", ".gitattributes",
            ".pre-commit-config.yaml", "opencode.json", "AGENTS.md", "CLAUDE.md",
        ]
        with tempfile.TemporaryDirectory() as workspace:
            for path in paths:
                with self.subTest(path=path), self.assertRaisesRegex(broker.BrokerError, "execution surface"):
                    broker.parse_request("implement", {"task": "Change", "workspace": workspace, "writable_paths": [path]})

    def test_workspace_root_home_and_allowed_roots(self) -> None:
        for mode in ("research", "review", "implement"):
            extra = {"writable_paths": ["safe.txt"]} if mode == "implement" else {}
            for workspace in ("/", "~"):
                with self.subTest(mode=mode, workspace=workspace), self.assertRaisesRegex(broker.BrokerError, "root or home"):
                    broker.parse_request(mode, {"task": "Check", "workspace": workspace, **extra})
        with tempfile.TemporaryDirectory() as root:
            allowed = Path(root, "allowed")
            outside = Path(root, "outside")
            allowed.mkdir()
            outside.mkdir()
            with patch.dict(os.environ, {"FEDERATED_BROKER_ALLOWED_ROOTS": str(allowed)}):
                with self.assertRaisesRegex(broker.BrokerError, "outside FEDERATED"):
                    broker.parse_request("research", {"task": "Check", "workspace": str(outside)})
                self.assertEqual(broker.parse_request("research", {"task": "Check", "workspace": str(allowed)}).workspace, allowed.resolve())

    def test_receipt_id_rejected_before_filesystem_access_and_retention(self) -> None:
        with patch.object(broker, "_state_directory", side_effect=AssertionError("filesystem touched")):
            for request_id in ("../x", "/tmp/x", "del_ABCDEF0123456789"):
                with self.assertRaises(broker.BrokerError):
                    broker.broker_receipt(request_id)
        with patch.dict(os.environ, {"FEDERATED_BROKER_RECEIPT_KEEP": "2"}):
            for index in range(3):
                broker._write_full_receipt({"requestId": f"del_{index:016x}", "events": [index]})
            self.assertEqual(len(list((Path(self.state.name) / "receipts").glob("*.json"))), 2)
            self.assertEqual((Path(self.state.name) / "receipts").stat().st_mode & 0o777, 0o700)
            with self.assertRaisesRegex(broker.BrokerError, "receipt expired"):
                broker.broker_receipt("del_0000000000000000")

    def test_usage_log_terminal_statuses_and_no_validation_record(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            request = broker.parse_request("research", {"task": "Inspect", "workspace": workspace,
                                                         "task_class": "codebase-research"})
            results = [
                broker.ProcessResult(0, '', '', False, False, False,
                                     ({"type": "assistant.message", "content": "done"},)),
                broker.ProcessResult(0, '', '', False, False, False),
                broker.ProcessResult(1, '', '', False, False, False),
                broker.ProcessResult(-15, '', '', True, False, False),
                broker.ProcessResult(-15, '', '', False, False, False, termination="cancelled"),
                broker.ProcessResult(-15, '', '', False, False, False, termination="interrupted"),
            ]
            with patch.object(broker, "_run_bounded_process", side_effect=results), patch.object(
                broker, "_provider_version", return_value="1.0.87-0"
            ), patch.dict(os.environ, {"FEDERATED_BROKER_HOST": "claude-code",
                                       "FEDERATED_BROKER_ACCOUNT_LABEL": "personal-copilot"}):
                receipts = [broker.run_delegation(request) for _ in results]
            self.assertEqual([item["status"] for item in receipts],
                             ["completed", "completed_no_response", "failed", "timed_out", "cancelled", "interrupted"])
            self.assertTrue(all(item["limitations"][0] == broker.UNTRUSTED_LIMITATION for item in receipts))
            lines = (Path(self.state.name) / "delegations.jsonl").read_text().splitlines()
            self.assertEqual(len(lines), 6)
            record = json.loads(lines[0])
            self.assertEqual(record["taskClass"], "codebase-research")
            self.assertIsNone(record["usageObserved"])
            self.assertEqual(record["providerVersion"], "1.0.87-0")
            self.assertEqual(record["host"], "claude-code")
            self.assertEqual(record["accountLabel"], "personal-copilot")
            self.assertFalse(any(key in record for key in ("task", "finalResponse", "events", "stderr")))
            with self.assertRaises(broker.BrokerError):
                broker.parse_request("research", {"task": "", "workspace": workspace})
            self.assertEqual(len((Path(self.state.name) / "delegations.jsonl").read_text().splitlines()), 6)
            self.assertEqual((Path(self.state.name) / "delegations.jsonl").stat().st_mode & 0o777, 0o600)
            with patch.dict(os.environ, {"FEDERATED_BROKER_ACCOUNT_LABEL": "personal-copilot"}):
                self.assertEqual(broker.broker_status()["accountLabel"], "personal-copilot")

    def test_lean_receipt_bounds_serialized_code_and_preserves_full_detail(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            request = broker.parse_request("research", {"task": "Inspect", "workspace": workspace})
            answer = ('"\\n\n' * 4000)[:16000]
            result = broker.ProcessResult(0, '', '', False, False, False,
                                          ({"type": "assistant.message", "content": answer},))
            with patch.object(broker, "_run_bounded_process", return_value=result):
                lean = broker.run_delegation(request)
            self.assertLessEqual(len(json.dumps(lean, ensure_ascii=False, indent=2)), broker.MAX_LEAN_RECEIPT_CHARS)
            self.assertTrue(lean["finalResponseTruncated"])
            self.assertEqual(broker.broker_receipt(lean["requestId"])["finalResponse"], answer)
            self.assertEqual(lean["untrustedContent"], ["finalResponse", "assumptions", "openQuestions"])
            self.assertEqual(lean["limitations"][0], broker.UNTRUSTED_LIMITATION)

    def test_receipt_persistence_failure_preserves_result(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            request = broker.parse_request("research", {"task": "Inspect", "workspace": workspace})
            result = broker.ProcessResult(0, '', '', False, False, False,
                                          ({"type": "assistant.message", "content": "answer"},))
            with patch.object(broker, "_run_bounded_process", return_value=result), patch.object(
                broker, "_write_full_receipt", side_effect=OSError("unwritable")
            ):
                lean = broker.run_delegation(request)
            self.assertEqual(lean["status"], "completed")
            self.assertFalse(lean["detailAvailable"])
            self.assertTrue(any("unwritable" in item for item in lean["limitations"]))
            self.assertEqual(len((Path(self.state.name) / "delegations.jsonl").read_text().splitlines()), 1)

    def test_usage_log_failure_preserves_result(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            request = broker.parse_request("research", {"task": "Inspect", "workspace": workspace})
            result = broker.ProcessResult(0, '', '', False, False, False,
                                          ({"type": "assistant.message", "content": "answer"},))
            with patch.object(broker, "_run_bounded_process", return_value=result), patch.object(
                broker, "_append_usage_log", side_effect=OSError("log unwritable")
            ):
                lean = broker.run_delegation(request)
            self.assertEqual(lean["status"], "completed")
            self.assertTrue(any("log unwritable" in item for item in lean["limitations"]))

    def test_lean_receipt_bounds_large_change_lists(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            request = broker.parse_request("research", {"task": "Inspect", "workspace": workspace})
            result = broker.ProcessResult(0, '', '', False, False, False,
                                          ({"type": "assistant.message", "content": "answer"},))
            with patch.object(broker, "_run_bounded_process", return_value=result):
                lean = broker.run_delegation(request)
            full = broker.broker_receipt(lean["requestId"])
            full["undeclaredChanges"] = [{"path": f"file-{index}-" + "x" * 300,
                                           "before": None, "after": "??"} for index in range(200)]
            full["limitations"].append("x" * 50000)
            bounded = broker._lean_receipt(full)
            self.assertLessEqual(len(json.dumps(bounded, ensure_ascii=False, indent=2)), broker.MAX_LEAN_RECEIPT_CHARS)
            self.assertTrue(bounded["receiptFieldsTruncated"])

    def test_hash_changes_and_non_git_limit(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            Path(workspace, "one.txt").write_text("before")
            Path(workspace, "two.txt").write_text("same")
            Path(workspace, "three.txt").write_text("same")
            worker = Path(self.state.name, "worker.py")
            worker.write_text("import sys\nfrom pathlib import Path\nif '--version' in sys.argv:\n    print('fake 1.0')\n    sys.exit(0)\nPath('one.txt').write_text('after')\nprint('''{\"type\":\"assistant.message\",\"content\":\"done\"}''')\n")
            request = broker.parse_request("implement", {"task": "Edit", "workspace": workspace,
                                                         "writable_paths": ["one.txt", "two.txt", "three.txt"]})
            with patch.dict(os.environ, {"FEDERATED_BROKER_COPILOT_BIN": f"{sys.executable} {worker}"}):
                lean = broker.run_delegation(request)
            self.assertEqual([item["change"] for item in lean["filesChanged"]], ["modified", "unchanged", "unchanged"])
            self.assertIsNone(lean["undeclaredChanges"])
            self.assertTrue(any("not a Git repository" in item for item in lean["limitations"]))

    def test_undeclared_write_is_error_and_logged(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            subprocess.run(["git", "init", "-q", workspace], check=True)
            worker = Path(self.state.name, "worker.py")
            worker.write_text("import sys\nfrom pathlib import Path\nif '--version' in sys.argv:\n    print('fake 1.0')\n    sys.exit(0)\nPath('leak.txt').write_text('x')\nprint('''{\"type\":\"assistant.message\",\"content\":\"done\"}''')\n")
            request = {"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {
                "name": "copilot_implement", "arguments": {"task": "Edit", "workspace": workspace,
                "writable_paths": ["allowed.txt"]}}}
            with patch.dict(os.environ, {"FEDERATED_BROKER_COPILOT_BIN": f"{sys.executable} {worker}"}):
                response = broker.McpServer().handle_request(request)
            assert response is not None
            self.assertTrue(response["result"]["isError"])
            lean = json.loads(response["result"]["content"][0]["text"])
            self.assertEqual(lean["undeclaredChanges"][0]["path"], "leak.txt")
            log = json.loads((Path(self.state.name) / "delegations.jsonl").read_text().splitlines()[0])
            self.assertEqual(log["undeclaredChangesCount"], 1)

    def test_post_run_hash_failure_is_logged_once(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            request = broker.parse_request("implement", {"task": "Edit", "workspace": workspace,
                                                         "writable_paths": ["safe.txt"]})
            result = broker.ProcessResult(0, '', '', False, False, False)
            def fake_run(*args: object, **kwargs: object) -> broker.ProcessResult:
                kwargs["on_spawn"]()
                return result
            with patch.object(broker, "_path_state", side_effect=[{"safe.txt": None}, RuntimeError("hash failed")]), patch.object(
                broker, "_run_bounded_process", side_effect=fake_run
            ):
                lean = broker.run_delegation(request)
            self.assertEqual(lean["status"], "failed")
            self.assertTrue(any("RuntimeError" in item for item in lean["limitations"]))
            self.assertEqual(len((Path(self.state.name) / "delegations.jsonl").read_text().splitlines()), 1)

    def _start_long_running_server(self, workspace: str) -> tuple[subprocess.Popen[str], Path]:
        worker = Path(self.state.name, "sleep_worker.py")
        pid_file = Path(self.state.name, "worker.pid")
        worker.write_text(
            "import os, sys, time\n"
            "from pathlib import Path\n"
            "if '--version' in sys.argv:\n    print('fake 1.0')\n    sys.exit(0)\n"
            f"Path({str(pid_file)!r}).write_text(str(os.getpid()))\n"
            "time.sleep(60)\n"
        )
        environment = os.environ.copy()
        environment["FEDERATED_BROKER_COPILOT_BIN"] = f"{sys.executable} {worker}"
        process = subprocess.Popen(
            [sys.executable, str(Path(broker.__file__))], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=environment,
        )
        for stream in (process.stdin, process.stdout, process.stderr):
            if stream is not None:
                self.addCleanup(stream.close)
        assert process.stdin is not None
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 77, "method": "tools/call", "params": {
            "name": "copilot_research", "arguments": {"task": "Wait", "workspace": workspace}}}) + "\n")
        process.stdin.flush()
        deadline = time.monotonic() + 10
        while not pid_file.exists() and time.monotonic() < deadline:
            time.sleep(0.02)
        self.assertTrue(pid_file.exists(), "worker did not start")
        return process, pid_file

    def _wait_for_status(self, status: str) -> None:
        path = Path(self.state.name, "delegations.jsonl")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if path.exists() and any(json.loads(line)["status"] == status for line in path.read_text().splitlines()):
                return
            time.sleep(0.02)
        self.fail(f"no {status} usage line")

    def _assert_worker_gone(self, pid_file: Path) -> None:
        pid = int(pid_file.read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_cancel_kills_worker_logs_once_and_emits_no_response(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            process, pid_file = self._start_long_running_server(workspace)
            assert process.stdin is not None and process.stdout is not None
            process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/cancelled",
                                            "params": {"requestId": 77}}) + "\n")
            process.stdin.flush()
            self._wait_for_status("cancelled")
            process.stdin.close()
            process.wait(timeout=10)
            self.assertNotIn('"id": 77', process.stdout.read())
            self._assert_worker_gone(pid_file)
            self.assertEqual(len(Path(self.state.name, "delegations.jsonl").read_text().splitlines()), 1)

    def test_sigterm_kills_worker_and_logs_interrupted(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            process, pid_file = self._start_long_running_server(workspace)
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=10)
            self._wait_for_status("interrupted")
            self._assert_worker_gone(pid_file)
            self.assertEqual(len(Path(self.state.name, "delegations.jsonl").read_text().splitlines()), 1)

    def test_stdin_eof_kills_worker_and_status_waits_for_delegation(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            process, pid_file = self._start_long_running_server(workspace)
            assert process.stdin is not None and process.stdout is not None
            process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": 78, "method": "tools/call",
                                            "params": {"name": "broker_status", "arguments": {}}}) + "\n")
            process.stdin.flush()
            readable, _, _ = select.select([process.stdout], [], [], 0.2)
            self.assertFalse(readable, "single-worker server answered while delegation was in flight")
            process.stdin.close()
            process.wait(timeout=10)
            self._wait_for_status("interrupted")
            self._assert_worker_gone(pid_file)

    def test_unexpected_exception_gets_one_json_rpc_error(self) -> None:
        import io
        with tempfile.TemporaryDirectory() as workspace:
            request = {"jsonrpc": "2.0", "id": 91, "method": "tools/call", "params": {
                "name": "copilot_research", "arguments": {"task": "Inspect", "workspace": workspace}}}
            output = io.StringIO()
            with patch.object(broker, "run_delegation", side_effect=RuntimeError("broken")), patch.object(
                sys, "stdin", io.StringIO(json.dumps(request) + "\n")
            ), patch.object(sys, "stdout", output), patch.object(sys, "stderr", io.StringIO()):
                broker.serve()
            messages = [json.loads(line) for line in output.getvalue().splitlines()]
            self.assertEqual(len(messages), 1)
            self.assertEqual(messages[0]["id"], 91)
            self.assertEqual(messages[0]["error"]["code"], -32603)
            self.assertIn("RuntimeError", messages[0]["error"]["message"])


if __name__ == "__main__":
    unittest.main()

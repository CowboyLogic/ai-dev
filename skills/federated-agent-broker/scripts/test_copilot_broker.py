#!/usr/bin/env python3
"""Focused unit tests for the dependency-free Copilot MCP broker."""

from __future__ import annotations

import json
from io import BytesIO
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
import copilot_broker as broker  # noqa: E402


class CopilotBrokerTests(unittest.TestCase):
    def test_tools_list_exposes_the_bounded_surface(self) -> None:
        result = broker.McpServer().handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
        )
        assert result is not None
        self.assertEqual(
            [tool["name"] for tool in result["result"]["tools"]],
            ["copilot_research", "copilot_review", "copilot_implement", "broker_status"],
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
            self.assertEqual(receipt["events"][0]["content"], "review complete")
            self.assertEqual(receipt["command"][receipt["command"].index("-p") + 1], "[delegation prompt omitted]")

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
            self.assertEqual(receipt["events"][1]["data"]["content"], "Windows review complete")
            self.assertNotIn("encryptedContent", receipt["events"][1]["data"])
            self.assertEqual(receipt["sessionId"], "sanitized-session")
            self.assertTrue(receipt["sessionLogPath"].endswith("sanitized-session/events.jsonl"))
            tool_event = receipt["events"][0]
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


if __name__ == "__main__":
    unittest.main()

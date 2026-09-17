#!/usr/bin/env python3
"""Focused unit tests for the dependency-free Copilot MCP broker."""

from __future__ import annotations

import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest

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

    def test_research_uses_read_only_copilot_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            request = broker.parse_request(
                "research", {"task": "Explain this repository", "workspace": temporary_directory}
            )
            command = broker._copilot_base_command(request, broker.build_prompt(request))
            self.assertIn("--available-tools", command)
            self.assertIn("read", command)
            self.assertNotIn("write", command)
            self.assertNotIn("shell", command)

    def test_implementation_passes_exact_write_and_shell_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            request = broker.parse_request(
                "implement",
                {
                    "task": "Update the focused test",
                    "workspace": temporary_directory,
                    "writable_paths": ["tests/test_broker.py"],
                    "allowed_commands": ["python -m pytest"],
                },
            )
            command = broker._copilot_base_command(request, broker.build_prompt(request))
            permissions = command[command.index("--allow-tool") + 1]
            self.assertEqual(
                permissions,
                "read,write(tests/test_broker.py),shell(python -m pytest)",
            )

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


if __name__ == "__main__":
    unittest.main()

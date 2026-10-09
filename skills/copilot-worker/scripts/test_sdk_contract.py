#!/usr/bin/env python3
"""Contract tests: the SDK and runtime in use are the pinned ones, and the SDK still
offers every name the engine calls. They cost no credits and start no worker.

They need the SDK installed, so run them in the environment the script header pins
(references/upgrading.md gives the command). Without the SDK they skip, unless
REQUIRE_SDK_CONTRACT is set, which CI sets so that a missing SDK fails the run.
"""

from __future__ import annotations

import dataclasses
from importlib.metadata import PackageNotFoundError, requires, version
import inspect
import os
from pathlib import Path
import re
import sys
import typing
import unittest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import worker_engine as engine  # noqa: E402

try:
    import copilot
    import copilot.generated.session_events as events
    import copilot.rpc as rpc
except ImportError:
    if os.environ.get("REQUIRE_SDK_CONTRACT"):
        raise
    copilot = None

SAMPLE_CONFIG = {
    "mode": "implement", "model": "model", "workspace": "/workspace", "credits": 30,
    "effort": "high", "copilotHome": "/copilot-home", "timeout": 600,
}


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _header_pins() -> dict[str, str]:
    header = (HERE / "copilot_worker.py").read_text(encoding="utf-8").split("# ///", 2)[1]
    pins = {}
    for requirement in re.findall(r'^#\s+"([^"]+)",?$', header, re.MULTILINE):
        name, _, pinned = requirement.partition("==")
        pins[_normalize(name)] = pinned
    return pins


def _parameters(callable_: object) -> set[str]:
    return set(inspect.signature(callable_).parameters)


@unittest.skipIf(copilot is None, "github-copilot-sdk is not installed")
class SdkContractTests(unittest.TestCase):
    def test_installed_sdk_and_runtime_are_the_pinned_ones(self) -> None:
        self.assertIsNone(engine.pin_problem(engine.versions(), engine.load_pins()))

    def test_script_header_pins_every_package_the_sdk_pulls_in(self) -> None:
        pins = _header_pins()
        seen: set[str] = set()
        pending = ["github-copilot-sdk"]
        while pending:
            name = _normalize(pending.pop())
            if name in seen:
                continue
            seen.add(name)
            self.assertIn(name, pins, f"{name} is installed with the SDK but not pinned in the header")
            self.assertEqual(version(name), pins[name], f"{name} differs from its header pin")
            for requirement in requires(name) or []:
                if "extra ==" in requirement:
                    continue
                dependency = re.match(r"[A-Za-z0-9._-]+", requirement).group(0)
                try:
                    version(dependency)
                except PackageNotFoundError:
                    continue  # excluded by an environment marker on this interpreter
                pending.append(dependency)

    def test_client_accepts_every_option_the_engine_passes(self) -> None:
        options = engine.client_options(SAMPLE_CONFIG, {})
        self.assertLessEqual(set(options), _parameters(copilot.CopilotClient.__init__))

    def test_create_session_accepts_every_option_the_engine_passes(self) -> None:
        kwargs = engine.session_kwargs(SAMPLE_CONFIG, lambda *_: None, lambda *_: None, object())
        self.assertLessEqual(set(kwargs), _parameters(copilot.CopilotClient.create_session))

    def test_session_limits_use_a_field_the_sdk_defines(self) -> None:
        limits = engine.session_options(SAMPLE_CONFIG)["session_limits"]
        config_type = typing.get_type_hints(copilot.CopilotClient.create_session)["session_limits"]
        limit_type = next(arg for arg in typing.get_args(config_type) if arg is not type(None))
        fields = (
            {field.name for field in dataclasses.fields(limit_type)}
            if dataclasses.is_dataclass(limit_type) else set(typing.get_type_hints(limit_type))
        )
        self.assertLessEqual(set(limits), fields)

    def test_send_and_wait_accepts_the_timeout_the_engine_passes(self) -> None:
        self.assertLessEqual(set(engine.send_options(SAMPLE_CONFIG)), _parameters(copilot.CopilotSession.send_and_wait))

    def test_toolset_still_adds_builtin_tools(self) -> None:
        for windows in (False, True):
            tools = copilot.ToolSet()
            for name in engine.tools_for(windows)["implement"]:
                tools.add_builtin(name)

    def test_permission_decisions_the_engine_returns_still_construct(self) -> None:
        rpc.PermissionDecisionApproveOnce()
        rpc.PermissionDecisionReject(feedback="reason")

    def test_permission_request_classes_map_to_the_kinds_the_policy_decides(self) -> None:
        expected = {"PermissionRequestShell": "shell", "PermissionRequestRead": "read", "PermissionRequestWrite": "write"}
        for class_name, kind in expected.items():
            request = object.__new__(getattr(events, class_name))
            self.assertEqual(engine.request_kind(request), kind)

    def test_permission_requests_still_carry_the_fields_the_engine_reads(self) -> None:
        def names(class_name: str) -> set[str]:
            return {field.name for field in dataclasses.fields(getattr(events, class_name))}

        self.assertLessEqual({"full_command_text", "command_segments", "commands"}, names("PermissionRequestShell"))
        self.assertIn("identifier", names("PermissionRequestShellCommand"))
        self.assertLessEqual({"full_command_text", "identifier"}, names("PermissionRequestShellCommandSegment"))
        self.assertTrue({"resolved_path", "path"} & names("PermissionRequestRead"))
        self.assertTrue({"resolved_path", "file_name"} & names("PermissionRequestWrite"))

    def test_events_still_carry_the_fields_usage_and_the_response_come_from(self) -> None:
        def names(class_name: str) -> set[str]:
            return {field.name for field in dataclasses.fields(getattr(events, class_name))}

        self.assertLessEqual(
            {"model", "input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens", "copilot_usage"},
            names("AssistantUsageData"),
        )
        self.assertIn("total_nano_aiu", names("AssistantUsageCopilotUsage"))
        self.assertIn("content", names("AssistantMessageData"))


if __name__ == "__main__":
    unittest.main()

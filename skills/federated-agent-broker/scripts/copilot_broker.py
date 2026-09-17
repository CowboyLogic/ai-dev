#!/usr/bin/env python3
"""Expose GitHub Copilot CLI as bounded local MCP tools.

The server deliberately uses only Python's standard library. It speaks MCP's
stdio JSON-RPC transport and starts Copilot only after a client calls a tool.
All diagnostic output goes to stderr; stdout is reserved for protocol messages.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator


SERVER_NAME = "federated-agent-broker"
SERVER_VERSION = "0.1.0"
DEFAULT_TIMEOUT_SECONDS = 300
DEFAULT_MAX_AI_CREDITS = 1
MAX_TASK_CHARS = 12_000
MAX_CAPTURED_OUTPUT_CHARS = 60_000
MAX_DIFF_CHARS = 40_000
SUPPORTED_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max"}
SUPPORTED_CONTEXTS = {"default", "long_context"}
MODEL_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
SAFE_COMMANDS = {
    "cargo test",
    "git diff --check",
    "git status --short",
    "go test ./...",
    "npm run test",
    "npm test",
    "pnpm test",
    "pytest",
    "python -m pytest",
    "uv run pytest",
    "yarn test",
}


class BrokerError(ValueError):
    """An invalid or disallowed broker request."""


@dataclass(frozen=True)
class DelegationRequest:
    mode: str
    task: str
    workspace: Path
    paths: tuple[str, ...]
    writable_paths: tuple[str, ...]
    allowed_commands: tuple[str, ...]
    profile: str
    model: str
    effort: str
    context: str
    max_ai_credits: int
    timeout_seconds: int
    include_working_diff: bool


@dataclass(frozen=True)
class Profile:
    """A named, user-controlled Copilot execution policy."""

    name: str
    model: str
    effort: str
    context: str
    max_ai_credits: int
    timeout_seconds: int


@dataclass(frozen=True)
class BrokerPolicy:
    source: str
    default_profile: str
    mode_profiles: dict[str, str]
    profiles: dict[str, Profile]


def _tool_schema(
    description: str, properties: dict[str, Any], required: list[str]
) -> dict[str, Any]:
    return {
        "name": "",
        "description": description,
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": properties,
            "required": required,
        },
    }


COMMON_PROPERTIES: dict[str, Any] = {
    "task": {
        "type": "string",
        "description": "Concrete delegation objective, acceptance criteria, and questions to answer.",
        "minLength": 1,
        "maxLength": MAX_TASK_CHARS,
    },
    "workspace": {
        "type": "string",
        "description": "Absolute workspace directory. Defaults to CLAUDE_PROJECT_DIR when omitted.",
    },
    "paths": {
        "type": "array",
        "description": "Relative paths that define the delegation scope.",
        "items": {"type": "string"},
        "maxItems": 50,
    },
    "model": {
        "type": "string",
        "description": "Copilot model name. Defaults to auto or FEDERATED_BROKER_COPILOT_MODEL.",
    },
    "effort": {
        "type": "string",
        "enum": sorted(SUPPORTED_EFFORTS),
        "description": "Copilot reasoning effort. Defaults to low for research/review and medium for implementation.",
    },
    "context": {
        "type": "string",
        "enum": sorted(SUPPORTED_CONTEXTS),
        "description": "Copilot context tier. Defaults to the selected delegation profile.",
    },
    "max_ai_credits": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "description": "Maximum Copilot AI credits for this delegation. Defaults to 1.",
    },
    "timeout_seconds": {
        "type": "integer",
        "minimum": 15,
        "maximum": 900,
        "description": "Maximum time to wait for Copilot. Defaults to 300 seconds.",
    },
}


def _validated_model(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise BrokerError(f"{field} must be a string")
    model = value.strip()
    if not model or model.startswith("-") or len(model) > 120 or not MODEL_PATTERN.fullmatch(model):
        raise BrokerError(f"{field} must contain only letters, numbers, periods, underscores, or hyphens")
    return model


def _validated_int(value: Any, field: str, minimum: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise BrokerError(f"{field} must be an integer from {minimum} through {maximum}")
    return value


def _profile_from_mapping(name: str, value: Any) -> Profile:
    if not isinstance(name, str) or not MODEL_PATTERN.fullmatch(name) or name.startswith("-"):
        raise BrokerError("profile names must contain only letters, numbers, periods, underscores, or hyphens")
    if not isinstance(value, dict):
        raise BrokerError(f"profiles.{name} must be an object")
    expected = {"model", "effort", "context", "maxAiCredits", "timeoutSeconds"}
    unexpected = set(value) - expected
    missing = expected - set(value)
    if unexpected or missing:
        details = []
        if missing:
            details.append(f"missing {', '.join(sorted(missing))}")
        if unexpected:
            details.append(f"unknown {', '.join(sorted(unexpected))}")
        raise BrokerError(f"profiles.{name} has {'; '.join(details)} field(s)")
    effort = value["effort"]
    if effort not in SUPPORTED_EFFORTS:
        raise BrokerError(f"profiles.{name}.effort must be one of: {', '.join(sorted(SUPPORTED_EFFORTS))}")
    context = value["context"]
    if context not in SUPPORTED_CONTEXTS:
        raise BrokerError(f"profiles.{name}.context must be one of: {', '.join(sorted(SUPPORTED_CONTEXTS))}")
    return Profile(
        name=name,
        model=_validated_model(value["model"], f"profiles.{name}.model"),
        effort=effort,
        context=context,
        max_ai_credits=_validated_int(value["maxAiCredits"], f"profiles.{name}.maxAiCredits", 1, 100),
        timeout_seconds=_validated_int(value["timeoutSeconds"], f"profiles.{name}.timeoutSeconds", 15, 900),
    )


def _built_in_policy() -> BrokerPolicy:
    model = _validated_model(os.environ.get("FEDERATED_BROKER_COPILOT_MODEL", "auto"), "FEDERATED_BROKER_COPILOT_MODEL")
    profiles = {
        "research": Profile("research", model, "low", "default", 1, DEFAULT_TIMEOUT_SECONDS),
        "review": Profile("review", model, "low", "default", 1, DEFAULT_TIMEOUT_SECONDS),
        "implementation": Profile("implementation", model, "medium", "default", 1, DEFAULT_TIMEOUT_SECONDS),
    }
    return BrokerPolicy(
        source="built-in defaults",
        default_profile="research",
        mode_profiles={"research": "research", "review": "review", "implement": "implementation"},
        profiles=profiles,
    )


def load_policy() -> BrokerPolicy:
    """Load an optional user policy without persisting credentials or task data."""
    configured_path = os.environ.get("FEDERATED_BROKER_POLICY", "").strip()
    if not configured_path:
        return _built_in_policy()
    path = Path(configured_path).expanduser().resolve()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise BrokerError(f"could not read FEDERATED_BROKER_POLICY at {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise BrokerError(f"FEDERATED_BROKER_POLICY is not valid JSON: {error.msg}") from error
    if not isinstance(data, dict):
        raise BrokerError("FEDERATED_BROKER_POLICY must contain a JSON object")
    expected = {"defaultProfile", "modeProfiles", "profiles"}
    unexpected = set(data) - expected
    missing = expected - set(data)
    if unexpected or missing:
        details = []
        if missing:
            details.append(f"missing {', '.join(sorted(missing))}")
        if unexpected:
            details.append(f"unknown {', '.join(sorted(unexpected))}")
        raise BrokerError(f"FEDERATED_BROKER_POLICY has {'; '.join(details)} field(s)")
    profiles_data = data["profiles"]
    if not isinstance(profiles_data, dict) or not profiles_data:
        raise BrokerError("FEDERATED_BROKER_POLICY.profiles must be a non-empty object")
    profiles = {name: _profile_from_mapping(name, value) for name, value in profiles_data.items()}
    default_profile = data["defaultProfile"]
    if not isinstance(default_profile, str) or default_profile not in profiles:
        raise BrokerError("FEDERATED_BROKER_POLICY.defaultProfile must name a configured profile")
    mode_profiles = data["modeProfiles"]
    if not isinstance(mode_profiles, dict) or set(mode_profiles) != {"research", "review", "implement"}:
        raise BrokerError("FEDERATED_BROKER_POLICY.modeProfiles must define research, review, and implement")
    if not all(isinstance(profile, str) and profile in profiles for profile in mode_profiles.values()):
        raise BrokerError("FEDERATED_BROKER_POLICY.modeProfiles must reference configured profiles")
    return BrokerPolicy(
        source=str(path),
        default_profile=default_profile,
        mode_profiles=dict(mode_profiles),
        profiles=profiles,
    )


def _common_properties(policy: BrokerPolicy | None) -> dict[str, Any]:
    profile_names = sorted(policy.profiles) if policy else []
    profile_description = "Named Copilot execution profile. Defaults to the configured mode profile."
    if profile_names:
        profile_description += f" Available profiles: {', '.join(profile_names)}."
    profile = {"type": "string", "description": profile_description}
    if profile_names:
        profile["enum"] = profile_names
    return {**COMMON_PROPERTIES, "profile": profile}


def tool_definitions() -> list[dict[str, Any]]:
    try:
        policy = load_policy()
    except BrokerError:
        policy = None
    common_properties = _common_properties(policy)
    research = _tool_schema(
        "Ask Copilot for read-only codebase research, diagnosis, or an independent opinion.",
        common_properties,
        ["task"],
    )
    research["name"] = "copilot_research"

    review_properties = {
        **common_properties,
        "include_working_diff": {
            "type": "boolean",
            "default": True,
            "description": "Attach a bounded git diff from the workspace for Copilot to review.",
        },
    }
    review = _tool_schema(
        "Ask Copilot for a read-only review of a Git diff, files, plan, or proposed change.",
        review_properties,
        ["task"],
    )
    review["name"] = "copilot_review"

    implementation_properties = {
        **common_properties,
        "writable_paths": {
            "type": "array",
            "description": "Exact relative files Copilot may create or modify. Directories and globs are rejected.",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 25,
        },
        "allowed_commands": {
            "type": "array",
            "description": "Optional verification commands from the broker's allowlist.",
            "items": {"type": "string", "enum": sorted(SAFE_COMMANDS)},
            "uniqueItems": True,
        },
    }
    implementation = _tool_schema(
        "Delegate a bounded implementation to Copilot. Requires exact writable files and locks the workspace for the run.",
        implementation_properties,
        ["task", "writable_paths"],
    )
    implementation["name"] = "copilot_implement"

    status = _tool_schema(
        "Report broker policy and whether the configured Copilot executable is available. It does not call a model.",
        {},
        [],
    )
    status["name"] = "broker_status"
    return [research, review, implementation, status]


def _as_string(arguments: dict[str, Any], key: str, default: str = "") -> str:
    value = arguments.get(key, default)
    if not isinstance(value, str):
        raise BrokerError(f"{key} must be a string")
    return value


def _relative_paths(value: Any, key: str, *, required: bool = False) -> tuple[str, ...]:
    if value is None:
        values: list[Any] = []
    elif isinstance(value, list):
        values = value
    else:
        raise BrokerError(f"{key} must be an array")
    if required and not values:
        raise BrokerError(f"{key} must include at least one path")
    if len(values) > 50:
        raise BrokerError(f"{key} may include at most 50 paths")

    result: list[str] = []
    for raw in values:
        if not isinstance(raw, str) or not raw.strip():
            raise BrokerError(f"{key} entries must be non-empty strings")
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts or raw.startswith("~"):
            raise BrokerError(f"{key} entries must be relative paths within the workspace")
        if any(character in raw for character in "*?[]"):
            raise BrokerError(f"{key} entries cannot contain glob characters")
        normalized = path.as_posix()
        if normalized in {".", ""} or normalized.endswith("/"):
            raise BrokerError(f"{key} entries must not name the workspace root")
        result.append(normalized)
    return tuple(dict.fromkeys(result))


def _workspace(arguments: dict[str, Any]) -> Path:
    configured = _as_string(arguments, "workspace", os.environ.get("CLAUDE_PROJECT_DIR", ""))
    if not configured:
        raise BrokerError("workspace is required when CLAUDE_PROJECT_DIR is not set")
    path = Path(configured).expanduser().resolve()
    if not path.is_dir():
        raise BrokerError(f"workspace is not an existing directory: {path}")
    return path


def parse_request(mode: str, arguments: Any) -> DelegationRequest:
    if not isinstance(arguments, dict):
        raise BrokerError("tool arguments must be an object")
    task = _as_string(arguments, "task").strip()
    if not task:
        raise BrokerError("task is required")
    if len(task) > MAX_TASK_CHARS:
        raise BrokerError(f"task exceeds {MAX_TASK_CHARS} characters")

    policy = load_policy()
    requested_profile = _as_string(arguments, "profile", policy.mode_profiles.get(mode, policy.default_profile))
    if requested_profile not in policy.profiles:
        raise BrokerError(f"profile must be one of: {', '.join(sorted(policy.profiles))}")
    profile = policy.profiles[requested_profile]

    effort = _as_string(arguments, "effort", profile.effort)
    if effort not in SUPPORTED_EFFORTS:
        raise BrokerError(f"effort must be one of: {', '.join(sorted(SUPPORTED_EFFORTS))}")

    context = _as_string(arguments, "context", profile.context)
    if context not in SUPPORTED_CONTEXTS:
        raise BrokerError(f"context must be one of: {', '.join(sorted(SUPPORTED_CONTEXTS))}")

    credits = _validated_int(arguments.get("max_ai_credits", profile.max_ai_credits), "max_ai_credits", 1, 100)
    timeout = _validated_int(arguments.get("timeout_seconds", profile.timeout_seconds), "timeout_seconds", 15, 900)

    commands = arguments.get("allowed_commands", [])
    if not isinstance(commands, list) or not all(isinstance(item, str) for item in commands):
        raise BrokerError("allowed_commands must be an array of command strings")
    if any(command not in SAFE_COMMANDS for command in commands):
        raise BrokerError("allowed_commands contains a command outside the broker allowlist")
    if mode != "implement" and commands:
        raise BrokerError("allowed_commands is available only for implementation")

    include_diff = arguments.get("include_working_diff", True)
    if not isinstance(include_diff, bool):
        raise BrokerError("include_working_diff must be a boolean")

    model = _validated_model(arguments.get("model", profile.model), "model")

    workspace = _workspace(arguments)
    writable_paths = _relative_paths(
        arguments.get("writable_paths"), "writable_paths", required=mode == "implement"
    )
    if mode != "implement" and writable_paths:
        raise BrokerError("writable_paths is available only for implementation")
    if len(writable_paths) > 25:
        raise BrokerError("writable_paths may include at most 25 files")
    for relative_path in writable_paths:
        if (workspace / relative_path).is_dir():
            raise BrokerError("writable_paths entries must name files, not existing directories")
        if any(character in relative_path for character in ",()\r\n"):
            raise BrokerError("writable_paths entries cannot contain permission-syntax characters")

    return DelegationRequest(
        mode=mode,
        task=task,
        workspace=workspace,
        paths=_relative_paths(arguments.get("paths"), "paths"),
        writable_paths=writable_paths,
        allowed_commands=tuple(dict.fromkeys(commands)),
        profile=profile.name,
        model=model,
        effort=effort,
        context=context,
        max_ai_credits=credits,
        timeout_seconds=timeout,
        include_working_diff=include_diff,
    )


def _read_working_diff(request: DelegationRequest) -> str:
    command = ["git", "-C", str(request.workspace), "diff", "--no-ext-diff", "--"]
    command.extend(request.paths)
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"[Broker could not collect the working diff: {error}]"
    if completed.returncode != 0:
        return f"[Broker could not collect the working diff: {completed.stderr.strip()}]"
    output = completed.stdout
    if len(output) > MAX_DIFF_CHARS:
        output = output[:MAX_DIFF_CHARS] + "\n[Diff truncated by broker.]"
    return output or "[No uncommitted diff matched the requested scope.]"


def build_prompt(request: DelegationRequest) -> str:
    authority = "read-only" if request.mode in {"research", "review"} else "write only named files"
    sections = [
        "You are a delegated GitHub Copilot worker.",
        f"Workspace: {request.workspace}",
        f"Mode: {request.mode}",
        f"Authority: {authority}.",
        "Follow repository instructions. Do not commit, push, create pull requests, change dependencies, or modify files outside the granted scope.",
        "The parent agent owns final decisions. Report evidence, changed files, tests run, limitations, and any follow-up it must perform.",
        "",
        "Task:",
        request.task,
    ]
    if request.paths:
        sections.extend(["", "Relevant paths:", *[f"- {path}" for path in request.paths]])
    if request.writable_paths:
        sections.extend(["", "Writable files:", *[f"- {path}" for path in request.writable_paths]])
    if request.allowed_commands:
        sections.extend(["", "Allowed verification commands:", *[f"- {command}" for command in request.allowed_commands]])
    if request.mode == "review" and request.include_working_diff:
        sections.extend(["", "Working-tree diff supplied by the broker:", "```diff", _read_working_diff(request), "```"])
    return "\n".join(sections)


def _copilot_base_command(request: DelegationRequest, prompt: str) -> list[str]:
    binary = shlex.split(os.environ.get("FEDERATED_BROKER_COPILOT_BIN", "copilot"))
    if not binary:
        raise BrokerError("FEDERATED_BROKER_COPILOT_BIN cannot be empty")
    command = [
        *binary,
        "-C",
        str(request.workspace),
        "-p",
        prompt,
        "--output-format",
        "json",
        "--no-ask-user",
        "--no-remote",
        "--no-remote-export",
        "--disable-builtin-mcps",
        "--disallow-temp-dir",
        "--model",
        request.model,
        "--effort",
        request.effort,
        "--context",
        request.context,
        "--max-ai-credits",
        str(request.max_ai_credits),
    ]
    if request.mode in {"research", "review"}:
        command.extend(["--available-tools", "read", "--allow-tool", "read"])
    else:
        allowed_tools = ["read"]
        allowed_tools.extend(f"write({path})" for path in request.writable_paths)
        allowed_tools.extend(f"shell({command})" for command in request.allowed_commands)
        command.extend(["--available-tools", "read,write,shell", "--allow-tool", ",".join(allowed_tools)])
    return command


def _redacted_command(command: list[str]) -> list[str]:
    redacted = command.copy()
    try:
        redacted[redacted.index("-p") + 1] = "[delegation prompt omitted]"
    except (ValueError, IndexError):
        pass
    return redacted


@contextmanager
def workspace_lock(workspace: Path) -> Iterator[None]:
    identifier = hashlib.sha256(str(workspace).encode()).hexdigest()[:20]
    path = Path(tempfile.gettempdir()) / f"federated-agent-broker-{identifier}.lock"
    with path.open("w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise BrokerError("another implementation delegation already holds this workspace lock") from error
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _parse_output(output: str) -> tuple[list[Any], str]:
    events: list[Any] = []
    text_lines: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            text_lines.append(line)
    if len(events) > 30:
        events = events[-30:]
    text = "\n".join(text_lines)
    return events, text


def run_delegation(request: DelegationRequest) -> dict[str, Any]:
    prompt = build_prompt(request)
    command = _copilot_base_command(request, prompt)
    started = time.monotonic()
    request_id = f"del_{uuid.uuid4().hex[:16]}"
    try:
        completed = subprocess.run(
            command,
            cwd=request.workspace,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=request.timeout_seconds,
            check=False,
        )
        timed_out = False
    except subprocess.TimeoutExpired as error:
        completed = None
        timed_out = True
        stdout = error.stdout or ""
        stderr = error.stderr or ""
    except OSError as error:
        raise BrokerError(f"could not start Copilot CLI: {error}") from error

    if completed is not None:
        stdout = completed.stdout
        stderr = completed.stderr
    if isinstance(stdout, bytes):
        stdout = stdout.decode(errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode(errors="replace")
    stdout = stdout[:MAX_CAPTURED_OUTPUT_CHARS]
    stderr = stderr[:MAX_CAPTURED_OUTPUT_CHARS]
    events, text_output = _parse_output(stdout)
    status = "timed_out" if timed_out else "completed" if completed and completed.returncode == 0 else "failed"
    return {
        "requestId": request_id,
        "provider": "github-copilot-cli",
        "mode": request.mode,
        "authority": "read-only" if request.mode in {"research", "review"} else "scoped-write",
        "workspace": str(request.workspace),
        "profile": request.profile,
        "model": request.model,
        "effort": request.effort,
        "context": request.context,
        "maxAiCredits": request.max_ai_credits,
        "status": status,
        "exitCode": None if completed is None else completed.returncode,
        "durationSeconds": round(time.monotonic() - started, 3),
        "paths": list(request.paths),
        "writablePaths": list(request.writable_paths),
        "allowedCommands": list(request.allowed_commands),
        "command": _redacted_command(command),
        "events": events,
        "textOutput": text_output,
        "stderr": stderr,
        "limitations": [
            "The parent agent must inspect any changes and run final verification.",
            "The receipt records Copilot output; it does not prove the task is correct.",
        ],
    }


def broker_status() -> dict[str, Any]:
    binary = shlex.split(os.environ.get("FEDERATED_BROKER_COPILOT_BIN", "copilot"))
    version = "unavailable"
    error = ""
    try:
        completed = subprocess.run(
            [*binary, "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
        version = completed.stdout.strip() or completed.stderr.strip() or f"exit {completed.returncode}"
    except (OSError, subprocess.TimeoutExpired) as status_error:
        error = str(status_error)
    try:
        policy = load_policy()
        policy_summary: dict[str, Any] = {
            "source": policy.source,
            "defaultProfile": policy.default_profile,
            "modeProfiles": policy.mode_profiles,
            "profiles": {
                name: {
                    "model": profile.model,
                    "effort": profile.effort,
                    "context": profile.context,
                    "maxAiCredits": profile.max_ai_credits,
                    "timeoutSeconds": profile.timeout_seconds,
                }
                for name, profile in policy.profiles.items()
            },
        }
    except BrokerError as policy_error:
        policy_summary = {"error": str(policy_error)}
    return {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "copilotCommand": binary,
        "copilotVersion": version,
        "error": error,
        "policy": {
            "defaultMaxAiCredits": DEFAULT_MAX_AI_CREDITS,
            "readOnlyTools": ["copilot_research", "copilot_review"],
            "implementationRequiresExactWritablePaths": True,
            "implementationWorkspaceLock": True,
            "safeCommands": sorted(SAFE_COMMANDS),
            "profiles": policy_summary,
        },
    }


def tool_result(value: dict[str, Any], *, is_error: bool = False) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}],
        "isError": is_error,
    }


class McpServer:
    """Minimal MCP stdio server with only the capabilities the broker needs."""

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        request_id = request.get("id")
        method = request.get("method")
        if not isinstance(method, str):
            return self._error(request_id, -32600, "method must be a string")
        if method == "notifications/initialized":
            return None
        if method == "initialize":
            params = request.get("params", {})
            requested_version = params.get("protocolVersion") if isinstance(params, dict) else None
            protocol_version = requested_version if isinstance(requested_version, str) else "2025-06-18"
            return self._result(
                request_id,
                {
                    "protocolVersion": protocol_version,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            )
        if method == "ping":
            return self._result(request_id, {})
        if method == "tools/list":
            return self._result(request_id, {"tools": tool_definitions()})
        if method == "tools/call":
            params = request.get("params")
            if not isinstance(params, dict):
                return self._error(request_id, -32602, "tools/call params must be an object")
            return self._result(request_id, self.call_tool(params))
        return self._error(request_id, -32601, f"method not found: {method}")

    def call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        arguments = params.get("arguments", {})
        if name == "broker_status":
            return tool_result(broker_status())
        modes = {
            "copilot_research": "research",
            "copilot_review": "review",
            "copilot_implement": "implement",
        }
        if name not in modes:
            return tool_result({"error": f"unknown broker tool: {name}"}, is_error=True)
        try:
            delegation = parse_request(modes[name], arguments)
            if delegation.mode == "implement":
                with workspace_lock(delegation.workspace):
                    receipt = run_delegation(delegation)
            else:
                receipt = run_delegation(delegation)
            return tool_result(receipt, is_error=receipt["status"] != "completed")
        except BrokerError as error:
            return tool_result({"error": str(error)}, is_error=True)

    @staticmethod
    def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "result": result}

    @staticmethod
    def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def serve() -> None:
    server = McpServer()
    for raw_line in sys.stdin:
        try:
            request = json.loads(raw_line)
            if not isinstance(request, dict):
                raise ValueError("JSON-RPC request must be an object")
            response = server.handle_request(request)
            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
        except Exception as error:  # Keep the server usable after malformed client input.
            print(f"{SERVER_NAME}: {error}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    serve()

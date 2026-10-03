#!/usr/bin/env python3
"""Drive one GitHub Copilot SDK session for the copilot-worker supervisor.

The policy in this module is pure and imports nothing from the SDK, so it can be
tested on its own. Only the driver imports the SDK.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import re
import shlex
import sys
from typing import Any

READ_TOOLS = ("view", "rg", "glob")
TOOLS = {
    "research": READ_TOOLS,
    "review": READ_TOOLS,
    "implement": (
        *READ_TOOLS, "create", "edit", "apply_patch",
        "bash", "read_bash", "stop_bash", "list_bash",
    ),
}
# The supervisor enforces the real timeout. This margin keeps the SDK's own wait,
# which defaults to 60 seconds, from ending a run first.
SEND_TIMEOUT_MARGIN = 60

# Commands a worker may never run, as leading words after wrappers are removed.
DENIED_COMMANDS = (
    ("gh",),
    ("sudo",),
    ("git", "push"),
    ("git", "remote"),
    ("git", "worktree"),
)
_WRAPPERS = {"env", "command", "exec", "nohup", "time"}
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_SEPARATORS = re.compile(r"\|\||&&|[;|&\n]")
# git options that take a separate value before the subcommand.
_GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def _words(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        # Unbalanced quotes: still check the plain words rather than skipping the check.
        return segment.split()


def _command_words(words: list[str]) -> list[str]:
    """Drop variable assignments and wrapper programs, and normalize the program name."""
    index = 0
    while index < len(words):
        word = words[index]
        if _ASSIGNMENT.match(word):
            index += 1
        elif os.path.basename(word) in _WRAPPERS:
            index += 1
            while index < len(words) and words[index].startswith("-"):
                index += 1
        else:
            break
    rest = words[index:]
    if not rest:
        return []
    program = os.path.basename(rest[0])
    if program != "git":
        return [program, *rest[1:]]
    # Skip git's global options so "git -C path push" is still seen as "git push".
    args = rest[1:]
    position = 0
    while position < len(args) and args[position].startswith("-"):
        position += 2 if args[position] in _GIT_VALUE_OPTIONS else 1
    return ["git", *args[position:]]


def _denied_command(text: str) -> str | None:
    for segment in _SEPARATORS.split(text):
        words = _command_words(_words(segment))
        for denied in DENIED_COMMANDS:
            if tuple(words[: len(denied)]) == denied:
                return " ".join(denied)
    return None


def _inside(path: str | None, workspace: str) -> bool:
    if not path:
        return False
    if not os.path.isabs(path):
        path = os.path.join(workspace, path)
    real = os.path.realpath(path)
    root = os.path.realpath(workspace)
    return real == root or real.startswith(root + os.sep)


def decide(kind: str, fields: dict, workspace: str, mode: str) -> tuple[bool, str]:
    """Return (allowed, reason) for one permission request. Unknown kinds are rejected."""
    if kind == "shell":
        if mode != "implement":
            return False, f"shell commands are not allowed in {mode} mode"
        segments = [segment for segment in fields.get("segments") or [] if segment]
        if not segments:
            return False, "shell request carried no command text"
        for segment in segments:
            denied = _denied_command(segment)
            if denied:
                return False, f"copilot-worker denied command: {denied}"
        return True, "allowed"
    if kind in ("read", "write"):
        if kind == "write" and mode != "implement":
            return False, f"writes are not allowed in {mode} mode"
        if not _inside(fields.get("path"), workspace):
            return False, f"{fields.get('path')!r} is outside the workspace"
        return True, "allowed"
    return False, f"copilot-worker does not allow {kind} requests"


def request_kind(request: Any) -> str:
    """Map an SDK permission request class to a policy kind: PermissionRequestShell -> shell."""
    name = type(request).__name__.removeprefix("PermissionRequest")
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower() or "unknown"


def request_fields(request: Any) -> dict:
    kind = request_kind(request)
    if kind == "shell":
        texts = [getattr(request, "full_command_text", None)]
        for part in [*(getattr(request, "command_segments", None) or []),
                     *(getattr(request, "commands", None) or [])]:
            texts += [getattr(part, "full_command_text", None), getattr(part, "identifier", None)]
        return {"segments": [text for text in texts if text]}
    if kind in ("read", "write"):
        path = (getattr(request, "resolved_path", None) or getattr(request, "path", None)
                or getattr(request, "file_name", None))
        return {"path": path}
    return {}


def client_options(config: dict) -> dict:
    # An isolated Copilot home keeps the user's hooks, skills, and MCP config out.
    return {"working_directory": config["workspace"], "base_directory": config["copilotHome"]}


def session_options(config: dict) -> dict:
    options = {
        "model": config["model"],
        "working_directory": config["workspace"],
        "available_tools": TOOLS[config["mode"]],
        "session_limits": {"max_ai_credits": config["credits"]},
        "enable_skills": False,
    }
    if config.get("effort"):
        options["reasoning_effort"] = config["effort"]
    return options


def send_options(config: dict) -> dict:
    return {"timeout": float(config["timeout"] + SEND_TIMEOUT_MARGIN)}


def summarize_usage(calls: list[dict]) -> dict:
    keys = ("inputTokens", "outputTokens", "cacheReadTokens", "cacheWriteTokens")
    total = sum(call.get("totalNanoAiu") or 0 for call in calls)
    summary = {key: sum(call.get(key) or 0 for call in calls) for key in keys}
    summary.update({
        "aiCredits": round(total / 1e9, 4),
        "totalNanoAiu": total,
        "modelCalls": len(calls),
        "models": sorted({call["model"] for call in calls if call.get("model")}),
    })
    return summary


def _usage_call(data: Any) -> dict:
    copilot_usage = getattr(data, "copilot_usage", None)
    return {
        "totalNanoAiu": getattr(copilot_usage, "total_nano_aiu", 0) or 0,
        "inputTokens": getattr(data, "input_tokens", 0),
        "outputTokens": getattr(data, "output_tokens", 0),
        "cacheReadTokens": getattr(data, "cache_read_tokens", 0),
        "cacheWriteTokens": getattr(data, "cache_write_tokens", 0),
        "model": getattr(data, "model", None),
    }


def versions() -> dict:
    from importlib.metadata import version

    from copilot._cli_version import CLI_VERSION

    return {"sdkVersion": version("github-copilot-sdk"), "runtimeVersion": CLI_VERSION}


async def drive(run_dir: Path) -> None:
    from copilot import CopilotClient, ToolSet
    from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject

    config = json.loads((run_dir / "engine.json").read_text(encoding="utf-8"))
    prompt = (run_dir / "task.md").read_text(encoding="utf-8")
    (run_dir / "runtime.json").write_text(json.dumps(versions()) + "\n", encoding="utf-8")
    calls: list[dict] = []
    response = ""

    with open(run_dir / "events.jsonl", "a", encoding="utf-8") as events, \
            open(run_dir / "permissions.jsonl", "a", encoding="utf-8") as permissions:

        def on_permission(request: Any, _invocation: Any) -> Any:
            kind, fields = request_kind(request), request_fields(request)
            allowed, reason = decide(kind, fields, config["workspace"], config["mode"])
            permissions.write(json.dumps(
                {"kind": kind, "fields": fields, "allowed": allowed, "reason": reason}) + "\n")
            permissions.flush()
            if allowed:
                return PermissionDecisionApproveOnce()
            return PermissionDecisionReject(feedback=reason)

        def on_event(event: Any) -> None:
            nonlocal response
            events.write(json.dumps(event.to_dict(), default=str) + "\n")
            name = type(event.data).__name__
            if name == "AssistantUsageData":
                calls.append(_usage_call(event.data))
            elif name == "AssistantMessageData":
                content = getattr(event.data, "content", None)
                if isinstance(content, str) and content.strip():
                    response = content

        tools = ToolSet()
        for tool in TOOLS[config["mode"]]:
            tools.add_builtin(tool)
        options = {**session_options(config), "available_tools": tools}
        try:
            async with CopilotClient(**client_options(config)) as client:
                session = await client.create_session(
                    on_permission_request=on_permission, on_event=on_event, **options
                )
                await session.send_and_wait(prompt, **send_options(config))
        finally:
            (run_dir / "response.md").write_text(response, encoding="utf-8")
            (run_dir / "usage.json").write_text(
                json.dumps(summarize_usage(calls), indent=2) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    if argv == ["--version"]:
        info = versions()
        print(f"github-copilot-sdk {info['sdkVersion']} (runtime {info['runtimeVersion']})")
        return 0
    if len(argv) != 1:
        print("usage: worker_engine.py RUN_DIR | --version", file=sys.stderr)
        return 2
    asyncio.run(drive(Path(argv[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

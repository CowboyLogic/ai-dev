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
import subprocess
import sys
from typing import Any

READ_TOOLS = ("view", "rg", "glob")
TOOLS = {
    "research": READ_TOOLS,
    "review": READ_TOOLS,
    "implement": (*READ_TOOLS, "apply_patch", "bash", "read_bash", "stop_bash", "list_bash"),
}
# The supervisor enforces the real timeout. This margin keeps the SDK's own wait,
# which defaults to 60 seconds, from ending a run first.
SEND_TIMEOUT_MARGIN = 60

# An accident guard, not a sandbox: an interpreter given code (python -c, a script
# file, a variable holding a command name) can still run anything.
DENIED_PROGRAMS = {"gh", "sudo", "doas"}
DENIED_GIT_SUBCOMMANDS = {"push", "remote", "worktree", "send-pack"}
_SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}
# Programs that run another command, with their options that take a separate value and
# the number of plain arguments that come before the command they run.
_WRAPPERS = {
    "env": ({"-u", "-P", "-S", "-C", "-a", "--unset", "--chdir", "--split-string", "--argv0"}, 0),
    "command": (set(), 0),
    "exec": ({"-a"}, 0),
    "nohup": (set(), 0),
    "time": ({"-f", "-o", "--format", "--output"}, 0),
    "nice": ({"-n", "--adjustment"}, 0),
    "timeout": ({"-s", "-k", "--signal", "--kill-after"}, 1),
    "xargs": ({
        "-I", "-J", "-R", "-S", "-n", "-L", "-P", "-d", "-E", "-s", "-a", "--max-args", "--max-lines", "--max-procs",
        "--max-chars", "--delimiter", "--eof", "--arg-file", "--process-slot-var",
    }, 0),
    "stdbuf": ({"-i", "-o", "-e", "--input", "--output", "--error"}, 0),
    "caffeinate": ({"-t", "-w"}, 0),
    "script": ({"-c", "--command"}, 1),
}
# Wrapper options whose value is itself a command line, which is checked in turn.
_COMMAND_OPTIONS = {"env": ("-S", "--split-string"), "script": ("-c", "--command")}
# Shell reserved words that precede a command: "! gh" and "if gh" still run gh.
_RESERVED_PREFIXES = {"!", "if", "then", "else", "elif", "do", "while", "until", "coproc"}
# Environment variables through which git reads aliases or a different config file.
_GIT_CONFIG_FILE_VARIABLES = {"GIT_CONFIG", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM"}
# Builtins that put an assignment into the shell session, where the next command sees it.
_EXPORTERS = {"export", "declare", "typeset", "readonly", "local"}
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_REDIRECT = re.compile(r"^\d*(>>?|<<?|&>|>&)")
_BARE_REDIRECT = re.compile(r"^\d*(>>?|<<?|&>|>&)$")
# Command separators, plus grouping and substitution, so "(gh ...)", "{ gh ...; }",
# "$(gh ...)" and "`gh ...`" are each checked as a command of their own.
_SEPARATORS = re.compile(r"\|\||&&|\$\(|[;|&\n(){}`]")
# git options that take a separate value before the subcommand.
_GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env"}
# Copilot runtime settings in the environment, such as COPILOT_ALLOW_ALL or
# COPILOT_CLI_PATH, could pre-approve tools or replace the pinned runtime.
_KEPT_COPILOT_VARIABLES = {"COPILOT_GITHUB_TOKEN"}
_MAX_DEPTH = 5


def _words(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        # Unbalanced quotes: still check the plain words rather than skipping the check.
        return segment.split()


def _denied_git(args: list[str], aliases: frozenset[str]) -> str | None:
    index = 0
    while index < len(args) and args[index].startswith("-"):
        option = args[index]
        separate = args[index + 1] if index + 1 < len(args) else ""
        if option.startswith("--config-env"):
            value = option.partition("=")[2] or separate
        elif option.startswith("-c") and not option.startswith("--"):
            value = separate if option == "-c" else option[2:]
        else:
            value = ""
        if value.lower().startswith("alias."):
            return "git alias"
        index += 2 if option in _GIT_VALUE_OPTIONS else 1
    if index >= len(args):
        return None
    subcommand, rest = args[index].lower(), args[index + 1:]
    if subcommand in DENIED_GIT_SUBCOMMANDS:
        return f"git {subcommand}"
    # An alias already in the repository or global config can stand for git push.
    if subcommand in aliases:
        return "git alias"
    if subcommand == "config":
        for arg in rest:
            if arg.lower().startswith("alias."):
                return "git config alias"
            if arg.lower().startswith("remote."):
                return "git config remote"
    return None


def _denied_assignment(word: str) -> str | None:
    """Deny NAME=value words that make git resolve an alias or read a config file we cannot see."""
    name, _, value = word.partition("=")
    if name.startswith("GIT_CONFIG_KEY_") or name == "GIT_CONFIG_PARAMETERS":
        return "git alias" if "alias." in value.lower() else None
    if name in _GIT_CONFIG_FILE_VARIABLES and value not in ("", os.devnull):
        return "a git config file from the environment"
    return None


def _scan_option(
    wrapper: str, words: list[str], index: int, value_options: set[str]
) -> tuple[str | None, int]:
    """Return (command line the option carries, if any, words the option consumes).

    Short options may be clustered (script -qc CMD, env -iS CMD): the first letter that
    takes a value ends the cluster, and the rest of the word, or else the next word, is
    that value.
    """
    option = words[index]
    command_options = _COMMAND_OPTIONS.get(wrapper, ())
    following = words[index + 1] if index + 1 < len(words) else ""
    if option.startswith("--"):
        key, equals, attached = option.partition("=")
        if equals:
            return (attached if key in command_options else None), 1
        if key in command_options:
            return following, 2
        return None, 2 if key in value_options else 1
    letters = option[1:]
    for position, letter in enumerate(letters):
        flag, rest = "-" + letter, letters[position + 1:]
        if flag in command_options:
            return (rest, 1) if rest else (following, 2)
        if flag in value_options:
            return None, 1 if rest else 2
    return None, 1


def _denied_words(words: list[str], depth: int, aliases: frozenset[str]) -> str | None:
    index = 0
    while index < len(words):
        word = words[index]
        name = os.path.basename(word).lower()
        if _ASSIGNMENT.match(word):
            denied = _denied_assignment(word)
            if denied:
                return denied
            index += 1
        elif word in _RESERVED_PREFIXES:
            index += 1
        elif _REDIRECT.match(word):
            index += 2 if _BARE_REDIRECT.match(word) else 1
        elif name in _WRAPPERS:
            value_options, positionals = _WRAPPERS[name]
            index += 1
            while index < len(words) and words[index].startswith("-"):
                payload, width = _scan_option(name, words, index, value_options)
                if payload is not None:
                    denied = _denied_command(payload, aliases, depth + 1)
                    if denied:
                        return denied
                index += width
            index += positionals
        else:
            break
    if index >= len(words):
        return None
    # Lowercase: macOS file systems are case-insensitive, so GH runs gh.
    program, args = os.path.basename(words[index]).lower(), words[index + 1:]
    if program in DENIED_PROGRAMS:
        return program
    if program in _EXPORTERS:
        for arg in args:
            denied = _denied_assignment(arg) if _ASSIGNMENT.match(arg) else None
            if denied:
                return denied
        return None
    if program == "eval":
        return _denied_command(" ".join(args), aliases, depth + 1)
    if program in _SHELLS:
        for position, arg in enumerate(args[:-1]):
            if arg.startswith("-") and not arg.startswith("--") and "c" in arg[1:]:
                return _denied_command(args[position + 1], aliases, depth + 1)
        return None
    if program.startswith("git-"):
        program, args = "git", [program[4:], *args]
    if program == "git":
        return _denied_git(args, aliases)
    return None


def _split_commands(text: str) -> tuple[list[str], bool]:
    """Split on separators the shell would act on, leaving quoted text whole.

    This keeps a payload such as bash -c 'echo ok; git push' in one piece, so that the
    recursive check sees it intact. Inside double quotes only $( and a backtick still
    start a command. Also return whether every quote was closed.
    """
    segments: list[str] = []
    current: list[str] = []
    quote = ""
    index = 0

    def cut() -> None:
        segments.append("".join(current))
        current.clear()

    while index < len(text):
        char, pair = text[index], text[index:index + 2]
        if char == "\\" and quote != "'" and len(pair) == 2:
            current.append(pair)
            index += 2
            continue
        if quote == "'":
            quote = "" if char == "'" else quote
        elif quote == '"':
            if char == '"':
                quote = ""
            elif pair == "$(" or char == "`":
                cut()
                index += len(pair) if pair == "$(" else 1
                continue
        elif char in "'\"":
            quote = char
        elif pair in ("||", "&&", "$("):
            cut()
            index += 2
            continue
        elif char in ";|&\n(){}`":
            cut()
            index += 1
            continue
        current.append(char)
        index += 1
    cut()
    return segments, not quote


def _denied_command(text: str, aliases: frozenset[str], depth: int = 0) -> str | None:
    if depth > _MAX_DEPTH:
        return "a command nested too deeply to check"
    # The shell removes a backslash-newline pair before it splits words, so a command
    # continued across lines is still one command.
    text = text.replace("\\\n", "")
    segments, balanced = _split_commands(text)
    if not balanced:
        # An unclosed quote would swallow what follows it, so also check the plain split.
        segments += _SEPARATORS.split(text)
    for segment in segments:
        denied = _denied_words(_words(segment), depth, aliases)
        if denied:
            return denied
    return None


def configured_aliases(workspace: str) -> frozenset[str]:
    """Names of the git aliases the workspace's repository and global config define."""
    try:
        result = subprocess.run(
            ["git", "-C", workspace, "config", "--get-regexp", r"^alias\."],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return frozenset()
    keys = (line.split(None, 1)[0] for line in result.stdout.splitlines() if line.strip())
    return frozenset(key.split(".", 1)[1].lower() for key in keys)


def _inside(path: str | None, workspace: str) -> bool:
    if not path or path.startswith("~") or "$" in path:
        # Reject forms the runtime might expand before reading.
        return False
    if not os.path.isabs(path):
        path = os.path.join(workspace, path)
    real = os.path.realpath(path)
    root = os.path.realpath(workspace)
    return real == root or real.startswith(root + os.sep)


def decide(
    kind: str, fields: dict, workspace: str, mode: str, aliases: frozenset[str] = frozenset()
) -> tuple[bool, str]:
    """Return (allowed, reason) for one permission request. Unknown kinds are rejected."""
    if kind == "shell":
        if mode != "implement":
            return False, f"shell commands are not allowed in {mode} mode"
        segments = [segment for segment in fields.get("segments") or [] if segment]
        if not segments:
            return False, "shell request carried no command text"
        for segment in segments:
            denied = _denied_command(segment, aliases)
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


def scrub_environment(environ: dict) -> dict:
    return {
        key: value for key, value in environ.items()
        if not key.startswith("COPILOT_") or key in _KEPT_COPILOT_VARIABLES
    }


def client_options(config: dict, env: dict) -> dict:
    # An isolated Copilot home keeps the user's hooks, skills, and MCP config out.
    return {
        "working_directory": config["workspace"],
        "base_directory": config["copilotHome"],
        "env": env,
    }


def session_options(config: dict) -> dict:
    options = {
        "model": config["model"],
        "working_directory": config["workspace"],
        "available_tools": TOOLS[config["mode"]],
        "session_limits": {"max_ai_credits": config["credits"]},
        "enable_skills": False,
        # Repository .github/hooks would run commands and could settle permissions first.
        "enable_file_hooks": False,
        "disabled_mcp_servers": ["github-mcp-server"],
    }
    if config.get("effort"):
        options["reasoning_effort"] = config["effort"]
    return options


def session_kwargs(config: dict, on_permission: Any, on_event: Any, tools: Any) -> dict:
    """Everything create_session receives. drive() passes exactly this."""
    return {
        **session_options(config),
        "available_tools": tools,
        "on_permission_request": on_permission,
        "on_event": on_event,
    }


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
    # Scrub before the SDK loads: it reads COPILOT_* settings from this process too.
    env = scrub_environment(dict(os.environ))
    os.environ.clear()
    os.environ.update(env)

    from copilot import CopilotClient, ToolSet
    from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject

    config = json.loads((run_dir / "engine.json").read_text(encoding="utf-8"))
    prompt = (run_dir / "task.md").read_text(encoding="utf-8")
    (run_dir / "runtime.json").write_text(json.dumps(versions()) + "\n", encoding="utf-8")
    calls: list[dict] = []
    response = ""
    aliases = configured_aliases(config["workspace"])

    with open(run_dir / "events.jsonl", "a", encoding="utf-8") as events, \
            open(run_dir / "permissions.jsonl", "a", encoding="utf-8") as permissions:

        def on_permission(request: Any, _invocation: Any) -> Any:
            kind, fields = request_kind(request), request_fields(request)
            allowed, reason = decide(kind, fields, config["workspace"], config["mode"], aliases)
            permissions.write(json.dumps(
                {"kind": kind, "fields": fields, "allowed": allowed, "reason": reason}) + "\n")
            permissions.flush()
            if allowed:
                return PermissionDecisionApproveOnce()
            return PermissionDecisionReject(feedback=reason)

        def on_event(event: Any) -> None:
            nonlocal response
            events.write(json.dumps(event.to_dict(), default=str) + "\n")
            events.flush()
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
        try:
            async with CopilotClient(**client_options(config, env)) as client:
                session = await client.create_session(
                    **session_kwargs(config, on_permission, on_event, tools)
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

#!/usr/bin/env python3
"""Drive one GitHub Copilot SDK session for the copilot-worker supervisor.

The policy in this module is pure and imports nothing from the SDK, so it can be
tested on its own. Only the driver imports the SDK.
"""

from __future__ import annotations

import os
import re
import shlex

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

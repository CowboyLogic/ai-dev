#!/usr/bin/env python3
"""Run GitHub Copilot CLI as a bounded worker for Claude Code."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import secrets
import shlex
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

MODES = ("research", "review", "implement")
DEFAULT_MODELS = {"research": "gpt-6-luna", "review": "gpt-6.1-sol", "implement": "gpt-6.1-sol"}
DEFAULT_CREDITS = {"research": 30, "review": 30, "implement": 60}
DEFAULT_TIMEOUTS = {"research": 600, "review": 600, "implement": 1800}
# An accident guard, not a sandbox: shell commands are not confined to the worktree.
DENY_TOOLS = (
    "shell(git push)",
    "shell(git remote)",
    "shell(git worktree)",
    "shell(gh:*)",
    "shell(sudo)",
)
EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max")
RUN_ID_PATTERN = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}$")
MAX_DIFF_CHARS = 200_000
MIN_CREDITS = 30
KILL_GRACE_SECONDS = 10
FOOTER = (
    "\n\n---\nWorker rules: stay inside the current working directory. Do not push, "
    "do not open pull requests, and do not change Git remotes. Finish with a short "
    "summary of what you did and anything left undone."
)


class WorkerError(Exception):
    """A problem reported to the caller without a traceback."""


def state_home() -> Path:
    return Path(os.environ.get("COPILOT_WORKER_HOME") or Path.home() / ".copilot-worker")


def copilot_bin() -> list[str]:
    binary = shlex.split(os.environ.get("COPILOT_WORKER_BIN") or "copilot")
    if not binary:
        raise WorkerError("COPILOT_WORKER_BIN is empty")
    return binary


def git(args: list[str], cwd: Path) -> str:
    done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if done.returncode != 0:
        raise WorkerError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    # Keep leading whitespace: porcelain status lines can start with a space.
    return done.stdout.rstrip("\n")


def repo_root(cwd: Path) -> Path:
    try:
        return Path(git(["rev-parse", "--show-toplevel"], cwd))
    except WorkerError as error:
        raise WorkerError(f"{cwd} is not inside a Git repository") from error


def build_prompt(mode: str, task: str, root: Path) -> str:
    prompt = task.strip() + FOOTER
    if mode == "review":
        diff = git(["diff", "HEAD"], root)
        if len(diff) > MAX_DIFF_CHARS:
            diff = diff[:MAX_DIFF_CHARS] + "\n[diff truncated by copilot-worker]"
        prompt += "\n\nWorking-tree diff against HEAD:\n\n" + (diff or "[no tracked changes]")
    return prompt


def build_command(
    *,
    mode: str,
    workspace: Path,
    prompt: str,
    model: str,
    effort: str | None,
    credits: int,
    usage_file: Path,
) -> list[str]:
    command = [
        *copilot_bin(),
        "-C", str(workspace),
        # The equals form keeps a prompt that starts with "-" from being read as an option.
        f"--prompt={prompt}",
        "--output-format", "json",
        "--no-ask-user",
        "--no-remote",
        "--no-remote-export",
        "--disable-builtin-mcps",
        "--model", model,
        "--max-ai-credits", str(credits),
        "--usage-output-file", str(usage_file),
    ]
    if effort:
        command += ["--reasoning-effort", effort]
    if mode == "implement":
        command.append("--allow-all-tools")
        command += [f"--deny-tool={pattern}" for pattern in DENY_TOOLS]
    else:
        command += ["--available-tools=view", "--allow-tool=read"]
    return command


def extract_response(events_text: str) -> str:
    """Return the last non-empty assistant message in Copilot's JSONL output."""
    response = ""
    for line in events_text.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict) or event.get("type") != "assistant.message":
            continue
        data = event.get("data")
        content = data.get("content") if isinstance(data, dict) else event.get("content")
        if isinstance(content, str) and content.strip():
            response = content
    return response

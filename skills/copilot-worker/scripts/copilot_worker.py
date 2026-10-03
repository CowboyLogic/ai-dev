#!/usr/bin/env python3
# Every dependency is pinned exactly, the SDK's own included, so that a new release of
# any of them cannot change what runs. To upgrade, follow references/upgrading.md.
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "annotated-types==0.8.0",
#     "anyio==4.15.1",
#     "certifi==2026.7.22",
#     "github-copilot-sdk==1.0.14",
#     "h11==0.16.0",
#     "httpcore==1.0.9",
#     "httpx==0.28.1",
#     "idna==3.20",
#     "pydantic==2.13.5",
#     "pydantic-core==2.46.5",
#     "python-dateutil==2.9.0.post0",
#     "six==1.17.0",
#     "typing-extensions==4.16.0",
#     "typing-inspection==0.4.4",
# ]
# ///
"""Run GitHub Copilot as a bounded worker for Claude Code.

This supervisor is standard-library Python. It starts worker_engine.py, which drives
the GitHub Copilot SDK, and enforces the timeout, worktree, and branch rules around it.
Run it with `uv run` so the SDK dependency declared above is available to the engine.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import secrets
import shlex
import shutil
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
# The values the SDK accepts for reasoning_effort.
EFFORTS = ("low", "medium", "high", "xhigh", "max")
RUN_ID_PATTERN = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}$")
# Keeps an attached review diff to a size the worker can read alongside the files.
MAX_DIFF_BYTES = 100_000
MIN_CREDITS = 30
KILL_GRACE_SECONDS = 10
FOOTER = (
    "\n\n---\nWorker rules: stay inside the current working directory. Do not push, "
    "do not open pull requests, do not change Git remotes, and do not switch, create, or "
    "rename branches. Finish with a short "
    "summary of what you did and anything left undone."
)


class WorkerError(Exception):
    """A problem reported to the caller without a traceback."""


def state_home() -> Path:
    return Path(os.environ.get("COPILOT_WORKER_HOME") or Path.home() / ".copilot-worker")


ENGINE = Path(__file__).with_name("worker_engine.py")


def engine_base() -> list[str]:
    """The engine command without its argument. Tests replace it with a fake."""
    override = os.environ.get("COPILOT_WORKER_ENGINE")
    if override is None:
        return [sys.executable, str(ENGINE)]
    command = shlex.split(override)
    if not command:
        raise WorkerError("COPILOT_WORKER_ENGINE is empty")
    return command


def git(args: list[str], cwd: Path) -> str:
    # A diff can carry bytes that are not UTF-8; replace them instead of failing.
    done = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, encoding="utf-8", errors="replace"
    )
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
        encoded = diff.encode("utf-8")
        if len(encoded) > MAX_DIFF_BYTES:
            diff = encoded[:MAX_DIFF_BYTES].decode("utf-8", errors="ignore")
            diff += "\n[diff truncated by copilot-worker]"
        prompt += "\n\nWorking-tree diff against HEAD:\n\n" + (diff or "[no tracked changes]")
    return prompt


class _Terminated(Exception):
    def __init__(self, signum: int) -> None:
        super().__init__(signum)
        self.signum = signum


def new_run_id() -> str:
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{stamp}-{secrets.token_hex(2)}"


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def copilot_version() -> str:
    try:
        done = subprocess.run(
            [*engine_base(), "--version"], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"
    lines = done.stdout.strip().splitlines()
    return lines[0] if done.returncode == 0 and lines else "unknown"


def pins_status() -> tuple[bool, str]:
    """Ask the engine whether the installed SDK and runtime are the ones pins.json names."""
    try:
        done = subprocess.run(
            [*engine_base(), "--check-pins"], capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, "could not run the engine to check them"
    lines = done.stdout.strip().splitlines()
    return done.returncode == 0, lines[0] if lines else "no answer from the engine"


def _kill_group(process: subprocess.Popen[bytes]) -> None:
    """SIGTERM the worker's process group, then SIGKILL whatever is left of it."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=KILL_GRACE_SECONDS)
    except (ProcessLookupError, PermissionError, subprocess.TimeoutExpired):
        pass
    # The leader exiting does not mean the group is gone: a child may ignore SIGTERM.
    _kill_stragglers(process)
    process.wait()


def _kill_stragglers(process: subprocess.Popen[bytes]) -> None:
    # Reaches the worker's own process group only. A process that moved to a new session
    # is not contained; SKILL.md states that limit.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run_engine(command: list[str], run_dir: Path, timeout: int) -> tuple[int | None, str]:
    """Run the worker to completion. Return (exit code, termination reason)."""

    def on_signal(signum: int, _frame: Any) -> None:
        raise _Terminated(signum)

    def stop_worker() -> None:
        # A second signal during the kill must not abort it and lose the result.
        for name in previous:
            signal.signal(name, signal.SIG_IGN)
        if process is not None:
            _kill_group(process)

    process: subprocess.Popen[bytes] | None = None
    previous = {name: signal.signal(name, on_signal) for name in (signal.SIGTERM, signal.SIGINT)}
    try:
        with open(run_dir / "stderr.log", "wb") as log:
            # Own session and no stdin: the worker outlives the caller's connection. The
            # engine reads its task from task.md, so it never appears in the process list.
            process = subprocess.Popen(
                command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            code = process.wait(timeout=timeout)
            # Anything the worker left running must not outlive the run it belongs to.
            _kill_stragglers(process)
        return (code, "exit") if code >= 0 else (None, f"signal:{-code}")
    except subprocess.TimeoutExpired:
        stop_worker()
        return None, "timeout"
    except _Terminated as stop:
        stop_worker()
        return None, f"signal:{stop.signum}"
    finally:
        for name, handler in previous.items():
            signal.signal(name, handler)


def execute_run(
    *,
    mode: str,
    task: str,
    cwd: Path,
    model: str | None = None,
    effort: str | None = None,
    credits: int | None = None,
    timeout: int | None = None,
) -> dict[str, Any]:
    if mode not in MODES:
        raise WorkerError(f"unknown mode: {mode}")
    if not task.strip():
        raise WorkerError("the task is empty")
    if effort is not None and effort not in EFFORTS:
        raise WorkerError(f"unknown effort: {effort}")
    model = model or DEFAULT_MODELS[mode]
    credits = DEFAULT_CREDITS[mode] if credits is None else credits
    timeout = DEFAULT_TIMEOUTS[mode] if timeout is None else timeout
    if credits < MIN_CREDITS:
        raise WorkerError(f"--max-ai-credits must be at least {MIN_CREDITS}")
    if timeout <= 0:
        raise WorkerError("--timeout must be greater than 0")
    root = repo_root(cwd)
    prompt = build_prompt(mode, task, root)

    run_id = new_run_id()
    # Tasks, diffs, responses, and worktrees are private: keep the state root owner-only.
    state_home().mkdir(parents=True, exist_ok=True)
    os.chmod(state_home(), 0o700)
    run_dir = state_home() / "runs" / run_id
    run_dir.mkdir(parents=True)
    workspace, branch, base = root, None, None
    if mode == "implement":
        base = git(["rev-parse", "HEAD"], root)
        if git(["status", "--porcelain"], root):
            print(
                "warning: the checkout has uncommitted changes; the worker starts from "
                "HEAD and will not see them",
                file=sys.stderr,
            )
        branch = f"copilot/{run_id}"
        workspace = state_home() / "worktrees" / f"{root.name}-{run_id}"
        workspace.parent.mkdir(parents=True, exist_ok=True)
        git(["worktree", "add", str(workspace), "-b", branch, "HEAD"], root)

    (run_dir / "task.md").write_text(prompt, encoding="utf-8")
    copilot_home = state_home() / "copilot-home"
    copilot_home.mkdir(exist_ok=True)
    engine_config = {
        "mode": mode, "model": model, "effort": effort, "credits": credits,
        "timeout": timeout, "workspace": str(workspace), "copilotHome": str(copilot_home),
    }
    (run_dir / "engine.json").write_text(json.dumps(engine_config, indent=2) + "\n", encoding="utf-8")
    command = [*engine_base(), str(run_dir)]
    started_at, clock = utc_now(), time.monotonic()
    try:
        exit_code, reason = run_engine(command, run_dir, timeout)
    except OSError as error:
        (run_dir / "stderr.log").write_text(f"could not start the engine: {error}\n", encoding="utf-8")
        exit_code, reason = None, "spawn_error"
    duration = round(time.monotonic() - clock, 3)

    response_path = run_dir / "response.md"
    response = response_path.read_text(encoding="utf-8", errors="replace") if response_path.exists() else ""
    if not response_path.exists():
        response_path.write_text("", encoding="utf-8")
    if reason == "timeout":
        status = "timed_out"
    elif reason == "exit" and exit_code == 0:
        status = "completed" if response else "completed_no_response"
    else:
        status = "failed"

    changed: dict[str, list[str]] | None = {"uncommitted": [], "commits": []}
    current_branch = None
    if mode == "implement":
        try:
            current_branch = git(["rev-parse", "--abbrev-ref", "HEAD"], workspace)
            changed["uncommitted"] = git(["status", "--porcelain"], workspace).splitlines()
            changed["commits"] = git(["log", "--oneline", f"{base}..HEAD"], workspace).splitlines()
        except (WorkerError, OSError):
            # The worker damaged its own worktree. Still record the run so clean can find it.
            changed = None
        if changed is not None and current_branch != branch:
            # The worker's commits are not on the branch the caller is told to merge.
            status = "failed"

    result = {
        "runId": run_id,
        "mode": mode,
        "model": model,
        "effort": effort,
        "status": status,
        "terminationReason": reason,
        "exitCode": exit_code,
        "startedAt": started_at,
        "endedAt": utc_now(),
        "durationSeconds": duration,
        "timeoutSeconds": timeout,
        "maxAiCredits": credits,
        "repoRoot": str(root),
        "runDir": str(run_dir),
        "workspace": str(workspace),
        "branch": branch,
        "currentBranch": current_branch,
        "baseCommit": base,
        "changedFiles": changed,
        "copilotVersion": _runtime_version(run_dir),
    }
    (run_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def _runtime_version(run_dir: Path) -> str:
    try:
        info = json.loads((run_dir / "runtime.json").read_text(encoding="utf-8"))
        return f"github-copilot-sdk {info['sdkVersion']} (runtime {info['runtimeVersion']})"
    except (OSError, ValueError, KeyError):
        return copilot_version()


def print_summary(result: dict[str, Any]) -> None:
    print(f"status: {result['status']}")
    print(f"run: {result['runId']}")
    print(f"runDir: {result['runDir']}")
    print(f"model: {result['model']}")
    print(f"duration: {result['durationSeconds']}s")
    print(f"termination: {result['terminationReason']}")
    if result["mode"] != "implement":
        return
    changed = result["changedFiles"]
    print(f"workspace: {result['workspace']}")
    print(f"branch: {result['branch']}")
    if changed is None:
        print("changes: unavailable; the worktree is no longer a Git checkout")
        return
    if result["currentBranch"] != result["branch"]:
        print(
            f"branch changed: the worker left the worktree on {result['currentBranch']!r}; "
            f"{result['branch']} does not hold its commits"
        )
    print(f"changes: {len(changed['uncommitted'])} uncommitted, {len(changed['commits'])} commits")
    lines = changed["uncommitted"] + changed["commits"]
    for line in lines[:8]:
        print(f"  {line}")
    if len(lines) > 8:
        print(f"  ... {len(lines) - 8} more; see result.json")


def cmd_run(args: argparse.Namespace, cwd: Path) -> int:
    try:
        task = Path(args.task_file).read_text(encoding="utf-8")
    except OSError as error:
        raise WorkerError(f"cannot read the task file: {error}") from error
    result = execute_run(
        mode=args.mode, task=task, cwd=cwd, model=args.model, effort=args.effort,
        credits=args.max_ai_credits, timeout=args.timeout,
    )
    print_summary(result)
    return 0 if result["status"] == "completed" else 1


def cmd_clean(args: argparse.Namespace, cwd: Path) -> int:
    run_id = args.run_id
    if not RUN_ID_PATTERN.match(run_id):
        raise WorkerError(f"not a run ID: {run_id!r}")
    result_path = state_home() / "runs" / run_id / "result.json"
    if not result_path.exists():
        raise WorkerError(f"no such run: {run_id}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result["mode"] != "implement":
        print(f"{run_id}: read-only run, nothing to clean")
        return 0
    # Build both names from the validated run ID, never from the stored result.
    root = Path(result["repoRoot"])
    workspace = state_home() / "worktrees" / f"{root.name}-{run_id}"
    branch = f"copilot/{run_id}"
    if workspace.exists():
        try:
            git(["worktree", "remove", "--force", str(workspace)], root)
        except WorkerError:
            # Git refuses a worktree it no longer recognizes; the path is ours, so remove it.
            shutil.rmtree(workspace, ignore_errors=True)
    git(["worktree", "prune"], root)
    if git(["branch", "--list", branch], root):
        git(["branch", "-D", branch], root)
    print(f"{run_id}: removed worktree and branch {branch}")
    return 0


def cmd_check(args: argparse.Namespace, cwd: Path) -> int:
    ok = True
    version = copilot_version()
    if version == "unknown":
        print("copilot sdk: NOT AVAILABLE; run this script with `uv run`")
        ok = False
    else:
        print(f"copilot sdk: {version}")
        pins_ok, pins_line = pins_status()
        print(f"pins: {pins_line}")
        ok = ok and pins_ok
    try:
        print(f"repository: {repo_root(cwd)}")
    except WorkerError:
        print("repository: NOT A GIT REPOSITORY")
        ok = False
    if not ok or not args.live:
        return 0 if ok else 1
    for model in sorted(set(DEFAULT_MODELS.values())):
        result = execute_run(
            mode="research", task="Reply with the single word: ok", cwd=cwd,
            model=model, timeout=120,
        )
        passed = result["status"] == "completed"
        print(f"model {model}: {'ok' if passed else result['status']} ({result['runDir']})")
        ok = ok and passed
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run one delegation and exit")
    run.add_argument("--mode", required=True, choices=MODES)
    run.add_argument("--task-file", required=True)
    run.add_argument("--model")
    run.add_argument("--effort", choices=EFFORTS)
    run.add_argument("--max-ai-credits", type=int)
    run.add_argument("--timeout", type=int)
    run.set_defaults(handler=cmd_run)
    clean = commands.add_parser("clean", help="remove a run's worktree and branch")
    clean.add_argument("run_id")
    clean.set_defaults(handler=cmd_clean)
    check = commands.add_parser("check", help="verify the Copilot SDK and repository")
    check.add_argument("--live", action="store_true", help="also probe each default model")
    check.set_defaults(handler=cmd_check)
    return parser


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    # A hangup of the caller's terminal must not end a run.
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args, cwd or Path.cwd())
    except WorkerError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

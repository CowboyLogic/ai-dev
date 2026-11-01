#!/usr/bin/env python3
# Every dependency is pinned exactly, the SDK's own included, so that a new release of
# any of them cannot change what runs. To upgrade, follow references/upgrading.md.
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "annotated-types==0.8.0",
#     "anyio==4.15.1",
#     "certifi==2026.10.23",
#     "github-copilot-sdk==1.0.28",
#     "h11==0.16.0",
#     "httpcore==1.0.9",
#     "httpx==0.28.1",
#     "idna==3.20",
#     "pydantic==2.14.1",
#     "pydantic-core==2.50.1",
#     "python-dateutil==3.0.0",
#     "six==1.17.0",
#     "typing-extensions==4.16.0",
#     "typing-inspection==0.4.4",
#     "tzdata==2026.5",
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
# Each profile fixes one model and one reasoning effort.
# They are ordered cheapest first: a retry moves exactly one step up this order.
PROFILES: dict[str, dict[str, str | None]] = {
    "light": {"model": "gpt-6-luna", "effort": "medium"},
    "standard": {"model": "gpt-6.1-terra", "effort": "medium"},
    "deep": {"model": "gpt-6.1-sol", "effort": "medium"},
    "heavy": {"model": "gpt-6-astra", "effort": "medium"},
}
# review defaults to a different model from implement, so worker-written code is not
# reviewed by the model that wrote it.
DEFAULT_PROFILES = {"research": "light", "review": "deep", "implement": "standard"}
# A run that fails verification may be retried one profile up at most this many times.
MAX_RETRIES = 2
DEFAULT_CREDITS = {"research": 30, "review": 30, "implement": 60}
DEFAULT_TIMEOUTS = {"research": 600, "review": 600, "implement": 1800}
# The reasoning efforts a run may use. The SDK also accepts "max"; the worker caps at xhigh.
EFFORTS = ("low", "medium", "high", "xhigh")
RUN_ID_PATTERN = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}$")
# Keeps an attached review diff to a size the worker can read alongside the files.
MAX_DIFF_BYTES = 100_000
MIN_CREDITS = 30
KILL_GRACE_SECONDS = 10
# On Windows a blocking wait keeps a signal handler from running until it returns, so the
# supervisor waits in slices of this length to stay responsive to Ctrl+C and Ctrl+Break.
WAIT_SLICE_SECONDS = 0.5
WINDOWS = os.name == "nt"
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


class _ProcessGroup:
    """POSIX containment: the worker leads its own session and process group."""

    popen_options: dict[str, Any] = {"start_new_session": True}

    def started(self, process: subprocess.Popen[bytes]) -> None:
        pass

    def stop(self, process: subprocess.Popen[bytes]) -> None:
        """SIGTERM the worker's process group, then SIGKILL whatever is left of it."""
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=KILL_GRACE_SECONDS)
        except (ProcessLookupError, PermissionError, subprocess.TimeoutExpired):
            pass
        # The leader exiting does not mean the group is gone: a child may ignore SIGTERM.
        self.kill_rest(process)
        process.wait()

    def kill_rest(self, process: subprocess.Popen[bytes]) -> None:
        # Reaches the worker's own process group only. A process that moved to a new session
        # is not contained; SKILL.md states that limit.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    def close(self) -> None:
        pass


class _JobObject:
    """Windows containment: a job object holds the worker and every process it starts.

    The worker starts suspended and resumes only once it is in the job, so nothing it
    starts runs outside it. Closing the job kills whatever is left in it, so the worker
    also ends when the supervisor itself is killed. Windows has no SIGTERM to send first:
    stopping a run ends every process in the job at once.
    """

    _CREATE_SUSPENDED = 0x00000004
    _CREATE_NO_WINDOW = 0x08000000
    _EXTENDED_LIMIT_INFORMATION = 9
    _KILL_ON_JOB_CLOSE = 0x00002000
    # PROCESS_SET_QUOTA | PROCESS_TERMINATE | PROCESS_SUSPEND_RESUME
    _PROCESS_ACCESS = 0x0100 | 0x0001 | 0x0800
    # A hidden console of its own: Ctrl+C in the caller's console does not reach the worker.
    popen_options: dict[str, Any] = {"creationflags": _CREATE_SUSPENDED | _CREATE_NO_WINDOW}

    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes

        class BasicLimits(ctypes.Structure):
            _fields_ = [
                ("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                ("SchedulingClass", wintypes.DWORD),
            ]

        class ExtendedLimits(ctypes.Structure):
            _fields_ = [
                ("BasicLimitInformation", BasicLimits), ("IoInfo", ctypes.c_uint64 * 6),
                ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t),
            ]

        self._ctypes = ctypes
        self._kernel32 = kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._ntdll = ctypes.WinDLL("ntdll")
        kernel32.CreateJobObjectW.restype = wintypes.HANDLE
        kernel32.OpenProcess.restype = wintypes.HANDLE
        self._handle = kernel32.CreateJobObjectW(None, None)
        if not self._handle:
            raise ctypes.WinError(ctypes.get_last_error())
        limits = ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = self._KILL_ON_JOB_CLOSE
        if not kernel32.SetInformationJobObject(
            ctypes.c_void_p(self._handle), self._EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits), ctypes.sizeof(limits),
        ):
            error = ctypes.WinError(ctypes.get_last_error())
            self.close()
            raise error

    def started(self, process: subprocess.Popen[bytes]) -> None:
        ctypes, kernel32 = self._ctypes, self._kernel32
        handle = kernel32.OpenProcess(self._PROCESS_ACCESS, False, process.pid)
        try:
            error: OSError | None = None
            if not handle or not kernel32.AssignProcessToJobObject(
                ctypes.c_void_p(self._handle), ctypes.c_void_p(handle)
            ):
                error = ctypes.WinError(ctypes.get_last_error())
            elif self._ntdll.NtResumeProcess(ctypes.c_void_p(handle)) != 0:
                error = OSError("could not resume the worker process")
            if error is not None:
                # Never let an uncontained worker run. It is still suspended, so end it.
                process.kill()
                process.wait()
                raise error
        finally:
            if handle:
                kernel32.CloseHandle(ctypes.c_void_p(handle))

    def stop(self, process: subprocess.Popen[bytes]) -> None:
        self.kill_rest(process)
        # A stop can land before started() put the still-suspended worker in the job; the
        # job does not hold it then, so end it directly or the wait never returns.
        if process.poll() is None:
            process.kill()
        process.wait()

    def kill_rest(self, process: subprocess.Popen[bytes]) -> None:
        if self._handle:
            self._kernel32.TerminateJobObject(self._ctypes.c_void_p(self._handle), 1)

    def close(self) -> None:
        if self._handle:
            self._kernel32.CloseHandle(self._ctypes.c_void_p(self._handle))
            self._handle = None


def _containment() -> _ProcessGroup | _JobObject:
    return _JobObject() if WINDOWS else _ProcessGroup()


def _stop_signals() -> tuple[int, ...]:
    # SIGBREAK is Ctrl+Break, the stop signal a Windows console process can catch.
    return (signal.SIGTERM, signal.SIGINT, *([signal.SIGBREAK] if hasattr(signal, "SIGBREAK") else []))


def _wait(process: subprocess.Popen[bytes], timeout: float) -> int:
    """process.wait(timeout), in slices so that a signal handler can run between them."""
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        try:
            return process.wait(timeout=max(0.0, min(WAIT_SLICE_SECONDS, remaining)))
        except subprocess.TimeoutExpired:
            if remaining <= WAIT_SLICE_SECONDS:
                raise


def run_engine(command: list[str], run_dir: Path, timeout: int) -> tuple[int | None, str]:
    """Run the worker to completion. Return (exit code, termination reason)."""

    def on_signal(signum: int, _frame: Any) -> None:
        raise _Terminated(signum)

    def stop_worker() -> None:
        # A second signal during the kill must not abort it and lose the result.
        for name in previous:
            signal.signal(name, signal.SIG_IGN)
        if process is not None:
            container.stop(process)

    process: subprocess.Popen[bytes] | None = None
    container = _containment()
    previous = {name: signal.signal(name, on_signal) for name in _stop_signals()}
    try:
        with open(run_dir / "stderr.log", "wb") as log:
            # Own session (a job, on Windows) and no stdin: the worker outlives the caller's
            # connection. The engine reads its task from task.md, so it never appears in
            # the process list.
            process = subprocess.Popen(
                command, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                **container.popen_options,
            )
            container.started(process)
            code = _wait(process, timeout)
            # Anything the worker left running must not outlive the run it belongs to.
            container.kill_rest(process)
        return (code, "exit") if code >= 0 else (None, f"signal:{-code}")
    except subprocess.TimeoutExpired:
        stop_worker()
        return None, "timeout"
    except _Terminated as stop:
        stop_worker()
        return None, f"signal:{stop.signum}"
    finally:
        container.close()
        for name, handler in previous.items():
            signal.signal(name, handler)


def execute_run(
    *,
    mode: str,
    task: str,
    cwd: Path,
    profile: str | None = None,
    reason: str | None = None,
    retry_of: str | None = None,
    model: str | None = None,
    effort: str | None = None,
    credits: int | None = None,
    timeout: int | None = None,
) -> dict[str, Any]:
    if mode not in MODES:
        raise WorkerError(f"unknown mode: {mode}")
    if not task.strip():
        raise WorkerError("the task is empty")
    if effort == "max":
        raise WorkerError("effort max is not allowed; the highest effort a run may use is xhigh")
    if effort is not None and effort not in EFFORTS:
        raise WorkerError(f"unknown effort: {effort}")
    justification = reason.strip() if reason else None
    profile, attempt = resolve_profile(mode, profile, retry_of)
    default_profile = DEFAULT_PROFILES[mode]
    off_default = profile != default_profile or model is not None or effort is not None
    if off_default and not justification:
        raise WorkerError(
            f"this run is off the {mode} default profile ({default_profile}); "
            "pass --reason to say why"
        )
    model = model or PROFILES[profile]["model"]
    effort = effort if effort is not None else PROFILES[profile]["effort"]
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
    # Windows ignores these mode bits; there the directory keeps the ACL it inherits.
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
        "profile": profile,
        "defaultProfile": default_profile,
        "reason": justification,
        "attempt": attempt,
        "retryOf": retry_of,
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


def resolve_profile(mode: str, profile: str | None, retry_of: str | None) -> tuple[str, int]:
    """Return the profile a run uses and its attempt number (1 for a first run)."""
    if profile is not None and profile not in PROFILES:
        raise WorkerError(f"unknown profile: {profile}")
    if retry_of is None:
        return profile or DEFAULT_PROFILES[mode], 1
    if profile is not None:
        raise WorkerError("--retry-of picks the next profile itself; do not pass --profile with it")
    previous = load_result(retry_of)
    if previous.get("mode") != mode:
        raise WorkerError(f"run {retry_of} was a {previous.get('mode')} run, not {mode}")
    attempt = int(previous.get("attempt") or 1) + 1
    if attempt > MAX_RETRIES + 1:
        raise WorkerError(
            f"run {retry_of} was already retried {MAX_RETRIES} times; do the work yourself"
        )
    order = list(PROFILES)
    if previous.get("profile") not in order:
        raise WorkerError(f"run {retry_of} has no profile to step up from")
    index = order.index(previous["profile"]) + 1
    if index == len(order):
        raise WorkerError(f"run {retry_of} used {order[-1]}, the top profile; do the work yourself")
    return order[index], attempt


def load_result(run_id: str) -> dict[str, Any]:
    if not RUN_ID_PATTERN.match(run_id):
        raise WorkerError(f"not a run ID: {run_id!r}")
    result_path = state_home() / "runs" / run_id / "result.json"
    if not result_path.exists():
        raise WorkerError(f"no such run: {run_id}")
    return json.loads(result_path.read_text(encoding="utf-8"))


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
    print(f"profile: {result['profile']} (attempt {result['attempt']})")
    print(f"model: {result['model']} (effort {result['effort'] or 'model default'})")
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
        mode=args.mode, task=task, cwd=cwd, profile=args.profile, reason=args.reason,
        retry_of=args.retry_of, model=args.model, effort=args.effort,
        credits=args.max_ai_credits, timeout=args.timeout,
    )
    print_summary(result)
    return 0 if result["status"] == "completed" else 1


def cmd_clean(args: argparse.Namespace, cwd: Path) -> int:
    run_id = args.run_id
    result = load_result(run_id)
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
    models, problem = available_models()
    if models is None:
        print(f"models: could not list them: {problem}")
        return 1
    for name in PROFILES:
        problem = profile_problem(name, models)
        print(f"profile {name} ({describe_profile(name)}): {problem or 'offered'}")
        ok = ok and problem is None
    if not ok:
        # Probing a profile the catalog does not offer only spends credits on a failure.
        return 1
    for name in PROFILES:
        result = execute_run(
            mode="research", task="Reply with the single word: ok", cwd=cwd,
            profile=name, reason="check --live probe", timeout=120,
        )
        passed = result["status"] == "completed"
        print(f"probe {name}: {'ok' if passed else result['status']} ({result['runDir']})")
        ok = ok and passed
    return 0 if ok else 1


def describe_profile(name: str) -> str:
    profile = PROFILES[name]
    return f"{profile['model']}, effort {profile['effort'] or 'model default'}"


def available_models() -> tuple[dict[str, dict[str, Any]] | None, str]:
    """Ask the engine for the models this login offers. Return (models by ID, problem)."""
    home = state_home() / "copilot-home"
    home.mkdir(parents=True, exist_ok=True)
    try:
        done = subprocess.run(
            [*engine_base(), "--list-models", str(home)], capture_output=True, text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, str(error)
    if done.returncode != 0:
        lines = (done.stderr or done.stdout).strip().splitlines()
        return None, lines[-1] if lines else f"the engine exited {done.returncode}"
    try:
        return {model["id"]: model for model in json.loads(done.stdout)}, ""
    except (ValueError, KeyError, TypeError) as error:
        return None, f"unreadable model list: {error}"


def profile_problem(name: str, models: dict[str, dict[str, Any]]) -> str | None:
    """Say why the model catalog cannot serve a profile, or None when it can."""
    profile = PROFILES[name]
    model = models.get(profile["model"])
    if model is None:
        return f"NOT OFFERED: no model {profile['model']}"
    supported = model.get("supportedReasoningEfforts") or []
    if profile["effort"] is not None and profile["effort"] not in supported:
        listed = ", ".join(supported) or "none"
        return f"NOT OFFERED: {profile['model']} does not support effort {profile['effort']} (supports: {listed})"
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="run one delegation and exit")
    run.add_argument("--mode", required=True, choices=MODES)
    run.add_argument("--task-file", required=True)
    run.add_argument("--profile", choices=tuple(PROFILES), help="default: the mode's profile")
    run.add_argument("--reason", help="why this run is off its mode's default profile")
    run.add_argument("--retry-of", metavar="RUN_ID", help="retry that run one profile up")
    run.add_argument("--model", help="override the profile's model, only when the user names one")
    # Not choices=: an argparse rejection would not say why max is refused.
    run.add_argument("--effort", help="override the profile's effort, only when the user names one")
    run.add_argument("--max-ai-credits", type=int)
    run.add_argument("--timeout", type=int)
    run.set_defaults(handler=cmd_run)
    clean = commands.add_parser("clean", help="remove a run's worktree and branch")
    clean.add_argument("run_id")
    clean.set_defaults(handler=cmd_clean)
    check = commands.add_parser("check", help="verify the Copilot SDK and repository")
    check.add_argument("--live", action="store_true", help="also check and probe each profile")
    check.set_defaults(handler=cmd_check)
    return parser


def main(argv: list[str] | None = None, cwd: Path | None = None) -> int:
    # A hangup of the caller's terminal must not end a run. Windows has no SIGHUP.
    if hasattr(signal, "SIGHUP"):
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args, cwd or Path.cwd())
    except WorkerError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

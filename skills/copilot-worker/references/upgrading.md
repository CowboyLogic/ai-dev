# Upgrading the Copilot SDK and runtime

The worker is pinned to one GitHub Copilot SDK and the one Copilot runtime that SDK
carries. Upgrading either is a deliberate change made with this procedure, never a side
effect of running the script.

## What is pinned, and where

| What | Where |
| --- | --- |
| The SDK version | `pins.json` (`sdk`) and the `github-copilot-sdk==` line in the header of `scripts/copilot_worker.py` |
| The runtime version | `pins.json` (`runtime`). Each SDK release carries its own runtime and downloads it, checked against published checksums, so the two always move together |
| Every package the SDK needs | The same header, each at an exact `==` version |

The header lists the whole dependency set, not only the SDK, because the SDK's own
requirements are loose ranges (`pydantic>=2.0`, `httpx>=0.24`) that would otherwise float.

> [!NOTE]
> A lockfile (`uv lock --script`) was tried and rejected. It records the `exclude-newer`
> setting and package index of the machine that made it, and `uv run` ignores it and
> re-resolves when the user's configuration differs. Exact pins in the header behave the
> same on every machine and mirror.

## What enforces the pins

- The engine refuses to start a worker when the installed SDK or runtime differs from
  `pins.json`. The run ends `failed`, and `stderr.log` names the difference.
- `check` prints a `pins:` line and fails on a mismatch.
- The unit and contract tests run in CI against an environment built from the header, and
  fail when the header, `pins.json`, the installed SDK, or the SDK's dependency set disagree.

## Upgrade procedure

1. **Pick the SDK version** and read its release notes. Look for changes to permission
   handling, session options, event types, and the names of the runtime's built-in tools.
2. **Find its runtime and its dependency set:**

   ```bash
   uv run --no-project --no-config --with github-copilot-sdk==NEW \
     python -c "from copilot._cli_version import CLI_VERSION; print(CLI_VERSION)"
   echo "github-copilot-sdk==NEW" | uv pip compile - --no-config --no-header --no-annotate
   ```

3. **Update the header** in `scripts/copilot_worker.py` with the compiled list, and
   `pins.json` with the new `sdk` and `runtime`.
4. **Run the tests** from the repository root, in the environment the header describes:

   ```bash
   python - > /tmp/copilot-worker-requirements.txt <<'PY'
   import pathlib, re
   header = pathlib.Path("skills/copilot-worker/scripts/copilot_worker.py").read_text().split("# ///", 2)[1]
   print("\n".join(re.findall(r'^#\s+"([^"]+)",?$', header, re.MULTILINE)))
   PY
   REQUIRE_SDK_CONTRACT=1 uv run --no-project --with-requirements /tmp/copilot-worker-requirements.txt \
     python -m unittest discover -s skills/copilot-worker/scripts -v
   ```

   A failing contract test names the SDK option, class, or field that moved. Change the
   engine to match, and do not loosen the test.
5. **Check what the tests cannot see.** The SDK does not validate tool names, so a renamed
   runtime tool shows up only as a worker without that tool. Run the live check, then one
   `implement` task that runs a shell command, and read `permissions.jsonl` and
   `events.jsonl` for anything unexpected:

   ```bash
   uv run skills/copilot-worker/scripts/copilot_worker.py check --live
   ```

6. **Update the documentation** that mentions behavior the upgrade changed, and say in the
   pull request which SDK and runtime versions moved.

## What the contract tests do not cover

- Whether the runtime still offers the built-in tools in `TOOLS` under the same names.
- How the runtime behaves: permission prompts, shell handling, and the content of events.
- Event shapes beyond the fields the engine reads. A parser built on `events.jsonl` needs
  its own tests when it exists.

## Housekeeping

The SDK keeps each runtime it has downloaded in its cache directory (on macOS,
`~/Library/Caches/github-copilot-sdk/cli/`). Old versions stay there unused after an
upgrade and can be deleted.

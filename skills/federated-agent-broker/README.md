# Federated agent broker

Use GitHub Copilot CLI as a bounded worker from Claude Code. The local MCP server
offers read-only research and review first, then a narrowly scoped implementation
mode when you explicitly name the only files Copilot can change.

The broker uses the Copilot CLI session already authenticated on your machine. It
does not send an API key to Claude Code, start a background service, or store task
transcripts. Copilot subscription limits and premium-request rules still apply.

## Prerequisites

- Python 3.10 or later.
- GitHub Copilot CLI installed and authenticated. Confirm it with `copilot --version`.
- Claude Code installed.
- A local checkout containing this skill.

## Add the broker to Claude Code

1. Set `BROKER_ROOT` to the directory that contains this skill.

   ```bash
   BROKER_ROOT="/absolute/path/to/ai-dev/skills/federated-agent-broker"
   ```

2. Add the local stdio MCP server at user scope.

   ```bash
   claude mcp add --scope user --transport stdio federated-agent-broker -- \
     python3 "$BROKER_ROOT/scripts/copilot_broker.py"
   ```

3. Start a new Claude Code session and run `/mcp`. The server should expose
   `copilot_research`, `copilot_review`, `copilot_implement`, and `broker_status`.

The command stores the resolved script path in Claude Code's user configuration. To
remove it later, run `claude mcp remove federated-agent-broker`.

## Use the broker

Ask Claude to use a named broker tool and include a bounded objective. For example:

```text
Use copilot_research to inspect the failing tests in packages/api. Do not change files.
Report the likely root cause, relevant paths, smallest safe fix, and tests to run.
Use max_ai_credits 1.
```

For a review, ask Claude to call `copilot_review`. It can attach the current working
tree diff, clipped to 40,000 characters, and still gives Copilot read-only access.

For implementation, provide exact files rather than a directory:

```text
Use copilot_implement to add the missing validation described in the task.
It may modify only src/validation.ts and tests/validation.test.ts.
It may run npm test. Use max_ai_credits 2.
Afterward, inspect the receipt and verify the diff yourself.
```

The broker does not commit, push, create pull requests, install dependencies, or
allow arbitrary shell commands. Use an isolated Git worktree for substantial changes.

## Configure defaults

Set `FEDERATED_BROKER_COPILOT_MODEL` in the environment that starts Claude Code to
choose a default Copilot model. Per-tool `model` values override it. The broker
defaults to `auto` and one Copilot AI credit per delegation.

For development tests only, set `FEDERATED_BROKER_COPILOT_BIN` to an alternate
Copilot executable. Do not use it to bypass Copilot authentication or subscription
rules.

## Verify the artifact

Run the broker's unit tests without invoking a model:

```bash
python3 scripts/test_copilot_broker.py
```

See [delegation-contract.md](references/delegation-contract.md) for the complete
tool contract and receipt format.

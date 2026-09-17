# Federated agent broker

Use GitHub Copilot CLI as a bounded worker from Claude Code. The local MCP server
offers read-only research and review first, then a narrowly scoped implementation
mode when you explicitly name the only files Copilot can change.

The broker uses the Copilot CLI session already authenticated on your machine. It
does not send an API key to Claude Code, start a background service, or store task
transcripts. Copilot subscription limits and premium-request rules still apply.

## Prerequisites

- Python 3.10 or later on macOS or Linux. Implementation mode requires POSIX file
  locks and process groups; read-only modes have the same tested platform support.
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
Use max_ai_credits 2. Afterward, inspect the receipt, then run npm test yourself.
```

The broker does not commit, push, create pull requests, install dependencies, or
allow shell commands. Use an isolated Git worktree for substantial changes.

## Configure delegation profiles

Profiles tell Claude which Copilot model, thinking effort, context tier, credit
ceiling, and timeout to use for each kind of delegation. Copy the included example
to a private user configuration directory, then replace `auto` with models available
to your Copilot subscription when you want deterministic routing.

```bash
BROKER_CONFIG_DIR="/absolute/path/to/your/config/federated-agent-broker"
mkdir -p "$BROKER_CONFIG_DIR"
cp "$BROKER_ROOT/references/policy.example.json" \
  "$BROKER_CONFIG_DIR/policy.json"
```

Set the policy path in the environment that launches Claude Code:

```bash
export FEDERATED_BROKER_POLICY="$BROKER_CONFIG_DIR/policy.json"
```

Restart Claude Code, call `broker_status`, and verify the reported profile names and
values. Claude then selects semantic profiles such as `economy`, `review`, or
`implementation` instead of inventing model settings. A tool call can still override
`model`, `effort`, `context`, `max_ai_credits`, or `timeout_seconds` for an exceptional
task.

Without a policy file, the broker uses built-in profiles: `research`, `review`, and
`implementation`. They retain the original conservative defaults: model `auto`, one
credit, default context, and low effort for read-only work or medium effort for writes.
`FEDERATED_BROKER_COPILOT_MODEL` changes the built-in profiles' model only.

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

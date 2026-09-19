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

## Run the setup script

Run the included script to create a private policy and register the local MCP server
with Claude Code at user scope:

```bash
BROKER_ROOT="/absolute/path/to/ai-dev/skills/federated-agent-broker"
"$BROKER_ROOT/scripts/setup.sh"
```

By default, the script creates `~/.config/federated-agent-broker/policy.json` from
the included template. It registers the broker with that exact policy path in its MCP
environment, so you do not need to export `FEDERATED_BROKER_POLICY` from every shell
that starts Claude Code. It never overwrites an existing policy file or an existing
MCP entry named `federated-agent-broker`.

Use `--config-dir PATH` to store the policy elsewhere. If the MCP entry already
exists and you want the script to replace it, pass `--replace`. Use `--skip-mcp` to
create only the policy file. Run `"$BROKER_ROOT/scripts/setup.sh" --help` for all
options.

## Add the broker to Claude Code

Use these manual instructions if you do not use the setup script.

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
Use max_ai_credits 30.
```

For a review, ask Claude to call `copilot_review`. It can attach the current working
tree diff, clipped to 40,000 characters, and still gives Copilot read-only access.

For implementation, provide exact files rather than a directory:

```text
Use copilot_implement to add the missing validation described in the task.
It may modify only src/validation.ts and tests/validation.test.ts.
Use max_ai_credits 30. Afterward, inspect the receipt, then run npm test yourself.
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

Set the policy path in the environment that launches Claude Code when you use the
manual installation method:

```bash
export FEDERATED_BROKER_POLICY="$BROKER_CONFIG_DIR/policy.json"
```

Restart Claude Code, call `broker_status`, and verify the reported profile names and
values. Claude then selects semantic profiles such as `economy`, `review`, or
`implementation` instead of inventing model settings. A tool call can still override
`model`, `effort`, `context`, `max_ai_credits`, or `timeout_seconds` for an exceptional
task.

Copilot CLI requires `maxAiCredits` and `max_ai_credits` to be at least `30`. This is
a soft cap per response, not a 30-credit reservation. The broker rejects lower values
before invoking Copilot so a bad policy or per-call override fails clearly.

### Select Copilot models

Set `model` to a Copilot CLI model identifier, not the display name shown in a model
picker. The broker passes the value unchanged to `copilot --model`. For example, the
display name **GPT-5.6 Luna** uses the identifier `gpt-5.6-luna`.

Open an interactive Copilot CLI session and run `/model` to see the identifiers
available to your authenticated account. Copy the identifier shown there: available
models vary by Copilot plan, organization policy, and CLI version. `broker_status`
confirms that the policy parses, but an actual delegation is the only confirmation
that Copilot will grant access to a pinned model.

The following is a cost-aware starting point when your Copilot account exposes the
GPT-5.6 family. Keep the shipped policy example on `auto` if you want Copilot to
route dynamically instead.

```json
{
  "defaultProfile": "economy",
  "modeProfiles": {
    "research": "economy",
    "review": "review",
    "implement": "implementation"
  },
  "profiles": {
    "economy": {
      "model": "gpt-5.6-luna",
      "effort": "low",
      "context": "default",
      "maxAiCredits": 30,
      "timeoutSeconds": 180
    },
    "review": {
      "model": "gpt-5.6-sol",
      "effort": "medium",
      "context": "default",
      "maxAiCredits": 30,
      "timeoutSeconds": 300
    },
    "implementation": {
      "model": "gpt-5.6-terra",
      "effort": "medium",
      "context": "default",
      "maxAiCredits": 30,
      "timeoutSeconds": 300
    }
  }
}
```

This routes small, repetitive work to Luna; routine coding and bounded changes to
Terra; and complex review or diagnosis to Sol. Use the exact identifiers from `/model`
if your subscription presents a different set.

### Select thinking effort and context

The broker accepts these `effort` values: `none`, `minimal`, `low`, `medium`, `high`,
`xhigh`, and `max`. It passes the selected value to Copilot as `--effort`. Start with
`low` for reconnaissance, `medium` for routine reviews and small changes, and reserve
`high` or above for a deliberate complex analysis. Copilot determines which effort
levels the selected model actually supports.

The broker accepts two `context` values: `default` and `long_context`. `default` is
the normal context window and should be the routine choice. `long_context` requests
Copilot CLI's extended context tier for large-repository or long-running work when
the selected model supports it. Higher effort and extended context can consume more
Copilot AI credits, so raise one setting at a time and retain an appropriate
`maxAiCredits` ceiling. Copilot CLI requires a minimum cap of `30`; that value permits
up to 30 credits rather than reserving or automatically consuming 30 credits.

Without a policy file, the broker uses built-in profiles: `research`, `review`, and
`implementation`. They use model `auto`, Copilot's minimum 30-credit soft cap,
default context, and low effort for read-only work or medium effort for writes.
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

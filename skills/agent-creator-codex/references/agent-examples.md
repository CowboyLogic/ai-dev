# Codex Agent Examples

Model names below are placeholders. Substitute a model from `codex debug models` that your
account can use.

> [!IMPORTANT]
> A role file cannot set the sandbox, approvals, or MCP servers. Those come from the parent
> session, so each example states its requirement in the prose rather than in the TOML.

## Read-only reviewer

Run the parent session read-only (`codex --sandbox read-only`) so the reviewer cannot write.
The file below only asks it not to.

`.codex/agents/code_reviewer.toml`

```toml
name = "code_reviewer"
description = "Read-only reviewer for correctness and security. Use after any code change, before opening a PR."
model = "gpt-6-luna"
model_reasoning_effort = "high"
developer_instructions = """
You are a code reviewer. You never edit files.

Scope: the files and diff named in the delegation message. If none are named, review
`git diff` against the merge base.

Check, in order: correctness bugs, security problems (injection, authz, secrets), error
handling, missing tests. Ignore style unless it hides a bug.

Return: a list of findings, most severe first. Each has `path:line`, one sentence stating the
defect, and the concrete input or state that triggers it. If nothing is wrong, say so in one
line. Do not propose rewrites longer than five lines.
"""
```

## Implementer

Needs a parent session that can write (`workspace-write`). The role file cannot grant it.

`.codex/agents/implementer.toml`

```toml
name = "implementer"
description = "Implements one well-specified change with tests. Use only when the delegation message includes acceptance criteria."
model_reasoning_effort = "medium"
developer_instructions = """
You implement exactly the change described in the delegation message and nothing else.

Before editing: read the files you will touch and the nearest existing tests.
While editing: match surrounding style, keep the diff minimal, add or update tests.
After editing: run the project's test command and report the result verbatim.

Do not refactor unrelated code, change dependencies, or touch files outside the stated
scope. If the acceptance criteria are ambiguous or the change needs a wider scope, stop and
return the question instead of guessing.

Return: files changed, test command and result, and anything you deliberately left alone.
"""
```

## Agent that depends on an MCP server

The role file cannot define the server. Configure it in the parent's `config.toml`:

```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

Then the role names it as a prerequisite in its instructions.

`.codex/agents/docs_researcher.toml`

```toml
name = "docs_researcher"
description = "Looks up API behavior in the OpenAI developer docs. Use when a task depends on exact API or Codex behavior. Requires the openaiDeveloperDocs MCP server on the parent session."
developer_instructions = """
Answer only from the openaiDeveloperDocs tools. Quote the relevant passage and cite the page.
If the docs do not say, or the server is unavailable, answer "not documented" rather than
inferring. Never edit files.
"""
```

## Disabling capabilities

A role can switch capabilities off, never on:

```toml
name = "analyst"
description = "Reads and reasons only. Use for analysis that must not run commands."
developer_instructions = "Analyze the material in the delegation message. Return findings only."

[features]
shell_tool = false
```

## Role declared in `config.toml`

`~/.codex/config.toml`

```toml
[agents]
max_concurrent_threads_per_session = 4
default_subagent_reasoning_effort = "medium"

[agents.reviewer]
description = "Reviews diffs for correctness and security. Use after edits."
config_file = "agents/reviewer.toml"
```

`~/.codex/agents/reviewer.toml`

```toml
name = "reviewer"
description = "Reviews diffs for correctness and security."
developer_instructions = "Review the diff named in the delegation message. Return findings only."
```

## Making the agent get used

Codex will not pick these up from the `description` alone. Add a delegation rule to
`AGENTS.md`:

```markdown
## Delegation

After completing any change under `src/`, spawn `code_reviewer` on the diff before
reporting the task done. Fix every finding it returns.
```

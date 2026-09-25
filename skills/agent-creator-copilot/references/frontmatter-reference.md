# Frontmatter Reference — Custom Agent Profiles

Reference for the YAML frontmatter properties in custom agent profiles (`.agent.md`). Load this file when writing or modifying agent frontmatter.

**Sources (last verified September 2026):**

- GitHub configuration reference: <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- VS Code: <https://code.visualstudio.com/docs/agent-customization/custom-agents>
- VS Code subagents: <https://code.visualstudio.com/docs/agents/run/subagents>
- VS Code hooks: <https://code.visualstudio.com/docs/agent-customization/hooks>
- Copilot CLI: <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#custom-agents-reference>
- Models: <https://docs.github.com/en/copilot/reference/ai-models/supported-models>

---

## Surfaces

Custom agents are used by several products that each read the profile differently:

- **Copilot cloud agent on GitHub.com**: agents tab/panel, issue assignment, pull requests
- **GitHub Copilot CLI**: `/agent`, `--agent`, or inferred delegation to a subagent
- **VS Code** (and JetBrains IDEs, Eclipse, Xcode, which are in public preview for custom agents): the agents dropdown in chat. VS Code has several harnesses (**Local**, **Copilot**, Claude, Codex, Cloud); some properties only work with **Local**.

Every surface ignores tool names it does not recognize, and GitHub.com explicitly ignores the IDE-only `argument-hint` and `handoffs` properties.

---

## Platform Compatibility Overview

| Property | VS Code / IDEs | GitHub.com cloud agent | Copilot CLI |
|---|---|---|---|
| `name` | ✅ | ✅ | ✅ |
| `description` | ✅ (header optional) | ✅ **Required** | ✅ **Required** |
| `target` | ✅ | ✅ | Not listed in CLI reference |
| `tools` | ✅ (aliases, tool sets, tool names) | ✅ (aliases, MCP tools) | ✅ |
| `model` | ✅ string or array | ⚠️ See [`model`](#model) | ✅ string |
| `user-invocable` | ✅ | ✅ | Not listed in CLI reference |
| `disable-model-invocation` | ✅ (blocks subagent use) | ✅ (blocks auto-selection) | Not listed in CLI reference |
| `infer` | Deprecated | Retired | ✅ Listed as active (see [`infer`](#infer-retired--deprecated)) |
| `argument-hint` | ✅ | ❌ Ignored | Not listed |
| `handoffs` | ✅ | ❌ Ignored | Not listed |
| `agents` | ✅ | Not listed | Not listed |
| `hooks` | ✅ Preview, Local harness only | Not listed | Not listed |
| `mcp-servers` | ❌ Not used (only passed through for `target: github-copilot`) | ✅ | ✅ |
| `metadata` | ❌ Not used | ✅ | Not listed |
| `include-custom-instructions` | Not listed | Not listed | ✅ |
| `models` | Not listed | Not listed | ✅ |
| `modelPolicy` | Not listed | Not listed | ✅ |
| `reasoningEffort` | Not listed | Not listed | ✅ |

"Not listed" means the surface's docs do not mention the property. It will most likely be ignored, but that is not documented.

> [!NOTE]
> The GitHub configuration reference states its property table applies to "GitHub.com, the Copilot CLI, and supported IDEs (unless otherwise noted)", yet the CLI's own frontmatter table omits `target`, `user-invocable`, `disable-model-invocation`, and `metadata`. Treat those as unverified in the CLI.

---

## All Properties at a Glance

```yaml
---
name: my-agent                        # display name; defaults to filename
description: What this agent does     # required on GitHub.com and CLI
target: vscode                        # vscode | github-copilot | omit for both
tools: ["read", "search"]             # omit = all tools
model: Claude Sonnet 5                # string, or array in VS Code
user-invocable: true                  # show in agent picker (default true)
disable-model-invocation: false       # block auto-selection / subagent use (default false)
argument-hint: Paste your spec here   # VS Code / IDEs only
agents: ["Researcher", "Reviewer"]    # VS Code only: allowed subagents
handoffs:                             # VS Code / IDEs only
  - label: Implement
    agent: implementation
    prompt: Implement the plan above.
    send: false
    model: GPT-5.5 (copilot)
hooks:                                # VS Code Local harness only (Preview)
  PostToolUse:
    - type: command
      command: "./scripts/format-changed-files.sh"
mcp-servers:                          # GitHub.com cloud agent and Copilot CLI
  my-server:
    type: local
    command: npx
    args: ["-y", "my-mcp-server"]
    tools: ["*"]
    env:
      API_KEY: ${{ secrets.COPILOT_MCP_API_KEY }}
metadata:                             # GitHub.com only
  team: platform
---
```

This block shows syntax only. A real profile should set only the properties its target surfaces use.

---

## Property Reference

### `description` *(Required)*

**Type:** string
**Platforms:** All

Describes the agent's purpose and capabilities. GitHub.com and the CLI use it to decide when to infer/auto-select the agent, and the CLI shows it in the agent list and `task` tool. VS Code shows it as placeholder text in the chat input field.

```yaml
description: Reviews REST API designs for correctness, security, and consistency
```

---

### `name`

**Type:** string
**Default:** filename without `.md` / `.agent.md`
**Platforms:** All

Display name. The filename, not `name`, is the agent's ID for deduplication across levels and for `copilot --agent <id>`. In VS Code, `agents` lists and handoff `agent` values reference agents by name, and subagent names are case-sensitive.

```yaml
name: API Reviewer
```

---

### `target`

**Type:** string
**Values:** `vscode` | `github-copilot` | *(omit for both)*
**Platforms:** GitHub.com, VS Code / IDEs

Restricts which environment uses the profile. Omit it to make the agent available in both.

```yaml
target: vscode           # VS Code and IDEs only
target: github-copilot   # GitHub.com cloud agent only
```

---

### `tools`

**Type:** list of strings, or comma-separated string
**Default:** all tools
**Platforms:** All

Filters the tools available to the agent, whether built-in or from MCP servers. See `tools-reference.md` for aliases, VS Code tool sets, and MCP namespacing.

```yaml
tools: ["read", "search"]           # specific aliases (least privilege)
tools: ["*"]                        # all tools explicitly
tools: []                           # no tools
tools: ["read", "github/*"]         # alias + all tools from an MCP server
tools: ["read", "my-server/tool-a"] # alias + one MCP tool
```

In the CLI, including `*` anywhere grants every tool (`["view", "*"]` means all tools).

**Tool list priority (VS Code Local):** when a prompt file and a custom agent both set `tools`, the prompt file's list wins. Agent Host sessions (such as the Copilot harness) don't load prompt files.

---

### `model`

**Type:** string (all surfaces); string or array (VS Code)
**Default:** inherits the currently selected / session / parent-agent model

```yaml
# VS Code / IDEs: model display name
model: Claude Sonnet 5

# VS Code: prioritized fallback list, tried in order
model: ["Claude Opus 5", "GPT-5.5"]

# Copilot CLI: model ID
model: gpt-5.6-luna
```

**Surface notes:**

- **VS Code:** accepts a model name or a prioritized array. For subagents, the order is: explicit model from the `runSubagent` call, then the agent's `model`, then the main conversation's model. A subagent model above the main model's cost tier does not run.
- **Copilot CLI:** uses lowercase IDs (the CLI docs show `claude-sonnet-4.6`, `claude-haiku-4.5`, `gpt-5.4-mini`, `gpt-5.6-luna`, `gpt-6-astra`, `gemini-3.7-flash`). When the session model is `Auto`, subagents always use the resolved session model and ignore this field. See also `models`, `modelPolicy`, and `reasoningEffort` below.
- **GitHub.com cloud agent:** ambiguous. The configuration reference lists `model` without restriction ("Model to use when this custom agent executes"), but the create how-to says `model` applies "if you are creating and using the agent profile in VS Code, JetBrains IDEs, Eclipse, or Xcode". Don't rely on `model` to select the cloud agent's model.
- **Handoff `model`** uses the qualified format `Model Name (vendor)`, for example `GPT-5.5 (copilot)`.

**Current model names (from the supported-models page, September 2026):** GPT-5 mini, GPT-5.3-Codex, GPT-5.4, GPT-5.4 mini, GPT-5.5, GPT-5.6 Luna, GPT-5.6 Sol, GPT-5.6 Terra, GPT-6 Astra, GPT-6 Luna, GPT-6 Sol, Claude Fable 5, Claude Fable 5.1, Claude Haiku 4.5, Claude Opus 4.7, Claude Opus 4.8, Claude Opus 5, Claude Opus 5.5, Claude Sonnet 4.6, Claude Sonnet 5, Gemini 3.5–3.8 Flash, MAI-Code-1.1-Flash, Kimi K2.7 Code, Kimi K3, Grok 4.5–4.7. Availability differs by client. For example, Gemini and Grok models are not available on GitHub.com.

> [!WARNING]
> Retired models no longer resolve. Retired as of 2026-09-01: Claude Sonnet 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Sonnet 4.6 (still available to individual subscribers on annual plans), and Gemini 3.1 Pro. GPT-5.2 and GPT-5.2-Codex were retired 2026-06-05, and GPT-4.1 on 2026-06-01. Claude Opus 4.7, Gemini 3.5/3.6 Flash, and Kimi K2.7 Code are scheduled for 2026-10-02. Many community examples (including awesome-copilot and VS Code's own doc samples) still pin retired models such as `GPT-4.1`, `GPT-5.2`, or `Claude Sonnet 4.5`. Check the retirement table before copying one.

---

### `models`, `modelPolicy`, `reasoningEffort` *(Copilot CLI only)*

| Property | Type | Description |
|---|---|---|
| `models` | string[] | Models in priority order. The first one the user's plan can access is used; if none resolve, falls back to the session's model. Overrides `model` when both are set. |
| `modelPolicy` | string | `"preferred"` (default) lets `model`/`models` be overridden by a `subagents` override in `~/.copilot/settings.json` or the `/subagents` picker. `"required"` locks dispatch to one of the authored models. |
| `reasoningEffort` | string | Default reasoning effort, for example `"low"`, `"medium"`, `"high"`. Inherits the outer agent's effort when unset. |

Precedence, highest first: explicit per-call value, then the `subagents` override in `~/.copilot/settings.json`, then the agent's `model`/`models`/`reasoningEffort`, then the parent session's value.

---

### `include-custom-instructions` *(Copilot CLI only)*

**Type:** boolean
**Default:** `false`

When the agent runs as a **subagent**, include repository instruction files (`copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`). Has no effect when the agent is selected directly (`--agent`, `/agent`, inference), because the session agent already receives them. `--no-custom-instructions` always wins.

```yaml
include-custom-instructions: true
```

---

### `user-invocable`

**Type:** boolean
**Default:** `true`
**Platforms:** GitHub.com, VS Code / IDEs

When `false`, users can't select the agent manually. It can only be used as a subagent or programmatically. In VS Code this controls picker visibility for both the Local and Copilot harnesses.

```yaml
user-invocable: false
```

---

### `disable-model-invocation`

**Type:** boolean
**Default:** `false`
**Platforms:** GitHub.com, VS Code / IDEs

The meaning differs by surface:

- **GitHub.com:** when `true`, the cloud agent will not automatically use this agent based on task context. It must be selected manually. Equivalent to `infer: false`. If both are set, `disable-model-invocation` wins.
- **VS Code:** when `true`, other agents can't invoke this agent as a subagent. An explicit entry in a coordinator's `agents` list overrides it.

```yaml
disable-model-invocation: true
```

| Combination | Effect |
|---|---|
| `user-invocable: false` | Hidden from the picker, still usable as a subagent |
| `disable-model-invocation: true` | Visible in the picker, not auto-selected / not used as a subagent (unless explicitly listed in `agents` in VS Code) |
| Both | Not user-selectable and not auto-invoked. Only reachable via an explicit `agents` entry (VS Code) or programmatically |

---

### `infer` *(Retired / Deprecated)*

**Do not use in new profiles.** GitHub.com marks it retired and VS Code deprecated, replaced by `user-invocable` and `disable-model-invocation`. On GitHub.com, `infer: false` is equivalent to `disable-model-invocation: true` (it does **not** imply `user-invocable: false`).

> [!NOTE]
> The Copilot CLI command reference still lists `infer` (boolean, default `true`, "Allow auto-delegation by the main agent") as an active field and does not list `disable-model-invocation`. If you need to stop CLI auto-delegation, `infer: false` is the only CLI-documented option.

---

### `argument-hint`

**Type:** string
**Platforms:** VS Code / IDEs only. Ignored on GitHub.com.

Hint text shown in the chat input field when the agent is selected.

```yaml
argument-hint: Paste the OpenAPI spec or describe the endpoint to review
```

---

### `agents`

**Type:** list of strings
**Platforms:** VS Code only

Names of agents this agent may invoke as subagents. The `agent` tool must be in `tools`.

```yaml
tools: ["agent", "read", "search"]
agents: ["Codebase Researcher", "Reviewer"]
```

- Omitted or `["*"]`: all available agents (except those with `disable-model-invocation: true`)
- `[]`: no subagents
- Names are case-sensitive

**Nested subagents:** Local subagents can't invoke further subagents unless `chat.subagents.allowInvocationsFromSubagents` is enabled (default `false`, maximum depth five). A self-referential agent lists itself in `agents`.

---

### `handoffs`

**Type:** list of objects
**Platforms:** VS Code / IDEs only. Ignored on GitHub.com.

Buttons shown after a response completes that switch to another agent with the conversation context and a pre-filled prompt.

| Property | Type | Required | Description |
|---|---|---|---|
| `label` | string | Yes | Button text |
| `agent` | string | Yes | Target agent identifier (built-in agents such as `agent` also work) |
| `prompt` | string | No | Prompt text sent to the target agent |
| `send` | boolean | No | `true` auto-submits the prompt; default `false` |
| `model` | string | No | Model for the handoff, in `Model Name (vendor)` format, for example `Claude Sonnet 5 (copilot)` |

```yaml
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Implement the plan outlined above, starting with the database layer.
    send: false
    model: GPT-5.5 (copilot)
  - label: Security Review
    agent: security-analyst
    prompt: Review the implementation above for security vulnerabilities.
    send: true
```

Common workflows:

- Planning → Implementation
- Implementation → Code Review
- Write Failing Tests → Write Passing Implementation

---

### `hooks` *(Preview)*

**Type:** object (map of event name → list of hook commands)
**Platforms:** VS Code **Local** harness only
**Requires:** `chat.useHooks` (on by default) and a trusted workspace

Hook commands that run only while this agent is active (user-selected or as a subagent), in addition to user, workspace, and plugin hooks. Use PascalCase event names: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `Stop`. When the agent runs as a subagent, its `Stop` hook is treated as `SubagentStop`.

```yaml
hooks:
  PostToolUse:
    - type: command
      command: "./scripts/format-changed-files.sh"
```

Agent-scoped hooks don't apply to the Copilot, Claude, or Codex harnesses, which use their own hook implementations. The event list may have more entries than shown here, so check the [VS Code hooks reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference) for the complete list.

---

### `mcp-servers`

**Type:** object
**Platforms:** GitHub.com cloud agent and Copilot CLI. Not used by VS Code or other IDE custom agents.

MCP servers available only to this agent. On GitHub.com it is a YAML form of the repository MCP JSON configuration. In the CLI it uses the same schema as `~/.copilot/mcp-config.json`.

```yaml
mcp-servers:
  custom-mcp:              # key becomes the tool namespace (custom-mcp/<tool>)
    type: local            # "stdio" is accepted and mapped to "local"
    command: some-command
    args: ["--arg1", "--arg2"]
    tools: ["*"]           # tools the server exposes; ["*"] = all
    env:
      ENV_VAR_NAME: ${{ secrets.COPILOT_MCP_ENV_VAR_VALUE }}
```

**Secret and variable syntax (GitHub.com):**

| Syntax | Where supported |
|---|---|
| `$COPILOT_MCP_ENV_VAR_VALUE` | Repository MCP JSON and agent YAML |
| `${COPILOT_MCP_ENV_VAR_VALUE}` | Repository MCP JSON and agent YAML (Claude Code syntax) |
| `${COPILOT_MCP_ENV_VAR_VALUE:-default}` | Repository MCP JSON and agent YAML, with default |
| `${{ secrets.COPILOT_MCP_ENV_VAR_VALUE }}` | Agent YAML only |
| `${{ vars.COPILOT_MCP_ENV_VAR_VALUE }}` | Agent YAML only |

Secrets and variables must be configured as **Agents** secrets/variables at the organization or repository level, and their names **must start with `COPILOT_MCP_`**. Only prefixed secrets and variables are passed to MCP configuration, and they are exposed only to MCP servers, not to the agent's environment.

**Processing order (GitHub.com):** out-of-the-box MCP (for example `github`) → custom agent `mcp-servers` → repository-settings MCP. Each level can override the previous one. Out-of-the-box servers are covered in `tools-reference.md`.

---

### `metadata`

**Type:** object of string name/value pairs
**Platforms:** GitHub.com only. Not used by VS Code or other IDEs.

```yaml
metadata:
  team: platform-engineering
  owner: dev-productivity
```

---

## Claude Agent Format (`.claude/agents/`)

VS Code and Copilot CLI both load agents from `.claude/agents/` (plain `.md` files in the [Claude sub-agents format](https://code.claude.com/docs/en/sub-agents)). VS Code also reads `~/.claude/agents/` at user level.

| Property | `.agent.md` format | Claude format |
|---|---|---|
| File extension | `.agent.md` | `.md` |
| `name` | Optional | Required |
| `tools` | YAML array | Comma-separated string, for example `"Read, Grep, Glob, Bash"` |
| `disallowedTools` | Not supported | Comma-separated string of blocked tools |

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, WebFetch
disallowedTools: Bash, Edit, Write
---

You are a security specialist...
```

VS Code maps Claude tool names to the corresponding VS Code tools. In the CLI, `.github/agents/` takes precedence over `.claude/agents/` at the same directory level.

---

## Processing Rules

### Naming conflicts

The filename (minus `.md` / `.agent.md`) identifies the agent. The lowest-level configuration wins: repository over organization, organization over enterprise.

**Copilot CLI specifics:** the CLI walks up from the current directory to the Git root and loads every `.github/agents/` and `.claude/agents/` on the way. The deepest directory wins, and `.github/agents/` beats `.claude/agents/` at the same level. Plugin agents have the lowest priority.

> [!WARNING]
> The CLI docs contradict each other on user vs. project priority. The CLI how-to says "the one in your home directory will be used", while the CLI command reference says "User-level agents have lower priority than project-level agents". Avoid reusing a name across the two scopes.

### Versioning (GitHub.com)

Versioning follows Git commit SHAs of the profile file. An assigned task uses the latest profile version on the repository and branch, and follow-up interactions in the resulting pull request keep using that same version.

### File detection (VS Code)

VS Code treats **any** `.md` file in `.github/agents/` as a custom agent. The settings `chat.agentFilesLocations` and `chat.modeFilesLocations` are deprecated (Local agent only). Legacy `.chatmode.md` files should be renamed to `.agent.md`.

---

## Complete Working Examples

### Read-only analyst (VS Code)

```yaml
---
name: API Analyst
description: Reviews REST API specifications for design quality and security. Does not modify code.
tools: ["read", "search", "web"]
model: Claude Sonnet 5
argument-hint: Paste the OpenAPI spec or describe the endpoint
target: vscode
handoffs:
  - label: Implement Changes
    agent: api-dotnet
    prompt: Implement the API changes recommended by the analyst.
    send: false
---
```

### Orchestrator with subagents (VS Code)

```yaml
---
name: Project Lead
description: Coordinates planning, implementation, and review across specialized agents.
tools: ["agent", "read", "search"]
agents: ["Implementation Planner", "Code Reviewer", "Security Analyst"]
target: vscode
---
```

### Hidden utility subagent (VS Code)

```yaml
---
name: Terraform Validator
description: Validates Terraform plans. Invoked only as a subagent, not shown in the picker.
tools: ["read", "execute"]
user-invocable: false
---
```

Leave `disable-model-invocation` unset here. Setting it to `true` would stop coordinators from delegating to this agent unless they list it explicitly in `agents`.

### Cloud agent with MCP (GitHub.com)

```yaml
---
name: data-pipeline-agent
description: Manages ETL pipelines using the internal data platform API.
tools: ["read", "edit", "search", "data-platform/list-pipelines", "data-platform/run-pipeline", "github/*"]
target: github-copilot
mcp-servers:
  data-platform:
    type: local
    command: npx
    args: ["-y", "@company/data-platform-mcp"]
    tools: ["*"]
    env:
      API_TOKEN: ${{ secrets.COPILOT_MCP_DATA_PLATFORM_TOKEN }}
      ENVIRONMENT: ${{ vars.COPILOT_MCP_DEPLOY_ENV }}
metadata:
  team: data-engineering
---
```

### CLI subagent with model policy (Copilot CLI)

```yaml
---
name: test-runner
description: Runs the test suite and summarizes failures. Use when tests need to be run or diagnosed.
tools: ["execute", "read", "search"]
models: ["gpt-5.6-luna", "gpt-5.4-mini"]
reasoningEffort: low
include-custom-instructions: true
---
```

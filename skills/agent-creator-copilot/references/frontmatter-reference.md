# Frontmatter Reference — Custom Agent Profiles

Comprehensive reference for all YAML frontmatter properties in custom agent profiles (`.agent.md`). Load this file when writing or modifying agent frontmatter.

**Sources (last verified April 2026):**
- VS Code: https://code.visualstudio.com/docs/copilot/customization/custom-agents
- GitHub: https://docs.github.com/en/copilot/reference/custom-agents-configuration

---

## Platform Compatibility Overview

Not all frontmatter properties are supported in all environments. Refer to this table before using any property.

| Property | VS Code / JetBrains / IDEs | GitHub.com Cloud Agent |
|---|---|---|
| `name` | ✅ | ✅ |
| `description` | ✅ | ✅ |
| `target` | ✅ | ✅ |
| `tools` | ✅ | ✅ |
| `model` | ✅ (string or array) | ✅ (string only) |
| `user-invocable` | ✅ | ✅ |
| `disable-model-invocation` | ✅ | ✅ |
| `argument-hint` | ✅ | ❌ Ignored |
| `handoffs` | ✅ | ❌ Ignored |
| `agents` | ✅ | ❌ |
| `hooks` | ✅ Preview | ❌ |
| `mcp-servers` | ❌ Ignored | ✅ |
| `metadata` | ❌ | ✅ |
| `infer` | Retired | Retired |

---

## All Properties at a Glance

```yaml
---
name: my-agent                        # display name (optional)
description: What this agent does     # required
target: vscode                        # vscode | github-copilot | omit for both
tools: ["read", "search"]             # list of tools; omit = all tools
model: claude-sonnet-4-5              # single model or priority array (VS Code)
user-invocable: true                  # show in agents dropdown (default: true)
disable-model-invocation: false       # prevent auto-selection by cloud agent (default: false)
argument-hint: Paste your spec here   # VS Code only — hint text in chat input
agents:                               # VS Code only — available subagents
  - planner
  - "*"
handoffs:                             # VS Code only — post-response transition buttons
  - label: Implement
    agent: implementation
    prompt: Implement the plan above.
    send: false
    model: GPT-5.2 (copilot)
hooks:                                # VS Code Preview — agent-scoped hooks
  onChatRequest:
    - command: some-command
mcp-servers:                          # Cloud agent only
  my-server:
    type: local
    command: npx
    args: ["-y", "my-mcp-server"]
    tools: ["*"]
    env:
      API_KEY: ${{ secrets.MY_API_KEY }}
metadata:                             # Cloud agent only — arbitrary annotation
  team: platform
  version: "2.0"
---
```

---

## Property Reference

### `description` *(Required)*

**Type:** string  
**Platforms:** All

Description of the agent's purpose and capabilities. Shown as placeholder text in the VS Code chat input when the agent is selected. Used by the cloud agent to understand when to invoke this agent.

```yaml
description: Reviews REST API designs for correctness, security, and consistency
```

---

### `name`

**Type:** string  
**Default:** filename (without `.md` / `.agent.md`)  
**Platforms:** All

Display name for the agent in the agents dropdown. If omitted, the filename (minus extension) is used.

**Naming conflict resolution:** When agents exist at multiple levels (workspace, user, org, enterprise), the lowest-level configuration wins. A workspace agent overrides an org-level agent of the same name.

```yaml
name: API Reviewer
```

---

### `target`

**Type:** string  
**Values:** `vscode` | `github-copilot` | *(omit for both)*  
**Platforms:** All

Restricts which environment loads this agent profile. Omit to allow the profile to be loaded in both VS Code and GitHub.com.

```yaml
target: vscode           # VS Code and IDEs only
target: github-copilot   # GitHub.com cloud agent only
```

---

### `tools`

**Type:** list of strings, or comma-separated string  
**Default:** all tools  
**Platforms:** All

Controls which tools are available to the agent. See `tools-reference.md` for the full alias table and MCP namespacing syntax.

```yaml
tools: ["read", "search"]           # specific aliases (least privilege)
tools: ["*"]                        # all tools explicitly
tools: []                           # no tools
tools: ["read", "github/*"]         # built-in + all tools from an MCP server
tools: ["read", "my-server/tool-a"] # built-in + specific MCP tool
```

**Tool list priority:** When a prompt file and a custom agent are both active, the prompt file's `tools` property takes precedence over the agent's.

---

### `model`

**Type:** string or array (VS Code); string only (cloud agent)  
**Default:** inherits user's selected model  
**Platforms:** All (array form VS Code only)

Specifies the AI model for the agent. In VS Code, provide an array for a prioritized fallback list — the system tries each model in order until an available one is found.

```yaml
# Single model (works everywhere):
model: claude-sonnet-4-5

# Priority fallback list (VS Code only):
model:
  - GPT-5.2 (copilot)
  - Claude Sonnet 4.5 (copilot)
```

Use the qualified model name format for Copilot-served models: `Model Name (copilot)`.

---

### `user-invocable`

**Type:** boolean  
**Default:** `true`  
**Platforms:** All

When `false`, the agent is hidden from the agents dropdown and can only be accessed as a subagent invoked by another agent, or programmatically. Use this for orchestration-only or utility agents that users should never call directly.

```yaml
user-invocable: false   # subagent/programmatic use only
```

---

### `disable-model-invocation`

**Type:** boolean  
**Default:** `false`  
**Platforms:** All

When `true`, prevents the Copilot cloud agent from automatically selecting this agent based on task context. The agent must be manually selected or invoked via handoff. Has no effect in VS Code (manual selection is always required there).

```yaml
disable-model-invocation: true   # must be manually selected
```

> **Relationship to `user-invocable`:**  
> These two properties give independent control:
> - `user-invocable: false` → hidden from dropdown, still auto-invokable as subagent
> - `disable-model-invocation: true` → visible in dropdown, but never auto-selected
> - Both `false`/`true` together → fully private utility agent

---

### `argument-hint`

**Type:** string  
**Platforms:** VS Code / IDEs only. Ignored on GitHub.com.

Optional hint text shown in the chat input field when this agent is selected. Guides users on what to type or paste.

```yaml
argument-hint: Paste the OpenAPI spec or describe the endpoint to review
```

---

### `agents`

**Type:** list of strings  
**Platforms:** VS Code only

Declares which agents this agent is permitted to invoke as subagents. The `agent` tool alias must also be included in `tools` for subagent invocation to work.

```yaml
agents:
  - planner          # specific agent by filename (without extension)
  - code-reviewer
  - "*"              # allow all available agents
```

Use `agents: []` to explicitly prevent this agent from using any subagents.

**Self-referential agents:** To allow an agent to list itself in `agents` (recursive orchestration), enable `chat.subagents.allowInvocationsFromSubagents` in VS Code settings.

---

### `handoffs`

**Type:** list of objects  
**Platforms:** VS Code / IDEs only. Ignored on GitHub.com.

Defines guided transitions to other agents that appear as buttons after a chat response completes. Each handoff can pre-fill a prompt and optionally auto-submit it.

**Full property reference for each handoff entry:**

| Property | Type | Required | Description |
|---|---|---|---|
| `label` | string | **Yes** | Button text shown to the user |
| `agent` | string | **Yes** | Target agent filename without extension |
| `prompt` | string | No | Pre-filled prompt sent to the target agent |
| `send` | boolean | No | `true` = auto-submit the prompt; `false` (default) = user must confirm |
| `model` | string | No | Model override for the handoff step. Use qualified name: `Model Name (vendor)` |

```yaml
handoffs:
  - label: Start Implementation
    agent: implementation
    prompt: Implement the plan outlined above, starting with the database layer.
    send: false
    model: GPT-5.2 (copilot)

  - label: Security Review
    agent: security-analyst
    prompt: Review the implementation above for security vulnerabilities.
    send: true
```

**Common handoff workflows:**
- Planning → Implementation
- Implementation → Code Review
- Write Failing Tests → Write Passing Implementation

---

### `hooks` *(Preview)*

**Type:** object  
**Platforms:** VS Code only (Preview)  
**Requires:** `chat.useCustomAgentHooks` VS Code setting enabled

Hook commands scoped to this agent. Hooks defined here run only when this agent is active (user-invoked or as a subagent). Uses the same format as VS Code hook configuration files.

```yaml
hooks:
  onChatRequest:
    - command: my-hook-command
      args: ["--flag"]
```

---

### `mcp-servers` *(Cloud Agent Only)*

**Type:** object  
**Platforms:** GitHub.com cloud agent only. Ignored in VS Code and other IDEs.

Embeds MCP server configuration directly in the agent profile. For VS Code, configure MCP servers through VS Code settings instead.

**Full MCP server entry format:**

```yaml
mcp-servers:
  server-name:             # arbitrary key — used as the server namespace
    type: local            # local (also accepts stdio for Claude Code compat)
    command: npx           # executable to run
    args:                  # arguments array
      - "-y"
      - "my-mcp-package"
    tools: ["*"]           # tools from this server to expose; ["*"] = all
    env:                   # environment variables / secrets
      API_KEY: ${{ secrets.MY_SECRET }}
      BASE_URL: https://api.example.com
```

**`type` values:**

| Value | Meaning |
|---|---|
| `local` | Standard cloud agent type |
| `stdio` | Claude Code / VS Code compatibility alias — mapped to `local` |

**Secret/variable reference syntax:**

| Syntax | Source |
|---|---|
| `${{ secrets.NAME }}` | Repository secret (Copilot environment) |
| `${{ vars.NAME }}` | Repository variable (Copilot environment) |
| `$VARIABLE_NAME` | Environment variable |
| `${VARIABLE_NAME}` | Environment variable (Claude Code syntax) |
| `${VARIABLE_NAME:-default}` | Environment variable with fallback default |

**Built-in out-of-box MCP servers (GitHub.com cloud agent):**

| Server namespace | Access |
|---|---|
| `github/*` | All read-only GitHub tools, scoped to source repository |
| `playwright/*` | Browser automation tools, restricted to localhost |

**MCP processing order (cloud agent):** out-of-box MCP (e.g., `github/*`) → custom agent profile MCP → repository settings MCP. Each level can override the previous.

**Enabling specific MCP tools only:**

```yaml
# In the agent's top-level tools property, reference MCP tools by namespace:
tools: ["read", "edit", "custom-mcp/tool-1", "github/create-pull-request"]

# In mcp-servers, tools: controls what the server exposes to the agent:
mcp-servers:
  custom-mcp:
    type: local
    command: some-command
    args: ["--arg1"]
    tools: ["*"]          # expose all tools from this server
```

---

### `metadata` *(Cloud Agent Only)*

**Type:** object (key-value pairs, both strings)  
**Platforms:** GitHub.com cloud agent only. Not used in VS Code or other IDEs.

Allows annotation of the agent with arbitrary metadata. Useful for tracking team ownership, versions, or other organizational attributes.

```yaml
metadata:
  team: platform-engineering
  version: "2.1"
  owner: dev-productivity
```

---

### `infer` *(Retired)*

**Do not use.** Replaced by `user-invocable` and `disable-model-invocation`.

| Old behavior | New equivalent |
|---|---|
| `infer: true` (default) | `user-invocable: true` + `disable-model-invocation: false` |
| `infer: false` | `user-invocable: false` + `disable-model-invocation: true` |

---

## Claude Agent Format (`.claude/agents/`)

VS Code natively reads `.md` files from `.claude/agents/` using Claude's sub-agent format. This enables sharing agent definitions across VS Code and Claude Code.

**Frontmatter differences from `.agent.md`:**

| Property | `.agent.md` format | Claude format |
|---|---|---|
| File extension | `.agent.md` | `.md` |
| `tools` | YAML array `["Read", "Grep"]` | Comma-separated string `"Read, Grep, Glob"` |
| `disallowedTools` | Not supported | Comma-separated string of blocked tools |
| `name` | Optional | Required |

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, WebFetch
disallowedTools: Bash, Edit, Write
---

You are a security specialist...
```

VS Code maps Claude tool names to the corresponding VS Code tools automatically.

---

## Processing Rules

### Naming Conflicts

When agents exist at multiple scope levels with the same name (based on filename minus extension), the **lowest level wins**:

`Workspace > User profile > Organization > Enterprise`

A workspace `.github/agents/reviewer.agent.md` overrides an org-level `reviewer.agent.md`.

### Versioning (Cloud Agent)

Agent profile versioning is based on Git commit SHAs for the profile file. When assigned to a task, the cloud agent uses the latest version on the current branch. When a pull request is created, the same agent version is used for consistency throughout that PR's lifecycle.

---

## Complete Working Examples

### Read-Only Analyst (VS Code)

```yaml
---
name: API Analyst
description: Reviews REST API specifications for design quality and security. Does not modify code.
tools: ["read", "search", "web"]
model: claude-sonnet-4-5
argument-hint: Paste the OpenAPI spec or describe the endpoint
handoffs:
  - label: Implement Changes
    agent: api-dotnet
    prompt: Implement the API changes recommended by the analyst.
    send: false
---
```

### Orchestrator with Subagents (VS Code)

```yaml
---
name: Project Lead
description: Coordinates planning, implementation, and review across specialized agents.
tools: ["read", "search", "agent"]
agents:
  - implementation-planner
  - code-reviewer
  - security-analyst
user-invocable: true
disable-model-invocation: false
---
```

### Cloud Agent with MCP (GitHub.com)

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
      API_TOKEN: ${{ secrets.DATA_PLATFORM_TOKEN }}
      ENVIRONMENT: ${{ vars.DEPLOY_ENV }}
metadata:
  team: data-engineering
  owner: pipeline-team
---
```

### Hidden Utility Subagent (VS Code)

```yaml
---
name: terraform-validator
description: Validates Terraform plans. Invoked only as a subagent — not shown in dropdown.
tools: ["read", "execute"]
user-invocable: false
disable-model-invocation: true
---
```
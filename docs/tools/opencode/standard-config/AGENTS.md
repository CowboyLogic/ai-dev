# OpenCode Configuration Guide for AI Assistants

This directory contains configuration files and examples for the OpenCode CLI tool, a powerful AI-assisted development environment.

## Behavioral Foundation

**All AI assistants must first follow the baseline behavioral model:**

📋 **[`../../../agents/baseline-behaviors.md`](../../../agents/baseline-behaviors.md)**

The guidelines below are OpenCode-specific and should be applied **in addition to** the baseline behaviors. When conflicts arise, the baseline behaviors take precedence unless explicitly overridden by user directives.

## Directory Structure

```
opencode/
├── opencode.json              # Main configuration file
├── agent-subagent-config/     # Advanced modular subagent configuration
│   ├── opencode.json          # Minimal primary agent config
│   ├── agent/                 # Individual subagent definitions
│   │   ├── api.md             # API design and integration
│   │   ├── architect.md       # System architecture
│   │   ├── cloud.md           # Cloud infrastructure
│   │   ├── data.md            # Data analysis and ETL
│   │   ├── database.md        # Database design and optimization
│   │   ├── devops.md          # CI/CD and deployment
│   │   ├── documentation.md   # Technical documentation
│   │   ├── performance.md     # Performance optimization
│   │   ├── research.md        # Technical research
│   │   ├── reviewer.md        # Code review
│   │   ├── security.md        # Security audits
│   │   ├── testing.md         # Test development
│   │   └── uxui.md            # UI/UX design
│   └── README.md              # Modular config documentation
├── README.md                  # User guide
└── AGENTS.md                  # This file
```

## User Documentation

**For comprehensive user guides and setup instructions, see:**

📖 **[`docs/tools/opencode/configuration.md`](../configuration.md)** - Complete configuration guide  
📖 **[`docs/tools/opencode/index.md`](../index.md)** - OpenCode overview and quick start  
📖 **[`docs/tools/opencode/samples.md`](../samples.md)** - MCP server configuration examples

## AI Assistant Guidelines

### Configuration Awareness

- **Always reference the appropriate configuration files** and understand the current agent setup
- **Respect tool permissions** - Never attempt operations that are disabled for the current agent
- **Use appropriate models** for task complexity and requirements
- **Update documentation** when making changes to agent definitions or settings

### Model Selection Guidelines

#### For Simple Tasks
- **GPT-5-mini** or **Claude Haiku 4.5**: Quick tasks, testing, data processing
- **Grok 2**: Alternative for general development tasks

#### For Complex Tasks
- **Claude Sonnet 4.5**: Code review, security analysis, architecture
- **Grok Code Fast 1**: API design, database work, full-stack development

#### For Creative Tasks
- **Gemini 2.5 Pro**: UI/UX design, documentation, creative problem-solving

### Temperature Settings

| Temperature | Use Case | Examples |
|-------------|----------|----------|
| 0.0-0.1 | Deterministic code generation | Bug fixes, refactoring, security reviews |
| 0.2-0.3 | Balanced development | API design, database queries, general coding |
| 0.4-0.5 | Creative tasks | Documentation, UI/UX design, brainstorming |

### Tool Permission Patterns

#### Read-Only Agents (Analysis/Review)
```json
{
  "tools": {
    "read": true,
    "list": true,
    "glob": true,
    "grep": true,
    "webfetch": true
    // No write, edit, or bash
  }
}
```
**Use for**: `@reviewer`, `@security`, `@research`, `@architect`

#### Documentation Agents
```json
{
  "tools": {
    "write": true,
    "edit": true,
    "read": true,
    "list": true,
    "glob": true,
    "grep": true,
    "webfetch": true
    // No bash for security
  }
}
```
**Use for**: `@docs`, `@documentation`

#### Full Development Agents
```json
{
  "tools": {
    "write": true,
    "edit": true,
    "bash": true,
    "read": true,
    "list": true,
    "glob": true,
    "grep": true
  }
}
```
**Use for**: `@api`, `@database`, `@devops`, `@testing`

### Security Considerations

- **Never hardcode secrets** in configuration files
- **Use environment variables** for API keys and tokens: `${GITHUB_TOKEN}`
- **Restrict tool permissions** appropriately for each agent
- **Regularly audit** agent configurations for security implications
- **Use read-only agents** for sensitive code reviews

### Agent Naming Conventions

- **Use lowercase**: `api`, `database`, `security` (not `API`, `Database`, `Security`)
- **Be descriptive but concise**: `uxui` (not `ui`), `devops` (not `deployment`)
- **Match filename**: `api.md` → `@api`, `security.md` → `@security`
- **Use hyphens for compound names**: `performance-tuning.md` → `@performance-tuning`

#### `quick` Agent
- **Purpose**: Fast general tasks (code formatting, simple queries, quick fixes)
- **Model**: `xai/grok-2-mini`
- **Mode**: `primary`
- **Temperature**: 0.1 (deterministic)
- **Tools**: Full access (write, edit, bash, read, list, glob, grep)

#### `reviewer` Agent
- **Purpose**: Code review and analysis (read-only, no modifications)
- **Model**: `anthropic/claude-sonnet-4-5-20250929`
- **Mode**: `subagent`
- **Temperature**: 0.1
- **Tools**: Read-only (read, list, glob, grep, webfetch) - NO write/edit/bash

#### `docs` Agent
- **Purpose**: Documentation creation and maintenance
- **Model**: `anthropic/claude-sonnet-4-5-20250929`
- **Mode**: `subagent`
- **Temperature**: 0.3 (slightly more creative)
- **Tools**: Documentation-focused (write, edit, read, list, glob, grep, webfetch) - NO bash

### 3. **Custom Commands**
Pre-defined commands that leverage the tiered agent approach:

| Command | Agent | Purpose |
|---------|-------|---------|
| `quick-fix` | `quick` | Fast, simple fixes |
| `analyze` | `reasoning` | Deep architecture/pattern analysis |
| `build` | (default) | Build and test project |
| `review` | `reviewer` | Code quality/security review (read-only) |
| `document` | `docs` | Create/update documentation |
| `test` | (default) | Run and fix tests |
| `deploy` | (default) | Deployment tasks |
| `refactor` | `reasoning` | Advanced code refactoring |

**Command Template Variables**: Use `$ARGUMENTS` in templates to reference user input.

### 4. **Tool Permissions**
All tools enabled by default:
- File operations: `write`, `edit`, `read`, `list`
- System: `bash`
- Search: `glob`, `grep`
- Network: `webfetch`
- Task management: `task`, `todowrite`, `todoread`

**Permissions**: `bash`, `write`, and `edit` set to `allow` (execute without prompting).

### 5. **MCP (Model Context Protocol) Servers**
Remote MCP server configured:
- **GitHub MCP**: Connected via GitHub Copilot API
  - URL: `https://api.githubcopilot.com/mcp/`
  - Authentication: Bearer token via `${GITHUB_TOKEN}` environment variable

### 6. **Instructions Loading**
The configuration automatically loads project-specific instructions from:
- `AGENTS.md`
- `.cursor/rules/*.md`
- `README.md`

## Sample Configurations

### `sample-docker-mcp.json`
Demonstrates how to configure a **local Docker-based MCP server**:

```json
"mcp": {
  "docker-mcp-sample": {
    "type": "local",
    "command": ["docker", "run", "--rm", "-i", "my-mcp-server:latest"],
    "enabled": true,
    "environment": {
      "API_KEY": "${MY_API_KEY}",
      "DEBUG": "true"
    },
    "timeout": 10000
  }
}
```

**Key Points**:
- Use `type: "local"` for local servers
- Command must be an array of strings
- Environment variables can reference shell variables using `${VAR_NAME}`
- Timeout in milliseconds

### `sample-npx-mcp.json`
Demonstrates how to configure an **NPX-based MCP server** (Snyk example):

```json
"mcp": {
  "snyk": {
    "type": "local",
    "command": ["npx", "-y", "@snyk/mcp-server"],
    "enabled": true,
    "environment": {
      "SNYK_TOKEN": "${SNYK_TOKEN}"
    },
    "timeout": 15000
  }
}
```

**Key Points**:
- Use `npx -y` to automatically install and run npm packages
- Common pattern for Node.js-based MCP servers
- Remember to enable the tool in the `tools` section

### `docker-desktop-github-mcp.json`
Demonstrates how to configure the **Docker Desktop MCP Toolbox GitHub server**:

```json
"mcp": {
  "docker-desktop-github": {
    "type": "local",
    "command": ["docker", "run", "--rm", "-i", "docker/desktop-mcp-toolbox-github:latest"],
    "enabled": true,
    "environment": {
      "GITHUB_TOKEN": "${GITHUB_TOKEN}"
    },
    "timeout": 30000
  }
}
```

**Key Points**:
- Requires Docker Desktop with MCP Toolbox extension installed
- Provides local GitHub operations through Docker containers
- Uses `GITHUB_TOKEN` for authentication (same as remote GitHub MCP)
- Longer timeout (30 seconds) to accommodate Docker startup time
- Enable in `tools` section as `"docker-desktop-github": true`

## Modular Subagent Configuration

The `agent-subagent-config/` directory demonstrates an **advanced modular pattern** for managing specialized subagents. Instead of defining all agents in `opencode.json`, this approach uses individual markdown files with YAML frontmatter to configure agents.

### How It Works

**Main Configuration** (`agent-subagent-config/opencode.json`):
- Defines only **primary agents** (plan, build)
- Minimal configuration focused on top-level workflow

**Agent Definitions** (`agent-subagent-config/agent/*.md`):
- Each specialized agent in its own markdown file
- YAML frontmatter contains OpenCode configuration
- Automatic discovery and loading via instruction system

**Example Agent File** (`agent/api.md`):
```markdown
---
description: REST/GraphQL API design, OpenAPI specs, and API integration
mode: subagent
model: github-copilot/grok-code-fast-1
temperature: 0.2
tools:
  write: true
  edit: true
  bash: true
---

# Agent Purpose

The API agent is designed to assist with API design, documentation, and integration...
```

### Available Modular Subagents

| Agent | Focus | Model | Temp | Access |
|-------|-------|-------|------|--------|
| `api` | REST/GraphQL API design, OpenAPI | github-copilot/grok-code-fast-1 | 0.2 | Full |
| `architect` | System design, architecture | Qwen2.5-Coder:32b | 0.2 | Read-only |
| `cloud` | AWS/Azure/GCP, IaC | github-copilot/grok-code-fast-1 | 0.1 | Full |
| `data` | Data analysis, ETL | GPT-5-mini | 0.2 | Full |
| `database` | Schema design, query optimization | github-copilot/grok-code-fast-1 | 0.1 | Full |
| `devops` | CI/CD, Docker, Kubernetes | GPT-5-mini | 0.2 | Full |
| `documentation` | Technical docs, API docs | Claude Haiku 4.5 | 0.3 | Docs only |
| `performance` | Performance profiling, optimization | github-copilot/grok-code-fast-1 | 0.1 | Full |
| `research` | Technical discovery, doc analysis | GPT-5-mini | 0.2 | Read-only |
| `reviewer` | Code review, best practices | github-copilot/claude-sonnet-4.5 | 0.1 | Read-only |
| `security` | Security audits, vulnerabilities | github-copilot/claude-sonnet-4.5 | 0.1 | Bash only |
| `testing` | Unit/integration tests | GPT-5-mini | 0.2 | Full |
| `uxui` | UI/UX design, accessibility | Gemini 2.5 Pro | 0.3 | No bash |

### Benefits of Modular Configuration

- **Modularity**: Add/remove agents by adding/removing markdown files
- **Maintainability**: Each agent is self-contained and documented
- **Discoverability**: OpenCode automatically finds and loads agents
- **Version Control**: Track changes to individual agents independently
- **Reusability**: Share specific agent configurations across projects

### Agent Configuration Properties (YAML Frontmatter)

**Required**:
- `description`: Agent's purpose and capabilities
- `mode`: `subagent` for specialized agents

**Optional**:
- `model`: AI model to use (provider/model-name format)
- `temperature`: Creativity level (0.0-1.0)
- `tools`: Permissions object (`write`, `edit`, `bash`)

### Usage Examples

```bash
# Invoke specific subagents
opencode @api "Design a REST API for user authentication"
opencode @security "Audit authentication for vulnerabilities"
opencode @database "Optimize slow query in user_stats table"
opencode @uxui "Improve accessibility of login form"
opencode @cloud "Create Terraform module for AWS ECS"

# Primary agents auto-delegate to subagents
opencode @plan "Design microservices architecture"
opencode @build "Implement user authentication API"
```

### Adding New Modular Agents

1. Create `agent/yourname.md` with YAML frontmatter
2. Define `description`, `mode`, `model`, `temperature`, `tools`
3. Add documentation about purpose and usage
4. Agent is automatically available as `@yourname`

See `../agent-subagent-config/README.md` for comprehensive documentation.

## Traditional Configuration vs Modular Configuration

**Traditional** (`opencode.json`):
- All agents defined in single configuration file
- Suitable for simple setups with few agents
- Direct, straightforward configuration
- Examples: `quick`, `reviewer`, `docs` agents

**Modular** (`agent-subagent-config/`):
- Agents defined in individual markdown files
- Ideal for complex workflows with many specialized agents
- Modular, scalable, maintainable
- Examples: 13 specialized agents (api, security, devops, etc.)

## Working with This Configuration

### When Modifying `opencode.json`:

1. **Adding New Agents**:
   - Define under the `agent` section
   - Choose appropriate `mode`: `primary` or `subagent`
   - Set model based on complexity needs
   - Configure `temperature` (0.1 for deterministic, higher for creative)
   - Specify tool permissions carefully

2. **Adding Custom Commands**:
   - Define under the `command` section
   - Use `$ARGUMENTS` for user input
   - Optionally specify an `agent` to use a specialized model
   - Include clear `description` for discoverability

3. **Adding MCP Servers**:
   - Define under the `mcp` section
   - Set `type`: `"local"` or `"remote"`
   - For local: provide `command` array
   - For remote: provide `url` and authentication
   - Set `enabled: true`
   - Enable the tool in the `tools` section

4. **Environment Variables**:
   - Reference using `${VARIABLE_NAME}` syntax
   - Common variables: `${GITHUB_TOKEN}`, `${SNYK_TOKEN}`, `${API_KEY}`

### Best Practices:

- **Model Selection**: Use smaller/faster models for simple tasks, reserve advanced models for complex reasoning
- **Agent Modes**: Use `subagent` for specialized tasks, `primary` for general use
- **Tool Restrictions**: Limit tool access for review/analysis agents to prevent unintended modifications
- **Temperature Settings**: Keep low (0.1-0.2) for code generation, slightly higher (0.3-0.5) for documentation
- **MCP Timeouts**: Set appropriate timeouts based on expected server response times
- **Permissions**: Use `allow` carefully for destructive operations like `bash` and `write`

## Integration Notes

When working with OpenCode configurations:
- The `$schema` field provides validation and autocomplete in supported editors
- JSON comments (// and /* */) are supported in this configuration format
- The `autoupdate` setting keeps OpenCode CLI current
- `share: "manual"` requires explicit approval before sharing data

## Troubleshooting MCP Servers

Common issues when configuring MCP servers:
1. **Authentication failures**: Ensure environment variables are set in your shell
2. **Timeout errors**: Increase the `timeout` value for slow servers
3. **Command not found**: Verify Docker/NPX is installed and in PATH
4. **Tool not available**: Check that the tool is enabled in the `tools` section

## Documentation Maintenance for OpenCode

**CRITICAL: OpenCode configuration and documentation must remain synchronized.**

### When Modifying `opencode.json`

Any changes to the main configuration file require updates to:

1. **`docs/tools/opencode/index.md`** - User-facing documentation
   - Update configuration highlights if models, agents, or commands change
   - Update examples to match actual configuration
   - Add/remove sections for new/deleted features

2. **`opencode/standard-config/AGENTS.md`** (this file) - AI assistant guide
   - Update specialized agents section with new configurations
   - Update custom commands table with additions/removals
   - Update MCP server examples if integration changes
   - Modify best practices if configuration patterns change

3. **`docs/tools/opencode/configuration.md`** - Detailed MkDocs documentation
   - Comprehensive documentation of new features
   - Updated code examples
   - Usage patterns and best practices

4. **`docs/tools/opencode/index.md`** - OpenCode overview page
   - High-level changes that affect the overview
   - Updated feature lists

5. **`docs/index.md`** - Main site landing page
   - If changes significantly affect OpenCode capabilities
   - Update feature highlights

### When Adding/Modifying Sample Configurations

Changes to files in `docs/tools/opencode/agent-subagent-config/`:

1. **`docs/tools/opencode/index.md`** - Add examples and usage instructions
2. **`opencode/standard-config/AGENTS.md`** - Update sample configuration explanations
3. **`docs/tools/opencode/samples.md`** - Comprehensive sample documentation
4. **`docs/mcp/overview.md`** - MCP-specific documentation
5. **`agent-subagent-config/README.md`** - Update if modular config changes

### Common Update Scenarios

**Added a new agent:**
```
✓ Update agent table in opencode/standard-config/AGENTS.md
✓ Add example usage in docs/tools/opencode/index.md
✓ Document configuration in `docs/tools/opencode/configuration.md`
✓ Update feature list in `docs/tools/opencode/index.md` if significant
```

**Changed model configuration:**
```
✓ Update model sections in all three OpenCode documentation files
✓ Update examples that reference model names
✓ Verify MCP server configurations still match
```

**Added custom command:**
```
✓ Add to custom commands table in opencode/standard-config/AGENTS.md
✓ Add usage example in `docs/tools/opencode/index.md`
✓ Document in `docs/tools/opencode/configuration.md`
```

**Modified MCP server configuration:**
```
✓ Update MCP sections in both README.md and AGENTS.md
✓ Update sample configs if they reference changed configuration
✓ Update troubleshooting if error patterns change
```

### Verification Before Completing Changes

- [ ] `opencode.json` matches all documentation examples
- [ ] All three OpenCode documentation files are updated
- [ ] Sample configurations reflect current best practices
- [ ] Code blocks use correct JSON syntax and actual values
- [ ] Cross-references between documentation files work
- [ ] Environment variable references are consistent
- [ ] Version numbers or dates updated if applicable

### Documentation Standards for OpenCode

- **Use actual configuration snippets** from `opencode.json`, not pseudo-code
- **Test JSON validity** - Ensure all code examples are valid JSON
- **Maintain consistency** - Agent names, model identifiers, and commands must match exactly
- **Update timestamps** - If configuration includes dates or version info
- **Verify links** - Check all internal and external links

**The OpenCode configuration serves as a reference for others - documentation accuracy is paramount.**

---

*For OpenCode CLI documentation, visit the official OpenCode documentation.*

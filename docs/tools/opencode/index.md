# OpenCode CLI Configuration

Practical configurations and examples for the OpenCode CLI tool.

## What is OpenCode?

OpenCode CLI integrates multiple AI models, custom commands, and specialized agents into your development workflow.

**Learn more:** [OpenCode Official Documentation](https://opencode.ai/docs)

This guide focuses on **working configurations and integration patterns** from this repository.

> [!NOTE]
> The sample configurations use the native **OpenCode V2** format: `agents` (not `agent`), `commands` (not `command`), ordered `permissions` rules (not `tools`/`permission` maps), and MCP servers under `mcp.servers`. V2 loads project guidance from `AGENTS.md` only. See the [Configuration Guide](configuration.md) for the full V2 reference.

## Repository Contents

The OpenCode CLI provides **two configuration approaches** for different project needs:

### Standard Configuration

**Location:** `docs/tools/opencode/standard-config/`

- **`opencode.json`** - Single-file configuration with tiered agents, custom commands, and MCP servers

**Best for:** Quick setup, straightforward agent needs, centralized configuration

### Agent/SubAgent Configuration

**Location:** `docs/tools/opencode/agent-subagent-config/`

- **`opencode.json`** - `plan` and `build` primary agents
- **`agents/`** - 13 specialized subagent definitions in individual markdown files (installed to `.opencode/agents/`)
- **`prompts/`** - System prompt for the `plan` agent

**Best for:** Complex projects, many specialized agents, team collaboration, modular maintenance

**[📖 Complete Configuration Guide →](configuration.md)** - Detailed setup instructions for both approaches

### MCP Server Examples

**Location:** `docs/mcp/sample-configs/`

Sample configurations for Docker, NPX, and Docker Desktop-based MCP servers.

## Quick Start

### Using Standard Configuration

### 1. Review the Configuration

The standard configuration demonstrates:

- **Tiered AI models** for cost-effective operation
- **Specialized agents** for different task types
- **Custom commands** for common workflows
- **MCP server integration** for extended capabilities

### 2. Copy and Customize

```bash
# Copy the standard configuration to your project
cp docs/tools/opencode/standard-config/opencode.json ~/your-project/opencode.json

# Or copy the agent/subagent configuration
cp docs/tools/opencode/agent-subagent-config/opencode.json ~/your-project/
cp -r docs/tools/opencode/agent-subagent-config/prompts ~/your-project/
mkdir -p ~/your-project/.opencode/agents
cp docs/tools/opencode/agent-subagent-config/agents/*.md ~/your-project/.opencode/agents/
```

Both samples use the built-in GitHub Copilot provider. Sign in once with `/connect` in the OpenCode interface.

### 3. Set Environment Variables

The GitHub MCP server in the standard configuration reads `{env:GITHUB_TOKEN}`, so set the variable before starting OpenCode:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN = "your-github-token"

# Linux/Mac
export GITHUB_TOKEN="your-github-token"
```

### 4. Start Using Commands

Start `opencode` in your project, then run the custom commands from the prompt:

```text
/quick-fix fix the typo in main.js
/review check security in auth.js
/document API endpoints in routes/
```

## Key Features

### 🎯 Tiered Model Approach

The configuration uses different AI models based on task complexity:

**Fast Model** (`github-copilot/gpt-5-mini`)

- Quick fixes and formatting
- Session titles (built-in `title` agent)
- Routine file operations
- Cost-effective for simple tasks

**Balanced Model** (`github-copilot/claude-sonnet-5`)

- General development work (default model)
- Code review
- Architecture decisions
- High-quality code generation

**Multiple Providers** (via GitHub Copilot)

- GPT, Claude, and Gemini models through the GitHub Copilot provider
- Models written as `provider/model`, optionally with a `#variant`
- Switch models based on task needs

### 🤖 Specialized Agents

Pre-configured agents optimize for specific workflows:

#### Quick Agent

- **Purpose**: Fast operations
- **Model**: Lightweight (`github-copilot/gpt-5-mini`)
- **Access**: Full (can modify code)
- **Use for**: Quick fixes, formatting, simple tasks

#### Reviewer Agent

- **Purpose**: Code analysis
- **Model**: Advanced (`github-copilot/claude-sonnet-5`)
- **Access**: Read-only (denies `edit` and `shell`)
- **Use for**: Code review, security audits, analysis

#### Documentation Agent

- **Purpose**: Writing documentation
- **Model**: Lightweight (`github-copilot/claude-haiku-4.5`)
- **Access**: Edits files, denies `shell`
- **Use for**: README files, API docs, guides

### 🧩 Modular Agent/SubAgent Configuration

The **agent/subagent configuration** in `docs/tools/opencode/agent-subagent-config/` demonstrates an advanced modular pattern:

- **13 specialized subagents** in individual markdown files
- **Automatic discovery** from `.opencode/agents/` (project) or `~/.config/opencode/agents/` (global); the file name is the agent ID
- **Modular and maintainable** - add/remove agents by adding/removing files
- **Specialized agents**: API design, security, DevOps, cloud infrastructure, database, testing, documentation, UI/UX, and more

**How it works:**

Instead of defining all agents in `opencode.json`, each agent lives in its own markdown file with YAML frontmatter:

```markdown
---
description: Security audits, vulnerability scanning, and best practices
mode: subagent
model: github-copilot/claude-sonnet-5
permissions:
  - { action: edit, resource: "*", effect: deny }
---

You are a security specialist. Identify vulnerabilities...
```

The Markdown body is the agent's system prompt.

**Available specialized agents:**

- `@api` - REST/GraphQL API design and integration
- `@security` - Security audits and vulnerability scanning
- `@database` - Schema design and query optimization
- `@devops` - CI/CD pipelines and deployment automation
- `@cloud` - AWS/Azure/GCP and Infrastructure as Code
- `@testing` - Test development and TDD
- `@performance` - Performance optimization and profiling
- `@documentation` - Technical documentation
- `@reviewer` - Code review and quality assurance
- `@architect` - System architecture and design patterns
- `@uxui` - UI/UX design and implementation
- `@data` - Data analysis and ETL
- `@research` - Technical research and investigation

**Usage:** ask the primary agent to delegate to a subagent by name:

```text
Use the security subagent to audit the authentication system.
Use the api subagent to design REST endpoints for user management.
Use the devops subagent to create a GitHub Actions CI/CD pipeline.
```

[Learn more in the Configuration Guide →](configuration.md)

### ⚡ Custom Commands

Ready-to-use commands that leverage specialized agents:

| Command | Description | Example |
|---------|-------------|---------|
| `quick-fix` | Fast fixes using lightweight model | `/quick-fix fix typo` |
| `review` | Code review (read-only subagent) | `/review security in api/` |
| `document` | Generate documentation | `/document user API` |
| `build` | Build and test | `/build run tests` |
| `deploy` | Deployment tasks | `/deploy staging environment` |
| `test` | Run and fix tests | `/test user authentication` |

### 🔌 MCP Server Integration

Model Context Protocol servers extend OpenCode's capabilities:

**Included:**

- GitHub MCP (remote) - GitHub integration via Copilot API

**Examples Available:**

- Docker MCP - Containerized services
- Snyk MCP - Security scanning via NPX

**Add Your Own:**

- See [Sample Configurations](samples.md) for examples
- Support for Docker, NPX, and custom servers
- Environment variables through `{env:NAME}` substitution

### 📋 Auto-Loaded Instructions

OpenCode V2 automatically loads guidance from `AGENTS.md` files:

- `~/.config/opencode/AGENTS.md` - Global guidance for every project
- `AGENTS.md` files from the current workspace up to the project root
- Nested `AGENTS.md` files as the agent reads those parts of the project

V2 does not fall back to `CLAUDE.md`, and the `instructions` config key is accepted but its entries are not loaded. Put project conventions in `AGENTS.md`.

## Configuration Structure

```jsonc
{
  // Model selection
  "model": "github-copilot/claude-sonnet-5",
  "default_agent": "build",

  // Specialized agents (the built-in title agent replaces V1 small_model)
  "agents": {
    "title": { "model": "github-copilot/gpt-5-mini" },
    "quick": { /* fast operations */ },
    "reviewer": { /* read-only analysis */ },
    "docs": { /* documentation */ }
  },

  // Custom commands
  "commands": {
    "quick-fix": { /* template and agent */ },
    "review": { /* template, agent, subagent */ }
  },

  // Ordered permission rules; last match wins
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "ask" }
  ],

  // MCP servers
  "mcp": {
    "servers": {
      "github": { /* remote server config */ }
    }
  },

  // Update checks (global config only)
  "update": "notify"
}
```

## Use Cases

### Development Workflow

1. **Quick fixes** - Use `quick-fix` for typos, simple bugs
2. **Feature development** - Default agent for complex implementation
3. **Code review** - Use `review` before committing
4. **Documentation** - Use `document` for README updates
5. **Deployment** - Use `deploy` for release tasks

### Team Collaboration

- **Standardize AI behavior** - Share configuration across team
- **Consistent code quality** - Same review standards
- **Documentation standards** - Unified documentation style
- **Custom workflows** - Team-specific commands

### Project Types

**Web Applications:**

- Build commands for frontend/backend
- Deploy commands for staging/production
- Review commands for security

**Libraries/Packages:**

- Test commands for comprehensive testing
- Document commands for API documentation
- Build commands for compilation and packaging

**Microservices:**

- Deploy commands per service
- Review commands for API contracts
- Test commands for integration testing

## Benefits

### Cost Optimization

- Fast model for simple tasks reduces API costs
- Advanced model only when needed
- Smart agent selection maximizes value

### Quality Assurance

- Read-only review agent prevents accidental changes
- Behavioral baseline ensures consistency
- Automated documentation keeps docs current

### Developer Productivity

- Custom commands reduce repetitive tasks
- Specialized agents optimize for task type
- MCP servers extend capabilities

### Team Consistency

- Shared configuration ensures same patterns
- Behavioral baseline standardizes AI behavior
- Project instructions maintain conventions

## Next Steps

Choose your path:

- **[Configuration Guide](configuration.md)** - Detailed configuration documentation
- **[Sample Configurations](samples.md)** - Real-world MCP server examples
- **[Getting Started](../../index.md)** - General repository guide

## Additional Resources

- **[OpenCode V2 Docs](https://opencode.ai/v2/docs/)** - Complete OpenCode documentation
- **[OpenCode Configuration Schema](https://opencode.ai/config.json)** - JSON schema reference (still describes V1; may flag V2 keys)
- **[Model Context Protocol](https://modelcontextprotocol.io)** - MCP specification and tools

---

**Ready to dive deeper?** Explore the **[Configuration Guide](configuration.md)** for detailed setup instructions and best practices.

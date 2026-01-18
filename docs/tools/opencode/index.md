# OpenCode CLI Configuration

Practical configurations and examples for the OpenCode CLI tool.

## What is OpenCode?

OpenCode CLI integrates multiple AI models, custom commands, and specialized agents into your development workflow.

**Learn more:** [OpenCode Official Documentation](https://opencode.ai/docs)

This guide focuses on **working configurations and integration patterns** from this repository.

## Repository Contents

The OpenCode CLI provides **two configuration approaches** for different project needs:

### Standard Configuration
**Location:** `docs/tools/opencode/standard-config/`

- **`opencode.json`** - Single-file configuration with tiered agents, custom commands, and MCP servers

**Best for:** Quick setup, straightforward agent needs, centralized configuration

### Agent/SubAgent Configuration
**Location:** `docs/tools/opencode/agent-subagent-config/`

- **`opencode.json`** - Minimal primary agent configuration
- **`agent/`** - 13 specialized subagent definitions in individual markdown files
- **`prompts/`** - Reusable prompt templates

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
cp docs/tools/opencode/standard-config/opencode.json ~/your-project/.opencode.json

# Or copy the agent/subagent configuration
cp -r docs/tools/opencode/agent-subagent-config/* ~/your-project/
```

### 3. Set Environment Variables

Some features require authentication tokens:

```bash
# Windows PowerShell
$env:GITHUB_TOKEN = "your-github-token"

# Linux/Mac
export GITHUB_TOKEN="your-github-token"
```

### 4. Start Using Commands

```bash
# Quick fixes with fast model
opencode quick-fix "fix the typo in main.js"

# Code review (read-only)
opencode review "check security in auth.js"

# Generate documentation
opencode document "API endpoints in routes/"
```

## Key Features

### 🎯 Tiered Model Approach

The configuration uses different AI models based on task complexity:

**Fast Model** (`xai/grok-2-mini`)
- Quick fixes and formatting
- Simple refactoring
- Routine file operations
- Cost-effective for simple tasks

**Balanced Model** (`claude-sonnet-4-5`)
- General development work
- Complex refactoring
- Architecture decisions
- High-quality code generation

**Multiple Providers**
- Access to GPT-4o, GPT-5, Claude, Gemini, Grok
- Flexible model selection via GitHub Copilot
- Switch models based on task needs

### 🤖 Specialized Agents

Pre-configured agents optimize for specific workflows:

#### Quick Agent
- **Purpose**: Fast operations
- **Model**: Lightweight (grok-2-mini)
- **Access**: Full (can modify code)
- **Use for**: Quick fixes, formatting, simple tasks

#### Reviewer Agent
- **Purpose**: Code analysis
- **Model**: Advanced (claude-sonnet-4-5)
- **Access**: Read-only (cannot modify)
- **Use for**: Code review, security audits, analysis

#### Documentation Agent
- **Purpose**: Writing documentation
- **Model**: Advanced (claude-sonnet-4-5)
- **Access**: Write docs only (no bash)
- **Use for**: README files, API docs, guides

### 🧩 Modular Agent/SubAgent Configuration

The **agent/subagent configuration** in `docs/tools/opencode/agent-subagent-config/` demonstrates an advanced modular pattern:

- **13 specialized subagents** in individual markdown files
- **Automatic discovery** via YAML frontmatter in markdown files
- **Modular and maintainable** - add/remove agents by adding/removing files
- **Specialized agents**: API design, security, DevOps, cloud infrastructure, database, testing, documentation, UI/UX, and more

**How it works:**

Instead of defining all agents in `opencode.json`, each agent lives in its own markdown file with YAML frontmatter:

```markdown
---
description: Security audits, vulnerability scanning, and best practices
mode: subagent
model: github-copilot/claude-sonnet-4
temperature: 0.1
tools:
  bash: true
---

# Security Agent

This agent specializes in identifying security vulnerabilities...
```

**Available specialized agents:**
- `@api` - REST/GraphQL API design and integration
- `@security` - Security audits and vulnerability scanning
- `@database` - Schema design and query optimization
- `@devops` - CI/CD pipelines and deployment automation
- `@cloud` - AWS/Azure/GCP and Infrastructure as Code
- `@testing` - Test development and TDD
- `@performance` - Performance optimization and profiling
- `@docs` - Technical documentation
- `@reviewer` - Code review and quality assurance
- `@architect` - System architecture and design patterns
- `@uxui` - UI/UX design and implementation
- `@data` - Data analysis and ETL
- `@research` - Technical research and investigation

**Usage:**
```bash
opencode @security "Audit the authentication system"
opencode @api "Design REST endpoints for user management"
opencode @devops "Create a GitHub Actions CI/CD pipeline"
```

[Learn more in the Configuration Guide →](configuration.md)

### ⚡ Custom Commands

Ready-to-use commands that leverage specialized agents:

| Command | Description | Example |
|---------|-------------|---------|
| `quick-fix` | Fast fixes using lightweight model | `opencode quick-fix "fix typo"` |
| `analyze` | Deep code analysis | `opencode analyze "review auth system"` |
| `review` | Code review (read-only) | `opencode review "security in api/"` |
| `document` | Generate documentation | `opencode document "user API"` |
| `refactor` | Intelligent refactoring | `opencode refactor "optimize queries"` |
| `build` | Build and test | `opencode build "run tests"` |
| `deploy` | Deployment tasks | `opencode deploy "staging environment"` |
| `test` | Run and fix tests | `opencode test "user authentication"` |

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
- Easy environment variable configuration

### 📋 Auto-Loaded Instructions

OpenCode automatically reads project context from:

- `AGENTS.md` - AI assistant behavioral guidelines
- `.cursor/rules/*.md` - Project-specific rules
- `README.md` - Project documentation

This ensures AI assistants understand your project's conventions and requirements.

## Configuration Structure

```json
{
  // Model selection
  "model": "anthropic/claude-sonnet-4-5-20250929",
  "small_model": "xai/grok-2-mini",
  
  // Specialized agents
  "agent": {
    "quick": { /* fast operations */ },
    "reviewer": { /* read-only analysis */ },
    "docs": { /* documentation */ }
  },
  
  // Custom commands
  "command": {
    "quick-fix": { /* template and agent */ },
    "review": { /* template and agent */ }
  },
  
  // Tool permissions
  "tools": {
    "write": true,
    "edit": true,
    "bash": true
  },
  
  // MCP servers
  "mcp": {
    "github": { /* remote server config */ }
  },
  
  // Auto-loaded instructions
  "instructions": [
    "AGENTS.md",
    ".cursor/rules/*.md",
    "README.md"
  ]
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
- **[LLM Baseline Behaviors](../../LLM-BaselineBehaviors.md)** - Understanding the instruction hierarchy

## Additional Resources

- **[OpenCode Official Docs](https://opencode.ai/docs)** - Complete OpenCode CLI documentation
- **[OpenCode Configuration Schema](https://opencode.ai/config.json)** - JSON schema reference
- **[Model Context Protocol](https://modelcontextprotocol.io)** - MCP specification and tools
- **[LLM Baseline Behaviors](../../LLM-BaselineBehaviors.md)** - Behavioral guidelines for this repository

---

**Ready to dive deeper?** Explore the **[Configuration Guide](configuration.md)** for detailed setup instructions and best practices.

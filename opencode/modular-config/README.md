# Modular Subagent Configuration for OpenCode

This directory demonstrates an advanced **modular configuration pattern** for OpenCode that automatically loads specialized subagents from individual markdown files. This approach provides a modular, maintainable way to manage complex multi-agent workflows.

**Special thanks to Larry Bailey for providing this very cool modular configuration for opencode!**

## Overview

Instead of defining all agents directly in `opencode.json`, this configuration uses OpenCode's instruction loading feature to automatically discover and configure subagents from individual markdown files in the `agent/` directory.

### Key Benefits

- **Modularity**: Each agent is defined in its own file, making them easy to add, remove, or modify
- **Maintainability**: Agent configurations are self-contained and well-documented
- **Discoverability**: New agents are automatically available by adding a markdown file
- **Version Control**: Track changes to individual agents independently
- **Reusability**: Share specific agent configurations across projects

## How It Works

### 1. Main Configuration (`opencode.json`)

The main configuration file is minimal and defines only **primary agents** (plan and build):

```json
{
  "agent": {
    "plan": {
      "mode": "primary",
      "description": "Planning and analysis without making changes, while leveraging subagents...",
      "model": "github-copilot/claude-sonnet-4.5",
      "temperature": 0.1,
      "tools": {
        "write": true,
        "bash": false
      }
    },
    "build": {
      "mode": "primary",
      "description": "Full development work with all tools enabled, while leveraging subagents...",
      "model": "github-copilot/grok-code-fast-1",
      "temperature": 0.3,
      "tools": {
        "write": true,
        "edit": true,
        "bash": true
      }
    }
  }
}
```

### 2. Agent Definitions (`agent/*.md`)

Each specialized agent is defined in a markdown file with YAML frontmatter containing the agent configuration:

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

The API agent is designed to assist with API design...
```

OpenCode automatically reads these files and configures the agents based on the frontmatter properties.

## Available Subagents

This configuration includes 13 specialized subagents:

| Agent | Description | Model | Temperature | Write Access |
|-------|-------------|-------|-------------|--------------|
| **api** | REST/GraphQL API design, OpenAPI specs, integration | Grok Code Fast 1 | 0.2 | ✅ Full |
| **architect** | System design, architecture decisions | Claude Sonnet 4.5 | 0.2 | ❌ Read-only |
| **cloud** | AWS/Azure/GCP configurations, Infrastructure as Code | Grok Code Fast 1 | 0.1 | ✅ Full |
| **data** | Data analysis, ETL pipelines, data validation | GPT-5-mini | 0.2 | ✅ Full |
| **database** | Schema design, query optimization, migrations | Grok Code Fast 1 | 0.1 | ✅ Full |
| **devops** | CI/CD pipelines, Docker, Kubernetes, deployment | GPT-5-mini | 0.2 | ✅ Full |
| **documentation** | Technical docs, API docs, README files | Claude Haiku 4.5 | 0.3 | ✅ Docs only |
| **performance** | Performance profiling, optimization, analysis | Grok Code Fast 1 | 0.1 | ✅ Full |
| **research** | Technical discovery, product research, doc analysis | GPT-5-mini | 0.2 | ❌ Read-only |
| **reviewer** | Code review for best practices and issues | Claude Sonnet 4 | 0.1 | ❌ Read-only |
| **security** | Security audits, vulnerability scanning | Claude Sonnet 4 | 0.1 | ❌ Bash only |
| **testing** | Unit tests, integration tests, test optimization | GPT-5-mini | 0.2 | ✅ Full |
| **uxui** | UI/UX design evaluation, accessibility, styling | Gemini 2.5 Pro | 0.3 | ✅ No bash |

### Agent Configuration Properties

Each agent's YAML frontmatter can include:

#### Required Properties
- **`description`**: Brief description of the agent's purpose and capabilities
- **`mode`**: Agent mode (`subagent` for specialized agents, `primary` for main agents)

#### Optional Properties
- **`model`**: AI model to use (defaults to main config model if not specified)
  - Format: `provider/model-name` (e.g., `github-copilot/grok-code-fast-1`)
- **`temperature`**: Creativity level (0.0-1.0)
  - `0.1-0.2`: Deterministic, consistent code generation
  - `0.3-0.4`: Balanced creativity
  - `0.5+`: More creative/exploratory
- **`tools`**: Tool permissions object
  - `write`: Create new files
  - `edit`: Modify existing files
  - `bash`: Execute shell commands
  - Omit tools that should be disabled (defaults to `false`)

## Usage Examples

### Calling Specific Agents

With this configuration, OpenCode's primary agents (plan/build) automatically delegate to specialized subagents based on the task context. You can also invoke specific agents directly:

```bash
# API design and documentation
opencode @api "Design a REST API for user authentication"

# Security review (read-only, no changes)
opencode @security "Audit the authentication system for vulnerabilities"

# Database optimization
opencode @database "Optimize the slow query in user_stats table"

# UI/UX improvements
opencode @uxui "Improve the accessibility of the login form"

# Infrastructure as Code
opencode @cloud "Create a Terraform module for AWS ECS deployment"

# Code review (read-only analysis)
opencode @reviewer "Review the payment processing code for best practices"

# Technical research (no code changes)
opencode @research "Compare Redis vs Memcached for our caching needs"

# Documentation creation
opencode @documentation "Generate API documentation for the user endpoints"
```

### Primary Agent Workflow

The `plan` and `build` agents leverage subagents automatically:

```bash
# Planning phase - analyzes and delegates to subagents
opencode @plan "Design a microservices architecture for the e-commerce platform"
# May delegate to: @architect, @cloud, @database, @security

# Build phase - implements changes with subagent support
opencode @build "Implement the user authentication API"
# May delegate to: @api, @security, @database, @testing
```

## Adding New Agents

To add a new specialized agent:

1. **Create a new markdown file** in the `agent/` directory (e.g., `agent/mobile.md`)

2. **Add YAML frontmatter** with configuration:

```markdown
---
description: Mobile app development for iOS and Android
mode: subagent
model: github-copilot/grok-code-fast-1
temperature: 0.2
tools:
  write: true
  edit: true
  bash: true
---

# Agent Purpose

The Mobile agent specializes in mobile app development...

## Core Responsibilities

- Develop iOS and Android applications
- Optimize mobile UI/UX
- Handle platform-specific features

## Focus Areas

### iOS Development
- Swift/SwiftUI best practices
- iOS SDK integration

### Android Development
- Kotlin best practices
- Android SDK integration

## Best Practices

- Test on multiple device sizes
- Optimize for battery usage
- Follow platform design guidelines
```

3. **No configuration changes needed** - OpenCode automatically discovers the new agent

4. **Use the agent**: `opencode @mobile "Create a login screen for iOS"`

## Configuration Patterns

### Read-Only Agents (Review/Analysis)

For agents that should only analyze without making changes:

```yaml
---
description: Architecture review and recommendations
mode: subagent
model: github-copilot/claude-sonnet-4.5
temperature: 0.1
# No tools defined = read-only access
---
```

### Documentation-Only Agents

For agents that should only modify documentation:

```yaml
---
description: Documentation writing and maintenance
mode: subagent
model: github-copilot/claude-haiku-4.5
temperature: 0.3
tools:
  write: true
  edit: true
  bash: false  # Explicitly disable bash
---
```

### Full-Access Development Agents

For agents that need complete control:

```yaml
---
description: Full-stack web development
mode: subagent
model: github-copilot/grok-code-fast-1
temperature: 0.2
tools:
  write: true
  edit: true
  bash: true
---
```

## Model Selection Guide

### Fast & Cost-Effective
- **GPT-5-mini**: Quick tasks, testing, data processing
- **Claude Haiku 4.5**: Fast documentation, simple queries

### Balanced Performance
- **Grok Code Fast 1**: General development, APIs, databases
- **Claude Sonnet 4.5**: Code review, security analysis

### Advanced Reasoning
- **Claude Sonnet 4.5**: Complex architecture, planning
- **Gemini 2.5 Pro**: Creative tasks, UI/UX design
- **Qwen2.5-Coder:32b**: Deep code analysis (local model)

### Specialized Tasks
- **Grok 2**: Alternative to Grok Code Fast 1 for general tasks
- **O1**: Advanced reasoning and problem-solving

## Best Practices

### Temperature Settings
- **0.1-0.2**: Code generation, security reviews, database queries
- **0.3**: General development, API design
- **0.4-0.5**: Documentation, UI/UX, creative tasks

### Tool Permissions
- **Grant `bash` access carefully**: Only for agents that need to run tests, deployments, or system commands
- **Restrict review agents**: Keep `@reviewer`, `@security`, and `@research` read-only
- **Documentation agents**: Enable `write` and `edit`, but disable `bash`

### Agent Naming
- Use **lowercase** names (e.g., `api`, not `API`)
- Use **descriptive** names (e.g., `uxui`, not `ui`)
- Keep names **short** for easy invocation (e.g., `@api` vs `@api-design`)

### File Organization
- **One agent per file**: Keep each agent definition in its own markdown file
- **Descriptive filenames**: Match the filename to the agent name (e.g., `api.md` → `@api`)
- **Clear documentation**: Include purpose, responsibilities, and examples in each file

## Troubleshooting

### Agent Not Available
- **Check filename**: Must be in `agent/` directory with `.md` extension
- **Verify frontmatter**: YAML must be valid and properly formatted
- **Restart OpenCode**: Configuration changes may require restart

### Agent Not Behaving as Expected
- **Check model**: Ensure the specified model is accessible via GitHub Copilot
- **Verify temperature**: Adjust for desired behavior (lower = more deterministic)
- **Review tool permissions**: Confirm the agent has necessary access

### Performance Issues
- **Use faster models**: Switch to GPT-5-mini or Claude Haiku for simpler tasks
- **Lower temperature**: Reduces processing time for deterministic tasks
- **Limit tool access**: Fewer tools = faster initialization

## Migration from Traditional Config

To convert a traditional `opencode.json` configuration to this modular pattern:

1. **Keep primary agents** in `opencode.json` (plan, build, etc.)
2. **Extract subagents** to individual files in `agent/`:
   - Copy the agent's `description`, `model`, `temperature`, and `tools`
   - Create YAML frontmatter with these properties
   - Add documentation about the agent's purpose and usage
3. **Remove subagent definitions** from `opencode.json`
4. **Test each agent** to ensure configuration is correct

## Advanced Features

### Agent Inheritance (Future Enhancement)

While not currently supported, you could structure agents hierarchically:

```
agent/
  base/
    code-agent.md          # Base configuration for code agents
    review-agent.md        # Base configuration for review agents
  api.md                   # Inherits from code-agent
  reviewer.md              # Inherits from review-agent
```

### Environment-Specific Agents

Create environment-specific agent directories:

```
agent/
  development/
    *.md                   # Development-focused agents
  production/
    *.md                   # Production-optimized agents
```

Switch by changing OpenCode's instruction loading path.

## Contributing

To contribute new agents or improve existing ones:

1. **Follow the established pattern**: Use YAML frontmatter with consistent properties
2. **Document thoroughly**: Include purpose, responsibilities, and examples
3. **Test before submitting**: Verify the agent works as expected
4. **Update this README**: Add the new agent to the table above

---

*This modular configuration pattern demonstrates the power and flexibility of OpenCode's instruction loading feature, enabling scalable and maintainable multi-agent workflows.*

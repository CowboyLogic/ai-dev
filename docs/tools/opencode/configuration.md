# OpenCode Configuration Guide

Detailed guide to configuring and using the OpenCode CLI with the configurations provided in this repository.

## Configuration Approaches

This repository provides two configuration approaches for OpenCode:

### Standard Configuration
**Location:** `docs/reference/opencode/standard-config/`

A single-file configuration approach where all agents, commands, and settings are defined in one `opencode.json` file.

**Best for:**
- Quick setup and getting started
- Projects with straightforward agent needs (3-5 agents)
- Centralizing all configuration in one place
- Simple, easy-to-understand configuration

### Agent/SubAgent Configuration  
**Location:** `docs/reference/opencode/agent-subagent-config/`

A modular configuration approach where agents are defined in individual markdown files with YAML frontmatter.

**Best for:**
- Complex projects with many specialized agents (5+)
- Team collaboration where different members manage different agents
- Modular, maintainable agent definitions
- Automatic agent discovery from files
- Sharing/reusing agents across projects

---

## Standard Configuration Structure

The `opencode.json` file in `standard-config/` is organized into several key sections:

### 1. Schema and Models

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "anthropic/claude-sonnet-4-5-20250929",
  "small_model": "xai/grok-2-mini"
}
```

**Purpose:**
- Schema provides validation and autocomplete in editors
- Primary model for complex tasks
- Small model for fast, simple operations

**Customization:**
- Change models based on your provider and preferences
- Balance cost vs. capability
- Test different models for your use cases

### 2. Provider Configuration

```json
{
  "provider": {
    "github": {
      "name": "GitHub Copilot",
      "models": {
        "gpt-4o": { "name": "GPT-4o via Copilot" },
        "claude-sonnet-4-5": { "name": "Claude Sonnet 4.5 via Copilot" }
        // ... more models
      }
    }
  }
}
```

**Available Models:**
- GPT-4o, GPT-4.1, GPT-5, GPT-5 mini, GPT-5 Codex
- Claude 3.5 Sonnet, Haiku 4.5, Opus 4.1, Sonnet 4, Sonnet 4.5
- Gemini 2.5 Pro
- Grok Code Fast 1, Raptor mini

**Usage:**
- Access models via GitHub Copilot subscription
- Switch models using provider prefix: `github/gpt-4o`
- Choose model based on task complexity

### 3. Specialized Agents

Agents are pre-configured AI assistants optimized for specific tasks.

#### Quick Agent Configuration

```json
{
  "agent": {
    "quick": {
      "description": "Fast agent for basic tasks",
      "mode": "primary",
      "model": "xai/grok-2-mini",
      "temperature": 0.1,
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
  }
}
```

**Properties:**
- **description** - Human-readable purpose
- **mode** - `primary` (main agent) or `subagent` (specialized)
- **model** - Which AI model to use
- **temperature** - Randomness (0.0 = deterministic, 1.0 = creative)
- **tools** - Available tool permissions

**Best Practices:**
- Use fast models (grok-2-mini, gpt-4o-mini) for quick agents
- Set low temperature (0.1) for deterministic code generation
- Grant full tool access for implementation agents

#### Reviewer Agent Configuration

```json
{
  "agent": {
    "reviewer": {
      "description": "Code review agent (read-only)",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-5-20250929",
      "temperature": 0.1,
      "tools": {
        "write": false,
        "edit": false,
        "bash": false,
        "read": true,
        "list": true,
        "glob": true,
        "grep": true,
        "webfetch": true
      }
    }
  }
}
```

**Key Features:**
- **Read-only** - Cannot modify files (write, edit, bash disabled)
- **Advanced model** - Uses capable model for deep analysis
- **Web access** - Can fetch documentation for research

**Use Cases:**
- Security audits
- Code quality reviews
- Architecture analysis
- Best practices checking

#### Documentation Agent Configuration

```json
{
  "agent": {
    "docs": {
      "description": "Documentation agent",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-5-20250929",
      "temperature": 0.3,
      "tools": {
        "write": true,
        "edit": true,
        "bash": false,
        "read": true,
        "list": true,
        "glob": true,
        "grep": true,
        "webfetch": true
      }
    }
  }
}
```

**Key Features:**
- **Higher temperature** (0.3) - More creative for writing
- **No bash access** - Can't run system commands
- **Write/edit enabled** - Can create and modify documentation
- **Web access** - Can research examples and references

### 4. Custom Commands

Commands are shortcuts that combine templates with specific agents.

#### Command Structure

```json
{
  "command": {
    "quick-fix": {
      "template": "Make a quick fix for: $ARGUMENTS. Keep it simple and fast.",
      "description": "Quick fixes using fast model",
      "agent": "quick"
    }
  }
}
```

**Properties:**
- **template** - Instructions with `$ARGUMENTS` placeholder
- **description** - Shown in help text
- **agent** - (Optional) Which agent to use

#### Creating Custom Commands

**Example: Testing Command**
```json
{
  "test-api": {
    "template": "Test the API endpoint: $ARGUMENTS. Check request/response and error handling.",
    "description": "Test API endpoints",
    "agent": "quick"
  }
}
```

Usage: `opencode test-api "/users/:id"`

**Example: Database Command**
```json
{
  "migrate": {
    "template": "Create a database migration for: $ARGUMENTS. Include rollback logic.",
    "description": "Generate database migration"
  }
}
```

Usage: `opencode migrate "add user preferences table"`

**Example: Review Command**
```json
{
  "security-check": {
    "template": "Perform security review of: $ARGUMENTS. Focus on authentication, authorization, and data validation.",
    "description": "Security-focused code review",
    "agent": "reviewer"
  }
}
```

Usage: `opencode security-check "src/auth/"`

### 5. Tool Configuration

Control which tools are available globally:

```json
{
  "tools": {
    "write": true,
    "edit": true,
    "read": true,
    "list": true,
    "bash": true,
    "glob": true,
    "grep": true,
    "webfetch": true,
    "task": true,
    "todowrite": true,
    "todoread": true
  }
}
```

**Tool Descriptions:**

| Tool | Purpose |
|------|---------|
| `write` | Create new files |
| `edit` | Modify existing files |
| `read` | Read file contents |
| `list` | List directory contents |
| `bash` | Execute shell commands |
| `glob` | Search for files by pattern |
| `grep` | Search file contents |
| `webfetch` | Fetch web resources |
| `task` | Manage tasks |
| `todowrite` | Create/update todos |
| `todoread` | Read todos |

**Security Considerations:**
- Disable `bash` for review-only agents
- Disable `write`/`edit` for analysis-only agents
- Grant minimal necessary permissions

### 6. Permission Configuration

Control how OpenCode requests permission for operations:

```json
{
  "permission": {
    "bash": "allow",
    "write": "allow",
    "edit": "allow"
  }
}
```

**Permission Levels:**
- **`allow`** - Execute without prompting
- **`ask`** - Prompt user for confirmation
- **`deny`** - Never allow

**Recommendations:**
- Use `ask` for destructive operations in shared environments
- Use `allow` for personal development workflow
- Use `deny` for restricted operations in production

### 7. MCP Server Configuration

Model Context Protocol servers extend OpenCode with additional capabilities.

#### Remote MCP Server

```json
{
  "mcp": {
    "github": {
      "type": "remote",
      "url": "https://api.githubcopilot.com/mcp/",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    }
  }
}
```

**Properties:**
- **type** - `remote` for HTTP servers
- **url** - Server endpoint
- **enabled** - Enable/disable server
- **headers** - HTTP headers (use `${VAR}` for environment variables)

#### Local MCP Server (Docker)

```json
{
  "mcp": {
    "my-docker-server": {
      "type": "local",
      "command": ["docker", "run", "--rm", "-i", "my-server:latest"],
      "enabled": true,
      "environment": {
        "API_KEY": "${MY_API_KEY}",
        "DEBUG": "true"
      },
      "timeout": 10000
    }
  }
}
```

**Properties:**
- **type** - `local` for local processes
- **command** - Array of command parts
- **environment** - Environment variables for the process
- **timeout** - Milliseconds before timeout

#### Local MCP Server (NPX)

```json
{
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
}
```

**NPX Servers:**
- Use `npx -y` to auto-install packages
- Common for Node.js-based MCP servers
- Examples: Snyk, custom npm packages

**Remember:**
- Enable the tool in the `tools` section: `"snyk": true`
- Set required environment variables before running
- Adjust timeout for slow-starting servers

### 8. Instructions Loading

```json
{
  "instructions": [
    "AGENTS.md",
    ".cursor/rules/*.md",
    "README.md"
  ]
}
```

**Purpose:**
- Automatically load project-specific instructions
- Provide context to AI assistants
- Ensure consistent behavior across projects

**File Order:**
- Files are loaded in the order specified
- Later files can override earlier ones
- Glob patterns (`*.md`) are supported

**Best Practices:**
- Include behavioral baselines (AGENTS.md)
- Add project-specific rules
- Reference documentation files

## Modular Agent Configuration

For complex projects with many specialized agents, the `agent-subagent-config/` directory demonstrates an advanced pattern where each agent is defined in its own markdown file with YAML frontmatter.

### Architecture

**Main Configuration** (`agent-subagent-config/opencode.json`):
- Defines only **primary agents** (plan, build)
- Minimal configuration focused on workflow orchestration
- Delegates to specialized subagents automatically

**Agent Definitions** (`agent-subagent-config/agent/*.md`):
- Each agent in a separate markdown file
- YAML frontmatter contains configuration
- Automatic discovery via instruction loading

### Example Agent File

**`agent/security.md`:**
```markdown
---
description: Security audits, vulnerability scanning, and best practices
mode: subagent
model: github-copilot/claude-sonnet-4.5
temperature: 0.1
tools:
  bash: true
---

# Agent Purpose

The Security agent focuses on identifying vulnerabilities and ensuring
best practices for secure coding and infrastructure.

## Core Responsibilities

- Conduct security audits
- Identify and mitigate vulnerabilities
- Provide recommendations for secure coding practices
```

### Configuration Properties

**YAML Frontmatter:**

**Required:**
- `description` - Agent's purpose and capabilities
- `mode` - `subagent` for specialized agents

**Optional:**
- `model` - AI model in `provider/model-name` format
- `temperature` - Creativity level (0.0-1.0)
- `tools` - Permission object with `write`, `edit`, `bash` properties

### Available Modular Agents

| Agent | Focus | Model | Access |
|-------|-------|-------|--------|
| `api` | REST/GraphQL API design | Grok Code Fast 1 | Full |
| `architect` | System architecture | Claude Sonnet 4.5 | Read-only |
| `cloud` | AWS/Azure/GCP, IaC | Grok Code Fast 1 | Full |
| `data` | Data analysis, ETL | GPT-5-mini | Full |
| `database` | Schema design, optimization | Grok Code Fast 1 | Full |
| `devops` | CI/CD, Docker, Kubernetes | GPT-5-mini | Full |
| `documentation` | Technical docs, API docs | Claude Haiku 4.5 | Docs only |
| `performance` | Profiling, optimization | Grok Code Fast 1 | Full |
| `research` | Technical discovery | GPT-5-mini | Read-only |
| `reviewer` | Code review | Claude Sonnet 4.5 | Read-only |
| `security` | Security audits | Claude Sonnet 4.5 | Bash only |
| `testing` | Unit/integration tests | GPT-5-mini | Full |
| `uxui` | UI/UX design, accessibility | Gemini 2.5 Pro | No bash |

### Usage

**Direct Invocation:**
```bash
opencode @api "Design REST API for user authentication"
opencode @security "Audit authentication system for vulnerabilities"
opencode @database "Optimize slow query in user_stats table"
opencode @devops "Create GitHub Actions workflow for deployment"
```

**Primary Agent Delegation:**
```bash
# Plan agent automatically delegates to relevant subagents
opencode @plan "Design microservices architecture"

# Build agent implements with subagent support
opencode @build "Implement user authentication API"
```

### Adding New Agents

1. Create `agent/yourname.md`
2. Add YAML frontmatter with configuration
3. Document purpose and responsibilities
4. Agent automatically available as `@yourname`

**Example:**
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

Specializes in mobile app development...
```

### Benefits

- **Modularity** - Add/remove agents by adding/removing files
- **Maintainability** - Each agent is self-contained
- **Discoverability** - OpenCode automatically finds agents
- **Reusability** - Share agents across projects
- **Version Control** - Track changes independently

See `docs/reference/opencode/agent-subagent-config/README.md` for comprehensive documentation.

### 9. Additional Settings

```json
{
  "autoupdate": true,
  "theme": "opencode",
  "share": "manual"
}
```

**Settings:**
- **autoupdate** - Automatically update OpenCode CLI
- **theme** - UI theme preference
- **share** - Sharing mode (`auto`, `manual`, `never`)

## Environment Variables

### Setting Variables

**Windows PowerShell:**
```powershell
$env:GITHUB_TOKEN = "ghp_your_token_here"
$env:SNYK_TOKEN = "your_snyk_token"
$env:OPENAI_API_KEY = "sk-your_key"
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN="ghp_your_token_here"
export SNYK_TOKEN="your_snyk_token"
export OPENAI_API_KEY="sk-your_key"
```

### Referencing in Config

Use `${VARIABLE_NAME}` syntax:

```json
{
  "environment": {
    "TOKEN": "${MY_TOKEN}",
    "API_URL": "${API_ENDPOINT}"
  },
  "headers": {
    "Authorization": "Bearer ${AUTH_TOKEN}"
  }
}
```

### Common Variables

- `GITHUB_TOKEN` - GitHub personal access token
- `SNYK_TOKEN` - Snyk API token
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key

## Best Practices

### Model Selection

**For Simple Tasks:**
- Use `xai/grok-2-mini` or `gpt-4o-mini`
- Fast and cost-effective
- Good for formatting, quick fixes

**For Complex Tasks:**
- Use `claude-sonnet-4-5` or `gpt-4o`
- Better reasoning and understanding
- Worth the cost for quality

**For Deep Reasoning:**
- Use `claude-opus-4-1` or `o1`
- Advanced problem-solving
- Use sparingly due to cost

### Temperature Settings

| Temperature | Use Case |
|-------------|----------|
| 0.0-0.1 | Code generation, bug fixes |
| 0.2-0.3 | Documentation, refactoring |
| 0.4-0.5 | Creative writing, brainstorming |

### Agent Design

**Quick Agent:**
- Fast model + low temperature + full access
- For routine development tasks

**Review Agent:**
- Advanced model + low temperature + read-only
- For quality assurance

**Docs Agent:**
- Advanced model + medium temperature + no bash
- For documentation work

### Security

- Never hardcode secrets in configuration
- Always use environment variables for tokens
- Use `${VARIABLE}` syntax for references
- Set appropriate file permissions on config files

## Troubleshooting

### Common Issues

**OpenCode not finding config:**
- Place `opencode.json` in project root
- Or use `.opencode.json` (hidden file)
- Check file permissions

**MCP server failing:**
- Verify environment variables are set
- Check Docker/NPX is installed
- Increase timeout value
- Enable the tool in `tools` section

**Wrong model being used:**
- Check `model` and `small_model` settings
- Verify agent assignments in commands
- Check provider configuration

**Commands not working:**
- Validate JSON syntax
- Restart OpenCode after changes
- Check command is defined in config

## Advanced Configuration

### Multiple MCP Servers

```json
{
  "mcp": {
    "github": { /* remote server */ },
    "snyk": { /* local NPX server */ },
    "docker-tools": { /* local Docker server */ }
  },
  "tools": {
    "github": true,
    "snyk": true,
    "docker-tools": true
  }
}
```

### Conditional Commands

```json
{
  "command": {
    "test-backend": {
      "template": "Test backend code: $ARGUMENTS",
      "agent": "quick"
    },
    "test-frontend": {
      "template": "Test frontend code: $ARGUMENTS",
      "agent": "quick"
    }
  }
}
```

### Project-Specific Overrides

Create `.opencode.json` in project root to override settings:

```json
{
  "model": "openai/gpt-4o",
  "instructions": [
    "../reference/agents/baseline-behaviors.md",
    "PROJECT_RULES.md"
  ]
}
```

---

## Agent/SubAgent Configuration Pattern

The modular configuration in `docs/reference/opencode/agent-subagent-config/` uses a different approach where agents are defined in individual markdown files.

### Structure

```
agent-subagent-config/
├── opencode.json          # Minimal primary agent config
├── agent/                 # Individual agent definitions
│   ├── api.md
│   ├── security.md
│   ├── devops.md
│   └── ... (13 total)
├── prompts/               # Reusable prompt templates
│   └── plan.txt
└── README.md              # Full documentation
```

### How It Works

**1. Minimal Main Config** (`opencode.json`):

```json
{
  "agent": {
    "plan": {
      "mode": "primary",
      "description": "Planning and analysis",
      "model": "github-copilot/claude-sonnet-4.5",
      "tools": { "write": false, "bash": false }
    }
  },
  "instructions": [
    "agent/*.md",  // Auto-loads all agents
    "prompts/*.txt"
  ]
}
```

**2. Individual Agent Files** (`agent/security.md`):

```markdown
---
description: Security audits, vulnerability scanning, and best practices
mode: subagent
model: github-copilot/claude-sonnet-4
temperature: 0.1
tools:
  bash: true
  write: false
---

# Security Agent

This agent specializes in identifying security vulnerabilities...

## Capabilities
- OWASP Top 10 analysis
- Dependency vulnerability scanning
- Code injection detection
- Authentication/authorization review
```

**3. Automatic Discovery:**

When OpenCode loads, it:
1. Reads `opencode.json`
2. Processes `instructions` glob patterns
3. Discovers all `agent/*.md` files
4. Parses YAML frontmatter to configure each agent
5. Makes agents available via `@` syntax

**4. Usage:**

```bash
opencode @security "Audit authentication in auth.js"
opencode @api "Design REST endpoints for user management"
opencode @devops "Create GitHub Actions CI/CD pipeline"
```

### Available Specialized Agents

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| `@api` | API design and integration | write, edit, bash |
| `@architect` | System architecture | read, write |
| `@cloud` | Cloud infrastructure (AWS/Azure/GCP) | write, edit, bash |
| `@data` | Data analysis and ETL | write, bash |
| `@database` | Database design and optimization | write, edit |
| `@devops` | CI/CD and deployment | write, edit, bash |
| `@docs` | Technical documentation | write, edit |
| `@performance` | Performance optimization | read, edit, bash |
| `@research` | Technical research | read, webfetch |
| `@reviewer` | Code review | read only |
| `@security` | Security audits | read, bash |
| `@testing` | Test development | write, edit, bash |
| `@uxui` | UI/UX design | write, edit |

### Benefits

✅ **Modularity** - Each agent in its own file  
✅ **Maintainability** - Easy to add/remove/modify agents  
✅ **Discoverability** - New agents automatically available  
✅ **Version Control** - Track individual agent changes  
✅ **Reusability** - Share specific agents across projects  
✅ **Team Collaboration** - Different members own different agents  
✅ **Documentation** - Agent capabilities documented in-file

### Creating Custom Agents

**1. Create a new markdown file** in `agent/` directory:

```markdown
---
description: Your agent's purpose
mode: subagent
model: github-copilot/claude-sonnet-4.5
temperature: 0.1
tools:
  write: true
  edit: true
  bash: false
---

# My Custom Agent

Detailed description of what this agent does...

## Capabilities
- Capability 1
- Capability 2

## Best Used For
- Use case 1
- Use case 2
```

**2. Save as `agent/myagent.md`**

**3. Restart OpenCode** (if running)

**4. Use the agent:**

```bash
opencode @myagent "your task here"
```

### When to Use This Pattern

**Choose Agent/SubAgent Configuration when:**
- ✅ You need 5+ specialized agents
- ✅ Different team members manage different agents
- ✅ You want modular, easy-to-maintain configuration
- ✅ You need to share/reuse agents across projects
- ✅ Agents have complex, well-documented capabilities

**Choose Standard Configuration when:**
- ✅ You need 3-5 agents maximum
- ✅ You prefer everything in one file
- ✅ Configuration is relatively simple
- ✅ Quick setup is priority

### Full Documentation

See [`agent-subagent-config/README.md`](../../reference/opencode/agent-subagent-config/README.md) for:
- Complete agent descriptions
- Usage examples for each agent
- Advanced customization patterns
- Team workflow recommendations

## Next Steps

- **[Sample Configurations](samples.md)** - Real-world MCP server examples
- **[OpenCode Overview](index.md)** - Feature overview and use cases
- **[Agent Configuration](../../agents/configuration.md)** - General agent configuration guide

---

**Need help?** Check the [OpenCode official documentation](https://opencode.ai) or review the sample configurations.

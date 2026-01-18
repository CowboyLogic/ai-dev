# Agent Configuration

This guide explains how to configure and use AI agents based on the behavioral baseline defined in this repository.

## Overview

Agent configuration in this repository follows a layered approach where specialized configurations build upon the foundational behavioral baseline. This ensures consistency while allowing flexibility for specific use cases.

## Configuration Layers

### Layer 1: Behavioral Baseline

The **[LLM Baseline Behaviors](../LLM-BaselineBehaviors.md)** document serves as the foundation. All agents should:

1. Read and internalize this baseline
2. Apply these behaviors as default
3. Override only when explicitly directed

### Layer 2: Tool-Specific Guidelines

Tool-specific `AGENTS.md` files provide additional context:

- **[Root AGENTS.md](https://github.com/CowboyLogic/ai-dev/blob/main/AGENTS.md)** - Repository-wide guidelines
- **[OpenCode Configuration](../tools/opencode/configuration.md)** - OpenCode CLI specific

### Layer 3: Project-Specific Rules

Individual projects may add:

- `.cursor/rules/` files for Cursor IDE
- `.github/../copilot-instructions.md` for GitHub Copilot
- Custom instruction files for other tools

### Layer 4: User Directives

Direct user instructions in conversation always take highest priority.

## Instruction Priority Hierarchy

```
┌─────────────────────────────────┐
│   User Directives (Highest)    │  ← "Do it this way"
├─────────────────────────────────┤
│   Project-Specific Rules        │  ← .cursor/rules/*.md
├─────────────────────────────────┤
│   Tool-Specific Guidelines      │  ← docs/reference/opencode/standard-config/AGENTS.md
├─────────────────────────────────┤
│   Behavioral Baseline           │  ← docs/reference/../LLM-BaselineBehaviors.md
└─────────────────────────────────┘
```

## Practical Examples

### Example 1: OpenCode CLI

The OpenCode configuration demonstrates specialized agents:

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
        "read": true
      }
    }
  }
}
```

**Purpose:** Fast operations with minimal overhead

**Use cases:**
- Code formatting
- Simple bug fixes
- Quick refactoring
- Routine file operations

#### Reviewer Agent Configuration

```json
{
  "agent": {
    "reviewer": {
      "description": "Code review agent (read-only)",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-5",
      "temperature": 0.1,
      "tools": {
        "write": false,
        "edit": false,
        "bash": false,
        "read": true,
        "grep": true,
        "webfetch": true
      }
    }
  }
}
```

**Purpose:** Analysis without modifications

**Use cases:**
- Code reviews
- Security audits
- Architecture analysis
- Documentation review

#### Documentation Agent Configuration

```json
{
  "agent": {
    "docs": {
      "description": "Documentation agent",
      "mode": "subagent",
      "model": "anthropic/claude-sonnet-4-5",
      "temperature": 0.3,
      "tools": {
        "write": true,
        "edit": true,
        "read": true,
        "bash": false
      }
    }
  }
}
```

**Purpose:** Documentation creation and maintenance

**Use cases:**
- Writing README files
- Creating API documentation
- Updating guides and tutorials
- Generating code comments

### Example 2: GitHub Copilot

For GitHub Copilot Chat, reference the baseline in workspace settings:

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": "agents/../LLM-BaselineBehaviors.md"
    }
  ]
}
```

### Example 3: Cursor IDE

Place instructions in `.cursor/rules/`:

```markdown
# .cursor/rules/baseline.md

Follow the behavioral baseline defined in:
agents/../LLM-BaselineBehaviors.md

Additional project rules:
- Use TypeScript strict mode
- Prefer functional programming patterns
- Write tests for all new features
```

## Agent Types and Use Cases

### General Purpose Agent

**Characteristics:**
- Balanced model selection
- Full tool access
- Moderate temperature (0.1-0.2)

**Best for:**
- General development tasks
- Feature implementation
- Bug fixing
- Refactoring

### Fast Agent

**Characteristics:**
- Lightweight model (e.g., grok-2-mini, gpt-4o-mini)
- Full tool access
- Low temperature (0.1)

**Best for:**
- Quick fixes
- Code formatting
- Simple refactoring
- Routine operations

### Review Agent

**Characteristics:**
- Advanced model (e.g., claude-sonnet-4-5, o1)
- Read-only tools
- Low temperature (0.1)

**Best for:**
- Code review
- Security analysis
- Architecture review
- Best practices checking

### Documentation Agent

**Characteristics:**
- Advanced model
- Write access to docs only
- Higher temperature (0.3-0.5)

**Best for:**
- README creation
- API documentation
- Tutorial writing
- Comment generation

### Reasoning Agent

**Characteristics:**
- Most advanced model (e.g., o1, claude-opus)
- Limited tool access during reasoning
- Very low temperature (0.0-0.1)

**Best for:**
- Complex algorithmic problems
- Architecture decisions
- Performance optimization
- Deep debugging

## Configuration Best Practices

### Model Selection

Choose models based on task complexity:

| Task Complexity | Recommended Model Type | Example Models |
|----------------|------------------------|----------------|
| **Simple** | Fast, lightweight | grok-2-mini, gpt-4o-mini |
| **Standard** | Balanced | claude-sonnet-4-5, gpt-4o |
| **Complex** | Advanced reasoning | claude-opus-4-1, o1 |

### Temperature Settings

Set temperature based on task creativity needs:

| Temperature | Use Case | Examples |
|------------|----------|----------|
| **0.0-0.1** | Deterministic, precise | Code generation, bug fixes |
| **0.2-0.3** | Slightly varied | Documentation, refactoring |
| **0.4-0.5** | Creative | Tutorial writing, brainstorming |

### Tool Permissions

Grant appropriate tool access:

```json
{
  "tools": {
    "read": true,      // Almost always enable
    "list": true,      // Almost always enable
    "grep": true,      // Almost always enable
    "write": true,     // Enable for implementation agents
    "edit": true,      // Enable for implementation agents
    "bash": false,     // Restrict for review/docs agents
    "webfetch": true   // Enable when internet research needed
  }
}
```

## Creating Custom Agents

### Step 1: Define Purpose

Clearly articulate what the agent should do:

- What tasks will it handle?
- What should it NOT do?
- What level of autonomy is appropriate?

### Step 2: Select Model

Choose based on:

- Task complexity
- Response time requirements
- Cost considerations
- Quality requirements

### Step 3: Configure Tools

Grant minimum necessary permissions:

- **Read-only**: For analysis agents
- **Write access**: For implementation agents
- **Bash access**: Only when system operations needed
- **Web access**: When research required

### Step 4: Set Temperature

- **Low (0.0-0.1)**: Code generation, precise tasks
- **Medium (0.2-0.3)**: Documentation, explanations
- **Higher (0.4-0.5)**: Creative writing, brainstorming

### Step 5: Test and Iterate

- Test with real tasks
- Adjust model/temperature based on results
- Refine tool permissions
- Document learnings

## Environment Variables

Many agent configurations require environment variables:

### Common Variables

```bash
# GitHub integration
GITHUB_TOKEN="ghp_..."

# OpenAI
OPENAI_API_KEY="sk-..."

# Anthropic
ANTHROPIC_API_KEY="sk-ant-..."

# Security scanning
SNYK_TOKEN="..."
```

### Setting Variables

**Windows (PowerShell):**
```powershell
$env:GITHUB_TOKEN = "your-token"
```

**Linux/Mac:**
```bash
export GITHUB_TOKEN="your-token"
```

### Referencing in Config

```json
{
  "environment": {
    "API_KEY": "${GITHUB_TOKEN}"
  }
}
```

## Troubleshooting

### Agent Not Behaving as Expected

1. **Check instruction hierarchy** - Is a higher priority instruction overriding?
2. **Verify model selection** - Is the model appropriate for the task?
3. **Review tool permissions** - Does the agent have necessary access?
4. **Check temperature** - Is it too high or too low for the task?

### Agent Too Slow

1. **Use faster model** - Switch to lightweight model for simple tasks
2. **Reduce context** - Limit instruction file sizes
3. **Optimize tools** - Grant only necessary tool access

### Agent Too Expensive

1. **Use tiered approach** - Fast model for simple tasks, advanced for complex
2. **Reduce context** - Minimize instruction content
3. **Batch operations** - Group related tasks together

### Inconsistent Behavior

1. **Lower temperature** - Reduce randomness
2. **Be more explicit** - Provide clearer instructions
3. **Check baseline** - Ensure behavioral baseline is included

## Additional Resources

- **[Baseline Behaviors](../LLM-BaselineBehaviors.md)** - Foundational behavioral model
- **[OpenCode Configuration](../tools/opencode/configuration.md)** - Practical implementation
- **[Sample Configurations](../tools/opencode/samples.md)** - Real-world examples
- **[MCP Overview](../mcp/overview.md)** - Quick start guide

---

**Next Steps:**

1. Review the **[Baseline Behaviors](../LLM-BaselineBehaviors.md)** in detail
2. Explore **[OpenCode Configuration](../tools/opencode/configuration.md)** for practical examples
3. Try creating your own custom agent configuration
4. Share successful patterns with the community

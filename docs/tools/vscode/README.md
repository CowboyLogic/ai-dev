# Visual Studio Code Agent Configuration Guide

> **Configure specialized AI agents in VS Code using GitHub Copilot**

## Overview

Visual Studio Code's GitHub Copilot provides flexible ways to configure specialized AI agents for different tasks. This guide covers both declarative configuration using markdown files and programmatic delegation using the `runSubagent` tool.

## Documentation Structure

This guide is organized into focused topics:

### 🚀 Getting Started

- **[Quick Start Guide](quick-start.md)** - Get up and running in 5 minutes
  - Basic agent file setup
  - Your first agent invocation
  - Common agent examples

### 📋 Configuration Methods

- **[Markdown-Based Agents](markdown-agents.md)** - Declarative configuration (Recommended)
  - How markdown agents work
  - YAML frontmatter reference
  - VS Code workspace settings
  - Agent file organization
  - Complete agent examples

- **[Programmatic SubAgents](subagent-tool.md)** - The `runSubagent` tool
  - When to use runSubagent
  - How it works
  - Configuration strategies
  - Advanced examples

### 📚 Reference

- **[Agent Examples Library](agent-examples.md)** - Ready-to-use agent configurations
  - Code Review Agent
  - Testing Specialist
  - Security Auditor
  - Documentation Generator
  - Performance Optimizer
  - And more...

- **[Best Practices](best-practices.md)** - Optimization and patterns
  - Agent design principles
  - Permission configuration
  - Temperature selection
  - Multi-agent workflows
  - Team collaboration

- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
  - Agent not recognized
  - Permission issues
  - Performance problems
  - Configuration errors

## Key Concepts

### Two Configuration Approaches

#### Method 1: Markdown Files (Recommended)

Create specialized agents as markdown files with YAML frontmatter:

```markdown
---
name: reviewer
description: Code review specialist
model: claude-sonnet-4.5
temperature: 0.1
permissions:
  read: true
  write: false
  execute: false
---

# Code Review Agent
You are a specialized code review agent...
```

**Invoke with:** `@reviewer Check this code for issues`

**Best for:**
- Reusable agent behaviors
- Team-wide standardization
- Quick access to specialized "modes"
- Version-controlled configurations

#### Method 2: runSubagent Tool

Programmatically delegate complex tasks to autonomous sub-agents:

```typescript
runSubagent({
  description: "Research authentication patterns",
  prompt: "Comprehensive task instructions..."
})
```

**Best for:**
- One-off complex research
- Autonomous multi-step tasks
- Dynamic task generation
- Deep codebase analysis

## Quick Comparison

| Feature | Markdown Files | runSubagent |
|---------|----------------|-------------|
| **Setup** | Create `.md` file once | No setup needed |
| **Invocation** | `@agentname` | Full prompt each time |
| **Reusability** | High | Low |
| **Team Sharing** | Excellent | N/A |
| **Complexity** | Simple | Advanced |
| **Best For** | Consistent roles | Complex one-off tasks |

## Getting Started

1. **New to VS Code agents?** Start with the [Quick Start Guide](quick-start.md)
2. **Want to create custom agents?** See [Markdown-Based Agents](markdown-agents.md)
3. **Need complex automation?** Check out [Programmatic SubAgents](subagent-tool.md)
4. **Looking for examples?** Browse the [Agent Examples Library](agent-examples.md)

## What You'll Learn

Throughout this guide, you'll discover how to:

- ✅ Create specialized agents for different workflows
- ✅ Configure agent behaviors, models, and permissions
- ✅ Invoke agents efficiently in your daily development
- ✅ Build multi-agent workflows for complex tasks
- ✅ Share agent configurations with your team
- ✅ Troubleshoot common configuration issues

## Additional Resources

- **[LLM Baseline Behaviors](../../agents/baseline-behaviors.md)** - Foundation behavioral model
- **[OpenCode Modular Config](../opencode/samples.md#modular-agent-configuration)** - Similar pattern for CLI
- **[GitHub Copilot Documentation](https://docs.github.com/en/copilot)** - Official docs

---

**Ready to get started?** Jump to the [Quick Start Guide](quick-start.md) →

---

**Last Updated:** November 25, 2025  
**Repository:** [ai-dev](https://github.com/CowboyLogic/ai-dev)


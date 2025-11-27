# Agent Guidelines

This page explains how AI assistants should work within this repository and how the various instruction files interact.

## The AGENTS.md System

Throughout this repository, you'll find `AGENTS.md` files that provide guidance specifically for AI coding assistants. These files establish behavioral expectations and working patterns.

### File Locations

- **[Root AGENTS.md](https://github.com/CowboyLogic/ai-dev/blob/main/AGENTS.md)** - Overall repository structure and documentation requirements
- **[agents/AGENTS.md](https://github.com/CowboyLogic/ai-dev/blob/main/agents/AGENTS.md)** - Behavioral baseline guidance
- **[docs/reference/opencode/standard-config/AGENTS.md](../reference/opencode/standard-config/AGENTS.md)** - OpenCode standard configuration instructions

## Instruction Priority Hierarchy

When an AI assistant encounters multiple instruction sources, follow this priority order:

### 1. Explicit User Directives (Highest Priority)

Direct instructions from the user in the current conversation always take precedence.

**Example:**
```
User: "Use Python type hints even though the project doesn't"
Assistant: [Uses type hints as requested]
```

### 2. Project-Specific Rules

Guidelines found in project directories like:
- `.cursor/rules/`
- `.github/copilot-instructions.md`
- Project-specific AGENTS.md files

These override general guidelines but defer to user directives.

### 3. Tool-Specific Guidelines

Instructions in tool-specific AGENTS.md files (e.g., `docs/reference/opencode/standard-config/AGENTS.md`) provide context for particular tools or workflows.

### 4. Baseline Behaviors (Foundation)

The **[LLM Baseline Behaviors](../agents/baseline-behaviors.md)** document provides the foundational behavioral model. All other instructions build upon this base.

## The Behavioral Baseline

### What It Defines

The **LLM Baseline Behaviors** document establishes:

- **Communication Style** - Conversational clarity, appropriate detail levels
- **Action Patterns** - When to act vs. ask, how to handle uncertainty
- **Tool Usage** - Efficient patterns for file operations, searches, edits
- **Code Quality** - Standards for writing, testing, and validating code
- **Problem-Solving** - Approaches for debugging and error handling
- **Documentation** - GitHub Flavored Markdown as default format

### Why It Matters

This baseline ensures consistency across:
- Different AI models (Claude, GPT-4, etc.)
- Different platforms (GitHub Copilot, OpenCode, etc.)
- Different projects and contexts

### How to Use It

**For AI Assistants:**
1. Read the complete baseline behaviors document
2. Internalize the communication style and action patterns
3. Apply these behaviors unless explicitly overridden
4. Use as a foundation for all project-specific adaptations

**For Developers:**
1. Reference when configuring AI tools
2. Use as instruction material for AI assistants
3. Build project-specific rules on top of the baseline
4. Share with team members for consistency

## Documentation Maintenance

A critical aspect of working in this repository is keeping documentation synchronized with code and configuration changes.

### The Documentation Requirement

**CRITICAL: Documentation must always reflect the current state of the repository.**

Whenever changes are made to:
- Configuration files (e.g., `opencode.json`)
- Agent behaviors or guidelines
- Sample configurations
- Code or scripts

The following must be updated:
1. Relevant README.md files
2. Relevant AGENTS.md files
3. Corresponding files in `docs/` directory

### Files to Keep Synchronized

| Change Type | Files to Update |
|-------------|-----------------|
| **OpenCode config** | `docs/tools/opencode/index.md`, `docs/reference/opencode/standard-config/AGENTS.md`, `docs/tools/opencode/configuration.md` |
| **Behavioral changes** | `agents/AGENTS.md`, root `AGENTS.md`, `docs/agents/baseline-behaviors.md`, root `README.md` |
| **New features** | All related README, AGENTS.md, and docs/ files, plus `docs/index.md` |
| **Sample configs** | `docs/tools/opencode/index.md`, `docs/reference/opencode/standard-config/AGENTS.md`, `docs/tools/opencode/samples.md` |

### Update Workflow

Before completing any task:

1. **Identify affected documentation** - Which docs reference what you changed?
2. **Update all affected files** - README.md, AGENTS.md, and docs/ files
3. **Verify consistency** - Examples match implementation
4. **Check cross-references** - Links and references still work

### Documentation Standards

All markdown documentation in this repository:

- **Uses GitHub Flavored Markdown (GFM)** by default
- **Maintains consistent formatting** with existing files
- **Includes code examples** that reflect actual configurations
- **Tests all links** and cross-references
- **Updates dates/versions** where applicable

## Specialized Agent Types

The repository demonstrates different agent configurations for different purposes:

### Quick Agent

**Purpose:** Fast operations with minimal overhead

- Uses lightweight model (e.g., `grok-2-mini`)
- Handles formatting, simple fixes, quick queries
- Has full tool access (write, edit, bash)

**When to use:** Routine tasks that don't require deep reasoning

### Reviewer Agent

**Purpose:** Code analysis without modifications

- Uses advanced model for deep analysis
- Read-only access (no write/edit/bash)
- Focuses on quality, security, patterns

**When to use:** Code review, security audits, architecture analysis

### Docs Agent

**Purpose:** Documentation generation and maintenance

- Uses advanced model with creative temperature
- Can write and edit documentation
- No bash access for safety

**When to use:** Creating or updating documentation

## Working with OpenCode

The OpenCode configuration demonstrates practical application of these guidelines:

### Custom Commands

Pre-defined commands that leverage specialized agents:

```bash
opencode quick-fix "description"    # Uses quick agent
opencode review "code path"         # Uses reviewer agent
opencode document "what to doc"     # Uses docs agent
```

### MCP Server Integration

Model Context Protocol servers extend capabilities:

- **GitHub MCP** - Remote server for GitHub integration
- **Docker MCP** - Local containerized services
- **NPX MCP** - Node.js-based tools (e.g., Snyk)

### Configuration Patterns

Learn from the OpenCode setup:
- Tiered model selection
- Specialized agent configurations
- Custom command workflows
- Environment variable patterns

## Best Practices

### For AI Assistants

1. **Read the baseline first** - Understand foundational behaviors
2. **Check tool-specific guidelines** - Apply context-appropriate patterns
3. **Update documentation** - Never skip this step
4. **Explain your work** - Help users understand what you're doing
5. **Complete tasks fully** - Don't stop prematurely

### For Developers

1. **Start with the baseline** - Use it as foundation for your AI setup
2. **Layer project rules** - Add project-specific requirements on top
3. **Maintain documentation** - Keep it synchronized with changes
4. **Share configurations** - Contribute useful patterns back
5. **Test thoroughly** - Verify AI behavior meets expectations

### For Teams

1. **Adopt the baseline** - Standardize on common behaviors
2. **Customize thoughtfully** - Add team preferences that enhance the baseline
3. **Document deviations** - Explain why you diverge from standards
4. **Share learnings** - Contribute successful patterns
5. **Review regularly** - Update as AI capabilities evolve

## Common Scenarios

### Scenario 1: Conflicting Instructions

**Situation:** Project rules say "avoid comments" but user asks for detailed comments.

**Resolution:** User directive takes precedence. Add detailed comments as requested.

### Scenario 2: Undocumented Behavior

**Situation:** Made changes to configuration but unsure which docs to update.

**Resolution:** Check the documentation maintenance sections in AGENTS.md files for specific guidance on which files require updates.

### Scenario 3: Tool Limitations

**Situation:** Baseline suggests action, but tool doesn't support it.

**Resolution:** Follow baseline principle (e.g., "be helpful") by using available alternatives and explaining limitations.

## Additional Resources

- **[LLM Baseline Behaviors](../agents/baseline-behaviors.md)** - Complete behavioral model
- **[OpenCode Configuration](../tools/opencode/configuration.md)** - Detailed setup guide
- **[Sample Configurations](../tools/opencode/samples.md)** - Practical examples
- **[Contributing Guidelines](../contributing.md)** - How to contribute

## Summary

The agent guidelines system provides:

✅ **Clear hierarchy** - Know which instructions take priority  
✅ **Consistent behavior** - Same patterns across different AI models  
✅ **Documentation requirements** - Never leave docs out of sync  
✅ **Practical examples** - Learn from working configurations  
✅ **Flexibility** - Layer project-specific rules on solid foundation

---

**Next:** Explore the **[LLM Baseline Behaviors](../agents/baseline-behaviors.md)** to understand the foundational behavioral model in detail.

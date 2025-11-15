# AI Agent Guidelines

This repository contains configurations and guidelines for working with AI development assistants.

## Behavioral Baseline

**All AI assistants working in this repository must follow the behavioral model defined in:**

📋 **[`agents/LLM-BaselineBehaviors.md`](agents/LLM-BaselineBehaviors.md)**

This document establishes the authoritative baseline for:
- Communication style and tone
- Action-oriented behavior and decision-making
- Tool usage patterns and efficiency
- Code quality standards
- Error handling and problem-solving approaches

Any project-specific or tool-specific directives should be layered on top of this baseline behavior model.

## Directory-Specific Guidelines

For additional context specific to certain tools or configurations:

- **`agents/`** - General AI agent configurations and behavioral baselines
- **`opencode/`** - OpenCode CLI-specific configurations and guidelines (see [`opencode/AGENTS.md`](opencode/AGENTS.md))

## Priority of Instructions

When multiple instruction sources exist, follow this priority order:

1. **Explicit user directives** - Direct instructions from the user in the current conversation
2. **Project-specific rules** - Guidelines in project `.cursor/rules/` or similar directories
3. **Tool-specific guidelines** - Instructions in tool-specific AGENTS.md files (e.g., `opencode/AGENTS.md`)
4. **Baseline behaviors** - The foundational model in `agents/LLM-BaselineBehaviors.md`

## Documentation Maintenance

**CRITICAL: Documentation must always reflect the current state of the repository.**

Whenever you make changes to configuration files, code, or any repository content, you **MUST** update all related documentation:

### Files to Keep Synchronized

1. **README.md files** - Update any README.md in the affected directory and the root README.md if needed
2. **AGENTS.md files** - Update relevant AGENTS.md files when behaviors or configurations change
3. **MkDocs documentation** - Update files in `docs/` directory:
   - `docs/index.md` - Main landing page
   - `docs/agents/` - Agent-related documentation
   - `docs/opencode/` - OpenCode-specific documentation
   - Any other relevant documentation pages

### Update Workflow

**Before completing any task:**

1. **Identify affected documentation** - Determine which documentation files describe or reference what you changed
2. **Update all affected files** - Modify README.md, AGENTS.md, and docs/ files to reflect changes
3. **Verify consistency** - Ensure examples, instructions, and descriptions match the actual implementation
4. **Check cross-references** - Update any links or references to changed content

### Examples of Changes Requiring Documentation Updates

**Configuration Changes:**
- Modified `opencode.json` → Update `opencode/README.md`, `opencode/AGENTS.md`, `docs/opencode/configuration.md`
- Added new agent → Update all three files above plus `docs/index.md`

**Behavioral Changes:**
- Modified `agents/LLM-BaselineBehaviors.md` → Update `README.md`, `AGENTS.md`, `agents/AGENTS.md`, `docs/agents/baseline-behaviors.md`

**New Files/Directories:**
- Added new tool configuration → Create corresponding README.md, AGENTS.md, and docs/ pages
- Update root `README.md` and `docs/index.md` to reference new content

**Sample Configurations:**
- Added/modified sample configs → Update `opencode/README.md` and `docs/opencode/samples.md`

### Documentation Standards

- Use **GitHub Flavored Markdown** for all .md files
- Maintain consistent formatting with existing documentation
- Include code examples that reflect actual configurations
- Update version numbers or dates where applicable
- Test all links and cross-references

**Never consider a task complete until all documentation is updated and synchronized.**

---

*These guidelines ensure consistent, high-quality AI assistance across all tools and platforms used in this repository.*
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

---

*These guidelines ensure consistent, high-quality AI assistance across all tools and platforms used in this repository.*
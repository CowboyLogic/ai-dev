# Context & Baselines

This section contains the behavioral baselines, instruction templates, and high-fidelity context documents that govern how AI assistants operate in development environments.

## What's Here

- **LLM Baseline Behaviors** ([LLM-BaselineBehaviors.md](LLM-BaselineBehaviors.md)) — The foundational behavioral model for AI assistants. Covers communication style, action-oriented behavior, tool usage, code quality, and problem-solving.
- **Baseline Behaviors v2.0** ([BaselineBehaviors-v2.0.md](BaselineBehaviors-v2.0.md)) — The XML-structured evolution of the baseline. Optimized for machine readability, KV-caching, and attention anchoring.
- **Copilot Instructions** ([copilot-instructions.md](copilot-instructions.md)) — Repository-specific directives for GitHub Copilot, defining instruction priority order.
- **High-Fidelity Context** ([high-fidelity-context.md](high-fidelity-context.md)) — Explains the strategic rationale for migrating AI directives from Markdown to structured XML modules.
- **High-Fidelity Migration Guide** ([high-fidelity-context-migration.md](high-fidelity-context-migration.md)) — Step-by-step guide for converting existing AGENTS.md files to the XML system.

## Instruction Priority Hierarchy

Follow this canonical hierarchy when multiple instruction sources exist:

1. **Explicit user directives** — Direct commands in the current conversation (highest priority)
2. **Repository-specific directives** — Guidelines in `AGENTS.md` or `AGENTS.xml` files
3. **Tool-specific guidelines** — Instructions from external tools or systems
4. **Baseline behaviors** — Foundational model (lowest priority)

This hierarchy ensures clear decision-making when instructions conflict. For detailed configuration layer documentation, see [Agent Configuration](../agents/configuration.md).

## Evolution Path

The baseline originally shipped as Markdown ([LLM-BaselineBehaviors.md](LLM-BaselineBehaviors.md)). Version 2.0 introduces an XML-structured format for better machine parsing. Both are maintained; new projects should prefer the XML version.

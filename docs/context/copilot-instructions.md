# GitHub Copilot Instructions

Follow all directives defined in the repository's `AGENTS.md` file located at the root of this repository.

Key behavioral guidelines are defined in `.github/LLM-BaselineBehaviors.md`, which serves as the authoritative source for AI agent behavior. Refer to that document for detailed instructions and remove any overlapping directives from this file.

**Priority order for instructions:**

1. Explicit user directives in the current conversation
2. Repository-specific directives in `AGENTS.md`
3. Baseline behaviors in `.github/LLM-BaselineBehaviors.md`

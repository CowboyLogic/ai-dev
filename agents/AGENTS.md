# AI Agent Configuration Guidelines

This directory contains the core behavioral guidelines and configurations for AI assistants.

## Baseline Behavioral Model

**📋 [`LLM-BaselineBehaviors.md`](LLM-BaselineBehaviors.md)**

This is the **authoritative behavioral baseline** for all AI assistants working in this repository. It defines:

- Communication style (conversational clarity, appropriate detail level)
- Action-oriented approach (implementation over suggestion)
- Work persistence (complete tasks fully, handle errors actively)
- Tool usage philosophy (efficiency, parallelization, context gathering)
- Code and file operation standards
- Problem-solving approaches
- Task management for complex work
- Quality and security standards
- Platform-specific adaptations

### How to Use This Baseline

**For AI Assistants:**
Read and internalize the complete `LLM-BaselineBehaviors.md` file at the start of any session. Follow these behaviors unless explicitly overridden by:
- Direct user instructions
- Project-specific rules (`.cursor/rules/`, etc.)
- Tool-specific guidelines (e.g., `opencode/AGENTS.md`)

**For Users:**
Reference this baseline when configuring AI tools or when you want to align different AI assistants to consistent behavior patterns.

**For Contributors:**
When creating tool-specific or project-specific guidelines, build upon this baseline rather than contradicting it. Document any deviations with clear rationale.

## Additional Files

As additional agent configurations are created, they will be documented here.

## Documentation Maintenance Requirements

**CRITICAL: When modifying files in the `agents/` directory, documentation must be updated.**

### Files That Require Updates

When you modify `LLM-BaselineBehaviors.md` or other agent configurations:

1. **Root `README.md`** - If changes affect overall repository purpose or capabilities
2. **Root `AGENTS.md`** - If changes affect the behavioral baseline or instruction hierarchy
3. **`agents/AGENTS.md`** (this file) - Update to reflect new configurations or changes
4. **`docs/agents/baseline-behaviors.md`** - Mirror changes from LLM-BaselineBehaviors.md
5. **`docs/agents/configuration.md`** - Document any new agent configurations
6. **`docs/index.md`** - Update if changes affect key features or overview

### Synchronization Rules

**For `LLM-BaselineBehaviors.md` changes:**
- This is the **authoritative source** for behavioral guidelines
- Changes here should propagate to documentation that references these behaviors
- Update examples in `docs/` to reflect new behavioral patterns
- Ensure `docs/agents/baseline-behaviors.md` stays synchronized

**For new agent configurations:**
- Document in this `AGENTS.md` file
- Create corresponding documentation in `docs/agents/`
- Update navigation in `mkdocs.yml` if adding new documentation pages
- Reference in root `README.md` if it's a major addition

### Verification Checklist

Before completing changes to agent configurations:

- [ ] Updated all README.md files that reference the changed content
- [ ] Updated relevant AGENTS.md files
- [ ] Updated corresponding files in `docs/` directory
- [ ] Verified all cross-references and links still work
- [ ] Ensured examples match actual implementation
- [ ] Checked that behavioral descriptions are consistent across all files

**Documentation consistency is essential for this repository's purpose as a shared resource.**

---

*This baseline ensures consistent AI assistance across different models and platforms, promoting efficient collaboration and high-quality output.*
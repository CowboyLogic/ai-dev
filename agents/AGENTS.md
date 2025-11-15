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

---

*This baseline ensures consistent AI assistance across different models and platforms, promoting efficient collaboration and high-quality output.*
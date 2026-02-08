# README: LLM Baseline Behavioral Model (XML Version)

This repository contains the **authoritative behavioral baseline** for AI development assistants. Transitioning from the legacy Markdown format to this **XML-structured model** improves machine readability, context efficiency, and consistency across all projects.

---

## Why XML?

While Markdown is excellent for human readability, XML provides a superior "grammar" for Large Language Models (LLMs) when used in system prompts:

* **Attention Anchoring**: Explicit tags like `<action_logic>` act as semantic anchors, helping the model maintain focus on specific rules during long sessions.
* **Context Efficiency**: The structure reduces token overhead by removing repetitive formatting while maintaining full fidelity of the original directives.
* **KV-Caching Optimization**: This file is designed as a **static prefix**. By keeping it identical across all projects, you maximize "Key-Value Cache" hits, resulting in faster response times and lower latency.

---

## Core Sections

* **`<core_identity>`**: Defines the persona, communication tone, and expansion triggers for technical explanations.
* **`<action_logic>`**: Governs how the agent decides between acting immediately and asking for clarification.
* **`<background_protocols>`**: Specialized instructions for autonomous or non-interactive CLI operations, including "Assume & Document" logic.
* **`<workspace_protocols>`**: Directives for repository research, tool efficiency, and Git safety.
* **`<management_guardrails>`**: Safety limits, including time-boxing, loop detection, and stateful recovery via `.state.json`.

---

## Usage Guidelines

1. **Keep it Static**: Do not modify the XML structure or add project-specific data to this file. All project-specific rules should go into a local `AGENTS.md` file.
2. **The Cache Breakpoint**: Ensure your loader injects this file at the very beginning of the system prompt. The `` tag marks where variable session data should begin.
3. **Background Mode**: When running agents via CLI with background flags, the agent will automatically pivot to the protocols defined in `<background_protocols>`.

---

## How to Contribute

If you need to propose a change to the baseline behaviors:

1. Ensure the change is applicable to **all** projects.
2. Maintain the XML tag hierarchy to preserve structural clarity.
3. Test the new directive to ensure it doesn't cause "instruction drift" or conflict with existing `<action_logic>`.

---
*This model is designed to ensure consistent, high-quality AI assistance across all tools and platforms.*

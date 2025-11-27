# AI Agent Guidelines

This repository contains configurations and guidelines for working with AI development assistants.

## Purpose and Scope

**This AGENTS.md file is the authoritative directive for how AI agents should work with this repository.**

It defines:
- How agents should behave when managing this repository
- File structure and organization conventions
- When and how to update documentation
- Repository-specific workflows and requirements

**The `docs/` folder contains publishable content for readers.** Content in `docs/` may describe agent behaviors or best practices, but those descriptions are for educational/reference purposes. Only directives in this AGENTS.md file (or explicitly referenced external files) govern agent behavior in this repository.

## Behavioral Baseline

**Authoritative baseline behaviors are defined in `.github/LLM-BaselineBehaviors.md`.** This file serves as the definitive source for AI agent behavioral guidelines in this repository. **NEVER modify `.github/LLM-BaselineBehaviors.md` without explicit instruction from the user.**

All AI assistants working in this repository must follow these behavioral principles:

- **Action-oriented**: Implement changes rather than only suggesting them
- **Direct communication**: Brief, clear responses without unnecessary framing
- **Efficient tool usage**: Parallelize independent operations when possible
- **Complete work**: Continue until tasks are fully resolved before yielding to user
- **Proactive problem-solving**: Research and deduce solutions rather than giving up

These behaviors apply to repository management work. Detailed behavioral documentation in `docs/agents/` is for reference and publication, not authoritative directives unless explicitly incorporated here.

## Repository Structure

This repository is organized as follows:

- **`AGENTS.md`** (this file) - Authoritative directives for AI agents working in this repository
- **`README.md`** - Repository overview and quick start guide
- **`mkdocs.yml`** - MkDocs configuration for building publishable documentation
- **`docs/`** - Publishable documentation content (educational/reference material)
  - `docs/agents/` - Documentation about agent behaviors and best practices
  - `docs/tools/` - Tool-specific guides and configuration examples
  - `docs/mcp/` - MCP configuration documentation and samples
- **`site/`** - Generated static site from MkDocs build (do not edit directly)
- **`agent-output/`** - Temporary files and agent-generated content (excluded from version control)

## Priority of Instructions

When multiple instruction sources exist, follow this priority order:

1. **Explicit user directives** - Direct instructions from the user in the current conversation
2. **This AGENTS.md file** - Repository-specific directives and workflows defined here
3. **Project-specific rules** - Guidelines in `.cursor/rules/` or similar tool-specific directories
4. **Referenced external files** - Only files explicitly referenced as authoritative by this AGENTS.md

**Important**: Content in `docs/` is for publication and reference. It does not override directives in this file unless explicitly incorporated by reference.

## Managing This Repository

### When to Update AGENTS.md

**Update this AGENTS.md file only when:**

1. **Repository structure changes** - New directories, moved files, or reorganization
2. **Explicitly directed by the user** - User specifically requests changes to agent behavior or directives
3. **File path references become outdated** - Links or references in this file point to non-existent locations

**Do NOT update this AGENTS.md file when:**

- Making changes to content within `docs/` folder
- Updating examples, guides, or educational content
- Modifying configuration samples or tool-specific documentation
- Adding new documentation pages or articles

### Documentation Update Requirements

**When making changes to repository content, update documentation as appropriate:**

1. **Configuration files changed** - Update relevant documentation in `docs/` that references those configurations
2. **New features or tools added** - Create or update documentation pages to describe them
3. **Structure changes** - Update this AGENTS.md file to reflect new paths (see above)
4. **Sample code modified** - Ensure examples in documentation match actual implementations

**Direction of information flow:**

- `AGENTS.md` → `docs/` (only when explicitly directed)
- `docs/` content changes do NOT automatically flow back to `AGENTS.md`
- Repository structure changes → Update `AGENTS.md` paths/references
- User behavioral directives → Update `AGENTS.md` if requested

### Documentation Standards

When creating or updating documentation in `docs/`:

- Use **GitHub Flavored Markdown** for all .md files
- Maintain consistent formatting with existing documentation
- Include code examples that reflect actual configurations
- Update version numbers or dates where applicable
- Test all links and cross-references

### Markdown Formatting Guidelines

All markdown documentation must follow standard formatting rules:

1. **Blank Lines Around Block Elements**
   - Always add a blank line before and after:
     - Lists (ordered and unordered)
     - Code blocks (fenced with ```)
     - Blockquotes
     - Tables
   - Exception: Multiple consecutive list items don't need blank lines between them

2. **Code Block Formatting**
   - Use fenced code blocks (```) instead of indented blocks
   - Specify language for syntax highlighting when possible
   - Add blank lines before and after code blocks

3. **List Formatting**
   - Use consistent indentation (2 spaces for nested lists)
   - Add blank lines before and after lists
   - Use `-` for unordered lists, `1.` for ordered lists

4. **Heading Spacing**
   - Add a blank line after headings (except when followed by another heading)
   - Use consistent heading levels without skipping levels

5. **Link and Reference Formatting**
   - Use descriptive link text
   - Ensure all links are functional
   - Use reference-style links for repeated URLs when appropriate

### Agent Output Directory

**All agent-generated files that are not part of the documentation set must be placed in the `agent-output/` directory.**

- **Location**: Create files in `agent-output/` folder in the repository root
- **Directory creation**: Create the directory if it doesn't exist before placing files
- **Purpose**: Keep generated content separate from source documentation
- **Examples**: Test files, temporary configurations, analysis outputs, generated code samples
- **Documentation files**: Only create files in `docs/` if they are intended to be part of the official documentation

The `agent-output/` directory is automatically excluded from version control.

---

*These guidelines ensure consistent, high-quality AI assistance across all tools and platforms used in this repository.*
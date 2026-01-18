# Copilot Prompt Creator

A specialized skill for creating effective custom prompts for GitHub Copilot, with built-in research capabilities to ensure prompts are based on the latest information from GitHub's official resources.

## Overview

This skill guides you through the process of creating custom prompts that help GitHub Copilot perform specific tasks more effectively. Unlike general prompting, this skill emphasizes researching the latest Copilot capabilities and best practices from GitHub's documentation and community resources.

The skill ensures that every prompt creation process starts with checking online resources from github.com for the most current information, patterns, and techniques.

## Key Features

- **Latest Information Research**: Automatically checks GitHub's official documentation and repositories
- **Task-Specific Prompts**: Creates prompts tailored to specific development tasks
- **Best Practices Integration**: Incorporates current prompting techniques and Copilot capabilities
- **Testing and Refinement**: Includes steps for testing and improving prompts
- **Documentation**: Provides clear usage instructions and examples

## Quick Start

1. **Research Phase**: The skill automatically searches GitHub for latest Copilot information
2. **Requirements Analysis**: Define the specific task and context
3. **Prompt Design**: Structure the prompt using current best practices
4. **Testing**: Validate the prompt works effectively
5. **Documentation**: Create usage instructions for the prompt

## When to Use

Use this skill when you need Copilot to:
- Generate code for specific frameworks or patterns
- Perform code reviews or analysis
- Create documentation or API specs
- Debug complex issues
- Follow specific coding standards or conventions

## Research Sources

The skill checks these GitHub resources for latest information:
- Official Copilot documentation (github.com/docs)
- Copilot-related repositories (microsoft/vscode-copilot, github/copilot-docs)
- Community prompt collections and examples
- Recent updates and feature announcements

## Example Usage

When asked to create a prompt for "generating React components", the skill will:
1. Search GitHub for latest React + Copilot patterns
2. Check current Copilot capabilities for React development
3. Create a prompt incorporating best practices
4. Provide testing guidance

## Integration

This skill works alongside:
- `copilot-instruction-creator`: For persistent Copilot behavior customization
- `skill-creator`: For creating new skills that use custom prompts
- `copilot-agent-creator`: For building VS Code extensions with Copilot integration

## Files in This Skill

- **SKILL.md**: Main skill instructions with step-by-step guidance
- **README.md**: This overview and quick reference
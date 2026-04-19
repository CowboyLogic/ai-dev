# MkDocs Site Management - Agent Skill

This skill teaches AI agents how to create and maintain MkDocs documentation sites, ensuring configuration consistency and resolving build issues.

## What's Included

- **SKILL.md** - The main skill file with comprehensive instructions for MkDocs site management

## Usage

When working with an AI agent (GitHub Copilot, Claude, etc.), this skill will be automatically discovered when you ask to:

- "Set up a new MkDocs site"
- "Add a page to my MkDocs documentation"
- "Fix MkDocs build errors"
- "Update MkDocs navigation"
- "Configure MkDocs plugins"

## Key Features

- **Configuration Management**: Ensures mkdocs.yml stays synchronized with source directory changes
- **Build Validation**: Automatically runs `mkdocs build --clean --strict` after configuration changes
- **Error Resolution**: Provides systematic approaches to common MkDocs build issues
- **Navigation Updates**: Maintains consistent navigation structure as documentation evolves

## Prerequisites

- MkDocs installed in the development environment
- Basic familiarity with MkDocs configuration concepts
- Access to terminal for running MkDocs commands

## Integration

This skill integrates with MkDocs workflows by:

1. Monitoring changes to the `docs/` directory structure
2. Updating `mkdocs.yml` navigation configuration as needed
3. Validating configuration changes through strict builds
4. Resolving common build errors and warnings
5. Ensuring site consistency and reliability

## Related Skills

- **Skill Creator**: For creating additional custom skills
- **Google Style Docs**: For documentation writing standards
- **Git Commit Messages**: For proper versioning of documentation changes
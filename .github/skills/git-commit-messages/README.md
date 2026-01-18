# Git Commit Messages Skill

This skill provides comprehensive guidance for writing clear, descriptive, and succinct git commit messages that follow industry best practices and conventional commit standards.

## Overview

The Git Commit Messages skill helps AI agents and developers create commit messages that:
- Follow conventional commit format
- Are descriptive yet concise
- Provide clear context for code changes
- Support automated tooling and release processes
- Maintain readable project history

## What's Included

- **`SKILL.md`** - Main skill file with detailed guidelines and instructions
- **`examples.md`** - Comprehensive examples of good and bad commit messages
- **`commit-generator.py`** - Python script to analyze changes and suggest commit messages
- **`vscode-integration.md`** - Complete guide for VS Code integration and automation
- **`README.md`** - This overview file

## Key Features

### Commit Message Standards
- Conventional commit format with types (feat, fix, docs, etc.)
- Subject line limits (50 characters) and body formatting (72 characters)
- Proper use of imperative mood and capitalization
- Breaking change declarations and issue references

### Practical Examples
- Real-world examples for different change types
- Good vs bad message comparisons
- Templates for common scenarios
- Industry best practices

### Automation Tools
- Python script for analyzing git diffs
- Automatic type and scope detection
- Suggested commit message generation
- Integration with conventional commit workflows

## Usage

### Manual Message Writing

When writing commit messages manually:

1. **Analyze your changes** - Understand what files changed and why
2. **Choose appropriate type** - Use conventional commit types (feat, fix, docs, etc.)
3. **Write clear subject** - Keep under 50 characters, imperative mood
4. **Add detailed body** - Explain what and why, use bullet points
5. **Include references** - Link to issues, PRs, or related commits

### Using the Generator Script

The included Python script can help generate commit messages:

```bash
# Stage your changes first
git add .

# Run the generator
python .github/skills/git-commit-messages/commit-generator.py
```

This will analyze your staged changes and suggest an appropriate commit message.

### Integration with AI Agents

AI agents can use this skill when:
- Asked to "write a good commit message for these changes"
- Reviewing pull requests for commit message quality
- Establishing team commit message conventions
- Training on commit message best practices

## Conventional Commit Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add OAuth login` |
| `fix` | Bug fix | `fix(api): resolve null pointer` |
| `docs` | Documentation | `docs(readme): update guide` |
| `style` | Code style | `style(lint): fix formatting` |
| `refactor` | Code refactoring | `refactor(utils): simplify logic` |
| `test` | Testing | `test(auth): add unit tests` |
| `chore` | Maintenance | `chore(deps): update packages` |
| `perf` | Performance | `perf(db): optimize queries` |
| `ci` | CI/CD | `ci(pipeline): add deployment` |
| `build` | Build system | `build(webpack): update config` |

## Best Practices

### Subject Lines
- ✅ Under 50 characters
- ✅ Start with capital letter
- ✅ No ending punctuation
- ✅ Imperative mood ("Add" not "Added")
- ✅ Specific and descriptive

### Message Body
- ✅ Separated from subject by blank line
- ✅ Wrapped at 72 characters per line
- ✅ Explains both what and why
- ✅ Uses bullet points for multiple changes
- ✅ References issues when applicable

### Breaking Changes
- ✅ Use "BREAKING CHANGE:" in footer
- ✅ Explain migration path
- ✅ Update version numbers appropriately

## Examples

### Good Commit Message
```
feat(user-profile): add avatar upload functionality

Implement secure file upload with validation and resizing.
- Add image format validation (JPEG, PNG, WebP)
- Implement automatic resizing and optimization
- Store files in cloud storage with CDN
- Update user API to include avatar URLs

Closes #123
```

### Breaking Change
```
refactor(api): migrate to GraphQL schema

Replace REST endpoints with GraphQL for better flexibility.

BREAKING CHANGE: All REST API endpoints deprecated.
Migrate to GraphQL queries by v2.0.0.

Migration guide: docs.company.com/graphql-migration
```

## VS Code Integration

This skill includes comprehensive VS Code integration options for automatic commit message generation and validation. See [`vscode-integration.md`](vscode-integration.md) for:

- **VS Code Tasks** - Keyboard shortcuts for quick message generation
- **Git Hooks** - Automatic validation of commit message format
- **Custom Extensions** - Full VS Code extension for seamless integration
- **Copilot Integration** - AI-powered interactive commit message assistance
- **Complete Workflows** - Integrated development workflows combining multiple methods

### Quick Setup

1. **VS Code Tasks**: Add keyboard shortcut for instant message generation
2. **Git Hooks**: Automatic validation prevents poorly formatted commits
3. **Copilot**: Ask `@commit` for interactive help with message writing

See the [VS Code Integration Guide](vscode-integration.md) for complete setup instructions.

## Resources

- [Conventional Commits Specification](https://conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [Git Best Practices](https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project)
- [Commit Message Linting](https://commitlint.js.org/)
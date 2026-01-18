# Copilot Custom Instructions

A comprehensive skill for creating custom instructions that tailor GitHub Copilot's responses to your personal preferences, team workflows, project requirements, or organization standards.

## Overview

Custom instructions allow you to customize how GitHub Copilot responds to queries by providing persistent context and preferences. Instead of repeating the same information in every conversation, you can create instruction files that automatically guide Copilot's behavior.

This skill provides step-by-step guidance for creating effective custom instructions at three levels: personal, repository, and organization.

## Key Features

- **Personal Instructions**: Individual preferences for Copilot Chat on GitHub.com
- **Repository Instructions**: Project-specific standards and context
- **Organization Instructions**: Company-wide policies and preferences
- **Path-Specific Instructions**: Targeted guidance for different file types or directories
- **Agent Instructions**: Specialized instructions for different AI models
- **Best Practices**: Proven patterns for writing effective instructions

## Quick Start

1. **Check the latest GitHub documentation**: Always visit https://docs.github.com/en/copilot/concepts/prompting/response-customization first
2. **Determine your scope**: Personal, repository, or organization level
3. **Choose instruction type**: Repository-wide, path-specific, or agent instructions
4. **Analyze your needs**: What behaviors need customization?
5. **Write clear instructions**: Follow the guidelines for effective instruction writing
6. **Test and refine**: Verify instructions work as intended

## Types of Custom Instructions

### Personal Instructions
- Apply to your individual Copilot Chat experience on GitHub.com
- Set personal preferences like language, response style, or communication preferences
- Example: "Always respond in clear, concise English with practical examples."

### Repository Instructions
- **Repository-wide**: `.github/copilot-instructions.md` - applies to entire repository
- **Path-specific**: `.github/instructions/NAME.instructions.md` - applies to specific paths
- **Agent instructions**: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` - model-specific guidance

### Organization Instructions
- Apply to all organization members (Enterprise plan required)
- Set company-wide standards and preferences
- Example: "Always follow our security guidelines and coding standards."

## Examples

### Repository-Wide Instructions

Create `.github/copilot-instructions.md`:

```markdown
# Project Overview
This is a React TypeScript application for task management.

## Technology Stack
- React 18 with TypeScript
- Tailwind CSS for styling
- React Query for data fetching
- Jest for testing

## Coding Standards
- Use functional components with hooks
- Prefer custom hooks over class components
- Use early returns in functions
- Handle errors with try-catch blocks
- Write descriptive names for variables and functions

## Project Structure
- `/src/components`: Reusable UI components
- `/src/hooks`: Custom React hooks
- `/src/utils`: Helper functions
- `/tests`: Test files
```

### Path-Specific Instructions

Create `.github/instructions/api.instructions.md`:

```markdown
# API Layer Instructions

These instructions apply to API-related files and backend code.

## API Design
- Use RESTful principles
- Include proper HTTP status codes
- Validate all inputs
- Provide meaningful error messages

## Security
- Implement authentication and authorization
- Use HTTPS for all endpoints
- Validate and sanitize inputs
- Rate limiting for public endpoints

## Error Handling
- Use consistent error response format
- Log errors appropriately
- Don't expose sensitive information in errors
```

### Personal Instructions

In Copilot Chat settings:
```
Always explain code concepts with practical examples.
Prefer modern JavaScript/TypeScript features.
When suggesting code, include comments for complex logic.
Focus on readable, maintainable solutions.
Be concise but thorough in explanations.
```

## Best Practices

### Writing Effective Instructions
- **Be specific and actionable**: Use concrete examples rather than vague guidance
- **Keep it concise**: Short, focused statements work better than long explanations
- **Test thoroughly**: Verify instructions produce desired behavior
- **Avoid conflicts**: Ensure instructions don't contradict each other
- **Update regularly**: Review and refine as needs change

### Repository Management
- **Version control**: Track instruction files in git like any other code
- **Team alignment**: Ensure instructions reflect team consensus
- **Documentation**: Reference instruction files in project README
- **Gradual adoption**: Start with a few key instructions and expand

### Organization Implementation
- **Start small**: Begin with a few high-impact instructions
- **Gather feedback**: Monitor effectiveness and team satisfaction
- **Scale gradually**: Expand coverage as the organization adopts
- **Maintain flexibility**: Allow teams to add repository-specific instructions

## Common Use Cases

### Development Teams
- Enforce coding standards and conventions
- Specify technology stack preferences
- Define project structure and patterns
- Set testing and documentation requirements

### Open Source Projects
- Communicate contribution guidelines
- Specify coding style and formatting
- Define project architecture and patterns
- Set documentation standards

### Enterprise Organizations
- Enforce security and compliance requirements
- Standardize technology choices
- Define communication and response styles
- Implement accessibility and internationalization requirements

## Troubleshooting

### Instructions Not Taking Effect
- Check file location and naming conventions
- Verify Copilot plan supports custom instructions
- Check precedence (personal overrides repository, etc.)
- Test in different Copilot features

### Inconsistent Behavior
- Review for conflicting instructions
- Check if instructions are too broad or vague
- Test across different file types and contexts
- Consider path-specific instructions for complex projects

### Team Adoption Issues
- Ensure instructions are documented and discoverable
- Provide training on how to use custom instructions
- Gather feedback and iterate on instructions
- Start with simple, high-value instructions

## Related Skills

- [Copilot Agent Creator](../copilot-agent-creator/): For creating custom agents and extensions
- [Google Style Docs](../google-style-docs/): For documenting your projects and instructions
- [Git Commit Messages](../git-commit-messages/): For maintaining consistent commit practices

## Resources

- [GitHub Custom Instructions Documentation](https://docs.github.com/en/copilot/concepts/prompting/response-customization)
- [Adding Repository Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Custom Instructions Library](https://docs.github.com/en/copilot/tutorials/customization-library/custom-instructions)
- [Support Matrix](https://docs.github.com/en/copilot/reference/custom-instructions-support)
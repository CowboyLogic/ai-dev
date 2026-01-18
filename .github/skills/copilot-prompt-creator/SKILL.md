---
name: copilot-prompt-creator
description: Guide for creating custom prompts for GitHub Copilot, including checking online resources from github.com for the latest information before creating prompts.
license: MIT
---

# Copilot Prompt Creator

This skill provides a structured approach to creating effective custom prompts for GitHub Copilot, ensuring that the latest information and best practices from GitHub's resources are incorporated.

## When to Use This Skill

Use this skill when:
- Creating custom prompts for Copilot to perform specific tasks
- Developing prompts for code generation, refactoring, or analysis
- Building prompts for documentation, testing, or debugging workflows
- Need to ensure prompts are based on the most current Copilot capabilities and guidelines

## Prerequisites

- Access to GitHub repositories and documentation
- Understanding of the task or domain for which the prompt is being created
- Knowledge of Copilot's capabilities and limitations

## Instructions

1. **Research Latest Information from GitHub**
   - Use the `github_repo` tool to search for official GitHub Copilot documentation and examples
   - Search for repositories like `github/copilot-docs` or `microsoft/vscode-copilot` for latest features
   - Use `fetch_webpage` tool to check GitHub's official documentation at https://docs.github.com/en/copilot
   - Look for recent updates on prompt engineering techniques specific to Copilot

2. **Analyze Requirements and Context**
   - Identify the specific task or workflow the prompt should address
   - Determine the programming language, framework, or domain
   - Consider the user's skill level and expected output format
   - Review existing similar prompts or examples from the research

3. **Design the Prompt Structure**
   - Start with a clear, specific instruction
   - Include context about the codebase or project when relevant
   - Specify the desired output format (code, explanation, steps, etc.)
   - Add constraints or guidelines to improve accuracy
   - Incorporate best practices from the latest GitHub resources

4. **Incorporate Latest Copilot Features**
   - Include references to recent Copilot capabilities discovered in research
   - Use new prompt patterns or techniques from official documentation
   - Ensure compatibility with current Copilot versions and limitations

5. **Test and Refine the Prompt**
   - Test the prompt in a development environment
   - Iterate based on Copilot's responses
   - Refine based on accuracy, completeness, and usefulness
   - Document any limitations or edge cases

6. **Document the Prompt**
   - Include usage instructions and examples
   - Note any prerequisites or setup requirements
   - Provide context for when and how to use the prompt effectively

## Examples

### Example 1: Creating a Code Review Prompt

After researching GitHub's latest Copilot documentation:

```
You are an expert code reviewer. Review the following [language] code for:
- Security vulnerabilities
- Performance issues
- Code quality and best practices
- Potential bugs

Code to review:
```[language]
[code here]
```

Provide specific, actionable feedback with code examples for fixes.
```

### Example 2: API Documentation Prompt

Based on current Copilot capabilities:

```
Generate comprehensive API documentation for the following [language] function/class. Include:
- Purpose and functionality
- Parameters with types and descriptions
- Return values
- Usage examples
- Error handling

Function/Class:
```[language]
[code here]
```

Format as clean Markdown with proper headings and code blocks.
```

## Best Practices

- Always start with research to ensure using current best practices
- Be specific about the task and expected output format
- Include context from the codebase when possible
- Test prompts with multiple scenarios
- Keep prompts concise but comprehensive
- Use clear, natural language that Copilot can understand

## Common Issues

**Issue**: Prompt generates incorrect or outdated code patterns
**Solution**: Ensure research step includes checking for latest language/framework updates

**Issue**: Copilot doesn't understand the context
**Solution**: Provide more specific codebase context and examples in the prompt

**Issue**: Prompt is too vague, leading to inconsistent results
**Solution**: Add specific constraints, examples, and output format requirements

## Additional Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Copilot Prompt Engineering Guide](https://github.com/microsoft/vscode-copilot)
- [Awesome Copilot Prompts](https://github.com/f/awesome-chatgpt-prompts) (adapt for Copilot)
- Related skills: `copilot-custom-instructions`, `skill-creator`
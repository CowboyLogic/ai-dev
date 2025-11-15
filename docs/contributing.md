# Contributing to AI Dev

Thank you for your interest in contributing to this repository! This guide will help you understand how to submit configurations, documentation, and other improvements.

## Who Should Contribute?

**You should contribute if:**
- You've created useful AI agent configurations
- You've developed custom OpenCode commands or agents
- You've found better ways to work with AI tools
- You've discovered useful MCP server integrations
- You want to improve documentation or examples

**No contribution is too small** - even fixing typos or clarifying documentation helps everyone.

## What to Contribute

### Configuration Files

**OpenCode Configurations:**
- Custom specialized agents
- Useful command definitions
- MCP server integrations
- Model provider setups
- Tool permission patterns

**Other AI Tool Configs:**
- Cursor IDE rules
- VS Code Copilot settings
- Claude project configurations
- ChatGPT custom instructions

### Documentation

- Improved explanations
- Additional examples
- Troubleshooting guides
- Best practices
- Use case walkthroughs

### Behavioral Baselines

- Enhanced behavioral guidelines
- Model-specific adaptations
- Communication style refinements
- Workflow improvements

## Before You Contribute

### Review Existing Content

1. **Check if it already exists** - Search the repository
2. **Review similar examples** - Maintain consistency
3. **Read the guidelines** - Follow established patterns

### Test Your Contribution

1. **Verify configurations work** - Test before submitting
2. **Check formatting** - Ensure valid JSON/Markdown
3. **Test links** - All links should resolve
4. **Validate examples** - Code samples should be functional

## How to Contribute

### Quick Process

1. **Fork the repository**
2. **Create a branch** for your changes
3. **Make your changes** following guidelines below
4. **Test thoroughly**
5. **Submit a Pull Request**

### Detailed Steps

#### 1. Fork and Clone

```bash
# Fork via GitHub UI, then:
git clone https://github.com/YOUR-USERNAME/ai-dev.git
cd ai-dev
git remote add upstream https://github.com/ORIGINAL-OWNER/ai-dev.git
```

#### 2. Create a Branch

```bash
# Use descriptive branch names
git checkout -b add-postgres-mcp-config
git checkout -b improve-agent-docs
git checkout -b fix-opencode-examples
```

#### 3. Make Changes

Follow the guidelines below for your type of contribution.

#### 4. Commit Changes

```bash
git add .
git commit -m "Add PostgreSQL MCP server configuration example"
```

**Good commit messages:**
- `Add Snyk MCP server configuration`
- `Improve behavioral baseline documentation`
- `Fix typo in opencode README`
- `Update agent configuration examples`

**Bad commit messages:**
- `Update files`
- `Fix stuff`
- `Changes`

#### 5. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a Pull Request via GitHub UI.

## Contribution Guidelines

### Configuration Files

#### Location

- **MCP server configs** → `mcp/sample-configs/`
- **Other tool configs** → Create appropriate directory
- **Shared configs** → `agents/` for cross-tool configurations

#### Format

**JSON Files:**
```json
{
  "$schema": "https://opencode.ai/config.json",
  
  // Clear comments explaining purpose
  "section": {
    "key": "value"  // Inline comments for clarity
  }
}
```

**Requirements:**
- Valid JSON syntax
- Descriptive comments
- No hardcoded secrets
- Use environment variables: `${VARIABLE_NAME}`

#### Documentation

Each configuration should include:

**Inline Comments:**
```json
{
  // PostgreSQL MCP server for database operations
  "postgres": {
    "type": "local",  // Runs as local Docker container
    "command": ["docker", "run", "--rm", "-i", "postgres-mcp"],
    "environment": {
      "DB_PASSWORD": "${DB_PASSWORD}"  // Set in your shell
    }
  }
}
```

**Companion README:**
- What the configuration does
- Prerequisites
- Setup instructions
- Usage examples
- Troubleshooting tips

### Documentation Files

#### Format Standard

**All documentation must use GitHub Flavored Markdown (GFM).**

**Required Elements:**
```markdown
# Clear Descriptive Title

Brief introduction explaining purpose.

## Sections with Clear Headings

Content organized logically.

### Subsections as Needed

More detailed information.

**Key Points:**
- Bullet lists for clarity
- `Code formatting` for technical terms
- Clear examples

## Examples

\`\`\`json
{
  "example": "with syntax highlighting"
}
\`\`\`

## Next Steps

Links to related documentation.
```

#### Writing Style

**Conversational Clarity:**
- Explain concepts thoroughly
- Use examples liberally
- Avoid jargon without explanation
- Write for understanding, not brevity

**Structure:**
- Start with "what" and "why"
- Follow with "how"
- Include troubleshooting
- Link to related content

**Examples:**

✅ **Good:**
```markdown
## Setting Up Snyk MCP Server

The Snyk MCP server provides security scanning capabilities directly within OpenCode. It analyzes your code for vulnerabilities, license compliance issues, and dependency risks.

**Prerequisites:**
- Node.js 16 or higher
- Snyk account (free or paid)
- SNYK_TOKEN environment variable

**Setup Steps:**

1. **Create Snyk Account**
   Visit [snyk.io](https://snyk.io) and sign up.

2. **Get API Token**
   Navigate to Account Settings → API Token → Copy
```

❌ **Bad:**
```markdown
## Snyk Setup

Install snyk. Get token. Add to config.
```

#### Code Examples

**Requirements:**
- Syntax highlighting specified
- Complete, working examples
- Comments explaining non-obvious parts
- Error handling shown when relevant

**Example:**
````markdown
```json
{
  "mcp": {
    "snyk": {
      "type": "local",
      "command": ["npx", "-y", "@snyk/mcp-server"],
      "environment": {
        "SNYK_TOKEN": "${SNYK_TOKEN}"  // From your shell environment
      },
      "timeout": 15000  // 15 seconds for npm install
    }
  }
}
```
````

### Behavioral Guidelines

When contributing to `agents/LLM-BaselineBehaviors.md` or related files:

**Principles:**
- Based on real usage patterns
- Tested across multiple models
- Clear rationale provided
- Examples demonstrating behavior

**Format:**
```markdown
### Behavior Area

**Principle:** Clear statement of expected behavior

**Rationale:** Why this behavior is important

**Implementation:**
- Specific guideline 1
- Specific guideline 2
- Specific guideline 3

**Examples:**

✅ **Good:** Demonstration of correct behavior

❌ **Bad:** Counter-example showing what to avoid
```

## Documentation Maintenance

**CRITICAL: When you make ANY changes, you MUST update all related documentation.**

### Files to Update

When changing **configuration files:**
- Related README.md files
- Sample configuration files
- MkDocs documentation in `docs/`
- AGENTS.md if behavior changes

When changing **documentation:**
- Cross-referenced files
- Navigation in `mkdocs.yml` if adding/removing pages
- Index pages that list content

When changing **behavioral baselines:**
- All AGENTS.md files that reference behaviors
- MkDocs behavioral baseline documentation
- Any examples demonstrating the behavior

### Checklist

Before submitting PR, verify:

- [ ] All referenced files exist
- [ ] All links resolve correctly
- [ ] Code examples are accurate
- [ ] JSON is valid
- [ ] Markdown renders correctly
- [ ] No hardcoded secrets
- [ ] Environment variables documented
- [ ] Related docs updated
- [ ] `mkdocs.yml` updated if needed
- [ ] Tested on actual tools/models

## Pull Request Process

### PR Description Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] New configuration
- [ ] Documentation improvement
- [ ] Bug fix
- [ ] Behavioral baseline update
- [ ] Other (specify)

## Changes Made
- Specific change 1
- Specific change 2

## Testing Performed
- How you tested these changes
- Which models/tools tested with
- Any edge cases verified

## Documentation Updated
- [ ] README files
- [ ] AGENTS.md files
- [ ] MkDocs documentation
- [ ] Sample configurations
- [ ] Other (list)

## Related Issues
Fixes #123, Relates to #456
```

### Review Process

1. **Automated Checks** - Ensure all pass
2. **Documentation Review** - Completeness and accuracy
3. **Format Review** - GFM compliance, JSON validity
4. **Content Review** - Usefulness and correctness
5. **Testing** - Maintainer may test your contribution

### Approval and Merge

- At least one maintainer approval required
- All checks must pass
- Documentation must be complete
- Merge typically within 1 week

## Style Guide

### JSON Formatting

```json
{
  "key": "value",
  "nested": {
    "property": "value"
  },
  "array": [
    "item1",
    "item2"
  ]
}
```

**Standards:**
- 2-space indentation
- No trailing commas
- Comments where helpful
- Descriptive keys

### Markdown Formatting

**Headers:**
```markdown
# H1 - Page Title (one per page)
## H2 - Major Sections
### H3 - Subsections
#### H4 - Minor Subsections (use sparingly)
```

**Lists:**
```markdown
- Unordered lists for non-sequential items
- Use bullet points
- Keep items parallel in structure

1. Ordered lists for sequential steps
2. Number automatically
3. Each step on new line
```

**Code:**
```markdown
Inline `code` for short snippets, commands, file names.

```language
Block code for longer examples, always specify language
```
```

**Links:**
```markdown
[Descriptive text](relative/or/absolute/url)
```

**Emphasis:**
```markdown
*Italic* for emphasis
**Bold** for strong emphasis
`Code` for technical terms
```

### Environment Variables

**Always use this pattern:**
```json
{
  "environment": {
    "VARIABLE_NAME": "${VARIABLE_NAME}"
  }
}
```

**Documentation must include:**
- Where to obtain the value
- How to set it (all major shells)
- What permissions/scopes needed
- Security considerations

**Example:**
```markdown
### Setting SNYK_TOKEN

**Obtain Token:**
1. Visit [Snyk Account Settings](https://app.snyk.io/account)
2. Copy your API token

**Set Environment Variable:**

```powershell
# PowerShell (Windows)
$env:SNYK_TOKEN = "your-token-here"
```

```bash
# Bash (Linux/Mac)
export SNYK_TOKEN="your-token-here"
```

**Security:** Never commit this token to version control.
```

## Questions?

- **File an issue** - For questions about contributing
- **Start a discussion** - For ideas and proposals
- **Submit a draft PR** - For early feedback

## Code of Conduct

- Be respectful and constructive
- Focus on the content, not the person
- Assume good intentions
- Help create a welcoming environment

## License

By contributing, you agree that your contributions will be licensed under the same license as this project.

---

**Thank you for contributing!** Your improvements help the entire AI development community.

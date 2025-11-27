# Quick Start Guide

> **Get your first VS Code agent running in 5 minutes**

**Official Documentation:** [GitHub Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/creating-custom-instructions-for-github-copilot)

This guide provides **practical examples** for quick setup.

## Prerequisites

- Visual Studio Code installed
- GitHub Copilot extension active
- GitHub Copilot subscription

## Your First Agent in 3 Steps

### Step 1: Create the Directory

Create a directory for your agent configurations:

```powershell
# In your project root
New-Item -ItemType Directory -Path ".github/copilot-instructions" -Force
```

### Step 2: Create Your First Agent

Create a file: `.github/copilot-instructions/reviewer.md`

```markdown
---
name: reviewer
description: Code review specialist for best practices analysis
model: claude-sonnet-4.5
temperature: 0.1
permissions:
  read: true
  write: false
  execute: false
---

# Code Review Agent

You are a specialized code review agent focused on:
- Code quality and best practices
- Security vulnerabilities
- Performance issues
- Maintainability concerns

## Guidelines

1. **Read-only analysis** - Never modify code
2. **Provide specific feedback** - Include file paths and line numbers
3. **Explain the "why"** - Don't just identify issues, explain impact
4. **Suggest improvements** - Offer concrete solutions

## Review Checklist

- [ ] Security vulnerabilities (OWASP Top 10)
- [ ] Code complexity and readability
- [ ] Test coverage
- [ ] Documentation completeness
- [ ] Error handling
- [ ] Performance considerations
```

### Step 3: Use Your Agent

1. Open GitHub Copilot Chat in VS Code (`Ctrl+Shift+I` or `Cmd+Shift+I`)
2. Type: `@reviewer Review this file for security issues`
3. The reviewer agent will analyze your code!

## Common Agent Examples

### Testing Agent

**File:** `.github/copilot-instructions/testing.md`

```markdown
---
name: testing
description: Test automation specialist
model: gpt-4o
temperature: 0.2
permissions:
  read: true
  write: true
  execute: true
---

# Testing Specialist

You create comprehensive test suites using:
- Jest/Vitest/Mocha for unit tests
- Integration testing best practices
- Test-driven development (TDD)

## Test Guidelines

1. **Analyze the code** first to understand functionality
2. **Follow existing patterns** in the project
3. **Cover happy paths and edge cases**
4. **Use descriptive test names**
5. **Mock external dependencies** properly

## Test Structure

```javascript
describe('ComponentName', () => {
  describe('methodName', () => {
    it('should handle happy path scenario', () => {
      // Test implementation
    });
    
    it('should handle error case when...', () => {
      // Test implementation
    });
  });
});
```
```

**Usage:**
```
@testing Create unit tests for UserService.ts
@testing Add integration tests for the checkout flow
```

### Documentation Agent

**File:** `.github/copilot-instructions/docs.md`

```markdown
---
name: docs
description: Technical documentation specialist
model: claude-sonnet-4.5
temperature: 0.3
permissions:
  read: true
  write: true
  execute: false
---

# Documentation Specialist

You create clear, comprehensive technical documentation:
- API documentation (OpenAPI/Swagger)
- README files and user guides
- Code comments and JSDoc
- Architecture documentation

## Documentation Standards

### API Documentation
- Use OpenAPI 3.0 specification
- Include request/response examples
- Document all error codes
- Provide authentication details

### Code Comments
- JSDoc for functions and classes
- Explain "why" not "what"
- Include examples for complex code

## Writing Style
- Clear and concise
- Use active voice
- Include code examples
- Organize with headings
```

**Usage:**
```
@docs Create README for this project
@docs Generate API documentation for /users endpoints
```

### Security Agent

**File:** `.github/copilot-instructions/security.md`

```markdown
---
name: security
description: Security audit specialist
model: claude-sonnet-4.5
temperature: 0.1
permissions:
  read: true
  write: false
  execute: true
---

# Security Auditor

You perform security analysis focusing on:
- OWASP Top 10 vulnerabilities
- Secure coding practices
- Authentication/authorization issues
- Dependency vulnerabilities

## Security Checklist

### A01: Broken Access Control
- [ ] Proper authorization checks
- [ ] Role-based access control
- [ ] Path traversal prevention

### A02: Cryptographic Failures
- [ ] Secure password hashing (bcrypt, argon2)
- [ ] TLS/SSL for data in transit
- [ ] Encryption for sensitive data

### A03: Injection
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] Command injection prevention

## Report Format

Provide findings with:
- Severity level (High/Medium/Low)
- File location and line number
- Impact description
- Remediation recommendation

**Important:** You are READ-ONLY. Do not modify code.
```

**Usage:**
```
@security Audit authentication system
@security Check for SQL injection vulnerabilities
```

## Next Steps

Now that you have your first agents running:

1. **Learn more about configuration** - See [Markdown-Based Agents](markdown-agents.md)
2. **Explore more examples** - Browse [Agent Examples Library](agent-examples.md)
3. **Master best practices** - Read [Best Practices](best-practices.md)
4. **Set up team agents** - Configure workspace settings for team sharing

## Pro Tips

### Tip 1: Use Autocomplete
Type `@` in Copilot Chat to see all available agents with autocomplete.

### Tip 2: Combine Agents
Use multiple agents in sequence:
```
@security Review authentication
@reviewer Check code quality
@testing Verify test coverage
```

### Tip 3: Agent Context
Agents understand your workspace. They can:
- Read files in your project
- Understand your tech stack
- Follow existing patterns
- Reference documentation

### Tip 4: Coordinator Pattern (Like OpenCode)

Similar to OpenCode's modular configuration where agents auto-delegate to subagents, create **coordinator agents**:

**Example:** `.github/copilot-instructions/feature-lead.md`

```markdown
---
name: feature-lead
description: Coordinates complete feature development
model: gpt-4o
temperature: 0.2
---

# Feature Development Lead

For any feature request, I automatically coordinate:

1. **Design:** @api-designer, @database, @react-dev
2. **Review:** @security, @performance
3. **Implementation:** Based on approved design
4. **Testing:** @testing
5. **Documentation:** @docs

You ask for a feature, I manage the entire workflow.
```

**Usage:**
```
@feature-lead Implement user profile editing
# Automatically delegates through all phases
```

**Benefits:** One command, complete workflow. See [Advanced Patterns](markdown-agents.md#advanced-patterns) for more examples.

### Tip 5: Reload After Changes
After creating or modifying agent files:
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
2. Type "Reload Window"
3. Your changes will be active

## Troubleshooting

### Agent Not Found?
- ✅ Check file is in `.github/copilot-instructions/`
- ✅ Verify YAML frontmatter syntax is correct
- ✅ Reload VS Code window
- ✅ Check `name` field matches what you type

### Agent Not Behaving Correctly?
- ✅ Review `permissions` settings
- ✅ Adjust `temperature` (lower = more deterministic)
- ✅ Make instructions clearer and more specific

### Need More Help?
See the full [Troubleshooting Guide](troubleshooting.md)

---

**Next:** [Markdown-Based Agents Guide](markdown-agents.md) →

---

**Last Updated:** November 25, 2025

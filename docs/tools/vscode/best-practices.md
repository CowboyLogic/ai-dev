# Best Practices

> **Optimization patterns and guidelines for VS Code agent configuration**

## Agent Design Principles

### 1. Single Responsibility

Each agent should have one clear purpose:

**❌ Bad - Too broad:**
```yaml
name: everything-agent
description: Does all development tasks
```

**✅ Good - Focused:**
```yaml
name: reviewer
description: Code review for quality and security
```

```yaml
name: testing
description: Test generation and coverage analysis
```

### 2. Clear Naming

Agent names should be:
- Lowercase with hyphens
- Descriptive and memorable
- Easy to type

**Examples:**
- `reviewer` - Code review
- `testing` - Test automation
- `api-designer` - API design
- `security-audit` - Security analysis

### 3. Appropriate Permissions

Follow the **principle of least privilege**:

| Agent Type | Read | Write | Execute |
|------------|------|-------|---------|
| **Analysis** (review, security) | ✅ | ❌ | ❌ |
| **Implementation** (dev, testing) | ✅ | ✅ | ✅ |
| **Documentation** | ✅ | ✅ | ❌ |
| **Security Scan** | ✅ | ❌ | ✅ |

### 4. Temperature Selection

Match temperature to task:

| Temperature | Use For | Example Agents |
|-------------|---------|----------------|
| 0.0-0.2 | Deterministic, consistent output | `reviewer`, `security` |
| 0.3-0.5 | Balanced creativity | `developer`, `api-designer` |
| 0.6-1.0 | Creative, exploratory | `docs`, `architect` |

### 5. Coordinator Pattern for Complex Workflows

For multi-step processes, create **coordinator agents** that automatically delegate to specialists (similar to OpenCode's modular configuration):

**Pattern: Coordinator + Specialists**

```markdown
---
name: feature-lead
description: Coordinates complete feature development
model: gpt-4o
temperature: 0.2
permissions:
  read: true
  write: true
  execute: true
---

# Feature Development Lead

You orchestrate complete feature development by delegating to specialists.

## Workflow

For any feature request:

1. **Design Phase**
   \```
   @api-designer Design API endpoints
   @database Design schema changes
   @react-dev Design UI components
   \```

2. **Security & Performance Review**
   \```
   @security Review for vulnerabilities
   @performance Check performance implications
   \```

3. **Implementation**
   - Implement based on approved design
   - Follow specialist recommendations

4. **Quality Assurance**
   \```
   @testing Create comprehensive test suite
   @reviewer Review implementation
   \```

5. **Documentation**
   \```
   @docs Generate documentation
   \```

## Example

User: "@feature-lead Add password reset"

You coordinate all phases and specialists automatically.
```

**Benefits:**
- ✅ User invokes one agent, gets complete workflow
- ✅ Consistent process every time
- ✅ All specialist perspectives included
- ✅ Clear separation of concerns

**Common Coordinator Patterns:**
- **`architect`** - Coordinates api-designer, database, security, cloud, performance
- **`feature-lead`** - Coordinates design → review → implementation → testing → docs
- **`review-lead`** - Coordinates security, performance, reviewer, testing audits
- **`api-lead`** - Coordinates API design → security → implementation → testing → docs

**When to Use:**
- Complete feature development
- System architecture design
- Comprehensive code reviews
- Release preparation workflows

## Configuration Best Practices

### Organize by Purpose

**By Role:**
```
.github/copilot-instructions/
├── development/
│   ├── api-designer.md
│   ├── frontend-dev.md
│   └── backend-dev.md
├── quality/
│   ├── reviewer.md
│   ├── testing.md
│   └── security.md
└── documentation/
    └── docs.md
```

**By Tech Stack:**
```
.github/copilot-instructions/
├── react-dev.md
├── node-dev.md
├── python-dev.md
└── general-reviewer.md
```

### Document Agent Capabilities

Include clear sections in agent markdown:

```markdown
---
name: agent-name
description: Brief description
---

# Agent Title

## Purpose
What this agent does and when to use it

## Capabilities
- Specific capability 1
- Specific capability 2

## Limitations
- What this agent CANNOT do
- What this agent should NOT do

## Usage Examples
@agent-name Command example 1
@agent-name Command example 2
```

### Version Control

**Commit agents to repository:**
```bash
git add .github/copilot-instructions/
git commit -m "Add code review and testing agents"
git push
```

**Benefits:**
- Team members get agents automatically
- Track changes over time
- Consistent behavior across team
- Easy rollback if needed

## Multi-Agent Workflows

### Sequential Workflows

Use agents in logical order:

```bash
# Feature development workflow
@api-designer Design the user profile API
# Review the design, then...

@developer Implement the API endpoints
# Code is written, then...

@testing Create comprehensive test suite
# Tests are added, then...

@security Audit for security issues
# Security checked, then...

@docs Generate API documentation
# Finally documented
```

### Parallel Analysis

Run independent analyses together:

```bash
# Submit for parallel analysis
@security Review authentication system
@performance Check for bottlenecks
@reviewer Analyze code quality
```

### Iterative Refinement

Use agents iteratively:

```bash
@developer Implement user registration
# Review output...

@reviewer Check the implementation
# Address issues...

@developer Fix issues found by reviewer
# Test...

@testing Add tests for registration flow
```

## Team Collaboration

### Share Agent Configurations

**1. Create team-wide agents in repository:**
```
.github/copilot-instructions/
├── team-reviewer.md      # Team coding standards
├── team-testing.md       # Team testing practices
└── team-docs.md          # Team documentation style
```

**2. Configure in workspace settings:**

`.vscode/settings.json`:
```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".github/copilot-instructions/team-reviewer.md"
    },
    {
      "file": ".github/copilot-instructions/team-testing.md"
    },
    {
      "file": "agents/LLM-BaselineBehaviors.md"
    }
  ]
}
```

**3. Commit to repository:**
```bash
git add .vscode/settings.json .github/copilot-instructions/
git commit -m "Add team agent configurations"
```

### Standardize Behaviors

Include team standards in agents:

```markdown
---
name: team-reviewer
description: Code review enforcing team standards
---

# Team Code Reviewer

## Team Coding Standards

### Naming Conventions
- Use camelCase for variables/functions
- Use PascalCase for classes/components
- Use UPPER_SNAKE_CASE for constants

### File Organization
- One component per file
- Group by feature, not by type
- Use index.ts for barrel exports

### Testing Requirements
- 80%+ code coverage
- Unit tests for all business logic
- Integration tests for API endpoints

## Review Checklist
- [ ] Follows naming conventions
- [ ] Includes tests
- [ ] Has JSDoc comments
- [ ] No console.log statements
- [ ] Error handling present
```

## Performance Optimization

### Keep Agents Focused

**❌ Bad - Kitchen sink agent:**
```markdown
The agent does code review, testing, documentation,
security audits, performance optimization, and...
```

**✅ Good - Focused agents:**
- `reviewer` - Only code review
- `testing` - Only test generation
- `docs` - Only documentation

### Use Appropriate Models

**For simple tasks:**
```yaml
model: gpt-4o-mini  # Faster, cheaper
```

**For complex analysis:**
```yaml
model: claude-sonnet-4.5  # More capable
```

**For creative work:**
```yaml
model: gpt-4o
temperature: 0.5  # More creative
```

### Optimize Agent Instructions

**Keep instructions concise but complete:**

```markdown
# Good balance

You are a code reviewer focusing on:
- Security (OWASP Top 10)
- Code quality
- Performance

## Process
1. Analyze code
2. Identify issues
3. Suggest fixes

Provide specific feedback with file paths and line numbers.
```

## Common Patterns

### Pattern 1: Read-Only Analyst

```yaml
name: analyst
permissions:
  read: true
  write: false
  execute: false
temperature: 0.1  # Deterministic
```

**Use for:** Review, audit, analysis

### Pattern 2: Careful Implementer

```yaml
name: implementer
permissions:
  read: true
  write: true
  execute: true
temperature: 0.2  # Slightly creative
```

**Use for:** Development, testing

### Pattern 3: Creative Writer

```yaml
name: writer
permissions:
  read: true
  write: true
  execute: false
temperature: 0.5  # Creative
```

**Use for:** Documentation, content creation

### Pattern 4: Security Scanner

```yaml
name: security
permissions:
  read: true
  write: false
  execute: true  # Can run scanning tools
temperature: 0.1  # Consistent
```

**Use for:** Security audits, vulnerability scanning

## Quick Reference

### Agent Configuration Checklist

- [ ] Clear, descriptive name
- [ ] Concise description
- [ ] Appropriate model selection
- [ ] Correct temperature setting
- [ ] Minimal necessary permissions
- [ ] Clear purpose statement
- [ ] Usage examples included
- [ ] Limitations documented

### Permission Quick Guide

```yaml
# Analysis only
permissions: { read: true, write: false, execute: false }

# Implementation
permissions: { read: true, write: true, execute: true }

# Documentation
permissions: { read: true, write: true, execute: false }

# Security scanning
permissions: { read: true, write: false, execute: true }
```

### Temperature Quick Guide

```yaml
temperature: 0.1  # Security, review, refactoring
temperature: 0.3  # Development, API design, testing
temperature: 0.5  # Documentation, architecture, creative
```

## Anti-Patterns to Avoid

### ❌ Don't: Give Excessive Permissions

```yaml
# Bad - Review agent doesn't need write access
name: reviewer
permissions:
  write: true  # Not needed for review!
```

### ❌ Don't: Create Duplicate Agents

```yaml
# Bad - Just variations of same thing
name: reviewer-strict
name: reviewer-lenient
name: reviewer-security

# Good - One focused agent
name: reviewer  # Covers all review aspects
```

### ❌ Don't: Use Vague Names

```yaml
# Bad names
name: helper
name: agent1
name: do-stuff

# Good names
name: reviewer
name: testing
name: api-designer
```

### ❌ Don't: Overload Agent Instructions

Keep instructions focused and scannable, not pages of text.

## Additional Tips

1. **Start small** - Create 2-3 essential agents first
2. **Test thoroughly** - Verify each agent before sharing with team
3. **Iterate** - Refine based on actual usage
4. **Document changes** - Note why you adjust temperature or permissions
5. **Share learnings** - Communicate what works well with your team

---

**Next:** [Troubleshooting](troubleshooting.md) →

**Last Updated:** November 25, 2025

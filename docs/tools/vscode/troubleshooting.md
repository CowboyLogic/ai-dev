# Troubleshooting

> **Common issues and solutions for VS Code agent configuration**

## Markdown-Based Agents

### Agent Not Recognized

**Symptoms:**
- `@agentname` doesn't autocomplete
- Agent doesn't appear in Copilot Chat
- No response when invoking agent

**Solutions:**

✅ **Check file location:**
```bash
# File must be in correct directory
.github/copilot-instructions/agentname.md
# OR
agents/agentname.md
```

✅ **Verify YAML frontmatter:**
```yaml
---
name: agentname  # Must match what you type
description: Valid description
---
```

✅ **Reload VS Code:**
1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Reload Window"
3. Press Enter

✅ **Check workspace settings:**
```json
// .vscode/settings.json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".github/copilot-instructions/agentname.md"
    }
  ]
}
```

### YAML Syntax Errors

**Symptoms:**
- Agent loads but behaves strangely
- Error messages about configuration
- Agent uses default settings instead of custom

**Solutions:**

✅ **Validate YAML syntax:**
```yaml
---
# Correct - uses colons and proper indentation
name: reviewer
description: Code review specialist
permissions:
  read: true
  write: false
---

# WRONG - syntax errors
name = reviewer  # Should use colon, not equals
description "Code review"  # Missing colon
permissions:
read: true  # Wrong indentation
```

✅ **Check for special characters:**
```yaml
# Quote strings with special characters
description: "Code review: security & quality"
```

✅ **Validate online:**
Use [YAML Lint](http://www.yamllint.com/) to check syntax

### Agent Not Following Instructions

**Symptoms:**
- Agent ignores documented guidelines
- Doesn't follow specified format
- Behaves inconsistently

**Solutions:**

✅ **Make instructions more explicit:**
```markdown
# Vague
You review code.

# Explicit
You are a READ-ONLY code reviewer. You MUST:
1. Analyze code without modifying it
2. Provide specific file:line references
3. Explain WHY each issue matters
4. Suggest concrete fixes
```

✅ **Adjust temperature:**
```yaml
# If responses too random
temperature: 0.1  # More deterministic

# If responses too rigid
temperature: 0.3  # More balanced
```

✅ **Check permissions match intent:**
```yaml
# For review agent - should be read-only
permissions:
  read: true
  write: false  # Prevent code modifications
  execute: false
```

### Wrong Permissions

**Symptoms:**
- "I don't have permission to..." messages
- Agent can't perform intended tasks
- Agent modifies code when it shouldn't

**Solutions:**

✅ **Review permission settings:**
```yaml
# Analysis agents
permissions:
  read: true
  write: false
  execute: false

# Implementation agents
permissions:
  read: true
  write: true
  execute: true
```

✅ **Match permissions to purpose:**

| Agent Purpose | Read | Write | Execute |
|---------------|------|-------|---------|
| Code review | ✅ | ❌ | ❌ |
| Testing | ✅ | ✅ | ✅ |
| Documentation | ✅ | ✅ | ❌ |
| Security scan | ✅ | ❌ | ✅ |

### Agent Too Verbose or Too Terse

**Symptoms:**
- Responses are too long/detailed
- Responses are too short/missing info

**Solutions:**

✅ **Specify output format:**
```markdown
## Output Format

Provide:
- **Summary** - 2-3 sentences max
- **Issues** - Bullet list, max 5 items
- **Recommendation** - One specific action

Keep total response under 500 words.
```

✅ **Adjust temperature:**
```yaml
# More concise
temperature: 0.1

# More elaborate
temperature: 0.4
```

### Agent Mixing Concerns

**Symptoms:**
- Review agent tries to implement fixes
- Documentation agent tries to refactor code
- Agent does unrelated tasks

**Solutions:**

✅ **Emphasize limitations:**
```markdown
## What You MUST NOT Do

- ❌ Modify code (you are READ-ONLY)
- ❌ Implement fixes (only suggest)
- ❌ Run commands (no execute permission)
- ❌ Create files (no write permission)

**Important:** If asked to do any of the above, explain your limitations
and suggest the appropriate agent (@developer, @testing, etc.)
```

## Programmatic SubAgents

### SubAgent Returns Incomplete Results

**Symptoms:**
- SubAgent finishes but missing expected information
- Partial analysis or implementation
- Vague or unclear response

**Solutions:**

✅ **Be more specific about output:**
```typescript
// Vague
prompt: "Analyze the code"

// Specific
prompt: `Analyze authentication code.

Return JSON:
{
  "files_analyzed": ["file1", "file2"],
  "issues": [
    {"file": "...", "line": 123, "issue": "...", "severity": "HIGH"}
  ],
  "summary": "..."
}`
```

✅ **Include examples:**
```typescript
prompt: `...

Example output:
## Critical Issues
1. **SQL Injection** in \`user.ts:45\`
   - Impact: Database compromise
   - Fix: Use parameterized queries
`
```

✅ **Break into smaller tasks:**
```typescript
// Too broad
runSubagent({ prompt: "Analyze entire codebase" })

// Focused
runSubagent({ prompt: "Analyze authentication in src/auth/" })
runSubagent({ prompt: "Analyze API endpoints in src/api/" })
```

### SubAgent Takes Too Long

**Symptoms:**
- SubAgent runs for extended time
- No progress indication
- Times out before completing

**Solutions:**

✅ **Narrow the scope:**
```typescript
// Too broad - searches everything
prompt: "Find all database queries"

// Focused - specific location
prompt: "Find database queries in src/api/users/"
```

✅ **Specify file patterns:**
```typescript
prompt: `Search only TypeScript files in src/api/
Pattern: src/api/**/*.ts
Exclude: test files, node_modules`
```

✅ **Limit results:**
```typescript
prompt: `Find top 10 most complex functions.
Return only the 10 highest complexity, not all functions.`
```

### SubAgent Can't Find Expected Code

**Symptoms:**
- SubAgent reports "not found" when code exists
- Misses obvious patterns
- Returns no results

**Solutions:**

✅ **Provide multiple search strategies:**
```typescript
prompt: `Find authentication code using ANY of:
1. Functions named: login, authenticate, signIn, auth
2. Imports from: passport, jwt, bcrypt
3. Files in: auth/, authentication/, middleware/auth
4. Comments containing: authentication, login, auth

Try all strategies and combine results.`
```

✅ **Specify file locations:**
```typescript
prompt: `Search for authentication in:
- src/auth/
- src/middleware/
- src/api/auth/
- src/services/auth*

Do not search test files.`
```

✅ **Include alternative patterns:**
```typescript
prompt: `Find error handling using:
- try/catch blocks
- .catch() on promises
- error middleware
- Error classes

Search for pattern variations.`
```

### Results Don't Match Expectations

**Symptoms:**
- SubAgent returns different information than expected
- Analysis focuses on wrong aspects
- Implementation doesn't match requirements

**Solutions:**

✅ **Provide clear acceptance criteria:**
```typescript
prompt: `Implement password reset feature.

Must include:
- [ ] POST /api/auth/reset-password endpoint
- [ ] Email verification token generation
- [ ] Token expiration (15 minutes)
- [ ] Secure password hashing
- [ ] Unit tests for all functions

Do not proceed without ALL items above.`
```

✅ **Include examples:**
```typescript
prompt: `Create tests similar to existing tests in tests/api/auth.test.ts

Example test structure:
describe('PasswordReset', () => {
  it('should send reset email', async () => {
    // Test implementation
  });
});

Match this style exactly.`
```

✅ **Clarify research vs implementation:**
```typescript
// Clear intent
prompt: `This is RESEARCH ONLY - no code changes.
Analyze and return recommendations only.`

// Or
prompt: `This is IMPLEMENTATION - write complete working code.
Create all necessary files.`
```

## Common Configuration Issues

### Agent Context Too Long

**Symptoms:**
- Errors about context length
- Agent seems to "forget" early instructions
- Incomplete processing

**Solutions:**

✅ **Split into focused agents:**
```markdown
# Instead of one giant agent, create:
security.md         # Security focus
performance.md      # Performance focus
quality.md          # Code quality focus
```

✅ **Remove unnecessary content:**
```markdown
# Remove lengthy examples
# Keep instructions concise
# Link to external docs instead of embedding
```

✅ **Use external references:**
```markdown
For detailed style guide, see: docs/STYLE_GUIDE.md
For security standards, see: docs/SECURITY.md
```

### Model Not Available

**Symptoms:**
- Error about unavailable model
- Falls back to default model
- Agent doesn't work

**Solutions:**

✅ **Check model availability:**
```yaml
# Available models (as of Nov 2025)
model: gpt-4o
model: gpt-4o-mini
model: claude-sonnet-4.5
model: claude-haiku-4.5
```

✅ **Use default if unsure:**
```yaml
# Omit model to use system default
---
name: reviewer
description: Code reviewer
# No model specified - uses default
---
```

### Workspace Settings Ignored

**Symptoms:**
- Settings in `.vscode/settings.json` not applied
- Agents not loading automatically

**Solutions:**

✅ **Check file location:**
```
project-root/
└── .vscode/
    └── settings.json  # Must be here
```

✅ **Verify JSON syntax:**
```json
{
  // Correct syntax
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "file": ".github/copilot-instructions/reviewer.md"
    }
  ]
}
```

✅ **Use relative paths:**
```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      // Relative to workspace root
      "file": ".github/copilot-instructions/reviewer.md"
    }
  ]
}
```

## Getting Help

### Debug Checklist

When an agent isn't working:

- [ ] File in correct location (`.github/copilot-instructions/`)
- [ ] Valid YAML frontmatter
- [ ] `name` field matches invocation
- [ ] Reloaded VS Code window
- [ ] Checked for YAML syntax errors
- [ ] Reviewed permissions settings
- [ ] Checked model availability
- [ ] Verified workspace settings

### Enable Logging

To see what's happening:

1. Open Output panel (`Ctrl+Shift+U` or `Cmd+Shift+U`)
2. Select "GitHub Copilot" from dropdown
3. Observe logs during agent invocation

### Test Incrementally

Start simple and add complexity:

```markdown
# Step 1: Minimal agent
---
name: test
description: Test agent
---
Test agent

# Step 2: Add permissions
---
name: test
description: Test agent
permissions:
  read: true
---

# Step 3: Add full instructions
...
```

### Community Resources

- **[GitHub Copilot Docs](https://docs.github.com/en/copilot)** - Official documentation
- **[GitHub Community](https://github.com/community)** - Community discussions
- **[VS Code Issues](https://github.com/microsoft/vscode/issues)** - Report VS Code issues

---

**Back to:** [Overview](README.md)

**Last Updated:** November 25, 2025

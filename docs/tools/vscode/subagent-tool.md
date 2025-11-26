# Programmatic SubAgents

> **Using the `runSubagent` tool for complex, autonomous tasks**

## Overview

The `runSubagent` tool enables you to programmatically delegate complex, multi-step tasks to autonomous sub-agents. Unlike markdown-based agents, subagents are launched on-demand for specific complex tasks that require deep research or autonomous decision-making.

## When to Use runSubagent

### ✅ Ideal Use Cases

**Use `runSubagent` when you need:**

- **Complex codebase research** - Multi-pattern searches across many files
- **Autonomous code generation** - Large features requiring decision-making
- **Deep analysis tasks** - Comprehensive reports requiring tool orchestration
- **One-off complex tasks** - Tasks too specific for reusable agents

### ❌ When NOT to Use

**Don't use `runSubagent` for:**

- **Simple operations** - Reading a file, editing one function
- **Reusable behaviors** - Use markdown agents instead
- **Interactive tasks** - Tasks needing user input during execution
- **Quick questions** - Answer directly without delegation

## How It Works

### Tool Definition

```typescript
runSubagent({
  description: string,  // 3-5 word task description
  prompt: string        // Detailed autonomous task instructions
})
```

### Execution Flow

1. **Primary agent identifies** a complex task suitable for delegation
2. **Primary agent calls** `runSubagent` with detailed instructions
3. **SubAgent launches** and works autonomously (no communication)
4. **Primary agent waits** for completion
5. **SubAgent returns** single message with results
6. **Primary agent processes** and presents to user

### Critical Requirements

**✅ Must Include:**
- Highly detailed task description
- Exact output format specification
- Clear indication: RESEARCH or IMPLEMENTATION
- All necessary context for autonomous work

**❌ Cannot Do:**
- Communicate during execution
- Ask user for clarification
- Access conversation history
- Return multiple updates

## Configuration Strategies

### Strategy 1: Research Before Action

Use subagent to gather information first:

```typescript
// Step 1: Launch research subagent
const research = await runSubagent({
  description: "Research error handling patterns",
  prompt: `Analyze existing error handling patterns in the codebase.
  
  Search for:
  1. Custom error classes
  2. Error handling middleware
  3. Logging strategies
  4. Error response formats
  
  Return JSON summary:
  {
    "error_classes": ["file:line", ...],
    "middleware": "file path and approach",
    "logging": "strategy description",
    "response_format": "current standard"
  }
  
  This is RESEARCH ONLY - no code changes.`
})

// Step 2: Use research to inform implementation
// Now implement following discovered patterns
```

### Strategy 2: Parallel Investigation

Launch subagent while handling other work:

```typescript
// Launch time-consuming analysis
const analysis = runSubagent({
  description: "Dependency security analysis",
  prompt: `Analyze all dependencies for security issues.
  
  Check:
  - package.json for outdated packages
  - Known CVEs in dependencies
  - License compatibility
  
  Return report with HIGH/MEDIUM/LOW severity issues.
  
  ANALYSIS ONLY.`
})

// Meanwhile, work on other aspects
// Results ready when subagent completes
```

### Strategy 3: Specialized Task Delegation

Delegate complex implementation:

```typescript
runSubagent({
  description: "Generate comprehensive tests",
  prompt: `Create complete test suite for src/services/payment.ts.
  
  Requirements:
  1. Analyze PaymentService to understand all methods
  2. Create tests in tests/services/payment.test.ts
  3. Include:
     - Unit tests for all public methods
     - Integration tests for payment flow
     - Edge case testing (declined cards, timeouts, etc.)
     - Proper mocking for Stripe API
  4. Follow testing patterns in tests/services/user.test.ts
  5. Use Jest and follow project conventions
  
  Technical requirements:
  - Target 90%+ coverage
  - Mock all external services
  - Test async operations properly
  - Include setup/teardown
  
  This is IMPLEMENTATION - write the test file.
  
  Return:
  - Test coverage summary
  - List of test cases created
  - Any edge cases needing manual testing
  - Suggested additional tests`
})
```

### Strategy 4: Incremental Implementation

Break large features into phases:

```typescript
// Phase 1: Database layer
await runSubagent({
  description: "Create database schema",
  prompt: `Create database schema for blog feature.
  
  Tables needed:
  - posts (id, title, content, author_id, created_at, updated_at)
  - comments (id, post_id, user_id, content, created_at)
  - categories (id, name, slug)
  - post_categories (post_id, category_id) - junction table
  
  Create:
  - Prisma schema definitions
  - Migration files
  - Seed data examples
  
  Follow existing schema patterns in prisma/schema.prisma.
  
  IMPLEMENTATION - create files.
  Return summary of schema decisions.`
})

// Phase 2: API layer (after Phase 1)
await runSubagent({
  description: "Implement blog API",
  prompt: `Create REST API for blog functionality.
  
  Use database schema just created.
  Implement CRUD for posts, comments, categories.
  
  IMPLEMENTATION - create API files.`
})
```

## Example Use Cases

### Example 1: Code Pattern Discovery

```typescript
runSubagent({
  description: "Find authentication patterns",
  prompt: `Search codebase for all authentication implementations.
  
  Find:
  1. Login/logout endpoints
  2. JWT/session handling
  3. Password hashing strategy
  4. Authorization middleware
  5. OAuth integrations
  
  For each, document:
  - File location (path:line)
  - Implementation approach
  - Dependencies used
  
  Return markdown report with:
  ## Authentication Strategy
  [Summary of approach]
  
  ## Implementation Locations
  | Component | File | Approach |
  |-----------|------|----------|
  
  ## Security Concerns
  [Any issues found]
  
  RESEARCH ONLY.`
})
```

### Example 2: Performance Investigation

```typescript
runSubagent({
  description: "Analyze query performance",
  prompt: `Find and analyze all database queries for performance issues.
  
  Investigation:
  1. Find all database queries in src/
  2. Identify N+1 query patterns
  3. Check for missing indexes
  4. Analyze query complexity
  5. Find sequential queries that could be parallel
  
  For each issue:
  - Location and query code
  - Performance impact estimate
  - Optimization suggestion with code
  
  Return prioritized list:
  ## Critical Issues (fix immediately)
  1. [Issue with HIGH impact]
  
  ## Optimizations (medium priority)
  1. [Issue with MEDIUM impact]
  
  ## Before/After Examples
  [Code comparisons for top 3 issues]
  
  ANALYSIS ONLY.`
})
```

### Example 3: Migration Planning

```typescript
runSubagent({
  description: "Plan TypeScript migration",
  prompt: `Create migration plan for converting JavaScript to TypeScript.
  
  Analysis:
  1. Inventory all .js files in src/
  2. Identify dependencies and migration order
  3. Find required type definitions
  4. Assess complexity of each file (simple/medium/complex)
  5. Recommend migration phases
  
  Return detailed plan:
  ## Migration Strategy
  [Overall approach]
  
  ## File Inventory
  - Total files: X
  - Simple: Y (no complex types)
  - Medium: Z (some typing needed)
  - Complex: N (extensive typing)
  
  ## Recommended Order
  Phase 1: [Files with no dependencies]
  Phase 2: [Core utilities]
  Phase 3: [Business logic]
  Phase 4: [Entry points]
  
  ## Type Definition Needs
  [List of @types packages needed]
  
  ## Estimated Effort
  [Time estimates per phase]
  
  PLANNING ONLY - no code changes.`
})
```

## Best Practices

### 1. Write Comprehensive Prompts

**❌ Bad - Vague:**
```typescript
runSubagent({
  description: "Fix the API",
  prompt: "Look at the API and make it better"
})
```

**✅ Good - Specific:**
```typescript
runSubagent({
  description: "Optimize user API endpoints",
  prompt: `Analyze and optimize User API in src/api/users/.
  
  Tasks:
  1. Review endpoint response times
  2. Identify N+1 query problems
  3. Find unnecessary data fetching
  4. Recommend caching opportunities
  
  Context:
  - Using Express.js and Prisma ORM
  - Current avg response time: 500ms
  - Target: <100ms
  
  Return:
  - Prioritized optimization list
  - Code examples for top 3 fixes
  - Expected performance improvement
  
  ANALYSIS with suggested fixes.`
})
```

### 2. Specify Research vs Implementation

Always clarify what the subagent should do:

```typescript
// Research only
prompt: `...
This is RESEARCH ONLY - do not modify any code.
Return analysis and recommendations.`

// Implementation
prompt: `...
This is IMPLEMENTATION - write all necessary code.
Return summary of files created/modified.`

// Analysis with suggestions
prompt: `...
This is ANALYSIS with code suggestions.
Provide examples but don't modify files.`
```

### 3. Define Expected Output

Tell subagent exactly what to return:

```typescript
prompt: `...

Return JSON:
{
  "summary": "brief overview",
  "findings": [
    {
      "file": "path/to/file",
      "issue": "description",
      "severity": "high|medium|low",
      "fix": "recommended solution"
    }
  ],
  "next_steps": ["action 1", "action 2"]
}`
```

### 4. Provide Context

Include relevant architectural information:

```typescript
prompt: `...

Current architecture:
- Framework: Express.js with TypeScript
- Database: PostgreSQL with Prisma ORM
- Auth: JWT tokens
- Testing: Jest

Existing patterns to follow:
- Error handling: src/middleware/errorHandler.ts
- Logging: src/utils/logger.ts
- API structure: src/api/README.md

Requirements:
[Detailed requirements]

Return: [Expected output]`
```

### 5. Scope Appropriately

**❌ Too broad:**
```typescript
prompt: "Build entire e-commerce platform"
```

**✅ Focused:**
```typescript
prompt: "Implement shopping cart add/remove/update operations"
```

## Comparison with Markdown Agents

| Aspect | Markdown Agents | runSubagent |
|--------|-----------------|-------------|
| **Setup** | Create file once | No setup |
| **Invocation** | `@agentname` | Full prompt each time |
| **Reusability** | High - use repeatedly | Low - recreate each time |
| **Complexity** | Simple tasks | Complex autonomous tasks |
| **Team Sharing** | Commit to repo | N/A |
| **Best For** | Consistent behaviors | One-off complex research |

### When to Use Each

**Use Markdown Agents:**
- Code review workflow
- Testing automation
- Documentation generation
- Recurring specialized tasks

**Use runSubagent:**
- One-time codebase analysis
- Complex migration planning
- Deep research requiring multiple tool calls
- Tasks too specific for reusable agent

## Troubleshooting

### SubAgent Returns Incomplete Results

**Solutions:**
- ✅ Be more specific about required output format
- ✅ Include examples of expected results
- ✅ Break into smaller, focused tasks
- ✅ Specify exact file paths or patterns

### SubAgent Takes Too Long

**Solutions:**
- ✅ Narrow the scope (specific directories)
- ✅ Use file patterns to limit search
- ✅ Break into multiple smaller subagents
- ✅ Specify maximum results needed

### Results Don't Match Expectations

**Solutions:**
- ✅ Provide examples of expected output
- ✅ Be more explicit about requirements
- ✅ Include acceptance criteria
- ✅ Specify level of detail needed

---

**Next:** [Best Practices](best-practices.md) →

**Last Updated:** November 25, 2025

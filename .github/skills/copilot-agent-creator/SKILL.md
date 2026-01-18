---
name: copilot-agent-creator
description: Guide for creating custom agents for VS Code and GitHub Copilot. Use this when building VS Code extensions, MCP servers, or custom agent configurations that integrate with Copilot.
license: MIT
---

# Copilot Agent Creator

This skill provides comprehensive guidance for creating custom agents that integrate with VS Code and GitHub Copilot. It covers VS Code extension development, MCP (Model Context Protocol) server creation, agent configuration, and best practices for building effective AI-powered tools.

## When to Use This Skill

Use this skill when:
- Creating VS Code extensions with AI capabilities
- Building MCP servers for Copilot integration
- Developing custom agents for specific workflows
- Setting up agent configurations for development tasks
- Integrating AI tools with VS Code's extension API
- Creating specialized agents for code review, testing, or documentation

## Prerequisites

- Basic knowledge of JavaScript/TypeScript (for extensions)
- Understanding of VS Code extension development (for extensions)
- Familiarity with Node.js and npm (for extensions)
- Access to VS Code API documentation (for extensions)
- **Always check the latest GitHub documentation**: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents
- Knowledge of the task domain (e.g., testing, documentation, etc.)

## Latest Information Check

**IMPORTANT**: Before creating any custom agents, always check the official GitHub documentation for the latest information on custom agents: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents

Key points from the latest documentation:
- Custom agents are specialized versions of Copilot coding agent
- They are defined using Markdown files called "agent profiles"
- Agent profiles use YAML frontmatter with name, description, and prompt
- They can include tools and MCP server configurations
- Available at repository level (`.github/agents/`) or organization level
- Work in VS Code, JetBrains IDEs, Eclipse, Xcode, and GitHub.com

## Instructions

### Step 1: Plan Your Agent

1. **Define the scope**: What specific task or domain will your agent handle?
2. **Identify integration points**: How will it integrate with VS Code/Copilot?
3. **Determine the agent type**: Extension, MCP server, or configuration-based agent?
4. **Assess required APIs**: What VS Code APIs or external services are needed?

### Step 2: Choose the Implementation Approach

#### Primary Approach: Custom Agent Profiles (Recommended)
For most use cases, create custom agent profiles using Markdown files:

1. **Check GitHub documentation**: Visit https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents
2. **Create agent profile**: Use `.github/agents/YOUR-AGENT-NAME.md` format
3. **Define YAML frontmatter**: Include name, description, and prompt
4. **Configure tools and MCP servers** (optional): Specify tools the agent can access
5. **Test the agent**: Use in VS Code, GitHub.com, or other supported environments

#### Option A: VS Code Extension Agent
For agents that need deep VS Code integration beyond what custom profiles provide:

1. Use `create_new_workspace` tool with `projectType: 'vscode-extension'`
2. Implement using VS Code Extension API
3. Register commands, providers, and handlers
4. Use `get_vscode_api` tool for API documentation

#### Option B: MCP Server Agent
For agents that provide custom tools to Copilot via the Model Context Protocol:

1. Use `create_new_workspace` tool with `projectType: 'model-context-protocol-server'`
2. Implement MCP protocol handlers
3. Define tools, resources, and prompts
4. Configure server connection in VS Code settings or agent profiles

### Step 3: Create Custom Agent Profile

For the recommended approach using custom agent profiles:

1. **Create the agent file**: Create `.github/agents/your-agent-name.md` in your repository
2. **Add YAML frontmatter**:
   ```yaml
   ---
   name: your-agent-name
   description: Brief description of what this agent does
   ---
   ```
3. **Write the prompt**: Define the agent's behavior and expertise
4. **Configure tools** (optional): Specify which tools the agent can access
5. **Add MCP servers** (optional): Include MCP server configurations for organization/enterprise agents

### Step 4: Implement Core Functionality

1. **For Extensions**:
   ```typescript
   // Activate the extension
   export function activate(context: vscode.ExtensionContext) {
     // Register commands, providers, etc.
   }
   ```

2. **For MCP Servers**:
   ```typescript
   const server = new Server({
     name: 'my-agent',
     version: '1.0.0'
   }, {
     capabilities: {
       tools: {},
       resources: {},
       prompts: {}
     }
   });
   ```

3. **Define agent capabilities**:
   - Tools: Executable functions
   - Resources: Data sources
   - Prompts: Reusable prompt templates

### Step 4: Add VS Code Integration

1. **Register commands**:
   ```typescript
   vscode.commands.registerCommand('myAgent.command', async () => {
     // Command implementation
   });
   ```

2. **Create webview panels** (if needed):
   ```typescript
   const panel = vscode.window.createWebviewPanel(
     'myAgent',
     'My Agent',
     vscode.ViewColumn.One,
     { enableScripts: true }
   );
   ```

3. **Handle workspace events**:
   ```typescript
   vscode.workspace.onDidChangeTextDocument(event => {
     // Handle document changes
   });
   ```

### Step 5: Implement AI Integration

1. **Use Copilot API** (when available):
   ```typescript
   // Access Copilot suggestions
   const copilot = vscode.extensions.getExtension('GitHub.copilot');
   ```

2. **Create custom prompts**:
   ```typescript
   const prompt = {
     name: 'code-review',
     description: 'Review code for best practices',
     arguments: [{ name: 'code', description: 'Code to review' }]
   };
   ```

3. **Handle AI responses**:
   - Parse structured outputs
   - Provide feedback to users
   - Integrate with VS Code UI

### Step 6: Add Error Handling and Logging

1. **Implement proper error handling**:
   ```typescript
   try {
     // Agent logic
   } catch (error) {
     vscode.window.showErrorMessage(`Agent error: ${error.message}`);
   }
   ```

2. **Add logging**:
   ```typescript
   const logger = vscode.window.createOutputChannel('My Agent');
   logger.appendLine('Agent started');
   ```

### Step 7: Test and Debug

1. **Use VS Code's debugger** for extension development
2. **Test MCP server** with MCP client tools
3. **Validate agent responses** in VS Code environment
4. **Check for API compatibility** across VS Code versions

### Step 8: Package and Distribute

1. **Update package.json** with proper metadata
2. **Create vsix package** for extensions
3. **Document installation** and configuration steps
4. **Publish to marketplace** or provide installation instructions

## Examples

### Example 1: Custom Agent Profile for Code Review

Create `.github/agents/code-reviewer.md`:

```markdown
---
name: code-reviewer
description: Agent specializing in code review with focus on best practices, security, and performance
---

You are an expert code reviewer with deep knowledge of software development best practices, security vulnerabilities, and performance optimization. Your role is to provide thorough, constructive code reviews that help improve code quality, maintainability, and reliability.

## Code Review Guidelines

### General Principles
- Focus on code clarity, maintainability, and correctness
- Suggest improvements rather than just pointing out problems
- Consider the broader context and impact of changes
- Be specific about why changes are needed and what benefits they provide

### Security Review
- Check for common vulnerabilities (SQL injection, XSS, CSRF, etc.)
- Verify proper input validation and sanitization
- Ensure secure handling of sensitive data
- Review authentication and authorization logic

### Performance Considerations
- Identify potential performance bottlenecks
- Check for inefficient algorithms or data structures
- Review database queries for optimization opportunities
- Consider memory usage and resource management

### Code Quality Standards
- Ensure consistent naming conventions
- Check for proper error handling
- Verify appropriate logging and monitoring
- Review test coverage and quality

## Review Process
1. Understand the change context and requirements
2. Review code for functionality and correctness
3. Check security implications
4. Assess performance impact
5. Evaluate code quality and maintainability
6. Provide actionable feedback with specific recommendations

Always provide specific, actionable feedback with code examples when suggesting improvements.
```

### Example 2: Code Review Agent Extension

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand('codeReviewAgent.review', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const code = editor.document.getText();
    const review = await performCodeReview(code);

    const panel = vscode.window.createWebviewPanel(
      'codeReview',
      'Code Review Results',
      vscode.ViewColumn.Beside,
      {}
    );

    panel.webview.html = generateReviewHTML(review);
  });

  context.subscriptions.push(disposable);
}

async function performCodeReview(code: string): Promise<ReviewResult> {
  // AI-powered code review logic
  return { issues: [], suggestions: [] };
}
```

### Example 2: MCP Server for Database Operations

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const server = new Server({
  name: 'database-agent',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {
      'query-database': {
        description: 'Execute SQL queries',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string' }
          },
          required: ['query']
        }
      }
    }
  }
});

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'query-database') {
    const result = await executeQuery(args.query);
    return {
      content: [{ type: 'text', text: JSON.stringify(result) }]
    };
  }
});
```

### Example 3: Configuration-Based Testing Agent

```json
{
  "agent": {
    "name": "testing-agent",
    "description": "Automated testing agent",
    "tools": [
      {
        "name": "run-tests",
        "command": "npm test",
        "description": "Run test suite"
      },
      {
        "name": "generate-tests",
        "command": "npx jest --init",
        "description": "Generate test files"
      }
    ],
    "prompts": [
      {
        "name": "test-coverage",
        "template": "Analyze test coverage for {file} and suggest improvements"
      }
    ]
  }
}
```

## Best Practices

### Extension Development
- Follow VS Code extension guidelines
- Use TypeScript for type safety
- Implement proper activation/deactivation
- Handle workspace trust and permissions
- Test across different VS Code versions

### MCP Server Development
- Implement proper error handling
- Use structured schemas for inputs/outputs
- Provide clear tool descriptions
- Handle connection lifecycle properly
- Support cancellation and timeouts

### Agent Design
- Keep agents focused on specific tasks
- Provide clear user feedback
- Handle edge cases gracefully
- Document capabilities and limitations
- Consider performance implications

### Security Considerations
- Validate all inputs
- Use secure communication protocols
- Respect user privacy
- Implement proper authentication
- Avoid exposing sensitive data

## Common Issues

**Issue**: Extension not activating
**Solution**: Check package.json activation events and main entry point

**Issue**: MCP server connection fails
**Solution**: Verify server configuration in VS Code settings and check server logs

**Issue**: Agent responses are inconsistent
**Solution**: Implement proper prompt engineering and response validation

**Issue**: Performance problems
**Solution**: Optimize async operations and implement caching where appropriate

**Issue**: VS Code API compatibility
**Solution**: Check API availability and use feature detection

## Additional Resources

- **[GitHub Custom Agents Documentation](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)** - Official documentation for creating custom agents (always check this first)
- [Creating Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents) - Step-by-step guide for creating custom agents
- [VS Code Extension API](https://code.visualstudio.com/api)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [VS Code Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [Copilot Extensibility](https://docs.github.com/en/copilot)
- [Agent Skills Standard](https://agentskills.io)

## Testing Checklist

- [ ] Extension activates properly
- [ ] Commands execute without errors
- [ ] UI elements render correctly
- [ ] Error handling works as expected
- [ ] Performance is acceptable
- [ ] Compatible with target VS Code versions
- [ ] MCP server (if applicable) connects successfully
- [ ] Tools/resources/prompts function correctly
- [ ] Documentation is complete and accurate
# Copilot Agent Creator

A comprehensive skill for creating custom agents that integrate with VS Code and GitHub Copilot. This skill provides guidance for developing VS Code extensions, MCP servers, and most importantly, custom agent profiles for GitHub Copilot coding agent.

## Overview

The Copilot Agent Creator skill helps developers build sophisticated AI-powered tools that extend VS Code's capabilities and create specialized versions of GitHub Copilot coding agent. Whether you're creating a full VS Code extension, an MCP server for Copilot integration, or a custom agent profile, this skill provides step-by-step guidance and best practices.

## Key Features

- **Custom Agent Profiles**: Create specialized versions of Copilot coding agent using Markdown files
- **VS Code Extension Development**: Complete guide for building extensions with AI capabilities
- **MCP Server Creation**: Instructions for Model Context Protocol servers
- **Agent Configuration**: Best practices for setting up custom agent workflows
- **Integration Patterns**: How to connect agents with VS Code APIs and Copilot
- **Testing and Debugging**: Comprehensive testing strategies

## Quick Start

1. **Check the latest GitHub documentation**: Always visit https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents first
2. **Choose your approach**:
   - **Custom Agent Profiles** (recommended): Create `.github/agents/your-agent.md` files
   - VS Code Extension: For deep IDE integration
   - MCP Server: For custom tools via Model Context Protocol

3. **Follow the skill instructions**:
   - Plan your agent's scope and capabilities
   - Implement using the appropriate framework
   - Test thoroughly in VS Code environment
   - Package and distribute your agent

4. **Use the examples**:
   - Custom agent profile for code review
   - VS Code extension with AI code review functionality
   - MCP server for file system operations

## Prerequisites

- Node.js and npm
- VS Code with extension development tools
- Basic TypeScript/JavaScript knowledge
- Understanding of the target domain

## Examples

### Creating a Custom Agent Profile

Custom agent profiles are the recommended approach for most use cases. Create a file at `.github/agents/your-agent-name.md`:

```markdown
---
name: documentation-writer
description: Agent specializing in creating and improving technical documentation
---

You are a technical documentation specialist with expertise in creating clear, comprehensive, and user-friendly documentation. Your focus is on README files, API documentation, and technical guides.

## Documentation Standards

### README Files
- Start with a clear project description (what it does, why it exists)
- Include installation and setup instructions
- Provide usage examples with code snippets
- Document configuration options and environment variables
- Add contribution guidelines and license information

### API Documentation
- Document all public functions, classes, and methods
- Include parameter types, return values, and possible exceptions
- Provide practical usage examples
- Note any breaking changes or deprecations

### Technical Guides
- Structure content logically with clear headings
- Use consistent formatting and terminology
- Include troubleshooting sections
- Provide links to related documentation

## Writing Style
- Use clear, concise language accessible to developers at different skill levels
- Prefer active voice and imperative mood for instructions
- Include code examples that work out of the box
- Use relative links for repository files (e.g., `docs/CONTRIBUTING.md`)

Always ensure documentation is accurate, up-to-date, and follows the project's established patterns.
```

### Creating a Simple Code Review Extension

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  const command = vscode.commands.registerCommand('agentCodeReview.review', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showInformationMessage('No active editor');
      return;
    }

    // Get the code from the active editor
    const code = editor.document.getText();

    // Here you would integrate with an AI service
    const review = await performAIReview(code);

    // Display results in a new panel
    const panel = vscode.window.createWebviewPanel(
      'codeReview',
      'AI Code Review',
      vscode.ViewColumn.Beside,
      {}
    );

    panel.webview.html = generateReviewHTML(review);
  });

  context.subscriptions.push(command);
}

async function performAIReview(code: string) {
  // Placeholder for AI integration
  return {
    issues: ['Consider adding error handling'],
    suggestions: ['Use const instead of let where possible']
  };
}

function generateReviewHTML(review: any) {
  return `
    <!DOCTYPE html>
    <html>
    <head><title>Code Review</title></head>
    <body>
      <h2>AI Code Review Results</h2>
      <h3>Issues Found:</h3>
      <ul>
        ${review.issues.map((issue: string) => `<li>${issue}</li>`).join('')}
      </ul>
      <h3>Suggestions:</h3>
      <ul>
        ${review.suggestions.map((suggestion: string) => `<li>${suggestion}</li>`).join('')}
      </ul>
    </body>
    </html>
  `;
}
```

### MCP Server for File Operations

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'file-operations-agent',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {
      'read-file': {
        description: 'Read the contents of a file',
        inputSchema: {
          type: 'object',
          properties: {
            path: { type: 'string', description: 'File path to read' }
          },
          required: ['path']
        }
      },
      'list-directory': {
        description: 'List contents of a directory',
        inputSchema: {
          type: 'object',
          properties: {
            path: { type: 'string', description: 'Directory path to list' }
          },
          required: ['path']
        }
      }
    }
  }
});

server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'read-file':
      try {
        const content = await fs.readFile(args.path, 'utf-8');
        return {
          content: [{ type: 'text', text: content }]
        };
      } catch (error) {
        return {
          content: [{ type: 'text', text: `Error reading file: ${error.message}` }],
          isError: true
        };
      }

    case 'list-directory':
      try {
        const entries = await fs.readdir(args.path);
        return {
          content: [{ type: 'text', text: entries.join('\n') }]
        };
      } catch (error) {
        return {
          content: [{ type: 'text', text: `Error listing directory: ${error.message}` }],
          isError: true
        };
      }

    default:
      return {
        content: [{ type: 'text', text: `Unknown tool: ${name}` }],
        isError: true
      };
  }
});

const transport = new StdioServerTransport();
server.connect(transport).catch(console.error);
```

## Best Practices

### Extension Development
- Always handle activation failures gracefully
- Use proper TypeScript types for VS Code APIs
- Implement comprehensive error handling
- Test across different VS Code versions
- Follow the extension manifest guidelines

### MCP Server Development
- Validate all inputs and outputs
- Provide clear error messages
- Implement proper logging
- Handle connection timeouts
- Support tool cancellation

### Agent Design
- Keep agents focused on specific domains
- Provide clear user feedback
- Document limitations and assumptions
- Consider performance implications
- Implement security best practices

## Troubleshooting

### Extension Won't Activate
- Check `package.json` for correct `main` entry point
- Verify activation events are properly configured
- Check VS Code developer console for errors

### MCP Server Connection Issues
- Verify server configuration in VS Code settings
- Check server logs for startup errors
- Ensure MCP protocol version compatibility

### Agent Performance Problems
- Profile your code for bottlenecks
- Implement caching where appropriate
- Use async operations for long-running tasks
- Consider lazy loading for large resources

## Related Skills

- [Skill Creator](../skill-creator/README.md): For creating custom agent skills
- [Google Style Docs](../google-style-docs/README.md): For documenting your agents
- [Git Commit Messages](../git-commit-messages/README.md): For maintaining your agent codebase

## Resources

- [VS Code Extension API Documentation](https://code.visualstudio.com/api)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [VS Code Extension Samples](https://github.com/microsoft/vscode-extension-samples)
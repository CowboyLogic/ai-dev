# VS Code Git Commit Integration

This guide shows how to integrate the Git Commit Messages skill with VS Code for automatic commit message generation and validation.

## Method 1: VS Code Tasks Integration

Create a VS Code task that runs the commit message generator.

### Setup

1. **Create `.vscode/tasks.json`** in your workspace:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Generate Commit Message",
      "type": "shell",
      "command": "python",
      "args": [
        "${workspaceFolder}/.github/skills/git-commit-messages/commit-generator.py"
      ],
      "group": {
        "kind": "build",
        "isDefault": true
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared",
        "showReuseMessage": true,
        "clear": false
      },
      "problemMatcher": []
    }
  ]
}
```

2. **Add keyboard shortcut** in `keybindings.json`:

```json
{
  "key": "ctrl+shift+g",
  "command": "workbench.action.tasks.runTask",
  "args": "Generate Commit Message"
}
```

### Usage

1. Stage your changes: `git add .`
2. Press `Ctrl+Shift+G` or run Command Palette → "Tasks: Run Task" → "Generate Commit Message"
3. Copy the suggested message and use it: `git commit -m "suggested message"`

## Method 2: Git Hooks Integration

Automatically validate commit messages using git hooks.

### Setup

1. **Create `.git/hooks/commit-msg`**:

```bash
#!/bin/bash

# Git commit message validation hook
# Requires: pip install conventional-commits

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat $COMMIT_MSG_FILE)

# Basic validation
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .{1,50}$"; then
    echo "❌ Commit message doesn't follow conventional commit format"
    echo "Expected: type(scope): description (max 50 chars)"
    echo ""
    echo "💡 Tip: Run 'python .github/skills/git-commit-messages/commit-generator.py' for suggestions"
    exit 1
fi

# Check line length
if [ ${#COMMIT_MSG} -gt 72 ]; then
    echo "⚠️  Commit message body lines should be <= 72 characters"
fi

echo "✅ Commit message format validated"
```

2. **Make it executable**:

```bash
chmod +x .git/hooks/commit-msg
```

### Usage

The hook runs automatically on every commit. If validation fails, it shows helpful error messages and suggests using the generator.

## Method 3: VS Code Extension Integration

Create a custom VS Code extension that integrates the skill.

### Extension Structure

```
vscode-commit-helper/
├── package.json
├── src/
│   ├── extension.ts
│   └── commitGenerator.ts
├── .github/
│   └── skills/
│       └── git-commit-messages/
└── README.md
```

### package.json

```json
{
  "name": "commit-message-helper",
  "displayName": "Commit Message Helper",
  "description": "Generate conventional commit messages using AI skills",
  "version": "0.1.0",
  "engines": {
    "vscode": "^1.74.0"
  },
  "categories": ["Other"],
  "activationEvents": ["onCommand:commitHelper.generateMessage"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "commitHelper.generateMessage",
        "title": "Generate Commit Message"
      }
    ],
    "menus": {
      "scm/title": [
        {
          "command": "commitHelper.generateMessage",
          "group": "navigation",
          "when": "scmProvider == git"
        }
      ]
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./"
  },
  "devDependencies": {
    "@types/node": "16.x",
    "typescript": "^4.9.4"
  }
}
```

### extension.ts

```typescript
import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {
    const generateCommand = vscode.commands.registerCommand('commitHelper.generateMessage', async () => {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        const scriptPath = path.join(workspaceFolder.uri.fsPath, '.github', 'skills', 'git-commit-messages', 'commit-generator.py');

        try {
            const result = await runPythonScript(scriptPath, workspaceFolder.uri.fsPath);
            const message = await vscode.window.showInputBox({
                prompt: 'Suggested commit message',
                value: result,
                placeHolder: 'Enter your commit message'
            });

            if (message) {
                // Copy to clipboard
                await vscode.env.clipboard.writeText(`git commit -m "${message}"`);
                vscode.window.showInformationMessage('Commit command copied to clipboard!');
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to generate commit message: ${error}`);
        }
    });

    context.subscriptions.push(generateCommand);
}

function runPythonScript(scriptPath: string, cwd: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const python = spawn('python', [scriptPath], { cwd });

        let output = '';
        let errorOutput = '';

        python.stdout.on('data', (data) => {
            output += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        python.on('close', (code) => {
            if (code === 0) {
                // Extract the suggested commit message from output
                const lines = output.split('\n');
                const subjectLine = lines.find(line => line.includes(': ') && !line.includes('==='));
                resolve(subjectLine || 'feat: update code');
            } else {
                reject(errorOutput || 'Script failed');
            }
        });
    });
}

export function deactivate() {}
```

### Usage

1. Install the extension
2. Stage your changes
3. Click the commit message icon in the Source Control panel
4. Review and edit the suggested message
5. The commit command is copied to clipboard

## Method 4: Copilot Integration

Configure GitHub Copilot to use the skill automatically.

### Setup

1. **Create `.github/copilot-instructions/commit.md`**:

```markdown
---
name: commit
description: Generate conventional commit messages using project standards
model: claude-sonnet-4.5
temperature: 0.3
permissions:
  read: true
  write: false
  execute: true
---

# Commit Message Specialist

You are an expert at writing conventional commit messages following the project's standards defined in `.github/skills/git-commit-messages/SKILL.md`.

## Your Role

When asked to create commit messages, you will:
1. Analyze the staged changes
2. Determine the appropriate conventional commit type
3. Identify the scope if applicable
4. Write a clear, descriptive subject line (≤50 characters)
5. Add a detailed body when the changes are complex
6. Include issue references when mentioned

## Commit Types

Use these conventional commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style/formatting
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance
- `perf`: Performance
- `ci`: CI/CD
- `build`: Build system

## Message Format

```
type(scope): subject line (≤50 chars)

Detailed explanation of changes made.

- Bullet point for each major change
- Include technical details
- Reference related issues

Closes #123
```

## Examples

**Feature Addition:**
```
feat(auth): add OAuth2 login flow

Implement complete OAuth2 authorization code flow with
automatic token refresh and secure storage.

- Add OAuth2 provider configuration
- Implement PKCE for enhanced security
- Store tokens in secure HTTP-only cookies
- Add logout with token revocation

Closes #456
```

**Bug Fix:**
```
fix(validation): prevent XSS in user input

Sanitize HTML input to prevent cross-site scripting attacks.
Replace dangerous tags with safe alternatives and add
content security policy headers.

Fixes #789
```

## Important Rules

- Subject line: imperative mood, no ending punctuation
- Body: explain what and why, not how
- Keep subject ≤50 characters, body lines ≤72 characters
- Use bullet points for multi-part changes
- Reference issues with "Closes #123" or "Fixes #456"
```

2. **Configure VS Code settings** in `.vscode/settings.json`:

```json
{
  "github.copilot.instructions": [
    {
      "file": ".github/copilot-instructions/commit.md"
    }
  ]
}
```

### Usage

Ask Copilot directly:
```
@commit Generate a commit message for these authentication changes
@commit What would be a good commit message for this bug fix?
@commit Review this commit message: "fix login bug"
```

## Method 5: Integrated Development Workflow

Combine multiple methods for a complete workflow.

### Setup

1. **VS Code Tasks** for quick generation
2. **Git Hooks** for validation
3. **Copilot Integration** for interactive help
4. **Team Guidelines** in CONTRIBUTING.md

### Workflow

1. **Make Changes** - Develop your code
2. **Stage Changes** - `git add .` or selective staging
3. **Generate Message** - Use VS Code task or Copilot
4. **Review & Edit** - Ensure message follows standards
5. **Commit** - Git hook validates format
6. **Push** - Changes are ready for review

### Team Integration

Add to your `CONTRIBUTING.md`:

```markdown
## Commit Messages

This project uses conventional commit format. Follow these guidelines:

### Quick Start
1. Stage your changes: `git add .`
2. Generate message: `Ctrl+Shift+G` (VS Code) or ask @commit
3. Commit: `git commit -m "generated message"`

### Standards
- Use conventional commit types: feat, fix, docs, etc.
- Subject line ≤50 characters
- Body explains what and why
- Reference issues: Closes #123

### Tools
- **VS Code Extension**: Automatic message generation
- **Git Hooks**: Format validation
- **Copilot**: Interactive help (@commit)

See `.github/skills/git-commit-messages/` for complete guidelines.
```

## Troubleshooting

### Common Issues

**"Python not found"**
- Install Python 3.7+
- Add to PATH or use full path in tasks.json

**"Script permission denied"**
- Run: `chmod +x .git/hooks/commit-msg`
- Ensure Python script is executable

**"Copilot not using skill"**
- Check `.vscode/settings.json` configuration
- Ensure copilot-instructions file exists
- Restart VS Code

**"Extension not loading"**
- Check VS Code version compatibility
- Verify package.json activation events
- Check developer console for errors

### Performance Tips

- Cache analysis results for large repositories
- Use `--cached` flag for faster diff analysis
- Implement incremental analysis for frequent commits

### Advanced Configuration

**Custom Commit Types:**
```json
// .vscode/settings.json
{
  "commit-generator.customTypes": {
    "hotfix": "Critical production fix",
    "security": "Security-related changes"
  }
}
```

**Team-specific Rules:**
```json
{
  "commit-generator.teamRules": {
    "requireScope": true,
    "maxSubjectLength": 50,
    "requireIssueRefs": true
  }
}
```

This integration provides multiple levels of automation while maintaining flexibility for different team preferences and workflows.
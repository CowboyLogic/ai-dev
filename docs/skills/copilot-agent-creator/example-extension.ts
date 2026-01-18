import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  console.log('Code Review Agent is now active!');

  // Register the code review command
  const reviewCommand = vscode.commands.registerCommand('codeReviewAgent.review', async () => {
    const editor = vscode.window.activeTextEditor;

    if (!editor) {
      vscode.window.showInformationMessage('Please open a file to review');
      return;
    }

    // Show progress indicator
    await vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: 'Analyzing code...',
      cancellable: false
    }, async (progress) => {
      progress.report({ increment: 0, message: 'Reading file...' });

      const document = editor.document;
      const code = document.getText();
      const fileName = document.fileName;

      progress.report({ increment: 50, message: 'Running analysis...' });

      // Simulate AI analysis (replace with actual AI service call)
      const review = await analyzeCode(code, fileName);

      progress.report({ increment: 100, message: 'Generating report...' });

      // Display results
      displayReviewResults(review);
    });
  });

  // Register the quick fix command
  const quickFixCommand = vscode.commands.registerCommand('codeReviewAgent.quickFix', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    // Apply a simple quick fix (example: convert let to const)
    const selection = editor.selection;
    const text = editor.document.getText(selection);

    if (text.includes('let ')) {
      const newText = text.replace(/let /g, 'const ');
      editor.edit(editBuilder => {
        editBuilder.replace(selection, newText);
      });
      vscode.window.showInformationMessage('Applied quick fix: let → const');
    } else {
      vscode.window.showInformationMessage('No quick fixes available for selection');
    }
  });

  context.subscriptions.push(reviewCommand, quickFixCommand);
}

export function deactivate() {
  console.log('Code Review Agent deactivated');
}

async function analyzeCode(code: string, fileName: string): Promise<CodeReviewResult> {
  // This is a mock implementation
  // In a real agent, you would call an AI service here

  const issues: CodeIssue[] = [];
  const suggestions: string[] = [];

  // Simple analysis examples
  const lines = code.split('\n');

  lines.forEach((line, index) => {
    // Check for console.log statements
    if (line.includes('console.log') && !line.trim().startsWith('//')) {
      issues.push({
        line: index + 1,
        type: 'warning',
        message: 'console.log statement found - consider removing for production',
        code: line.trim()
      });
    }

    // Check for TODO comments
    if (line.includes('TODO') || line.includes('FIXME')) {
      suggestions.push(`Address TODO on line ${index + 1}: ${line.trim()}`);
    }

    // Check for unused variables (very basic check)
    if (line.includes('let ') && !code.includes(line.split('let ')[1].split(' ')[0])) {
      issues.push({
        line: index + 1,
        type: 'info',
        message: 'Potentially unused variable',
        code: line.trim()
      });
    }
  });

  // General suggestions
  if (!code.includes('try') && !code.includes('catch')) {
    suggestions.push('Consider adding error handling with try-catch blocks');
  }

  if (lines.length > 50) {
    suggestions.push('File is quite long - consider breaking into smaller functions');
  }

  return {
    fileName,
    totalLines: lines.length,
    issues,
    suggestions,
    score: Math.max(0, 10 - issues.length - Math.floor(suggestions.length / 2))
  };
}

function displayReviewResults(review: CodeReviewResult) {
  const panel = vscode.window.createWebviewPanel(
    'codeReviewResults',
    `Code Review: ${review.fileName}`,
    vscode.ViewColumn.Beside,
    { enableScripts: true }
  );

  panel.webview.html = getReviewHTML(review);
}

function getReviewHTML(review: CodeReviewResult): string {
  const issueRows = review.issues.map(issue => `
    <tr>
      <td>${issue.line}</td>
      <td><span class="issue-type ${issue.type}">${issue.type}</span></td>
      <td>${issue.message}</td>
      <td><code>${issue.code}</code></td>
    </tr>
  `).join('');

  const suggestionItems = review.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('');

  return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Code Review Results</title>
      <style>
        body { font-family: var(--vscode-font-family); margin: 20px; }
        .header { background: var(--vscode-editorWidget-background); padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .score { font-size: 24px; font-weight: bold; color: ${review.score >= 7 ? '#28a745' : review.score >= 4 ? '#ffc107' : '#dc3545'}; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid var(--vscode-panel-border); }
        th { background: var(--vscode-editorWidget-background); font-weight: bold; }
        .issue-type { padding: 2px 6px; border-radius: 3px; font-size: 0.8em; text-transform: uppercase; }
        .error { background: #dc3545; color: white; }
        .warning { background: #ffc107; color: black; }
        .info { background: #17a2b8; color: white; }
        code { background: var(--vscode-textCodeBlock-background); padding: 2px 4px; border-radius: 3px; }
        ul { background: var(--vscode-editorWidget-background); padding: 15px; border-radius: 5px; }
        li { margin-bottom: 5px; }
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Code Review Results</h1>
        <p><strong>File:</strong> ${review.fileName}</p>
        <p><strong>Total Lines:</strong> ${review.totalLines}</p>
        <p><strong>Code Quality Score:</strong> <span class="score">${review.score}/10</span></p>
      </div>

      ${review.issues.length > 0 ? `
        <h2>Issues Found (${review.issues.length})</h2>
        <table>
          <thead>
            <tr>
              <th>Line</th>
              <th>Type</th>
              <th>Message</th>
              <th>Code</th>
            </tr>
          </thead>
          <tbody>
            ${issueRows}
          </tbody>
        </table>
      ` : '<h2>No Issues Found</h2><p>Great job! Your code looks clean.</p>'}

      ${review.suggestions.length > 0 ? `
        <h2>Suggestions</h2>
        <ul>
          ${suggestionItems}
        </ul>
      ` : ''}
    </body>
    </html>
  `;
}

interface CodeIssue {
  line: number;
  type: 'error' | 'warning' | 'info';
  message: string;
  code: string;
}

interface CodeReviewResult {
  fileName: string;
  totalLines: number;
  issues: CodeIssue[];
  suggestions: string[];
  score: number;
}
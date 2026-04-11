# OpenCode — GitHub Integration

> Source: <https://opencode.ai/docs/github/>  
> Last updated: April 10, 2026

OpenCode integrates with GitHub Actions. Mention `/opencode` or `/oc` in a comment, and OpenCode executes tasks within your GitHub Actions runner.

---

## Features

- **Triage issues:** Ask OpenCode to look into and explain an issue
- **Fix and implement:** Ask OpenCode to fix an issue, create a branch, and open a PR
- **Secure:** Runs inside your GitHub runners

---

## Installation

```bash
opencode github install
```

This walks you through installing the GitHub app, creating the workflow, and setting up secrets.

### Manual Setup

**1. Install the GitHub app**

Go to [github.com/apps/opencode-agent](https://github.com/apps/opencode-agent) and install on the target repository.

**2. Add the workflow**

```yaml
# .github/workflows/opencode.yml
name: opencode

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  opencode:
    if: |
      contains(github.event.comment.body, '/oc') ||
      contains(github.event.comment.body, '/opencode')
    runs-on: ubuntu-latest
    permissions:
      id-token: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v6
        with:
          fetch-depth: 1
          persist-credentials: false

      - name: Run OpenCode
        uses: anomalyco/opencode/github@latest
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        with:
          model: anthropic/claude-sonnet-4-20250514
          # share: true
          # github_token: xxxx
```

**3. Store API keys in secrets**

In your org/project settings → Secrets and variables → Actions → add required API keys.

---

## Configuration

| Input | Description |
|-------|-------------|
| `model` | Required. Format: `provider/model` |
| `agent` | Agent to use (must be primary). Defaults to `default_agent` or `"build"` |
| `share` | Whether to share the session. Defaults to `true` for public repos |
| `prompt` | Optional custom prompt to override default behavior |
| `token` | Optional GitHub access token. By default uses the OpenCode app's installation token |

To use the runner's built-in `GITHUB_TOKEN` instead of the OpenCode app:

```yaml
permissions:
  id-token: write
  contents: write
  pull-requests: write
  issues: write
```

---

## Supported Events

| Event | Trigger | Notes |
|-------|---------|-------|
| `issue_comment` | Comment on an issue or PR | Mention `/opencode` or `/oc` |
| `pull_request_review_comment` | Comment on specific code lines | Receives file path, line numbers, diff context |
| `issues` | Issue opened/edited | Requires `prompt` input |
| `pull_request` | PR opened/updated | Auto-review trigger; defaults to reviewing the PR |
| `schedule` | Cron schedule | Requires `prompt` input |
| `workflow_dispatch` | Manual trigger | Requires `prompt` input |

### Schedule Example

```yaml
# .github/workflows/opencode-scheduled.yml
name: Scheduled OpenCode Task

on:
  schedule:
    - cron: "0 9 * * 1" # Every Monday at 9am UTC

jobs:
  opencode:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: write
      pull-requests: write
      issues: write
    steps:
      - uses: actions/checkout@v6
        with:
          persist-credentials: false
      - uses: anomalyco/opencode/github@latest
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        with:
          model: anthropic/claude-sonnet-4-20250514
          prompt: |
            Review the codebase for any TODO comments and create a summary.
            If you find issues worth addressing, open an issue to track them.
```

### Automatic PR Review

```yaml
# .github/workflows/opencode-review.yml
name: opencode-review

on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
      pull-requests: read
      issues: read
    steps:
      - uses: actions/checkout@v6
        with:
          persist-credentials: false
      - uses: anomalyco/opencode/github@latest
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          model: anthropic/claude-sonnet-4-20250514
          use_github_token: true
          prompt: |
            Review this pull request:
            - Check for code quality issues
            - Look for potential bugs
            - Suggest improvements
```

---

## Examples

```
# Explain an issue
/opencode explain this issue

# Fix an issue (creates branch + PR)
/opencode fix this

# Review a PR and make changes
Delete the attachment from S3 when the note is removed /oc

# Review specific code lines (comment in Files tab)
/oc add error handling here
```

When commenting on specific code lines, OpenCode automatically receives the file path, line numbers, diff context, and surrounding code.

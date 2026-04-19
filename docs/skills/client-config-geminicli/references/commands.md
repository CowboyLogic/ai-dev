# Custom Commands Reference

Custom commands are slash commands you define in TOML files.

## File locations

| Scope | Location | Priority |
|-------|----------|----------|
| Global | `~/.gemini/commands/*.toml` | Lower |
| Project | `.gemini/commands/*.toml` | Higher (overrides global) |

## Naming convention

File path → command name, using `:` for namespacing:

| File | Command |
|------|---------|
| `review.toml` | `/review` |
| `git/commit.toml` | `/git:commit` |
| `deploy/prod.toml` | `/deploy:prod` |

## File format

```toml
# Required
prompt = "Review this code for bugs, security issues, and style."

# Optional
description = "Perform a thorough code review"
```

Only `prompt` is required. `description` is shown in the command picker; if omitted, auto-generated from filename.

## Argument handling

**With `{{args}}` placeholder** — arguments replace the token:
```toml
prompt = "Review the following for security issues:\n\n{{args}}"
description = "Security review of provided code"
```

**Without `{{args}}`** — arguments are appended after two newlines:
```toml
prompt = "You are a senior TypeScript developer. Review for idiomatic patterns."
```
User runs `/ts-review some code here` → model sees both the instruction and the code.

## Dynamic content

**Shell execution** (`!{...}`) — run a command and inject output:
```toml
prompt = """
Here is the current git diff:
!{git diff --staged}

Review this diff for issues before committing.
"""
description = "Review staged changes"
```

The CLI prompts for confirmation before running shell commands. Inside `!{...}`, `{{args}}` is automatically shell-escaped.

**File injection** (`@{...}`) — embed file contents:
```toml
prompt = """
Review this file for issues:
@{{{args}}}
"""
description = "Review a file"
```

Supports multimodal content — images and PDFs are embedded directly.

## Reloading

After editing command files, run `/commands reload` to apply changes without restarting.

## Examples

**Standup summary:**
```toml
# ~/.gemini/commands/standup.toml
prompt = """
Based on recent git history, write a brief standup update:
!{git log --oneline --since="yesterday" --author="$(git config user.email)"}
"""
description = "Generate standup from recent commits"
```

**File explainer:**
```toml
# ~/.gemini/commands/explain.toml
prompt = "Explain this code clearly, including what it does and why:\n\n@{{{args}}}"
description = "Explain a file"
```

**Commit message:**
```toml
# ~/.gemini/commands/commit.toml
prompt = """
Write a conventional commit message for this diff:
!{git diff --staged}

Format: <type>(<scope>): <description>
Types: feat, fix, docs, style, refactor, test, chore
"""
description = "Generate a commit message for staged changes"
```

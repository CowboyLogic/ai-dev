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

## File format (TOML v1)

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

The CLI prompts for confirmation before running shell commands — it shows the exact resolved command (after `{{args}}` escaping) before executing, and reports stderr plus an exit-status line (e.g. `[Shell command exited with code 1]`) on failure. The content inside `!{...}` must have balanced braces; wrap unbalanced-brace commands (e.g. inline JSON) in an external script instead.

**File injection** (`@{...}`) — embed file or directory contents. Processed *before* `!{...}` and `{{args}}` substitution:
```toml
prompt = """
Review this file for issues:
@{{{args}}}
"""
description = "Review a file"
```

- `@{path/to/file}`: replaced by file content.
- `@{path/to/dir}`: traversed recursively; every file inserted (respects `.gitignore`/`.geminiignore`).
- Multimodal: images (PNG/JPEG), PDF, audio, and video files are encoded and injected as multimodal input; other binaries are skipped gracefully.
- Workspace-aware: searches cwd and other workspace directories; absolute paths allowed if within the workspace.
- Content inside `@{...}` (the path) must have balanced braces.

## Reloading and discovery

| Command | Description |
|---------|-------------|
| `/commands reload` | Re-scan `.toml` files after editing, without restarting |
| `/commands list` | List all discovered command files |

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

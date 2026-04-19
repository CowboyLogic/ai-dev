# Permissions Reference

## Structure in settings.json

```json
{
  "permissions": {
    "allow": [],
    "deny": [],
    "ask": [],
    "defaultMode": "default",
    "additionalDirectories": [],
    "disableBypassPermissionsMode": "disable",
    "skipDangerousModePermissionPrompt": true
  }
}
```

**Rule evaluation order**: deny → ask → allow. First match wins. Deny always beats allow.

---

## Rule syntax: `Tool` or `Tool(specifier)`

### Match all uses
```
Bash          → all bash commands
WebFetch      → all web fetches
Read          → all file reads
Edit          → all file edits
```

### Bash rules (glob wildcards)
```
Bash(npm run *)           → commands starting with "npm run "
Bash(git commit *)        → git commits
Bash(git * main)          → any git command ending with "main"
Bash(* --version)         → any --version check
Bash(npm run build)       → exact match only
```

> Space before `*` enforces word boundary: `Bash(ls *)` matches `ls -la` but NOT `lsof`
> `Bash(ls*)` matches both.

### Read / Edit rules (gitignore patterns)
```
Read(./.env)              → relative to cwd
Read(./secrets/**)        → recursive under secrets/
Read(~/Documents/*.pdf)   → home-relative
Read(//Users/alice/file)  → absolute (double-slash!)
Edit(/src/**/*.ts)        → project-root relative (single slash = project root)
```

> WARNING: `/path` = project-root relative, NOT absolute. Use `//path` for absolute.

### WebFetch rules
```
WebFetch(domain:github.com)       → all requests to github.com
WebFetch(domain:*.npmjs.org)      → subdomains
```

### MCP rules
```
mcp__puppeteer                    → all tools from puppeteer server
mcp__puppeteer__*                 → same (wildcard form)
mcp__puppeteer__puppeteer_navigate → specific tool
```

### Agent (subagent) rules
```
Agent(Explore)     → Explore subagent
Agent(Plan)        → Plan subagent
Agent(my-agent)    → custom named agent
```

---

## Permission modes (`defaultMode`)

| Mode | Behavior |
|------|----------|
| `default` | Prompts on first use of each tool |
| `acceptEdits` | Auto-accepts file edits + common fs commands (mkdir, touch, mv, cp) |
| `plan` | Read-only analysis, no file modification or command execution |
| `auto` | AI classifier decides; background safety checks (research preview) |
| `dontAsk` | Denies all tools unless pre-approved via rules |
| `bypassPermissions` | Skips all prompts (except .git, .claude, .vscode writes) — DANGEROUS |

---

## Common patterns

### Allow common dev commands
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(npm test *)",
      "Bash(npm install *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "WebSearch"
    ]
  }
}
```

### Protect sensitive files
```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(~/.ssh/**)",
      "Bash(curl *)",
      "Bash(wget *)"
    ]
  }
}
```

### Ask before risky operations
```json
{
  "permissions": {
    "ask": [
      "Bash(git push *)",
      "Bash(rm *)",
      "Bash(docker *)"
    ]
  }
}
```

### Compound command note
A rule like `Bash(safe-cmd *)` does NOT allow `safe-cmd && other-cmd`.
Claude Code matches each subcommand in a pipeline independently.

---

## additionalDirectories
Extend file access beyond the working directory:
```json
{
  "permissions": {
    "additionalDirectories": ["../shared-libs/", "~/my-configs/"]
  }
}
```
Note: this grants file access only; hooks/subagents are NOT loaded from these dirs.

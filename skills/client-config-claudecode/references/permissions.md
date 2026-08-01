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
Edit(/src/**/*.ts)        → anchored to the settings source (single slash)
```

> WARNING: `/path` anchors to the *settings source*, not the filesystem root — project settings → project root, user settings → `~/.claude/`, local settings → original cwd, `--settings <file>` → that file's directory. Use `//path` for absolute.

- `Edit` rules cover all built-in file-editing tools (Write, NotebookEdit, legacy MultiEdit included) — a path rule written for `Write(...)` etc. is accepted but never consulted (startup warning). Always write `Edit(path)`.
- `Read` rules similarly cover Grep/Glob/`@file` mentions/IDE selection context — write `Read(path)`, not `Glob(path)`.
- A `Read` deny rule also blocks `Edit` on the same path (including creating a new file there).
- Single-segment directory patterns (`src/**`) differ by rule type: as an **allow** rule it matches only `<anchor>/src`; as a **deny/ask** rule it matches `src` at *any* depth. Use `**/src/**` to force any-depth matching in an allow rule, or `/src/**` / `path/to/src/**` to force top-level-only in a deny rule.
- Symlinks: allow rules require both the symlink path and its resolved target to match (else prompts); deny rules block if *either* matches.

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

### PowerShell rules (same shape as Bash)
```
PowerShell(Get-ChildItem *)   → matches Get-ChildItem and its aliases (gci, ls, dir)
PowerShell(Remove-Item *)
```
Cmdlet aliases are canonicalized before matching; matching is case-insensitive. `|`, `;`, and (PS7+) `&&`/`||` split compound commands — each subcommand must match independently, same as Bash.

### Cd rules (controls `/cd`, not model-invocable)
```
Cd(~/code/*)        → ~/code/app only (single segment)
Cd(~/code/**)       → ~/code and everything under it
Cd(**/node_modules) → any node_modules dir at any depth
```
A bare `Cd` deny disables `/cd` entirely. Adding any `Cd` allow rule switches `/cd` to allowlist mode. With no `Cd` rules, `/cd` keeps default behavior (prompts to trust unfamiliar directories).

### Match by input parameter: `Tool(param:value)`
Deny/ask rules only (not allow) — matches a top-level scalar input field:
```
Agent(model:opus)             → Agent calls requesting the Opus tier
Agent(isolation:worktree)     → Agent calls requesting a git worktree
Bash(run_in_background:true)  → backgrounded Bash calls
```
One rule per parameter (can't combine `model` + `isolation` in one rule). `*` wildcard supported; omitted params never match. Can't target a tool's primary content field this way (`command`, `file_path`, `path`, `url`, etc.) — Claude Code ignores such a rule and warns at startup.

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

Even in `dontAsk`/`bypassPermissions`, these still force a prompt (or deny, in `dontAsk`): explicit `ask` rules, org-controlled connector tools set to `ask`, MCP tools marked `requiresUserInteraction`, and `rm -rf /` / `rm -rf ~` (circuit breaker, including via `$(...)`/backtick/`<(...)` substitution).

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
Claude Code matches each subcommand in a pipeline independently (separators: `&&`, `||`, `;`, `|`, `|&`, `&`, newline). Approving a compound command with "don't ask again" saves one rule per subcommand (up to 5), not one rule for the whole string.

### Wrapper stripping (Bash)
Before matching, Claude Code strips known-safe wrappers so `Bash(npm test *)` also matches `timeout 30 npm test`: `timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin`, zsh `noglob`, and bare `xargs` (no flags). Also strips a leading assignment of known-safe env vars for **allow** rules (`Bash(rm *)` deny still matches `FOO=bar rm -rf tmp/`). Not configurable. Runners like `npx`, `docker exec`, `devbox run` are NOT stripped — `Bash(devbox run *)` matches anything after `run`, including `devbox run rm -rf .`; write the full runner+command pair instead.

### Built-in read-only Bash commands (no prompt, any mode)
`ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, read-only `git` forms. Not configurable (add `ask`/`deny` to override). Still prompt when: an unquoted glob hits a write-capable flag (`find`, `sort`, `sed`, `git`), `docker`/`file` carry daemon/path-opening flags, a Windows UNC path appears, or the command is too long/unparseable (>10,000 chars always prompts). `cd` into the working dir or an additional directory is read-only too, except `cd`+`git` (new dir may run hooks) and `cd`+output-redirect (target dir unclear) — both still prompt.

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

---

## Managed-only settings (ignored outside managed-settings)
`allowAllClaudeAiMcps`, `allowedChannelPlugins`, `allowManagedHooksOnly`, `allowManagedMcpServersOnly`, `allowManagedPermissionRulesOnly`, `blockedMarketplaces`, `channelsEnabled`, `disableSideloadFlags`, `forceRemoteSettingsRefresh`, `pluginTrustMessage`, `sandbox.filesystem.allowManagedReadPathsOnly`, `sandbox.network.allowManagedDomainsOnly`, `strictKnownMarketplaces`, `strictPluginOnlyCustomization`, `wslInheritsWindowsSettings`. `disableBypassPermissionsMode` works from any scope but is typically placed here.

## Settings precedence (highest → lowest)
1. Managed settings (can't be overridden, including CLI args)
2. Command line arguments
3. Local project settings (`.claude/settings.local.json`)
4. Shared project settings (`.claude/settings.json`)
5. User settings (`~/.claude/settings.json`)

Deny always wins regardless of which scope set it — a user-level deny blocks a project-level allow and vice versa.

## Project allow rules require workspace trust
`permissions.allow` and `permissions.additionalDirectories` from a project's `.claude/settings.json` apply only after accepting the workspace-trust dialog for that repo (`deny`/`ask` apply immediately). `.claude/settings.local.json` is exempt from trust unless the repo could have supplied it (committed, or `.claude` is a symlink).

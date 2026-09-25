# Permissions Reference

Upstream: `https://code.claude.com/docs/en/permissions.md` and `https://code.claude.com/docs/en/permission-modes.md`.

## Structure in settings.json

```json
{
  "permissions": {
    "allow": [],
    "deny": [],
    "ask": [],
    "defaultMode": "default",
    "additionalDirectories": [],
    "blockReadsOutsideWorkingDirectories": false,
    "disableBypassPermissionsMode": "disable",
    "disableAutoMode": "disable"
  },
  "skipDangerousModePermissionPrompt": true,
  "skipAutoPermissionPrompt": true
}
```

**Rule evaluation order**: deny → ask → allow. First match in that order wins; specificity doesn't change it. A broad deny (`Bash(aws *)`) beats a narrower allow (`Bash(aws s3 ls)`), and a matching ask prompts even if a more specific allow also matches.

A **bare tool name** in `deny` (e.g. `Bash`, or the equivalent `Bash(*)`) removes the tool from Claude's context entirely; a scoped rule (`Bash(rm *)`) keeps the tool and blocks matching calls.

| Key | Notes |
| --- | --- |
| `permissions.blockReadsOutsideWorkingDirectories` | Read/Grep/Glob/LSP refuse paths outside the working directories in every mode, incl. `bypassPermissions`; recognized Bash file readers (`cat` etc.) prompt. `true` from any source applies (v2.1.257+) |
| `permissions.disableBypassPermissionsMode` | `"disable"` — rejects `--dangerously-skip-permissions` and ignores subagent `permissionMode: bypassPermissions` |
| `permissions.disableAutoMode` | `"disable"` — same as top-level `disableAutoMode` |
| `skipDangerousModePermissionPrompt` | *(User, local, or managed; top-level key)* Skip the bypass-mode confirmation dialog; Claude Code writes `true` when you accept it once |
| `skipAutoPermissionPrompt` | *(User or managed; top-level key)* Skip the one-time auto mode notice |

---

## Rule syntax: `Tool` or `Tool(specifier)`

Parentheses inside the specifier are literal — no escaping needed.

### Match all uses

```text
Bash          → all bash commands (Bash(*) is equivalent)
WebFetch      → all web fetches
Read          → all file reads
Edit          → all file edits
```

### Bash rules (wildcards)

```text
Bash(npm run *)           → commands starting with "npm run " (also bare "npm run")
Bash(git commit *)        → git commits
Bash(git log * main)      → git log ... main
Bash(* --version)         → any program's --version
Bash(npm run build)       → exact match only
Bash(ls:*)                → same as Bash(ls *) — ":*" only valid at the end
```

- The space before `*` enforces a word boundary: `Bash(ls *)` matches `ls -la` and `ls` but NOT `lsof`; `Bash(ls*)` matches both.
- Put the `*` **after the subcommand**. Everything before the first `*` is what limits the rule. An allow rule with `*` before the subcommand, such as `Bash(git * main)`, produces a startup warning (it also matches `git push origin main` and `git -c core.fsmonitor=<script> diff main`).
- A trailing space-plus-`*` matches the bare command only when it is the rule's only wildcard: `Bash(* --help *)` matches `npm --help x` but not `npm --help`.

### Read / Edit rules (gitignore patterns)

```text
Read(./.env)              → relative to cwd
Read(.env)                → any .env at or under cwd (bare filenames match at any depth)
Read(./secrets/**)        → recursive under secrets/
Read(~/Documents/*.pdf)   → home-relative
Read(//Users/alice/file)  → absolute (double-slash!)
Edit(/src/**/*.ts)        → anchored to the settings source (single slash)
```

> [!WARNING]
> `/path` anchors to the *settings source*, not the filesystem root: project and local settings → primary working directory; user settings → `~/.claude/`; `--settings <file>` → that file's directory; CLI flags/session rules → primary working directory. Use `//path` for absolute, `~/` for home.

- `Edit` rules cover all built-in file-editing tools. A path rule written for `Write`, `NotebookEdit`, `Glob`, or legacy `MultiEdit` is accepted but never consulted (startup warning). Always write `Edit(path)` / `Read(path)`. A bare tool-name rule such as a `Write` deny still applies at the tool level.
- `Read` rules are applied best-effort to Grep/Glob, `@file` mentions, and IDE selection context.
- A `Read` deny rule also blocks Edit/Write on the same path (including creating a file). NotebookEdit isn't covered — add an `Edit` deny too.
- Read/Edit deny rules also apply to recognized Bash file commands (`cat`, `head`, `tail`, `sed`, `tee`) and redirect targets, but NOT to commands that read without naming the file (`grep -r pattern .`) or scripts that open files themselves. Use the sandbox for OS-level enforcement.
- Single-segment directory patterns (`src/**`): as an **allow** rule it matches only `<cwd>/src`; as a **deny/ask** rule it matches `src` at *any* depth. Use `**/src/**` for any depth, `/src/**` for top-level only.
- `!` negation (deny/ask only): `Read(*.env)` then `Read(!sample.env)` in the same file's list carves out `sample.env`. Only reaches rules from the same source and listed before it.
- Symlinks: allow rules require both the symlink path and its target to match (else prompts); deny rules block if *either* matches.
- Windows paths are normalized to POSIX: `C:\Users\alice` → `/c/Users/alice`, so `//c/**/.env`.

### WebFetch rules

```text
WebFetch(domain:github.com)       → requests to github.com
WebFetch(domain:*.npmjs.org)      → subdomains at any depth (not npmjs.org itself)
WebFetch(domain:*)                → every domain (domain: rules also feed the sandbox allowed/denied domain list)
```

A bare `WebFetch` allow fetches freely without changing the sandbox network allowlist; `WebFetch(domain:*)` also lets sandboxed commands reach any host. A bare `WebFetch` deny removes the tool; `WebFetch(domain:*)` deny keeps it and refuses every fetch. Wildcards need v2.1.172+.

### MCP rules

```text
mcp__puppeteer                     → all tools from puppeteer server
mcp__puppeteer__*                  → same (wildcard form)
mcp__puppeteer__puppeteer_navigate → specific tool
mcp__claude_ai_<server>__<tool>    → claude.ai connector tools
```

An `mcp__` rule with parentheses (parameter match) is skipped when loaded from a settings file — use `--disallowedTools` for that.

### Tool-name wildcards

Deny/ask rules accept globs in the tool-name position: `"*"` (every tool), `"mcp__*"` (every MCP tool). Allow rules accept tool-name globs only after a literal `mcp__<server>__` prefix (e.g. `mcp__github__get_*`); `"*"`, `"B*"`, or `"mcp__*"` as an allow rule is skipped with a warning. Use canonical tool names (e.g. `TaskStop`, not the label "Stop Task").

### Agent (subagent) rules

```text
Agent(Explore)     → Explore subagent
Agent(Plan)        → Plan subagent
Agent(my-agent)    → custom named agent
```

### Skill rules

```text
Skill(commit)        → exact skill name
Skill(review-pr *)   → prefix match with any arguments
```

A deny rule naming an alias or unqualified name still blocks the skill (e.g. `Skill(deploy)` blocks nested `apps/web:deploy`); an allow rule matches only the skill's own name and the name in Claude's invocation. Source: `https://code.claude.com/docs/en/skills.md`.

### PowerShell rules (same shape as Bash)

```text
PowerShell(Get-ChildItem *)   → also matches aliases gci, ls, dir
PowerShell(Remove-Item *)
```

Aliases are canonicalized; matching is case-insensitive. `|`, `;`, and (PS7+) `&&`/`||` split compound commands — every subcommand must match.

### Cd rules (controls `/cd`, not model-invocable)

```text
Cd(~/code/*)        → ~/code/app only (single segment)
Cd(~/code/**)       → ~/code and everything under it
Cd(**/node_modules) → any node_modules dir at any depth
```

A bare `Cd` deny disables `/cd`. Any `Cd` allow rule switches `/cd` to allowlist mode. With no `Cd` rules, `/cd` prompts to trust unfamiliar directories.

### Match by input parameter: `Tool(param:value)`

Deny/ask rules only (not allow), built-in tools only — matches a top-level scalar input field:

```text
Agent(model:opus)             → Agent calls requesting the Opus tier (alias, not full ID)
Agent(isolation:worktree)     → Agent calls requesting a git worktree
Bash(run_in_background:true)  → backgrounded Bash calls
```

One parameter per rule; `*` wildcard supported; omitted params never match. A tool's primary content field (`command`, `file_path`, `path`, `notebook_path`, `url`) can't be matched this way — the rule is ignored with a startup warning.

---

## Permission modes (`defaultMode`)

| Mode | Behavior |
| --- | --- |
| `default` | Prompts on first use of each tool. Labeled **Manual**; `"manual"` is accepted as an alias (v2.1.200+) |
| `acceptEdits` | Auto-accepts file edits + common fs commands (`mkdir`, `touch`, `mv`, `cp`) in working/additional dirs |
| `plan` | Reads and runs read-only commands; no source edits until you approve a plan |
| `auto` | Auto-approves with background classifier safety checks |
| `dontAsk` | Auto-denies anything that would prompt; reads and pre-approved tools still run. `AskUserQuestion` and `requiresUserInteraction` MCP tools are denied |
| `bypassPermissions` | Skips prompts, including writes to protected paths like `.git` and `.claude` — DANGEROUS, isolated environments only |

- `auto` and `bypassPermissions` do NOT take effect as `defaultMode` from project or local settings (v2.1.257+) — set them in `~/.claude/settings.json`.
- `--permission-mode` / `--dangerously-skip-permissions` override `defaultMode` for one session.
- In cloud sessions only `acceptEdits`, `plan`, `default`, and `auto` are honored.

**Actions no mode auto-approves** (even `bypassPermissions`): explicit `ask` rules; org connector tools set to `ask`; `AskUserQuestion` and MCP tools marked `requiresUserInteraction`; `rm`/`rmdir` targeting a critical path (circuit breaker — no allow rule or hook `"allow"` approves it; `dontAsk` denies it, `auto` sends it to the classifier); cross-session messaging safeguards; reads outside working dirs while `blockReadsOutsideWorkingDirectories` is on.

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

### Compound commands

A rule like `Bash(safe-cmd *)` does NOT allow `safe-cmd && other-cmd`. Separators: `&&`, `||`, `;`, `|`, `|&`, `&`, newline — each subcommand must match an allow rule. Deny/ask rules match any subcommand, including inside `$(...)`, subshells, and loop bodies. A dangling `&&`/`||` makes the command unparseable (no allow match). "Don't ask again" on a compound command saves one rule per subcommand (up to 5).

### What a Bash rule doesn't match

Rules match command text, not the program. `Bash(git push *)` in deny does NOT stop `git -C . push`, `/usr/bin/git push`, or `sh -c 'git push'`. For real boundaries use the sandbox or a PreToolUse hook.

### Wrapper stripping (Bash)

Stripped before matching (not configurable): `timeout`, `time`, `nice`, `nohup`, `stdbuf`, `command`, `builtin`, zsh `noglob`, and bare `xargs` (no flags). Not stripped: `command -v`, zsh `nocorrect`. A leading assignment of known-safe env vars is stripped for **allow** rules; deny/ask rules match past any leading assignment. Runners (`npx`, `docker exec`, `devbox run`, `direnv exec`, `mise exec`) are NOT stripped — write the full runner+command pair. Exec wrappers (`watch`, `setsid`, `ionice`, `flock`) and `find -exec`/`-delete` can't be approved by a prefix rule; use an exact-match rule.

### Redirections

Output redirects (`>`, `>>`, `2>`) and `tee` targets are checked against `Edit` rules, protected paths, and working dirs (`tee` v2.1.269+). Input redirects (`<`) are checked against `Read` rules (v2.1.257+). `/dev/null`, `2>&1`, here-docs are exempt.

### Built-in read-only Bash commands (no prompt, any mode)

`ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, read-only `git` forms. Not configurable (add `ask`/`deny` to override). Still prompt when: an unquoted glob hits a write/exec-capable command (`find`, `sort`, `sed`, `git`), `docker` targets another daemon, `file` uses `-m`/`-f`, a Windows UNC path appears, or the command can't be parsed (>10,000 chars always prompts). `cd` into a working/additional dir is read-only, except `cd`+`git` into a different dir and `cd`+redirect with an unclear target.

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

Settings-file `additionalDirectories` grant file access only — no skills, agents, commands, settings, or CLAUDE.md load from them. Directories added with `--add-dir` / `/add-dir` additionally load skills, commands, subagents, and `enabledPlugins`/`extraKnownMarketplaces`.

---

## Managed-only settings (ignored outside managed sources)

`allowAllClaudeAiMcps`, `allowedChannelPlugins`, `allowManagedHooksOnly`, `allowManagedMcpServersOnly`, `allowManagedPermissionRulesOnly`, `blockedMarketplaces`, `channelsEnabled`, `disableCommandPluginSources`, `disableSideloadFlags`, `forceRemoteSettingsRefresh`, `managedMcpServers`, `managedSourcesBehavior`, `parentSettingsBehavior`, `pluginSuggestionMarketplaces`, `pluginTrustMessage`, `policyHelper`, `sandbox.filesystem.allowManagedReadPathsOnly`, `sandbox.network.allowManagedDomainsOnly`, `strictKnownMarketplaces`, `strictPluginOnlyCustomization`, `wslInheritsWindowsSettings`. Also managed-only: `forceLoginGatewayUrl`, `gatewayInternalNetworks`, `requiredMinimumVersion`/`requiredMaximumVersion`, browser/mobile-simulator controls, `sshHostAllowlist`, `disableDesktopLocalSessions`, `sandbox.bwrapPath`/`socatPath`, `modelPricing`, `claudeMd`.

`disableBypassPermissionsMode` works from any scope but is typically placed in managed settings.

## Settings precedence (highest → lowest)

1. Managed settings (can't be overridden, including by CLI args)
2. Command line arguments
3. Local project settings (`.claude/settings.local.json`)
4. Shared project settings (`.claude/settings.json`)
5. User settings (`~/.claude/settings.json`)

Deny always wins regardless of scope — a user-level deny blocks a project-level allow and vice versa. `--disallowedTools` can add restrictions beyond managed settings; `--allowedTools` can't override a managed deny.

"Yes, and don't ask again" saves the rule to `.claude/settings.local.json` at the git repo root (v2.1.211+), so it applies across subdirectories and worktrees.

## Project allow rules require workspace trust

`permissions.allow` and `permissions.additionalDirectories` from a project's `.claude/settings.json` apply only after accepting the workspace-trust dialog (`deny`/`ask` apply immediately). `.claude/settings.local.json` is exempt from trust unless it's tracked in git or `.claude` is a symlink. `claude -p` / SDK sessions never show the dialog and don't apply untrusted project allow rules.

## Hooks and permissions

PreToolUse hooks run before the permission prompt. A hook `"allow"` does not bypass matching deny/ask rules. A hook exiting 2 blocks even when an allow rule would permit the call.

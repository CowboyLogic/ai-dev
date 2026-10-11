# Permissions Reference

Covers trusted directories, tool/path/URL permissions, permission patterns, saved approvals
(`permissions-config.json`), permission modes, sandboxing, and managed permission policy.

## Where permission state lives

| What | Where | Lifetime |
|------|-------|----------|
| Trusted directories | `trustedFolders` in `~/.copilot/config.json` | Permanent |
| Tool approvals "for this location" | `~/.copilot/permissions-config.json` | Per repo/directory, permanent |
| Extra allowed directories for a location | `allowed_directories` in `permissions-config.json` | Per location, permanent |
| Permanently approved URLs | `allowedUrls` in `~/.copilot/settings.json` | All sessions |
| Always-denied URLs | `deniedUrls` in `settings.json` (user or repo) | All sessions |
| `--allow-tool`, `--deny-tool`, etc. | Command line | Current session only |
| "Allow for session" prompt answers | Memory | Current session only |

Deny rules always take precedence over allow rules — even with `--allow-all` or a saved approval.

---

## Trusted directories

At startup you confirm trust for the launch directory: this session only, or this and future
sessions (written to `trustedFolders` in `config.json`). Edit that array to add or remove
permanent trust. Trust also gates project MCP servers, hooks, skills, plugins, and repository
model/effort overrides. Scoping is heuristic — avoid launching from `$HOME` or directories with
untrusted executables.

`--add-dir=PATH` / `/add-dir PATH` grants file access to another directory **and** loads its
`.github/skills` and `.github/agents` as trusted configuration. `/list-dirs` shows granted
directories.

---

## Command-line permission flags

### Tools

| Flag | Effect |
|------|--------|
| `--allow-all-tools` | Skip approval for every tool (required for `-p` automation; env `COPILOT_ALLOW_ALL`) |
| `--allow-tool=PATTERN` | Pre-approve matching tools (quoted, comma-separated list for many) |
| `--deny-tool=PATTERN` | Block matching tools; beats every allow |
| `--available-tools=LIST` | Only these tools exist for the model (allowlist) |
| `--excluded-tools=LIST` | Remove these tools from the model (denylist); ignored if `--available-tools` is set |

`--available-tools`/`--excluded-tools` control what the model can *see*; `--allow-tool`/`--deny-tool`
control whether it is *prompted*. A tool outside the available set can't be used even if allowed.

### Paths

| Flag | Effect |
|------|--------|
| (default) | cwd, its subdirectories, and the system temp directory |
| `--allow-all-paths` | Disable path verification |
| `--disallow-temp-dir` | Remove automatic temp-dir access |
| `--add-dir=PATH` | Grant an additional directory (repeatable) |

Path checks apply to shell commands, file tools, and search tools. For shell commands paths are
extracted heuristically: complex constructs may be missed, only `HOME`, `TMPDIR`, `PWD` and
similar variables are expanded, and symlinks resolve only for existing files.

### URLs

| Flag | Effect |
|------|--------|
| (default) | Every URL requires approval |
| `--allow-all-urls` | Skip URL verification |
| `--allow-url=DOMAIN` | Pre-approve a domain |
| `--deny-url=DOMAIN` | Block a domain; beats `--allow-url` |

URL checks apply to `web_fetch` and a curated set of network shell commands (`curl`, `wget`,
`fetch`, ...). HTTP and HTTPS are approved separately. URLs inside files, config, env vars, or
obfuscated strings are not detected.

### Master override

```bash
copilot --allow-all   # = --allow-all-tools --allow-all-paths --allow-all-urls
copilot --yolo        # alias for --allow-all
```

Never put an allow-all flag in a shell alias — use it only in isolated environments.

---

## Permission patterns (`--allow-tool` / `--deny-tool`)

Format `Kind(argument)`; the argument is optional (omitting it matches every tool of that kind).

| Kind | Matches | Examples |
|------|---------|----------|
| `shell` | Shell commands | `shell`, `shell(git push)`, `shell(git:*)` |
| `write` | File creation/modification (non-shell) | `write`, `write(src/*.ts)` |
| `read` | File or directory reads | `read`, `read(.env)` |
| `url` | URL access via `web_fetch` or shell | `url(github.com)`, `url(https://*.api.com)` |
| `memory` | Storing facts to agent memory | `memory` |
| `SERVER-NAME` | MCP server tools | `MyMCP`, `MyMCP(create_issue)` |

- `shell(git:*)` matches `git` followed by a space and more text — `git push`, `git pull`, but not
  `gitea`.
- For `git` and `gh`, specify a first-level subcommand: `shell(git push)`.
- `--deny-tool='write(secret.txt)'` denies that path only (exact or trailing-segment match; no
  globs yet; symlinks and `.`/`..` resolved; case-insensitive on macOS/Windows).
- Use the raw MCP server name (see `/mcp`).

```bash
# All git except push
copilot --allow-tool='shell(git:*)' --deny-tool='shell(git push)'

# Everything except rm and git push
copilot --allow-all-tools --deny-tool='shell(rm)' --deny-tool='shell(git push)'

# All reads, and writes to one file
copilot --allow-tool='read, write(.github/copilot-instructions.md)'

# Restricted session: explore, edit, commit — no internet, no subagents, no push
copilot --available-tools='bash,edit,view,grep,glob' \
  --allow-tool='shell(git:*)' --deny-tool='shell(git push)'
```

### Tool names (for `--available-tools` / `--excluded-tools`)

| Group | Tool names |
|-------|------------|
| Shell | `bash`/`powershell`, `list_bash`/`list_powershell`, `read_bash`/`read_powershell`, `stop_bash`/`stop_powershell`, `write_bash`/`write_powershell` |
| Files | `apply_patch`, `create`, `edit`, `view` |
| Agents | `list_agents`, `read_agent`, `task`, `write_agent` |
| Other | `ask_user`, `glob`, `grep` (or `rg`), `skill`, `web_fetch` |

---

## Approval prompts

Keys: `y` allow once, `n` deny once, `!` allow similar for the session, `#` deny similar for the
session, `?` details.

Full dialog options:

| Option | Persistence |
|--------|-------------|
| Once | None |
| This location | Saved to `permissions-config.json` for the Git root or cwd |
| Always | Config file |

Approving a tool "for the rest of the session" allows it in any form (approving `rm ./file` allows
`rm -rf ./*`).

Per the v1.0.90 release notes, path access prompts can also grant a session-scoped read-only
directory approval (not covered in the docs reference).

### Permission modes and resets

| Command | Effect |
|---------|--------|
| `/permissions default\|assisted\|allow-all\|show` | Switch or show mode. `assisted` attaches an LLM safety recommendation and can auto-approve acceptable requests |
| `/allow-all [off\|auto\|show]`, `/yolo` | Aliases for `/permissions allow-all` |
| `/permissions reset` | Clear in-memory approvals for this session |
| `/reset-allowed-tools` | Revert to startup flags **and** clear saved approvals for this location in `permissions-config.json` |

---

## permissions-config.json

Saved "this location" approvals. Resolved from `--config-dir` (legacy), then `COPILOT_HOME`, then
`~/.copilot/` — only the first applicable directory is used. An extensionless legacy
`permissions-config` file is still honored if the `.json` file is absent. Don't edit while a
session is running; entries for paths that no longer exist are removed automatically.

**Location keys** (`locations` object) are absolute paths: the Git root (linked worktrees resolve
to the main repo root; submodules use their own directory) or the normalized cwd outside Git.

```json
{
  "locations": {
    "/Users/YOUR-USER/src/my-repo": {
      "tool_approvals": [
        { "kind": "commands", "commandIdentifiers": ["git:*", "npm test"] },
        { "kind": "write" },
        { "kind": "mcp", "serverName": "github-mcp-server", "toolName": null }
      ],
      "allowed_directories": ["/Users/YOUR-USER/src/shared-docs"]
    }
  }
}
```

| `kind` | Required fields | Meaning |
|--------|-----------------|---------|
| `commands` | `commandIdentifiers` | Shell command identifiers |
| `read` | — | Read requests (usually unnecessary; interactive reads are auto-approved) |
| `write` | — | File create/modify (path prompts still apply outside allowed dirs) |
| `mcp` | `serverName`, `toolName` | One MCP tool, or every tool when `toolName` is `null` |
| `mcp-sampling` | `serverName` | MCP sampling for one server |
| `memory` | — | Memory write and vote |
| `custom-tool` | `toolName` | Custom tool by exact name |
| `extension-management` | optional `operation` | Extension management (all ops if omitted) |
| `extension-permission-access` | `extensionName` | Extension access to permission-gated capabilities |

- Matching is literal — no regex or globs. Only a trailing `:*` in `commandIdentifiers` is special
  (`git:*` matches `git`, `git status`; not `gitea`). `git*` does **not** match `git status`.
- `allowed_directories` entries must be absolute, existing directories; they skip the path prompt
  but don't approve the operation itself.
- Not supported here: deny rules, ask rules, default modes, URL rules, tool filtering, or shared
  repo policy. Unknown fields may be dropped on the next write.

---

## Sandboxing

Restricts filesystem, network, and credential access for shell commands (and, by default, MCP and
LSP servers) even under `--allow-all`. The v1.0.93 release notes state that command sandboxing is
available to all users via `/sandbox` and `--sandbox`.

| Mechanism | How |
|-----------|-----|
| Local sandbox | `/sandbox enable`, the `/sandbox` dialog, `sandbox.enabled: true`, or `--sandbox` (this session only; useful with `-p`). `--no-sandbox` disables it for this session only and is ignored when managed policy enforces sandboxing |
| Cloud sandbox | `copilot --cloud --experimental` — an interactive session in a GitHub-hosted, isolated environment. Documented as public preview and experimental; org/enterprise access is off by default |

Backends (via Microsoft eXecution Container): Seatbelt (macOS), Bubblewrap (Linux), ProcessContainer
(Windows). Linux needs Bubblewrap 0.5.0+ and `slirp4netns` on `PATH`; macOS 15 or later is the
tested baseline; Windows needs Windows 11 25H2 with KB5124010 or later, or 26H1 with KB5124006 or
later, with the BaseContainer tier of ProcessContainer. On an unsupported
host a saved preference is turned off for the session with a notice, and `/sandbox enable` is
refused.

`/sandbox` subcommands: `config` (or bare `/sandbox`, opens the General / Credentials / Filesystem /
Network dialog), `status`, `policy [COMMAND]` (effective policy with grant sources; a command shows
its dev-tool access without running it), `enable`, `disable`, and `ca [create|trust|rotate|remove]`
for the proxy certificate authority. Outside a session: `copilot sandbox ca
status|create|trust|rotate|remove`. Run `copilot help sandbox` for the full reference.

### Defaults and bypass

- Read/write to the working directory; in a Git repo also read/write to `.git` and read access to
  the rest of the repository. "Allow dev tool access" (default on) adds read access to toolchain
  directories and some shared caches.
- **Allow sandbox bypass** (default on): when a command is blocked, the CLI prompts to re-run it
  outside the sandbox. Approval covers that attempt; the prompt can also disable sandboxing for the
  rest of the session. A bypass removes only Copilot's sandbox limits, not your OS permissions.
  Detached (backgrounded) commands can't be sandboxed and prompt before they start.
- Sandbox settings are user-level or enterprise-managed. Repository settings files can't set them.
- Per the v1.0.92 release notes, sandboxed shells withhold an ambient `GITHUB_TOKEN` unless it is
  explicitly configured.

### User sandbox settings (`settings.json`)

| Key | Default | Purpose |
|-----|---------|---------|
| `sandbox.enabled` | `false` | Sandbox shell, MCP/LSP servers, and built-in file and web tools |
| `sandbox.allowBypass` | `true` | Allow prompting to re-run a blocked command outside the sandbox |
| `sandbox.auth.git` / `sandbox.auth.gh` | `true` | Provide Git / `gh` credentials inside the sandbox (renamed from `sandbox.gitAuth` / `sandbox.ghAuth`; old keys are ignored) |
| `sandbox.credentials.envVars` | unset | Mask environment variables: `{ "NAME": { "injectHosts": ["api.example.com"] } }`. Processes get placeholders; the local proxy supplies the real value only in HTTPS headers to those hosts. Needs sandboxing on; the variable must be non-empty in the launching environment and must not be listed in `--secret-env-vars` |
| `sandbox.userPolicy.network.allowLocalNetwork` | `false` | Local network access; effect varies by OS. Windows proxying and host rules require `true` |
| `sandbox.userPolicy.network.allowedHosts` | `[]` | Hostnames, IPs, `*.example.com` (subdomains only), or `*`; no CIDR, URLs, or ports. A non-empty list blocks unmatched hosts (localhost and loopback are added automatically when outbound and local network are both on) |
| `sandbox.userPolicy.network.blockedHosts` | `[]` | Always beats `allowedHosts`; denying a domain denies its subdomains |
| `sandbox.userPolicy.network.proxy` | unset | `url` (no embedded credentials), optional `username`/`password`. Literal passwords use the OS credential store when available (local file fallback); a whole-field `${VAR}`/`$VAR` env reference is allowed. Host rules and the proxy are inactive when outbound access is off |
| `sandbox.userPolicy.filesystem.deniedPaths` | `[]` | Denied paths. If the host can't enforce them (older Windows), the command fails rather than running with weaker protection |
| `sandbox.userPolicy.seatbelt.keychainAccess` | `false` | macOS only; `settings.json` only (not in `/sandbox` or `/settings`) |

Managed policy can force sandboxing on as a floor that users can only tighten. With the managed
`sandbox.failIfUnavailable: true` (plus `sandbox.enabled: true`) the CLI blocks model and tool
execution when the sandbox can't be established. If a managed floor permits bypass, `/sandbox
disable` turns sandboxing off for the current session only.

---

## Restricting allow-all

`permissions.disableBypassPermissionsMode` (user settings, server-managed, or MDM):

- `"disable"` — suppresses `--allow-all-tools`, `--allow-all-paths`, `--allow-all-urls`,
  `--allow-all`, `--yolo`, and `/permissions allow-all` (`/allow-all`, `/yolo`).
- `"allow-auto-only"` — blocks full allow-all but permits assisted approval.
- Unrecognized values fail closed to `"disable"`.
- The v1.0.94 release notes add that managed policy can disable Assisted Permissions and keep
  sessions in Manual Approval mode, and that a policy warning is shown when startup bypass flags
  are suppressed by managed settings.

## Managed permission rules (administrators)

MDM/server managed `permissions` may contain `deny`, `ask`, and `allow` arrays:

```json
{
  "permissions": {
    "deny": ["Shell(rm -rf *)", "Domain(*.evil.example)"],
    "ask": ["Shell(git push *)"],
    "allow": ["Read(**)"]
  }
}
```

Rule families: `Bash(...)`/`Shell(...)`, `PowerShell(...)`, `Read(...)`, `Edit(...)`/`Write(...)`
(also cover shell redirections and `sed -i`), `Domain(...)`. Deny beats ask beats allow; when any
list is set, unmatched operations default to ask.

### Domain boundary (`limitTo`)

A managed `permissions.limitTo` array of `Domain(...)` entries is a closed-world allowlist for
agent network requests:

```json
{ "permissions": { "limitTo": ["github.com", "*.github.com"] } }
```

- Requests to domains outside the list are denied without prompting; user rules, saved approvals,
  and allow-all modes can't widen it. URLs found in shell commands count as `Domain` requests.
- It doesn't restrict `shell`, `read`, or `write` by itself. `deny` still wins; `ask`/`allow` only
  refine requests already inside the boundary.
- An empty list denies every domain request; an invalid list or entry is enforced as empty. Across
  managed sources it is an intersection.

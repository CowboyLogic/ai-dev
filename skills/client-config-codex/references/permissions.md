# Permissions Reference

Covers `sandbox_mode`, `approval_policy`, `approvals_reviewer` (auto-review), workspace-write
options, network access, protected paths, permission profiles (beta), Rules files, project trust,
and platform sandboxes.

## Two controls, two questions

| Control | Question it answers | Keys |
|---------|---------------------|------|
| Sandbox | What can commands technically touch (files, network)? | `sandbox_mode`, `[sandbox_workspace_write]`, or permission profiles |
| Approval | When must Codex stop and ask before crossing the sandbox? | `approval_policy`, `approvals_reviewer`, Rules |

Changing who reviews a request never widens the sandbox. The sandbox applies to spawned commands
(`git`, package managers, test runners), not only to built-in file edits.

Codex CLI defaults: no network access, writes limited to the active workspace. On launch Codex
recommends `workspace-write` + `on-request` for version-controlled folders and `read-only` for
others, and may start `read-only` until the directory is trusted.

---

## `sandbox_mode`

| Value | Effect |
|-------|--------|
| `read-only` | Inspect files; no edits; commands outside the read-only sandbox need approval |
| `workspace-write` | Read, edit inside the workspace, run routine local commands. Default low-friction mode |
| `danger-full-access` | No sandbox: no filesystem or network boundary. See [Safety notes](#safety-notes) |

The workspace is the cwd plus temp directories such as `/tmp`. Run `/status` in the TUI to see the
actual workspace directories.

## `approval_policy`

| Value | Effect |
|-------|--------|
| `on-request` | Work inside the sandbox; ask when a command needs to go beyond it |
| `never` | Never prompt. Best effort inside whatever sandbox is set; failures return to the model |
| `{ granular = { ... } }` | Keep some prompt categories interactive, auto-reject others |
| `untrusted` | **Retired.** Remove it; it can stop the client from starting |
| `on-failure` | **Deprecated** per the config reference; use `on-request` or `never` |

Granular keys: `sandbox_approval`, `rules`, `mcp_elicitations`, `request_permissions`,
`skill_approval` (booleans; `true` keeps that prompt interactive).

> [!NOTE]
> The installed CLI (0.158.0) accepts only `on-request` and `never` for `--ask-for-approval`
> (`untrusted`, `on-failure`, and `granular` are rejected as flag values). `granular` works only in
> `config.toml`.

Destructive app/MCP tool calls always require approval when the tool advertises a destructive
annotation (a read annotation takes priority).

### Migrating off `untrusted`

Remove `approval_policy = "untrusted"` from user and project config, profile files, scripts, and
managed defaults. Use `sandbox_mode = "read-only"` with `approval_policy = "on-request"` for
interactive read-only work. To keep "approve every command", omit `approval_policy` and set the
project's `trust_level = "untrusted"` in `~/.codex/config.toml` (see [Trusted projects](#trusted-projects)).
An explicit `on-request` overrides that derived policy.

---

## Setting them

### `config.toml`

```toml
approval_policy = "on-request"
sandbox_mode    = "workspace-write"
allow_login_shell = false   # optional hardening: no login shells for shell-based tools
```

### Command line

| Flag | Effect |
|------|--------|
| `-s`, `--sandbox <MODE>` | `read-only`, `workspace-write`, `danger-full-access` |
| `-a`, `--ask-for-approval <POLICY>` | `on-request` or `never` |
| `--approve-for-me` | Route approvals through auto-review using the `workspace-write` sandbox |
| `--add-dir <DIR>` | Extra directories writable alongside the workspace (repeatable) |
| `--search` | Live web search (same as `web_search = "live"`) |
| `-c key=value` | One-off config override, e.g. `-c approvals_reviewer=auto_review` |
| `-p`, `--profile <NAME>` | Layer `$CODEX_HOME/<NAME>.config.toml` over the base config |
| `--dangerously-bypass-approvals-and-sandbox` | No sandbox, no approvals. See [Safety notes](#safety-notes) |

`-a never` works with every `--sandbox` mode, so autonomy is still bounded by the sandbox you pick.
`/permissions` in the TUI switches the active mode or permission profile mid-session.

> [!NOTE]
> The docs call `--yolo` an alias of `--dangerously-bypass-approvals-and-sandbox`. The installed CLI
> accepts `--yolo` but hides it from `--help`. The docs say `codex exec --full-auto` remains as a
> deprecated compatibility path; the CLI rejects `--full-auto` on bare `codex` and does not list it
> under `exec --help`. Do not recommend either flag. Use explicit `--sandbox` and
> `--ask-for-approval` instead.

### Common combinations

| Intent | Settings |
|--------|----------|
| Auto (default preset) | `--sandbox workspace-write --ask-for-approval on-request` |
| Read-only browsing | `--sandbox read-only --ask-for-approval on-request` |
| Read-only CI | `--sandbox read-only --ask-for-approval never` |
| Auto-review | Auto preset plus `-c approvals_reviewer=auto_review` (or `--approve-for-me`) |
| Non-interactive edits | `codex exec --sandbox workspace-write` |

### Config profile files

`codex --profile <name>` layers `$CODEX_HOME/<name>.config.toml` (for example
`approval_policy = "never"` plus `sandbox_mode = "read-only"`) over `config.toml`. These are
whole-file layers, unrelated to permission profiles below.

---

## `[sandbox_workspace_write]`

Applies only when `sandbox_mode = "workspace-write"`.

| Key | Default | Purpose |
|-----|---------|---------|
| `writable_roots` | `[]` | Extra writable directories beyond the workspace |
| `network_access` | `false` | Allow outbound network for commands |
| `exclude_tmpdir_env_var` | `false` | Exclude `$TMPDIR` from writable roots |
| `exclude_slash_tmp` | `false` | Exclude `/tmp` from writable roots |

```toml
[sandbox_workspace_write]
writable_roots = ["/Users/YOU/.pyenv/shims"]
network_access = true
```

Prefer a narrow `writable_roots` entry or a Rules entry over widening the mode.

### Protected paths

Inside every writable root these stay **read-only, recursively**, even under `workspace-write`:

- `.git` (directory or file; if it is a `gitdir:` pointer file, the resolved Git directory too)
- `.agents` (when it is a directory)
- `.codex` (when it is a directory)

Edits to these need approval or a different profile. Do not tell the user to work around this by
loosening `sandbox_mode`.

---

## Network access

Default: off. Options, narrowest first:

1. **Rules or per-request approval** for specific commands (see [Rules](#rules)).
2. **`network_access = true`** under `[sandbox_workspace_write]` for unrestricted command network.
3. **`network_proxy` feature** to restrict that traffic to a domain policy.

```toml
[sandbox_workspace_write]
network_access = true

[features.network_proxy]
enabled = true
domains = { "api.openai.com" = "allow", "example.com" = "deny" }
```

One-off: `codex -c 'features.network_proxy=true' -c 'sandbox_workspace_write.network_access=true'`.

| Network access | `network_proxy` | Result |
|----------------|-----------------|--------|
| off | on | Stays off; the feature does nothing |
| on | off | Unrestricted direct outbound |
| on | on | Outbound constrained by the domain policy |

The proxy enforces rules only; it never grants access. `network_proxy` is `experimental` and off by
default in 0.158.0 (`codex features list`).

Domain rules: exact host matches itself; `*.example.com` matches subdomains only;
`**.example.com` matches apex plus subdomains; bare `*` is allow-only and broad. `deny` always wins.
With no `allow` entries, an active proxy blocks all external destinations.

Proxy defaults: `allow_local_binding = false` (blocks loopback, link-local, and private targets;
allow exact `localhost` or IP literals instead of enabling broadly), `unix_sockets` unset (none
allowed), `enable_socks5`, `enable_socks5_udp`, and `allow_upstream_proxy` all `true`. Avoid the
`dangerously_allow_non_loopback_proxy` and `dangerously_allow_all_unix_sockets` escape hatches.

Hostnames that resolve to private addresses stay blocked even when allowlisted. DNS checks are best
effort against rebinding, not a guarantee.

**Not covered by the command proxy:** web search, apps/connectors, MCP servers, browser and Computer
Use, Codex cloud tasks, and the client's own model/auth traffic. Control each separately.

### Web search

```toml
web_search = "cached"   # default; also "live", "indexed", "disabled"
```

Full-access sandbox settings (including `--yolo`) flip the default to live results. Treat all web
content as untrusted; prompt injection can make the agent fetch and follow hostile instructions.

---

## Permission profiles (beta)

Named policies combining filesystem rules and network rules. Beta; the format may change.

> [!WARNING]
> Profiles do **not** compose with the older settings. If `sandbox_mode` appears in any loaded
> config file, `--sandbox` is passed, or the selected config profile file sets `sandbox_mode`, Codex
> uses the older settings and ignores `default_permissions`. Configure one system or the other.

Built-ins: `:read-only`, `:workspace` (writes in workspace roots and temp dirs; keeps `.codex`
read-only), `:danger-full-access`. Select with `default_permissions`, or `/permissions` in the TUI.
Prefer `extends = ":workspace"` (or `:read-only`, or another profile) over building from scratch so
baseline protections carry forward. `:danger-full-access` cannot be extended; unknown parents and
cycles are rejected.

```toml
default_permissions = "project-edit"

[features]
network_proxy = true

[permissions.project-edit]
description = "Project editing with OpenAI API access."
extends = ":workspace"

[permissions.project-edit.workspace_roots]
"~/code/shared-lib" = true

[permissions.project-edit.filesystem.":workspace_roots"]
"**/*.env" = "deny"

[permissions.project-edit.network]
enabled = true

[permissions.project-edit.network.domains]
"api.openai.com" = "allow"
```

### Filesystem

Entries map a path to `read`, `write`, or `deny`. More specific entries beat broader ones; at equal
specificity `deny` > `write` > `read`. A missing or empty `filesystem` table keeps access
restricted and warns at startup.

| Path form | Meaning | Scoped subpaths |
|-----------|---------|-----------------|
| `:root` | Filesystem root | `.` only |
| `:minimal` | Platform and runtime paths common tools need | `.` only |
| `:workspace_roots` | Session workspace roots plus enabled profile `workspace_roots` | Yes |
| `:tmpdir` | `$TMPDIR` if set | `.` only |
| `:slash_tmp` | `/tmp` if it exists | `.` only |
| `/absolute/path`, `~/path` | Absolute or home-relative (`C:\path`, `~\work` on Windows) | Yes |

Under `:workspace_roots`, subpaths are relative to each root; `.` is the root itself; `..`
traversal is rejected. `deny` accepts globs (`"**/*.env" = "deny"`); prefer exact paths or subtree
rules for `read`/`write`, since globs there are less portable on Linux, WSL, and Windows. On those
platforms set `glob_scan_max_depth` (at least `1`) for unbounded `**` deny patterns.

`[permissions.<name>.workspace_roots]` maps a path to `true` to add a root (`false` stays inactive).
Config layers can add entries to the same profile name independently.

### Network

| Key | Default | Purpose |
|-----|---------|---------|
| `network.enabled` | `false` | Grants command network access; does **not** start the proxy |
| `network.domains."<pattern>"` | none | `allow` or `deny`; enforced only when the proxy is active |
| `network.unix_sockets."<path>"` | none | `allow` or `deny` for absolute socket paths |
| `network.proxy_url` | `http://127.0.0.1:3128` | HTTP proxy listener |
| `network.socks_url` | `http://127.0.0.1:8081` | SOCKS5 listener |
| `network.allow_local_binding` | `false` | Local/private guard, as above |

Domain rules take effect only with `features.network_proxy = true` (or admin-managed
`[experimental_network]`). Omit it and `network.enabled = true` gives unrestricted direct access.

Profiles govern local sandboxed commands only. Connectors, MCP, browser, Computer Use, and cloud use
their own controls. Treat writes to scripts, hooks, shell startup files, and shared directories as
sensitive: later tools run them outside the sandbox.

---

## Auto-review

A reviewer agent replaces the human at the sandbox boundary. It is a reviewer swap, not a grant: it
does not widen `writable_roots`, enable network, or weaken protected paths.

```toml
approval_policy = "on-request"
approvals_reviewer = "auto_review"   # default is "user"
```

- Applies only when approvals are interactive (`on-request` or a granular policy that surfaces the
  prompt). With `never`, `danger-full-access`, or `--yolo`, no approval request exists to review.
- Reviews only requests that already need approval: sandbox escalations, blocked network, edits
  outside writable roots, side-effecting app/MCP calls. In-sandbox actions run unreviewed. A
  destination on a network allowlist does not trigger review; add a Rules `decision = "prompt"`.
- Denials tell the main agent to find a materially safer path or stop and ask. The turn is
  interrupted after 3 consecutive denials or 10 in the last 50 reviews (open-source implementation).
  `/approve` in the TUI lets a person approve one recent denied action for one retry.
- Low- and medium-risk actions can proceed; critical-risk is denied; failures fail closed.
- Custom policy: local `[auto_review].policy = """..."""` replaces (does not merge with) the default
  policy; copy the full default first. Managed `guardian_policy_config` takes precedence.
- It uses extra model calls and adds to usage. It is not a deterministic guarantee.
- Reduce review volume by adding narrow `writable_roots` and narrow prefix rules such as
  `["cargo", "test"]`, never broad ones such as `["python"]` or `["curl"]`.

---

## Rules

Experimental. Rules decide which commands may run **outside** the sandbox.

**Location:** `.rules` files under a `rules/` folder next to any active config layer, for example
`~/.codex/rules/default.rules`. Codex scans them at startup, so restart after editing. Project rules
in `<repo>/.codex/rules/` load only when the project `.codex/` layer is trusted. Allow-listing a
command in the TUI writes to `~/.codex/rules/default.rules`. Codex may propose a `prefix_rule`
during escalations; review the prefix before accepting.

The format is Starlark (Python-like, side-effect free):

```python
prefix_rule(
    pattern = ["gh", "pr", ["view", "list"]],
    decision = "prompt",
    justification = "Viewing PRs is allowed with approval",
    match = ["gh pr view 7888", "gh pr list --repo openai/codex"],
    not_match = ["gh pr --repo openai/codex view 7888"],
)
```

| Field | Meaning |
|-------|---------|
| `pattern` (required) | Non-empty list. Each element is a literal string or a list of alternatives for that position. Matches an exact argument **prefix** |
| `decision` | `allow` (default): run outside the sandbox without prompting. `prompt`: ask each time. `forbidden`: block without prompting |
| `justification` | Optional non-empty reason, shown in prompts and rejections. For `forbidden`, name the alternative |
| `match`, `not_match` | Inline tests validated when rules load; a failing example rejects the file |

When several rules match, the most restrictive wins: `forbidden` > `prompt` > `allow`.

**Shell wrappers.** `bash -lc`, `bash -c`, and `zsh`/`sh` equivalents are split into individual
commands (each evaluated, strictest wins) only when the script is plain words joined by `&&`, `||`,
`;`, or `|`. With redirection, substitution, variable assignment or expansion, wildcards, or control
flow, the whole `["bash", "-lc", "<script>"]` is matched as one command. Allowing
`["git", "add"]` therefore does not allow `git add . && rm -rf /`.

### Test rules

```bash
codex execpolicy check --pretty --rules ~/.codex/rules/default.rules -- gh pr view 7888
```

`--rules` is required and repeatable; `--pretty` formats the JSON. Output has `matchedRules` and a
`decision` field. With no match, the output is `{"matchedRules":[]}` and has no `decision`. The CLI
also offers `--resolve-host-executables` (resolve absolute program paths against basename rules,
gated by `host_executable()` definitions); the fetched docs do not cover it.

`codex exec --ignore-rules` skips user and project `.rules` files for that run.

---

## Trusted projects

Trust is recorded per path in **user-level** `~/.codex/config.toml`:

```toml
[projects."/path/to/repo"]
trust_level = "trusted"   # or "untrusted"
```

An `untrusted` project skips project-scoped `.codex/` layers: project `config.toml`, hooks, and
rules. User and system layers still load. Untrusted also makes commands require approval unless a
rule allows them (see the `untrusted` migration above). Trust may also apply to worktrees. Do not
mark broad directories such as `$HOME` trusted.

---

## Platform sandboxes

| Platform | Mechanism | Notes |
|----------|-----------|-------|
| macOS | Seatbelt via `sandbox-exec` | Works out of the box. If the policy cannot be enforced, Codex refuses to run the command |
| Linux, WSL2 | `bwrap` (bubblewrap) + seccomp, Landlock as compatibility fallback | Install `bubblewrap`. Codex uses the first `bwrap` on `PATH`, else a bundled helper needing unprivileged user namespaces. Ubuntu 24.04 may need the `bwrap-userns-restrict` AppArmor profile. WSL1 is unsupported since 0.115 |
| Native Windows | Windows sandbox | `[windows] sandbox = "elevated"` (strongest) or `"unelevated"` (weaker network isolation; refuses policies it cannot enforce); config reference also lists `mxc`. `sandbox_private_desktop = true` by default |

In Docker or other containers the sandbox may fail if the host blocks namespaces, setuid `bwrap`, or
seccomp. Then provide isolation in the container and run with `--sandbox danger-full-access`. The
docs point to the Codex secure devcontainer example (firewalled egress plus `bubblewrap`).

### Test the sandbox

```bash
codex sandbox -P <profile> --log-denials -- <command> [args...]
```

Runs a command under the sandbox without starting a session. Options in 0.158.0: `-P`,
`--permission-profile <NAME>`, `--log-denials` (macOS: print sandbox denials after exit),
`--allow-unix-socket <PATH>`, `-C`, `-p`.

> [!NOTE]
> The docs show per-platform subcommands (`codex sandbox macos|linux|windows`) and a
> `--permissions-profile` flag. The installed macOS build has a flat `codex sandbox [COMMAND]...`
> (help text: "run under seatbelt") with `-P/--permission-profile`. Running `codex sandbox macos`
> here tries to execute a program named `macos`. Check `codex help sandbox` on the target machine.

`codex doctor` reports the effective posture (for example "restricted fs + restricted network ·
approval OnRequest"); `--summary` shortens it and `--json` emits a redacted report.

---

## Safety notes

> [!CAUTION]
> `danger-full-access`, `--dangerously-bypass-approvals-and-sandbox`, and `--yolo` remove the
> filesystem and network boundary. `approval_policy = "never"` with `danger-full-access` is "full
> access": no sandbox and no prompts. Prompt injection, a hostile repository, or a model mistake can
> then read credentials, exfiltrate data, or delete files. Codex credentials are among the
> reachable data.

- Do not set `danger-full-access` in `config.toml`, a profile file, or a shell alias. Use it per
  invocation, and only inside an already isolated environment (VM, container, throwaway checkout).
- Full access flips web search to live by default. Set `web_search` explicitly.
- Auto-review does nothing under full access (nothing crosses a boundary).
- Prefer the least step that solves the problem: a Rules entry, a narrow `writable_roots`, a scoped
  permission profile, or `network_access` with a domain allowlist.
- Keep `.env` and secret paths denied in permission profiles; keep broad prefix rules
  (`["python"]`, `["curl"]`, `["bash"]`) out of `allow`.
- Admins can restrict all of this in `requirements.toml` (for example `allowed_approval_policies`,
  `allowed_sandbox_modes`, `allowed_permission_profiles`). A managed constraint overrides user
  config; report it rather than working around it.

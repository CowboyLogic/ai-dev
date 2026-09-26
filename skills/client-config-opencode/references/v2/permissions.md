# V2 Permissions and Policies Reference

Sources: <https://opencode.ai/v2/docs/permissions/>, <https://opencode.ai/v2/docs/policies/>,
<https://opencode.ai/v2/docs/tools/>.

V2 replaces the V1 `permission` object (and the deprecated `tools` map) with one ordered `permissions` array.

## Rule shape

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git diff *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" },
  ],
}
```

| Field | Meaning |
|-------|---------|
| `action` | Tool permission action (wildcards allowed) |
| `resource` | Value being used: path, command, URL, query, skill ID, agent ID (wildcards allowed) |
| `effect` | `allow` \| `ask` \| `deny` |

All three fields are required strings.

## Matching

- **Last matching rule wins.** Put broad rules first, exceptions after.
- If no rule matches, the evaluator returns `ask`. In practice this never happens for an agent: every agent's
  rules sit on top of the [base policy](#defaults), whose first rule is `*`/`*` → `allow`. An action none of
  your rules mention therefore falls through to that baseline and is **allowed**, except for the baseline's own
  `ask` exceptions (external directories, `.env` reads).
- Wildcards match the whole value: `*` = zero or more characters **including `/`**, `?` = one character.
- A shell pattern ending in a space plus `*` also matches the bare command (`git status *` matches `git status`).
- Paths are normalized to forward slashes; matching is case-insensitive on Windows.
- For `read`, `edit`, and `external_directory`, a leading `~`, `~/`, `$HOME`, or `$HOME/` is expanded.
  Shell resources are raw command text and are **not** home-expanded.
- When one operation checks several resources (e.g. a multi-file patch): any `deny` denies, else any `ask` asks,
  else allow.

## Actions

| Action | Resource |
|--------|----------|
| `read` | Location-relative path, or canonical absolute external path |
| `edit` | Target path for `edit`, `write`, and `patch` |
| `glob` | Requested glob pattern |
| `grep` | Requested regex (not the search path) |
| `shell` | Scanner-produced command string; compound commands can produce several |
| `subagent` | Target agent ID |
| `skill` | Skill ID |
| `question` | `*` |
| `webfetch` | Requested URL |
| `websearch` | Search query |
| `external_directory` | Canonical external directory boundary, normally ending in `/*` |
| `<server>_<tool>` | `*` — one MCP tool (unsupported characters become `_`) |
| `execute` | `*` — whether Code Mode is available (nested tools still enforce their own rules) |
| `browser` | `*` — a `deny` removes the desktop browser Code Mode namespace |

Plugins may define more actions (actions are free-form strings).

The docs state `doom_loop` and `lsp` are not V2 Core actions. The V1 keys `list` and `todowrite` do not appear in
the V2 action table. V1 names map as: `bash` → `shell`, `task` → `subagent`, `write`/`patch` → `edit`.

## Defaults

Every agent starts from this base, then the shipped agent adds its own rules:

```json
[
  { "action": "*", "resource": "*", "effect": "allow" },
  { "action": "external_directory", "resource": "*", "effect": "ask" },
  { "action": "read", "resource": "*.env", "effect": "ask" },
  { "action": "read", "resource": "*.env.*", "effect": "ask" },
  { "action": "read", "resource": "*.env.example", "effect": "allow" }
]
```

| Agent | Additional built-in policy |
|-------|----------------------------|
| `build` | Allows questions |
| `plan` | Allows questions; denies edits except files under `~/.opencode/plan` |
| `general` | Denies questions and launching subagents |
| `explore` | Denies everything except reads, globs, grep, webfetch, websearch; asks for external dirs and `.env` reads |
| `title`, `summary` | Deny all actions |
| `compaction` | Base policy only |

## Global vs per-agent

Rules concatenate: lower-priority config first, global rules next, agent rules (`agents.<id>.permissions`) last.
Agent rules **append**; they never replace the global array. A custom subagent uses its own permissions, not a
subset of its parent's.

```jsonc
{
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
  ],
  "agents": {
    "reviewer": {
      "mode": "subagent",
      "permissions": [
        { "action": "edit", "resource": "*", "effect": "deny" },
        { "action": "shell", "resource": "*", "effect": "deny" },
      ],
    },
  },
}
```

## External directories

A path outside the active Location and its project worktree needs `external_directory` approval **before** its
`read`/`edit` rule is evaluated:

```jsonc
{
  "permissions": [
    { "action": "external_directory", "resource": "~/projects/reference/*", "effect": "allow" },
    { "action": "read", "resource": "~/projects/reference/*", "effect": "allow" },
    { "action": "edit", "resource": "~/projects/reference/*", "effect": "deny" },
  ],
}
```

## Common recipes

```jsonc
// Read-only agent
{ "permissions": [
  { "action": "*", "resource": "*", "effect": "deny" },
  { "action": "read", "resource": "*", "effect": "allow" },
  { "action": "glob", "resource": "*", "effect": "allow" },
  { "action": "grep", "resource": "*", "effect": "allow" },
] }

// Only one subagent may be launched
{ "permissions": [
  { "action": "subagent", "resource": "*", "effect": "deny" },
  { "action": "subagent", "resource": "reviewer", "effect": "allow" },
] }

// Deny all tools from one MCP server
{ "permissions": [{ "action": "context7_*", "resource": "*", "effect": "deny" }] }

// Allow one skill only — replace "git-release" with the skill ID to allow
{ "permissions": [
  { "action": "skill", "resource": "*", "effect": "deny" },
  { "action": "skill", "resource": "git-release", "effect": "allow" },
] }

// Ask before web searches
{ "permissions": [{ "action": "websearch", "resource": "*", "effect": "ask" }] }
```

## Approvals

| Choice | Reply | Result |
|--------|-------|--------|
| Allow once | `once` | Approve only this request |
| Allow always | `always` | Save the tool's proposed pattern as a durable, **project-scoped** `allow` rule |
| Reject | `reject` | Reject this and every other pending request in the session |

Saved approvals never override a configured `deny`. The CLI setting `session.permissions: "autoaccept"` in
`cli.json` accepts every request automatically (see [cli.md](cli.md)).

## Shell scanner (experimental)

```jsonc
{ "experimental": { "portable_shell_scanner": true } }
```

Replaces the default tree-sitter scanner (no fallback). An unparsable command returns a scanner error, not a denial.

---

## Policies

Policies live under `experimental.policies`. They are binary (`allow`/`deny`), never prompt, and only ever
**tighten** what permissions and providers allow.

| Field | Values |
|-------|--------|
| `action` | `provider.use` \| `permission` |
| `resource` | Wildcard pattern; meaning depends on the action |
| `effect` | `allow` \| `deny` |

Invalid statements are dropped with a server-log warning; the rest still apply. Last matching statement wins;
no match = allowed.

### `provider.use`

Resource is the provider ID. A denied provider disappears from the catalog even with valid credentials. This
replaces V1 `enabled_providers` / `disabled_providers`:

```jsonc
{
  "experimental": {
    "policies": [
      { "action": "provider.use", "resource": "*", "effect": "deny" },
      { "action": "provider.use", "resource": "anthropic", "effect": "allow" },
    ],
  },
}
```

### `permission`

Resource is `<action>:<value>`. A `deny` hard-blocks the check **after** agent rules and saved approvals
(fails with `Blocked by configuration policy`). An `allow` never grants access; it only lifts an earlier broader
policy `deny`, after which the agent's own rules decide.

```jsonc
{
  "experimental": {
    "policies": [
      { "action": "permission", "resource": "shell:git push *", "effect": "deny" },
      { "action": "permission", "resource": "edit:*.env", "effect": "deny" },
      { "action": "permission", "resource": "read:*/.ssh/*", "effect": "deny" },
      { "action": "permission", "resource": "github_delete_repository:*", "effect": "deny" },
    ],
  },
}
```

### Precedence (reversed vs normal settings)

| Authority | Source |
|-----------|--------|
| 1 (highest) | Connected OpenCode Console workspace |
| 2 | Global `~/.config/opencode/opencode.json(c)` |
| 3 | Direct `opencode.json(c)`; outer directories beat inner ones |
| 4 (lowest) | `.opencode/opencode.json(c)`; outer directories beat inner ones |

A repository cannot re-enable a provider or command that the global config denies. The
`opencode.config.policy` and `opencode.provider.opencode` plugins cannot be disabled via `plugins`.

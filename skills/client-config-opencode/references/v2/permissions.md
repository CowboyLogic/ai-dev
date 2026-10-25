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
| `opencode_list_mcp_resources` | MCP server name |
| `opencode_read_mcp_resource` | `<server>:<uri>` |
| `execute` | `*` — a `deny` removes Code Mode and the tools reached only through it (including MCP tools from servers that do not set `codemode: false`); nested tools still enforce their own rules |
| `browser` | `*` — a `deny` removes the desktop browser Code Mode namespace |
| `todowrite` | `*` — only exists when `experimental.todo` is `true` (2.1.0) |

Plugins may define more actions (actions are free-form strings).

The tools page (these lines unchanged through 2.1.4) lists Code Mode worktree utilities in the `opencode` namespace. `worktree_remove` uses
`edit` with the worktree directory as the resource, so an `edit` rule that denies that directory blocks it
(`force: true` can discard modified or untracked files). `worktree_create` and `worktree_list` request no built-in
permission action. The namespace is part of Code Mode, which `execute` controls.

The docs state `doom_loop` and `lsp` are not V2 Core actions. The V1 key `list` does not appear in the V2 action
table. `todowrite` is not in the docs table either, but the 2.1.4 source asserts it (resource `*`) when the
experimental todo tool is enabled. V1 names map as: `bash` → `shell`, `task` → `subagent`, `write`/`patch` → `edit`.

## Defaults

Every agent starts from this base, then the shipped agent adds its own rules:

```json
[
  { "action": "*", "resource": "*", "effect": "allow" },
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
| `explore` | Denies everything except shell, reads, globs, grep, webfetch, websearch, and external directories; asks for `.env` reads |
| `title`, `summary` | Deny all actions |
| `compaction` | Base policy only |

**Docs correction after 2.0.29 (upstream commit `20d172e462`, `docs: document external_directory allow default`):**
the base policy has no `external_directory` rule (`packages/schema/src/agent.ts`, identical in 2.0.29 and 2.1.4), so
the `*` allow applies and reads/edits outside the Location and worktree proceed without a prompt. V1 asked. Earlier
versions of this skill, following the older docs, listed an `ask` base rule and `explore` asking for external
directories; neither matches the source. `explore` allows `shell` and `external_directory`
(`packages/core/src/plugin/agent.ts`). Add the `ask` rule shown below to restore the V1 prompt.

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

A path outside the active Location and its project worktree is checked against `external_directory` **before** its
`read`/`edit` rule. The default policy **allows** `external_directory`, so nothing is
prompted unless you add a rule. To be asked before any access outside the project, then narrow with later rules
(last match wins):

```jsonc
{
  "permissions": [
    { "action": "external_directory", "resource": "*", "effect": "ask" },
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

Policies live under the top-level `policies` array. They are binary (`allow`/`deny`), never prompt, and only ever
**tighten** what permissions and providers allow.

> [!NOTE]
> Releases before 2.0.29 documented policies under `experimental.policies`. That key still works and merges into
> `policies` (order: V1 `enabled_providers` / `disabled_providers`, then `experimental.policies`, then `policies`;
> later statements win ties). Write new config under `policies`.

| Field | Values |
|-------|--------|
| `action` | `provider.use` \| `tool.use` \| `integration.use` |
| `resource` | Wildcard pattern; meaning depends on the action |
| `effect` | `allow` \| `deny` |

`permission` is **not** an action value (the 2.0.27 policies page listed it, but the config schema at 2.0.27,
2.0.29, and 2.1.4 only accepts the three above). Invalid statements are dropped with a server-log warning; the rest still
apply, so check the log after editing a `deny`. Last matching statement wins; no match = allowed. `*` matches zero
or more characters and `?` matches one; a trailing space-and-star, as in `shell:git push *`, also matches the
value without arguments.

### `provider.use`

Resource is the provider ID. A denied provider disappears from the catalog and model selection even with valid
credentials. This replaces V1 `enabled_providers` / `disabled_providers`:

```jsonc
{
  "policies": [
    { "action": "provider.use", "resource": "*", "effect": "deny" },
    { "action": "provider.use", "resource": "anthropic", "effect": "allow" },
  ],
}
```

### `tool.use`

Resource is `<action>:<value>`, matched against every resource the tool checks. A `deny` hard-blocks the check
**after** agent rules and saved approvals (fails with `Blocked by configuration policy`), so it overrides an `ask`
and an "Allow always" approval. An `allow` never grants access; it only lifts an earlier broader policy `deny`,
after which the agent's own rules decide.

```jsonc
{
  "policies": [
    { "action": "tool.use", "resource": "shell:git push *", "effect": "deny" },
    { "action": "tool.use", "resource": "edit:*.env", "effect": "deny" },
    { "action": "tool.use", "resource": "read:*/.ssh/*", "effect": "deny" },
    { "action": "tool.use", "resource": "github_delete_repository:*", "effect": "deny" },
  ],
}
```

| Pattern | Blocks |
|---------|--------|
| `shell:*` | Every shell command |
| `external_directory:*` | Any access outside the Location or worktree |
| `subagent:general` | Launching one subagent |
| `github_delete_repository:*` | One MCP tool |
| `*` | Everything not already denied |

### `integration.use`

Controls whether an MCP server, skill, or plugin is loaded at all. A denied MCP server or skill is removed; a
denied plugin is not loaded, however it was configured.

| Resource | Applies to |
|----------|------------|
| `mcp:<server>` | An MCP server by its configured name |
| `skill:<id>` | A skill by its ID |
| `plugin:<target>` | A plugin by unversioned package name or absolute path |

```jsonc
{
  "policies": [
    { "action": "integration.use", "resource": "mcp:*", "effect": "deny" },
    { "action": "integration.use", "resource": "mcp:github", "effect": "allow" },
  ],
}
```

### Precedence (reversed vs normal settings)

Ordinary settings let the nearest configuration win. Policies reverse that: statements from broader configuration
are evaluated later, so they override narrower ones.

| Authority | Source |
|-----------|--------|
| 1 (highest) | Connected OpenCode Console workspace |
| 2 | macOS managed preferences (`/Library/Managed Preferences/ai.opencode.managed.plist`) |
| 3 | System `opencode.json(c)` (`/Library/Application Support/opencode`, `/etc/opencode`, `%ProgramData%\opencode`) |
| 4 | Global `~/.config/opencode/opencode.json(c)` |
| 5 | Direct `opencode.json(c)`; outer directories beat inner ones |
| 6 (lowest) | `.opencode/opencode.json(c)`; outer directories beat inner ones |

A repository cannot re-enable a provider that the global config denies. Within one file, statements keep their
written order. A Console workspace's policies are appended after every authored statement; a denial from them
reads `Blocked by <organization>'s policy`. The `opencode.config.policy` and `opencode.provider.opencode` plugins
cannot be disabled via `plugins`.

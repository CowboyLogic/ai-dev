# OpenCode V2 Permission Reference

The native V2 `permissions` array: rule shape, matching, actions, defaults, and
policies.

**Sources (checked 2026-09-24):** <https://opencode.ai/v2/docs/permissions/> ·
<https://opencode.ai/v2/docs/tools/> · <https://opencode.ai/v2/docs/policies/> ·
<https://opencode.ai/v2/docs/skills/>

Load this file when writing V2 permission rules. For V1 `permission` maps, load
`../v1/permissions.md`. For converting V1 maps to V2 rules, load `migration.md`.

---

## Rule shape

`permissions` is an **ordered array**. Each rule has three required strings:

| Field | Meaning |
|---|---|
| `action` | Tool permission action. Wildcards allowed. |
| `resource` | Value being checked: path, command, URL, query, skill ID, or agent ID. Wildcards allowed. |
| `effect` | `allow`, `ask`, or `deny` |

JSON:

```json
{
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" },
    { "action": "shell", "resource": "git diff *", "effect": "allow" },
    { "action": "shell", "resource": "git push *", "effect": "deny" }
  ]
}
```

Markdown frontmatter (YAML list of maps):

```yaml
permissions:
  - action: shell
    resource: "*"
    effect: ask
  - action: shell
    resource: "git status *"
    effect: allow
```

Quote any `resource` that starts with `*` or contains a colon followed by a space, so YAML parses it as a
string.

---

## Evaluation

- **Last matching rule wins.** Put broad rules first, exceptions after.
- **No matching rule means `ask`.** (The base policy below starts with an
  allow-all rule, so in practice unmatched actions are allowed unless you add a
  deny.)
- Order of assembly: lower-priority configuration first, then global rules, then
  agent rules. Agent rules are appended, not substituted.
- An operation that checks several resources (for example a patch touching
  several files): any `deny` denies; otherwise any `ask` asks; otherwise allow.
- A custom subagent uses its own permissions, not a subset of its parent's.

## Matching

| Pattern | Matches |
|---|---|
| `*` | Zero or more characters, **including `/`** |
| `?` | Exactly one character |
| other | The literal character |

- Patterns match the **whole** normalized value. Backslashes normalize to `/`;
  matching is case-insensitive on Windows.
- A shell pattern ending in `" *"` also matches the command with no arguments:
  `git status *` matches `git status` and `git status --short`.
- `~`, `~/`, `$HOME`, and `$HOME/` at the start of a `read`, `edit`, or
  `external_directory` resource expand to the home directory. **Shell resources
  are raw command text and are not expanded.**

---

## Actions

| Action | Resource | Covers |
|---|---|---|
| `read` | Location-relative internal path, or canonical absolute external path | `read` tool |
| `edit` | Target path (every affected path for `patch`) | `edit`, `write`, `patch` |
| `glob` | Requested glob pattern | `glob` |
| `grep` | Requested regular expression (not the search path) | `grep` |
| `shell` | Scanner-produced command string; compound commands may produce several | `shell` |
| `subagent` | Target agent ID | `subagent` tool |
| `skill` | Skill ID | `skill` tool |
| `question` | `*` | `question` tool |
| `webfetch` | Requested URL | `webfetch` |
| `websearch` | Search query | `websearch` |
| `external_directory` | Canonical external directory boundary, normally ending in `/*` | Paths outside the Location and project worktree |
| `<server>_<tool>` | `*` | One MCP tool (unsupported characters become `_`) |
| `execute` | `*` | Code Mode availability; nested tools still enforce their own rules |

- Action names are strings, so plugins may add actions.
- `doom_loop` and `lsp` are **not** V2 core permission actions.
- V1 keys `list` and `todowrite` have no action in the V2 permissions or tools
  pages checked. Do not emit rules for them in native V2.
- The tools page says a `browser` deny rule with resource `*` removes the browser
  Code Mode catalog; it is not in the permissions page's action table.
- `skill` effects: `allow` advertises and loads; `ask` advertises and asks before
  loading; `deny` hides the skill from the model and rejects loading.
- `subagent` approvals save the agent ID; shell approvals save command prefixes.

### Deny everything, then allow

```json
{
  "permissions": [
    { "action": "*", "resource": "*", "effect": "deny" },
    { "action": "read", "resource": "src/**", "effect": "allow" }
  ]
}
```

### Restrict which subagents an orchestrator may launch

```json
{
  "permissions": [
    { "action": "subagent", "resource": "*", "effect": "deny" },
    { "action": "subagent", "resource": "reviewer", "effect": "allow" }
  ]
}
```

---

## Defaults

Every agent, including custom agents, starts with this ordered base policy:

```json
[
  { "action": "*", "resource": "*", "effect": "allow" },
  { "action": "external_directory", "resource": "*", "effect": "ask" },
  { "action": "read", "resource": "*.env", "effect": "ask" },
  { "action": "read", "resource": "*.env.*", "effect": "ask" },
  { "action": "read", "resource": "*.env.example", "effect": "allow" }
]
```

Note the change from V1: `.env` reads **ask** in V2 (V1 denied them).

Shipped agents append policies: `build` and `plan` allow questions; `plan` denies
edits except under `~/.opencode/plan`; `general` denies questions and launching
subagents; `explore` denies everything except read, glob, grep, webfetch, and
websearch; `title` and `summary` deny all; `compaction` keeps the base policy.

OpenCode also allows external-directory access to its own tool-output,
shell-output, temporary, and global configuration directories. The underlying
read or edit action still applies its own rules.

---

## External directories

A path outside both the active Location and its project worktree needs
`external_directory` approval **before** its `read` or `edit` approval:

```json
{
  "permissions": [
    { "action": "external_directory", "resource": "~/projects/reference/*", "effect": "allow" },
    { "action": "read", "resource": "~/projects/reference/*", "effect": "allow" },
    { "action": "edit", "resource": "~/projects/reference/*", "effect": "deny" }
  ]
}
```

Shell checks its external working directory and directories its scanner infers
before checking shell resources. Directory inference is best effort; prefer a
narrow shell allowlist over trying to deny every dangerous command.

---

## Approvals

When a rule resolves to `ask`, the client replies:

| Choice | Result |
|---|---|
| `once` | Approve only this request |
| `always` | Approve and save the tool's proposed pattern as a **durable, project-scoped** allow rule |
| `reject` | Reject this and every other pending permission request in the session |

Saved approvals never override a configured `deny`. (V1 `always` lasted only for
the current session.)

---

## Policies (hard deny)

Policies live under `experimental.policies`. They run after permission rules and
saved approvals, never prompt, and can only turn `allow` or `ask` into `deny`.

```json
{
  "experimental": {
    "policies": [
      { "action": "permission", "resource": "shell:git push *", "effect": "deny" },
      { "action": "permission", "resource": "edit:*.env", "effect": "deny" }
    ]
  }
}
```

- `permission` resource format: `<action>:<value>`, for example
  `subagent:general` or `github_delete_repository:*`.
- `provider.use` resource: a provider ID. It replaces V1 `enabled_providers` and
  `disabled_providers`.
- If nothing matches, the action is allowed. Last match wins.
- A policy `allow` never grants access; it only lifts an earlier broader policy
  `deny`, after which the agent's own rules decide.
- Precedence is reversed from normal config: the connected OpenCode Console
  workspace wins, then global config, then direct `opencode.json(c)` (outer beats
  inner), then `.opencode/opencode.json(c)`. A repository cannot re-enable what
  global config denies.

Policies are config-level, not per-agent. Use them for organization or user
guardrails; use agent `permissions` for role scoping.

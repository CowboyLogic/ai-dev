# Troubleshooting — Claude Code Agent Frontmatter

Load this file when an agent file does not behave as written. Start with the first table:
most "my field does nothing" reports are load failures or spelling.

**Source:** <https://code.claude.com/docs/en/sub-agents> and
<https://code.claude.com/docs/en/errors>

---

## Step Zero: Look at the Debug Log

Most load problems are **not reported in the session**. They appear only in the debug log:

```bash
claude --debug
```

Also run the bundled validator (`scripts/validate-agent.py <file-or-dir>`) and Claude
Code's own YAML check: `claude plugin validate .claude/agents` (v2.1.233+). The Claude Code
check reports files whose YAML does not parse, but **not** a file that parses and has no
`name`. `/doctor` reports agents in one directory sharing a name.

---

## Agent Not Found or Not Listed

Claude Code skips the file, without telling the session, when any of these is true:

| Problem | What Claude Code does | Fix |
|---|---|---|
| No `name` | Treats the file as documentation | Add `name` |
| Opening `---` is not line 1 (blank line, BOM, comment above it) | Reads the file as having no frontmatter | Make `---` the very first line |
| `name` starts with `-` | Skips, logs an error | Rename |
| `name` contains `:` | Skips, logs an error (since v2.1.218) | Remove the colon; `:` is reserved for plugin scoping |
| `name` but no `description` | Skips, logs the reason | Add `description` |
| YAML does not parse | Reads no fields, skips, logs the parse error | Fix the YAML (see next table) |

Other reasons an agent that *is* valid is not found:

| Symptom | Cause | Fix |
|---|---|---|
| Just created the first file in a brand-new `agents/` directory | The watcher only covers directories that existed at session start | Restart the session |
| File is under an `--add-dir` directory | Not watched | Restart after adding or editing |
| Session started with `--disable-slash-commands` | Directories not watched | Restart |
| Two files, same `name`, same tree | Only one loads, by filesystem order | Make names unique; `/doctor` lists duplicates |
| Same `name` in project and user scope | Higher-priority scope wins (managed, `--agents`, project, user, plugin) | Rename or delete one |
| Plugin agent | Scoped name | @-mention as `@agent-my-plugin:agent-name`; subfolders become part of the name (`my-plugin:review:security`) |

A plugin agent with no `name` or unparsable YAML still loads under its filename, unlike the
other scopes.

---

## YAML Problems That Break Parsing

| Symptom | Example | Fix |
|---|---|---|
| Colon inside an unquoted value | `description: Reviews code: fast` | Quote it, or use folded style `description: >` |
| Tab indentation | tab before `- Read` | YAML allows spaces only |
| Bad list indent under `skills`, `mcpServers`, `hooks` | children not indented beneath the key | Two-space indent consistently |
| Unquoted special characters (`*`, `&`, `!`, `@`, `%`, leading `{`/`[`) | `matcher: *` | Quote: `matcher: "*"` |
| Missing closing `---` | body swallowed into YAML | Add the closing delimiter |
| Prompt text above the first `---` | | Move the prompt to the body |

Multi-line descriptions are fine:

```yaml
description: >
  Researcher agent. Invoke when current information is needed before a decision.
  Use proactively for market or library comparisons.
```

---

## A Field Has No Effect

Claude Code ignores unrecognized fields without any error. Check in this order:

1. **Spelling and case.** Fields are camelCase. Common mistakes:

   | Written | Should be |
   |---|---|
   | `disallowed-tools`, `disallowed_tools`, `denyTools` | `disallowedTools` |
   | `max-turns`, `max_turns`, `maxturns` | `maxTurns` |
   | `permission-mode`, `permission_mode` | `permissionMode` |
   | `mcp-servers`, `mcp_servers` | `mcpServers` |
   | `omit-claude-md` | `omitClaudeMd` |
   | `initial-prompt` | `initialPrompt` |
   | `allowed-tools`, `allowedTools` | `tools` |
   | `system-prompt`, `prompt` (in a file) | the Markdown body |
   | `cacheTtl` at top level | nested under `experimental` |
   | `Tools`, `Model` | lowercase `tools`, `model` |

2. **Copilot or OpenCode field names.** Files copied from those tools carry fields Claude
   Code does not read: `handoffs`, `user-invocable`, `disable-model-invocation`, `target`,
   `infer`, `argument-hint`, `agents`, `mode`, `temperature`, `permission`, `steps`,
   `hidden`. They are ignored, not rejected. Note that `tools` values differ too: Copilot's
   `["read", "edit"]` aliases and OpenCode's tool maps are not Claude tool names.

3. **Scope restrictions.** Plugin agents ignore `hooks`, `mcpServers`, `permissionMode`,
   `initialPrompt`. `--agents` JSON ignores `color` and `experimental`. `initialPrompt` and
   `omitClaudeMd` only matter in specific run modes (see the frontmatter reference).

4. **Version requirements.** `omitClaudeMd` needs v2.1.271, `experimental.cacheTtl` v2.1.248,
   `permissionMode: manual` v2.1.200, empty `--agents` `prompt` v2.1.281. On an older
   version the field is unrecognized and ignored. Check with `claude --version`.

5. **Invalid value.** An out-of-range value (`effort: extreme`, `isolation: docker`,
   `memory: global`, `color: teal`) may be ignored or rejected depending on the field; do
   not rely on it. Use the exact values in the frontmatter reference.

---

## Tool Problems

| Symptom | Cause | Fix |
|---|---|---|
| `Agent '<name>' would be spawned with zero tools — refusing` | Every `tools` entry is **unrecognized** (typo such as `Grpe`), **not available to subagents** (`AskUserQuestion`, `Workflow`, `CronCreate` in the background), or **matched no tools in this session** (`mcp__github__*` with no GitHub server, `Agent` at the depth limit) | Fix each entry the error names. Or delete `tools` to inherit everything |
| Agent has fewer tools than listed, no error | Some entries resolved and others were dropped (background filter, unconnected MCP server) | Check the foreground/background note below; verify MCP servers are connected |
| Works with `--agent` but not when delegated | Delegated agents run in the background by default, with a reduced tool set | Remove entries only foreground agents get, set `background: false` and ask for foreground, or turn fork mode off |
| `disallowedTools: Bash(git push *)` removed all of Bash | Specifiers remove the whole tool | Use a `permissions.deny` rule or a `PreToolUse` hook |
| Agent can edit despite `tools: Read, Grep` | `memory` enables Read, Write, and Edit for the memory directory | Drop `memory` or accept that Write/Edit are scoped to memory files |
| Agent cannot spawn subagents | `Agent` missing from `tools`, depth limit reached, or the tool is withheld at the limit | Add `Agent`; check `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` |
| `Agent(worker)` restriction ignored | It only applies when the file runs as the main session | Run with `--agent`, or enforce with `permissions.deny` |
| Empty `tools:` list | Launches with no tools and no error | Omit the field to inherit, or list tools |
| Cannot edit files despite having `Edit` | Permission mode is prompting/denying, or the parent's mode overrides `permissionMode` | See permission-mode rules below |
| Edit or Write refused: "covered by a Read deny rule" | A `Read` deny rule matches the path | Narrow the rule, or add an `Edit` deny if the file must stay untouched |

### Permission mode surprises

- `permissionMode: default` in the file does not stop a parent in `acceptEdits`, `auto`, or
  `bypassPermissions` from forcing its own mode on the agent.
- `bypassPermissions` in the file does nothing unless the parent is already in that mode
  (v2.1.267+).
- In a background agent, prompts appear in the main session and name the agent. Under
  `dontAsk`, anything not explicitly allowed is denied.

---

## Model Problems

| Symptom | Cause | Fix |
|---|---|---|
| Runs on a different model than `model:` | Per-invocation `model` parameter wins over frontmatter; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` overrides everything; the org `availableModels` allowlist substituted a value | Run `/tasks` while it runs to see the real model; check the env var and settings; look for the substitution warning |
| `opus` alias runs on the main conversation's exact model | Same-family alias resolves to the parent's model (including `[1m]`) | Use a full model ID to pin a specific version |
| Frontmatter model ignored on an older Claude Code | Before v2.1.251 the env var took precedence | Update, or unset `CLAUDE_CODE_SUBAGENT_MODEL` |
| Thinking behaves differently than expected | Subagents inherit the parent's extended-thinking setting; no per-agent field | Change it in the parent session |
| `effort` seems unchanged | Available levels depend on the model | Choose a level the model supports |

---

## Delegation Problems

| Symptom | Cause | Fix |
|---|---|---|
| Claude never uses the agent | Vague `description` | State what it does **and when**: "Use proactively after code changes" |
| Claude uses it for the wrong tasks | Description too broad | Narrow the trigger; add "Do not use for ..." |
| Startup warning: agent descriptions over 15,000 tokens | Too many or too long descriptions (name + description count; every agent still loads) | Shorten descriptions, move detail into the body |
| `@agent-name` does nothing | Plugin agent needs the scoped name; new directory needs a restart | `@agent-my-plugin:name`; restart |
| Agent starts without context | Subagents get only their system prompt, the delegation message, CLAUDE.md, git status, and preloaded skills | Have the parent put needed context in the delegation prompt; consider a fork |
| `SendMessage` refuses a resumed name | The name now refers to a different agent (v2.1.199+) | Use the agent ID |
| Agent stopped partway, output marked partial | `maxTurns` reached (v2.1.246+) | Raise `maxTurns` or resume the agent |
| Nested agent request blocked | Depth limit (3 by default) | Raise `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` or flatten the design |

---

## Hooks and MCP in Frontmatter

| Symptom | Cause | Fix |
|---|---|---|
| Frontmatter `hooks` never fire | Project agent in an untrusted folder (agent still runs; hooks skipped, error in debug log); `--add-dir` folder needs its own trust; `-p` sessions do not count as trusted; plugin agent | Accept the workspace trust dialog for the folder containing the file; move the file to `~/.claude/agents/` or `.claude/agents/`; restart if under `--add-dir` |
| Trusting a parent folder did not help | Parent trust does not count for agent frontmatter hooks or inline MCP | Trust the exact folder containing the agent file |
| `Stop` hook logs as `SubagentStop` | Expected: `Stop` in subagent frontmatter is converted | Match on `SubagentStop` in settings hooks |
| Settings hook matcher `db-agent` matches too much | Before v2.1.195 the matcher was an unanchored regex | Anchor it: `^db-agent$` |
| Inline `mcpServers` entry missing | Same trust rule as hooks; blocked by `--strict-mcp-config`, `--bare`, or an `allowedMcpServers`/`deniedMcpServers` policy (warning names the server) | Trust the folder, use a name reference, or adjust policy |
| Named MCP reference has no tools | The server is not configured or connected in the session | Configure it, or define it inline |
| MCP tool descriptions bloating the main conversation | Server defined in `.mcp.json` | Define it inline in the agent instead; only the subagent gets it |

---

## Memory, Skills, and Isolation

| Symptom | Cause | Fix |
|---|---|---|
| `memory` does nothing | Auto memory disabled (`autoMemoryEnabled: false` or `CLAUDE_CODE_DISABLE_AUTO_MEMORY`) | Enable auto memory |
| Memory notes truncated | Only the first 200 lines or 25 KB of `MEMORY.md` load | Have the agent curate `MEMORY.md`; put detail in topic files |
| Agent never writes memory | The body never tells it to | Add "update your agent memory when you discover..." to the prompt |
| A preloaded skill is missing | Skill not found, disabled by policy, or `disable-model-invocation: true` (cannot be preloaded) | Fix the name, or make the skill model-invocable. Skips are logged at debug level |
| `Skill` in `tools` did not preload it | Preloading is the `skills` field | Use `skills:` |
| Worktree agent's Bash command fails | Its working directory resolved to the main checkout, or git was redirected there | Keep commands inside the worktree; avoid runtime-computed command names |
| Worktree branched from the wrong commit | It branches from the default branch, not the parent's `HEAD` | Have the delegation prompt include what to check out, or change the base per the worktrees docs |
| Named worktree agent runs in the main directory | With agent teams enabled, a named spawn becomes a teammate and ignores frontmatter `isolation` | Pass `isolation` on the Agent call |

---

## `--agents` JSON Errors

`claude` exits with code 1 and prints `Error: Invalid --agents configuration:`. Checks run in
order and stop at the first class that fails:

1. **`invalid JSON:`** — value starts with `{` but does not parse (a file's contents are
   checked the same way). Look for shell quoting mangling the JSON; use a file with `-p`.
2. **Schema problems**, one line per problem (first 20, then `…and N more`) — wrong types or
   unknown structure in a definition.
3. **`<name>: agent names must not start with '-'`.**

Other refusals: `--agents takes a JSON object, or a file path only with --print (-p)` (file
form used interactively; add `-p` or pass inline JSON) and `--agents file not found: <path>`
(also raised when malformed inline JSON that does not start with `{` is read as a path).
`--safe-mode` / `CLAUDE_CODE_SAFE_MODE` ignore `--agents` entirely. With `--resume` or
`--continue`, inline JSON is not re-checked but a file is checked on every launch.

---

## Quick Checklist Before Filing a Bug

1. `head -c 200 agent.md` — does the file start with `---` on line 1, no BOM or blank line?
2. `python scripts/validate-agent.py agent.md` — any error or warning?
3. `claude --debug` — any skip reason logged?
4. `claude --version` — does it meet the field's minimum version?
5. Same `name` elsewhere (`/doctor`, `~/.claude/agents/`, plugins)?
6. Foreground vs background — does the behavior differ?
7. `/tasks` while running — model and effort as expected?

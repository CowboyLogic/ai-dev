# Instructions Reference (AGENTS.md)

Covers how Codex discovers and layers `AGENTS.md` guidance, the keys that tune it, size limits,
how to verify what loaded, and where instructions end and skills or custom agents begin.

Codex builds the instruction chain once per run (once per TUI session). There is no cache; restart
Codex, or start a new session, after editing an instruction file or the config keys below.

## Discovery order

1. **Global scope.** In `CODEX_HOME` (default `~/.codex`), Codex reads `AGENTS.override.md` if it
   exists, otherwise `AGENTS.md`. Only the first non-empty file at this level is used.
2. **Project scope.** From the project root (typically the Git root) down to the current working
   directory, in each directory Codex checks `AGENTS.override.md`, then `AGENTS.md`, then each name
   in `project_doc_fallback_filenames`, in that order. **At most one file per directory.** With no
   project root, only the current directory is checked.
3. **Merge.** Files are concatenated root-first, joined by blank lines. Files closer to the cwd
   appear later in the prompt, so they win on conflict.

Empty files are skipped. Codex stops adding files once the size limit is reached.

> [!WARNING]
> An explicit `trust_level = "untrusted"` for the project skips the whole project `AGENTS.md` chain;
> only the global file loads. Verified on 0.158.0 in a real git repository with
> `codex debug prompt-input`: unset and `"trusted"` loaded the project `AGENTS.md`, `"untrusted"`
> (keyed by the repo root or by the working directory) did not. A project with no entry still loads
> it. Trust keys must match a real project path; an empty `.git` directory is not a repository.

`CODEX_HOME` moves the global scope. `CODEX_HOME=$(pwd)/.codex codex ...` loads that directory's
`AGENTS.md` as the global file. Check `echo $CODEX_HOME` when the wrong global guidance appears.

### Example layout

| File | Loaded when cwd is `services/payments/` |
|------|-----------------------------------------|
| `~/.codex/AGENTS.md` | Yes, first (global) |
| `AGENTS.md` (repo root) | Yes, second |
| `services/payments/AGENTS.override.md` | Yes, last |
| `services/payments/AGENTS.md` | No: the override in the same directory replaces it |
| `services/search/AGENTS.md` | No: not on the path to the cwd |

Use `AGENTS.override.md` for a temporary override without deleting the base file; remove it to
restore the shared guidance. Codex does not read files below the cwd, so put overrides as close to
the specialized work as possible.

## Keys

```toml
# ~/.codex/config.toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536
```

| Key | Default | Meaning |
|-----|---------|---------|
| `project_doc_fallback_filenames` | `[]` | Extra names tried in each directory when `AGENTS.md` is missing. Names not listed are ignored |
| `project_doc_max_bytes` | `32768` (32 KiB) | Byte cap on embedded project instructions |

With the list above, each directory is checked as `AGENTS.override.md`, `AGENTS.md`,
`TEAM_GUIDE.md`, `.agents.md`. A fallback file is used only where no override or `AGENTS.md`
exists in that directory. Other agents' files such as `CLAUDE.md` are **not** read unless listed as a
fallback.

> [!NOTE]
> The docs say the limit applies to the combined size. In a local test on 0.158.0, lowering
> `project_doc_max_bytes` truncated only the project portion (cut mid-text); the global file was
> unaffected. Treat the cap as applying to project files, and raise it or split guidance into nested
> directories when instructions are cut off. Do not rely on the global file being counted.

## Size and content rules

- Keep each file short and specific: working agreements, commands to run, and conventions. Files
  are loaded on every run, so bulk costs tokens on every task.
- Split by scope: repo-wide rules at the root, team or service rules in a nested file.
- For Codex code review in GitHub, add a `## Code Review Rules` section to the `AGENTS.md` closest to
  the governed code. Keep rules concise, state the behavior to flag and any safe path, and leave
  formatting and lint checks to CI.
- Never put secrets in these files; they are sent to the model.

## Verify what loaded

Prefer the local render. It needs no model call and shows exactly what the model sees:

```bash
codex debug prompt-input | grep -c 'MARKER-FROM-YOUR-FILE'
```

In 0.158.0 the output is a JSON list of input items. The project instructions arrive in a `user`
item whose text begins `# AGENTS.md instructions for <cwd>` and wraps the content in
`<INSTRUCTIONS>`: global guidance first, then a `--- project-doc ---` separator, then the project
files in root-to-cwd order. Run it from the directory you want to test and search the text for a marker
string from each file. `codex debug prompt-input` also
accepts `-c key=value`, so it can test `project_doc_*` changes before committing them.

Other checks, less direct:

- Ask Codex to summarize its instructions, for example
  `codex --ask-for-approval never "Summarize the current instructions."`. This spends model tokens
  and relies on the model's report; use the render above first.
- Set `log_dir` (for example `codex -c log_dir=./.codex-log`) to enable the opt-in plaintext
  `codex-tui.log`, or inspect a `session-*.jsonl` file if session logging is on. Not verified locally.
- `/status` in the TUI shows the workspace roots. The docs also cite `codex status`, but 0.158.0 has
  no such subcommand; use the slash command.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Nothing loads | Wrong directory or no project root; file is empty (empty files are skipped) |
| Wrong guidance appears | An `AGENTS.override.md` higher in the tree or in `CODEX_HOME` |
| Fallback name ignored | Typo in `project_doc_fallback_filenames`, or a higher-priority file exists in that directory; restart Codex |
| Instructions truncated | Raise `project_doc_max_bytes` or split across nested directories |
| Stale guidance | Restart or start a new session; nothing to clear |

## AGENTS.md vs skills vs custom agents

| Mechanism | Purpose | Loaded | Lives in |
|-----------|---------|--------|----------|
| `AGENTS.md` | Always-on working agreements: commands, conventions, review rules | Every run, in full, up to the size cap | `~/.codex/`, repo root down to cwd |
| Skills | Task-specific procedures and bundled resources | On demand, when a task matches | `.agents/skills/`, `~/.agents/skills/` (see `skills.md`) |
| Custom agents | Named subagents with their own model, instructions, and settings | When spawned | `~/.codex/agents/*.toml`, `<repo>/.codex/agents/*.toml` |

Rules of thumb: put short guidance that applies to nearly every task in `AGENTS.md`; move long or
occasional procedures into a skill; use a custom agent when the work needs a separate role or
configuration. Do not duplicate content across them.

Creating or editing custom agents is out of scope here. Use the `agent-creator-codex` skill
(`skills/agent-creator-codex/` in this repository). Skills are covered in `skills.md`, and the
`[agents]` table and subagents overview in `agents-plugins.md`.

Instruction files never grant permissions. Sandbox and approval behavior comes from `config.toml`
and Rules (see `permissions.md`), and `AGENTS.md` text cannot loosen it.

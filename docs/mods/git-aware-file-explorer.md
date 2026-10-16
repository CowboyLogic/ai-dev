# Git-Aware File Explorer

A Files pane for Claude Code that knows about git. It joins the workspace file browser and the
list of changes into one pane: the tree marks what changed, and selecting a file shows its diff
in a panel beside the tree.

- **Mod name:** `git-aware-file-explorer`
- **Client:** Claude Code (desktop app and terminal)
- **Source:** [mods/claude/git-aware-file-explorer](https://github.com/CowboyLogic/ai-dev/tree/main/mods/claude/git-aware-file-explorer)

---

## What it does

- **Branch bar.** The current branch, the lines added and deleted across all changes, and a count of
  changed files. The count is a toggle that narrows the tree to changed files only. New files count
  as added lines; past 200 new files, or for a new file over 512 KB or one that cannot be read, the
  added total is marked as a minimum (`+1234+`). When git's output passes 4 MB it is cut, and the counts drawn from it are marked the same way.
- **Git-aware tree.** Files and folders with icons, a status letter on each changed file, and a mark
  on every folder that holds a change. Ignored files are dimmed and deleted files struck through.
  A filter box narrows the tree by name.
- **Diff panel.** Selecting a changed file shows its diff against `HEAD`, with added and deleted lines
  tinted and the file's own line counts in the header. Selecting an unchanged file shows a preview.
- **Stays current.** The pane rescans the workspace every few seconds and after each tool call that
  can change files.

## Where it applies

Use it in a git repository when you want to watch an agent's changes land file by file without
switching between the Files and Changes views. Outside a repository it works as a plain file browser.

The pane opens at the start of each session. `/git-files` reopens it after it is closed.

---

## Install

Load the mod's folder as described in [Installing a Claude Code mod](index.md#installing-a-claude-code-mod),
with `<mod-name>` set to `git-aware-file-explorer`.

### Verify installation

Start a session in a git repository. The **Files** pane opens with the branch bar at the top. If it
does not, run `/git-files`.

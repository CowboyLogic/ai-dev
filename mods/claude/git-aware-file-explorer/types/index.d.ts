/** One changed path, as `git status --porcelain` reports it. */
export type Change = {
  /** Path relative to the repository root, `/`-separated. */
  path: string
  /** Index (staged) column: one of ` MADRCU?`. */
  x: string
  /** Worktree column: one of ` MADRCU?`; `?` after a `D` is a deletion staged with the file back on disk. */
  y: string
  /** For a rename or copy, the path it came from. */
  from?: string
}

/** What the last scan of the workspace found. */
export type Scan = {
  /** The tree's root: the repository's top level, or the session's directory. */
  root: string
  /** Whether `root` is a git work tree. */
  isRepo: boolean
  /** The checked-out branch, or a short commit id when detached. */
  branch?: string
  /**
   * The commit HEAD names, absent before the first commit. A pull or checkout that leaves the status
   * clean still moves it, so the scan changes and the tree and filter are listed again.
   */
  head?: string
  changes: Change[]
  /** Ignored paths relative to root; a directory ends with `/`. */
  ignored: string[]
  /** git's list of ignored paths passed 4 MiB and was cut, so `ignored` holds its start only. */
  isIgnoredTruncated?: boolean
  /** Lines added and deleted across all changes against HEAD, untracked files included. */
  lines?: {
    added: number
    deleted: number
    /** Untracked files went uncounted (too many, or too large to read), so `added` is a floor. */
    partial?: boolean
    /**
     * git's line counts passed 4 MiB of output and were cut, a recreated file went uncounted (its
     * committed version passed 4 MiB, or git could not diff it), or git could not count them at all
     * (an unreadable changed file), so both totals are floors. Not always a cut, despite the name.
     */
    isTruncated?: boolean
  }
  /** git's status passed 4 MiB and was cut, so the changes and line totals are floors. */
  isTruncated?: boolean
  /** Error text from the last scan, if it failed. */
  error?: string
  /** Modification times and sizes of the files the pane shows, so a content edit redraws it. */
  stamp?: string
}

declare module 'claude-code' {
  interface PluginState {
    'git-aware-file-explorer': {
      scan: Scan | null
      expanded: string[]
      selected: string | null
      changedOnly: boolean
      filter: string
    }
  }
}

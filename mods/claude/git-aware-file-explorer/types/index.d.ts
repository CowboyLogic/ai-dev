/** One changed path, as `git status --porcelain` reports it. */
export type Change = {
  /** Path relative to the repository root, `/`-separated. */
  path: string
  /** Index (staged) column: one of ` MADRCU?`. */
  x: string
  /** Worktree column: one of ` MADRCU?`. */
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
  changes: Change[]
  /** Ignored paths relative to root; a directory ends with `/`. */
  ignored: string[]
  /** Lines added and deleted across all changes against HEAD, untracked files included. */
  lines?: {
    added: number
    deleted: number
    /** Untracked files went uncounted (too many, or too large to read), so `added` is a floor. */
    partial?: boolean
  }
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
      /** First line of the open file the right panel shows. */
      panelOffset: number
      /** First row of the tree the left column shows. */
      treeOffset: number
    }
  }
}

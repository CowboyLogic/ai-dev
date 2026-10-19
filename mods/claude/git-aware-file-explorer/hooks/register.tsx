import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Change, Scan } from '../types'
import { diffIndex, nativeWindow, PREVIEW_BLOCK_ROWS, previewCapacity, previewWindow, spacerHeights, visibleText } from './viewport'
import type { HunkStart } from './viewport'

const PANE = 'git-aware-file-explorer'
const TITLE = 'Files'
const SCAN_EVERY_MS = 5000
const PREVIEW_BYTES = 256 * 1024
/** Leave room within the engine's drawing budget for the tree and controls. */
const FULL_PREVIEW_CHARS = 48000
/** Most matches a filter lists; the rest are counted, not drawn. */
const FILTER_LIMIT = 300
/** Files and directories a filter outside a git repository discovers, at most. */
const WALK_LIMIT = 20000
/** The tree column's narrowest width, in cells; its widest is half the pane. */
const TREE_MIN_COLUMNS = 34
/** Cells between the tree column and the file panel. */
const GUTTER = 2
/** Rows the branch bar takes above both sides: its line and the gap under it. */
const BRANCH_ROWS = 2
/** A definite row height lets offscreen tree rows keep their native layout space. */
const TREE_ROW_ROWS = 2
/**
 * Tools whose calls can change the work tree; a scan follows each. PowerShell is the shell tool on
 * Windows. A subagent's own tool calls reach the hook too, so Agent needs no entry.
 */
const WRITERS = new Set(['Edit', 'MultiEdit', 'Write', 'NotebookEdit', 'Bash', 'PowerShell'])
/** Files the native Files pane leaves out too. */
const HIDDEN = new Set(['.git', '.DS_Store', 'Thumbs.db'])
/** Row tints: a neutral grey with alpha reads in both light and dark themes. */
const SELECTED_BG = '#8080803a'
const HOVER_BG = '#8080801f'
/** Diff line colors: light backgrounds with dark text, readable in either theme. */
const ADDED = { bg: '#ccffd8', fg: '#116329' }
const DELETED = { bg: '#ffd7d5', fg: '#82071e' }
const scanAtom = atom({ plugin: 'git-aware-file-explorer', key: 'scan' } as const, null)
const expandedAtom = atom({ plugin: 'git-aware-file-explorer', key: 'expanded' } as const, [])
const selectedAtom = atom({ plugin: 'git-aware-file-explorer', key: 'selected' } as const, null)
const changedOnlyAtom = atom({ plugin: 'git-aware-file-explorer', key: 'changedOnly' } as const, false)
const filterAtom = atom({ plugin: 'git-aware-file-explorer', key: 'filter' } as const, '')

type $ = EngineInterface

type Row = {
  path: string
  name: string
  depth: number
  isDir: boolean
  isOpen: boolean
  change?: Change
  /** Changed paths under a directory. */
  count: number
  isIgnored: boolean
  /** On record in git but gone from disk (deleted). */
  isMissing: boolean
}

/**
 * Splits `git status --porcelain=v1 -z` output into changes, one per path. A path staged for
 * deletion and back on disk comes as two records (`D ` and `??`); they become one, `D?`.
 */
export function parseStatus(out: string): Change[] {
  const parts = out.split('\0')
  const byPath = new Map<string, Change>()
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i] ?? ''
    if (part.length < 4) continue
    const change: Change = { x: part.charAt(0), y: part.charAt(1), path: part.slice(3) }
    if (change.x === 'R' || change.x === 'C') change.from = parts[++i]
    const seen = byPath.get(change.path)
    if (seen && (seen.x === 'D' || change.x === 'D') && (seen.x === '?' || change.x === '?')) {
      byPath.set(change.path, { x: 'D', y: '?', path: change.path })
    } else byPath.set(change.path, change)
  }
  return [...byPath.values()]
}

/** A path staged for deletion and back on disk, untracked: its diff is HEAD's version against the file. */
const isRecreated = (c: Change) => c.x === 'D' && c.y === '?'

/** The one letter and theme color a change is drawn with. */
export function badge(c: Change): { letter: string; color: string } {
  const { x, y } = c
  if (x === '?') return { letter: 'U', color: 'success' }
  if (isRecreated(c)) return { letter: 'M', color: 'warning' }
  if (x === 'U' || y === 'U' || (x === 'A' && y === 'A') || (x === 'D' && y === 'D')) {
    return { letter: '!', color: 'error' }
  }
  const code = y !== ' ' ? y : x
  if (code === 'A') return { letter: 'A', color: 'success' }
  if (code === 'D') return { letter: 'D', color: 'error' }
  if (code === 'R' || code === 'C') return { letter: code, color: 'suggestion' }
  return { letter: code, color: 'warning' }
}

function stageNote(c: Change): string {
  if (c.x === '?') return 'untracked'
  if (isRecreated(c)) return 'deletion staged, back on disk'
  if (c.x !== ' ' && c.y === ' ') return 'staged'
  if (c.x === ' ') return 'unstaged'
  return 'partly staged'
}

const DOC = (fill: string) =>
  `<path d="M3.5 1.5h5.5l3.5 3.5v9.5h-9z" fill="${fill}"/><path d="M9 1.5v3.5h3.5" fill="none" stroke="#00000055"/>`

/** A small file-type icon, by name, as SVG markup. */
export function iconFor(name: string): string {
  const lower = name.toLowerCase()
  const ext = lower.includes('.') ? lower.slice(lower.lastIndexOf('.') + 1) : ''
  let body: string
  if (lower.startsWith('.git')) body = '<path d="M8 1.5 14.5 8 8 14.5 1.5 8z" fill="#e0603d"/>'
  else if (ext === 'json' || ext === 'jsonc') {
    body =
      '<text x="8" y="12" font-size="11" font-family="ui-monospace,monospace" text-anchor="middle" fill="#d6a23a">{}</text>'
  } else {
    const colors: Record<string, string> = {
      md: '#4ea35b', mdx: '#4ea35b', yaml: '#e0604d', yml: '#e0604d', toml: '#9a8cd6',
      py: '#4b8bd4', ts: '#3d8fd6', tsx: '#3d8fd6', js: '#d9c13a', jsx: '#d9c13a', mjs: '#d9c13a',
      sh: '#6bab5a', zsh: '#6bab5a', bash: '#6bab5a', html: '#e07a3d', css: '#5a8fd6',
    }
    body = DOC(colors[ext] ?? '#8c8c8c')
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16">${body}</svg>`
}

async function git($: $, root: string, args: string[], stdin?: string) {
  return $.process.run(['git', '--no-optional-locks', ...args], { cwd: root, stdin })
}

/**
 * Whether a diff failed. `--no-index` exits 1 when the files differ, and also on some errors (a
 * file it can't access), which print nothing but the error.
 */
function isDiffFailed(out: { exitCode: number; stdout: string; stderr: string }) {
  return out.exitCode > 1 || (out.exitCode === 1 && out.stdout === '' && out.stderr.trim() !== '')
}

/**
 * `git diff` (with `flags`) of a recreated path: its version in `base`, piped in, against the file
 * on disk, so the panel and the totals see the net change. `'cut'` when that version passed 4 MiB
 * and can't be piped whole; undefined when git can't run it so.
 */
async function recreatedDiff($: $, root: string, base: string, path: string, flags: string[]) {
  const old = await git($, root, ['show', base + ':' + path])
  if (old.isStdoutTruncated) return 'cut' as const
  if (old.exitCode !== 0) return undefined
  const out = await git($, root, ['diff', ...flags, '--no-index', '--', '/dev/stdin', path], old.stdout)
  return isDiffFailed(out) ? undefined : out
}

async function scan($: $): Promise<Scan> {
  const cwd = await $.session.cwd()
  try {
    const top = await $.process.run(['git', 'rev-parse', '--show-toplevel'], { cwd })
    if (top.exitCode !== 0) {
      // Outside a repository is no error; any other failure (dubious ownership, a broken .git) is shown.
      const reason = top.stderr.trim()
      const error = reason === '' || /not a git repository/i.test(reason) ? undefined : reason
      return { root: cwd, isRepo: false, changes: [], ignored: [], error }
    }
    const root = top.stdout.trim()
    const [status, ignored, branch] = await Promise.all([
      git($, root, ['status', '--porcelain=v1', '-z', '-uall']),
      git($, root, ['ls-files', '-z', '--others', '--ignored', '--exclude-standard', '--directory']),
      git($, root, ['branch', '--show-current']),
    ])
    let name = branch.stdout.trim()
    if (name === '') name = (await git($, root, ['rev-parse', '--short', 'HEAD'])).stdout.trim()
    // Output past 4 MiB is cut: keep the whole entries, and mark the counts as floors.
    const out = status.isStdoutTruncated ? status.stdout.slice(0, status.stdout.lastIndexOf('\0') + 1) : status.stdout
    const changes = status.exitCode === 0 ? parseStatus(out) : []
    const lines = changes.length > 0 ? await lineTotals($, root, changes) : { added: 0, deleted: 0 }
    return {
      root,
      isRepo: true,
      branch: name || undefined,
      changes,
      lines,
      isTruncated: status.isStdoutTruncated || undefined,
      // Cut the same way: whole entries only, and a filter says it may have missed some.
      ignored: (ignored.isStdoutTruncated
        ? ignored.stdout.slice(0, ignored.stdout.lastIndexOf('\0') + 1)
        : ignored.stdout
      )
        .split('\0')
        .filter(Boolean),
      isIgnoredTruncated: ignored.isStdoutTruncated || undefined,
      // A failed status reads no changes; the error says so even when git printed nothing.
      error: status.exitCode === 0 ? undefined : status.stderr.trim() || `git status exited ${status.exitCode}`,
    }
  } catch (err) {
    return { root: cwd, isRepo: false, changes: [], ignored: [], error: String(err) }
  }
}

export type Numstat = { added: number; deleted: number; path: string }

/**
 * Entries of `git diff --numstat -z`, each path verbatim (without -z git quotes a name outside
 * printable ASCII). A rename's paths follow its counts, and it is named by the new one; binary
 * files (`-`) count no lines.
 */
export function parseNumstat(out: string): Numstat[] {
  const entries: Numstat[] = []
  const parts = out.split('\0')
  const count = (n: string) => (/^\d+$/.test(n) ? Number(n) : 0)
  for (let i = 0; i < parts.length; i++) {
    const record = parts[i] as string
    const a = record.indexOf('\t')
    const d = record.indexOf('\t', a + 1)
    if (a < 0 || d < 0) continue
    let path = record.slice(d + 1)
    if (path === '') {
      path = parts[i + 2] ?? ''
      i += 2
    }
    entries.push({ added: count(record.slice(0, a)), deleted: count(record.slice(a + 1, d)), path })
  }
  return entries
}

/** Lines added and deleted across numstat entries. */
export function sumNumstat(entries: Numstat[]): { added: number; deleted: number } {
  return entries.reduce((t, e) => ({ added: t.added + e.added, deleted: t.deleted + e.deleted }), { added: 0, deleted: 0 })
}

/** Lines in a text, as git counts them: a last line without a newline still counts. */
export function countLines(text: string): number {
  if (text === '' || text.includes('\0')) return 0
  const breaks = text.split('\n').length - 1
  return text.endsWith('\n') ? breaks : breaks + 1
}

/** Untracked files read for their line count, at most; larger ones are skipped. */
const UNTRACKED_LIMIT = 200
const UNTRACKED_BYTES = 512 * 1024
/** Changed files whose modification time a scan reads, at most (see stampFor). */
const STAMP_LIMIT = 200

/**
 * What a diff compares the working tree against: HEAD, or on a branch with no commits yet the empty
 * tree, so staged and unstaged changes come out as one diff and no line counts twice.
 */
async function diffBase($: $, root: string): Promise<string> {
  if ((await git($, root, ['rev-parse', '--verify', '-q', 'HEAD'])).exitCode === 0) return 'HEAD'
  return (await git($, root, ['hash-object', '-t', 'tree', '/dev/null'])).stdout.trim()
}

/** Lines added and deleted against HEAD (staged and unstaged), untracked files counted as added. */
async function lineTotals($: $, root: string, changes: Change[]) {
  const base = await diffBase($, root)
  const out = await git($, root, ['diff', '--numstat', '-z', '--no-ext-diff', base])
  // Output past 4 MiB is cut: keep the whole entries (the totals are marked as floors below).
  let numstat = parseNumstat(out.isStdoutTruncated ? out.stdout.slice(0, out.stdout.lastIndexOf('\0') + 1) : out.stdout)
  // A recreated path counts its net change, in place of the deletion the diff against base reports.
  let isUncounted = false
  for (const c of changes.filter(isRecreated)) {
    const net = await recreatedDiff($, root, base, c.path, ['--numstat', '-z'])
    const others = numstat.filter(e => e.path !== c.path)
    // Too large to diff, or git can't: neither its deletion nor its contents count, and both totals are floors.
    if (net === 'cut' || net === undefined) isUncounted = true
    numstat = net === 'cut' || net === undefined ? others : [...others, ...parseNumstat(net.stdout)]
  }
  const total: { added: number; deleted: number; partial?: boolean; isTruncated?: boolean } = sumNumstat(numstat)
  // A diff git could not make (an unreadable changed file) prints no counts at all: both are floors.
  if (out.isStdoutTruncated || isUncounted || out.exitCode !== 0) total.isTruncated = true
  const untracked = changes.filter(c => c.x === '?')
  if (untracked.length > UNTRACKED_LIMIT) total.partial = true
  for (const c of untracked.slice(0, UNTRACKED_LIMIT)) {
    const path = root + '/' + c.path
    const stat = await $.fs.stat(path).catch(() => undefined)
    // Gone since git listed it, or unreadable: uncounted, so the total is a floor.
    if (!stat) {
      total.partial = true
      continue
    }
    // git diffs a symbolic link as one line, its target, whatever it leads to.
    if (stat.isLink) {
      total.added += 1
      continue
    }
    if (stat.kind !== 'file') continue
    if (stat.size > UNTRACKED_BYTES) {
      total.partial = true
      continue
    }
    // A file that can't be read goes uncounted, so the total is a floor, not an exact zero for it.
    const text = await $.fs.read(path).catch(() => undefined)
    if (text === undefined) total.partial = true
    else total.added += countLines(text)
  }
  return total
}

/**
 * Modification time and size of the open file, the open folders and the first STAMP_LIMIT changed
 * files. An edit that leaves git's status and line totals as they were (`bar` to `baz`) still
 * changes this, so the scan that sees it redraws the pane.
 */
async function stampFor($: $, s: Scan): Promise<string> {
  const selected = await read($, selectedAtom)
  const paths = new Set(['', ...(await read($, expandedAtom)), ...s.changes.slice(0, STAMP_LIMIT).map(c => c.path)])
  if (selected !== null) paths.add(selected)
  const stats = await Promise.all(
    [...paths].map(p => $.fs.stat(p === '' ? s.root : s.root + '/' + p).catch(() => undefined)),
  )
  return stats.map(st => (st ? st.mtimeMs + ':' + st.size : '-')).join(',')
}

/** The scan running now, and whether another was asked for while it ran (see rescan). */
let scanning: Promise<void> | undefined
let isRescanDue = false

/**
 * Scans and writes the result only when it changed, so idle scans redraw nothing. Scans never
 * overlap: one asked for while another runs is folded into a single scan after it, so an older
 * scan can never finish last and overwrite a newer one.
 */
function rescan($: $): Promise<void> {
  if (scanning) {
    isRescanDue = true
    return scanning
  }
  scanning = (async () => {
    try {
      do {
        isRescanDue = false
        const found = await scan($)
        const next: Scan = { ...found, stamp: await stampFor($, found) }
        // Files may have come or gone since the filter's list was made, even with the scan unchanged.
        listing = undefined
        // Any write redraws the pane, so an unchanged scan is not written at all.
        if (JSON.stringify(await read($, scanAtom)) !== JSON.stringify(next)) await update($, scanAtom, () => next)
      } while (isRescanDue)
    } finally {
      scanning = undefined
    }
  })()
  return scanning
}

/** Reveal the shared pane's top after opening it or changing its selection/filter. */
async function settle($: $) {
  await $.ui.scroll({ to: 'start', in: PANE }).catch(() => undefined)
}

/** Changed-path counts for every directory that holds a change (`''` is the root). */
export function rollup(changes: Change[]): Map<string, number> {
  const counts = new Map<string, number>()
  for (const c of changes) {
    const segs = c.path.split('/')
    for (let i = 0; i < segs.length - 1; i++) {
      const dir = segs.slice(0, i + 1).join('/')
      counts.set(dir, (counts.get(dir) ?? 0) + 1)
    }
    counts.set('', (counts.get('') ?? 0) + 1)
  }
  return counts
}

function isIgnored(path: string, ignored: Set<string>): boolean {
  if (ignored.has(path) || ignored.has(path + '/')) return true
  const segs = path.split('/')
  for (let i = 1; i < segs.length; i++) {
    if (ignored.has(segs.slice(0, i).join('/') + '/')) return true
  }
  return false
}

/**
 * The paths a filtered view draws, every directory on the way open: the changes alone,
 * and/or the files whose path holds `filter`. Undefined for the plain lazy tree.
 */
async function pathsFor(
  $: $,
  s: Scan,
  changedOnly: boolean,
  filter: string,
): Promise<{ paths: string[]; total: number; incomplete?: string } | undefined> {
  const needle = filter.trim().toLowerCase()
  if (!changedOnly && needle === '') return undefined
  let paths: string[]
  // Why the search may have missed files, when it may have.
  let incomplete: string | undefined
  if (changedOnly) paths = s.changes.map(c => c.path)
  else if (!s.isRepo) ({ files: paths, incomplete } = await listFiles($, s))
  else {
    const listed = await listFiles($, s)
    incomplete = listed.incomplete
    if (!incomplete && s.isIgnoredTruncated) incomplete = "git's list of ignored files passed 4 MB; searched its start only."
    // Ignored entries as the scan found them (a directory ends with `/`), so a filter narrows the
    // tree without dropping what it shows dimmed; an ignored directory matches by its own path.
    paths = [...new Set([...listed.files, ...s.changes.map(c => c.path), ...s.ignored])]
    // The files inside an ignored directory are not listed (a .venv can hold tens of thousands).
    if (needle !== '' && s.ignored.some(p => p.endsWith('/'))) {
      incomplete = [incomplete, 'Files inside ignored folders are not searched.'].filter(Boolean).join(' ')
    }
  }
  const hits = needle === '' ? paths : paths.filter(p => p.toLowerCase().includes(needle))
  return { paths: hits.slice(0, FILTER_LIMIT), total: hits.length, incomplete }
}

/** The workspace's files as last listed for a filter; each finished scan clears it (see rescan). */
let listing: { root: string; files: Promise<{ files: string[]; incomplete?: string }> } | undefined

/**
 * The files a filter searches, listed once per scan: a redraw (a wheel move) or a new
 * filter reuses the list, and `incomplete` says why it may lack some.
 */
function listFiles($: $, s: Scan): Promise<{ files: string[]; incomplete?: string }> {
  if (listing?.root !== s.root) listing = { root: s.root, files: listFilesNow($, s) }
  return listing.files
}

async function listFilesNow($: $, s: Scan): Promise<{ files: string[]; incomplete?: string }> {
  if (!s.isRepo) {
    const walked = await walkFiles($, s.root)
    const notes = [
      walked.isCapped && `Searched the first ${WALK_LIMIT} entries (files and folders) only.`,
      walked.unread === 1 && '1 folder could not be read and was not searched.',
      walked.unread > 1 && `${walked.unread} folders could not be read and were not searched.`,
    ]
    return { files: walked.files, incomplete: notes.filter(Boolean).join(' ') || undefined }
  }
  const listed = await git($, s.root, ['ls-files', '-z', '--cached', '--others', '--exclude-standard'])
  // Output past 4 MiB is cut: keep the whole names, and say the search stopped there.
  if (!listed.isStdoutTruncated) return { files: listed.stdout.split('\0').filter(Boolean) }
  return {
    files: listed.stdout.slice(0, listed.stdout.lastIndexOf('\0') + 1).split('\0').filter(Boolean),
    incomplete: "git's file list passed 4 MB; searched its start only.",
  }
}

/**
 * File paths under `root`, breadth first, discovering at most WALK_LIMIT files and directories.
 * `isCapped` says the walk stopped there, and `unread` counts the folders it could not list
 * (permissions, I/O), so a search over it may miss files.
 */
async function walkFiles($: $, root: string): Promise<{ files: string[]; isCapped: boolean; unread: number }> {
  const files: string[] = []
  const dirs = ['']
  let unread = 0
  let seen = 0
  let isCapped = false
  let i = 0
  for (; i < dirs.length && seen < WALK_LIMIT; i++) {
    const dir = dirs[i] as string
    const entries = await $.fs.list(root + (dir === '' ? '' : '/' + dir)).catch(() => {
      unread++
      return []
    })
    for (const en of entries) {
      if (HIDDEN.has(en.name)) continue
      if (seen === WALK_LIMIT) {
        isCapped = true
        break
      }
      seen++
      const path = dir === '' ? en.name : dir + '/' + en.name
      // A link is never walked into, so a link to an ancestor can't loop the walk. This host reports
      // one as `other`; the isLink check holds on a host that reports a linked folder as a `dir`.
      if (en.kind === 'dir' && !en.isLink) dirs.push(path)
      else files.push(path)
    }
  }
  return { files, isCapped: isCapped || i < dirs.length, unread }
}

async function buildRows(
  $: $,
  s: Scan,
  expanded: Set<string>,
  virtual: string[] | undefined,
): Promise<Row[]> {
  const byPath = new Map(s.changes.map(c => [c.path, c]))
  const counts = rollup(s.changes)
  const ignored = new Set(s.ignored)
  const rows: Row[] = []

  async function walk(dir: string, depth: number) {
    const prefix = dir === '' ? '' : dir + '/'
    const kids = new Map<string, { isDir: boolean; isMissing: boolean; hasKids: boolean }>()
    const source = virtual ?? s.changes.map(c => c.path)
    if (!virtual) {
      const entries = await $.fs.list(s.root + (dir === '' ? '' : '/' + dir)).catch(() => [])
      for (const en of entries) {
        if (HIDDEN.has(en.name)) continue
        kids.set(en.name, { isDir: en.kind === 'dir', isMissing: false, hasKids: false })
      }
    }
    // In the lazy tree, changes add what the disk no longer holds (deletions).
    for (const path of source) {
      if (!path.startsWith(prefix)) continue
      const rest = path.slice(prefix.length)
      const seg = rest.split('/')[0] ?? ''
      if (seg === '') continue
      // A directory path ending in `/` (an ignored one) is a leaf: drawn closed, nothing under it.
      const hasKids = rest.length > seg.length + 1
      const kid = kids.get(seg)
      if (kid) kid.hasKids ||= hasKids
      else {
        const isDir = rest.includes('/')
        const c = byPath.get(path)
        // A recreated file (`D?`) is back on disk: not drawn as gone.
        const isGone = !isDir && c !== undefined && !isRecreated(c) && (c.x === 'D' || c.y === 'D')
        kids.set(seg, { isDir, isMissing: virtual ? isGone : true, hasKids })
      }
    }
    const sorted = [...kids].sort(([a, ka], [b, kb]) =>
      ka.isDir !== kb.isDir ? (ka.isDir ? -1 : 1) : a.localeCompare(b, undefined, { sensitivity: 'base' }),
    )
    for (const [name, k] of sorted) {
      const path = prefix + name
      const isOpen = k.isDir && (virtual !== undefined ? k.hasKids : expanded.has(path))
      rows.push({
        path,
        name,
        depth,
        isDir: k.isDir,
        isOpen,
        change: byPath.get(path),
        count: counts.get(path) ?? 0,
        isIgnored: s.isRepo && isIgnored(path, ignored),
        isMissing: k.isMissing,
      })
      if (isOpen) await walk(path, depth + 1)
    }
  }

  await walk('', 0)
  return rows
}

type TreeView = { rows: Row[]; virtual: Awaited<ReturnType<typeof pathsFor>>; widest: number }
let treeCache: { scanKey: string; viewKey: string; view: Promise<TreeView> } | undefined

/** Scrolls reuse the prepared tree, including its filter and width, without listing directories. */
function cachedTree($: $, s: Scan, scanKey: string, expanded: string[], changedOnly: boolean, filter: string) {
  const viewKey = JSON.stringify([expanded, changedOnly, filter])
  if (treeCache?.scanKey !== scanKey || treeCache.viewKey !== viewKey) {
    treeCache = { scanKey, viewKey, view: prepareTree($, s, expanded, changedOnly, filter) }
  }
  return treeCache.view
}

async function prepareTree($: $, s: Scan, expanded: string[], changedOnly: boolean, filter: string): Promise<TreeView> {
  const virtual = await pathsFor($, s, changedOnly, filter)
  const rows = await buildRows($, s, new Set(expanded), virtual?.paths)
  const widest = rows.reduce((w, r) => Math.max(w, r.depth * 2 + r.name.length + 8), 0)
  return { rows, virtual, widest }
}

/** One body line of a unified diff, with the line numbers it stands at. */
export type DiffLine = { text: string; kind: ' ' | '+' | '-'; o: number; n: number; hunk: number }

/** Reads a unified diff's hunks into numbered lines; file headers are dropped. */
export function diffLines(diff: string): DiffLine[] {
  const out: DiffLine[] = []
  let o = 0
  let n = 0
  let hunk = -1
  for (const line of diff.split('\n')) {
    const head = /^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/.exec(line)
    if (head) {
      o = Number(head[1])
      n = Number(head[2])
      hunk++
      continue
    }
    const kind = line.charAt(0)
    if (hunk < 0 || (kind !== ' ' && kind !== '+' && kind !== '-')) continue
    out.push({ text: line, kind, o, n, hunk })
    if (kind !== '+') o++
    if (kind !== '-') n++
  }
  return out
}

/**
 * A file's parsed diff; `isTruncated` when git's output passed 4 MiB and only its start is here, and
 * `error` when git could not make it (an unreadable file).
 */
type FileDiff = {
  lines: DiffLine[]
  isTruncated: boolean
  error?: string
  counts: { added: number; deleted: number }
  width: number
  hunks: HunkStart[]
  rows: number
}

/** The open file's parsed diff and what it was read for, so a scroll redraws without running git. */
let diffCache: { scanKey: string; path: string; diff: Promise<FileDiff> } | undefined

/** The parsed diff of `c`, read again only when the scan changed (a content edit changes its stamp). */
function cachedDiff($: $, s: Scan, c: Change, scanKey: string): Promise<FileDiff> {
  if (diffCache?.scanKey !== scanKey || diffCache.path !== c.path) {
    // Cache the in-flight work too: overlapping redraws share one process and one parse.
    diffCache = { scanKey, path: c.path, diff: prepareDiff($, s, c) }
  }
  return diffCache.diff
}

async function prepareDiff($: $, s: Scan, c: Change): Promise<FileDiff> {
  const out = await diffFor($, s, c)
  const lines = diffLines(out.stdout)
  const counts = { added: 0, deleted: 0 }
  let largest = 0
  const hunks: HunkStart[] = []
  let rows = 0
  let previousHunk = -1
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] as DiffLine
    if (line.hunk !== previousHunk) {
      if (i > 0) rows++
      hunks.push({ line: i, row: rows })
      previousHunk = line.hunk
    }
    rows++
    if (line.kind === '+') counts.added++
    if (line.kind === '-') counts.deleted++
    largest = Math.max(largest, line.o, line.n)
  }
  const error = isDiffFailed(out) ? out.stderr.trim() || `git diff exited ${out.exitCode}` : undefined
  return { lines, counts, width: String(largest).length, hunks, rows, isTruncated: out.isStdoutTruncated, error }
}

type Preview = { lines: string[]; notice?: string; source?: string }
let previewCache: { scanKey: string; path: string; preview: Promise<Preview> } | undefined

function cachedPreview($: $, s: Scan, path: string, scanKey: string): Promise<Preview> {
  if (previewCache?.scanKey !== scanKey || previewCache.path !== path) {
    previewCache = { scanKey, path, preview: preparePreview($, s.root + '/' + path) }
  }
  return previewCache.preview
}

async function preparePreview($: $, path: string): Promise<Preview> {
  const stat = await $.fs.stat(path).catch(() => undefined)
  if (!stat || stat.kind !== 'file') return { lines: [], notice: 'Not a readable file.' }
  if (stat.size > PREVIEW_BYTES) return { lines: [], notice: `Too large to preview (${stat.size} bytes).` }
  const text = await $.fs.read(path).catch(() => undefined)
  if (text === undefined) return { lines: [], notice: 'Not a readable file.' }
  if (text.includes('\0')) return { lines: [], notice: 'Binary file.' }
  const lines = text === '' ? [] : text.split('\n')
  if (text.endsWith('\n')) lines.pop()
  // Most files can remain one Code instance with its full syntax context and natural line height.
  // Reserve half the drawing budget for the rest of the pane, counting JSON escaping too.
  const source = JSON.stringify(text).length <= FULL_PREVIEW_CHARS ? text : undefined
  return { lines, source }
}

async function diffFor($: $, s: Scan, c: Change) {
  const flags = ['--no-color', '--no-ext-diff']
  if (c.x === '?') {
    // --no-index exits 1 when the files differ, which is the point here.
    return git($, s.root, ['diff', ...flags, '--no-index', '--', '/dev/null', c.path])
  }
  if (isRecreated(c)) {
    const net = await recreatedDiff($, s.root, await diffBase($, s.root), c.path, flags)
    if (net !== undefined && net !== 'cut') return net
    const contents = await git($, s.root, ['diff', ...flags, '--no-index', '--', '/dev/null', c.path])
    // Its committed version too large to diff against: the new contents alone, marked incomplete.
    return net === 'cut' ? { ...contents, isStdoutTruncated: true } : contents
  }
  const paths = c.from ? [c.from, c.path] : [c.path]
  return git($, s.root, ['diff', ...flags, '-M', await diffBase($, s.root), '--', ...paths])
}

const FOLDER_ICON =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path d="M1.5 3.5h4.5l1.5 1.5h7v8.5h-13z" fill="#c9a24a"/></svg>'
const EMPTY_ICON =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#8c8c8c" stroke-width="1.5"><path d="M3 6.5h6l2 2h10v10.5H3z"/></svg>'

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await $.command.register({
      name: 'git-files',
      description: 'Open the git-aware file explorer pane',
    })
    await rescan($)
    $.clock.every(SCAN_EVERY_MS, () => void rescan($))
    void $.ui.open({ id: PANE, title: TITLE }).then(() => settle($))
    return started
  })

  on('command.run', { command: 'git-files' }, async $ => {
    await rescan($)
    await $.ui.open({ id: PANE, title: TITLE, focus: true })
    await settle($)
    return { text: 'Files pane opened.' }
  })

  on('tool.call', async ($, e, next) => {
    const result = await next(e)
    if (WRITERS.has(String(e.tool))) void rescan($)
    return result
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const els = $.ui.resolve(e)
    const { Box, Text, Button, Code } = els
    const space = (key: string, height: number) => height <= 10000
      ? <Box key={key} height={height} flexShrink={0} />
      : <Box key={key} flexDirection="column" flexShrink={0}>
          {spacerHeights(height).map((part, i) => <Box key={key + ':' + i} height={part} flexShrink={0} />)}
        </Box>
    const Input = 'Input' in els ? els.Input : undefined
    const Svg = 'Svg' in els ? els.Svg : undefined
    // A pane drawn before the first scan landed scans for itself; only handlers and timers write.
    const s = (await read($, scanAtom)) ?? (await scan($))
    const expanded = await read($, expandedAtom)
    const selected = await read($, selectedAtom)
    const changedOnly = await read($, changedOnlyAtom)
    const filter = await read($, filterAtom)

    const scanKey = JSON.stringify(s)
    const { rows, virtual, widest } = await cachedTree($, s, scanKey, expanded, changedOnly, filter)
    const change = selected === null ? undefined : s.changes.find(c => c.path === selected)
    const bodyRows = e.props.scroll.bodyRows > 0 ? e.props.scroll.bodyRows : 30
    const offset = e.props.scroll.offset
    const n = s.changes.length

    // The tree column fits its widest row, up to half the pane; the file panel takes the rest.
    const half = Math.floor(e.props.bodyColumns / 2)
    const treeColumns = Math.max(Math.min(TREE_MIN_COLUMNS, half), Math.min(widest, half))

    const toggleDir = (path: string) =>
      update($, expandedAtom, list =>
        list.includes(path) ? list.filter(p => p !== path && !p.startsWith(path + '/')) : [...list, path],
      )
    const toTop = () => settle($)
    const setFilter = (value: string) => update($, filterAtom, () => value).then(toTop)
    const select = (path: string) =>
      update($, selectedAtom, cur => (cur === path ? null : path)).then(toTop)

    // Across the whole pane: the branch on the left 70%, the change counts right-aligned in the rest.
    const branchBar = (
      <Box key="branch-bar" flexDirection="row" alignItems="center">
        <Box width="70%" flexShrink={1}>
          <Text wrap="truncate-end">
            {s.isRepo ? (
              <Text color="suggestion">⎇ {s.branch ?? '?'}</Text>
            ) : s.error !== undefined ? (
              <Text color="error">git unavailable</Text>
            ) : (
              <Text dimColor>not a git repo</Text>
            )}
          </Text>
        </Box>
        <Box width="30%" flexDirection="row" justifyContent="flex-end" alignItems="center" columnGap={1}>
          {s.isRepo && n > 0 && s.lines && (
            <Text>
              {/* A trailing + marks a floor: some untracked files went uncounted, or git's output was cut. */}
              <Text color="success">
                +{s.lines.added}
                {s.lines.partial || s.lines.isTruncated || s.isTruncated ? '+' : ''}
              </Text>{' '}
              <Text color="error">
                −{s.lines.deleted}
                {s.lines.isTruncated || s.isTruncated ? '+' : ''}
              </Text>
            </Text>
          )}
          {s.isRepo && s.error !== undefined && <Text color="error">status unavailable</Text>}
          {s.isRepo && s.error === undefined && (
            <Button key="changes" plain onPress={() => update($, changedOnlyAtom, v => !v).then(toTop)}>
              {n === 0 ? (
                <Text dimColor>clean</Text>
              ) : (
                <Text color="warning" underline={changedOnly}>
                  ● {n}
                  {s.isTruncated ? '+' : ''} changed
                </Text>
              )}
            </Button>
          )}
        </Box>
      </Box>
    )

    const search = (
      <Box flexDirection="row" alignItems="center" columnGap={2}>
        {Input && (
          <Box flexGrow={1} flexShrink={1}>
            <Input
              key="filter"
              placeholder={changedOnly ? 'Filter changed files' : 'Filter files'}
              value={filter}
              onInput={value => void setFilter(value)}
              onSubmit={value => void setFilter(value)}
            />
          </Box>
        )}
        <Button key="refresh" plain onPress={() => rescan($)}>
          <Text dimColor>↻</Text>
        </Button>
        <Button key="collapse" plain onPress={() => update($, expandedAtom, () => []).then(toTop)}>
          <Text dimColor>⊟</Text>
        </Button>
      </Box>
    )

    // Only the rows near the native viewport are elements. Equal-height spacers retain the full
    // layout extent, so redrawing never shifts the scroll position or pins a column over it.
    const treeWindow = nativeWindow(rows.length, offset - BRANCH_ROWS - 3, bodyRows, TREE_ROW_ROWS)
    const tree = (
      <Box flexDirection="column">
        {treeWindow.before > 0 && space('tree-before', treeWindow.before)}
        {rows.length === 0 && (
          <Text dimColor>{filter.trim() !== '' ? 'No matching files.' : changedOnly ? 'No changes.' : 'Empty directory.'}</Text>
        )}
        {rows.slice(treeWindow.start, treeWindow.end).map(r => {
          const b = r.change ? badge(r.change) : undefined
          const color = b?.color ?? (r.isDir && r.count > 0 ? 'warning' : undefined)
          const press = () => (r.isDir ? toggleDir(r.path) : select(r.path))
          return (
            <Box
              key={'row:' + r.path}
              flexDirection="row"
              justifyContent="space-between"
              alignItems="center"
              paddingX={1}
              height={TREE_ROW_ROWS}
              flexShrink={0}
              backgroundColor={r.path === selected ? SELECTED_BG : undefined}
              hover={{ backgroundColor: HOVER_BG }}
            >
              <Box flexDirection="row" alignItems="center" columnGap={1} flexShrink={1}>
                {r.depth > 0 && <Text>{'  '.repeat(r.depth)}</Text>}
                <Button key={'chevron:' + r.path} plain onPress={press}>
                  <Text size="heading" dimColor>
                    {r.isDir ? (r.isOpen ? '⌄' : '›') : ' '}
                  </Text>
                </Button>
                {Svg && (
                  <Svg
                    source={r.isDir ? FOLDER_ICON : iconFor(r.name)}
                    alt={r.isDir ? 'folder' : 'file'}
                    width={16}
                    height={16}
                  />
                )}
                <Button key={'node:' + r.path} plain onPress={press}>
                  <Text color={color} dimColor={r.isIgnored} strikethrough={r.isMissing} wrap="truncate-end">
                    {r.name}
                  </Text>
                </Button>
              </Box>
              {b ? (
                <Text color={b.color}>{b.letter}</Text>
              ) : r.isDir && r.count > 0 ? (
                <Text color="warning" dimColor>
                  ●
                </Text>
              ) : null}
            </Box>
          )
        })}
        {treeWindow.after > 0 && space('tree-after', treeWindow.after)}
        {virtual && virtual.total > virtual.paths.length && (
          <Text dimColor>
            Showing {virtual.paths.length} of {virtual.total} matches.
          </Text>
        )}
        {virtual?.incomplete && <Text dimColor>{virtual.incomplete}</Text>}
      </Box>
    )

    const panelColumns = Math.max(1, e.props.bodyColumns - treeColumns - GUTTER)
    let body
    let fileLines: { added: number; deleted: number } | undefined
    let isDiffTruncated = false
    if (selected === null) {
      body = (
        <Box flexDirection="column" flexGrow={1} alignItems="center" justifyContent="center" rowGap={1}>
          {Svg && <Svg alt="folder" width={28} height={28} source={EMPTY_ICON} />}
          <Text>Open files appear here</Text>
          <Text dimColor>Changed files open as a diff, the rest as a preview.</Text>
        </Box>
      )
    } else if (change) {
      const diff = await cachedDiff($, s, change, scanKey)
      const lines = diff.lines
      isDiffTruncated = diff.isTruncated
      if (diff.error !== undefined) body = <Text color="error">{diff.error}</Text>
      else if (lines.length === 0) body = <Text dimColor>No textual difference (binary or mode change).</Text>
      else {
        const view = nativeWindow(diff.rows, offset - BRANCH_ROWS - 2, bodyRows)
        const width = diff.width
        const pad = (no: number | undefined) => (no === undefined ? '' : String(no)).padStart(width)
        // Each line is a row of its own, tinted by kind; a gap between hunks costs a separator row.
        const drawn = []
        for (let row = view.start; row < view.end; row++) {
          const i = diffIndex(diff.hunks, row)
          if (i === undefined) {
            drawn.push(
              <Box key={'gap:' + row} height={1} flexShrink={0}>
                <Text mono dimColor>{' '.repeat(width * 2 + 2)}⋯</Text>
              </Box>,
            )
            continue
          }
          const l = lines[i] as DiffLine
          const tint = l.kind === '+' ? ADDED : l.kind === '-' ? DELETED : undefined
          drawn.push(
            <Box key={'line:' + i} height={1} flexShrink={0} flexDirection="row" backgroundColor={tint?.bg}>
              <Text mono color={tint?.fg} dimColor={!tint}>
                {pad(l.kind === '+' ? undefined : l.o)} {pad(l.kind === '-' ? undefined : l.n)}{' '}
              </Text>
              <Text mono color={tint?.fg}>
                {l.kind === ' ' ? ' ' : l.kind}{' '}
              </Text>
              <Text mono color={tint?.fg} wrap="truncate-end">
                {visibleText(l.text.slice(1), panelColumns, view.end - view.start) || ' '}
              </Text>
            </Box>,
          )
        }
        fileLines = diff.counts
        body = (
          <Box key="diff-body" flexDirection="column">
            {view.before > 0 && space('diff-before', view.before)}
            {drawn}
            {view.after > 0 && space('diff-after', view.after)}
          </Box>
        )
      }
    } else {
      const preview = await cachedPreview($, s, selected, scanKey)
      if (preview.notice !== undefined) body = <Text dimColor>{preview.notice}</Text>
      else if (preview.source !== undefined) {
        body = <Code key="preview" source={preview.source} path={selected} startLine={1} wrap="truncate-end" />
      } else {
        const lines = preview.lines
        const view = previewWindow(lines.length, offset - BRANCH_ROWS - 2, bodyRows)
        const blocks = []
        for (let start = view.start; start < view.end; start += PREVIEW_BLOCK_ROWS) {
          const end = Math.min(lines.length, start + PREVIEW_BLOCK_ROWS)
          blocks.push(
            <Box key={'preview-block:' + start} height={end - start} flexShrink={0} overflow="hidden">
              <Code
                key={'preview:' + start}
                source={lines.slice(start, end)
                  .map(line => visibleText(line, panelColumns, previewCapacity(bodyRows))).join('\n')}
                path={selected}
                startLine={start + 1}
                wrap="truncate-end"
              />
            </Box>,
          )
        }
        body = (
          <Box key="preview-body" flexDirection="column">
            {view.before > 0 && space('preview-before', view.before)}
            {blocks}
            {view.after > 0 && space('preview-after', view.after)}
          </Box>
        )
      }
    }
    const slash = selected === null ? -1 : selected.lastIndexOf('/')
    const panel = (
      <Box
        key="file-panel"
        width={panelColumns}
        minHeight={Math.max(0, bodyRows - BRANCH_ROWS)}
        flexShrink={0}
        flexDirection="column"
        rowGap={1}
      >
        {selected !== null && (
          <Box flexDirection="row" justifyContent="space-between" alignItems="center" columnGap={1}>
            <Text wrap="truncate-start">
              <Text bold>{selected.slice(slash + 1)}</Text>
              {slash > 0 && <Text dimColor> {selected.slice(0, slash)}</Text>}
              {change ? (
                <Text color={badge(change).color}>
                  {' '}
                  · {change.from ? `from ${change.from}, ` : ''}
                  {stageNote(change)}
                </Text>
              ) : (
                <Text dimColor> · unchanged</Text>
              )}
            </Text>
            <Box flexDirection="row" columnGap={2} alignItems="center">
              {fileLines && (
                <Text>
                  {/* A cut diff's counts are floors, as the branch bar marks them. */}
                  {isDiffTruncated && <Text dimColor>cut at 4 MB </Text>}
                  <Text color="success">
                    +{fileLines.added}
                    {isDiffTruncated ? '+' : ''}
                  </Text>{' '}
                  <Text color="error">
                    −{fileLines.deleted}
                    {isDiffTruncated ? '+' : ''}
                  </Text>
                </Text>
              )}
              <Button key="close-panel" plain role="dismiss" onPress={() => update($, selectedAtom, () => null)}>
                <Text dimColor>✕</Text>
              </Button>
            </Box>
          </Box>
        )}
        {body}
      </Box>
    )

    return (
      <Box key="native-pane" flexDirection="column" rowGap={1}>
        {branchBar}
        <Box key="columns" flexDirection="row" columnGap={GUTTER} alignItems="flex-start">
          <Box flexDirection="column" rowGap={1} width={treeColumns} flexShrink={0}>
            {search}
            {s.error && <Text color="error">{s.error}</Text>}
            {tree}
          </Box>
          {panel}
        </Box>
      </Box>
    )
  })
}

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Change, Scan } from '../types'

const PANE = 'git-aware-file-explorer'
const TITLE = 'Files'
const SCAN_EVERY_MS = 5000
const PREVIEW_BYTES = 256 * 1024
/** Most matches a filter lists; the rest are counted, not drawn. */
const FILTER_LIMIT = 300
/** Paths a filter outside a git repository walks the disk for, at most. */
const WALK_LIMIT = 20000
/** The tree column's narrowest width, in cells; its widest is half the pane. */
const TREE_MIN_COLUMNS = 34
/** Cells between the tree column and the file panel. */
const GUTTER = 2
/** Rows the branch bar takes above both sides: its line and the gap under it. */
const BRANCH_ROWS = 2
/**
 * The desktop raises no wheel event for a window that cannot move, and moves the window a row
 * before a hook answers. So the pane's window rests over a blank spacer row above the branch bar
 * only while the tree or the file can scroll up, and has a spare row below only while the file can
 * scroll down (a long tree makes its own): at a limit the window has nowhere to go, and nothing
 * bounces. The mod moves the tree or the file panel itself.
 */
const ROOM = 1
/** Tools whose calls can change the work tree; a scan follows each. */
const WRITERS = new Set(['Edit', 'MultiEdit', 'Write', 'NotebookEdit', 'Bash'])
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
const panelOffsetAtom = atom({ plugin: 'git-aware-file-explorer', key: 'panelOffset' } as const, 0)
const treeOffsetAtom = atom({ plugin: 'git-aware-file-explorer', key: 'treeOffset' } as const, 0)

type $ = EngineInterface

/**
 * What the last drawing laid out, for the scroll hook to tell the two sides apart.
 * A module variable on purpose: it is layout, redrawn on every render, not state.
 */
const layout = {
  treeColumns: 0,
  panelLast: 0,
  panelRoom: 0,
  hasFile: false,
  offset: 0,
  spacer: 0,
  spare: 0,
  /** A wheel event has carried a pointer, so the wheel reaches the tree while a file is open. */
  hasPointer: false,
}

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
 * `git diff` (with `flags`) of a recreated path: its version in `base`, piped in, against the file
 * on disk, so the panel and the totals see the net change. `'cut'` when that version passed 4 MiB
 * and can't be piped whole; undefined when git can't run it so.
 */
async function recreatedDiff($: $, root: string, base: string, path: string, flags: string[]) {
  const old = await git($, root, ['show', base + ':' + path])
  if (old.isStdoutTruncated) return 'cut' as const
  if (old.exitCode !== 0) return undefined
  // --no-index exits 1 when the files differ, which is the point here.
  const out = await git($, root, ['diff', ...flags, '--no-index', '--', '/dev/stdin', path], old.stdout)
  return out.exitCode <= 1 ? out : undefined
}

async function scan($: $): Promise<Scan> {
  const cwd = await $.session.cwd()
  try {
    const top = await $.process.run(['git', 'rev-parse', '--show-toplevel'], { cwd })
    if (top.exitCode !== 0) return { root: cwd, isRepo: false, changes: [], ignored: [] }
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
      error: status.exitCode === 0 ? undefined : status.stderr.trim(),
    }
  } catch (err) {
    return { root: cwd, isRepo: false, changes: [], ignored: [], error: String(err) }
  }
}

/** Sums `git diff --numstat` output; binary files (`-`) count no lines. */
export function sumNumstat(out: string): { added: number; deleted: number } {
  let added = 0
  let deleted = 0
  for (const line of out.split('\n')) {
    const [a, d] = line.split('\t')
    if (a && /^\d+$/.test(a)) added += Number(a)
    if (d && /^\d+$/.test(d)) deleted += Number(d)
  }
  return { added, deleted }
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
  const out = await git($, root, ['diff', '--numstat', '--no-ext-diff', base])
  // A recreated path counts its net change, in place of the deletion the diff against base reports.
  let numstat = out.stdout
  let isUncounted = false
  let isCut = false
  for (const c of changes.filter(isRecreated)) {
    const net = await recreatedDiff($, root, base, c.path, ['--numstat'])
    if (net === undefined) {
      isUncounted = true
      continue
    }
    const others = numstat.split('\n').filter(line => line.split('\t')[2] !== c.path).join('\n')
    // Too large to diff: neither its deletion nor its contents count, and both totals are floors.
    if (net === 'cut') isCut = true
    numstat = net === 'cut' ? others : others + '\n' + net.stdout
  }
  const total: { added: number; deleted: number; partial?: boolean; isTruncated?: boolean } = sumNumstat(numstat)
  if (out.isStdoutTruncated || isCut) total.isTruncated = true
  if (isUncounted) total.partial = true
  const untracked = changes.filter(c => c.x === '?')
  if (untracked.length > UNTRACKED_LIMIT) total.partial = true
  for (const c of untracked.slice(0, UNTRACKED_LIMIT)) {
    const path = root + '/' + c.path
    const stat = await $.fs.stat(path).catch(() => undefined)
    if (!stat || stat.kind !== 'file') continue
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
        // Any write redraws the pane, so an unchanged scan is not written at all.
        if (JSON.stringify(await read($, scanAtom)) !== JSON.stringify(next)) await update($, scanAtom, () => next)
      } while (isRescanDue)
    } finally {
      scanning = undefined
    }
  })()
  return scanning
}

/** Scrolls the pane's window back so the branch bar is at its top, where it rests (see ROOM). */
async function settle($: $) {
  await $.ui.scroll({ to: { key: 'branch-bar' }, in: PANE, block: 'start' }).catch(() => undefined)
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
  else if (!s.isRepo) {
    const walked = await walkFiles($, s.root)
    paths = walked.files
    if (walked.isCapped) incomplete = `Searched the first ${WALK_LIMIT} files only.`
  } else {
    const listed = await git($, s.root, ['ls-files', '-z', '--cached', '--others', '--exclude-standard'])
    // Output past 4 MiB is cut: keep the whole names, and say the search stopped there.
    let names = listed.stdout
    if (listed.isStdoutTruncated) {
      names = names.slice(0, names.lastIndexOf('\0') + 1)
      incomplete = "git's file list passed 4 MB; searched its start only."
    } else if (s.isIgnoredTruncated) incomplete = "git's list of ignored files passed 4 MB; searched its start only."

    // Ignored entries as the scan found them (a directory ends with `/`), so a filter narrows the
    // tree without dropping what it shows dimmed; an ignored directory matches by its own path.
    paths = [...new Set([...names.split('\0').filter(Boolean), ...s.changes.map(c => c.path), ...s.ignored])]
  }
  const hits = needle === '' ? paths : paths.filter(p => p.toLowerCase().includes(needle))
  return { paths: hits.slice(0, FILTER_LIMIT), total: hits.length, incomplete }
}

/**
 * File paths under `root`, breadth first, up to WALK_LIMIT: what a filter searches without git.
 * `isCapped` says the walk stopped there, so a search over it may miss files.
 */
async function walkFiles($: $, root: string): Promise<{ files: string[]; isCapped: boolean }> {
  const files: string[] = []
  const dirs = ['']
  let i = 0
  for (; i < dirs.length && files.length < WALK_LIMIT; i++) {
    const dir = dirs[i] as string
    const entries = await $.fs.list(root + (dir === '' ? '' : '/' + dir)).catch(() => [])
    for (const en of entries) {
      if (HIDDEN.has(en.name)) continue
      const path = dir === '' ? en.name : dir + '/' + en.name
      // A link is never walked into, so a link to an ancestor can't loop the walk. This host reports
      // one as `other`; the isLink check holds on a host that reports a linked folder as a `dir`.
      if (en.kind === 'dir' && !en.isLink) dirs.push(path)
      else files.push(path)
    }
  }
  return { files: files.slice(0, WALK_LIMIT), isCapped: files.length > WALK_LIMIT || i < dirs.length }
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
        const isGone = !isDir && (c?.x === 'D' || c?.y === 'D')
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

/** One body line of a unified diff, with the line numbers it stands at. */
export type DiffLine = { text: string; kind: ' ' | '+' | '-'; o: number; n: number; hunk: number }

/**
 * Whether something the wheel can move can still go up, so the window keeps a row of room above
 * (see ROOM). Without a pointer the wheel moves the open file alone; with one it reaches the tree too.
 */
export function canGoUp(at: { hasFile: boolean; hasPointer: boolean; panelOffset: number; treeOffset: number }) {
  return (at.hasFile && at.panelOffset > 0) || ((!at.hasFile || at.hasPointer) && at.treeOffset > 0)
}

/**
 * The furthest a diff's window can start and still show its last line in `room` rows, counting
 * the separator row drawn between two hunks.
 */
export function lastTop(lines: DiffLine[], room: number): number {
  let used = 0
  for (let i = lines.length - 1; i >= 0; i--) {
    used += 1 + (i < lines.length - 1 && lines[i]?.hunk !== lines[i + 1]?.hunk ? 1 : 0)
    if (used > room) return i + 1
  }
  return 0
}

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

/** A file's parsed diff; `isTruncated` when git's output passed 4 MiB and only its start is here. */
type FileDiff = { lines: DiffLine[]; isTruncated: boolean }

/** The open file's parsed diff and what it was read for, so a scroll redraws without running git. */
let diffCache: { key: string; diff: FileDiff } | undefined

/** The parsed diff of `c`, read again only when the scan changed (a content edit changes its stamp). */
async function cachedDiff($: $, s: Scan, c: Change): Promise<FileDiff> {
  const key = JSON.stringify([s, c])
  if (diffCache?.key !== key) {
    const out = await diffFor($, s, c)
    diffCache = { key, diff: { lines: diffLines(out.stdout), isTruncated: out.isStdoutTruncated } }
  }
  return diffCache.diff
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

  // The pane's window stays at rest (see ROOM), so the branch bar and the filter stay put: the wheel
  // moves the open file's lines, or the tree's rows when the pointer is over the tree or no file is open.
  on('ui.scroll', { component: 'Pane', requestId: PANE }, async ($, e, next) => {
    if (e.origin.kind === 'plugin') return next(e)
    if (e.pointer) layout.hasPointer = true
    // A surface that reports no pointer (the desktop, keys) scrolls the panel whenever a file is open.
    const isOverPanel = e.pointer ? e.pointer.column >= layout.treeColumns + GUTTER : true
    let moved: number
    if (layout.hasFile && isOverPanel) {
      moved = Math.min(layout.panelLast, Math.max(0, (await read($, panelOffsetAtom)) + e.by))
      await update($, panelOffsetAtom, () => moved)
    } else {
      // The tree rows hidden below the window are as far as it can move down; a tree row is at least one.
      const below = Math.max(0, e.contentRows - e.bodyRows - layout.spacer - layout.spare)
      moved = Math.max(0, (await read($, treeOffsetAtom)) + Math.min(e.by, below))
      await update($, treeOffsetAtom, () => moved)
    }
    const isRoomAbove = canGoUp({
      hasFile: layout.hasFile,
      hasPointer: layout.hasPointer,
      panelOffset: await read($, panelOffsetAtom),
      treeOffset: await read($, treeOffsetAtom),
    })
    const rest = isRoomAbove ? ROOM : 0
    return layout.offset === rest ? {} : next({ ...e, offset: rest })
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    /** Moves the file panel's window by `by` lines, kept within the file. */
    const scrollPanel = (by: number) =>
      update($, panelOffsetAtom, cur => Math.min(layout.panelLast, Math.max(0, cur + by)))

    const els = $.ui.resolve(e)
    const { Box, Text, Button, Code } = els
    const Input = 'Input' in els ? els.Input : undefined
    const Svg = 'Svg' in els ? els.Svg : undefined
    // A pane drawn before the first scan landed scans for itself; only handlers and timers write.
    const s = (await read($, scanAtom)) ?? (await scan($))
    const expanded = await read($, expandedAtom)
    const selected = await read($, selectedAtom)
    const changedOnly = await read($, changedOnlyAtom)
    const filter = await read($, filterAtom)
    const panelOffset = await read($, panelOffsetAtom)
    const treeOffsetSet = await read($, treeOffsetAtom)

    const virtual = await pathsFor($, s, changedOnly, filter)
    const rows = await buildRows($, s, new Set(expanded), virtual?.paths)
    // The tree draws from its first visible row down; the window clips the rest.
    const treeOffset = Math.min(treeOffsetSet, Math.max(0, rows.length - 1))
    const change = selected === null ? undefined : s.changes.find(c => c.path === selected)
    const bodyRows = e.props.scroll.bodyRows > 0 ? e.props.scroll.bodyRows : 30
    const n = s.changes.length

    // The tree column fits its widest row, up to half the pane; the file panel takes the rest.
    const widest = rows.reduce((w, r) => Math.max(w, r.depth * 2 + r.name.length + 8), 0)
    const half = Math.floor(e.props.bodyColumns / 2)
    const treeColumns = Math.max(Math.min(TREE_MIN_COLUMNS, half), Math.min(widest, half))

    const toggleDir = (path: string) =>
      update($, expandedAtom, list =>
        list.includes(path) ? list.filter(p => p !== path && !p.startsWith(path + '/')) : [...list, path],
      )
    // A new filter, view or collapse redraws the tree from its first row.
    const toTreeTop = () => update($, treeOffsetAtom, () => 0)
    const setFilter = (value: string) => update($, filterAtom, () => value).then(toTreeTop)
    const select = (path: string) =>
      update($, selectedAtom, cur => (cur === path ? null : path)).then(() => update($, panelOffsetAtom, () => 0))

    // Across the whole pane: the branch on the left 70%, the change counts right-aligned in the rest.
    const branchBar = (
      <Box key="branch-bar" flexDirection="row" alignItems="center">
        <Box width="70%" flexShrink={1}>
          <Text wrap="truncate-end">
            {s.isRepo ? <Text color="suggestion">⎇ {s.branch ?? '?'}</Text> : <Text dimColor>not a git repo</Text>}
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
          {s.isRepo && (
            <Button key="changes" plain onPress={() => update($, changedOnlyAtom, v => !v).then(toTreeTop)}>
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
        <Button key="collapse" plain onPress={() => update($, expandedAtom, () => []).then(toTreeTop)}>
          <Text dimColor>⊟</Text>
        </Button>
      </Box>
    )

    const tree = (
      <Box flexDirection="column">
        {rows.length === 0 && (
          <Text dimColor>{filter.trim() !== '' ? 'No matching files.' : changedOnly ? 'No changes.' : 'Empty directory.'}</Text>
        )}
        {rows.slice(treeOffset).map(r => {
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
              paddingY="xs"
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
        {virtual && virtual.total > virtual.paths.length && (
          <Text dimColor>
            Showing {virtual.paths.length} of {virtual.total} matches.
          </Text>
        )}
        {virtual?.incomplete && <Text dimColor>{virtual.incomplete}</Text>}
      </Box>
    )

    // The file panel is pinned over the pane's window: it moves down as the tree scrolls,
    // so it stays in view, and scrolls its own content through panelOffset.
    const panelRoom = Math.max(4, bodyRows - BRANCH_ROWS - 3)
    // The first line the panel can start at and still end on the file's last line.
    let panelLast = 0
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
      const diff = await cachedDiff($, s, change)
      const lines = diff.lines
      isDiffTruncated = diff.isTruncated
      panelLast = lastTop(lines, panelRoom)
      if (lines.length === 0) body = <Text dimColor>No textual difference (binary or mode change).</Text>
      else {
        const top = Math.min(panelOffset, panelLast)
        const width = String(Math.max(...lines.map(l => Math.max(l.o, l.n)))).length
        const pad = (no: number | undefined) => (no === undefined ? '' : String(no)).padStart(width)
        // Each line is a row of its own, tinted by kind; a gap between hunks costs a separator row.
        const drawn = []
        for (let i = top, used = 0; i < lines.length; i++) {
          const l = lines[i] as DiffLine
          const tint = l.kind === '+' ? ADDED : l.kind === '-' ? DELETED : undefined
          const gap = i > top && lines[i - 1]?.hunk !== l.hunk
          if (used + (gap ? 2 : 1) > panelRoom) break
          if (gap) {
            drawn.push(
              <Text key={'gap:' + i} mono dimColor>
                {' '.repeat(width * 2 + 2)}⋯
              </Text>,
            )
            used++
          }
          drawn.push(
            <Box key={'line:' + i} flexDirection="row" backgroundColor={tint?.bg}>
              <Text mono color={tint?.fg} dimColor={!tint}>
                {pad(l.kind === '+' ? undefined : l.o)} {pad(l.kind === '-' ? undefined : l.n)}{' '}
              </Text>
              <Text mono color={tint?.fg}>
                {l.kind === ' ' ? ' ' : l.kind}{' '}
              </Text>
              <Text mono color={tint?.fg} wrap="truncate-end">
                {l.text.slice(1) || ' '}
              </Text>
            </Box>,
          )
          used++
        }
        fileLines = {
          added: lines.filter(l => l.kind === '+').length,
          deleted: lines.filter(l => l.kind === '-').length,
        }
        body = <Box flexDirection="column">{drawn}</Box>
      }
    } else {
      const stat = await $.fs.stat(s.root + '/' + selected).catch(() => undefined)
      if (!stat || stat.kind !== 'file') body = <Text dimColor>Not a readable file.</Text>
      else if (stat.size > PREVIEW_BYTES) body = <Text dimColor>Too large to preview ({stat.size} bytes).</Text>
      else {
        // A read that fails (permissions, I/O) is not an empty file.
        const text = await $.fs.read(s.root + '/' + selected).catch(() => undefined)
        if (text === undefined) body = <Text dimColor>Not a readable file.</Text>
        else if (text.includes('\0')) body = <Text dimColor>Binary file.</Text>
        else {
          const lines = text.split('\n')
          panelLast = Math.max(0, lines.length - panelRoom)
          const top = Math.min(panelOffset, panelLast)
          body = (
            <Code
              key="preview"
              source={lines.slice(top, top + panelRoom).join('\n')}
              path={selected}
              startLine={top + 1}
              wrap="truncate-end"
            />
          )
        }
      }
    }
    const offset = e.props.scroll.offset
    // Room above while what the wheel moves can go up; a window still below that rest is matched, so
    // the branch bar stays at its top until the next wheel move brings it to rest.
    const isRoomAbove = canGoUp({ hasFile: selected !== null, hasPointer: layout.hasPointer, panelOffset, treeOffset })
    const spacer = Math.max(isRoomAbove ? ROOM : 0, offset)
    const spare = selected !== null && panelOffset < panelLast ? ROOM : 0
    Object.assign(layout, { treeColumns, panelLast, panelRoom, hasFile: selected !== null, offset, spacer, spare })

    const slash = selected === null ? -1 : selected.lastIndexOf('/')
    // Under the branch bar, down to the bottom of the pane's window.
    const panel = (
      <Box
        position="absolute"
        top={BRANCH_ROWS + Math.max(0, offset - spacer)}
        left={treeColumns + GUTTER}
        right={0}
        height={bodyRows - BRANCH_ROWS - Math.max(0, spacer - offset)}
        overflow="hidden"
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
              {layout.hasFile && (
                <Box flexDirection="row" columnGap={1}>
                  <Button key="line-up" plain onPress={() => scrollPanel(-1)}>
                    <Text dimColor>▲</Text>
                  </Button>
                  <Button key="line-down" plain onPress={() => scrollPanel(1)}>
                    <Text dimColor>▼</Text>
                  </Button>
                </Box>
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
      <Box flexDirection="column">
        {spacer > 0 && <Box key="spacer" height={spacer} />}
        {/* With a file open the wheel moves the file, so the tree below the window is clipped, not scrolled to. */}
        <Box
          flexDirection="column"
          rowGap={1}
          minHeight={bodyRows}
          height={selected !== null ? bodyRows : undefined}
          overflow={selected !== null ? 'hidden' : undefined}
        >
          {branchBar}
          <Box flexDirection="column" rowGap={1} width={treeColumns} flexShrink={0}>
            {search}
            {s.error && <Text color="error">{s.error}</Text>}
            {tree}
          </Box>
          {panel}
        </Box>
        {spare > 0 && <Box key="spare" height={spare} />}
      </Box>
    )
  })
}

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Change, Scan } from '../types'

const PANE = 'git-aware-file-explorer'
const TITLE = 'Files'
const SCAN_EVERY_MS = 5000
const PREVIEW_BYTES = 256 * 1024
/** Most matches a filter lists; the rest are counted, not drawn. */
const FILTER_LIMIT = 300
/** The tree column's narrowest width, in cells; its widest is half the pane. */
const TREE_MIN_COLUMNS = 34
/** Cells between the tree column and the file panel. */
const GUTTER = 2
/** Tools whose calls can change the work tree; a scan follows each. */
const WRITERS = new Set(['Edit', 'MultiEdit', 'Write', 'NotebookEdit', 'Bash'])
/** Files the native Files pane leaves out too. */
const HIDDEN = new Set(['.git', '.DS_Store', 'Thumbs.db'])
/** Row tints: a neutral grey with alpha reads in both light and dark themes. */
const SELECTED_BG = '#8080803a'
const HOVER_BG = '#8080801f'

const scanAtom = atom({ plugin: 'git-aware-file-explorer', key: 'scan' } as const, null)
const expandedAtom = atom({ plugin: 'git-aware-file-explorer', key: 'expanded' } as const, [])
const selectedAtom = atom({ plugin: 'git-aware-file-explorer', key: 'selected' } as const, null)
const changedOnlyAtom = atom({ plugin: 'git-aware-file-explorer', key: 'changedOnly' } as const, false)
const filterAtom = atom({ plugin: 'git-aware-file-explorer', key: 'filter' } as const, '')
const panelOffsetAtom = atom({ plugin: 'git-aware-file-explorer', key: 'panelOffset' } as const, 0)

type $ = EngineInterface

/**
 * What the last drawing laid out, for the scroll hook to tell the two sides apart.
 * A module variable on purpose: it is layout, redrawn on every render, not state.
 */
const layout = { treeColumns: 0, panelLines: 0, panelRoom: 0, hasFile: false }

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

/** Splits `git status --porcelain=v1 -z` output into changes. */
export function parseStatus(out: string): Change[] {
  const parts = out.split('\0')
  const changes: Change[] = []
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i] ?? ''
    if (part.length < 4) continue
    const change: Change = { x: part.charAt(0), y: part.charAt(1), path: part.slice(3) }
    if (change.x === 'R' || change.x === 'C') change.from = parts[++i]
    changes.push(change)
  }
  return changes
}

/** The one letter and theme color a change is drawn with. */
export function badge(c: Change): { letter: string; color: string } {
  const { x, y } = c
  if (x === '?') return { letter: 'U', color: 'success' }
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

async function git($: $, root: string, args: string[]) {
  return $.process.run(['git', '--no-optional-locks', ...args], { cwd: root })
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
    return {
      root,
      isRepo: true,
      branch: name || undefined,
      changes: status.exitCode === 0 ? parseStatus(status.stdout) : [],
      ignored: ignored.stdout.split('\0').filter(Boolean),
      error: status.exitCode === 0 ? undefined : status.stderr.trim(),
    }
  } catch (err) {
    return { root: cwd, isRepo: false, changes: [], ignored: [], error: String(err) }
  }
}

/** Scans and writes the result only when it changed, so idle scans redraw nothing. */
async function rescan($: $) {
  const next = await scan($)
  const text = JSON.stringify(next)
  await update($, scanAtom, prev => (JSON.stringify(prev) === text ? prev : next))
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
): Promise<{ paths: string[]; total: number } | undefined> {
  const needle = filter.trim().toLowerCase()
  if (!changedOnly && needle === '') return undefined
  let paths: string[]
  if (changedOnly || !s.isRepo) paths = s.changes.map(c => c.path)
  else {
    const listed = await git($, s.root, ['ls-files', '-z', '--cached', '--others', '--exclude-standard'])
    paths = [...new Set([...listed.stdout.split('\0').filter(Boolean), ...s.changes.map(c => c.path)])]
  }
  const hits = needle === '' ? paths : paths.filter(p => p.toLowerCase().includes(needle))
  return { paths: hits.slice(0, FILTER_LIMIT), total: hits.length }
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
    const kids = new Map<string, { isDir: boolean; isMissing: boolean }>()
    const source = virtual ?? s.changes.map(c => c.path)
    if (!virtual) {
      const entries = await $.fs.list(s.root + (dir === '' ? '' : '/' + dir)).catch(() => [])
      for (const en of entries) {
        if (HIDDEN.has(en.name)) continue
        kids.set(en.name, { isDir: en.kind === 'dir', isMissing: false })
      }
    }
    // In the lazy tree, changes add what the disk no longer holds (deletions).
    for (const path of source) {
      if (!path.startsWith(prefix)) continue
      const rest = path.slice(prefix.length)
      const seg = rest.split('/')[0] ?? ''
      if (!kids.has(seg)) {
        const isDir = rest.includes('/')
        const c = byPath.get(path)
        const isGone = !isDir && (c?.x === 'D' || c?.y === 'D')
        kids.set(seg, { isDir, isMissing: virtual ? isGone : true })
      }
    }
    const sorted = [...kids].sort(([a, ka], [b, kb]) =>
      ka.isDir !== kb.isDir ? (ka.isDir ? -1 : 1) : a.localeCompare(b, undefined, { sensitivity: 'base' }),
    )
    for (const [name, k] of sorted) {
      const path = prefix + name
      const isOpen = k.isDir && (virtual !== undefined || expanded.has(path))
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
 * The lines `[start, start + count)` as a diff of their own: each run from one hunk
 * gets a header recounted for the run, so the window still parses as hunks.
 */
export function windowDiff(lines: DiffLine[], start: number, count: number): string {
  const runs: DiffLine[][] = []
  for (const line of lines.slice(start, start + count)) {
    const run = runs[runs.length - 1]
    if (run && run[0]?.hunk === line.hunk) run.push(line)
    else runs.push([line])
  }
  return runs
    .map(run => {
      const first = run[0] as DiffLine
      const oCount = run.filter(l => l.kind !== '+').length
      const nCount = run.filter(l => l.kind !== '-').length
      const oStart = oCount === 0 ? first.o - 1 : first.o
      const nStart = nCount === 0 ? first.n - 1 : first.n
      return [`@@ -${oStart},${oCount} +${nStart},${nCount} @@`, ...run.map(l => l.text)].join('\n')
    })
    .join('\n')
}

async function diffFor($: $, s: Scan, c: Change): Promise<string> {
  const flags = ['--no-color', '--no-ext-diff']
  if (c.x === '?') {
    // --no-index exits 1 when the files differ, which is the point here.
    return (await git($, s.root, ['diff', ...flags, '--no-index', '--', '/dev/null', c.path])).stdout
  }
  const paths = c.from ? [c.from, c.path] : [c.path]
  const hasHead = (await git($, s.root, ['rev-parse', '--verify', '-q', 'HEAD'])).exitCode === 0
  if (hasHead) return (await git($, s.root, ['diff', ...flags, '-M', 'HEAD', '--', ...paths])).stdout
  const staged = await git($, s.root, ['diff', ...flags, '--cached', '--', ...paths])
  const unstaged = await git($, s.root, ['diff', ...flags, '--', ...paths])
  return staged.stdout + unstaged.stdout
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
    void $.ui.open({ id: PANE, title: TITLE })
    return started
  })

  on('command.run', { command: 'git-files' }, async $ => {
    await rescan($)
    await $.ui.open({ id: PANE, title: TITLE, focus: true })
    return { text: 'Files pane opened.' }
  })

  on('tool.call', async ($, e, next) => {
    const result = await next(e)
    if (WRITERS.has(String(e.tool))) void rescan($)
    return result
  }).catch(($, e, next) => next(e))

  // The wheel over the file panel scrolls the panel alone; over the tree, the pane scrolls as usual.
  on('ui.scroll', { component: 'Pane', requestId: PANE }, async ($, e, next) => {
    const isOverPanel = e.pointer !== undefined && e.pointer.column >= layout.treeColumns + GUTTER
    if (!layout.hasFile || !isOverPanel) return next(e)
    const last = Math.max(0, layout.panelLines - Math.ceil(layout.panelRoom / 2))
    await update($, panelOffsetAtom, cur => Math.min(last, Math.max(0, cur + e.by)))
    return { deny: 'the file panel scrolls on its own' }
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
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

    const virtual = await pathsFor($, s, changedOnly, filter)
    const rows = await buildRows($, s, new Set(expanded), virtual?.paths)
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
    const select = (path: string) =>
      update($, selectedAtom, cur => (cur === path ? null : path)).then(() => update($, panelOffsetAtom, () => 0))

    const toolbar = (
      <Box flexDirection="row" justifyContent="space-between" alignItems="center" columnGap={1}>
        <Text wrap="truncate-end">
          {s.isRepo ? <Text color="suggestion">⎇ {s.branch ?? '?'}</Text> : <Text dimColor>not a git repo</Text>}
        </Text>
        <Box flexDirection="row" columnGap={2} alignItems="center">
          {s.isRepo && (
            <Button key="changes" plain onPress={() => update($, changedOnlyAtom, v => !v)}>
              {n === 0 ? (
                <Text dimColor>clean</Text>
              ) : (
                <Text color="warning" underline={changedOnly}>
                  ● {n} changed
                </Text>
              )}
            </Button>
          )}
          <Button key="refresh" plain onPress={() => rescan($)}>
            <Text dimColor>↻</Text>
          </Button>
          <Button key="collapse" plain onPress={() => update($, expandedAtom, () => [])}>
            <Text dimColor>⊟</Text>
          </Button>
        </Box>
      </Box>
    )

    const search = Input && (
      <Input
        key="filter"
        placeholder={changedOnly ? 'Filter changed files' : 'Filter files'}
        value={filter}
        onInput={value => void update($, filterAtom, () => value)}
        onSubmit={value => void update($, filterAtom, () => value)}
      />
    )

    const tree = (
      <Box flexDirection="column">
        {rows.length === 0 && (
          <Text dimColor>{filter.trim() !== '' ? 'No matching files.' : changedOnly ? 'No changes.' : 'Empty directory.'}</Text>
        )}
        {rows.map(r => {
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
      </Box>
    )

    // The file panel is pinned over the pane's window: it moves down as the tree scrolls,
    // so it stays in view, and scrolls its own content through panelOffset.
    const panelRoom = Math.max(4, bodyRows - 3)
    let panelLines = 0
    let body
    let range = ''
    if (selected === null) {
      body = (
        <Box flexDirection="column" flexGrow={1} alignItems="center" justifyContent="center" rowGap={1}>
          {Svg && <Svg alt="folder" width={28} height={28} source={EMPTY_ICON} />}
          <Text>Open files appear here</Text>
          <Text dimColor>Changed files open as a diff, the rest as a preview.</Text>
        </Box>
      )
    } else if (change) {
      const lines = diffLines(await diffFor($, s, change))
      panelLines = lines.length
      if (lines.length === 0) body = <Text dimColor>No textual difference (binary or mode change).</Text>
      else {
        const top = Math.min(panelOffset, Math.max(0, lines.length - 1))
        // Each hunk the window crosses costs a header row.
        const hunks = new Set(lines.slice(top, top + panelRoom).map(l => l.hunk)).size
        const count = Math.max(1, panelRoom - hunks)
        range = `${top + 1}–${Math.min(lines.length, top + count)} of ${lines.length}`
        body = <Code key="diff" source={windowDiff(lines, top, count)} format="diff" path={change.path} wrap="truncate-end" />
      }
    } else {
      const stat = await $.fs.stat(s.root + '/' + selected).catch(() => undefined)
      if (!stat || stat.kind !== 'file') body = <Text dimColor>Not a readable file.</Text>
      else if (stat.size > PREVIEW_BYTES) body = <Text dimColor>Too large to preview ({stat.size} bytes).</Text>
      else {
        const text = await $.fs.read(s.root + '/' + selected).catch(() => '')
        if (text.includes('\0')) body = <Text dimColor>Binary file.</Text>
        else {
          const lines = text.split('\n')
          panelLines = lines.length
          const top = Math.min(panelOffset, Math.max(0, lines.length - 1))
          range = `${top + 1}–${Math.min(lines.length, top + panelRoom)} of ${lines.length}`
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
    Object.assign(layout, { treeColumns, panelLines, panelRoom, hasFile: selected !== null })

    const slash = selected === null ? -1 : selected.lastIndexOf('/')
    const panel = (
      <Box
        position="absolute"
        top={e.props.scroll.offset}
        left={treeColumns + GUTTER}
        right={0}
        height={bodyRows}
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
              {range !== '' && <Text dimColor>{range}</Text>}
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
      <Box flexDirection="row">
        <Box flexDirection="column" rowGap={1} width={treeColumns} minHeight={bodyRows} flexShrink={0}>
          {toolbar}
          {search}
          {s.error && <Text color="error">{s.error}</Text>}
          {tree}
        </Box>
        {panel}
      </Box>
    )
  })
}

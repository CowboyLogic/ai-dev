import { describe, expect, mock, test } from 'claude-code/testing'
import type { FsEntry, On } from 'claude-code'

const ROOT = '/repo'
const DIFF = [
  'diff --git a/README.md b/README.md',
  '--- a/README.md',
  '+++ b/README.md',
  '@@ -1,2 +1,2 @@',
  ' # Title',
  '-old line',
  '+new line',
  '',
].join('\n')

const ok = (stdout: string, exitCode = 0, isStdoutTruncated = false) => ({
  value: {
    exitCode,
    stdout,
    stderr: '',
    isStdoutTruncated,
    isStderrTruncated: false,
  },
})

const file = (name: string): FsEntry => ({ name, kind: 'file' as const, size: 10, mtimeMs: 1, isLink: false })
const dir = (name: string): FsEntry => ({ name, kind: 'dir' as const, size: 0, mtimeMs: 0, isLink: false })

const DISK: Record<string, FsEntry[]> = {
  [ROOT]: [file('README.md'), dir('src'), dir('docs'), dir('node_modules'), dir('.git')],
  [ROOT + '/src']: [file('a.ts'), file('new.ts')],
  [ROOT + '/docs']: [file('index.md')],
}

const EMPTY_TREE = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

type Live = {
  diff: string
  mtimeMs: number
  diffRuns?: number
  lists?: number
  reads?: number
  stats?: number
  processes?: number
  text?: string
  /** Modification times of single files, by path from the root, in place of `mtimeMs`. */
  fileMtimes?: Record<string, number>
}

/**
 * A repository with one modified, one untracked and one deleted file. Without `hasHead` it has no
 * commits yet, and README.md is staged with its second line then changed again unstaged.
 * `onStatus` runs inside each `git status`, the call every scan makes first; `text` is every file's.
 * `live` is read on each call: README.md's diff and every file's modification time; `diffRuns`
 * counts the diffs of README.md run. With `isCut`, git's status, line counts, file list and diff
 * come back cut at the 4 MiB limit, as `process.run` reports them. With `isRecreated`, gone.txt is
 * staged for deletion and back on disk with its second line changed, and with `isBlobCut` too its
 * committed version passes 4 MiB; with `isBlobMissing`, git cannot show it. With `isUnreadable`, no file can be read. With `isIgnoredCut`,
 * the list of ignored paths comes back cut. With `isNewGone`, src/new.ts is gone by the time it is
 * looked at, and with `isNewLink` it is a symbolic link to a file. With `isDiffFailed`, git cannot read README.md, so every diff against the base fails.
 * With `isSrcUnreadable`, src can't be listed. With `statusError`, git status fails with that message. `gone` names the deleted file; git's line counts quote
 * it outside printable ASCII unless asked for `-z`.
 */
function fakeRepo(
  on: On,
  {
    fileSize = 4,
    hasHead = true,
    disk = DISK,
    onStatus,
    text = 'a\nb\n',
    live = { diff: DIFF, mtimeMs: 1 } as Live,
    isCut = false,
    isRecreated = false,
    isUnreadable = false,
    isBlobCut = false,
    isBlobMissing = false,
    isIgnoredCut = false,
    gone = 'gone.txt',
    isNewGone = false,
    isNewLink = false,
    isSrcUnreadable = false,
    statusError,
    isDiffFailed = false,
  }: {
    fileSize?: number
    hasHead?: boolean
    disk?: Record<string, FsEntry[]>
    onStatus?: () => Promise<void>
    text?: string
    live?: Live
    isCut?: boolean
    isRecreated?: boolean
    isUnreadable?: boolean
    isBlobCut?: boolean
    isBlobMissing?: boolean
    isIgnoredCut?: boolean
    gone?: string
    isNewGone?: boolean
    isNewLink?: boolean
    isSrcUnreadable?: boolean
    statusError?: string
    isDiffFailed?: boolean
  } = {},
) {
  // Quoted as git quotes it in output without -z (its octal escapes left out here).
  const quoted = /^[\x20-\x7e]*$/.test(gone) ? gone : `"${gone}"`
  on('session.cwd', () => ({ value: ROOT }))
  on('fs.list', ($, e) => {
    live.lists = (live.lists ?? 0) + 1
    if (isSrcUnreadable && e.path === ROOT + '/src') throw new Error('EACCES: permission denied')
    return { value: disk[e.path] ?? [] }
  })
  on('fs.stat', ($, e) => {
    live.stats = (live.stats ?? 0) + 1
    if (isNewGone && e.path.endsWith('/src/new.ts')) throw new Error('ENOENT: no such file or directory')
    const isLink = isNewLink && e.path.endsWith('/src/new.ts')
    const mtimeMs = live.fileMtimes?.[e.path.slice(ROOT.length + 1)] ?? live.mtimeMs
    return { value: { kind: 'file' as const, size: fileSize, mtimeMs, isLink } }
  })
  on('fs.read', () => {
    live.reads = (live.reads ?? 0) + 1
    if (isUnreadable) throw new Error('EACCES: permission denied')
    return { value: live.text ?? text }
  })
  on('process.run', async ($, e) => {
    live.processes = (live.processes ?? 0) + 1
    const args = e.argv.filter(a => a !== '--no-optional-locks').slice(1).join(' ')
    const z = e.argv.includes('-z')
    if (args === 'rev-parse --show-toplevel') return ok(ROOT + '\n')
    if (args.startsWith('status')) {
      await onStatus?.()
      if (statusError !== undefined) return { value: { ...ok('', 128).value, stderr: statusError } }
      if (isRecreated) return ok(` M README.md\0?? src/new.ts\0D  ${gone}\0?? ${gone}\0`)
      return isCut ? ok(' M README.md\0?? src/new.ts\0 D go', 0, true) : ok(` M README.md\0?? src/new.ts\0 D ${gone}\0`)
    }
    if (args.startsWith('ls-files') && args.includes('--ignored')) {
      return isIgnoredCut ? ok('node_modules/\0vend', 0, true) : ok('node_modules/\0')
    }
    if (args.startsWith('ls-files')) return isCut ? ok('README.md\0src/a.ts\0docs/ind', 0, true) : ok('README.md\0src/a.ts\0docs/index.md\0')
    if (args === 'branch --show-current') return ok('feat/x\n')
    if (args === `show HEAD:${gone}` && isBlobMissing) return { value: { ...ok('', 128).value, stderr: `fatal: bad object HEAD:${gone}` } }
    if (args === `show HEAD:${gone}`) return isBlobCut ? ok('a\nb', 0, true) : ok('a\nb\nc\n')
    if (args.endsWith(`--no-index -- /dev/null ${gone}`)) return ok(`diff --git a/${gone} b/${gone}\n@@ -0,0 +1,3 @@\n+a\n+B\n+c\n`, 1)
    if (args.endsWith(`--no-index -- /dev/stdin ${gone}`) && e.init?.stdin === 'a\nb\nc\n') {
      if (args.includes('--numstat')) return z ? ok(`1\t1\t\0/dev/stdin\0${gone}\0`, 1) : ok(`1\t1\t/dev/stdin => ${quoted}\n`, 1)
      return ok(`diff --git a/dev/stdin b/${gone}\n--- a/dev/stdin\n+++ b/${gone}\n@@ -1,3 +1,3 @@\n a\n-b\n+B\n c\n`, 1)
    }
    if (args.startsWith('rev-parse --verify')) return hasHead ? ok('abc\n') : ok('', 1)
    if (args === 'hash-object -t tree /dev/null') return ok(EMPTY_TREE + '\n')
    const end = z ? '\0' : '\n'
    if (isNewGone && args.endsWith('--no-index -- /dev/null src/new.ts')) {
      return { value: { ...ok('', 1).value, stderr: "error: Could not access 'src/new.ts'" } }
    }
    if (isDiffFailed && args.startsWith('diff') && !args.includes('--no-index')) {
      return { value: { ...ok('', 128).value, stderr: 'fatal: cannot hash README.md' } }
    }
    if (args.startsWith('diff --numstat') && args.endsWith(EMPTY_TREE)) return ok('2\t0\tREADME.md' + end)
    if (args.startsWith('diff --numstat')) {
      return ok('1\t1\tREADME.md' + end + '0\t3\t' + (z ? gone : quoted) + end, 0, isCut)
    }
    if (args.includes('README.md')) {
      live.diffRuns = (live.diffRuns ?? 0) + 1
      return ok(live.diff, 0, isCut)
    }
    return ok('', 1)
  })
}

const PROPS = {
  title: 'Files',
  isFocused: false,
  bodyColumns: 80,
  placement: 'dock' as const,
  scroll: { offset: 0, bodyRows: 60 },
  view: {},
}

describe('git-aware-file-explorer pane', () => {
  for (const surface of ['terminal', 'desktop'] as const) {
    test(`shows changes in the tree and a diff beside it (${surface})`, async ($, on) => {
      fakeRepo(on)
      const ui = await $.ui.mount({
        plugin: 'git-aware-file-explorer',
        surface,
        component: 'Pane',
        requestId: 'git-aware-file-explorer',
        props: PROPS,
      })

      expect(await ui.find({ key: 'node:README.md' })).toBeDefined()
      expect(await ui.find({ key: 'node:gone.txt' })).toBeDefined()
      expect(await ui.find({ key: 'node:src/new.ts' })).toBeUndefined()
      expect(await ui.find({ type: 'Text', text: /feat\/x/ })).toBeDefined()
      // One added in README.md, two in the untracked src/new.ts; one and three deleted.
      expect(await ui.find({ type: 'Text', text: '+3' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: '−4' })).toBeDefined()

      await ui.press({ key: 'node:src' })
      expect(await ui.find({ key: 'node:src/new.ts' })).toBeDefined()

      expect(await ui.find({ type: 'Text', text: 'Open files appear here' })).toBeDefined()

      await ui.press({ key: 'node:README.md' })
      expect(await ui.find({ type: 'Text', text: 'new line' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: 'old line' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: '+1' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: '−1' })).toBeDefined()

      await ui.press({ key: 'close-panel' })
      expect(await ui.find({ type: 'Text', text: 'new line' })).toBeUndefined()

      await ui.press({ key: 'changes' })
      expect(await ui.find({ key: 'node:docs' })).toBeUndefined()
      expect(await ui.find({ key: 'node:src/new.ts' })).toBeDefined()
      expect(await ui.find({ key: 'node:gone.txt' })).toBeDefined()

      await ui.input({ key: 'filter', text: 'new', kind: 'change' })
      expect(await ui.find({ key: 'node:src/new.ts' })).toBeDefined()
      expect(await ui.find({ key: 'node:README.md' })).toBeUndefined()

      // Out of the changed-only view, a filter still finds what the tree shows dimmed.
      await ui.press({ key: 'changes' })
      await ui.input({ key: 'filter', text: 'node_mod', kind: 'change' })
      expect(await ui.find({ key: 'node:node_modules' })).toBeDefined()
      expect(await ui.find({ key: 'node:README.md' })).toBeUndefined()

      await ui.unmount()
    })
  }

  test('marks the added total as a minimum when a new file is too large to count', async ($, on) => {
    fakeRepo(on, { fileSize: 1024 * 1024 })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    expect(await ui.find({ type: 'Text', text: '+1+' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−4' })).toBeDefined()

    await ui.unmount()
  })

  test('counts lines once on a branch with no commits yet', async ($, on) => {
    fakeRepo(on, { hasHead: false })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // README.md's 2 staged lines and src/new.ts's 2 untracked ones; the unstaged edit adds none.
    expect(await ui.find({ type: 'Text', text: '+4' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−0' })).toBeDefined()

    await ui.unmount()
  })

  test('redraws the open diff when an edit keeps the line counts', async ($, on) => {
    const live = { diff: DIFF, mtimeMs: 1 }
    fakeRepo(on, { live })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'node:README.md' })
    await ui.press({ key: 'refresh' })
    expect(await ui.find({ type: 'Text', text: 'new line' })).toBeDefined()

    // The same +1 −1, a different line: only the file's modification time says it changed.
    live.diff = DIFF.replace('+new line', '+newer line')
    live.mtimeMs = 2
    await ui.press({ key: 'refresh' })
    expect(await ui.find({ type: 'Text', text: 'newer line' })).toBeDefined()

    await ui.unmount()
  })

  test('reads a diff once while the scan stays the same', async ($, on) => {
    const live: { diff: string; mtimeMs: number; diffRuns?: number } = { diff: DIFF, mtimeMs: 1 }
    fakeRepo(on, { live })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'node:README.md' })
    const runs = live.diffRuns
    // What a native scroll does: draw the pane again with nothing in the workspace changed.
    for (let i = 0; i < 3; i++) await ui.redraw()
    expect(live.diffRuns).toBe(runs)

    await ui.unmount()
  })

  for (const selected of ['README.md', 'src/a.ts']) {
    test(`scrolling ${selected} performs no filesystem or git calls`, async ($, on) => {
      const live: Live = { diff: DIFF, mtimeMs: 1 }
      fakeRepo(on, { live, text: Array.from({ length: 100 }, (_, i) => `line ${i + 1}`).join('\n') })
      on('ui.scroll', () => ({}))
      const ui = await $.ui.mount({
        plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
        requestId: 'git-aware-file-explorer', props: { ...PROPS, scroll: { offset: 0, bodyRows: 20 } },
      })
      // Initialize the scan atom as session.start does in the app.
      await ui.press({ key: 'refresh' })
      await ui.press({ key: 'node:src' })
      await ui.press({ key: 'node:' + selected })
      const before = [live.lists, live.reads, live.stats, live.processes]
      for (let i = 0; i < 3; i++) {
        await $.ui.scroll({
          component: 'Pane', requestId: 'git-aware-file-explorer', offset: 1, by: 1,
          bodyRows: 20, contentRows: 100, origin: { kind: 'person' },
        })
        await ui.redraw({ ...PROPS, scroll: { offset: (i + 1) * 10, bodyRows: 20 } })
      }
      expect([live.lists, live.reads, live.stats, live.processes]).toEqual(before)
      await ui.unmount()
    })
  }

  test('shows the current preview of a file edited while closed', async ($, on) => {
    const live: Live = { diff: DIFF, mtimeMs: 1 }
    fakeRepo(on, { live })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props: PROPS,
    })
    await ui.press({ key: 'node:src' })
    await ui.press({ key: 'refresh' })
    await ui.press({ key: 'node:src/a.ts' })
    await ui.press({ key: 'node:src/a.ts' })
    // Edited while closed: only its own time moves, and git's status and line totals stay the same.
    live.fileMtimes = { 'src/a.ts': 2 }
    live.text = 'edited\nclosed\n'
    await ui.press({ key: 'refresh' })
    await ui.press({ key: 'node:src/a.ts' })

    expect((await ui.find({ type: 'Code' }))?.props.source).toBe('edited\nclosed\n')

    await ui.unmount()
  })

  test('invalidates a cached preview when its scan stamp changes', async ($, on) => {
    const live: Live = { diff: DIFF, mtimeMs: 1 }
    fakeRepo(on, { live })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props: PROPS,
    })
    await ui.press({ key: 'refresh' })
    await ui.press({ key: 'node:src' })
    await ui.press({ key: 'node:src/a.ts' })
    const reads = live.reads ?? 0
    live.mtimeMs++
    live.text = 'updated preview'
    await ui.press({ key: 'refresh' })
    // One untracked-file read for the totals, plus the refreshed preview.
    expect(live.reads).toBe(reads + 2)
    expect((await ui.find({ type: 'Code' }))?.props.source).toBe('updated preview')
    const after = live.reads
    await ui.redraw()
    expect(live.reads).toBe(after)
    await ui.unmount()
  })

  test('opens a 4 MB diff of two million lines', async ($, on) => {
    const added = Array.from({ length: 2_000_000 }, () => '+')
    const diff = ['diff --git a/README.md b/README.md', '@@ -0,0 +1,2000000 @@', ...added, ''].join('\n')
    fakeRepo(on, { live: { diff, mtimeMs: 1 } })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'node:README.md' })
    expect(await ui.find({ type: 'Text', text: '+2000000' })).toBeDefined()
    await ui.redraw({ ...PROPS, scroll: { offset: 1000000, bodyRows: 60 } })
    expect(await ui.find({ key: 'line:999988' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '+2000000' })).toBeDefined()

    await ui.unmount()
  })

  test('marks counts as floors when git output was cut', async ($, on) => {
    fakeRepo(on, { isCut: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // The cut entry (` D go`) is dropped, not read as a file named `go`.
    expect(await ui.find({ type: 'Text', text: '● 2+ changed' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−4+' })).toBeDefined()
    await ui.press({ key: 'node:README.md' })
    expect(await ui.find({ type: 'Text', text: /cut at 4 MB/ })).toBeDefined()

    await ui.unmount()
  })

  test('says when a filter searched a cut file list', async ($, on) => {
    fakeRepo(on, { isCut: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // The cut name (`docs/ind`) is dropped, not matched as a file of that name.
    await ui.input({ key: 'filter', text: 'ind', kind: 'change' })
    expect(await ui.find({ type: 'Text', text: 'No matching files.' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /searched its start only/ })).toBeDefined()

    await ui.unmount()
  })

  test('shows a file staged for deletion and recreated as one net change', async ($, on) => {
    fakeRepo(on, { isRecreated: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // README.md +1 −1, gone.txt's net +1 −1 in place of its −3, src/new.ts's 2 untracked lines.
    expect(await ui.find({ type: 'Text', text: '● 3 changed' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '+4' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−2' })).toBeDefined()
    await ui.press({ key: 'node:gone.txt' })
    expect(await ui.find({ type: 'Text', text: 'B' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /deletion staged, back on disk/ })).toBeDefined()

    await ui.unmount()
  })

  test('counts a recreated file once when git quotes its name', async ($, on) => {
    fakeRepo(on, { isRecreated: true, gone: 'café.txt' })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // café.txt's net +1 −1 replaces its −3, as for any other name, and is not added beside it.
    expect(await ui.find({ type: 'Text', text: '+4' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−2' })).toBeDefined()

    await ui.unmount()
  })

  test('marks the added total as a minimum when a new file cannot be read', async ($, on) => {
    fakeRepo(on, { isUnreadable: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // README.md's 1 added line; src/new.ts went uncounted, so the total is a floor.
    expect(await ui.find({ type: 'Text', text: '+1+' })).toBeDefined()

    await ui.unmount()
  })

  test('marks the added total as a minimum when a new file is gone before it is counted', async ($, on) => {
    fakeRepo(on, { isNewGone: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // README.md's 1 added line; src/new.ts went uncounted, so the total is a floor.
    expect(await ui.find({ type: 'Text', text: '+1+' })).toBeDefined()

    await ui.unmount()
  })

  test("shows git's error when a new file is gone before its diff opens", async ($, on) => {
    fakeRepo(on, { isNewGone: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'node:src' })
    await ui.press({ key: 'node:src/new.ts' })

    // --no-index exits 1 for this error too, as it does when the files differ.
    expect(await ui.find({ type: 'Text', text: /No textual difference/ })).toBeUndefined()
    expect(await ui.find({ type: 'Text', text: "error: Could not access 'src/new.ts'" })).toBeDefined()

    await ui.unmount()
  })

  test('says a folder it cannot list is unreadable, not empty', async ($, on) => {
    fakeRepo(on, { isSrcUnreadable: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'node:src' })

    expect(await ui.find({ type: 'Text', text: ' (unreadable)' })).toBeDefined()

    await ui.unmount()
  })

  test('counts a new symbolic link as one added line, as git does', async ($, on) => {
    fakeRepo(on, { isNewLink: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // README.md's 1 added line and src/new.ts's link target as 1, not the 2 lines of the file it leads to.
    expect(await ui.find({ type: 'Text', text: '+2' })).toBeDefined()

    await ui.unmount()
  })

  for (const statusError of ['fatal: index file corrupt', '']) {
    test(`says the status is unavailable when git status fails (${statusError || 'no message'})`, async ($, on) => {
      fakeRepo(on, { statusError })
      const ui = await $.ui.mount({
        plugin: 'git-aware-file-explorer',
        surface: 'desktop',
        component: 'Pane',
        requestId: 'git-aware-file-explorer',
        props: PROPS,
      })

      // No changes were read, which is not the same as a clean tree.
      expect(await ui.find({ type: 'Text', text: 'clean' })).toBeUndefined()
      expect(await ui.find({ type: 'Text', text: 'status unavailable' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: statusError || 'git status exited 128' })).toBeDefined()

      await ui.unmount()
    })
  }

  test('says when git could not diff a changed file', async ($, on) => {
    fakeRepo(on, { isDiffFailed: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // The failed line counts give no lines at all: what is left is src/new.ts's 2, and both are floors.
    expect(await ui.find({ type: 'Text', text: '+2+' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−0+' })).toBeDefined()
    await ui.press({ key: 'node:README.md' })
    expect(await ui.find({ type: 'Text', text: /No textual difference/ })).toBeUndefined()
    expect(await ui.find({ type: 'Text', text: 'fatal: cannot hash README.md' })).toBeDefined()

    await ui.unmount()
  })

  test('marks a recreated file too large to diff as incomplete', async ($, on) => {
    fakeRepo(on, { isRecreated: true, isBlobCut: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // gone.txt counts neither its deletion nor its contents; both totals are floors, the count exact.
    expect(await ui.find({ type: 'Text', text: '+3+' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−1+' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '● 3 changed' })).toBeDefined()
    await ui.press({ key: 'node:gone.txt' })
    expect(await ui.find({ type: 'Text', text: /cut at 4 MB/ })).toBeDefined()

    await ui.unmount()
  })

  test('marks both totals as floors when git cannot diff a recreated file', async ($, on) => {
    fakeRepo(on, { isRecreated: true, isBlobMissing: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // gone.txt's net change is unknown: neither its −3 deletion nor its contents count, both are floors.
    expect(await ui.find({ type: 'Text', text: '+3+' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '−1+' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: '● 3 changed' })).toBeDefined()

    await ui.unmount()
  })

  test("shows git's error when it cannot read a recreated file's committed version", async ($, on) => {
    fakeRepo(on, { isRecreated: true, isBlobMissing: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'node:gone.txt' })

    // Not the new contents alone, drawn as if they were the whole change.
    expect(await ui.find({ type: 'Text', text: 'fatal: bad object HEAD:gone.txt' })).toBeDefined()

    await ui.unmount()
  })

  test('does not strike through a recreated file in the changed-only view', async ($, on) => {
    fakeRepo(on, { isRecreated: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'changes' })

    expect((await ui.find({ type: 'Text', text: 'gone.txt' }))?.props.strikethrough).toBe(false)

    await ui.unmount()
  })

  test('says an unchanged file it cannot read is unreadable, not empty', async ($, on) => {
    fakeRepo(on, { isUnreadable: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.press({ key: 'node:src' })
    await ui.press({ key: 'node:src/a.ts' })

    expect(await ui.find({ type: 'Text', text: 'Not a readable file.' })).toBeDefined()
    expect(await ui.find({ type: 'Code' })).toBeUndefined()

    await ui.unmount()
  })

  test('says a filter does not search inside ignored folders', async ($, on) => {
    fakeRepo(on)
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // git lists the ignored node_modules/ by its own path, not the files inside it.
    await ui.input({ key: 'filter', text: 'read', kind: 'change' })
    expect(await ui.find({ key: 'node:README.md' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: 'Files inside ignored folders are not searched.' })).toBeDefined()

    await ui.unmount()
  })

  test('says when a filter searched a cut list of ignored files', async ($, on) => {
    fakeRepo(on, { isIgnoredCut: true })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    // The cut entry (`vend`) is dropped, not drawn as a file of that name.
    await ui.input({ key: 'filter', text: 'vend', kind: 'change' })
    expect(await ui.find({ key: 'node:vend' })).toBeUndefined()
    expect(await ui.find({ type: 'Text', text: /ignored files passed 4 MB/ })).toBeDefined()

    await ui.unmount()
  })

  test('runs one scan at a time and folds the requests made meanwhile into one', async ($, on) => {
    const clock = mock.clock(on)
    let isSlow = false
    let running = 0
    let most = 0
    let scans = 0
    fakeRepo(on, {
      onStatus: async () => {
        if (!isSlow) return
        scans++
        most = Math.max(most, ++running)
        await clock.sleep(20)
        running--
      },
    })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    isSlow = true

    const presses = Promise.all([ui.press({ key: 'refresh' }), ui.press({ key: 'refresh' }), ui.press({ key: 'refresh' })])
    await clock.advance(20)
    await clock.advance(20)
    await presses
    expect(most).toBe(1)
    expect(scans).toBe(2)

    await ui.unmount()
  })

  test('keeps an ordinary preview source unchanged while the native viewport moves and resizes', async ($, on) => {
    const text = Array.from({ length: 100 }, (_, i) => `line ${i + 1}`).join('\n')
    fakeRepo(on, { text })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props: { ...PROPS, scroll: { offset: 0, bodyRows: 20 } },
    })
    await ui.press({ key: 'node:src' })
    await ui.press({ key: 'node:src/a.ts' })
    expect((await ui.find({ type: 'Code' }))?.props.source).toBe(text)
    await ui.redraw({ ...PROPS, scroll: { offset: 50, bodyRows: 20 } })
    expect((await ui.find({ type: 'Code' }))?.props.startLine).toBe(1)
    expect((await ui.find({ type: 'Code' }))?.props.source).toBe(text)
    expect(await ui.find({ key: 'preview-before' })).toBeUndefined()
    expect(await ui.find({ key: 'preview-after' })).toBeUndefined()
    await ui.redraw({ ...PROPS, scroll: { offset: 0, bodyRows: 200 } })
    expect((await ui.find({ type: 'Code' }))?.props.startLine).toBe(1)
    expect(await ui.find({ key: 'preview-before' })).toBeUndefined()
    expect(await ui.find({ key: 'preview-after' })).toBeUndefined()
    await ui.unmount()
  })

  test('keeps retained large-preview Code blocks unchanged across scroll boundaries', async ($, on) => {
    const live: Live = { diff: DIFF, mtimeMs: 1 }
    fakeRepo(on, { live, text: Array.from({ length: 1000 }, (_, i) => `line ${i + 1} ${'x'.repeat(80)}`).join('\n') })
    const props = { ...PROPS, scroll: { offset: 0, bodyRows: 20 } }
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props,
    })
    await ui.press({ key: 'refresh' })
    await ui.press({ key: 'node:src' })
    await ui.press({ key: 'node:src/a.ts' })
    const codeProps = async () => (await ui.findAll({ type: 'Code' })).map(code => code.props)
    const initial = await codeProps()
    expect(initial.map(code => code.startLine)).toEqual([1, 33, 65])
    const calls = [live.lists, live.reads, live.stats, live.processes]

    await ui.redraw({ ...props, scroll: { offset: 100, bodyRows: 20 } })
    const later = await codeProps()
    expect(later.map(code => code.startLine)).toEqual([33, 65, 97, 129, 161])
    expect(later[0]).toEqual(initial[1])
    expect(later[1]).toEqual(initial[2])
    expect((await ui.find({ key: 'preview-before' }))?.props.height).toBe(32)
    expect((await ui.find({ key: 'preview-after' }))?.props.height).toBe(808)

    await ui.redraw({ ...props, scroll: { offset: 101, bodyRows: 20 } })
    expect(await codeProps()).toEqual(later)
    expect([live.lists, live.reads, live.stats, live.processes]).toEqual(calls)
    await ui.unmount()
  })

  test('puts both columns in normal flow without wheel reset space or file-only controls', async ($, on) => {
    fakeRepo(on)
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props: PROPS,
    })
    await ui.press({ key: 'node:README.md' })
    expect((await ui.find({ key: 'columns' }))?.props.flexDirection).toBe('row')
    expect((await ui.find({ key: 'file-panel' }))?.props.position).toBeUndefined()
    expect(await ui.find({ key: 'spacer' })).toBeUndefined()
    expect(await ui.find({ key: 'spare' })).toBeUndefined()
    expect(await ui.find({ key: 'line-up' })).toBeUndefined()
    expect(await ui.find({ key: 'line-down' })).toBeUndefined()
    await ui.press({ key: 'close-panel' })
    expect(await ui.find({ key: 'spacer' })).toBeUndefined()
    expect(await ui.find({ key: 'spare' })).toBeUndefined()
    await ui.unmount()
  })

  test('leaves person and plugin scroll offsets to the native surface', async ($, on) => {
    fakeRepo(on)
    const offsets: number[] = []
    on('ui.scroll', ($, e) => { offsets.push(e.offset); return {} })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props: PROPS,
    })
    for (const by of [5, -5]) {
      await $.ui.scroll({
        component: 'Pane', requestId: 'git-aware-file-explorer', offset: 40 + by, by,
        bodyRows: 20, contentRows: 100, origin: { kind: 'person' },
      })
    }
    await $.ui.scroll({
      component: 'Pane', requestId: 'git-aware-file-explorer', offset: 25, by: 10,
      bodyRows: 20, contentRows: 100, origin: { kind: 'plugin', name: 'git-aware-file-explorer' },
    })
    expect(offsets).toEqual([45, 35, 25])
    await ui.unmount()
  })

  test('bounds large trees while preserving their full native height', async ($, on) => {
    fakeRepo(on, { disk: {
      [ROOT]: Array.from({ length: 1000 }, (_, i) => file(`f${String(i).padStart(4, '0')}.ts`)),
    } })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props: { ...PROPS, scroll: { offset: 0, bodyRows: 20 } },
    })
    const treeRows = async () => (await ui.findAll({ type: 'Button' })).filter(b => b.key?.startsWith('node:'))
    expect((await treeRows()).length).toBe(18)
    // The fixture also contributes the three changed root entries.
    expect((await ui.find({ key: 'tree-after' }))?.props.height).toBe(1970)
    await ui.redraw({ ...PROPS, scroll: { offset: 1005, bodyRows: 20 } })
    expect((await treeRows()).length).toBe(26)
    expect(await ui.find({ key: 'node:f0500.ts' })).toBeDefined()
    expect((await ui.find({ key: 'tree-before' }))?.props.height).toBe(984)
    expect((await ui.find({ key: 'tree-after' }))?.props.height).toBe(970)
    await ui.redraw({ ...PROPS, scroll: { offset: 0, bodyRows: 20 } })
    expect(await ui.find({ key: 'node:f0000.ts' })).toBeDefined()
    await ui.unmount()
  })

  test('says when a search outside a git repository stopped at the walk limit', async ($, on) => {
    const many = Array.from({ length: 20001 }, (_, i) => file(`f${i}.txt`))
    on('session.cwd', () => ({ value: ROOT }))
    on('fs.list', ($, e) => ({
      value: e.path === ROOT ? [dir('bulk'), dir('deep')] : e.path === ROOT + '/bulk' ? many : [file('target.md')],
    }))
    on('process.run', () => ok('', 128))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    await ui.input({ key: 'filter', text: 'target', kind: 'change' })
    expect(await ui.find({ type: 'Text', text: 'No matching files.' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /Searched the first 20000 entries/ })).toBeDefined()

    await ui.unmount()
  })

  test('bounds a non-git search even when its entries are all directories', async ($, on) => {
    const many = Array.from({ length: 20001 }, (_, i) => dir(`d${i}`))
    let lists = 0
    on('session.cwd', () => ({ value: ROOT }))
    on('fs.list', ($, e) => {
      lists++
      return { value: e.path === ROOT ? [dir('bulk')] : e.path === ROOT + '/bulk' ? many : [] }
    })
    on('process.run', () => ok('', 128))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer', surface: 'desktop', component: 'Pane',
      requestId: 'git-aware-file-explorer', props: PROPS,
    })
    const before = lists
    await ui.input({ key: 'filter', text: 'target', kind: 'change' })
    expect(lists - before).toBe(2)
    expect(await ui.find({ type: 'Text', text: /Searched the first 20000 entries/ })).toBeDefined()
    await ui.unmount()
  })

  test('says when a search outside a git repository could not read a folder', async ($, on) => {
    on('session.cwd', () => ({ value: ROOT }))
    on('fs.list', ($, e) => {
      if (e.path === ROOT + '/locked') throw new Error('EACCES: permission denied')
      return { value: e.path === ROOT ? [file('a.md'), dir('locked')] : [] }
    })
    on('process.run', () => ok('', 128))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    await ui.input({ key: 'filter', text: 'target', kind: 'change' })
    expect(await ui.find({ type: 'Text', text: 'No matching files.' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /1 folder could not be read/ })).toBeDefined()

    await ui.unmount()
  })

  test('does not walk into a linked folder outside a git repository', async ($, on) => {
    // Every folder holds a link back to its parent, reported as a folder.
    const loop: FsEntry = { name: 'up', kind: 'dir', size: 0, mtimeMs: 0, isLink: true }
    let lists = 0
    on('session.cwd', () => ({ value: ROOT }))
    on('fs.list', ($, e) => {
      // Bounded, so a walk that follows the link ends (a failed listing reads as empty) and fails below.
      if (++lists > 50) throw new Error('ELOOP')
      return { value: e.path === ROOT ? [file('a.md'), loop] : [loop] }
    })
    on('process.run', () => ok('', 128))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    const before = lists

    await ui.input({ key: 'filter', text: 'a.md', kind: 'change' })
    expect(await ui.find({ key: 'node:a.md' })).toBeDefined()
    // The filter's walk lists the root alone.
    expect(lists - before).toBeLessThanOrEqual(2)

    await ui.unmount()
  })

  test('rescans after a shell command, PowerShell included, and not after a read', async ($, on) => {
    let scans = 0
    fakeRepo(on, { onStatus: async () => void scans++ })
    on('tool.call', () => ({ result: { text: '' } }))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    for (const [tool, isWriter] of [['Bash', true], ['PowerShell', true], ['Read', false]] as const) {
      const before = scans
      // Typed from this host's tools, which name no PowerShell off Windows: the input is cast.
      const input = { tool, command: 'echo x > a.md', file_path: 'a.md' }
      await $.tool.call(input as unknown as Parameters<typeof $.tool.call>[0])
      // The scan runs unawaited after the call returns; a redraw lets it finish.
      await ui.redraw()
      expect([tool, scans > before]).toEqual([tool, isWriter])
    }

    await ui.unmount()
  })

  test('says why git could not read the workspace, not that it is no repository', async ($, on) => {
    const dubious = "fatal: detected dubious ownership in repository at '/repo'"
    on('session.cwd', () => ({ value: ROOT }))
    on('fs.list', ($, e) => ({ value: DISK[e.path] ?? [] }))
    on('process.run', () => ({ value: { ...ok('', 128).value, stderr: dubious } }))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    expect(await ui.find({ type: 'Text', text: 'not a git repo' })).toBeUndefined()
    expect(await ui.find({ type: 'Text', text: 'git unavailable' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: dubious })).toBeDefined()
    // The files are still there to browse.
    expect(await ui.find({ key: 'node:README.md' })).toBeDefined()

    await ui.unmount()
  })

  test('walks the workspace once for a filter while the scan stays the same', async ($, on) => {
    let lists = 0
    on('session.cwd', () => ({ value: ROOT }))
    on('fs.list', ($, e) => {
      lists++
      return { value: DISK[e.path] ?? [] }
    })
    on('process.run', () => ok('', 128))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })
    await ui.input({ key: 'filter', text: 'a', kind: 'change' })
    const walked = lists
    // A native scroll and a new filter: no file on disk changed, so no new walk.
    for (let i = 0; i < 3; i++) await ui.redraw()
    await ui.input({ key: 'filter', text: 'a.', kind: 'change' })
    expect(lists).toBe(walked)
    expect(await ui.find({ key: 'node:src/a.ts' })).toBeDefined()
    // A finished scan drops the list, so files made since are found on the next draw.
    await ui.press({ key: 'refresh' })
    await ui.redraw()
    expect(lists).toBeGreaterThan(walked)

    await ui.unmount()
  })

  test('filters files outside a git repository', async ($, on) => {
    on('session.cwd', () => ({ value: ROOT }))
    on('fs.list', ($, e) => ({ value: DISK[e.path] ?? [] }))
    on('process.run', () => ok('', 128))
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: PROPS,
    })

    expect(await ui.find({ type: 'Text', text: /not a git repo/ })).toBeDefined()
    await ui.input({ key: 'filter', text: 'index', kind: 'change' })
    expect(await ui.find({ key: 'node:docs/index.md' })).toBeDefined()
    expect(await ui.find({ key: 'node:README.md' })).toBeUndefined()

    await ui.unmount()
  })
})

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

/**
 * A repository with one modified, one untracked and one deleted file. Without `hasHead` it has no
 * commits yet, and README.md is staged with its second line then changed again unstaged.
 * `onStatus` runs inside each `git status`, the call every scan makes first; `text` is every file's.
 * `live` is read on each call: README.md's diff and every file's modification time; `diffRuns`
 * counts the diffs of README.md run. With `isCut`, git's status, line counts, file list and diff
 * come back cut at the 4 MiB limit, as `process.run` reports them. With `isRecreated`, gone.txt is
 * staged for deletion and back on disk with its second line changed, and with `isBlobCut` too its
 * committed version passes 4 MiB. With `isUnreadable`, no file can be read. With `isIgnoredCut`,
 * the list of ignored paths comes back cut. With `isNewGone`, src/new.ts is gone by the time it is
 * looked at. With `statusError`, git status fails with that message. `gone` names the deleted file; git's line counts quote
 * it outside printable ASCII unless asked for `-z`.
 */
function fakeRepo(
  on: On,
  {
    fileSize = 4,
    hasHead = true,
    onStatus,
    text = 'a\nb\n',
    live = { diff: DIFF, mtimeMs: 1 } as { diff: string; mtimeMs: number; diffRuns?: number },
    isCut = false,
    isRecreated = false,
    isUnreadable = false,
    isBlobCut = false,
    isIgnoredCut = false,
    gone = 'gone.txt',
    isNewGone = false,
    statusError,
  }: {
    fileSize?: number
    hasHead?: boolean
    onStatus?: () => Promise<void>
    text?: string
    live?: { diff: string; mtimeMs: number; diffRuns?: number }
    isCut?: boolean
    isRecreated?: boolean
    isUnreadable?: boolean
    isBlobCut?: boolean
    isIgnoredCut?: boolean
    gone?: string
    isNewGone?: boolean
    statusError?: string
  } = {},
) {
  // Quoted as git quotes it in output without -z (its octal escapes left out here).
  const quoted = /^[\x20-\x7e]*$/.test(gone) ? gone : `"${gone}"`
  on('session.cwd', () => ({ value: ROOT }))
  on('fs.list', ($, e) => ({ value: DISK[e.path] ?? [] }))
  on('fs.stat', ($, e) => {
    if (isNewGone && e.path.endsWith('/src/new.ts')) throw new Error('ENOENT: no such file or directory')
    return { value: { kind: 'file' as const, size: fileSize, mtimeMs: live.mtimeMs, isLink: false } }
  })
  on('fs.read', () => {
    if (isUnreadable) throw new Error('EACCES: permission denied')
    return { value: text }
  })
  on('process.run', async ($, e) => {
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
    if (args === `show HEAD:${gone}`) return isBlobCut ? ok('a\nb', 0, true) : ok('a\nb\nc\n')
    if (args.endsWith(`--no-index -- /dev/null ${gone}`)) return ok(`diff --git a/${gone} b/${gone}\n@@ -0,0 +1,3 @@\n+a\n+B\n+c\n`, 1)
    if (args.endsWith(`--no-index -- /dev/stdin ${gone}`) && e.init?.stdin === 'a\nb\nc\n') {
      if (args.includes('--numstat')) return z ? ok(`1\t1\t\0/dev/stdin\0${gone}\0`, 1) : ok(`1\t1\t/dev/stdin => ${quoted}\n`, 1)
      return ok(`diff --git a/dev/stdin b/${gone}\n--- a/dev/stdin\n+++ b/${gone}\n@@ -1,3 +1,3 @@\n a\n-b\n+B\n c\n`, 1)
    }
    if (args.startsWith('rev-parse --verify')) return hasHead ? ok('abc\n') : ok('', 1)
    if (args === 'hash-object -t tree /dev/null') return ok(EMPTY_TREE + '\n')
    const end = z ? '\0' : '\n'
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
    // What a wheel or ▲/▼ press does: draw the pane again with nothing in the workspace changed.
    for (let i = 0; i < 3; i++) await ui.redraw()
    expect(live.diffRuns).toBe(runs)

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

  test('keeps a scrolled preview within the file when the pane grows', async ($, on) => {
    fakeRepo(on, { text: Array.from({ length: 100 }, (_, i) => `line ${i + 1}`).join('\n') })
    const ui = await $.ui.mount({
      plugin: 'git-aware-file-explorer',
      surface: 'desktop',
      component: 'Pane',
      requestId: 'git-aware-file-explorer',
      props: { ...PROPS, scroll: { offset: 0, bodyRows: 20 } },
    })
    await ui.press({ key: 'node:src' })
    await ui.press({ key: 'node:src/a.ts' })
    for (let i = 0; i < 30; i++) await ui.press({ key: 'line-down' })
    expect((await ui.find({ type: 'Code' }))?.props.startLine).toBe(31)

    // Tall enough for the whole file: the window can't sit 30 lines down any more.
    await ui.redraw({ ...PROPS, scroll: { offset: 0, bodyRows: 200 } })
    expect((await ui.find({ type: 'Code' }))?.props.startLine).toBe(1)

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
    expect(await ui.find({ type: 'Text', text: /Searched the first 20000 files only/ })).toBeDefined()

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
    // What a wheel or ▲/▼ press does, and a new filter: no file on disk changed, so no new walk.
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

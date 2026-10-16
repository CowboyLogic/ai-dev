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

const ok = (stdout: string, exitCode = 0) => ({
  value: {
    exitCode,
    stdout,
    stderr: '',
    isStdoutTruncated: false,
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
 * `onStatus` runs inside each `git status`, the call every scan makes first.
 */
function fakeRepo(
  on: On,
  { fileSize = 4, hasHead = true, onStatus }: { fileSize?: number; hasHead?: boolean; onStatus?: () => Promise<void> } = {},
) {
  on('session.cwd', () => ({ value: ROOT }))
  on('fs.list', ($, e) => ({ value: DISK[e.path] ?? [] }))
  on('fs.stat', () => ({ value: { kind: 'file' as const, size: fileSize, mtimeMs: 1, isLink: false } }))
  on('fs.read', () => ({ value: 'a\nb\n' }))
  on('process.run', async ($, e) => {
    const args = e.argv.filter(a => a !== '--no-optional-locks').slice(1).join(' ')
    if (args === 'rev-parse --show-toplevel') return ok(ROOT + '\n')
    if (args.startsWith('status')) {
      await onStatus?.()
      return ok(' M README.md\0?? src/new.ts\0 D gone.txt\0')
    }
    if (args.startsWith('ls-files') && args.includes('--ignored')) return ok('node_modules/\0')
    if (args.startsWith('ls-files')) return ok('README.md\0src/a.ts\0docs/index.md\0')
    if (args === 'branch --show-current') return ok('feat/x\n')
    if (args.startsWith('rev-parse --verify')) return hasHead ? ok('abc\n') : ok('', 1)
    if (args === 'hash-object -t tree /dev/null') return ok(EMPTY_TREE + '\n')
    if (args === 'diff --numstat --no-ext-diff ' + EMPTY_TREE) return ok('2\t0\tREADME.md\n')
    if (args === 'diff --numstat --no-ext-diff --cached') return ok('2\t0\tREADME.md\n')
    if (args === 'diff --numstat --no-ext-diff') return ok('1\t1\tREADME.md\n')
    if (args.startsWith('diff --numstat')) return ok('1\t1\tREADME.md\n0\t3\tgone.txt\n')
    if (args.includes('README.md')) return ok(DIFF)
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

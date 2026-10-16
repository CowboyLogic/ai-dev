import { describe, expect, test } from 'claude-code/testing'
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

/** A repository with one modified, one untracked and one deleted file. */
function fakeRepo(on: On) {
  on('session.cwd', () => ({ value: ROOT }))
  on('fs.list', ($, e) => ({ value: DISK[e.path] ?? [] }))
  on('process.run', ($, e) => {
    const args = e.argv.filter(a => a !== '--no-optional-locks').slice(1).join(' ')
    if (args === 'rev-parse --show-toplevel') return ok(ROOT + '\n')
    if (args.startsWith('status')) return ok(' M README.md\0?? src/new.ts\0 D gone.txt\0')
    if (args.startsWith('ls-files')) return ok('node_modules/\0')
    if (args === 'branch --show-current') return ok('feat/x\n')
    if (args.startsWith('rev-parse --verify')) return ok('abc\n')
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

      await ui.press({ key: 'node:src' })
      expect(await ui.find({ key: 'node:src/new.ts' })).toBeDefined()

      expect(await ui.find({ type: 'Text', text: 'Open files appear here' })).toBeDefined()

      await ui.press({ key: 'node:README.md' })
      expect(await ui.find({ type: 'Code', text: /\+new line/ })).toBeDefined()

      await ui.press({ key: 'close-panel' })
      expect(await ui.find({ type: 'Code' })).toBeUndefined()

      await ui.press({ key: 'changes' })
      expect(await ui.find({ key: 'node:docs' })).toBeUndefined()
      expect(await ui.find({ key: 'node:src/new.ts' })).toBeDefined()
      expect(await ui.find({ key: 'node:gone.txt' })).toBeDefined()

      await ui.input({ key: 'filter', text: 'new', kind: 'change' })
      expect(await ui.find({ key: 'node:src/new.ts' })).toBeDefined()
      expect(await ui.find({ key: 'node:README.md' })).toBeUndefined()

      await ui.unmount()
    })
  }
})

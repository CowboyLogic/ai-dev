import { describe, expect, test } from 'claude-code/testing'

import { countLines, diffLines, parseNumstat, parseStatus, sumNumstat } from '../hooks/register'
import { diffIndex, nativeWindow, previewCapacity, previewWindow, spacerHeights, visibleText } from '../hooks/viewport'

const DIFF = [
  'diff --git a/f b/f',
  '--- a/f',
  '+++ b/f',
  '@@ -1,3 +1,3 @@',
  ' one',
  '-two',
  '+TWO',
  ' three',
  '@@ -10,2 +10,3 @@',
  ' ten',
  '+ten and a half',
  ' eleven',
].join('\n')

describe('diff windowing', () => {
  test('numbers body lines and drops file headers', async () => {
    const lines = diffLines(DIFF)
    expect(lines.length).toBe(7)
    expect(lines[4]).toEqual({ text: ' ten', kind: ' ', o: 10, n: 10, hunk: 1 })
  })

  test('numstat sums lines and skips binary files', async () => {
    expect(sumNumstat(parseNumstat(['3\t1\ta.md', '-\t-\tlogo.png', '2\t0\tb.ts', ''].join('\0')))).toEqual({ added: 5, deleted: 1 })
  })

  test('numstat paths come verbatim, a rename named by its new path', async () => {
    expect(parseNumstat(['1\t0\tcafé\tx.md', '4\t2\t', 'old.ts', 'new.ts', ''].join('\0')).map(e => e.path)).toEqual(['café\tx.md', 'new.ts'])
  })

  test('status reads the original path of a rename in either column', async () => {
    // An unstaged rename (an intent-to-add file) names its original path too.
    expect(parseStatus(' R new.ts\0old.ts\0 M README.md\0')).toEqual([
      { x: ' ', y: 'R', path: 'new.ts', from: 'old.ts' },
      { x: ' ', y: 'M', path: 'README.md' },
    ])
  })

  test('lines count as git counts them', async () => {
    expect(countLines('')).toBe(0)
    expect(countLines('a\nb\n')).toBe(2)
    expect(countLines('a\nb')).toBe(2)
  })
})

describe('native viewport', () => {
  test('aligns preview ranges to fixed blocks and keeps their height and budget bounded', () => {
    for (let offset = 0; offset < 1100; offset++) {
      const view = previewWindow(1000, offset, 20)
      expect(view.before + view.end - view.start + view.after).toBe(1000)
      expect(view.end - view.start).toBeLessThanOrEqual(previewCapacity(20))
      if (view.start < 1000) expect(view.start % 32).toBe(0)
    }
    expect(previewWindow(1000, 96, 20)).toEqual(previewWindow(1000, 97, 20))
  })
  test('splits tall offscreen regions into dimensions the engine accepts', () => {
    expect(spacerHeights(20001)).toEqual([10000, 10000, 1])
    expect(spacerHeights(0)).toEqual([])
    expect(spacerHeights(2000000).reduce((sum, height) => sum + height, 0)).toBe(2000000)
  })
  test('keeps the total height constant at every scroll position', () => {
    for (const height of [1, 2]) {
      for (const offset of [-5, 0, 20, 500, 2000, 4000]) {
        const view = nativeWindow(1000, offset, 20, height)
        expect(view.before + (view.end - view.start) * height + view.after).toBe(1000 * height)
        expect(view.end - view.start).toBeLessThanOrEqual(36)
      }
    }
  })

  test('keeps an empty or completed column at its original height', () => {
    expect(nativeWindow(0, 100, 20)).toEqual({ start: 0, end: 0, before: 0, after: 0 })
    expect(nativeWindow(10, 100, 20, 2)).toEqual({ start: 10, end: 10, before: 20, after: 0 })
  })

  test('locates hunk separators and numbered lines by visual row', () => {
    const hunks = [{ line: 0, row: 0 }, { line: 4, row: 5 }]
    expect(Array.from({ length: 8 }, (_, row) => diffIndex(hunks, row))).toEqual([0, 1, 2, 3, undefined, 4, 5, 6])
  })

  test('bounds long lines without changing short lines', () => {
    expect(visibleText('short', 80, 20)).toBe('short')
    expect(visibleText('x'.repeat(30000), 80, 20).length).toBeLessThanOrEqual(161)
    expect(visibleText('x'.repeat(30000), 10000, 100).length).toBeLessThanOrEqual(301)
  })
})

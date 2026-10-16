import { describe, expect, test } from 'claude-code/testing'

import { canGoDown, canGoUp, countLines, diffLines, lastTop, parseNumstat, sumNumstat, wheel } from '../hooks/register'

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

  test('the window stops where the last line reaches the bottom, separators counted', async () => {
    const lines = diffLines(DIFF)
    // 7 lines and one separator need 8 rows: they fit whole.
    expect(lastTop(lines, 8)).toBe(0)
    // In 4 rows the last hunk's 3 lines fit, and not the separator above them.
    expect(lastTop(lines, 4)).toBe(4)
    expect(lastTop(lines, 3)).toBe(4)
    expect(lastTop(lines, 2)).toBe(5)
  })

  test('numstat sums lines and skips binary files', async () => {
    expect(sumNumstat(parseNumstat(['3\t1\ta.md', '-\t-\tlogo.png', '2\t0\tb.ts', ''].join('\0')))).toEqual({ added: 5, deleted: 1 })
  })

  test('numstat paths come verbatim, a rename named by its new path', async () => {
    expect(parseNumstat(['1\t0\tcafé\tx.md', '4\t2\t', 'old.ts', 'new.ts', ''].join('\0')).map(e => e.path)).toEqual(['café\tx.md', 'new.ts'])
  })

  test('lines count as git counts them', async () => {
    expect(countLines('')).toBe(0)
    expect(countLines('a\nb\n')).toBe(2)
    expect(countLines('a\nb')).toBe(2)
  })
})

// A file open that fits its panel, over a tree of 40 rows: the desktop's pane with a short file.
const FITS = { hasFile: true, panelOffset: 0, panelLast: 0, treeOffset: 0, treeLast: 39 }
const LONG = { ...FITS, panelLast: 10 }

describe('wheel', () => {
  test('moves the tree when the open file fits and the wheel has no pointer', () => {
    expect(wheel({ ...FITS, by: 3 })).toEqual({ panelOffset: 0, treeOffset: 3 })
    expect(wheel({ ...FITS, treeOffset: 3, by: -5 })).toEqual({ panelOffset: 0, treeOffset: 0 })
  })

  test('moves a long file first, then the tree with the rest', () => {
    expect(wheel({ ...LONG, panelOffset: 4, by: 3 })).toEqual({ panelOffset: 7, treeOffset: 0 })
    expect(wheel({ ...LONG, panelOffset: 8, by: 3 })).toEqual({ panelOffset: 10, treeOffset: 1 })
    expect(wheel({ ...LONG, panelOffset: 1, treeOffset: 5, by: -3 })).toEqual({ panelOffset: 0, treeOffset: 3 })
  })

  test('moves only the side under the pointer', () => {
    expect(wheel({ ...LONG, panelOffset: 10, by: 3, over: 'panel' })).toEqual({ panelOffset: 10, treeOffset: 0 })
    expect(wheel({ ...LONG, by: 3, over: 'tree' })).toEqual({ panelOffset: 0, treeOffset: 3 })
  })

  test('keeps the tree within its rows', () => {
    expect(wheel({ ...FITS, treeOffset: 38, by: 3 })).toEqual({ panelOffset: 0, treeOffset: 39 })
    expect(wheel({ ...FITS, hasFile: false, treeOffset: 0, treeLast: 2, by: 3 })).toEqual({ panelOffset: 0, treeOffset: 2 })
  })

  test('a file shorter than its stale offset passes the whole move on', () => {
    expect(wheel({ ...FITS, panelOffset: 12, by: 2 })).toEqual({ panelOffset: 0, treeOffset: 2 })
  })
})

describe('room around the window', () => {
  test('above, while the tree or the open file can go up', () => {
    expect(canGoUp({ ...FITS, hasFile: false, treeOffset: 3 })).toBe(true)
    expect(canGoUp({ ...FITS, treeOffset: 3 })).toBe(true)
    expect(canGoUp({ ...LONG, panelOffset: 2 })).toBe(true)
    expect(canGoUp({ ...FITS, panelOffset: 2 })).toBe(false)
    expect(canGoUp(FITS)).toBe(false)
  })

  test('below, while a file is open and the file or the tree can go down', () => {
    expect(canGoDown(FITS)).toBe(true)
    expect(canGoDown({ ...FITS, treeOffset: 39 })).toBe(false)
    expect(canGoDown({ ...LONG, treeOffset: 39 })).toBe(true)
    expect(canGoDown({ ...FITS, hasFile: false })).toBe(false)
  })
})

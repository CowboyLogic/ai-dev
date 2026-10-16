import { describe, expect, test } from 'claude-code/testing'

import { countLines, diffLines, lastTop, sumNumstat } from '../hooks/register'

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
    expect(sumNumstat('3\t1\ta.md\n-\t-\tlogo.png\n2\t0\tb.ts\n')).toEqual({ added: 5, deleted: 1 })
  })

  test('lines count as git counts them', async () => {
    expect(countLines('')).toBe(0)
    expect(countLines('a\nb\n')).toBe(2)
    expect(countLines('a\nb')).toBe(2)
  })
})

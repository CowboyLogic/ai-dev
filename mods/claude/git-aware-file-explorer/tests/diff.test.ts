import { describe, expect, test } from 'claude-code/testing'

import { diffLines, windowDiff } from '../hooks/register'

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

  test('a window across two hunks gets a recounted header for each run', async () => {
    const out = windowDiff(diffLines(DIFF), 2, 4)
    expect(out).toBe(['@@ -3,1 +2,2 @@', '+TWO', ' three', '@@ -10,1 +10,2 @@', ' ten', '+ten and a half'].join('\n'))
  })
})

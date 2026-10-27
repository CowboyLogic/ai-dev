/** Rows prepared outside the visible region so a native wheel move has content ready to paint. */
const OVERSCAN = 8

/** Keep preview Code instances in fixed blocks instead of replacing their source each line. */
export const PREVIEW_BLOCK_ROWS = 32

export function previewWindow(total: number, offset: number, room: number) {
  const top = Math.max(0, offset)
  const buffer = PREVIEW_BLOCK_ROWS * 2
  const start = Math.min(total, Math.max(0, Math.floor(top / PREVIEW_BLOCK_ROWS) * PREVIEW_BLOCK_ROWS - buffer))
  const end = Math.min(total, Math.max(start, Math.ceil((top + room) / PREVIEW_BLOCK_ROWS) * PREVIEW_BLOCK_ROWS + buffer))
  return { start, end, before: start, after: total - end }
}

/** A constant character budget across block transitions keeps each retained Code source stable. */
export function previewCapacity(room: number) {
  return Math.ceil(room / PREVIEW_BLOCK_ROWS) * PREVIEW_BLOCK_ROWS + PREVIEW_BLOCK_ROWS * 5
}

/** Individual Box dimensions are capped by the engine at 10,000 cells. */
export function spacerHeights(rows: number) {
  const heights: number[] = []
  for (let left = rows; left > 0; left -= 10000) heights.push(Math.min(10000, left))
  return heights
}

/** Replace offscreen rows with spacers of the same height; never move the native scroll offset. */
export function nativeWindow(total: number, offset: number, room: number, rowHeight = 1) {
  const top = Math.max(0, offset)
  const start = Math.min(total, Math.max(0, Math.floor(top / rowHeight) - OVERSCAN))
  const end = Math.min(total, Math.max(start, Math.ceil((top + room) / rowHeight) + OVERSCAN))
  return { start, end, before: start * rowHeight, after: (total - end) * rowHeight }
}

/** A hunk's first data line and its visual row, including the separators before it. */
export type HunkStart = { line: number; row: number }

/** Locate a visual diff row without walking the preceding lines. Undefined names a separator. */
export function diffIndex(hunks: HunkStart[], row: number): number | undefined {
  let low = 0
  let high = hunks.length
  while (low < high) {
    const mid = Math.floor((low + high) / 2)
    if ((hunks[mid]?.row ?? 0) <= row) low = mid + 1
    else high = mid
  }
  const next = hunks[low]
  if (next && row === next.row - 1) return undefined
  const hunk = hunks[low - 1]
  return hunk ? hunk.line + row - hunk.row : undefined
}

/** Only the visible prefix can be drawn; keep long lines within the engine's drawing budget too. */
export function visibleText(text: string, columns: number, rows: number) {
  const limit = Math.max(1, Math.min(Math.max(20, columns * 2), Math.floor(30000 / Math.max(1, rows))))
  return text.length > limit ? text.slice(0, limit) + '…' : text
}

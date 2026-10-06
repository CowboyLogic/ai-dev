#!/usr/bin/env bash
# SessionStart hook: print .agent-output/handoff.md to stdout so a new session starts
# with it as context. Never fails session start: every path exits 0.
#
# Environment:
#   CLAUDE_PROJECT_DIR     project root (falls back to the current directory)
#   HANDOFF_MAX_AGE_DAYS   skip a handoff older than this many days (default 7, 0 = no limit)
#
# Portable on purpose: no jq, no GNU-only flags, no bash 4 features.

MAX_LINES=150

main() {
  # Skip sources whose context is already present. The hook matcher should exclude
  # these too; this is the second line of defence.
  input=""
  if [ ! -t 0 ]; then
    input=$(cat 2>/dev/null)
  fi
  source=$(printf '%s' "$input" |
    sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -n 1)
  case "$source" in
    resume | fork) return 0 ;;
  esac

  dir="${CLAUDE_PROJECT_DIR:-$PWD}"
  file="$dir/.agent-output/handoff.md"
  [ -f "$file" ] && [ -r "$file" ] || return 0

  # Age cutoff.
  days="${HANDOFF_MAX_AGE_DAYS:-7}"
  case "$days" in
    '' | *[!0-9]*) days=7 ;;
  esac
  if [ "$days" -gt 0 ]; then
    stale=$(find "$file" -mmin +"$((days * 1440))" -print 2>/dev/null)
    [ -z "$stale" ] || return 0
  fi

  # Branch mismatch note.
  recorded=$(sed -n 's/^Branch:[[:space:]]*//p' "$file" 2>/dev/null | head -n 1)
  current=$(git -C "$dir" symbolic-ref --short -q HEAD 2>/dev/null)
  if [ -z "$current" ] && git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
    current="(detached)"
  fi

  echo "=== Handoff from a previous session (.agent-output/handoff.md) ==="
  echo "Written by a previous session. It may be stale: confirm it still applies before acting on it."
  if [ -n "$recorded" ] && [ -n "$current" ] && [ "$recorded" != "$current" ]; then
    echo "Note: it was written on branch '$recorded', and the current branch is '$current'."
  fi
  echo "---"
  head -n "$MAX_LINES" "$file" 2>/dev/null
  # awk counts records, so a last line with no trailing newline is still counted.
  total=$(awk 'END { print NR }' "$file" 2>/dev/null)
  if [ -n "$total" ] && [ "$total" -gt "$MAX_LINES" ]; then
    echo "[handoff truncated at $MAX_LINES of $total lines]"
  fi
  echo "=== end handoff ==="
  return 0
}

main 2>/dev/null
exit 0

#!/usr/bin/env bash
# Verify a deployed set of Matrix Topology agents against MANIFEST.sha256.
#
# Agents are deployed by copy (not symlink) on Windows, so `git pull` does not
# update them. This answers "is what is actually running current?" — Neo's
# TOPOLOGY VERSION line only proves Neo itself is current, not the other thirteen.
#
# Usage:
#   ./verify-deployment.sh                          # check this repo is self-consistent
#   ./verify-deployment.sh <deployed-dir> [format]  # check a deployed copy
#
#   format defaults to "opencode"; deployed files are matched by basename, so a
#   flattened deploy directory works.
#
# Regenerate after changing any agent:
#   ./verify-deployment.sh --update

set -uo pipefail
cd "$(dirname "$0")"

MANIFEST="MANIFEST.sha256"
FORMATS="opencode claude copilot"

if command -v sha256sum >/dev/null 2>&1; then
  sha() { sha256sum "$1" | awk '{print $1}'; }
elif command -v shasum >/dev/null 2>&1; then
  sha() { shasum -a 256 "$1" | awk '{print $1}'; }
else
  echo "No SHA-256 utility found; install sha256sum or shasum" >&2
  exit 127
fi

if [ "${1:-}" = "--update" ]; then
  {
    echo "# Matrix Topology agent manifest"
    echo "# Regenerate with: ./verify-deployment.sh --update"
    echo "# version: $(grep -m1 -o 'TOPOLOGY VERSION: [0-9-]*' opencode/neo.agent.md | cut -d' ' -f3)"
    echo "# generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    for d in $FORMATS; do
      for f in "$d"/*.agent.md; do
        echo "$(sha "$f")  $f"
      done
    done
  } > "$MANIFEST"
  echo "Wrote $MANIFEST ($(grep -vc '^#' "$MANIFEST") files)"
  exit 0
fi

[ -f "$MANIFEST" ] || { echo "No $MANIFEST — run: $0 --update" >&2; exit 2; }

grep -m1 '^# version:' "$MANIFEST"

# No argument: verify the repo against its own manifest.
if [ $# -eq 0 ]; then
  fail=0
  while read -r want file; do
    got=$(sha "$file")
    if [ -z "$got" ]; then echo "MISSING  $file"; fail=1
    elif [ "$got" != "$want" ]; then echo "CHANGED  $file"; fail=1
    fi
  done < <(grep -v '^#' "$MANIFEST")
  [ $fail -eq 0 ] && echo "OK — repo matches manifest" || echo "Manifest is stale: run $0 --update"
  exit $fail
fi

# Argument: verify a deployed directory, matching by basename.
target="${1%/}"
format="${2:-opencode}"
[ -d "$target" ] || { echo "Not a directory: $target" >&2; exit 2; }

fail=0 checked=0
while read -r want file; do
  case "$file" in "$format"/*) ;; *) continue ;; esac
  base=$(basename "$file")
  # Tolerate the .agent.md -> .md rename some deploys use.
  for cand in "$target/$base" "$target/${base%.agent.md}.md"; do
    [ -f "$cand" ] && break
  done
  if [ ! -f "$cand" ]; then echo "MISSING  $base"; fail=1; continue; fi
  checked=$((checked + 1))
  [ "$(sha "$cand")" = "$want" ] || { echo "STALE    $base"; fail=1; }
done < <(grep -v '^#' "$MANIFEST")

echo "Checked $checked file(s) in $target against format '$format'"
[ $fail -eq 0 ] && echo "OK — deployment is current" || echo "Deployment is STALE — re-copy $format/ to $target"
exit $fail

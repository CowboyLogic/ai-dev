#!/usr/bin/env bash
# validate.sh — Run markdownlint-cli against one or more paths
#
# Usage:
#   bash validate.sh                     # lint all .md files in current directory
#   bash validate.sh docs/               # lint all .md files under docs/
#   bash validate.sh docs/index.md       # lint a single file
#   bash validate.sh --fix docs/         # auto-fix where possible
#   bash validate.sh --strict docs/      # error on any violation (non-zero exit)
#
# Requirements: markdownlint-cli (npm install -g markdownlint-cli)
#               Config: nearest .markdownlint.json (or .yaml/.yml) is used automatically

set -euo pipefail

# ── Args ──────────────────────────────────────────────────────────────────────
FIX=false
STRICT=false
TARGETS=()

for arg in "$@"; do
  case "$arg" in
    --fix)    FIX=true ;;
    --strict) STRICT=true ;;
    *)        TARGETS+=("$arg") ;;
  esac
done

# Default target if none given
if [[ ${#TARGETS[@]} -eq 0 ]]; then
  TARGETS=(".")
fi

# ── Dependency check ──────────────────────────────────────────────────────────
if ! command -v markdownlint &>/dev/null; then
  echo "ERROR: markdownlint-cli not found."
  echo "  Install: npm install -g markdownlint-cli"
  echo "  Or use:  npx markdownlint-cli"
  exit 1
fi

# ── Build glob pattern from targets ───────────────────────────────────────────
GLOBS=()
for target in "${TARGETS[@]}"; do
  if [[ -f "$target" ]]; then
    GLOBS+=("$target")
  elif [[ -d "$target" ]]; then
    GLOBS+=("${target%/}/**/*.md")
  else
    # Treat as glob directly
    GLOBS+=("$target")
  fi
done

# ── Run ───────────────────────────────────────────────────────────────────────
CMD=(markdownlint)

if [[ "$FIX" == "true" ]]; then
  CMD+=(--fix)
fi

CMD+=("${GLOBS[@]}")

echo "Running: ${CMD[*]}"
echo ""

if "$STRICT"; then
  # --strict: exit non-zero on any violation (default markdownlint behavior)
  "${CMD[@]}"
else
  # Soft mode: show violations but exit 0 so CI can choose how to handle
  "${CMD[@]}" || true
fi

echo ""
echo "Done. Fix remaining violations manually or run with --fix."

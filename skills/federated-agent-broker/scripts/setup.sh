#!/usr/bin/env bash
# Set up the Federated Agent Broker's private policy and Claude Code MCP entry.

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
readonly BROKER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd -P)"
readonly DEFAULT_CONFIG_DIR="${HOME}/.config/federated-agent-broker"
readonly SERVER_NAME="federated-agent-broker"

CONFIG_DIR="${DEFAULT_CONFIG_DIR}"
REPLACE_SERVER=false
SKIP_MCP=false
PYTHON_BIN="${PYTHON_BIN:-python3}"

usage() {
  cat <<'EOF'
Usage: setup.sh [OPTIONS]

Create a private Federated Agent Broker policy and register the local stdio MCP
server with Claude Code at user scope.

Options:
  --config-dir PATH  Store policy.json in PATH instead of
                     ~/.config/federated-agent-broker.
  --replace          Replace an existing federated-agent-broker MCP entry.
  --skip-mcp         Create the policy file without changing Claude Code config.
  -h, --help         Show this help message.

The script never overwrites an existing policy.json. Set PYTHON_BIN to use a
specific Python 3.10+ interpreter.
EOF
}

fail() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

while (($# > 0)); do
  case "$1" in
    --config-dir)
      (($# >= 2)) || fail "--config-dir requires a path"
      CONFIG_DIR="$2"
      shift 2
      ;;
    --replace)
      REPLACE_SERVER=true
      shift
      ;;
    --skip-mcp)
      SKIP_MCP=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

command -v "${PYTHON_BIN}" >/dev/null 2>&1 || fail "Python interpreter not found: ${PYTHON_BIN}"
"${PYTHON_BIN}" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' \
  || fail "${PYTHON_BIN} must be Python 3.10 or later"

POLICY_PATH="${CONFIG_DIR}/policy.json"
[[ -n "${CONFIG_DIR}" ]] || fail "--config-dir cannot be empty"
mkdir -p "${CONFIG_DIR}"

if [[ -e "${POLICY_PATH}" ]]; then
  [[ -f "${POLICY_PATH}" ]] || fail "policy path exists but is not a regular file: ${POLICY_PATH}"
  printf 'Keeping existing policy: %s\n' "${POLICY_PATH}"
else
  cp "${BROKER_ROOT}/references/policy.example.json" "${POLICY_PATH}"
  printf 'Created policy template: %s\n' "${POLICY_PATH}"
fi

if [[ "${SKIP_MCP}" == true ]]; then
  printf 'Skipped Claude Code MCP registration.\n'
  exit 0
fi

command -v claude >/dev/null 2>&1 || fail "Claude Code CLI not found. Install it, then rerun this script."
command -v copilot >/dev/null 2>&1 || fail "GitHub Copilot CLI not found. Install and authenticate it, then rerun this script."

if claude mcp get "${SERVER_NAME}" >/dev/null 2>&1; then
  if [[ "${REPLACE_SERVER}" != true ]]; then
    printf 'An MCP entry named %s already exists; it was not changed.\n' "${SERVER_NAME}"
    printf 'Run this script again with --replace to replace that entry.\n'
    exit 0
  fi
  claude mcp remove "${SERVER_NAME}"
fi

claude mcp add --scope user --transport stdio "${SERVER_NAME}" \
  --env "FEDERATED_BROKER_POLICY=${POLICY_PATH}" -- \
  "${PYTHON_BIN}" "${BROKER_ROOT}/scripts/copilot_broker.py"

printf 'Configured Claude Code MCP server: %s\n' "${SERVER_NAME}"
printf 'Policy: %s\n' "${POLICY_PATH}"
printf 'Next: edit the policy if you want to pin models, start a new Claude Code session, then run /mcp and broker_status.\n'

# Containerized Agent Execution — Local Setup Guide

**Status:** Working Document — Personal Use
**Version:** 0.1.0
**Created:** 2026-04-18
**Context:** Local proof-of-concept for the Containerized Agent Execution Pattern

> "Make it so." — Captain Jean-Luc Picard

---

## Overview

> [!NOTE]
> This is a work in progress. The concept is real. Testing continues.

This guide sets up a **global, reusable container** for AI agent execution on your local
Windows 11 / WSL2 / Docker Desktop environment. The container:

- Is built once and reused across any project
- Mounts whatever repository you're working in at runtime
- Runs GitHub Copilot CLI as the execution agent
- Accepts your GitHub token via environment variable — no rebuild on token rotation
- Spins up in 5–15 seconds after the initial build

The repository only needs two things: `agents-output/` in `.gitignore`. Everything else
lives in the container.

---

## Prerequisites

Before starting, verify the following are in place:

- [ ] Docker Desktop installed and running
- [ ] WSL2 configured as the Docker Desktop backend
  - Docker Desktop → Settings → General → "Use WSL 2 based engine" ✅
- [ ] Active GitHub Copilot subscription (Pro, Pro+, Business, or Enterprise)
- [ ] GitHub fine-grained Personal Access Token with **Copilot Requests** permission
  - Generate at: <https://github.com/settings/tokens?type=beta>
  - Under Permissions → Add permissions → select "Copilot Requests"

---

## Directory Structure

Create the global agent container home. This lives outside any repo:

```
~/.agent-container/
  Dockerfile          ← defines the execution environment
  run.sh              ← launches the container against any repo
  .env.example        ← token configuration template
```

Set it up:

```bash
mkdir -p ~/.agent-container
cd ~/.agent-container
```

---

## Step 1: Create the Dockerfile

```dockerfile
# ~/.agent-container/Dockerfile
# Execution agent container — Ubuntu minimal base
# Copilot CLI installed, token passed at runtime via environment variable
# Runs as non-root user (agent) for security compliance

FROM ubuntu:24.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install core dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    wget \
    unzip \
    jq \
    sudo \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22+ (required by Copilot CLI)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub Copilot CLI via official install script
# Installs the standalone 'copilot' binary to /usr/local/bin
RUN curl -fsSL https://gh.io/copilot-install | bash

# Verify install (as root — binary is in /usr/local/bin)
RUN copilot --version

# Create non-root user and group for agent execution
RUN groupadd --gid 1001 agent \
    && useradd --uid 1001 --gid agent --shell /bin/bash --create-home agent

# Create workspace directory with correct ownership
# /workspace is mounted at runtime — agent user must own it
RUN mkdir -p /workspace/agents-output \
    && chown -R agent:agent /workspace

# Give agent user ownership of the entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown agent:agent /entrypoint.sh

# Switch to non-root user for all subsequent operations
USER agent

# Set working directory
WORKDIR /workspace

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
```

---

## Step 2: Create the Entrypoint Script

The entrypoint handles GitHub auth using the token passed via environment variable,
then drops you into an interactive shell inside the container.

```bash
# ~/.agent-container/entrypoint.sh
#!/bin/bash
set -e

echo "🔧 Initializing agent execution environment..."

# Resolve GitHub token from environment — checked in precedence order
# COPILOT_GITHUB_TOKEN > GH_TOKEN > GITHUB_TOKEN > GITHUB_TOKEN_CLIENT
if [ -n "$COPILOT_GITHUB_TOKEN" ]; then
  export GH_TOKEN="$COPILOT_GITHUB_TOKEN"
  echo "✅ Token resolved from COPILOT_GITHUB_TOKEN"
elif [ -n "$GH_TOKEN" ]; then
  echo "✅ Token resolved from GH_TOKEN"
elif [ -n "$GITHUB_TOKEN" ]; then
  export GH_TOKEN="$GITHUB_TOKEN"
  echo "✅ Token resolved from GITHUB_TOKEN"
elif [ -n "$GITHUB_TOKEN_CLIENT" ]; then
  export GH_TOKEN="$GITHUB_TOKEN_CLIENT"
  echo "✅ Token resolved from GITHUB_TOKEN_CLIENT"
else
  echo "❌ ERROR: No GitHub token found in environment."
  echo "   Set one of the following before running:"
  echo "     export GH_TOKEN=your_token_here"
  echo "     export GITHUB_TOKEN=your_token_here"
  echo "     export GITHUB_TOKEN_CLIENT=your_token_here"
  echo "   Token requires 'Copilot Requests' permission (fine-grained PAT)"
  exit 1
fi

# Verify Copilot CLI is available
if copilot --version > /dev/null 2>&1; then
  echo "✅ GitHub Copilot CLI ready"
else
  echo "⚠️  Copilot CLI not responding — may need reinstall"
fi

# Ensure agents-output exists and is writable
if [ -d "/workspace" ]; then
  mkdir -p /workspace/agents-output
  echo "✅ agents-output/ scratch space ready"
fi

# Show git context if inside a repo
if git -C /workspace rev-parse --git-dir > /dev/null 2>&1; then
  BRANCH=$(git -C /workspace branch --show-current 2>/dev/null || echo "unknown")
  REPO=$(basename $(git -C /workspace rev-parse --show-toplevel 2>/dev/null) || echo "unknown")
  echo "📁 Repository: $REPO"
  echo "🌿 Branch: $BRANCH"

  # Branch guard — warn if on main or trunk
  if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "trunk" ]; then
    echo ""
    echo "⚠️  WARNING: You are on the '$BRANCH' branch."
    echo "   The execution agent will warn before writing any tracked files."
    echo "   Consider switching to a feature branch before proceeding."
    echo ""
  fi
else
  echo "📁 No git repository detected at /workspace"
fi

echo ""
echo "🚀 Agent execution environment ready."
echo "   Workspace: /workspace"
echo "   Scratch space: /workspace/agents-output"
echo ""

# Execute the command passed to the container (default: bash)
exec "$@"
```

---

## Step 3: Create the Run Script

The run script is how you launch the container against any repo. Run it from the repo
root you want to work in.

```bash
# ~/.agent-container/run.sh
#!/bin/bash
set -e

# ── Configuration ──────────────────────────────────────────────────────────────

IMAGE_NAME="agent-execution-env"
IMAGE_TAG="latest"

# ── Validate environment ────────────────────────────────────────────────────────

# Check at least one token variable is set
if [ -z "$GH_TOKEN" ] && [ -z "$GITHUB_TOKEN" ] && [ -z "$GITHUB_TOKEN_CLIENT" ]; then
  echo "❌ No GitHub token found in environment."
  echo ""
  echo "   Set one of the following before running:"
  echo "   export GH_TOKEN=your_token_here"
  echo "   export GITHUB_TOKEN=your_token_here"
  echo "   export GITHUB_TOKEN_CLIENT=your_token_here"
  echo ""
  echo "   Or add it to your shell profile (~/.bashrc or ~/.zshrc) for persistence."
  exit 1
fi

# Determine repo path — use argument if provided, otherwise current directory
REPO_PATH="${1:-$(pwd)}"

if [ ! -d "$REPO_PATH" ]; then
  echo "❌ Directory not found: $REPO_PATH"
  exit 1
fi

# Resolve absolute path
REPO_PATH=$(realpath "$REPO_PATH")
echo "📂 Mounting: $REPO_PATH"

# ── Ensure agents-output exists in the repo ─────────────────────────────────────

AGENTS_OUTPUT="$REPO_PATH/agents-output"
GITIGNORE="$REPO_PATH/.gitignore"

# Create agents-output if it doesn't exist
if [ ! -d "$AGENTS_OUTPUT" ]; then
  mkdir -p "$AGENTS_OUTPUT"
  echo "✅ Created agents-output/ in repo"
fi

# Add to .gitignore if not already there
if [ -f "$GITIGNORE" ]; then
  if ! grep -q "agents-output" "$GITIGNORE"; then
    echo "agents-output/" >> "$GITIGNORE"
    echo "✅ Added agents-output/ to .gitignore"
  fi
else
  echo "agents-output/" > "$GITIGNORE"
  echo "✅ Created .gitignore with agents-output/"
fi

# ── Check image exists, build if not ───────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! docker image inspect "$IMAGE_NAME:$IMAGE_TAG" > /dev/null 2>&1; then
  echo "🔨 Image not found — building now (one-time, ~2-5 minutes)..."
  docker build -t "$IMAGE_NAME:$IMAGE_TAG" "$SCRIPT_DIR"
  echo "✅ Image built: $IMAGE_NAME:$IMAGE_TAG"
else
  echo "✅ Image found: $IMAGE_NAME:$IMAGE_TAG"
fi

# ── Launch the container ────────────────────────────────────────────────────────

echo "🚀 Starting agent execution environment..."
echo ""

docker run -it \
  --rm \
  --name "agent-exec-$(date +%s)" \
  --user 1001:1001 \
  -e GH_TOKEN="${GH_TOKEN:-}" \
  -e GITHUB_TOKEN="${GITHUB_TOKEN:-}" \
  -e GITHUB_TOKEN_CLIENT="${GITHUB_TOKEN_CLIENT:-}" \
  -v "$REPO_PATH:/workspace" \
  "$IMAGE_NAME:$IMAGE_TAG"
```

Make the scripts executable:

```bash
chmod +x ~/.agent-container/run.sh
chmod +x ~/.agent-container/entrypoint.sh
```

---

## Step 4: Set Your GitHub Token

Add your token to your shell profile so it persists across sessions. In WSL2:

```bash
# Add to ~/.bashrc or ~/.zshrc — use whichever variable matches your environment
echo 'export GH_TOKEN=your_github_token_here' >> ~/.bashrc
source ~/.bashrc
```

The entrypoint resolves tokens in this precedence order:
`COPILOT_GITHUB_TOKEN` → `GH_TOKEN` → `GITHUB_TOKEN` → `GITHUB_TOKEN_CLIENT`

Use whichever variable is already set in your environment. If multiple are set,
the first in the precedence order wins.

**Token rotation:** When your token changes, update the value in your shell profile
and `source` it. No container rebuild required — the token is passed at runtime.

```bash
# Update token — whichever variable you use
export GH_TOKEN=your_new_token_here

# Or re-source your profile after editing
source ~/.bashrc
```

---

## Step 5: Build the Image (One Time)

From your WSL2 terminal:

```bash
cd ~/.agent-container
docker build -t agent-execution-env:latest .
```

Expected output:

- Build time: 2–5 minutes on first build
- Image size: ~500MB–800MB (Ubuntu + Node + gh CLI + Copilot extension)
- Subsequent container starts from this image: **5–15 seconds**

Verify the build:

```bash
docker images | grep agent-execution-env
```

---

## Step 6: First Run — Cerebro

Navigate to your Cerebro repo and launch the container:

```bash
# From your WSL2 terminal
cd /path/to/cerebro

# Launch the container — mounts current directory
~/.agent-container/run.sh
```

The run script will:

1. Create `agents-output/` in the repo if it doesn't exist
2. Add it to `.gitignore` if not already there
3. Start the container with the repo mounted at `/workspace`
4. Authenticate Copilot CLI using your `GH_TOKEN`
5. Display your current branch and warn if you're on `main` or `trunk`
6. Drop you into an interactive bash shell inside the container

---

## Step 7: Using Copilot CLI as the Execution Agent

Inside the container, use `copilot suggest` or `copilot explain` to interact
with the execution agent. For agentic task execution, use:

```bash
# Basic task execution — default model
copilot suggest "your task prompt here"

# Specify model explicitly (recommended for controlled testing)
copilot suggest --model gpt-4.1 "your task prompt here"

# Available models (verify current list with: copilot models)
# gpt-4.1
# gpt-4.1-mini
# claude-haiku-4-5     ← if available in your Copilot tier
```

**For execution agent tasks — always:**

1. Write your handoff prompt first (outside the container, with the thinking agent)
2. Paste the prompt to `copilot suggest` inside the container
3. Direct output to `agents-output/`: the agent should write there by default per
   your skill directives; explicitly instruct it if needed
4. Exit the container (`exit`)
5. Review `agents-output/` contents on your host before touching your working tree

---

## Step 8: Verify Branch Guard Behavior

This test confirms the branch guard fires correctly.

**Test A — On a feature branch (expected: no warning):**

```bash
# On host, in your repo
git checkout -b test/agent-container-proof

# Launch container
~/.agent-container/run.sh

# Expected: no branch warning in startup output
# Branch line should read: 🌿 Branch: test/agent-container-proof
```

**Test B — On main (expected: warning fires):**

```bash
# On host
git checkout main

# Launch container
~/.agent-container/run.sh

# Expected: warning block appears in startup output
# ⚠️  WARNING: You are on the 'main' branch.
```

**Test C — Verify agents-output is gitignored:**

```bash
# On host, after running the container at least once
cat .gitignore | grep agents-output
# Expected: agents-output/

git status
# agents-output/ should not appear as a tracked path
```

---

## Convenience: Shell Alias

Add an alias to your shell profile so you don't have to type the full path:

```bash
# Add to ~/.bashrc or ~/.zshrc
echo "alias agent='~/.agent-container/run.sh'" >> ~/.bashrc
source ~/.bashrc

# Usage from any repo root:
agent
# Or with explicit path:
agent /path/to/some/other/repo
```

---

## Rebuilding the Image

You only need to rebuild when the container's tooling changes — not when your token
changes or when you switch repos.

Rebuild when:

- You update the Dockerfile (new tools, updated base image)
- A major Copilot CLI version update requires reinstall
- You want to pull a newer Ubuntu base image

```bash
cd ~/.agent-container

# Force rebuild (no cache)
docker build --no-cache -t agent-execution-env:latest .
```

---

## Troubleshooting

**Container fails to authenticate:**

- Verify at least one token variable is set:
  `echo "GH=$GH_TOKEN GITHUB=$GITHUB_TOKEN CLIENT=$GITHUB_TOKEN_CLIENT"`
- Token precedence: `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN` > `GITHUB_TOKEN_CLIENT`
- Verify token is a fine-grained PAT with "Copilot Requests" permission
- Generate a new token at: <https://github.com/settings/tokens?type=beta>

**Copilot CLI not available inside container:**

- The extension install sometimes fails silently on first build
- Verify inside container: `copilot --version`
- Rebuild with `--no-cache` flag: `docker build --no-cache -t agent-execution-env:latest .`

**Permission denied writing to /workspace:**

- The container runs as uid 1001 (agent user)
- The mounted repo directory on the host must be owned by or writable by your WSL2 user
- If you see permission errors: `ls -la /path/to/repo` — verify your user owns it
- On WSL2 this is rarely an issue since your home directory files are owned by your user

**agents-output/ appearing in git status:**

- Verify `.gitignore` contains `agents-output/`
- If already tracked: `git rm -r --cached agents-output/`

**Docker Desktop not seeing WSL2 filesystem paths:**

- Ensure WSL2 integration is enabled for your distro
- Docker Desktop → Settings → Resources → WSL Integration → enable your distro

**Container starts but workspace is empty:**

- Verify you ran `run.sh` from inside the repo directory
- Or pass the explicit path: `~/.agent-container/run.sh /path/to/repo`

---

## What to Document After Proving It

Once the pattern is validated locally, the following observations should be captured
before moving to the work context:

- [ ] Actual container startup time (measure it — perception vs. reality matters)
- [ ] Copilot CLI model performance differences observed during testing
- [ ] Any friction points in the setup that would affect engineer adoption
- [ ] Branch guard behavior — does it catch what you expect?
- [ ] agents-output/ workflow — is the review-before-integrate pattern natural?
- [ ] Anything that would need to change for an internal Artifact Registry base image

These observations feed directly into Section 8 (Implementation Guidance) of the
architecture pattern document.

---

## File Summary

```
~/.agent-container/
  Dockerfile          ← container definition (build once)
  entrypoint.sh       ← auth, branch guard, environment setup
  run.sh              ← launch script (run from any repo root)

[your-repo]/
  agents-output/      ← gitignored scratch space (created by run.sh)
  .gitignore          ← updated by run.sh if needed
```

No other files. No repo-specific configuration required.

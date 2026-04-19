# Docker Build Reference

Source: https://docs.docker.com/build/building/best-practices/ | https://docs.docker.com/reference/dockerfile/

## Table of Contents

1. [Dockerfile Instructions Quick Reference](#dockerfile-instructions-quick-reference)
2. [Multi-Stage Builds](#multi-stage-builds)
3. [Build Cache](#build-cache)
4. [Build Secrets and SSH](#build-secrets-and-ssh)
5. [Build Commands](#build-commands)
6. [Base Image Selection](#base-image-selection)
7. [Common Patterns](#common-patterns)

---

## Dockerfile Instructions Quick Reference

| Instruction | Purpose | Best Practice |
|---|---|---|
| `FROM` | Base image | Use official/verified images. Pin tag + digest for reproducibility. |
| `LABEL` | Metadata | Use reverse-DNS keys: `org.opencontainers.image.version` |
| `RUN` | Execute commands | Combine with `&&`; clean up in the same layer |
| `COPY` | Copy files from context | Prefer over `ADD` for local files |
| `ADD` | Copy + auto-extract tars, fetch URLs | Use only for remote artifacts or tar extraction |
| `ENV` | Set env vars persistent in image | Avoid using for secrets; they persist in layers |
| `ARG` | Build-time variables | Not visible in final image, but appear in build history |
| `WORKDIR` | Set working directory | Always use absolute paths |
| `EXPOSE` | Document listening port | Informational only; does not publish |
| `USER` | Set runtime user | Set to non-root before `CMD`/`ENTRYPOINT` |
| `CMD` | Default command | Use exec form: `["executable", "arg"]` |
| `ENTRYPOINT` | Fixed executable | Combine with `CMD` for defaults |
| `HEALTHCHECK` | Container health probe | Always define for services |
| `VOLUME` | Declare mount points | Declares intent; volume must be mounted at runtime |
| `ONBUILD` | Trigger on child image build | Tag images with `-onbuild` when using |

### RUN — Debian/Ubuntu apt pattern

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    package-a \
    package-b \
    && rm -rf /var/lib/apt/lists/*
```

Never split `apt-get update` and `apt-get install` into separate `RUN` instructions — the cached update layer will cause stale package versions.

### ENV — avoid leaking sensitive values

`ENV` values persist in every subsequent layer and are visible in `docker inspect`. For secrets, use `--secret` build mounts instead.

```dockerfile
# OK for version pinning
ENV PG_VERSION=16.3

# WRONG for secrets — visible in layer history
ENV DB_PASSWORD=mysecret  # never do this
```

### COPY vs ADD

- Use `COPY` for copying local files into the image.
- Use `ADD` only when you need automatic tar extraction or a remote URL with checksum:

```dockerfile
ADD --checksum=sha256:<hash> https://example.com/archive.tar.gz /tmp/archive.tar.gz
```

### ENTRYPOINT + CMD pattern

```dockerfile
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
```

Users can override `CMD` without touching `ENTRYPOINT`: `docker run myimage -g "daemon off; error_log /dev/stdout;"`.

### USER — non-root setup

```dockerfile
# Debian/Ubuntu
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser
USER appuser

# Alpine
RUN addgroup -g 1001 -S appgroup && adduser -u 1001 -S appuser -G appgroup
USER appuser
```

Use explicit UID/GID numbers for determinism.

### HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1
```

---

## Multi-Stage Builds

Multi-stage builds separate build and runtime environments, producing smaller, cleaner production images.

### Basic pattern

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
RUN addgroup -g 1001 -S nodejs && adduser -u 1001 -S appuser -G nodejs
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Selective stage targeting

```bash
# Build only the test stage
docker build --target builder -t myapp:test .
```

### Reusable base stages

```dockerfile
FROM ubuntu:24.04 AS base
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

FROM base AS app-a
# ...

FROM base AS app-b
# ...
```

---

## Build Cache

Docker caches each instruction layer. A cache miss invalidates all subsequent layers.

### Cache invalidation rules

| Instruction | Cache breaks when... |
|---|---|
| `FROM` | Base image digest changes |
| `COPY` / `ADD` | Any file in the copied set changes |
| `RUN` | The command string changes |
| `ENV` / `ARG` | Value changes |

### Cache-friendly ordering (copy from least to most volatile)

```dockerfile
# 1. Copy dependency manifests (rarely change)
COPY package*.json ./

# 2. Install dependencies (cached if manifests unchanged)
RUN npm ci

# 3. Copy source code (changes frequently — cache misses here won't re-run installs)
COPY src/ ./src/
```

### Cache mounts (BuildKit) — avoid re-downloading packages

```dockerfile
# pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# apt
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends curl
```

### Bind mounts — temporary context files in RUN

```dockerfile
RUN --mount=type=bind,source=requirements.txt,target=/tmp/req.txt \
    pip install -r /tmp/req.txt
```

The file is not copied into the image layer.

---

## Build Secrets and SSH

### Secret mounts (preferred for credentials)

```dockerfile
# In Dockerfile — secret is never stored in the image
RUN --mount=type=secret,id=github_token \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) \
    pip install --extra-index-url "https://${GITHUB_TOKEN}@pypi.example.com" mypackage
```

```bash
# Pass secret at build time
docker build --secret id=github_token,src=./.secrets/github_token .
```

### SSH forwarding (for private Git repos)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim
RUN --mount=type=ssh \
    pip install git+ssh://git@github.com/myorg/private-package.git
```

```bash
docker build --ssh default .
```

---

## Build Commands

```bash
# Basic build
docker build -t myapp:1.0 .

# Build from alternate Dockerfile
docker build -f Dockerfile.prod -t myapp:prod .

# Build and push in one step
docker build --push -t registry.example.com/myapp:1.0 .

# Force fresh base image and bypass cache
docker build --pull --no-cache -t myapp:1.0 .

# Pass build args (non-secret only)
docker build --build-arg NODE_ENV=production -t myapp:prod .

# Multi-platform build (requires buildx with docker-container driver)
docker buildx build --platform linux/amd64,linux/arm64 --push -t myapp:1.0 .

# Build with secret
docker build --secret id=mysecret,src=./secret.txt -t myapp:1.0 .

# Target a specific stage
docker build --target builder -t myapp:builder .

# Inspect build cache usage
docker buildx du
```

---

## Base Image Selection

| Need | Recommended base |
|---|---|
| Smallest possible image | `scratch` (static binaries only) or `gcr.io/distroless/*` |
| General Linux, smallest footprint | `alpine:3.21` |
| Debian-based, smaller than full | `debian:12-slim` or `ubuntu:24.04` |
| Node.js | `node:22-alpine` |
| Python | `python:3.12-slim` |
| Go (build stage only) | `golang:1.23-alpine` |
| Java | `eclipse-temurin:21-jre-alpine` |
| .NET | `mcr.microsoft.com/dotnet/aspnet:9.0-alpine` |

**Tag pinning strategy:**

```dockerfile
# Recommended: minor version (gets patch security updates, reproducible)
FROM node:22-alpine

# Maximum reproducibility: pin to digest
FROM node:22-alpine@sha256:abc123...

# Avoid: mutable, non-reproducible
FROM node:latest
```

---

## Common Patterns

### .dockerignore (essential)

```
.git
.gitignore
node_modules
npm-debug.log
dist
build
.env
.env.*
*.log
__pycache__
.pytest_cache
.venv
*.pyc
.DS_Store
README.md
docs/
tests/
```

### Pinning apt package versions

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl=7.81.0-1ubuntu1.* \
    && rm -rf /var/lib/apt/lists/*
```

### Using `set -o pipefail` in pipes

```dockerfile
RUN set -o pipefail && wget -qO- https://example.com/script.sh | bash
```

Without `pipefail`, a failed `wget` won't fail the build because only the exit code of `bash` is checked.

### Distroless example (Go binary)

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 go build -o /app/server .

FROM gcr.io/distroless/static-debian12
COPY --from=builder /app/server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

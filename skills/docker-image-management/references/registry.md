# Docker Registry Reference

Source: https://docs.docker.com/docker-hub/ | https://docs.docker.com/scout/

## Table of Contents

1. [Tagging Strategy](#tagging-strategy)
2. [Authentication](#authentication)
3. [Push and Pull](#push-and-pull)
4. [Docker Hub](#docker-hub)
5. [Private Registries](#private-registries)
6. [Image Management](#image-management)
7. [Vulnerability Scanning (Docker Scout)](#vulnerability-scanning-docker-scout)

---

## Tagging Strategy

Image references follow the format: `[registry/][namespace/]repository[:tag][@digest]`

| Format | Example |
|---|---|
| Official Docker Hub image | `nginx:1.27-alpine` |
| User/org namespace on Hub | `myorg/myapp:2.1.0` |
| Private registry | `registry.example.com/team/myapp:2.1.0` |
| Digest (immutable) | `nginx:1.27@sha256:abc123...` |

### Recommended tagging approach

```bash
# Semantic version tag + latest
docker tag myapp:2.1.0 myorg/myapp:2.1.0
docker tag myapp:2.1.0 myorg/myapp:2.1
docker tag myapp:2.1.0 myorg/myapp:latest

# Commit SHA tag (useful in CI)
docker tag myapp:2.1.0 myorg/myapp:$(git rev-parse --short HEAD)
```

**Avoid using `latest` as your only tag** — it's mutable and makes rollbacks difficult. Always tag with a specific version.

**For base images in Dockerfiles** — pin to a minor version tag (e.g. `node:22-alpine`) to get security patches, or pin to a digest for full reproducibility:

```dockerfile
FROM node:22-alpine@sha256:abc123...
```

---

## Authentication

### Docker Hub

```bash
# Login interactively
docker login

# Login with username (prompts for password)
docker login -u myusername

# Login with access token (recommended over password)
docker login -u myusername --password-stdin <<< "$DOCKER_PAT"
```

Create a Personal Access Token (PAT) at https://hub.docker.com/settings/security. Use PATs instead of passwords for CI/CD.

### Private registry

```bash
# Generic registry login
docker login registry.example.com

# AWS ECR (token expires every 12h)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    123456789.dkr.ecr.us-east-1.amazonaws.com

# Google Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Azure Container Registry
az acr login --name myregistry
```

### CI/CD authentication

Store credentials as secrets, never in source. Example (GitHub Actions):

```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}

- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Logout

```bash
docker logout
docker logout registry.example.com
```

---

## Push and Pull

### Push

```bash
# Must be tagged with registry/namespace before pushing
docker push myorg/myapp:2.1.0

# Build and push in one step (preferred)
docker build --push -t myorg/myapp:2.1.0 .

# Push multiple tags
docker buildx build --push \
  -t myorg/myapp:2.1.0 \
  -t myorg/myapp:2.1 \
  -t myorg/myapp:latest .
```

### Pull

```bash
# Pull specific tag
docker pull myorg/myapp:2.1.0

# Pull by digest (immutable)
docker pull myorg/myapp@sha256:abc123...

# Force pull latest (don't use cached layer)
docker build --pull -t myapp:latest .
```

---

## Docker Hub

### Repositories

- **Public repos**: Free, unlimited pulls for public images.
- **Private repos**: Requires account (1 free private repo on Personal plan).
- **Organizations**: Group repos under org namespaces with team access control.

### Rate limits (unauthenticated / free accounts)

| Account type | Pull rate |
|---|---|
| Unauthenticated | 10 pulls/6h per IP |
| Authenticated (free) | 100 pulls/6h |
| Pro/Team/Business | Unlimited |

Always authenticate in CI to avoid rate limiting.

### Docker Hub CLI commands

```bash
# Search public images
docker search nginx

# Filter to official images only
docker search --filter is-official=true python

# See image tags (Hub doesn't surface this natively in CLI; use API)
curl -s "https://hub.docker.com/v2/repositories/library/node/tags?page_size=20" \
  | jq '.results[].name'
```

---

## Private Registries

### GitHub Container Registry (GHCR)

```bash
echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
docker push ghcr.io/OWNER/IMAGE:TAG
```

Packages visibility is controlled per-package in GitHub settings.

### AWS ECR

```bash
# Create repository
aws ecr create-repository --repository-name myapp --region us-east-1

# Get login token and push
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
```

### Google Artifact Registry

```bash
# Configure auth helper
gcloud auth configure-docker us-central1-docker.pkg.dev

# Tag and push
docker tag myapp:1.0 us-central1-docker.pkg.dev/my-project/my-repo/myapp:1.0
docker push us-central1-docker.pkg.dev/my-project/my-repo/myapp:1.0
```

---

## Image Management

### Listing and inspecting

```bash
# List local images
docker images
docker image ls

# Filter by name
docker images myapp

# Show all images (including intermediates)
docker images -a

# Inspect image metadata
docker image inspect myapp:1.0

# Show image history/layers
docker image history myapp:1.0
docker image history --no-trunc myapp:1.0

# Show image digest
docker image inspect myapp:1.0 --format '{{index .RepoDigests 0}}'
```

### Cleanup

```bash
# Remove specific image
docker rmi myapp:1.0
docker image rm myapp:1.0

# Remove all unused images (dangling and unreferenced)
docker image prune -a

# Remove dangling images only (no tag, not referenced)
docker image prune

# Full system cleanup (containers, networks, images, build cache)
docker system prune -a

# With volume cleanup (destructive!)
docker system prune -a --volumes
```

### Export and import

```bash
# Export image to tar (for air-gapped transfers)
docker image save -o myapp.tar myapp:1.0

# Load from tar
docker image load -i myapp.tar

# Export container filesystem (not layers — loses metadata)
docker export <container> -o myapp-fs.tar
docker import myapp-fs.tar myapp:imported
```

---

## Vulnerability Scanning (Docker Scout)

Docker Scout analyzes image contents for CVEs and evaluates policy compliance.

### Quickstart

```bash
# Install Scout CLI plugin (if not on Docker Desktop)
curl -fsSL https://raw.githubusercontent.com/docker/scout-cli/main/install.sh | sh

# Analyze local image
docker scout cves myapp:1.0

# Analyze specific package only
docker scout cves --only-package express myapp:1.0

# Quick overview (vulnerabilities + policy compliance)
docker scout quickview myapp:1.0

# Compare two image versions
docker scout compare myapp:2.0 myapp:1.0

# Suggest base image update
docker scout recommendations myapp:1.0
```

### Policy evaluation

```bash
# Set your organization (required for policy eval)
docker scout config organization myorg

# Evaluate against default policies
docker scout quickview
```

Default policies include:

| Policy | Checks |
|---|---|
| No fixable critical/high CVEs | Image has no patched-but-unupdated vulnerabilities |
| Default non-root user | `USER` is not `root` |
| No outdated base images | Base image is current |
| No high-profile CVEs | Not affected by named CVEs (Log4Shell, etc.) |
| Supply chain attestations | SBOM and provenance attached |

### Build with attestations (required for full policy evaluation)

```bash
# Enable containerd image store in Docker Desktop first, then:
docker build \
  --provenance=true \
  --sbom=true \
  --push \
  -t myorg/myapp:1.0 .
```

### Enable Scout on a repository

```bash
docker scout enroll myorg
docker scout repo enable --org myorg myorg/myapp
```

### SBOM generation

```bash
# Generate SBOM locally
docker scout sbom myapp:1.0

# Output as SPDX JSON
docker scout sbom --format spdx myapp:1.0 > sbom.json
```

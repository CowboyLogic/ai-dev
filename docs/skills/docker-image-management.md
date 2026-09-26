# Docker Image Management

Author, build, run, and publish Docker images. Covers Dockerfile best practices,
multi-stage builds, BuildKit features, container runtime options, docker-compose patterns,
registry authentication and tagging, and Docker Scout vulnerability scanning.

- **Skill name:** `docker-image-management`
- **Last updated:** 2026-04-19
- **Source:** [skills/docker-image-management](https://github.com/CowboyLogic/ai-dev/tree/main/skills/docker-image-management)

---

## What it does

The skill gives an agent a standard container workflow and a set of core principles, then
loads the reference file for the specific task — building, running, or publishing — before
giving guidance.

**Core principles:**

- **Security first** — run as a non-root `USER`, never embed secrets in image layers (use
  `--secret` build mounts or runtime environment variables), and pin base images to a
  specific tag or digest.
- **Layer efficiency** — order instructions from least to most frequently changed, install
  dependencies before copying application code, clean up in the same `RUN` layer, and use
  multi-stage builds to keep build tools out of production images.
- **BuildKit by default** — parallel stages, cache export, secret mounts, and SSH forwarding;
  `docker buildx build` for multi-platform builds.

**Standard workflow:**

1. Analyze requirements — runtime versus build dependencies, ports, configuration, volumes,
   and security context.
2. Write the Dockerfile from a template.
3. Create a `.dockerignore`.
4. Build the image.
5. Run and test the container.
6. Tag and push to a registry.

The skill also includes a debugging checklist that maps symptoms (container exits
immediately, port not reachable, permission denied, large image, cache misses, secret
exposed in a layer) to the action to take.

---

## Reference files

| File | Contents |
|------|----------|
| `references/build.md` | Dockerfile instructions, multi-stage builds, BuildKit mounts, build cache, secrets, base image selection |
| `references/run.md` | `docker run` options, networking, storage mounts, resource constraints, capabilities, lifecycle |
| `references/registry.md` | Tagging strategy, authentication, push/pull, Docker Hub, private registries, Docker Scout |
| `references/dockerfile-templates.md` | Dockerfile templates for Node.js, Python, Go, and other runtimes |
| `references/docker-compose-examples.yml` | Multi-container compose configurations |
| `references/dockerignore-template` | Language-specific `.dockerignore` patterns |
| `scripts/docker-manage.sh` | Bash helper for common build and run operations |

---

## Install

### Using `npx skills` (recommended — works across all agents)

```bash
# Install globally for all detected agents
npx skills add CowboyLogic/ai-dev --skill docker-image-management -g

# Install for a specific agent only
npx skills add CowboyLogic/ai-dev --skill docker-image-management --agent <agent> -g
```

### Verify installation

```bash
npx skills ls -g
```

# Docker Image Management

Author, build, run, and publish Docker images. Covers Dockerfile best practices,
multi-stage builds, BuildKit features, container runtime options, docker-compose patterns,
registry authentication and tagging, and Docker Scout vulnerability scanning.

- **Skill name:** `docker-image-management`
- **Source:** [skills/docker-image-management](https://github.com/CowboyLogic/ai-dev/tree/main/skills/docker-image-management)

---

## What it does

The skill gives an agent a standard container workflow, from requirements through build,
test, and publish. It loads the reference file for the specific task, whether building,
running, or publishing, before giving guidance. It also includes a debugging checklist that
maps common symptoms to the action to take, templates for common runtimes, and a helper
script for build and run operations.

## Where it applies

Use it when an agent writes a Dockerfile or compose file, builds and runs containers, or
publishes an image to a registry.

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

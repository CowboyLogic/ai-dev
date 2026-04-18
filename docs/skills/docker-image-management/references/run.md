# Docker Run Reference

Source: https://docs.docker.com/engine/containers/run/ | https://docs.docker.com/engine/storage/

## Table of Contents

1. [docker run Syntax](#docker-run-syntax)
2. [Common Runtime Flags](#common-runtime-flags)
3. [Networking](#networking)
4. [Storage Mounts](#storage-mounts)
5. [Resource Constraints](#resource-constraints)
6. [Security and Capabilities](#security-and-capabilities)
7. [Container Lifecycle](#container-lifecycle)
8. [Debugging](#debugging)

---

## docker run Syntax

```
docker run [OPTIONS] IMAGE[:TAG|@DIGEST] [COMMAND] [ARG...]
```

- `IMAGE[:TAG]` — specify version; defaults to `latest` if omitted
- `IMAGE@sha256:<digest>` — pin to exact digest for reproducibility
- `[COMMAND]` — overrides `CMD` instruction from the image
- `[ARG...]` — appended to `ENTRYPOINT`

---

## Common Runtime Flags

| Flag | Short | Description |
|---|---|---|
| `--detach` | `-d` | Run in background |
| `--interactive` | `-i` | Keep stdin open |
| `--tty` | `-t` | Allocate pseudo-TTY (combine with `-i` for shell) |
| `--rm` | | Automatically remove container on exit |
| `--name <name>` | | Assign container name |
| `--publish <host:container>` | `-p` | Publish port(s) |
| `--publish-all` | `-P` | Publish all EXPOSE'd ports to random host ports |
| `--env <KEY=VALUE>` | `-e` | Set environment variable |
| `--env-file <file>` | | Load env vars from file |
| `--user <user[:group]>` | `-u` | Override USER; accepts name, UID, or `uid:gid` |
| `--workdir <path>` | `-w` | Override working directory |
| `--entrypoint <cmd>` | | Override ENTRYPOINT |
| `--restart <policy>` | | Restart policy: `no`, `always`, `unless-stopped`, `on-failure[:n]` |
| `--network <name>` | | Connect to network |
| `--hostname <name>` | `-h` | Container hostname |
| `--add-host <host:ip>` | | Add entry to `/etc/hosts` |

### Interactive shell

```bash
docker run -it --rm ubuntu:24.04 bash
docker run -it --rm alpine sh
```

### Background service

```bash
docker run -d --name myapp --restart unless-stopped -p 3000:3000 myapp:1.0
```

### Override entrypoint

```bash
docker run --entrypoint /bin/sh myapp:1.0
docker run --entrypoint "" myapp:1.0 bash   # clear entrypoint, run bash
```

---

## Networking

### Port publishing

```bash
# Specific host port -> container port
docker run -p 8080:3000 myapp:1.0

# Bind to specific interface
docker run -p 127.0.0.1:8080:3000 myapp:1.0

# Port range
docker run -p 8000-8005:8000-8005 myapp:1.0

# Publish all EXPOSE'd ports to random host ports
docker run -P myapp:1.0
docker port <container>   # see mappings
```

### User-defined networks (preferred over legacy links)

Containers on the same network communicate by container name as DNS hostname.

```bash
# Create network
docker network create my-net

# Run containers on it
docker run -d --name web --network my-net nginx:alpine
docker run -d --name api --network my-net myapi:1.0

# api can reach web via http://web/
```

### Network drivers

| Driver | Use case |
|---|---|
| `bridge` (default) | Single-host container communication |
| `host` | Container shares host network stack (no isolation) |
| `none` | No networking |
| `overlay` | Multi-host (Swarm) |

```bash
docker run --network host myapp:1.0        # host networking
docker run --network none myapp:1.0        # no network access
```

---

## Storage Mounts

### Volume mounts (managed by Docker daemon — preferred for persistence)

```bash
# Named volume (created automatically)
docker run --mount source=mydata,target=/data myapp:1.0

# Short form
docker run -v mydata:/data myapp:1.0

# Read-only
docker run --mount source=mydata,target=/data,readonly myapp:1.0

# Manage volumes
docker volume create mydata
docker volume ls
docker volume inspect mydata
docker volume rm mydata
docker volume prune    # remove unused
```

Volumes persist independently of containers. Data survives `docker rm`.

### Bind mounts (host path into container — use for dev, source sharing)

```bash
# Mount current directory
docker run --mount type=bind,source=$(pwd),target=/app myapp:1.0

# Short form
docker run -v $(pwd):/app myapp:1.0

# Read-only bind mount
docker run --mount type=bind,source=$(pwd)/config,target=/etc/app,readonly myapp:1.0
```

Bind mounts expose host files to the container. Both host and container processes can modify them.

### tmpfs mounts (in-memory, not persisted to disk)

```bash
docker run --mount type=tmpfs,target=/tmp myapp:1.0
docker run --tmpfs /tmp:rw,size=64m myapp:1.0
```

Use for: ephemeral credentials, temp files, reducing disk I/O.

### Mount comparison

| Type | Data persists | Managed by Docker | Use when |
|---|---|---|---|
| Volume | Yes | Yes | Databases, persistent app data |
| Bind mount | Yes (on host) | No | Dev hot reload, config sharing |
| tmpfs | No (memory only) | Yes | Secrets, caches, temp data |

---

## Resource Constraints

### Memory

```bash
# Hard limit: 512 MB
docker run -m 512m myapp:1.0

# Soft limit (reservation): container shrinks to this under pressure
docker run --memory-reservation 256m myapp:1.0

# Disable OOM killer (dangerous without -m)
docker run -m 512m --oom-kill-disable myapp:1.0
```

### CPU

```bash
# Limit to 1.5 CPUs
docker run --cpus 1.5 myapp:1.0

# Relative CPU shares (default 1024)
docker run --cpu-shares 512 myapp:1.0   # gets half the default

# Pin to specific CPUs
docker run --cpuset-cpus "0,1" myapp:1.0
docker run --cpuset-cpus "0-3" myapp:1.0
```

### Resource constraint reference

| Flag | Description |
|---|---|
| `-m`, `--memory` | Max memory (e.g., `512m`, `2g`) |
| `--memory-swap` | Memory + swap total (`-1` = unlimited swap) |
| `--memory-reservation` | Soft memory limit |
| `--cpus` | CPU quota as fractional number |
| `--cpu-shares` | Relative CPU weight (default 1024) |
| `--cpuset-cpus` | CPUs to pin (e.g., `0-3`, `0,2`) |
| `--blkio-weight` | Block I/O relative weight (10–1000) |

---

## Security and Capabilities

### Run as non-root

```bash
docker run --user 1001:1001 myapp:1.0
docker run --user appuser myapp:1.0
```

### Linux capabilities

Drop all capabilities and add only what you need:

```bash
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp:1.0
```

Common capabilities:

| Capability | Allows |
|---|---|
| `NET_BIND_SERVICE` | Bind to ports < 1024 |
| `NET_ADMIN` | Modify network interfaces |
| `SYS_PTRACE` | ptrace(2) — needed for debuggers |
| `SYS_ADMIN` | Broad system admin (avoid if possible) |
| `CHOWN` | Change file ownership |

### Privileged mode (avoid in production)

```bash
docker run --privileged myapp:1.0   # gives access to ALL host devices
```

Use `--device` instead to expose only specific devices:

```bash
docker run --device=/dev/snd myapp:1.0
```

### Read-only root filesystem

```bash
docker run --read-only --tmpfs /tmp myapp:1.0
```

Prevents writes to the container filesystem (mounts can still be writable).

### Security options

```bash
docker run --security-opt no-new-privileges myapp:1.0   # prevent privilege escalation
docker run --security-opt seccomp=./seccomp-profile.json myapp:1.0
```

---

## Container Lifecycle

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop (SIGTERM, then SIGKILL after 10s)
docker stop myapp

# Stop with custom timeout
docker stop --time 30 myapp

# Kill immediately (SIGKILL)
docker kill myapp

# Start a stopped container
docker start myapp

# Restart
docker restart myapp

# Remove a stopped container
docker rm myapp

# Remove a running container (force)
docker rm -f myapp

# Remove all stopped containers
docker container prune

# Auto-restart policies
docker run --restart always myapp:1.0          # always restart
docker run --restart unless-stopped myapp:1.0  # restart unless manually stopped
docker run --restart on-failure:3 myapp:1.0    # retry up to 3 times
```

---

## Debugging

```bash
# View container logs
docker logs myapp

# Follow logs
docker logs -f myapp

# Last N lines
docker logs -n 50 myapp

# Show timestamps
docker logs -t myapp

# Exec shell in running container
docker exec -it myapp sh
docker exec -it myapp bash

# Run one-off command
docker exec myapp cat /etc/os-release

# Inspect container metadata (config, network, mounts)
docker inspect myapp

# Extract a specific field
docker inspect -f '{{.State.Health.Status}}' myapp
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' myapp

# Resource usage live
docker stats myapp
docker stats   # all containers

# Process list inside container
docker top myapp

# Copy files to/from container
docker cp myapp:/app/logs/error.log ./error.log
docker cp ./config.json myapp:/app/config.json

# Disk usage
docker system df
docker system df -v   # verbose breakdown
```

### Exit code meanings

| Code | Meaning |
|---|---|
| 0 | Container exited cleanly |
| 1 | Application error |
| 125 | Docker daemon error (bad flag, etc.) |
| 126 | Command found but not executable |
| 127 | Command not found |
| 130 | SIGINT (Ctrl+C) |
| 137 | SIGKILL / OOM killed |
| 143 | SIGTERM |

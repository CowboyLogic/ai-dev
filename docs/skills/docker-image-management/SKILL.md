---
name: docker-image-management
description: Guide for creating, building, and managing Docker images and containers. Use this when working with Dockerfiles, containerization, image optimization, and Docker best practices.
license: MIT
---

# Docker Image Management Skill

This skill provides comprehensive guidance for creating, building, managing, and optimizing Docker images and containers. It covers best practices for Dockerfiles, image layering, security, and performance optimization.

## When to Use This Skill

Use this skill when:
- Creating or optimizing Dockerfiles
- Building Docker images for applications
- Managing container lifecycle (run, stop, remove)
- Debugging container issues
- Optimizing image size and build performance
- Implementing Docker security best practices
- Working with multi-stage builds
- Setting up container orchestration basics

## Prerequisites

- Docker installed and running on the system
- Basic understanding of containerization concepts
- Access to container management tools (Docker CLI, Docker Desktop)
- Project with application code to containerize

## Instructions

### 1. Analyze Application Requirements

Before creating a Dockerfile, understand your application's needs:

1. **Runtime dependencies**: What base image and packages are required?
2. **Build dependencies**: What tools are needed only during build?
3. **Ports**: Which ports does the application expose?
4. **Environment variables**: What configuration is needed?
5. **Volumes**: What data needs to persist?
6. **Security context**: What user should run the application?

### 2. Create Optimized Dockerfile

Follow these best practices for Dockerfile creation:

1. **Choose appropriate base image**
   - Use official images from verified publishers
   - Prefer smaller base images (alpine variants when possible)
   - Use specific version tags, not `latest`

2. **Use multi-stage builds for smaller images**
   ```dockerfile
   # Build stage
   FROM node:18-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production

   # Production stage
   FROM node:18-alpine
   WORKDIR /app
   COPY --from=builder /app/node_modules ./node_modules
   COPY . .
   USER node
   CMD ["npm", "start"]
   ```

3. **Optimize layer caching**
   - Copy package files first, then install dependencies
   - Group related operations in single RUN commands
   - Clean up caches and temporary files in the same layer

4. **Security considerations**
   - Run as non-root user when possible
   - Use `USER` directive
   - Avoid storing secrets in images
   - Keep base images updated

### 3. Build Docker Images

Use the `run_in_terminal` tool to build images:

```bash
# Build with specific tag
docker build -t myapp:1.0 .

# Build with no cache (for troubleshooting)
docker build --no-cache -t myapp:1.0 .

# Build with build args
docker build --build-arg NODE_ENV=production -t myapp:prod .
```

### 4. Manage Images

Common image management operations:

```bash
# List images
docker images

# Tag an image
docker tag myapp:1.0 myregistry.com/myapp:1.0

# Push to registry
docker push myregistry.com/myapp:1.0

# Remove unused images
docker image prune -f

# Remove specific image
docker rmi myapp:1.0
```

### 5. Run and Manage Containers

Container lifecycle management:

```bash
# Run container in background
docker run -d --name myapp-container -p 3000:3000 myapp:1.0

# Run with environment variables
docker run -d --name myapp-container \
  -p 3000:3000 \
  -e NODE_ENV=production \
  myapp:1.0

# Run with volume mounts
docker run -d --name myapp-container \
  -p 3000:3000 \
  -v /host/data:/app/data \
  myapp:1.0

# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Stop container
docker stop myapp-container

# Remove container
docker rm myapp-container
```

### 6. Debug Container Issues

When containers fail to start or behave unexpectedly:

1. **Check container logs**
   ```bash
   docker logs myapp-container
   ```

2. **Inspect container configuration**
   ```bash
   docker inspect myapp-container
   ```

3. **Execute commands in running container**
   ```bash
   docker exec -it myapp-container /bin/bash
   ```

4. **Check container resource usage**
   ```bash
   docker stats myapp-container
   ```

### 7. Optimize Image Size and Performance

Advanced optimization techniques:

1. **Use .dockerignore file**
   ```
   node_modules
   .git
   *.log
   .env
   ```

2. **Minimize layers**
   - Combine RUN commands
   - Use multi-stage builds
   - Clean up in same layer as installation

3. **Use appropriate base images**
   - `alpine` variants for smaller size
   - `distroless` for minimal attack surface

4. **Cache optimization**
   - Order COPY commands from least to most frequently changing
   - Use build stages to separate build and runtime dependencies

## Examples

### Example 1: Node.js Web Application

**Dockerfile for a Node.js Express app:**

```dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy application code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start application
CMD ["npm", "start"]
```

**Build and run:**
```bash
docker build -t nodejs-webapp .
docker run -d -p 3000:3000 nodejs-webapp
```

### Example 2: Python Flask API

**Dockerfile for a Python Flask application:**

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
```

### Example 3: Multi-stage Build for Go Application

**Dockerfile for a Go application:**

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Final stage
FROM alpine:latest

# Install ca-certificates for HTTPS requests
RUN apk --no-cache add ca-certificates

WORKDIR /root/

# Copy the binary from builder stage
COPY --from=builder /app/main .

# Expose port
EXPOSE 8080

# Run the binary
CMD ["./main"]
```

## Best Practices

### Image Creation
- Use specific version tags instead of `latest`
- Minimize image layers by combining commands
- Remove unnecessary files and caches
- Use multi-stage builds for smaller final images
- Test images in different environments

### Security
- Run containers as non-root users
- Keep base images updated
- Scan images for vulnerabilities
- Don't store secrets in images
- Use trusted base images

### Performance
- Optimize layer caching order
- Use appropriate base images
- Minimize image size
- Consider build context size
- Use buildkit for faster builds

### Container Management
- Use descriptive names for containers
- Clean up unused containers and images regularly
- Monitor resource usage
- Use health checks
- Implement proper logging

## Common Issues

**Issue**: Container exits immediately after starting
**Solution**: Check the CMD/ENTRYPOINT, ensure the application doesn't exit, verify dependencies are installed

**Issue**: Port already in use
**Solution**: Use different host ports with `-p` flag, or stop conflicting containers

**Issue**: No space left on device
**Solution**: Clean up unused images and containers with `docker system prune`

**Issue**: Permission denied errors
**Solution**: Check file permissions, ensure proper user setup in Dockerfile, avoid running as root

**Issue**: Slow builds
**Solution**: Optimize layer caching, use .dockerignore, consider using buildkit

## Additional Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/develop/dev-best-practices/#use-multi-stage-builds)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Supporting Files in This Skill

This skill includes several helpful resources:

- **`dockerfile-templates.md`** - Ready-to-use Dockerfile templates for Node.js, Python, Go, and multi-stage builds
- **`docker-compose-examples.yml`** - Sample docker-compose configurations for web apps, full-stack applications, development environments, and microservices
- **`dockerignore-template`** - Comprehensive .dockerignore templates for different programming languages and frameworks
- **`docker-manage.sh`** - Bash script for common Docker operations (build, run, cleanup, logging)
- **`README.md`** - Quick start guide and additional documentation

## Integration with Repository

When using this skill in the ai-dev repository:

1. Place Docker-related files in appropriate project directories
2. Use `docker-image-management` skill for containerization tasks
3. Consider creating docker-compose.yml for multi-container applications
4. Document container setup in project READMEs
5. Use GitHub Actions for automated building and testing of Docker images
# Docker Image Management Skill

This skill provides comprehensive guidance and tools for working with Docker containers and images. It covers everything from creating optimized Dockerfiles to managing container lifecycles and troubleshooting common issues.

## Files in This Skill

- **`SKILL.md`** - Main skill documentation with detailed instructions and best practices
- **`dockerfile-templates.md`** - Ready-to-use Dockerfile templates for different languages and frameworks
- **`docker-compose-examples.yml`** - Sample docker-compose configurations for various application architectures
- **`dockerignore-template`** - Comprehensive .dockerignore templates for different project types
- **`docker-manage.sh`** - Bash script for common Docker operations
- **`README.md`** - This file with overview and quick start guide

## Quick Start

### 1. Basic Containerization

For a simple Node.js application:

1. Copy a Dockerfile template from `dockerfile-templates.md`
2. Create a `.dockerignore` file based on `dockerignore-template`
3. Build and run using the management script:

```bash
# Make script executable
chmod +x docker-manage.sh

# Build image
./docker-manage.sh build myapp:v1.0

# Run container
./docker-manage.sh run myapp:v1.0 myapp-container 3000:3000
```

### 2. Multi-Container Applications

For applications requiring multiple services:

1. Copy a docker-compose configuration from `docker-compose-examples.yml`
2. Customize environment variables and service configurations
3. Run the application:

```bash
docker-compose up -d
```

### 3. Development Workflow

For development environments:

1. Use the development docker-compose example
2. Mount source code as volumes for hot reloading
3. Access debug ports for debugging

## Common Use Cases

### Web Applications
- Single-page applications (React, Vue, Angular)
- API servers (Express, Flask, Django)
- Full-stack applications

### Microservices
- Service mesh configurations
- API gateways
- Database services

### Development Environments
- Consistent development setup across team
- Isolated dependencies
- Easy onboarding for new developers

### CI/CD Pipelines
- Automated testing environments
- Build artifacts
- Deployment containers

## Best Practices Summary

### Image Optimization
- Use multi-stage builds to reduce image size
- Choose appropriate base images (Alpine for smaller size)
- Clean up caches and temporary files
- Use .dockerignore to exclude unnecessary files

### Security
- Run containers as non-root users
- Keep base images updated
- Don't store secrets in images
- Scan images for vulnerabilities

### Performance
- Optimize layer caching order
- Minimize number of layers
- Use buildkit for faster builds
- Consider image size vs build time trade-offs

## Troubleshooting

### Common Issues

**Container exits immediately:**
- Check CMD/ENTRYPOINT in Dockerfile
- Verify application dependencies are installed
- Check for missing environment variables

**Port conflicts:**
- Use different host ports
- Stop conflicting containers
- Check `docker ps` for running containers

**Permission denied:**
- Ensure proper user setup in Dockerfile
- Check file permissions on host
- Avoid running containers as root when possible

**Slow builds:**
- Optimize .dockerignore
- Reorder COPY commands for better caching
- Use multi-stage builds
- Enable BuildKit

### Debug Commands

```bash
# View container logs
docker logs <container_name>

# Execute commands in running container
docker exec -it <container_name> /bin/bash

# Inspect container configuration
docker inspect <container_name>

# Check container resource usage
docker stats <container_name>
```

## Integration with Development Workflow

### Version Control
- Commit Dockerfile and docker-compose.yml
- Consider committing docker-manage.sh for team use
- Use .dockerignore to exclude build artifacts

### CI/CD Integration
- Use GitHub Actions or other CI systems
- Build images automatically on commits
- Run tests in containers
- Deploy using container orchestration

### Team Collaboration
- Document container setup in project README
- Share common patterns and templates
- Establish naming conventions for images and containers

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Best Practices Guide](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)

## Contributing

When contributing to this skill:

1. Test all examples and scripts
2. Update documentation for new features
3. Follow the established patterns and conventions
4. Add examples for new use cases
5. Validate with the skill validation script from the skill-creator skill
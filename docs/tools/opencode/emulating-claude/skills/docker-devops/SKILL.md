---
name: docker-devops
description: Specialized skill for Docker containerization and DevOps workflows in the Happy Camper Planner project. Handles multi-service Docker Compose orchestration, PostgreSQL and Redis containers, .NET API and React webapp containerization, development environment setup, CI/CD pipelines, and production deployment optimization.
---

# Docker DevOps Skill for Happy Camper Planner

This skill provides specialized guidance for Docker containerization, development environment setup, and DevOps workflows in the Happy Camper Planner collaborative camping trip planning application.

## When to Use This Skill

Use this skill when you need to:
- Configure or troubleshoot Docker Compose services
- Optimize Dockerfiles for .NET API and React webapp
- Set up development containers and VS Code integration
- Create production-ready container configurations
- Implement CI/CD pipelines with Docker
- Debug container networking and connectivity issues
- Configure database and cache containers (PostgreSQL, Redis)
- Set up health checks and monitoring
- Optimize container build times and image sizes
- Handle environment-specific configurations

## Technology Context

### Container Stack
- **Docker Compose** for multi-service orchestration
- **PostgreSQL 16 Alpine** for primary database
- **Redis 7 Alpine** for caching and sessions
- **.NET 8 SDK** containers for API development
- **Node.js 20** containers for React webapp
- **Multi-stage builds** for production optimization

### Development Environment
```yaml
# Current docker-compose.yaml structure
services:
  db: postgres:16-alpine (port 5432)
  cache: redis:7-alpine (port 6379)
  api: .NET 8 development container (port 5000)
  webapp: React/Vite development container (port 3000)
```

### Connection Configuration
```bash
# Development database connection
Host=db;Database=happy_camper_db;Username=camper_admin;Password=dev_password_123

# Redis connection
host=cache:6379
```

## Docker Compose Management

### Complete Development Configuration
```yaml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:16-alpine
    container_name: happy-camper-db
    restart: always
    environment:
      POSTGRES_USER: camper_admin
      POSTGRES_PASSWORD: dev_password_123
      POSTGRES_DB: happy_camper_db
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
    networks:
      - camper-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U camper_admin -d happy_camper_db"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s

  # Redis Cache
  cache:
    image: redis:7-alpine
    container_name: happy-camper-cache
    restart: always
    command: redis-server --appendonly yes --requirepass dev_redis_password
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - camper-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 10s

  # .NET API Service
  api:
    build:
      context: ./src/api
      dockerfile: Dockerfile.dev
      target: development
    container_name: happy-camper-api
    restart: unless-stopped
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ASPNETCORE_URLS=http://+:8080
      - ConnectionStrings__DefaultConnection=Host=db;Database=happy_camper_db;Username=camper_admin;Password=dev_password_123
      - ConnectionStrings__Redis=cache:6379,password=dev_redis_password
      - Firebase__ProjectId=${FIREBASE_PROJECT_ID}
      - Firebase__ServiceAccountPath=/app/secrets/firebase-service-account.json
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    ports:
      - "5000:8080"
    volumes:
      - ./src/api:/app
      - ./secrets:/app/secrets:ro
      - api_packages:/root/.nuget/packages
    networks:
      - camper-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # React WebApp
  webapp:
    build:
      context: ./src/webapp
      dockerfile: Dockerfile.dev
      target: development
    container_name: happy-camper-webapp
    restart: unless-stopped
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://localhost:5000
      - VITE_FIREBASE_API_KEY=${FIREBASE_API_KEY}
      - VITE_FIREBASE_AUTH_DOMAIN=${FIREBASE_AUTH_DOMAIN}
      - VITE_FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
    depends_on:
      - api
    ports:
      - "3000:3000"
    volumes:
      - ./src/webapp:/app
      - webapp_node_modules:/app/node_modules
    networks:
      - camper-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # React Native Mobile (Development)
  mobile:
    build:
      context: ./src/mobile
      dockerfile: Dockerfile.dev
    container_name: happy-camper-mobile
    restart: unless-stopped
    environment:
      - EXPO_DEVTOOLS_LISTEN_ADDRESS=0.0.0.0
      - API_URL=http://api:8080
    depends_on:
      - api
    ports:
      - "19000:19000"  # Expo DevTools
      - "19001:19001"  # Expo Metro bundler
    volumes:
      - ./src/mobile:/app
      - mobile_node_modules:/app/node_modules
    networks:
      - camper-network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  api_packages:
    driver: local
  webapp_node_modules:
    driver: local
  mobile_node_modules:
    driver: local

networks:
  camper-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Environment-Specific Overrides
```yaml
# docker-compose.override.yml (development)
version: '3.8'
services:
  api:
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - Logging__LogLevel__Default=Debug
    volumes:
      - ./src/api:/app
      - ${APPDATA}/Microsoft/UserSecrets:/root/.microsoft/usersecrets:ro

  webapp:
    environment:
      - NODE_ENV=development
    command: npm run dev -- --host 0.0.0.0

# docker-compose.prod.yml (production)
version: '3.8'
services:
  db:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    secrets:
      - postgres_password

  api:
    build:
      target: production
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

secrets:
  postgres_password:
    external: true
```

## Dockerfile Optimization

### .NET API Multi-Stage Dockerfile
```dockerfile
# src/api/Dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

# Copy project files and restore dependencies
COPY ["*.csproj", "./"]
RUN dotnet restore --runtime alpine-x64

# Copy source code and build
COPY . .
RUN dotnet publish -c Release -o /app/publish \
    --runtime alpine-x64 \
    --self-contained false \
    --no-restore

# Development stage
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS development
WORKDIR /app
RUN apk add --no-cache curl
COPY . .
RUN dotnet restore
ENTRYPOINT ["dotnet", "watch", "run", "--urls", "http://0.0.0.0:8080"]

# Production stage  
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS production
WORKDIR /app

# Install security updates and required packages
RUN apk upgrade --no-cache && \
    apk add --no-cache curl tzdata && \
    adduser --disabled-password --home /app --gecos '' appuser && \
    chown -R appuser /app

# Copy published application
COPY --from=build /app/publish .

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
ENTRYPOINT ["dotnet", "HappyCamper.Api.dll"]
```

### React WebApp Multi-Stage Dockerfile
```dockerfile
# src/webapp/Dockerfile
FROM node:20-alpine AS base
WORKDIR /app
RUN apk add --no-cache libc6-compat curl

# Development stage
FROM base AS development
COPY package*.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM base AS build
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
COPY . .
RUN npm run build

# Production stage
FROM nginx:1.24-alpine AS production
RUN apk upgrade --no-cache

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### React Native Dockerfile
```dockerfile
# src/mobile/Dockerfile.dev
FROM node:20-alpine
WORKDIR /app

RUN apk add --no-cache git python3 make g++

# Install Expo CLI
RUN npm install -g @expo/cli

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

EXPOSE 19000 19001 19002

CMD ["npx", "expo", "start", "--tunnel"]
```

## Development Environment Setup

### VS Code DevContainer Configuration
```json
// .devcontainer/api/devcontainer.json
{
  "name": "Happy Camper API",
  "dockerComposeFile": ["../../docker-compose.yml", "docker-compose.devcontainer.yml"],
  "service": "api-dev",
  "workspaceFolder": "/app",
  "shutdownAction": "stopCompose",
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-dotnettools.csharp",
        "ms-dotnettools.csdevkit", 
        "ms-vscode.vscode-json",
        "bradlc.vscode-tailwindcss",
        "esbenp.prettier-vscode"
      ],
      "settings": {
        "dotnet.defaultSolution": "HappyCamper.sln"
      }
    }
  },

  "forwardPorts": [5000, 5432, 6379],
  "portsAttributes": {
    "5000": {
      "label": "API",
      "onAutoForward": "notify"
    }
  },

  "postCreateCommand": "dotnet restore",
  "remoteUser": "root"
}
```

```yaml
# .devcontainer/api/docker-compose.devcontainer.yml
version: '3.8'
services:
  api-dev:
    build:
      context: ../../src/api
      dockerfile: Dockerfile.dev
    volumes:
      - ../../:/workspace:cached
      - api-extensions:/root/.vscode-server/extensions
    command: sleep infinity
    depends_on:
      - db
      - cache

volumes:
  api-extensions:
```

### Docker Commands and Scripts

**Development Commands**
```bash
#!/bin/bash
# scripts/dev.sh

echo "Starting Happy Camper development environment..."

# Pull latest images
docker-compose pull

# Build and start services
docker-compose up -d --build

# Wait for services to be healthy
echo "Waiting for services to be ready..."
docker-compose exec db pg_isready -U camper_admin -d happy_camper_db
docker-compose exec cache redis-cli ping

# Run database migrations
echo "Running database migrations..."
docker-compose exec api dotnet ef database update

# Show service status
docker-compose ps

echo "Environment ready! Services available at:"
echo "  - API: http://localhost:5000"
echo "  - WebApp: http://localhost:3000"
echo "  - Database: localhost:5432"
echo "  - Redis: localhost:6379"
```

**Production Deployment Script**
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}

echo "Deploying Happy Camper to $ENVIRONMENT..."

# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Tag images for registry
docker tag happy-camper-api:latest gcr.io/happy-camper-project/api:$IMAGE_TAG
docker tag happy-camper-webapp:latest gcr.io/happy-camper-project/webapp:$IMAGE_TAG

# Push to registry
docker push gcr.io/happy-camper-project/api:$IMAGE_TAG
docker push gcr.io/happy-camper-project/webapp:$IMAGE_TAG

# Deploy to environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Deploying to production..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else
    echo "Deploying to staging..."
    docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
fi

echo "Deployment complete!"
```

## Database Management

### PostgreSQL Container Configuration
```yaml
# Database initialization
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_MULTIPLE_DATABASES: happy_camper_db,happy_camper_test
      POSTGRES_USER: camper_admin
      POSTGRES_PASSWORD: dev_password_123
    volumes:
      - ./scripts/create-multiple-postgresql-databases.sh:/docker-entrypoint-initdb.d/create-multiple-postgresql-databases.sh:ro
      - ./scripts/init-extensions.sql:/docker-entrypoint-initdb.d/init-extensions.sql:ro
      - postgres_data:/var/lib/postgresql/data
```

```sql
-- scripts/init-extensions.sql
-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create additional databases for testing
SELECT 'CREATE DATABASE happy_camper_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'happy_camper_test')\gexec
```

### Database Migration and Seeding
```bash
# Database management commands
docker-compose exec api dotnet ef migrations add InitialCreate
docker-compose exec api dotnet ef database update
docker-compose exec api dotnet run --seed-data

# Backup and restore
docker-compose exec db pg_dump -U camper_admin happy_camper_db > backup.sql
docker-compose exec -T db psql -U camper_admin happy_camper_db < backup.sql
```

## CI/CD Pipeline Configuration

### GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yml
name: Happy Camper CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: gcr.io
  PROJECT_ID: happy-camper-project

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: camper_admin
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: happy_camper_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup .NET
        uses: actions/setup-dotnet@v3
        with:
          dotnet-version: 8.0.x
          
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: src/webapp/package-lock.json
      
      - name: Restore .NET dependencies
        run: dotnet restore src/api
        
      - name: Install Node dependencies
        run: npm ci
        working-directory: src/webapp
      
      - name: Run .NET tests
        env:
          ConnectionStrings__DefaultConnection: Host=localhost;Database=happy_camper_test;Username=camper_admin;Password=test_password
          ConnectionStrings__Redis: localhost:6379
        run: |
          dotnet test src/api --no-restore --verbosity normal \
            --collect:"XPlat Code Coverage" \
            --results-directory ./coverage
      
      - name: Run React tests
        run: npm test -- --coverage --watchAll=false
        working-directory: src/webapp
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          directory: ./coverage
          flags: unittests

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          credentials_json: ${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}
      
      - name: Configure Docker for GCR
        run: gcloud auth configure-docker gcr.io
      
      - name: Build Docker images
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
          docker tag happy-camper-api:latest $REGISTRY/$PROJECT_ID/api:$GITHUB_SHA
          docker tag happy-camper-webapp:latest $REGISTRY/$PROJECT_ID/webapp:$GITHUB_SHA
      
      - name: Push to Container Registry
        run: |
          docker push $REGISTRY/$PROJECT_ID/api:$GITHUB_SHA
          docker push $REGISTRY/$PROJECT_ID/webapp:$GITHUB_SHA
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy happy-camper-api \
            --image $REGISTRY/$PROJECT_ID/api:$GITHUB_SHA \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --set-env-vars="ASPNETCORE_ENVIRONMENT=Production"
          
          gcloud run deploy happy-camper-webapp \
            --image $REGISTRY/$PROJECT_ID/webapp:$GITHUB_SHA \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated
```

## Monitoring and Health Checks

### Application Health Endpoints
```csharp
// API Health Check Implementation
app.MapHealthChecks("/health", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready"),
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});

// Register health checks
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, tags: new[] { "ready" })
    .AddRedis(redisConnectionString, tags: new[] { "ready" })
    .AddUrlGroup(new Uri("https://firebase.googleapis.com"), name: "firebase", tags: new[] { "external" });
```

### Container Monitoring with Prometheus
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: happy-camper-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    networks:
      - camper-network

  grafana:
    image: grafana/grafana:latest
    container_name: happy-camper-grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards:ro
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    networks:
      - camper-network

volumes:
  prometheus_data:
  grafana_data:
```

## Security and Best Practices

### Security Hardening
```dockerfile
# Security-hardened base image
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS production

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Install security updates
RUN apk upgrade --no-cache && \
    apk add --no-cache curl ca-certificates && \
    rm -rf /var/cache/apk/*

# Set proper ownership
WORKDIR /app
COPY --from=build --chown=appuser:appgroup /app/publish .

# Use non-root user
USER appuser

# Remove unnecessary capabilities
USER 1001:1001
```

### Secret Management
```yaml
# Use Docker secrets for production
version: '3.8'
services:
  api:
    secrets:
      - database_password
      - firebase_service_account
      - jwt_signing_key
    environment:
      - ConnectionStrings__DefaultConnection_FILE=/run/secrets/database_password
      - Firebase__ServiceAccountPath=/run/secrets/firebase_service_account

secrets:
  database_password:
    external: true
  firebase_service_account:
    external: true
  jwt_signing_key:
    external: true
```

## Troubleshooting Guide

### Common Docker Issues

**Issue: Port Already in Use**
```bash
# Find and kill process using port
lsof -ti:5000 | xargs kill -9
# Or use different port in docker-compose.yml
ports:
  - "5001:8080"  # Changed from 5000:8080
```

**Issue: Database Connection Failed**
```bash
# Check database container logs
docker-compose logs db

# Connect to database directly
docker-compose exec db psql -U camper_admin -d happy_camper_db

# Reset database volume
docker-compose down -v
docker-compose up db
```

**Issue: Out of Disk Space**
```bash
# Clean up Docker resources
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Check disk usage
docker system df
```

**Issue: Container Won't Start**
```bash
# Check container logs
docker-compose logs api

# Run container in interactive mode for debugging
docker-compose run --rm api sh

# Check container resource usage
docker stats
```

### Performance Optimization

**Build Cache Optimization**
```dockerfile
# Layer caching for faster builds
COPY package*.json ./
RUN npm ci --only=production

# Copy source files last (changes more frequently)
COPY . .
```

**Multi-Stage Build Cleanup**
```dockerfile
# Remove development dependencies in production
FROM node:20-alpine AS deps
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS build  
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
# deps layer not included in final image
```

## Environment Configuration

### Development Environment File
```bash
# .env.development
COMPOSE_PROJECT_NAME=happy-camper-dev
POSTGRES_PASSWORD=dev_password_123
REDIS_PASSWORD=dev_redis_password
FIREBASE_PROJECT_ID=happy-camper-dev
API_BASE_URL=http://localhost:5000
WEBAPP_PORT=3000
API_PORT=5000
```

### Production Environment
```bash
# .env.production
COMPOSE_PROJECT_NAME=happy-camper-prod
POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
REDIS_PASSWORD_FILE=/run/secrets/redis_password  
FIREBASE_PROJECT_ID=happy-camper-production
API_BASE_URL=https://api.happycamper.app
```

Remember: This skill automatically activates when working on Docker, containerization, or DevOps tasks. Always prioritize security, performance, and maintainability in your container configurations.
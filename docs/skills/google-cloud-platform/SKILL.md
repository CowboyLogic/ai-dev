---
name: google-cloud-platform
description: Expert knowledge of Google Cloud Platform services, tools, and best practices for development, deployment, and operations. Use this when working with GCP projects, services, infrastructure, or troubleshooting GCP-related issues.
license: MIT
---

# Google Cloud Platform Development Skill

This skill provides comprehensive guidance for working with Google Cloud Platform (GCP), covering project setup, service deployment, infrastructure management, security, and operational best practices.

## When to Use This Skill

Use this skill when:
- Setting up new GCP projects or organizations
- Deploying applications to GCP services (Cloud Run, App Engine, Kubernetes Engine)
- Managing GCP infrastructure with Terraform, Deployment Manager, or gcloud
- Working with GCP databases (BigQuery, Cloud SQL, Firestore, Spanner)
- Configuring GCP networking, load balancing, and CDN
- Implementing security, IAM, and compliance measures
- Setting up monitoring, logging, and alerting with Cloud Operations
- Optimizing costs and managing billing
- Troubleshooting GCP service issues or performance problems
- Migrating applications to GCP from other platforms

## Prerequisites

- Active Google Cloud account with billing enabled
- gcloud CLI installed and configured (`gcloud init`)
- Appropriate IAM permissions for the tasks
- Basic understanding of cloud computing concepts
- Project-specific requirements (APIs enabled, service accounts created)

## Instructions

### 1. Project and Environment Setup

1. **Authenticate and Configure gcloud**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   gcloud config set compute/region us-central1
   gcloud config set compute/zone us-central1-a
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable container.googleapis.com
   # Enable other APIs as needed
   ```

3. **Create Service Accounts (if needed)**
   ```bash
   gcloud iam service-accounts create my-service-account \
     --description="Service account for my application" \
     --display-name="My Service Account"
   ```

### 2. Infrastructure Management

1. **Use Terraform for Infrastructure as Code**
   - Initialize Terraform: `terraform init`
   - Plan changes: `terraform plan`
   - Apply changes: `terraform apply`

2. **Follow GCP Resource Naming Conventions**
   - Use consistent prefixes and suffixes
   - Include environment indicators (dev, staging, prod)
   - Use hyphens for readability

### 3. Application Deployment

1. **Choose the Right Compute Service**
   - **Cloud Run**: For containerized applications
   - **App Engine**: For web applications
   - **Kubernetes Engine**: For complex, scalable applications
   - **Compute Engine**: For custom VMs

2. **Deploy to Cloud Run (Example)**
   ```bash
   gcloud run deploy my-service \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENVIRONMENT=production
   ```

3. **Set Up CI/CD Pipelines**
   - Use Cloud Build for automated builds
   - Integrate with GitHub Actions or other CI tools
   - Implement blue-green or canary deployments

### 4. Database and Storage

1. **Select Appropriate Database Service**
   - **BigQuery**: For data analytics and warehousing
   - **Cloud SQL**: For relational databases (MySQL, PostgreSQL)
   - **Firestore**: For NoSQL document database
   - **Cloud Spanner**: For globally distributed relational database

2. **Configure Backups and High Availability**
   ```bash
   # Cloud SQL backup example
   gcloud sql backups create my-instance-backup \
     --instance my-instance
   ```

3. **Use Cloud Storage for Static Assets**
   ```bash
   gsutil mb gs://my-bucket
   gsutil cp file.txt gs://my-bucket/
   ```

### 5. Security and Networking

1. **Implement Least Privilege IAM**
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="user:email@example.com" \
     --role="roles/viewer"
   ```

2. **Configure VPC Networks**
   ```bash
   gcloud compute networks create my-network \
     --subnet-mode=custom
   ```

3. **Set Up Load Balancers and CDN**
   ```bash
   gcloud compute url-maps create my-load-balancer \
     --default-service my-backend-service
   ```

### 6. Monitoring and Operations

1. **Enable Cloud Monitoring and Logging**
   ```bash
   gcloud monitoring dashboards create my-dashboard \
     --config-from-file=dashboard.json
   ```

2. **Set Up Alerts and Notifications**
   ```bash
   gcloud alpha monitoring policies create my-alert-policy \
     --policy-from-file=alert-policy.json
   ```

3. **Use Cloud Trace for Performance Monitoring**
   - Enable tracing in your applications
   - Analyze latency and bottlenecks

## Examples

### Example 1: Deploying a Web Application to App Engine

```yaml
# app.yaml
runtime: python39
env: standard

handlers:
- url: /.*
  script: auto
```

```bash
gcloud app deploy
gcloud app browse
```

### Example 2: Creating a BigQuery Dataset and Loading Data

```bash
# Create dataset
bq mk --dataset \
  --description "My dataset description" \
  my_dataset

# Create table
bq mk --table my_dataset.my_table schema.json

# Load data
bq load --source_format=CSV \
  my_dataset.my_table \
  gs://my-bucket/data.csv \
  column1:STRING,column2:INTEGER
```

### Example 3: Setting Up a Kubernetes Cluster

```bash
# Create cluster
gcloud container clusters create my-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

# Get credentials
gcloud container clusters get-credentials my-cluster \
  --zone=us-central1-a

# Deploy application
kubectl apply -f deployment.yaml
```

## Best Practices

- **Resource Organization**: Use folders, projects, and labels for organization
- **Cost Management**: Set up billing budgets and alerts
- **Security**: Implement defense in depth with IAM, VPC, and security scanning
- **Performance**: Use appropriate machine types and autoscaling
- **Reliability**: Implement multi-region deployments for critical applications
- **Monitoring**: Set up comprehensive logging and monitoring from day one
- **Automation**: Use Infrastructure as Code for reproducible deployments
- **Compliance**: Follow GCP compliance certifications and regional requirements

## Common Issues and Solutions

**Issue**: `gcloud: command not found`
**Solution**: Install gcloud CLI from https://cloud.google.com/sdk/docs/install

**Issue**: Authentication timeout
**Solution**: Run `gcloud auth login` to refresh authentication

**Issue**: API not enabled error
**Solution**: Enable the required API in GCP Console or use:
```bash
gcloud services enable SERVICE_NAME.googleapis.com
```

**Issue**: Quota exceeded
**Solution**: Check quotas in GCP Console and request increases if needed

**Issue**: Deployment failures
**Solution**: Check Cloud Build logs and ensure proper permissions

**Issue**: High costs
**Solution**: Use cost calculators, set budgets, and monitor usage with billing reports

## Additional Resources

- [GCP Documentation](https://cloud.google.com/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
- [GCP Best Practices](https://cloud.google.com/docs/best-practices)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)
- [GCP Well-Architected Framework](https://cloud.google.com/architecture/framework)

## Related Skills

- `terraform-infrastructure`: For advanced Infrastructure as Code
- `kubernetes-management`: For container orchestration
- `database-administration`: For database-specific tasks
- `security-auditing`: For security assessments
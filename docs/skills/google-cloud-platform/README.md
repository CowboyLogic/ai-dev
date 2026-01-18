# Google Cloud Platform Development Skill

This skill provides expert knowledge and comprehensive guidance for working with Google Cloud Platform (GCP), covering everything from project setup and infrastructure management to application deployment and operational best practices.

## Overview

The Google Cloud Platform skill equips AI agents and developers with deep expertise in GCP services and tools, enabling them to:

- Set up and configure GCP projects with proper security and organization
- Deploy applications using appropriate GCP compute services
- Manage infrastructure with Infrastructure as Code principles
- Work with GCP databases, storage, and analytics services
- Implement security, monitoring, and cost optimization best practices
- Troubleshoot common GCP issues and performance problems

## What's Included

- **`SKILL.md`** - Main skill file with detailed instructions and best practices
- **`README.md`** - This overview file

## Key Features

### Comprehensive GCP Coverage
- **Compute Services**: Cloud Run, App Engine, Kubernetes Engine, Compute Engine
- **Database Services**: BigQuery, Cloud SQL, Firestore, Cloud Spanner
- **Storage & Networking**: Cloud Storage, VPC networks, load balancers, CDN
- **Developer Tools**: Cloud Build, Cloud Source Repositories, Cloud Functions
- **Operations**: Cloud Monitoring, Cloud Logging, Cloud Trace

### Infrastructure Management
- Terraform integration for Infrastructure as Code
- Resource naming conventions and organization
- Multi-environment deployments (dev/staging/prod)
- Cost optimization and budget management

### Security & Compliance
- Identity and Access Management (IAM) best practices
- VPC network security and firewall rules
- Service account management
- Compliance with GCP security standards

### Operational Excellence
- Monitoring and alerting setup
- Logging and tracing implementation
- Performance optimization techniques
- Disaster recovery and high availability

## Usage

### Project Setup and Authentication

When starting a new GCP project:

1. **Authenticate with GCP**
   ```bash
   gcloud auth login
   gcloud config set project your-project-id
   ```

2. **Enable required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable container.googleapis.com
   ```

3. **Set up service accounts and IAM roles** as needed for your application

### Application Deployment

Choose the right deployment strategy based on your application:

- **Containerized apps** → Cloud Run for serverless containers
- **Web applications** → App Engine for managed platforms
- **Complex microservices** → Kubernetes Engine for orchestration
- **Custom infrastructure** → Compute Engine for full control

### Infrastructure as Code

Use Terraform for reproducible infrastructure:

```hcl
resource "google_cloud_run_service" "my_service" {
  name     = "my-service"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/my-project/my-image:latest"
      }
    }
  }
}
```

### Database Selection and Management

Select the appropriate database service:

- **BigQuery** - Data warehousing and analytics
- **Cloud SQL** - Managed relational databases
- **Firestore** - NoSQL document database
- **Cloud Spanner** - Globally distributed relational database

## Examples

### Deploy to Cloud Run

```bash
gcloud run deploy my-app \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Create BigQuery Dataset

```bash
bq mk --dataset my_dataset
bq load my_dataset.my_table data.csv schema.json
```

### Set Up Kubernetes Cluster

```bash
gcloud container clusters create my-cluster \
  --num-nodes=3 \
  --zone=us-central1-a
```

## Best Practices

- **Resource Organization**: Use consistent naming, labels, and folder structures
- **Security First**: Implement least privilege IAM and secure network configurations
- **Cost Awareness**: Set up budgets, monitor usage, and optimize resource sizing
- **Monitoring**: Enable comprehensive logging and alerting from the start
- **Automation**: Use Infrastructure as Code and CI/CD pipelines
- **Compliance**: Follow GCP's security and compliance guidelines

## Common Scenarios

### Web Application Deployment
- Use App Engine for simple web apps
- Implement Cloud SQL for relational data
- Set up Cloud Storage for static assets
- Configure Cloud CDN for global performance

### Data Analytics Pipeline
- Ingest data into Cloud Storage
- Process with Dataflow or Dataproc
- Store results in BigQuery
- Visualize with Data Studio

### Microservices Architecture
- Deploy services to Cloud Run or GKE
- Use Cloud Pub/Sub for messaging
- Implement API Gateway for service management
- Set up distributed tracing with Cloud Trace

## Integration with Other Skills

This skill works well with:

- **Terraform Infrastructure** - For advanced Infrastructure as Code
- **Kubernetes Management** - For container orchestration details
- **Database Administration** - For database-specific optimization
- **Security Auditing** - For compliance and vulnerability assessments

## Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [GCP Best Practices](https://cloud.google.com/docs/best-practices)
- [GCP Well-Architected Framework](https://cloud.google.com/architecture/framework)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
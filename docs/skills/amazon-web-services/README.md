# Amazon Web Services Development Skill

This skill provides expert knowledge and comprehensive guidance for working with Amazon Web Services (AWS), covering everything from account setup and infrastructure management to application deployment and operational best practices.

## Overview

The Amazon Web Services skill equips AI agents and developers with deep expertise in AWS services and tools, enabling them to:

- Set up and configure AWS accounts with proper security and organization
- Deploy applications using appropriate AWS compute services
- Manage infrastructure with Infrastructure as Code principles
- Work with AWS databases, storage, and analytics services
- Implement security, monitoring, and cost optimization best practices
- Troubleshoot common AWS issues and performance problems

## What's Included

- **`SKILL.md`** - Main skill file with detailed instructions and best practices
- **`README.md`** - This overview file

## Key Features

### Comprehensive AWS Coverage
- **Compute Services**: EC2, Lambda, ECS, EKS, Elastic Beanstalk
- **Database Services**: RDS, DynamoDB, Redshift, Aurora
- **Storage & Networking**: S3, VPC, ELB, CloudFront
- **Developer Tools**: CodePipeline, CodeBuild, CloudFormation
- **Operations**: CloudWatch, CloudTrail, X-Ray

### Infrastructure Management
- CloudFormation integration for Infrastructure as Code
- Resource tagging conventions and organization
- Multi-environment deployments (dev/staging/prod)
- Cost optimization and budget management

### Security & Compliance
- Identity and Access Management (IAM) best practices
- Virtual Private Cloud (VPC) security and security groups
- AWS security services (WAF, Shield, GuardDuty)
- Compliance with AWS security standards

### Operational Excellence
- Monitoring and alerting setup with CloudWatch
- Logging and tracing implementation
- Performance optimization techniques
- Disaster recovery and high availability

## Usage

### Account Setup and Authentication

When starting a new AWS project:

1. **Configure AWS CLI**
   ```bash
   aws configure
   # Set your access key, secret key, and default region
   ```

2. **Create IAM users and roles**
   ```bash
   aws iam create-user --user-name developer
   aws iam attach-user-policy --user-name developer \
     --policy-arn arn:aws:iam::aws:policy/PowerUserAccess
   ```

3. **Set up billing alerts and budgets**

### Application Deployment

Choose the right deployment strategy based on your application:

- **Serverless functions** → AWS Lambda
- **Containerized apps** → ECS or EKS
- **Web applications** → Elastic Beanstalk
- **Custom infrastructure** → EC2 instances

### Infrastructure as Code

Use CloudFormation for reproducible infrastructure:

```yaml
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-unique-bucket-name

  MyFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-function
      Runtime: python3.9
      Handler: lambda_function.lambda_handler
      Code:
        S3Bucket: my-bucket
        S3Key: function.zip
      Role: !GetAtt MyRole.Arn
```

### Database Selection and Management

Select the appropriate database service:

- **RDS** - Managed relational databases
- **DynamoDB** - NoSQL document database
- **Redshift** - Data warehousing and analytics
- **Aurora** - High-performance MySQL/PostgreSQL

## Examples

### Deploy to AWS Lambda

```bash
aws lambda create-function --function-name hello-world \
  --runtime python3.9 \
  --role arn:aws:iam::account:role/lambda-role \
  --handler lambda_function.lambda_handler \
  --code S3Bucket=my-bucket,S3Key=function.zip
```

### Create S3 Bucket and Upload Files

```bash
aws s3 mb s3://my-app-bucket
aws s3 cp index.html s3://my-app-bucket/
aws s3 website s3://my-app-bucket/ --index-document index.html
```

### Set Up RDS Database

```bash
aws rds create-db-instance --db-instance-identifier my-database \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password mypassword \
  --allocated-storage 20
```

## Best Practices

- **Resource Tagging**: Use consistent tagging strategy for cost allocation and management
- **Security First**: Implement least privilege IAM and secure network configurations
- **Cost Awareness**: Set up budgets, use Reserved Instances, and monitor usage
- **Monitoring**: Enable comprehensive CloudWatch monitoring and alerting
- **Automation**: Use Infrastructure as Code and CI/CD pipelines
- **Compliance**: Follow AWS Well-Architected Framework guidelines

## Common Scenarios

### Serverless Web Application
- Use API Gateway and Lambda for backend
- Store data in DynamoDB
- Host static content on S3 with CloudFront
- Implement authentication with Cognito

### Containerized Microservices
- Deploy services to ECS or EKS
- Use ECR for container registry
- Implement service mesh with App Mesh
- Set up distributed tracing with X-Ray

### Data Analytics Pipeline
- Ingest data into S3
- Process with Glue or EMR
- Store results in Redshift
- Visualize with QuickSight

## Integration with Other Skills

This skill works well with:

- **Terraform Infrastructure** - For advanced Infrastructure as Code
- **Kubernetes Management** - For EKS cluster management
- **Database Administration** - For database-specific optimization
- **Security Auditing** - For compliance and vulnerability assessments

## Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/)
- [AWS Pricing Calculator](https://calculator.aws/)
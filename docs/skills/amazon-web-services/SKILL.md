---
name: amazon-web-services
description: Expert knowledge of Amazon Web Services (AWS) services, tools, and best practices for development, deployment, and operations. Use this when working with AWS projects, services, infrastructure, or troubleshooting AWS-related issues.
license: MIT
---

# Amazon Web Services Development Skill

This skill provides comprehensive guidance for working with Amazon Web Services (AWS), covering project setup, service deployment, infrastructure management, security, and operational best practices.

## When to Use This Skill

Use this skill when:
- Setting up new AWS accounts or organizations
- Deploying applications to AWS services (EC2, Lambda, ECS, EKS)
- Managing AWS infrastructure with CloudFormation or Terraform
- Working with AWS databases (RDS, DynamoDB, Redshift)
- Configuring AWS networking, load balancing, and CDN
- Implementing security, IAM, and compliance measures
- Setting up monitoring, logging, and alerting with CloudWatch
- Optimizing costs and managing billing
- Troubleshooting AWS service issues or performance problems
- Migrating applications to AWS from other platforms

## Prerequisites

- Active AWS account with billing enabled
- AWS CLI installed and configured (`aws configure`)
- Appropriate IAM permissions for the tasks
- Basic understanding of cloud computing concepts
- Project-specific requirements (IAM roles, VPC setup)

## Instructions

### 1. Account and Environment Setup

1. **Configure AWS CLI**
   ```bash
   aws configure
   # Or set environment variables
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

2. **Enable required services and APIs**
   - Most AWS services don't require explicit enabling
   - Ensure proper IAM permissions are in place

3. **Create IAM users, roles, and policies**
   ```bash
   aws iam create-user --user-name my-user
   aws iam attach-user-policy --user-name my-user --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
   ```

### 2. Infrastructure Management

1. **Use CloudFormation for Infrastructure as Code**
   ```bash
   aws cloudformation create-stack --stack-name my-stack --template-body file://template.yaml
   ```

2. **Follow AWS Resource Naming Conventions**
   - Use consistent prefixes and suffixes
   - Include environment indicators (dev, staging, prod)
   - Use hyphens for readability

### 3. Application Deployment

1. **Choose the Right Compute Service**
   - **Lambda**: For serverless functions
   - **EC2**: For virtual machines
   - **ECS/EKS**: For container orchestration
   - **Elastic Beanstalk**: For managed web applications

2. **Deploy to Lambda (Serverless Example)**
   ```bash
   aws lambda create-function --function-name my-function \
     --runtime python3.9 \
     --role arn:aws:iam::account:role/lambda-role \
     --handler lambda_function.lambda_handler \
     --code S3Bucket=my-bucket,S3Key=function.zip
   ```

3. **Set Up CI/CD Pipelines**
   - Use CodePipeline for automated deployments
   - Integrate with CodeBuild and CodeDeploy
   - Implement blue-green or canary deployments

### 4. Database and Storage

1. **Select Appropriate Database Service**
   - **RDS**: For managed relational databases (MySQL, PostgreSQL, etc.)
   - **DynamoDB**: For NoSQL document database
   - **Redshift**: For data warehousing
   - **Aurora**: For high-performance relational databases

2. **Configure Backups and High Availability**
   ```bash
   aws rds create-db-instance --db-instance-identifier my-db \
     --db-instance-class db.t3.micro \
     --engine mysql \
     --master-username admin \
     --master-user-password password \
     --allocated-storage 20 \
     --backup-retention-period 7
   ```

3. **Use S3 for Object Storage**
   ```bash
   aws s3 mb s3://my-bucket
   aws s3 cp file.txt s3://my-bucket/
   aws s3 sync ./local-dir s3://my-bucket/remote-dir
   ```

### 5. Security and Networking

1. **Implement Least Privilege IAM**
   ```bash
   aws iam create-policy --policy-name my-policy --policy-document file://policy.json
   aws iam attach-role-policy --role-name my-role --policy-arn arn:aws:iam::account:policy/my-policy
   ```

2. **Configure VPC Networks**
   ```bash
   aws ec2 create-vpc --cidr-block 10.0.0.0/16
   aws ec2 create-subnet --vpc-id vpc-12345678 --cidr-block 10.0.1.0/24
   ```

3. **Set Up Load Balancers and CDN**
   ```bash
   aws elbv2 create-load-balancer --name my-load-balancer \
     --subnets subnet-12345 subnet-67890 \
     --security-groups sg-12345
   ```

### 6. Monitoring and Operations

1. **Enable CloudWatch Monitoring and Logging**
   ```bash
   aws logs create-log-group --log-group-name my-log-group
   aws cloudwatch put-metric-alarm --alarm-name my-alarm \
     --alarm-description "High CPU usage" \
     --metric-name CPUUtilization \
     --namespace AWS/EC2 \
     --statistic Average \
     --period 300 \
     --threshold 70 \
     --comparison-operator GreaterThanThreshold
   ```

2. **Set Up Alerts and Notifications**
   - Use CloudWatch Alarms with SNS topics
   - Configure billing alerts

3. **Use X-Ray for Application Tracing**
   - Enable tracing in your applications
   - Analyze latency and bottlenecks

## Examples

### Example 1: Deploying a Web Application to Elastic Beanstalk

```bash
# Create application
aws elasticbeanstalk create-application --application-name my-app

# Create environment
aws elasticbeanstalk create-environment --application-name my-app \
  --environment-name my-env \
  --solution-stack-name "64bit Amazon Linux 2 v3.4.0 running Node.js 16"
```

### Example 2: Creating a DynamoDB Table and Loading Data

```bash
# Create table
aws dynamodb create-table --table-name my-table \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Put item
aws dynamodb put-item --table-name my-table \
  --item '{"id":{"S":"123"},"name":{"S":"John Doe"}}'
```

### Example 3: Setting Up an ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name my-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service --cluster my-cluster \
  --service-name my-service \
  --task-definition my-task \
  --desired-count 1
```

## Best Practices

- **Resource Organization**: Use resource tags extensively for cost tracking and management
- **Security**: Implement defense in depth with IAM, Security Groups, and WAF
- **Cost Management**: Use Cost Explorer, set up budgets, and monitor usage
- **Performance**: Choose appropriate instance types and use Auto Scaling
- **Reliability**: Implement Multi-AZ deployments for critical applications
- **Automation**: Use Infrastructure as Code and CI/CD pipelines
- **Compliance**: Follow AWS security best practices and compliance standards

## Common Issues and Solutions

**Issue**: Access denied errors
**Solution**: Check IAM permissions and ensure proper roles/policies are attached

**Issue**: Region-specific service availability
**Solution**: Verify service availability in your chosen region

**Issue**: API rate limiting
**Solution**: Implement exponential backoff and proper error handling

**Issue**: High costs
**Solution**: Use AWS Cost Explorer, set budgets, and optimize resource usage

**Issue**: Deployment failures
**Solution**: Check CloudWatch logs and ensure proper IAM permissions

## Additional Resources

- [AWS Documentation](https://docs.aws.amazon.com/)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/)
- [AWS Best Practices](https://aws.amazon.com/architecture/well-architected/)
- [AWS Pricing Calculator](https://calculator.aws/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## Related Skills

- `terraform-infrastructure`: For advanced Infrastructure as Code
- `kubernetes-management`: For container orchestration
- `database-administration`: For database-specific tasks
- `security-auditing`: For security assessments
---
name: azure
description: Expert knowledge of Microsoft Azure services, tools, and best practices for development, deployment, and operations. Use this when working with Azure projects, services, infrastructure, or troubleshooting Azure-related issues.
license: MIT
---

# Microsoft Azure Development Skill

This skill provides comprehensive guidance for working with Microsoft Azure, covering project setup, service deployment, infrastructure management, security, and operational best practices.

## When to Use This Skill

Use this skill when:
- Setting up new Azure subscriptions or resource groups
- Deploying applications to Azure services (App Service, Functions, AKS)
- Managing Azure infrastructure with ARM templates or Terraform
- Working with Azure databases (Azure SQL, Cosmos DB, Azure Database)
- Configuring Azure networking, load balancing, and CDN
- Implementing security, Azure AD, and compliance measures
- Setting up monitoring, logging, and alerting with Azure Monitor
- Optimizing costs and managing billing
- Troubleshooting Azure service issues or performance problems
- Migrating applications to Azure from other platforms

## Prerequisites

- Active Azure subscription with billing enabled
- Azure CLI installed and configured (`az login`)
- Appropriate Azure AD permissions for the tasks
- Basic understanding of cloud computing concepts
- Project-specific requirements (resource groups, service principals)

## Instructions

### 1. Subscription and Environment Setup

1. **Configure Azure CLI**
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   az configure --defaults location=eastus group=myResourceGroup
   ```

2. **Enable required services and providers**
   - Most Azure services don't require explicit enabling
   - Ensure proper Azure AD permissions are in place

3. **Create service principals and managed identities**
   ```bash
   az ad sp create-for-rbac --name myServicePrincipal \
     --role Contributor \
     --scopes /subscriptions/your-subscription-id
   ```

### 2. Infrastructure Management

1. **Use ARM templates for Infrastructure as Code**
   ```bash
   az deployment group create --resource-group myRG \
     --template-file template.json \
     --parameters parameters.json
   ```

2. **Follow Azure Resource Naming Conventions**
   - Use consistent prefixes and suffixes
   - Include environment indicators (dev, staging, prod)
   - Use hyphens for readability

### 3. Application Deployment

1. **Choose the Right Compute Service**
   - **Azure Functions**: For serverless functions
   - **App Service**: For web applications
   - **AKS**: For container orchestration
   - **Virtual Machines**: For custom infrastructure

2. **Deploy to Azure Functions (Serverless Example)**
   ```bash
   az functionapp create --resource-group myRG \
     --consumption-plan-location eastus \
     --runtime python \
     --runtime-version 3.9 \
     --functions-version 4 \
     --name myFunctionApp \
     --storage-account myStorageAccount
   ```

3. **Set Up CI/CD Pipelines**
   - Use Azure DevOps Pipelines for automated deployments
   - Integrate with GitHub Actions or other CI tools
   - Implement blue-green or canary deployments

### 4. Database and Storage

1. **Select Appropriate Database Service**
   - **Azure SQL Database**: For managed relational databases
   - **Cosmos DB**: For NoSQL globally distributed database
   - **Azure Database for PostgreSQL/MySQL**: For open-source databases
   - **Azure Synapse Analytics**: For data warehousing

2. **Configure Backups and High Availability**
   ```bash
   az sql db create --resource-group myRG \
     --server myServer \
     --name myDatabase \
     --service-objective S0 \
     --backup-storage-redundancy Geo
   ```

3. **Use Azure Storage for Object Storage**
   ```bash
   az storage account create --name mystorageaccount \
     --resource-group myRG \
     --location eastus \
     --sku Standard_LRS \
     --kind StorageV2

   az storage container create --name mycontainer \
     --account-name mystorageaccount
   ```

### 5. Security and Networking

1. **Implement Azure AD and RBAC**
   ```bash
   az role assignment create --assignee user@domain.com \
     --role Contributor \
     --scope /subscriptions/your-subscription-id
   ```

2. **Configure Virtual Networks**
   ```bash
   az network vnet create --resource-group myRG \
     --name myVNet \
     --address-prefix 10.0.0.0/16 \
     --subnet-name mySubnet \
     --subnet-prefix 10.0.0.0/24
   ```

3. **Set Up Load Balancers and CDN**
   ```bash
   az network lb create --resource-group myRG \
     --name myLoadBalancer \
     --frontend-ip-name myFrontEnd \
     --backend-pool-name myBackEndPool \
     --public-ip-address myPublicIP
   ```

### 6. Monitoring and Operations

1. **Enable Azure Monitor and Application Insights**
   ```bash
   az monitor diagnostic-settings create --name myDiagnosticSetting \
     --resource /subscriptions/subscription-id/resourceGroups/myRG/providers/Microsoft.Web/sites/myApp \
     --logs '[{"category": "AppServiceHTTPLogs", "enabled": true}]' \
     --metrics '[{"category": "AllMetrics", "enabled": true}]' \
     --workspace /subscriptions/subscription-id/resourceGroups/myRG/providers/Microsoft.OperationalInsights/workspaces/myWorkspace
   ```

2. **Set Up Alerts and Notifications**
   - Use Azure Monitor alerts with Action Groups
   - Configure billing alerts

3. **Use Application Insights for Application Monitoring**
   - Enable application insights in your applications
   - Analyze performance and usage metrics

## Examples

### Example 1: Deploying a Web Application to App Service

```bash
# Create resource group
az group create --name myRG --location eastus

# Create app service plan
az appservice plan create --name myAppServicePlan \
  --resource-group myRG \
  --sku FREE

# Create web app
az webapp create --resource-group myRG \
  --plan myAppServicePlan \
  --name myUniqueAppName \
  --runtime "PYTHON|3.9"
```

### Example 2: Creating a Cosmos DB and Loading Data

```bash
# Create Cosmos DB account
az cosmosdb create --name myCosmosDB \
  --resource-group myRG \
  --kind GlobalDocumentDB \
  --locations regionName=eastus failoverPriority=0

# Create database
az cosmosdb sql database create --account-name myCosmosDB \
  --resource-group myRG \
  --name myDatabase

# Create container
az cosmosdb sql container create --account-name myCosmosDB \
  --resource-group myRG \
  --database-name myDatabase \
  --name myContainer \
  --partition-key-path "/id"
```

### Example 3: Setting Up AKS Cluster

```bash
# Create AKS cluster
az aks create --resource-group myRG \
  --name myAKSCluster \
  --node-count 1 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group myRG \
  --name myAKSCluster
```

## Best Practices

- **Resource Organization**: Use resource groups and tags extensively for management
- **Security**: Implement defense in depth with Azure AD, NSGs, and Azure Security Center
- **Cost Management**: Use Azure Cost Management, set budgets, and monitor usage
- **Performance**: Choose appropriate VM sizes and use Azure Advisor
- **Reliability**: Implement availability zones and backup strategies
- **Automation**: Use ARM templates and Azure Policy for governance
- **Compliance**: Follow Azure's security and compliance frameworks

## Common Issues and Solutions

**Issue**: Authentication errors
**Solution**: Run `az login` and ensure proper Azure AD permissions

**Issue**: Resource quota exceeded
**Solution**: Check quotas in Azure Portal and request increases if needed

**Issue**: Deployment failures
**Solution**: Check Azure Activity Logs and resource deployment status

**Issue**: High costs
**Solution**: Use Azure Cost Management and Azure Advisor for optimization

**Issue**: Network connectivity issues
**Solution**: Verify NSG rules and VNet configurations

## Additional Resources

- [Azure Documentation](https://docs.microsoft.com/en-us/azure/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)
- [Azure Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/)
- [Azure Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## Related Skills

- `terraform-infrastructure`: For advanced Infrastructure as Code
- `kubernetes-management`: For AKS cluster management
- `database-administration`: For database-specific tasks
- `security-auditing`: For compliance and vulnerability assessments
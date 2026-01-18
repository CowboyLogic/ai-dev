# Microsoft Azure Development Skill

This skill provides expert knowledge and comprehensive guidance for working with Microsoft Azure, covering everything from subscription setup and infrastructure management to application deployment and operational best practices.

## Overview

The Microsoft Azure skill equips AI agents and developers with deep expertise in Azure services and tools, enabling them to:

- Set up and configure Azure subscriptions with proper security and organization
- Deploy applications using appropriate Azure compute services
- Manage infrastructure with Infrastructure as Code principles
- Work with Azure databases, storage, and analytics services
- Implement security, monitoring, and cost optimization best practices
- Troubleshoot common Azure issues and performance problems

## What's Included

- **`SKILL.md`** - Main skill file with detailed instructions and best practices
- **`README.md`** - This overview file

## Key Features

### Comprehensive Azure Coverage
- **Compute Services**: Virtual Machines, App Service, Functions, AKS
- **Database Services**: Azure SQL, Cosmos DB, Azure Database for PostgreSQL/MySQL
- **Storage & Networking**: Blob Storage, Virtual Networks, Load Balancers, CDN
- **Developer Tools**: Azure DevOps, Azure CLI, ARM templates
- **Operations**: Azure Monitor, Application Insights, Log Analytics

### Infrastructure Management
- ARM template integration for Infrastructure as Code
- Resource group and tagging conventions
- Multi-region deployments (dev/staging/prod)
- Cost optimization and budget management

### Security & Compliance
- Azure Active Directory (AAD) best practices
- Network Security Groups (NSGs) and Azure Firewall
- Azure Security Center and Azure Sentinel
- Compliance with Azure security standards

### Operational Excellence
- Monitoring and alerting setup with Azure Monitor
- Logging and tracing implementation
- Performance optimization techniques
- Disaster recovery and high availability

## Usage

### Subscription Setup and Authentication

When starting a new Azure project:

1. **Configure Azure CLI**
   ```bash
   az login
   az account set --subscription your-subscription-id
   ```

2. **Create resource groups and service principals**
   ```bash
   az group create --name myRG --location eastus
   az ad sp create-for-rbac --name myServicePrincipal --role Contributor
   ```

3. **Set up billing alerts and budgets**

### Application Deployment

Choose the right deployment strategy based on your application:

- **Serverless functions** → Azure Functions
- **Web applications** → App Service or Static Web Apps
- **Containerized apps** → AKS or Container Instances
- **Custom infrastructure** → Virtual Machines

### Infrastructure as Code

Use ARM templates for reproducible infrastructure:

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "resources": [
    {
      "type": "Microsoft.Storage/storageAccounts",
      "apiVersion": "2021-04-01",
      "name": "mystorageaccount",
      "location": "[resourceGroup().location]",
      "sku": {
        "name": "Standard_LRS"
      },
      "kind": "StorageV2"
    }
  ]
}
```

### Database Selection and Management

Select the appropriate database service:

- **Azure SQL Database** - Managed relational database
- **Cosmos DB** - Globally distributed NoSQL database
- **Azure Database for PostgreSQL/MySQL** - Managed open-source databases
- **Azure Synapse Analytics** - Enterprise data warehousing

## Examples

### Deploy to Azure Functions

```bash
az functionapp create --resource-group myRG \
  --consumption-plan-location eastus \
  --runtime node \
  --runtime-version 18 \
  --functions-version 4 \
  --name myFunctionApp \
  --storage-account myStorageAccount
```

### Create Azure Storage Account and Container

```bash
az storage account create --name mystorageaccount \
  --resource-group myRG \
  --location eastus \
  --sku Standard_LRS

az storage container create --name mycontainer \
  --account-name mystorageaccount \
  --auth-mode login
```

### Set Up Azure SQL Database

```bash
az sql server create --name myserver \
  --resource-group myRG \
  --location eastus \
  --admin-user myadmin \
  --admin-password myPassword123

az sql db create --resource-group myRG \
  --server myserver \
  --name mydatabase \
  --service-objective S0
```

## Best Practices

- **Resource Organization**: Use resource groups and consistent naming conventions
- **Security First**: Implement Azure AD authentication and NSG rules
- **Cost Awareness**: Set up budgets, use Azure Advisor, and monitor usage
- **Monitoring**: Enable comprehensive Azure Monitor and Application Insights
- **Automation**: Use ARM templates and Azure Policy for governance
- **Compliance**: Follow Azure's Well-Architected Framework guidelines

## Common Scenarios

### Serverless Web Application
- Use Azure Functions for backend APIs
- Store data in Cosmos DB
- Host frontend on Azure Static Web Apps
- Implement authentication with Azure AD B2C

### Enterprise Application
- Deploy to AKS for container orchestration
- Use Azure SQL Database for relational data
- Implement Azure Front Door for global CDN
- Set up Azure Monitor for comprehensive monitoring

### Data Analytics Pipeline
- Ingest data into Azure Data Lake Storage
- Process with Azure Synapse Analytics
- Store results in Azure SQL Data Warehouse
- Visualize with Power BI

## Integration with Other Skills

This skill works well with:

- **Terraform Infrastructure** - For advanced Infrastructure as Code
- **Kubernetes Management** - For AKS cluster management
- **Database Administration** - For database-specific optimization
- **Security Auditing** - For compliance and vulnerability assessments

## Resources

- [Azure Documentation](https://docs.microsoft.com/en-us/azure/)
- [Azure Well-Architected Framework](https://docs.microsoft.com/en-us/azure/architecture/framework/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)
- [Azure Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/)
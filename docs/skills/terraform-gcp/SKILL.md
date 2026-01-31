---
name: terraform-gcp
description: Guide for creating and managing Google Cloud Platform (GCP) infrastructure using Terraform. Includes examples, best practices, and common pitfalls.
license: MIT
---

# Terraform for Google Cloud Platform (GCP)

## Overview
This skill provides guidance for creating and managing Google Cloud Platform (GCP) infrastructure using Terraform. It includes examples for common resources, best practices, and troubleshooting tips.

## When to Use
Use this skill when:
- Automating the setup of GCP infrastructure.
- Managing existing GCP resources with Terraform.
- Learning best practices for Terraform and GCP integration.

## Step-by-Step Instructions

### 1. Prerequisites
Ensure the following are installed and configured:
- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- A GCP project with billing enabled
- A service account key with appropriate permissions

### 2. Authenticate with GCP
1. Create a service account in your GCP project.
2. Assign the necessary roles (e.g., `roles/editor`).
3. Download the service account key as a JSON file.
4. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
   ```

### 3. Initialize Terraform
1. Create a new directory for your Terraform configuration files.
2. Write a `main.tf` file with the following content:
   ```hcl
   provider "google" {
     project = "<your-project-id>"
     region  = "us-central1"
     zone    = "us-central1-a"
   }
   ```
3. Run the following commands:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

### 4. Create Resources
Add resource blocks to your `main.tf` file. For example, to create a Compute Engine instance:
```hcl
resource "google_compute_instance" "vm_instance" {
  name         = "example-instance"
  machine_type = "e2-medium"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }
}
```

### 5. Apply Changes
Run the following command to apply your configuration:
```bash
terraform apply
```

### 6. Manage State
- Use remote state storage (e.g., Google Cloud Storage) for collaboration.
- Lock state files to prevent conflicts.

## Examples
- **Compute Engine Instance**: See the `google_compute_instance` example above.
- **Cloud Storage Bucket**:
  ```hcl
  resource "google_storage_bucket" "example_bucket" {
    name     = "example-bucket"
    location = "US"
  }
  ```

## Best Practices
- Use modules to organize your Terraform code.
- Secure your service account key and avoid committing it to version control.
- Regularly update your Terraform provider plugins.

## Common Pitfalls
- **Misconfigured Credentials**: Ensure the `GOOGLE_APPLICATION_CREDENTIALS` variable points to the correct file.
- **State File Conflicts**: Use remote state storage and locking mechanisms.
- **Insufficient Permissions**: Verify that your service account has the necessary roles.

## Additional Resources
- [Terraform GCP Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Terraform Tutorials](https://cloud.google.com/docs/terraform)
# 🏗️ Terraform — Infrastructure as Code

## Overview

All AWS infrastructure is defined as code using **Terraform**.
One command creates everything needed to run the application.

---

## Resources Created

| Resource | Description |
|----------|-------------|
| `aws_instance` | EC2 t3.micro — Ubuntu 24.04 |
| `aws_eip` | Elastic IP — static public address |
| `aws_security_group` | Firewall rules |
| `aws_key_pair` | SSH key for EC2 access |

---

## File Structure
terraform/
├── main.tf       # All AWS resources
├── variables.tf  # Input variables
├── outputs.tf    # Output values (IP, SSH command)
└── userdata.sh   # EC2 bootstrap script
---

## Prerequisites

```bash
# Install Terraform
sudo apt install terraform -y

# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/pastebin -N ""
```

---

## Usage

### Initialize
```bash
cd terraform
terraform init
```

### Preview changes
```bash
terraform plan
```

### Apply infrastructure
```bash
terraform apply
```
Type `yes` when prompted.

### Get outputs
```bash
terraform output
```
Example output:
public_ip  = "18.184.216.234"
public_dns = "ec2-18-184-216-234.eu-central-1.compute.amazonaws.com"
ssh_command = "ssh -i ~/.ssh/pastebin ubuntu@18.184.216.234"
### Connect to EC2
```bash
ssh -i ~/.ssh/pastebin ubuntu@$(terraform output -raw public_ip)
```

### Destroy infrastructure
```bash
terraform destroy
```
⚠️ This will delete ALL resources including the EC2 instance and data.

---

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `region` | `eu-central-1` | AWS region |
| `ami` | Ubuntu 24.04 | EC2 AMI |
| `instance_type` | `t3.micro` | EC2 instance type |

---

## Security Group Rules

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | 0.0.0.0/0 | SSH access |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 443 | TCP | 0.0.0.0/0 | HTTPS |

---

## Cost Estimate

### Destroy infrastructure
```bash
terraform destroy
```
⚠️ This will delete ALL resources including the EC2 instance and data.

---

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `region` | `eu-central-1` | AWS region |
| `ami` | Ubuntu 24.04 | EC2 AMI |
| `instance_type` | `t3.micro` | EC2 instance type |

---

## Security Group Rules

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | 0.0.0.0/0 | SSH access |
| 80 | TCP | 0.0.0.0/0 | HTTP |
| 443 | TCP | 0.0.0.0/0 | HTTPS |

---

## Cost Estimate

| Resource | Monthly Cost |
|----------|-------------|
| t3.micro | ~$8.50 (free tier eligible) |
| Elastic IP | $0 (while attached) |
| 20GB EBS | ~$1.60 |
| **Total** | **~$10/mo** |

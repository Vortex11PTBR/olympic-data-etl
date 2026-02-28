# Ansible Deployment Guide - Olympic Data ETL

## Overview

Ansible automates the complete deployment of Olympic Data ETL to GCP and Azure, replacing the bash script with a modular, reproducible infrastructure-as-code approach.

**Benefits**:
- ✅ Idempotent operations (safe to run multiple times)
- ✅ Modular roles (reusable components)
- ✅ Error handling & rollback
- ✅ Detailed logging & reporting
- ✅ Multi-environment support (dev/staging/prod)
- ✅ Cloud-agnostic (works with GCP, Azure, AWS)

---

## Installation

### 1. Install Ansible

```bash
# Using pip (recommended)
pip install ansible>=2.14.0

# Or using system package manager
apt-get install ansible  # Ubuntu/Debian
brew install ansible     # macOS
choco install ansible    # Windows (via Chocolatey)
```

### 2. Install Ansible Collections & Roles

```bash
# Install from requirements file
ansible-galaxy install -r ansible/requirements.yml

# Or install individually
ansible-galaxy collection install google.cloud
ansible-galaxy collection install azure.azcollection
ansible-galaxy collection install community.general
ansible-galaxy collection install community.docker
```

### 3. Configure GCP Credentials

```bash
# Authenticate with GCP
gcloud auth login
gcloud config set project your-gcp-project-id

# Create service account for Ansible
gcloud iam service-accounts create ansible-sa \
  --display-name="Ansible Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding your-gcp-project-id \
  --member=serviceAccount:ansible-sa@your-gcp-project-id.iam.gserviceaccount.com \
  --role=roles/editor

# Create key
gcloud iam service-accounts keys create ~/ansible-gcp-key.json \
  --iam-account=ansible-sa@your-gcp-project-id.iam.gserviceaccount.com

# Export credentials
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/ansible-gcp-key.json"
```

---

## Usage

### 1. Configure Inventory

Edit `ansible/inventory/hosts.yml`:

```yaml
all:
  vars:
    gcp_project_id: "your-gcp-project"
    gcp_region: "us-central1"
    environment: "dev"  # or staging, prod
    slack_webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK"
  hosts:
    localhost:
      ansible_connection: local
```

### 2. Deploy to Development

```bash
# Deploy full stack
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev"

# Deploy only GCP
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev" \
  --tags "gcp"

# Deploy with verbose output
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev" \
  -vvv
```

### 3. Deploy to Production

```bash
# Apply deployment (requires confirmation)
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=prod" \
  --ask-become-pass

# Skip confirmation (careful!)
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=prod" \
  --extra-vars="skip_confirmation=true"
```

### 4. Run Pipeline

```bash
# Run DirectRunner (local)
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "environment=dev" \
  -e "runner_type=DirectRunner"

# Run DataflowRunner (GCP)
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "environment=prod" \
  -e "runner_type=DataflowRunner"

# Custom parameters
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "environment=dev" \
  -e "runner_type=DataflowRunner" \
  -e "dataflow_workers=5" \
  -e "dataflow_max_workers=50"
```

### 5. Verify Deployment

```bash
# Run verification
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml \
  -e "environment=dev"

# Check GCP resources only
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml \
  -e "environment=dev" \
  --tags "gcp"
```

---

## Ansible Playbooks

### deploy.yml

Main deployment playbook that orchestrates infrastructure setup.

**Roles executed (in order)**:
1. `gcp-setup` - Enables APIs, creates service account, sets up storage
2. `bigquery-setup` - Creates dataset, tables, materialized views
3. `dataflow-deploy` - Builds Docker image, deploys Beam template
4. `docker-setup` - Installs Docker, pulls images

**Usage**:
```bash
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -e "environment=dev"
```

**Output**:
- Service account credential file
- GCP resources (APIs, buckets, dataset)
- Dataflow template ready for execution
- Docker environment configured

---

### run-pipeline.yml

Executes the Olympic ETL pipeline on Dataflow or locally.

**Options**:
- `runner_type`: `DirectRunner` (local) or `DataflowRunner` (GCP)
- `job_timeout`: Seconds (default: 1800)
- `parallelism`: Worker parallelism (default: 10)

**Usage**:
```bash
# Local execution
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DirectRunner"

# Cloud execution
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DataflowRunner"
```

**Monitors**:
- Job execution status
- Error handling with DLQ
- Performance metrics
- Slack notifications

---

### verify.yml

Verifies all deployed components and generates health report.

**Checks**:
- GCP authentication status
- BigQuery dataset & tables
- Cloud Storage buckets
- Dataflow templates
- Docker daemon
- Overall deployment health

**Usage**:
```bash
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/verify.yml -e "environment=dev"
```

**Output**:
- Comprehensive verification report
- Resource readiness status
- Recommendations for issues

---

## Ansible Roles

### gcp-setup

**Purpose**: Initialize GCP infrastructure

**Tasks**:
1. Enable required APIs (9 services)
2. Create service account
3. Grant IAM roles (5 roles)
4. Create service account key
5. Create Cloud Storage buckets (4)
6. Configure bucket lifecycle policies

**Output Variables**:
- `gcp_service_account_email`
- `sa_key_file.dest` (path to credentials)

**Tags**: `gcp`, `setup`

---

### bigquery-setup

**Purpose**: Create BigQuery dataset, tables, and views

**Tasks**:
1. Create BQ dataset
2. Create medals table with schema
3. Create materialized views:
   - `daily_medal_counts`
   - `athlete_totals`
4. Verify table creation

**Output Variables**:
- `bq_dataset`
- `bq_table`

**Tags**: `gcp`, `bigquery`

---

### dataflow-deploy

**Purpose**: Build and deploy Dataflow Flex Template

**Tasks**:
1. Check template existence
2. Create Artifact Registry
3. Build Docker image
4. Push to Artifact Registry
5. Build Dataflow Flex Template
6. Create deployment manifest
7. Configure Cloud Scheduler

**Output Files**:
- `manifests/dataflow-{{ environment }}-manifest.json`

**Tags**: `gcp`, `dataflow`

---

### docker-setup

**Purpose**: Install and configure Docker

**Tasks**:
1. Install Python 3
2. Install Docker CE
3. Start Docker daemon
4. Configure user permissions
5. Pull docker-compose images
6. Create override files

**Tags**: `docker`

---

## Directory Structure

```
olympic-data-etl/
├── ansible/
│   ├── roles/
│   │   ├── gcp-setup/
│   │   │   └── tasks/main.yml
│   │   ├── bigquery-setup/
│   │   │   └── tasks/main.yml
│   │   ├── dataflow-deploy/
│   │   │   └── tasks/main.yml
│   │   └── docker-setup/
│   │       └── tasks/main.yml
│   ├── playbooks/
│   │   ├── deploy.yml
│   │   ├── run-pipeline.yml
│   │   └── verify.yml
│   ├── inventory/
│   │   └── hosts.yml
│   ├── logs/
│   └── requirements.yml
├── ansible.cfg
└── ANSIBLE_DEPLOY.md (this file)
```

---

## Variables Reference

### Global Variables

```yaml
gcp_project_id          # GCP project ID
gcp_region              # GCP region (us-central1)
environment             # dev, staging, prod
python_version          # Python version (3.11)
docker_compose_version  # Docker Compose version
```

### GCP Variables

```yaml
gcp_service_account_name         # SA name
gcp_dataset_name                 # BigQuery dataset
gcp_bigquery_table               # Table name
gcp_bucket_input                 # Storage input bucket
gcp_bucket_temp                  # Storage temp bucket
gcp_bucket_dlq                   # Storage DLQ bucket
gcp_bucket_output                # Storage output bucket
```

### Dataflow Variables

```yaml
dataflow_template_path           # Template GCS path
dataflow_job_name                # Default job name
dataflow_workers                 # Min workers (default: 2)
dataflow_max_workers             # Max workers (default: 20)
dataflow_machine_type            # VM type (n1-standard-4)
```

### Customization

Override variables at runtime:

```bash
ansible-playbook ... \
  -e "dataflow_workers=5" \
  -e "dataflow_max_workers=50" \
  -e "environment=prod"
```

Or in inventory file:

```yaml
all:
  vars:
    dataflow_workers: 5
    dataflow_max_workers: 50
```

---

## Common Tasks

### Task 1: Deploy to New GCP Project

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "gcp_project_id=new-project-id" \
  -e "environment=dev"
```

### Task 2: Update Dataflow Template

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/roles/dataflow-deploy/tasks/main.yml \
  -e "environment=prod"
```

### Task 3: Run Pipeline with Custom Workers

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DataflowRunner" \
  -e "dataflow_workers=10" \
  -e "dataflow_max_workers=100"
```

### Task 4: Verify All Components

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml \
  -e "environment=prod"
```

### Task 5: View Logs

```bash
# Check last deployment
tail -f ansible/logs/ansible.log

# View specific task
grep "gcp-setup" ansible/logs/ansible.log
```

---

## Troubleshooting

### Issue: "Permission denied" for GCP

**Solution**:
```bash
# Re-authenticate
gcloud auth application-default login

# Or use service account key
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/ansible-gcp-key.json"
```

### Issue: "Docker daemon not responding"

**Solution**:
```bash
# Start Docker
sudo systemctl start docker

# Check status
sudo systemctl status docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: "No Python interpreter found"

**Solution**:
```bash
# Update ansible.cfg
ansible_python_interpreter: /usr/bin/python3

# Or set in inventory
localhost:
  ansible_python_interpreter: /usr/bin/python3
```

### Issue: "Timeout waiting for job completion"

**Solution**:
```bash
# Increase timeout
ansible-playbook ... -e "job_timeout=3600"

# Monitor manually
gcloud dataflow jobs list --region=us-central1
gcloud dataflow jobs describe JOB_ID --region=us-central1
```

---

## Advanced Usage

### Dry Run (Check Mode)

```bash
# Preview changes without applying
ansible-playbook ansible/playbooks/deploy.yml --check
```

### Specific Tags

```bash
# Deploy only GCP
ansible-playbook ansible/playbooks/deploy.yml --tags "gcp"

# Deploy only BigQuery
ansible-playbook ansible/playbooks/deploy.yml --tags "bigquery"

# Skip Docker setup
ansible-playbook ansible/playbooks/deploy.yml --skip-tags "docker"
```

### Async Execution

```bash
# Run async (don't wait for completion)
ansible-playbook ansible/playbooks/deploy.yml \
  -e "async_mode=true"

# Check job status
ansible localhost -m async_status -a "jid=12345"
```

### Multi-Environment

```bash
# Deploy to dev and staging
for env in dev staging; do
  ansible-playbook ansible/playbooks/deploy.yml \
    -e "environment=$env"
done
```

---

## Best Practices

1. **Always use `--check` first**:
   ```bash
   ansible-playbook ... --check
   ```

2. **Store sensitive data in vault**:
   ```bash
   ansible-vault encrypt ansible/inventory/secrets.yml
   ```

3. **Use tags for selective deployment**:
   ```bash
   ansible-playbook ... --tags "bigquery"
   ```

4. **Review logs for debugging**:
   ```bash
   tail -f ansible/logs/ansible.log
   ```

5. **Test in dev before prod**:
   ```bash
   # Test in dev first
   ansible-playbook ... -e "environment=dev"
   
   # Then prod
   ansible-playbook ... -e "environment=prod"
   ```

6. **Keep inventory organized**:
   - `inventory/dev.yml` for development
   - `inventory/staging.yml` for staging
   - `inventory/prod.yml` for production

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run Ansible Deploy
  uses: dawidd6/action-ansible-playbook@v2
  with:
    playbook: ansible/playbooks/deploy.yml
    inventory: ansible/inventory/hosts.yml
    options: |
      -e "environment=prod"
      -e "gcp_project_id=${{ secrets.GCP_PROJECT_ID }}"
```

### GitLab CI

```yaml
deploy:
  stage: deploy
  script:
    - ansible-playbook ansible/playbooks/deploy.yml -e "environment=prod"
  only:
    - main
```

---

## Support

- **Documentation**: See `docs/ARCHITECTURE.md`
- **Questions**: GitHub Issues
- **Logs**: Check `ansible/logs/ansible.log`

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0  
**Maintained By**: Data Engineering Team

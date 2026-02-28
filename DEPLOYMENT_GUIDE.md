# Complete Ansible Deployment Guide - Step by Step

This guide walks through the complete deployment process using Ansible.

---

## Prerequisites

### System Requirements
- Python 3.8+
- Ansible 2.14+
- Google Cloud SDK installed and configured
- Docker (for DataflowRunner)
- 2GB free disk space

### GCP Requirements
- Active GCP project
- Billing enabled
- Editor role permissions
- Service account creation permissions

### Network Requirements
- Internet access for API calls
- GCP APIs accessible
- Docker registry access (if using DataflowRunner)

---

## Step 1: Install Ansible

### Option A: Automated Setup (Recommended)

**For Linux/macOS**:
```bash
cd ~/Desktop/olympic-data-etl
bash scripts/setup_ansible.sh
```

**For Windows (PowerShell)**:
```powershell
cd ~/Desktop/olympic-data-etl
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1
```

### Option B: Manual Installation

```bash
# Install Ansible
pip install 'ansible>=2.14.0' 'ansible[google,azure]'

# Install collections
ansible-galaxy collection install google.cloud
ansible-galaxy collection install azure.azcollection
ansible-galaxy collection install community.general
ansible-galaxy collection install community.docker
```

**Verify installation**:
```bash
ansible --version
ansible-galaxy collection list
```

---

## Step 2: Configure GCP Credentials

### Method 1: Application Default Credentials (Recommended)

```bash
# Login to Google Cloud
gcloud auth login

# Set default project
gcloud config set project YOUR_PROJECT_ID

# Create application default credentials
gcloud auth application-default login

# Verify
gcloud config list
gcloud auth list
```

### Method 2: Service Account Key

```bash
# Create service account
gcloud iam service-accounts create ansible-deploy \
  --display-name="Ansible Deployment Account"

# Create and download key
gcloud iam service-accounts keys create ~/ansible-key.json \
  --iam-account=ansible-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member=serviceAccount:ansible-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/editor

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/ansible-key.json"
```

### Method 3: Cloud Shell (GCP Native)

```bash
# Use GCP Cloud Shell (already authenticated)
# No additional setup needed!
git clone https://github.com/your-org/olympic-data-etl
cd olympic-data-etl
bash scripts/setup_ansible.sh
```

---

## Step 3: Configure Ansible Inventory

### Create Inventory File

```bash
# Copy template
cp ansible/inventory/hosts.example.yml ansible/inventory/hosts.yml

# Edit with your values
nano ansible/inventory/hosts.yml
```

### Essential Variables to Update

```yaml
all:
  vars:
    gcp_project_id: "your-actual-project-id"   # ← CHANGE THIS
    environment: "dev"                          # dev, staging, or prod
    slack_webhook_url: "https://..."           # (Optional)
```

### Dynamic Environment Setup

For multiple environments, create separate files:

```bash
# Development
cp ansible/inventory/hosts.example.yml ansible/inventory/dev.yml

# Staging
cp ansible/inventory/hosts.example.yml ansible/inventory/staging.yml

# Production
cp ansible/inventory/hosts.example.yml ansible/inventory/prod.yml
```

Then edit each file with environment-specific values.

---

## Step 4: Test Connectivity

### Test Local Connection

```bash
# Test Ansible can reach localhost
ansible localhost -m ping

# Output should show:
# localhost | SUCCESS => {
#     "changed": false,
#     "ping": "pong"
# }
```

### Test GCP Connection

```bash
# Run connectivity check
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml \
  --tags=gcp \
  -e "environment=dev"

# Should show GCP project info
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "localhost: FAILED" | Run `ansible localhost -m setup` to debug |
| "gcloud: command not found" | Install Google Cloud SDK |
| "Permission denied" | Run `gcloud auth login` |

---

## Step 5: Dry Run (Check Mode)

**Important**: Always run in check mode first!

```bash
# Preview all changes without applying
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev" \
  --check -vv

# Output will show:
# TASK [gcp-setup : Enable required APIs]
# changed: [localhost] (item=dataflow.googleapis.com)
# (no changes made, check mode)
```

This shows exactly what will happen without making changes.

---

## Step 6: Deploy to Development

### Full Stack Deployment

```bash
# Deploy everything (GCP, BigQuery, Dataflow, Docker)
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev"
```

**Expected output**:
```
TASK [gcp-setup : Enable required APIs] 
TASK [gcp-setup : Create service account]
TASK [gcp-setup : Grant IAM roles]
TASK [gcp-setup : Create storage buckets]
TASK [bigquery-setup : Create dataset]
TASK [bigquery-setup : Create medals table]
TASK [bigquery-setup : Create materialized views]
TASK [dataflow-deploy : Build Docker image]
TASK [dataflow-deploy : Create Dataflow template]
TASK [docker-setup : Install Docker]
PLAY RECAP
```

### Partial Deployment

```bash
# Deploy only GCP
ansible-playbook ansible/playbooks/deploy.yml \
  --tags=gcp \
  -e "environment=dev"

# Deploy only BigQuery
ansible-playbook ansible/playbooks/deploy.yml \
  --tags=bigquery \
  -e "environment=dev"

# Deploy only Dataflow
ansible-playbook ansible/playbooks/deploy.yml \
  --tags=dataflow \
  -e "environment=dev"

# Skip Docker setup
ansible-playbook ansible/playbooks/deploy.yml \
  --skip-tags=docker \
  -e "environment=dev"
```

### Wait for Completion

The playbook will output progress. Total time: **5-10 minutes**

---

## Step 7: Verify Deployment

### Run Verification

```bash
# Comprehensive verification
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml \
  -e "environment=dev"
```

**Checks performed**:
- ✓ GCP authentication
- ✓ BigQuery dataset exists
- ✓ BigQuery table schema
- ✓ Storage buckets created
- ✓ Dataflow template deployed
- ✓ Cloud Scheduler job configured
- ✓ Docker daemon running

### Manual Verification

```bash
# Check GCP resources
gcloud projects describe YOUR_PROJECT_ID
gcloud compute project-info describe --project=YOUR_PROJECT_ID

# Check BigQuery
bq ls
bq show olympics.medals
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM \`YOUR_PROJECT_ID.olympics.medals\`"

# Check storage
gsutil ls gs://YOUR_PROJECT_ID-input/
gsutil ls gs://YOUR_PROJECT_ID-temp/
gsutil ls gs://YOUR_PROJECT_ID-output/

# Check Dataflow
gcloud dataflow templates describe gs://YOUR_PROJECT_ID-beam-templates/olympic-etl-dev

# Check Docker (if installed)
docker ps
docker images
```

---

## Step 8: Run the Pipeline

### Local Execution (DirectRunner)

Good for testing the pipeline logic locally without cloud costs.

```bash
# Run with DirectRunner
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "environment=dev" \
  -e "runner_type=DirectRunner"

# Expected output:
# Task [Run pipeline locally]
# Pipeline finished successfully
# Execution time: X seconds
```

**Monitoring**:
```bash
# Watch logs
tail -f ~/.local/share/apache_beam/logs/latest.log

# Check BigQuery for results
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as records, MAX(processed_at) as latest FROM \`YOUR_PROJECT_ID.olympics.medals\`"
```

**Time**: 2-5 minutes for sample data

---

### Cloud Execution (DataflowRunner)

For production data processing on Google Cloud Dataflow.

```bash
# Run with DataflowRunner
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "environment=dev" \
  -e "runner_type=DataflowRunner"

# Expected output:
# Task [Submit Dataflow job]
# Job submitted: dataflow-job-xxxxx
# Monitoring job status...
# Job completed successfully
```

**Monitoring**:
```bash
# List jobs
gcloud dataflow jobs list --region=us-central1

# Watch specific job
gcloud dataflow jobs describe JOB_ID --region=us-central1

# View logs
gcloud logging read "resource.type=dataflow_step" --limit=50

# Query results
bq query --use_legacy_sql=false \
  "SELECT country_code, COUNT(*) as medals FROM \`YOUR_PROJECT_ID.olympics.medals\` GROUP BY country_code ORDER BY medals DESC LIMIT 10"
```

**Time**: 5-15 minutes depending on data size

---

### Custom Configuration

```bash
# Increase workers for faster processing
ansible-playbook ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DataflowRunner" \
  -e "dataflow_workers=5" \
  -e "dataflow_max_workers=50"

# Use better machine type
ansible-playbook ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DataflowRunner" \
  -e "dataflow_machine_type=n1-highmem-4"

# Longer timeout
ansible-playbook ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DataflowRunner" \
  -e "job_timeout=3600"
```

---

## Step 9: Deploy to Staging

When you're confident with dev setup:

```bash
# Update staging inventory
nano ansible/inventory/staging.yml

# Dry run
ansible-playbook -i ansible/inventory/staging.yml \
  ansible/playbooks/deploy.yml \
  --check

# Deploy
ansible-playbook -i ansible/inventory/staging.yml \
  ansible/playbooks/deploy.yml

# Verify
ansible-playbook -i ansible/inventory/staging.yml \
  ansible/playbooks/verify.yml
```

---

## Step 10: Deploy to Production

When staging is validated:

```bash
# Update production inventory
nano ansible/inventory/prod.yml

# IMPORTANT: Dry run first!
ansible-playbook -i ansible/inventory/prod.yml \
  ansible/playbooks/deploy.yml \
  --check -vv

# Review output carefully

# Deploy to production
ansible-playbook -i ansible/inventory/prod.yml \
  ansible/playbooks/deploy.yml

# Verify thoroughly
ansible-playbook -i ansible/inventory/prod.yml \
  ansible/playbooks/verify.yml

# Run production pipeline
ansible-playbook -i ansible/inventory/prod.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DataflowRunner"
```

---

## Step 11: Setup Automated Scheduling

Cloud Scheduler is automatically configured during deployment.

### Check Schedule

```bash
# List scheduled jobs
gcloud scheduler jobs list

# View job details
gcloud scheduler jobs describe olympic-etl-dev-daily \
  --location=us-central1

# Run manually if needed
gcloud scheduler jobs run olympic-etl-dev-daily \
  --location=us-central1
```

### Modify Schedule

Edit `ansible/inventory/hosts.yml`:

```yaml
scheduler_schedule: "0 6 * * *"  # Change this (cron format)
```

Then redeploy:
```bash
ansible-playbook ansible/playbooks/deploy.yml \
  --tags=dataflow \
  -e "environment=dev"
```

---

## Step 12: Monitor in Production

### View Dataflow Jobs

```bash
# All jobs
gcloud dataflow jobs list --region=us-central1

# Jobs in specific status
gcloud dataflow jobs list --region=us-central1 --filter="state=RUNNING"

# Monitor a running job
watch gcloud dataflow jobs describe JOB_ID --region=us-central1
```

### Check BigQuery

```bash
# Table size
bq show --schema --format=pretty olympics.medals

# Recent records
bq query --use_legacy_sql=false \
  'SELECT * FROM `YOUR_PROJECT_ID.olympics.medals` ORDER BY processed_at DESC LIMIT 5'

# Data quality checks
bq query --use_legacy_sql=false \
  'SELECT 
     COUNT(*) as total,
     COUNT(DISTINCT record_id) as unique_records,
     COUNT(DISTINCT athlete_id) as unique_athletes
  FROM `YOUR_PROJECT_ID.olympics.medals`'
```

### Setup Alerts

```bash
# View logs for errors
gcloud logging read "severity>=ERROR" --limit=10

# Setup log-based alert
# (via GCP Console -> Logging -> Create Alert)
```

---

## Troubleshooting During Deployment

### Issue: "Permission Denied"

```bash
# Re-authenticate
gcloud auth application-default login

# Or use service account
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/ansible-key.json"

# Then retry
ansible-playbook ansible/playbooks/deploy.yml \
  -e "environment=dev"
```

### Issue: "API Not Enabled"

```bash
# Enable missing API
gcloud services enable dataflow.googleapis.com

# Then retry deployment
```

### Issue: "Service Account Not Found"

```bash
# Create it manually
gcloud iam service-accounts create beam-sa \
  --display-name="Beam Service Account"

# Then retry
```

For more troubleshooting, see [ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md)

---

## Post-Deployment Checks

### Security Validation

```bash
# Check IAM bindings
gcloud projects get-iam-policy YOUR_PROJECT_ID

# Verify service accounts
gcloud iam service-accounts list

# Check bucket permissions
gsutil iam ch serviceAccount:beam-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com:roles/storage.admin gs://YOUR_PROJECT_ID-input
```

### Performance Validation

```bash
# Check Dataflow worker metrics
gcloud dataflow jobs describe JOB_ID \
  --region=us-central1 \
  --view=monitoring

# Check BigQuery slots usage
bq show --format=pretty \
  --project_id=YOUR_PROJECT_ID
```

### Cost Analysis

```bash
# View billing
gcloud billing projects describe YOUR_PROJECT_ID

# Estimate costs via Cloud Pricing Calculator
# https://cloud.google.com/products/calculator
```

---

## Maintenance

### Updating the Pipeline

```bash
# Update code in src/beam/pipelines/
vi src/beam/pipelines/olympic_etl_pipeline.py

# Rebuild Dataflow template
ansible-playbook ansible/playbooks/deploy.yml \
  --tags=dataflow \
  -e "environment=dev"

# Test updated pipeline
ansible-playbook ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DirectRunner"
```

### Backup & Recovery

```bash
# Export BigQuery table
bq extract \
  olympics.medals \
  gs://YOUR_PROJECT_ID-backups/medals_backup_$(date +%Y%m%d).parquet

# Restore if needed
bq load --source_format=PARQUET \
  olympics.medals_restored \
  gs://YOUR_PROJECT_ID-backups/medals_backup_20240228.parquet
```

### Cleanup

```bash
# List all created resources
gcloud compute project-info describe --project=YOUR_PROJECT_ID

# Delete Dataflow job
gcloud dataflow jobs cancel JOB_ID --region=us-central1

# Delete resources (carefully!)
# Delete with: terraform destroy
# Or manually via GCP Console
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [QUICK_START_ANSIBLE.md](QUICK_START_ANSIBLE.md) | 30-minute quick start |
| [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md) | Complete Ansible reference |
| [ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md) | Problem solving guide |
| [BASH_VS_ANSIBLE.md](BASH_VS_ANSIBLE.md) | Migration guide from bash |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design overview |
| [docs/SETUP.md](docs/SETUP.md) | Detailed setup instructions |

---

## Support

- Documentation: See `docs/` folder
- Issues: Check [ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md)
- Questions: Review Ansible documentation at [ansible.com/docs](https://docs.ansible.com/)

---

**Deployment Time Estimate**:
- Setup: 10 minutes
- Dry run: 2 minutes
- Deploy (dev): 5-10 minutes
- Verification: 2 minutes
- First run (local): 5 minutes
- **Total**: ~30 minutes for complete setup

**Total Cost Estimate** (dev/month):
- Dataflow: ~$50 (jobs + compute)
- BigQuery: ~$20 (queries + storage)
- Storage: ~$5 (4 buckets)
- **Total**: ~$75/month

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0

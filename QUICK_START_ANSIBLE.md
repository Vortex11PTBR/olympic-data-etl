# Quick Start - Ansible Deployment

**Time to deploy: 30 minutes**

## 1. Prerequisites Check

```bash
# Verify all requirements
ansible --version          # Should be 2.14+
python --version           # Should be 3.8+
gcloud --version           # Google Cloud SDK
docker --version           # Docker CLI
```

## 2. Clone & Setup

```bash
# Navigate to project
cd ~/Desktop/olympic-data-etl

# Install Python dependencies
pip install -r requirements.txt

# Install Ansible collections
ansible-galaxy install -r ansible/requirements.yml
```

## 3. Configure GCP

```bash
# Login to Google Cloud
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID

# Export credentials
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"

# Verify
gcloud config list
```

## 4. Update Inventory

Edit `ansible/inventory/hosts.yml`:

```yaml
all:
  vars:
    gcp_project_id: "YOUR_PROJECT_ID"      # ← Change this
    environment: "dev"                      # ← Change this
    slack_webhook_url: "YOUR_WEBHOOK_URL"  # (Optional)
```

## 5. Deploy

### Option A: Development (Recommended First)

```bash
# Deploy all components
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev"
```

**Output**:
- GCP service account created
- BigQuery dataset & tables ready
- Dataflow template deployed
- Docker configured

### Option B: Production

```bash
# Deploy with confirmation
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=prod" \
  --ask-become-pass
```

## 6. Verify Deployment

```bash
# Run verification
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml \
  -e "environment=dev"
```

**Expected output**:
```
✓ GCP authentication successful
✓ BigQuery dataset ready
✓ Storage buckets created
✓ Dataflow template deployed
✓ Docker daemon running
```

## 7. Run Pipeline

### Local Test (DirectRunner)

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "environment=dev" \
  -e "runner_type=DirectRunner"
```

**Monitor locally** (takes 5-10 minutes):
```bash
# Watch logs
tail -f ~/.local/share/apache_beam/logs/latest.log
```

### Cloud Execution (DataflowRunner)

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "environment=dev" \
  -e "runner_type=DataflowRunner"
```

**Monitor in GCP**:
```bash
# List jobs
gcloud dataflow jobs list --region=us-central1

# Watch job
gcloud dataflow jobs describe JOB_ID --region=us-central1
```

## 8. Check Results

### BigQuery

```bash
# Query results
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as total_records FROM `project.dataset.medals`'

# View schema
bq show project:dataset.medals
```

### Cloud Storage

```bash
# List processed files
gsutil ls gs://YOUR_PROJECT-output/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `gcloud: command not found` | Install Google Cloud SDK |
| `Permission denied` | Run `gcloud auth login` |
| `Docker daemon not responding` | Run `sudo systemctl start docker` |
| `Ansible not found` | Run `pip install ansible` |

---

## Next Steps

- ✅ **Deployment complete!**
- View [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md) for detailed documentation
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system overview
- Check [docs/SETUP.md](docs/SETUP.md) for advanced configuration

---

## Common Commands Reference

```bash
# Deploy to dev
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -e "environment=dev"

# Verify deployment
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/verify.yml -e "environment=dev"

# Run pipeline locally
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/run-pipeline.yml -e "runner_type=DirectRunner"

# Run pipeline on cloud
ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/run-pipeline.yml -e "runner_type=DataflowRunner"

# Check logs
tail -f ansible/logs/ansible.log

# Dry run (preview)
ansible-playbook ansible/playbooks/deploy.yml --check
```

---

**Need help?** See [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md)

**Last updated**: February 28, 2026

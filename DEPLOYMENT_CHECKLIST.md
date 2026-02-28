# ✅ Ansible Deployment - Verification Checklist

Use this checklist to verify complete setup before deployment.

---

## Pre-Deployment Checklist

### System Requirements
- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip installed (`pip --version`)
- [ ] Git installed (`git --version`)
- [ ] 2GB+ free disk space
- [ ] Internet connection available

### GCP Preparation
- [ ] GCP Account active with billing enabled
- [ ] Project ID ready (write it down: `_________________`)
- [ ] gcloud CLI installed (`gcloud --version`)
- [ ] Logged into gcloud (`gcloud auth list`)
- [ ] Project set as default (`gcloud config get-value project`)
- [ ] Editor role permissions verified

### Download & Access
- [ ] Project cloned/downloaded
- [ ] Located at: `~/Desktop/olympic-data-etl`
- [ ] All files readable (`ls -la`)

---

## Installation Verification

### Ansible Installation
- [ ] Ansible installed (`ansible --version`)
  - Expected version: 2.14.0 or higher
  - Command output shows version number
  
- [ ] Collections installed
  ```bash
  ansible-galaxy collection list
  ```
  Should show:
  - [ ] `google.cloud`
  - [ ] `azure.azcollection`
  - [ ] `community.general`
  - [ ] `community.docker`

### Connectivity Test
- [ ] Localhost ping successful
  ```bash
  ansible localhost -m ping
  # Expected: SUCCESS with "pong"
  ```

---

## Configuration Verification

### Ansible Configuration File
- [ ] `ansible.cfg` exists in project root
  ```bash
  ls -la ansible.cfg
  ```
- [ ] Contains valid settings:
  - [ ] `inventory` points to inventory file
  - [ ] `host_key_checking = False`
  - [ ] `roles_path` configured

### Inventory Configuration
- [ ] `ansible/inventory/hosts.yml` exists
  ```bash
  ls -la ansible/inventory/hosts.yml
  ```
- [ ] Contains required variables:
  - [ ] `gcp_project_id` - Set to your project
  - [ ] `gcp_region` - Default: `us-central1`
  - [ ] `environment` - Set to `dev` for testing
  - [ ] `ansible_python_interpreter` - Default: `/usr/bin/python3`

### Inventory Content Check
```bash
# Verify inventory is valid YAML
ansible-inventory -i ansible/inventory/hosts.yml --list | head -20

# Should show JSON output with your variables
```

### GCP Credentials
- [ ] Google Cloud credentials configured
  ```bash
  echo $GOOGLE_APPLICATION_CREDENTIALS
  # Should show path to credentials file
  ```
- [ ] Credentials file exists and readable
  ```bash
  ls -l $GOOGLE_APPLICATION_CREDENTIALS
  ```
- [ ] GCP authentication successful
  ```bash
  gcloud auth application-default print-access-token
  # Should return a token without errors
  ```

---

## Project Structure Verification

### Ansible Directory Structure
- [ ] `ansible/` directory exists
- [ ] `ansible/ansible.cfg` exists
- [ ] `ansible/requirements.yml` exists
- [ ] `ansible/inventory/` directory exists with `hosts.yml`
- [ ] `ansible/playbooks/` directory exists with:
  - [ ] `deploy.yml`
  - [ ] `run-pipeline.yml`
  - [ ] `verify.yml`
- [ ] `ansible/roles/` directory exists with:
  - [ ] `gcp-setup/tasks/main.yml`
  - [ ] `bigquery-setup/tasks/main.yml`
  - [ ] `dataflow-deploy/tasks/main.yml`
  - [ ] `docker-setup/tasks/main.yml`

### Playbook Syntax Validation
```bash
# Check all playbooks are valid YAML
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml --syntax-check

# Expected: "playbook: ansible/playbooks/deploy.yml"
```

- [ ] `deploy.yml` syntax valid
- [ ] `run-pipeline.yml` syntax valid
- [ ] `verify.yml` syntax valid

### Scripts Directory
- [ ] `scripts/` directory exists
- [ ] `scripts/setup_ansible.sh` exists (Linux/macOS)
- [ ] `scripts/setup_ansible.ps1` exists (Windows)
- [ ] `scripts/deploy.sh` exists (original bash)

---

## Documentation Verification

### All Documentation Files Present
- [ ] `QUICK_START_ANSIBLE.md` exists
- [ ] `DEPLOYMENT_GUIDE.md` exists
- [ ] `ANSIBLE_DEPLOY.md` exists
- [ ] `ANSIBLE_TROUBLESHOOTING.md` exists
- [ ] `BASH_VS_ANSIBLE.md` exists
- [ ] `ANSIBLE_INDEX.md` exists
- [ ] `ANSIBLE_SETUP_COMPLETE.md` exists (this file)
- [ ] `scripts/README.md` exists

### Documentation Read Check
- [ ] Skimmed `QUICK_START_ANSIBLE.md`
- [ ] Reviewed `DEPLOYMENT_GUIDE.md` overview
- [ ] Noted key commands from `ANSIBLE_DEPLOY.md`
- [ ] Bookmarked `ANSIBLE_TROUBLESHOOTING.md` for reference

---

## Pre-Deployment Test

### Connectivity Tests
- [ ] GCP API connectivity
  ```bash
  gcloud compute project-info describe --project=$(gcloud config get-value project)
  # Should show project information
  ```
  
- [ ] BigQuery connectivity
  ```bash
  bq ls
  # Should list existing datasets or show empty list
  ```

- [ ] Storage connectivity
  ```bash
  gsutil ls
  # Should list existing buckets or show empty list
  ```

### Ansible Playbook Dry-Run
- [ ] Deploy playbook check mode successful
  ```bash
  ansible-playbook -i ansible/inventory/hosts.yml \
    ansible/playbooks/deploy.yml -e "environment=dev" --check
  
  # Should show what "would" change without making changes
  ```

- [ ] Verify playbook check mode successful
  ```bash
  ansible-playbook -i ansible/inventory/hosts.yml \
    ansible/playbooks/verify.yml --check
  
  # Should show what "would" be checked without errors
  ```

---

## Ready for Deployment Decisions

### Deployment Scope
- [ ] Confirm you want to deploy to: `dev` / `staging` / `prod` (circle one)
- [ ] Understand this will create:
  - [ ] GCP service account
  - [ ] BigQuery dataset with tables
  - [ ] Cloud Storage buckets
  - [ ] Dataflow template
  - [ ] Cloud Scheduler job
  - [ ] Docker images and containers
- [ ] Budget impact understood (~$75-100/month for dev)

### Environment Settings Verified
- [ ] `gcp_project_id`: `_______________________`
- [ ] `environment`: `dev` / `staging` / `prod`
- [ ] `gcp_region`: `us-central1` (or your choice)
- [ ] `dataflow_workers`: `2` (or your desired number)
- [ ] `dataflow_max_workers`: `20` (or your desired max)

---

## First Run Verification

### After First Deployment
- [ ] Deployment completed without errors
- [ ] All tasks show "changed" or "ok" status
- [ ] No tasks marked as "failed"
- [ ] Service account created in GCP
  ```bash
  gcloud iam service-accounts list
  # Should see 'beam-sa' or similar
  ```

### BigQuery Verification
- [ ] Dataset created
  ```bash
  bq ls
  # Should see 'olympics' dataset
  ```

- [ ] Table created with correct schema
  ```bash
  bq show olympics.medals
  # Should show 15 fields (athlete_id, event_id, etc.)
  ```

- [ ] Materialized views created
  ```bash
  bq ls olympics
  # Should see 'daily_medal_counts', 'athlete_totals' views
  ```

### GCP Resource Verification
- [ ] Cloud Storage buckets created
  ```bash
  gsutil ls
  # Should see 4 buckets: input, temp, dlq, output
  ```

- [ ] Dataflow template created
  ```bash
  gcloud dataflow templates describe \
    gs://PROJECT-beam-templates/olympic-etl-dev \
    --region=us-central1
  # Should show template details
  ```

- [ ] Cloud Scheduler job created
  ```bash
  gcloud scheduler jobs list --location=us-central1
  # Should see 'olympic-etl-dev-daily' or similar
  ```

### Pipeline Execution Verification
- [ ] Pipeline ran successfully with DirectRunner
  - [ ] No errors in logs
  - [ ] Records processed
  - [ ] Data in BigQuery

- [ ] Or pipeline ran successfully with DataflowRunner
  - [ ] Job submitted successfully
  - [ ] Job completed (not failed)
  - [ ] Data in BigQuery

### Data Verification
- [ ] Records in BigQuery table
  ```bash
  bq query --use_legacy_sql=false \
    "SELECT COUNT(*) as count FROM \`PROJECT.olympics.medals\`"
  # Should return > 0
  ```

- [ ] No data quality issues
  ```bash
  bq query --use_legacy_sql=false \
    "SELECT * FROM \`PROJECT.olympics.medals\` LIMIT 5"
  # Should show valid records
  ```

---

## Post-Deployment Checklist

### Monitoring Setup
- [ ] Cloud Logging configured
- [ ] Cloud Monitoring alerts considered
- [ ] Slack notifications tested (if configured)

### Backup & Recovery
- [ ] Backup strategy planned
- [ ] Disaster recovery procedure documented
- [ ] Data export process tested

### Documentation Updates
- [ ] Team notified of new Ansible deployment system
- [ ] Deployment procedures documented
- [ ] Customizations documented
- [ ] Environment variables documented

### Security Review
- [ ] Service account permissions are minimal
- [ ] No hardcoded credentials in files
- [ ] Firewall rules reviewed
- [ ] IAM bindings checked

### Cost Monitoring
- [ ] GCP billing dashboard checked
- [ ] Cost estimates reviewed
- [ ] Budget alerts set up (optional)

---

## Troubleshooting Verification

### If Something Failed
- [ ] Checked [ANSIBLE_TROUBLESHOOTING.md](../ANSIBLE_TROUBLESHOOTING.md)
- [ ] Ran deployment with verbose output (`-vvv`)
- [ ] Reviewed `ansible/logs/ansible.log`
- [ ] Checked GCP error messages and logs
- [ ] Verified prerequisites are installed

### If Still Stuck
- [ ] All prerequisites double-checked
- [ ] Credentials refreshed
- [ ] GCP project permissions verified
- [ ] Ansible syntax validated
- [ ] Network connectivity confirmed

---

## Sign-Off Checklist

### Pre-Production Verification
- [ ] Development deployment successful ✅
- [ ] Staging deployment successful (if applicable) ✅
- [ ] Production deployment preparation complete ✅
- [ ] All documentation reviewed ✅
- [ ] Team trained (if applicable) ✅

### Deployment Authority
- [ ] Manager/Lead approval obtained
- [ ] Change notification sent
- [ ] Maintenance window scheduled (if needed)
- [ ] Rollback procedure documented

### Final Sign-Off
- [ ] I have verified all items in this checklist
- [ ] I understand the deployment implications
- [ ] I have backup procedures in place
- [ ] I am ready to deploy to production

**Date**: _______________
**Name**: _______________
**Signature**: _______________

---

## Common Verification Commands

```bash
# System check
python --version && pip --version && ansible --version

# GCP check
gcloud config list && gcloud auth list

# Ansieble check
ansible localhost -m ping
ansible-inventory -i ansible/inventory/hosts.yml --list

# Playbook validation
ansible-playbook ansible/playbooks/deploy.yml --syntax-check
ansible-playbook ansible/playbooks/verify.yml --syntax-check

# Dry-run
ansible-playbook ansible/playbooks/deploy.yml \
  -e "environment=dev" --check

# Deployment
ansible-playbook ansible/playbooks/deploy.yml \
  -e "environment=dev"

# Verification
ansible-playbook ansible/playbooks/verify.yml \
  -e "environment=dev"

# Pipeline execution
ansible-playbook ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DirectRunner"
```

---

## Next Steps After Verification

1. ✅ **All checks passed?** → You're ready to deploy!
2. ❓ **Found an issue?** → See [ANSIBLE_TROUBLESHOOTING.md](../ANSIBLE_TROUBLESHOOTING.md)
3. 📖 **Need more info?** → See [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
4. 🚀 **Ready to deploy?** → Follow [QUICK_START_ANSIBLE.md](../QUICK_START_ANSIBLE.md)

---

## Keep This Checklist

- Print this checklist for future deployments
- Update dates and sign-off information
- Keep in project documentation
- Reference for troubleshooting

---

**Deployment Status**: 
- [ ] ❌ Not Ready - Issues Found
- [ ] ⚠️ Partial - Some Issues Remain
- [ ] ⏳ Pending - Awaiting Approval
- [ ] ✅ Ready - All Checks Passed

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0  
**Next Review**: Before each production deployment

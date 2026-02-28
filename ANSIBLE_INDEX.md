# Ansible Documentation Index

Central hub for all Ansible-related documentation for the Olympic Data ETL project.

---

## Quick Navigation

### 🚀 Getting Started (NEW USERS)

Start here if you're new to Ansible deployment:

1. **[QUICK_START_ANSIBLE.md](QUICK_START_ANSIBLE.md)** (⏱️ 30 minutes)
   - Prerequisites check
   - Basic setup steps
   - First deployment
   - Verification

2. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** (⏱️ Complete reference)
   - Step-by-step walkthrough
   - All deployment scenarios
   - Environment setup
   - Post-deployment validation

### 📚 Complete Reference

Detailed documentation for experienced users:

3. **[ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md)** (📖 Full documentation)
   - Installation procedures
   - Ansible playbooks reference
   - Ansible roles documentation
   - Variables configuration
   - Advanced usage patterns
   - CI/CD integration

4. **[ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md)** (🔧 Problem solving)
   - Common issues & solutions
   - Installation troubleshooting
   - Authentication problems
   - GCP-specific issues
   - BigQuery issues
   - Dataflow issues
   - Performance tuning
   - Debug commands

### 🔄 Migration & Comparison

For users migrating from bash scripts:

5. **[BASH_VS_ANSIBLE.md](BASH_VS_ANSIBLE.md)** (📊 Comparison)
   - Side-by-side feature comparison
   - Command migration guide
   - Environment configuration
   - Error handling improvements
   - Testing & validation
   - Migration checklist

---

## Documentation By Use Case

### Use Case: "I want to deploy Olympic ETL today"

1. Read: [QUICK_START_ANSIBLE.md](QUICK_START_ANSIBLE.md)
2. Follow: Step 1-8 in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
3. If issues: Check [ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md)

**Time**: ~30 minutes

---

### Use Case: "I need to deploy to production with confidence"

1. Read: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - All steps
2. Review: [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md) - Playbooks section
3. Understand: Each role in [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md)
4. Execute: Step 9-10 in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
5. Monitor: Step 12 in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Time**: ~1-2 hours for first deployment

---

### Use Case: "I'm migrating from bash scripts"

1. Overview: [BASH_VS_ANSIBLE.md](BASH_VS_ANSIBLE.md)
2. Learn: [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md)
3. Execute: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Time**: ~1 hour

---

### Use Case: "Something is broken/not working"

1. Check: [ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md)
2. Find your issue type:
   - Installation Issues
   - Authentication Issues
   - Playbook Execution Issues
   - GCP-Specific Issues
   - BigQuery Issues
   - Docker Issues
   - Dataflow Issues
   - Performance Issues
3. Follow solution
4. If still stuck: Enable debug logging and check logs

---

### Use Case: "I need to customize the deployment"

1. Variables: [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md) - Variables Reference
2. Inventory: Review `ansible/inventory/hosts.yml`
3. Roles: Review appropriate role tasks
4. Playbooks: Review `ansible/playbooks/*.yml`
5. Modify as needed
6. Test: `ansible-playbook ... --check`

---

### Use Case: "I want to understand the full deployment"

1. Overview: [BASH_VS_ANSIBLE.md](BASH_VS_ANSIBLE.md) - Features Comparison
2. Architecture: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
3. Detailed walk-through: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
4. Reference: [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md)
5. Implementation: Review source files in `ansible/`

---

## File Structure

### Documentation Files

```
project-root/
├── QUICK_START_ANSIBLE.md          # 30-minute quick start
├── DEPLOYMENT_GUIDE.md              # Complete step-by-step guide
├── ANSIBLE_DEPLOY.md                # Full Ansible reference
├── ANSIBLE_TROUBLESHOOTING.md       # Problem solving
├── BASH_VS_ANSIBLE.md               # Migration guide
└── ANSIBLE_INDEX.md                 # This file
```

### Ansible Configuration Files

```
ansible/
├── ansible.cfg                      # Global configuration
├── requirements.yml                 # Collection dependencies
├── inventory/
│   ├── hosts.yml                   # Main inventory (EDIT THIS)
│   ├── hosts.example.yml           # Template
│   ├── dev.yml                     # Optional: Dev environment
│   ├── staging.yml                 # Optional: Staging environment
│   └── prod.yml                    # Optional: Prod environment
├── playbooks/
│   ├── deploy.yml                  # Main deployment playbook
│   ├── run-pipeline.yml            # Pipeline execution
│   └── verify.yml                  # Verification playbook
└── roles/
    ├── gcp-setup/
    │   └── tasks/main.yml
    ├── bigquery-setup/
    │   └── tasks/main.yml
    ├── dataflow-deploy/
    │   └── tasks/main.yml
    └── docker-setup/
        └── tasks/main.yml
```

### Setup Scripts

```
scripts/
├── setup_ansible.sh                # Linux/macOS setup (bash)
└── setup_ansible.ps1               # Windows setup (PowerShell)
```

---

## Quick Reference

### Installation

```bash
# Automated setup
bash scripts/setup_ansible.sh          # Linux/macOS
powershell -ExecutionPolicy Bypass \
  -File scripts/setup_ansible.ps1      # Windows

# Manual installation
pip install 'ansible>=2.14.0'
ansible-galaxy install -r ansible/requirements.yml
```

### Configuration

```bash
# Setup inventory from template
cp ansible/inventory/hosts.example.yml ansible/inventory/hosts.yml

# Edit with your GCP project
nano ansible/inventory/hosts.yml
```

### Deployment Commands

```bash
# Development deployment
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml -e "environment=dev"

# Staging deployment
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml -e "environment=staging"

# Production deployment
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml -e "environment=prod"

# Dry run (preview)
ansible-playbook ansible/playbooks/deploy.yml --check

# Verify deployment
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml

# Run pipeline (local)
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml -e "runner_type=DirectRunner"

# Run pipeline (cloud)
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml -e "runner_type=DataflowRunner"
```

### Debugging

```bash
# Verbose output (more details)
ansible-playbook ansible/playbooks/deploy.yml -vv

# Very verbose output (detailed)
ansible-playbook ansible/playbooks/deploy.yml -vvv

# Check mode (preview without changes)
ansible-playbook ansible/playbooks/deploy.yml --check

# Test connectivity
ansible localhost -m ping

# View Ansible logs
tail -f ansible/logs/ansible.log
```

---

## Documentation Matrix

| Document | Purpose | Audience | Time | Level |
|----------|---------|----------|------|-------|
| QUICK_START_ANSIBLE | Get started fast | New users | 30 min | Beginner |
| DEPLOYMENT_GUIDE | Complete walkthrough | All users | 2 hours | Beginner |
| ANSIBLE_DEPLOY | Full reference | Experienced users | Reference | Intermediate |
| ANSIBLE_TROUBLESHOOTING | Problem solving | All users | Reference | Intermediate |
| BASH_VS_ANSIBLE | Migration guide | Users familiar with bash | 30 min | Intermediate |

---

## Feature Overview

### Ansible Deployment Features

| Feature | Document | Status |
|---------|----------|--------|
| GCP Setup (APIs, IAM, Service Accounts) | ANSIBLE_DEPLOY | ✅ Complete |
| BigQuery Setup (Dataset, Tables, Views) | ANSIBLE_DEPLOY | ✅ Complete |
| Dataflow Deployment (Docker, Template, Scheduler) | ANSIBLE_DEPLOY | ✅ Complete |
| Docker Setup (Installation, Services) | ANSIBLE_DEPLOY | ✅ Complete |
| Pipeline Execution (DirectRunner, DataflowRunner) | ANSIBLE_DEPLOY | ✅ Complete |
| Deployment Verification | ANSIBLE_DEPLOY | ✅ Complete |
| Multi-Environment Support | DEPLOYMENT_GUIDE | ✅ Complete |
| Dry-Run/Check Mode | ANSIBLE_DEPLOY | ✅ Complete |
| Slack Notifications | ANSIBLE_DEPLOY | ✅ Complete |
| Cloud Logging Integration | ANSIBLE_DEPLOY | ✅ Complete |
| Automated Scheduling (Cloud Scheduler) | ANSIBLE_DEPLOY | ✅ Complete |

---

## Common Tasks

### Deploy Everything to Dev

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml -e "environment=dev"
```
**See**: DEPLOYMENT_GUIDE.md - Step 6

### Update GCP Setup Only

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml --tags=gcp -e "environment=dev"
```
**See**: ANSIBLE_DEPLOY.md - Playbooks

### Run Pipeline Locally

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/run-pipeline.yml \
  -e "runner_type=DirectRunner"
```
**See**: DEPLOYMENT_GUIDE.md - Step 8

### Verify All Components

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml -e "environment=dev"
```
**See**: DEPLOYMENT_GUIDE.md - Step 7

### Preview Changes (Don't Apply)

```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev" --check -vv
```
**See**: DEPLOYMENT_GUIDE.md - Step 5

---

## Related Documentation

### Core Project Documentation

- **[README.md](../README.md)** - Project overview
- **[docs/SETUP.md](../docs/SETUP.md)** - Manual setup guide
- **[docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)** - System architecture
- **[docs/API_INTEGRATION.md](../docs/API_INTEGRATION.md)** - API integration guide

### Infrastructure Files

- **[ansible.cfg](../ansible.cfg)** - Ansible configuration
- **[ansible/requirements.yml](../ansible/requirements.yml)** - Dependencies
- **[ansible/inventory/hosts.yml](../ansible/inventory/hosts.yml)** - Inventory (main)

### Ansible Playbooks

- **[ansible/playbooks/deploy.yml](../ansible/playbooks/deploy.yml)** - Main deployment
- **[ansible/playbooks/run-pipeline.yml](../ansible/playbooks/run-pipeline.yml)** - Pipeline execution
- **[ansible/playbooks/verify.yml](../ansible/playbooks/verify.yml)** - Verification

### Ansible Roles

- **[ansible/roles/gcp-setup/](../ansible/roles/gcp-setup/)** - GCP infrastructure
- **[ansible/roles/bigquery-setup/](../ansible/roles/bigquery-setup/)** - BigQuery setup
- **[ansible/roles/dataflow-deploy/](../ansible/roles/dataflow-deploy/)** - Dataflow deployment
- **[ansible/roles/docker-setup/](../ansible/roles/docker-setup/)** - Docker installation

---

## Support Resources

### Official Documentation

- [Ansible Documentation](https://docs.ansible.com/)
- [Google Cloud Ansible Collection](https://cloud.google.com/python/docs/reference/google-cloud-ansible-collection)
- [Azure Ansible Collection](https://docs.microsoft.com/en-us/ansible/ansible-collections/)

### Learning Resources

- [Ansible for Beginners](https://www.youtube.com/watch?v=e3yS0PDLC_M)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Dataflow Documentation](https://cloud.google.com/dataflow/docs)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

### Getting Help

1. **Check documentation**: Search in relevant `.md` files
2. **Check troubleshooting**: See [ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md)
3. **Review logs**: Check `ansible/logs/ansible.log`
4. **Debug**: Run with `-vvv` flag for detailed output
5. **Search online**: Google Cloud & Ansible communities

---

## Document Updates

| Document | Last Updated | Version | Status |
|----------|-------------|---------|--------|
| QUICK_START_ANSIBLE.md | Feb 28, 2026 | 1.0.0 | ✅ Complete |
| DEPLOYMENT_GUIDE.md | Feb 28, 2026 | 1.0.0 | ✅ Complete |
| ANSIBLE_DEPLOY.md | Feb 28, 2026 | 1.0.0 | ✅ Complete |
| ANSIBLE_TROUBLESHOOTING.md | Feb 28, 2026 | 1.0.0 | ✅ Complete |
| BASH_VS_ANSIBLE.md | Feb 28, 2026 | 1.0.0 | ✅ Complete |
| ANSIBLE_INDEX.md | Feb 28, 2026 | 1.0.0 | ✅ Complete |

---

## Feedback & Contributions

To improve this documentation:

1. Found an error? → Submit issue
2. Have a suggestion? → Create PR
3. Need clarification? → Open GitHub issue
4. Want to contribute? → Follow CONTRIBUTING.md

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0  
**Maintainer**: Data Engineering Team  
**License**: Same as project

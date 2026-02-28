# Bash vs Ansible: Comparison & Migration Guide

## Overview

The Olympic Data ETL project has evolved from bash scripts to Ansible infrastructure-as-code. This document highlights differences and migration path.

---

## Side-by-Side Comparison

### Deployment Approach

| Aspect | Bash Script | Ansible |
|--------|------------|---------|
| **Idempotency** | Manual verification needed | Built-in, safe to re-run |
| **Error Handling** | Custom error checking | Native handlers & blocks |
| **Multi-environment** | Environment-specific scripts | Single playbook with variables |
| **Modularity** | Monolithic script | Modular roles |
| **Testing** | Manual testing required | Dry-run with `--check` |
| **Rollback** | Manual undo steps | Built-in rollback tasks |
| **Learning Curve** | Low (shell syntax) | Medium (YAML/Ansible concepts) |
| **Dependencies** | bash, gcloud CLI, bq, gsutil | Ansible 2.14+, Collections |

---

## Feature Comparison

### GCP Setup

| Feature | Bash Script | Ansible |
|---------|------------|---------|
| Enable APIs | Manual `gcloud services enable` | Automated in gcp-setup role |
| Service Account | Manual creation | Automated with Ansible |
| IAM Roles | Manual `add-iam-policy-binding` | Loop over role list |
| Storage Buckets | Individual `gsutil` commands | gcp-storage module + lifecycle policies |
| Verification | Manual checks | verify.yml playbook |

### BigQuery Setup

| Feature | Bash Script | Ansible |
|---------|------------|---------|
| Dataset Creation | Manual BQ CLI | google.cloud.gcp_bigquery_dataset |
| Table Schema | JSON file + BQ load | YAML schema in task |
| Partitioning | Manual configuration | google.cloud.gcp_bigquery_table |
| Materialized Views | Manual SQL | google.cloud.gcp_bigquery_table_schema |
| Verification | Manual queries | verify.yml playbook |

### Dataflow Deployment

| Feature | Bash Script | Ansible |
|---------|------------|---------|
| Docker Build | Manual `docker build` | container.image module |
| Image Push | Manual `docker push` | container.image module |
| Template Creation | Manual `gcloud dataflow build-pipeline` | gcloud command in task |
| Cloud Scheduler | Manual job creation | cloud scheduler module (coming) |
| Job Monitoring | Manual polling | ansible async + monitoring |

---

## File Structure

### Bash Approach

```
scripts/
└── deploy.sh                # Single 500+ line script
    ├── GCP setup functions
    ├── BigQuery setup functions
    ├── Dataflow deployment functions
    ├── Docker setup functions
    └── Error handling throughout
```

**Issues**:
- All logic in one file
- Difficult to test components independently
- Manual error handling throughout
- Environment switching requires script modifications

### Ansible Approach

```
ansible/
├── ansible.cfg             # Global configuration
├── requirements.yml        # Collection dependencies
├── inventory/
│   ├── hosts.yml          # Inventory + variables
│   ├── hosts.example.yml  # Template
│   ├── dev.yml            # Dev environment (optional)
│   ├── staging.yml        # Staging environment (optional)
│   └── prod.yml           # Prod environment (optional)
├── playbooks/
│   ├── deploy.yml         # Main orchestration
│   ├── run-pipeline.yml   # Pipeline execution
│   └── verify.yml         # Verification
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

**Advantages**:
- Clear separation of concerns
- Reusable components (roles)
- Environment-specific variables
- Consistent Ansible patterns

---

## Command Migration

### GCP Setup

**Before (Bash)**:
```bash
./scripts/deploy.sh setup-gcp
```

**After (Ansible)**:
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  --tags=gcp
```

---

### BigQuery Setup

**Before (Bash)**:
```bash
./scripts/deploy.sh setup-bigquery
```

**After (Ansible)**:
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  --tags=bigquery
```

---

### Dataflow Deployment

**Before (Bash)**:
```bash
./scripts/deploy.sh deploy-dataflow
```

**After (Ansible)**:
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  --tags=dataflow
```

---

### Docker Setup

**Before (Bash)**:
```bash
./scripts/deploy.sh setup-docker
```

**After (Ansible)**:
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  --tags=docker
```

---

## Environment Configuration

### Bash Script Approach

```bash
# Edit script directly for each environment
ENVIRONMENT="dev"  # Change this for staging/prod
GCP_PROJECT="my-project"  # Change this

./scripts/deploy.sh
```

**Issues**:
- Manual edits required
- Easy to deploy to wrong environment
- No version control for configs
- Difficult to track what changed

### Ansible Approach

```bash
# Use inventory variables
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "environment=dev"

# Or create separate inventory files
ansible-playbook -i ansible/inventory/dev.yml \
  ansible/playbooks/deploy.yml

# Or combine both
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  -e "@ansible/inventory/prod.yml"
```

**Advantages**:
- Variables in separate files
- Git-tracked configurations
- Easy to switch environments
- Can override on command line
- No manual script editing

---

## Error Handling

### Bash Error Handling

```bash
# Manual error checking
if ! gcloud services enable dataflow.googleapis.com; then
    echo "ERROR: Failed to enable API"
    exit 1
fi

# Trap handler
trap 'cleanup' EXIT
cleanup() {
    if [ $? -ne 0 ]; then
        echo "Error occurred"
        # Manual rollback steps
    fi
}
```

**Issues**:
- Repetitive error checking
- Manual rollback logic needed
- Difficult to track failures across multiple steps

### Ansible Error Handling

```yaml
- name: Enable API
  google.cloud.gcp_service:
    name: dataflow.googleapis.com
  register: api_result
  failed_when: api_result is failed
  
- name: Rollback if failed
  block:
    - name: Some cleanup task
  rescue:
    - name: Handle error
      debug:
        msg: "API enablement failed"
```

**Advantages**:
- Native block/rescue blocks
- Automatic error propagation
- Conditional error handling
- No-fail options per task

---

## Testing & Validation

### Bash Testing

```bash
# Manual validation
./scripts/deploy.sh setup-gcp
# Then manually verify:
gcloud projects describe PROJECT_ID
gcloud compute project-info describe --project=PROJECT_ID
bq ls
```

### Ansible Testing

```bash
# Preview changes without applying (check mode)
ansible-playbook ansible/playbooks/deploy.yml --check

# Run verification playbook
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml

# Verbose output
ansible-playbook ansible/playbooks/deploy.yml -vvv

# Debug specific task
ansible-playbook ansible/playbooks/deploy.yml \
  -e "debug=true"
```

**Advantages**:
- Built-in check mode
- No-op dry runs
- Dedicated verification playbook
- Enhanced logging

---

## Monitoring & Logging

### Bash Approach

```bash
# Manual log checking
tail -f deploy-log.txt

# Manual output parsing
gcloud dataflow jobs describe JOB_ID | grep "state"
```

**Issues**:
- Manual log monitoring
- Limited structured logging
- Difficult to parse output
- No centralized logging

### Ansible Approach

```bash
# Automatic task logging
ansible-playbook ansible/playbooks/deploy.yml \
  > ansible/logs/deploy.log 2>&1

# View logs
cat ansible/logs/ansible.log

# Task-specific output
ansible-playbook ansible/playbooks/deploy.yml \
  -e "log_level=DEBUG"

# Slack integration
# (Built-in post-task notifiers)
```

**Advantages**:
- Automatic logging
- Structured task output
- File-based logging
- Slack/email notifications
- Tag-based filtering

---

## Migration Checklist

If migrating from bash scripts to Ansible:

- [ ] **Install Ansible**: `pip install 'ansible>=2.14.0'`
- [ ] **Install Collections**: `ansible-galaxy install -r ansible/requirements.yml`
- [ ] **Copy Inventory**: `cp ansible/inventory/hosts.example.yml ansible/inventory/hosts.yml`
- [ ] **Update Variables**: Edit `ansible/inventory/hosts.yml` with your GCP project ID
- [ ] **Test Connectivity**: `ansible localhost -m ping`
- [ ] **Dry Run**: `ansible-playbook ansible/playbooks/deploy.yml --check`
- [ ] **Run verify.yml**: `ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/verify.yml`
- [ ] **Deploy**: `ansible-playbook ansible/playbooks/deploy.yml -e "environment=dev"`
- [ ] **Verify Resources**: `ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/verify.yml`
- [ ] **Document Changes**: Update team documentation with new procedures

---

## Advantages Summary

### Bash Scripts
- ✅ Familiar to sysadmins
- ✅ No additional dependencies
- ✅ Direct tool usage

### Ansible (NEW)
- ✅ **Idempotent**: Safe to run multiple times
- ✅ **Modular**: Reusable roles
- ✅ **Declarative**: "What, not how"
- ✅ **Multi-environment**: Single playbook, multiple configs
- ✅ **Testable**: Check mode for validation
- ✅ **Documented**: Built-in documentation
- ✅ **Scalable**: Handles multiple clouds
- ✅ **Community**: Large ecosystem of roles & collections

---

## Future Roadmap

### Near Term
- [ ] Add Ansible Tower/AWX integration
- [ ] Implement Slack notifications for all playbooks
- [ ] Add Grafana dashboard provisioning
- [ ] Create cost reporting role

### Medium Term
- [ ] Implement GitOps with Ansible
- [ ] Add Terraform provider support
- [ ] Create multi-cloud deployment playbooks
- [ ] Add disaster recovery playbooks

### Long Term
- [ ] Implement Kubernetes deployment
- [ ] Add ML Pipeline orchestration
- [ ] Create self-healing infrastructure
- [ ] Implement zero-downtime deployments

---

## Support & Resources

### Documentation
- [Ansible Official Docs](https://docs.ansible.com/)
- [Google Cloud Ansible Collection](https://galaxy.ansible.com/google/cloud)
- [Azure Ansible Collection](https://galaxy.ansible.com/azure/azcollection)

### Migration Support
- See [ANSIBLE_DEPLOY.md](ANSIBLE_DEPLOY.md) for detailed usage
- See [ANSIBLE_TROUBLESHOOTING.md](ANSIBLE_TROUBLESHOOTING.md) for common issues
- See [QUICK_START_ANSIBLE.md](QUICK_START_ANSIBLE.md) for quick reference

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0

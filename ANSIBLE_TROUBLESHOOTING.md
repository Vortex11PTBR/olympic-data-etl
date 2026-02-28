# Ansible Troubleshooting Guide

## Common Issues & Solutions

### Installation Issues

#### Issue: Ansible Installation Fails

**Error Message**:
```
ERROR: Could not find a version that satisfies the requirement ...
```

**Solutions**:

1. **Update pip**:
```bash
pip install --upgrade pip setuptools wheel
pip install ansible>=2.14.0
```

2. **Use specific version**:
```bash
pip install ansible==2.14.0
```

3. **Install with extras**:
```bash
pip install 'ansible[google,azure]'
```

---

#### Issue: Collections Not Found

**Error Message**:
```
ERROR! couldn't resolve module/action 'google.cloud.gcp_*'
```

**Solution**:

```bash
# Install all requirements
ansible-galaxy install -r ansible/requirements.yml -f

# Or install individually
ansible-galaxy collection install google.cloud==1.14.0
ansible-galaxy collection install azure.azcollection==1.18.0
ansible-galaxy collection install community.general==7.4.0
ansible-galaxy collection install community.docker==5.3.0

# Verify installation
ansible-galaxy collection list
```

---

### Authentication Issues

#### Issue: GCP Authentication Fails

**Error Message**:
```
fatal: [localhost]: FAILED! => {"msg": "Error: ... (gcloud auth application-default login)"}
```

**Solutions**:

1. **Default Application Credentials**:
```bash
gcloud auth application-default login
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
```

2. **Service Account Key**:
```bash
# Create service account
gcloud iam service-accounts create ansible-deploy \
  --display-name="Ansible Deployment Account"

# Create key
gcloud iam service-accounts keys create ~/ansible-key.json \
  --iam-account=ansible-deploy@PROJECT_ID.iam.gserviceaccount.com

# Export
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/ansible-key.json"

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:ansible-deploy@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/editor"

# Verify
gcloud auth list
```

3. **Check Permissions in Inventory**:
```bash
# Ensure gcp_credentials_file path is correct
gcp_credentials_file: "/home/user/.config/gcloud/application_default_credentials.json"
```

---

#### Issue: Azure Authentication Fails

**Error Message**:
```
FAILED! => {"msg": "Unexpected kwargs passed to __init__: auth_source"}
```

**Solution**:

1. **Install Azure CLI**:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

2. **Login to Azure**:
```bash
az login
az account set --subscription="SUBSCRIPTION_ID"
```

3. **Verify in Inventory**:
```yaml
azure_resource_group: "your-rg"
azure_subscription_id: "your-subscription-id"
```

---

### Playbook Execution Issues

#### Issue: "hosts does not match any hosts"

**Error Message**:
```
fatal: [localhost]: FAILED! => {"msg": "Unable to connect to localhost"}
```

**Solutions**:

1. **Fix Inventory**:
```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
      ansible_python_interpreter: /usr/bin/python3
```

2. **Verify Connection**:
```bash
ansible localhost -m ping
```

3. **Check ansible.cfg**:
```ini
[defaults]
inventory = ./ansible/inventory/hosts.yml
host_key_checking = False
```

---

#### Issue: Python Interpreter Not Found

**Error Message**:
```
fatal: [localhost]: FAILED! => {"msg": "the python interpreter at ... is not a valid Elf binary"}
```

**Solutions**:

1. **Update ansible.cfg**:
```ini
[defaults]
inventory = ./ansible/inventory/hosts.yml
ansible_python_interpreter = /usr/bin/python3
```

2. **Update Inventory**:
```yaml
all:
  vars:
    ansible_python_interpreter: /usr/bin/python3
```

3. **Install Python**:
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
```

---

#### Issue: Permission Denied Errors

**Error Message**:
```
ERROR! Unexpected failure during file creation: Permission denied
```

**Solutions**:

1. **Use become/sudo**:
```bash
ansible-playbook playbooks/deploy.yml --ask-become-pass
```

2. **Add become to playbook**:
```yaml
tasks:
  - name: Create directory
    file:
      path: /opt/olympic-etl
      state: directory
    become: yes
    become_user: root
```

3. **Check file permissions**:
```bash
ls -la ansible/playbooks/
chmod +x ansible/playbooks/*.yml
```

---

### GCP-Specific Issues

#### Issue: "Project ID not found"

**Error Message**:
```
FAILED! => {"msg": "error: (gcloud.compute.project-info.describe) The Project ID 'xxx' is not found"}
```

**Solutions**:

1. **Verify project exists**:
```bash
gcloud projects list
gcloud config get-value project
```

2. **Update in inventory**:
```yaml
all:
  vars:
    gcp_project_id: "actual-project-id"  # ← Check spelling
```

3. **Set as default**:
```bash
gcloud config set project YOUR_PROJECT_ID
```

---

#### Issue: "API not enabled"

**Error Message**:
```
FAILED! => {"msg": "... The following APIs are not enabled: ... (dataflow.googleapis.com)"}
```

**Solutions**:

1. **Enable manually**:
```bash
gcloud services enable dataflow.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

2. **Or let Ansible enable them**:
```yaml
- name: Enable APIs
  google.cloud.gcp_compute_project_info:
    project: "{{ gcp_project_id }}"
```

---

#### Issue: "Service Account Not Found"

**Error Message**:
```
FAILED! => {"msg": "... Failed to retrieve service account ..."}
```

**Solutions**:

1. **Create service account**:
```bash
gcloud iam service-accounts create beam-sa \
  --display-name="Beam Service Account"
```

2. **Verify it exists**:
```bash
gcloud iam service-accounts list
gcloud iam service-accounts describe beam-sa@PROJECT_ID.iam.gserviceaccount.com
```

3. **Grant permissions**:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member=serviceAccount:beam-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/dataflow.worker
```

---

### BigQuery Issues

#### Issue: "Dataset not found"

**Error Message**:
```
FAILED! => {"msg": "... Dataset not found ... (NotFound)"}
```

**Solutions**:

1. **Create dataset manually**:
```bash
bq mk --dataset \
  --description="Olympic Dataset" \
  --location=us-central1 \
  olympics
```

2. **Check existing datasets**:
```bash
bq ls
```

3. **Verify in inventory**:
```yaml
gcp_dataset_name: "olympics"  # Must match
```

---

#### Issue: "Table schema mismatch"

**Error Message**:
```
FAILED! => {"msg": "... Fields cannot be changed ..."}
```

**Solutions**:

1. **Delete and recreate table**:
```bash
bq rm -f olympics.medals
# Then run playbook again
```

2. **Update schema in playbook**:
```yaml
- name: Update table schema
  google.cloud.gcp_bigquery_table:
    name: medals
    schema_fields:
      - name: record_id
        type: STRING
        mode: REQUIRED
```

---

### Docker Issues

#### Issue: "Docker daemon not running"

**Error Message**:
```
ERROR: Cannot connect to Docker daemon at unix:///var/run/docker.sock
```

**Solutions**:

1. **Start Docker**:
```bash
sudo systemctl start docker
sudo systemctl enable docker  # Auto-start on reboot
```

2. **Add user to docker group**:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

3. **Verify**:
```bash
docker ps
docker version
```

---

#### Issue: "Permission denied while trying to connect"

**Error Message**:
```
ERROR: permission denied while trying to connect to the Docker daemon
```

**Solution**:

```bash
# Add current user to docker group
sudo usermod -aG docker $(whoami)

# Apply new group membership
newgrp docker

# Verify
docker ps
```

---

### Dataflow Issues

#### Issue: "Dataflow job failed"

**Error Message**:
```
FAILED! => {"msg": "... Job failed with state FAILED"}
```

**Solutions**:

1. **Check job logs**:
```bash
gcloud dataflow jobs list --region=us-central1
gcloud dataflow jobs describe JOB_ID \
  --region=us-central1 \
  --view=monitoring
```

2. **View detailed logs**:
```bash
gcloud logging read "resource.type=dataflow_step AND jsonPayload.jobName=JOB_NAME" \
  --limit=50 \
  --format=json
```

3. **Common causes**:
   - Pipeline code syntax errors → Check `src/beam/pipelines/olympic_etl_pipeline.py`
   - Schema mismatch → Verify BigQuery table schema
   - Memory issues → Increase `dataflow_machine_type` or `dataflow_workers`

---

#### Issue: "Template not found"

**Error Message**:
```
FAILED! => {"msg": "... Invalid template path ..."}
```

**Solution**:

```bash
# Rebuild template
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml \
  --tags=dataflow

# Verify template exists
gsutil ls gs://PROJECT-beam-templates/

# Check Artifact Registry
gcloud artifacts docker images list us-central1-docker.pkg.dev/PROJECT/beam/
```

---

### Performance Issues

#### Issue: "Ansible playbook running slowly"

**Solutions**:

1. **Enable async operations**:
```yaml
tasks:
  - name: Long-running task
    shell: long_command
    async: 300
    poll: 0
    register: long_task

  - name: Check async result
    async_status:
      jid: "{{ long_task.ansible_job_id }}"
    register: result
    until: result.finished
    retries: 30
```

2. **Increase parallelism** in ansible.cfg:
```ini
[defaults]
forks = 10  # Default is 5
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600
```

3. **Skip unnecessary tasks**:
```bash
ansible-playbook playbooks/deploy.yml \
  --skip-tags "docker"  # Skip slow tasks
```

---

#### Issue: "Dataflow job taking too long"

**Solutions**:

1. **Increase workers**:
```bash
ansible-playbook ansible/playbooks/run-pipeline.yml \
  -e "dataflow_workers=10" \
  -e "dataflow_max_workers=50"
```

2. **Use better machine type**:
```bash
ansible-playbook ansible/playbooks/run-pipeline.yml \
  -e "dataflow_machine_type=n1-highmem-4"
```

3. **Monitor with**:
```bash
gcloud dataflow jobs describe JOB_ID \
  --region=us-central1 \
  --view=monitoring
```

---

### Debugging

#### Enable Verbose Output

```bash
# Show all variables and tasks
ansible-playbook playbooks/deploy.yml -vvv

# Show facts gathered
ansible-playbook playbooks/deploy.yml -vvv --gather-subset=all

# Show only failed tasks
ansible-playbook playbooks/deploy.yml -vvv --failed-only
```

#### Check Syntax

```bash
# Validate playbook syntax
ansible-playbook --syntax-check playbooks/deploy.yml

# Lint with ansible-lint (requires pip install ansible-lint)
ansible-lint playbooks/deploy.yml
```

#### Dry Run

```bash
# Preview changes without applying
ansible-playbook playbooks/deploy.yml --check -vv
```

#### Debug Specific Task

```yaml
- name: Debug task
  debug:
    msg: "Variable value: {{ variable_name }}"

- name: Print all variables
  debug:
    var: hostvars[inventory_hostname]
```

---

## Health Check Commands

```bash
# Check all components
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/verify.yml -e "environment=dev"

# Verify GCP access
gcloud auth list
gcloud config list

# List deployed resources
gcloud projects list
gcloud compute project-info describe --project=PROJECT_ID
gcloud bigquery datasets list
gcloud dataflow templates describe gs://PROJECT-beam-templates/*

# Check Dataflow jobs
gcloud dataflow jobs list --region=us-central1
gcloud dataflow jobs describe JOB_ID --region=us-central1

# Verify Docker
docker ps -a
docker images
```

---

## Getting Help

1. **Check logs**:
   ```bash
   cat ansible/logs/ansible.log
   tail -f ansible/logs/ansible.log
   ```

2. **Enable debug logging**:
   ```bash
   export ANSIBLE_DEBUG=1
   ansible-playbook playbooks/deploy.yml -vvv
   ```

3. **Check Google Cloud documentation**:
   - [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
   - [Dataflow Documentation](https://cloud.google.com/dataflow/docs)
   - [Cloud Storage Documentation](https://cloud.google.com/storage/docs)

4. **Report issues**:
   - Include full error message
   - Share relevant logs
   - Provide Ansible version: `ansible --version`
   - Provide Python version: `python --version`

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0

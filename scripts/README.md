# Scripts Directory - Deployment Automation

This directory contains automation scripts for deploying the Olympic Data ETL project.

---

## Available Scripts

### 1. setup_ansible.sh (Linux/macOS)

**Purpose**: Complete automated setup of Ansible environment

**Location**: `scripts/setup_ansible.sh`

**Usage**:
```bash
bash scripts/setup_ansible.sh
```

**What it does**:
1. ✅ Checks prerequisites (Python, pip, git, gcloud)
2. ✅ Installs Ansible and collections
3. ✅ Creates Ansible inventory from template
4. ✅ Configures GCP credentials
5. ✅ Creates environment variables file
6. ✅ Prepares log directory
7. ✅ Verifies setup

**Requirements**:
- Python 3.8+
- pip
- git (optional)
- Google Cloud SDK

**Time**: ~5 minutes

**Example**:
```bash
cd ~/Desktop/olympic-data-etl
bash scripts/setup_ansible.sh

# Follow the prompts:
# Continue? (y/n) y
# Enter GCP Project ID: my-project
# (Follow GCP login if prompted)
```

**Output**:
```
========================================
Olympic Data ETL - Ansible Setup
========================================

✓ All prerequisites found
✓ Ansible installed
✓ Collections installed
✓ Inventory template created at ansible/inventory/hosts.yml
✓ GCP authenticated
✓ Current GCP Project: my-project
✓ Environment file created: .env.local

========================================
Setup Complete!
========================================
```

---

### 2. setup_ansible.ps1 (Windows)

**Purpose**: Complete automated setup of Ansible environment on Windows

**Location**: `scripts/setup_ansible.ps1`

**Usage**:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1
```

**What it does**:
1. ✅ Checks prerequisites (Python, pip, gcloud)
2. ✅ Installs Ansible and collections
3. ✅ Creates Ansible inventory from template
4. ✅ Configures GCP credentials
5. ✅ Creates environment variables file
6. ✅ Prepares log directory
7. ✅ Verifies setup

**Requirements**:
- PowerShell 5.0+
- Python 3.8+
- pip
- Google Cloud SDK

**Time**: ~5 minutes

**Example**:
```powershell
cd $env:USERPROFILE\Desktop\olympic-data-etl
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1

# Follow the prompts:
# Continue? (y/n) y
# Enter GCP Project ID: my-project
# (Follow GCP login if prompted)
```

**Output**:
```
========================================
Olympic Data ETL - Ansible Setup (Windows)
========================================

✓ Python is installed
✓ pip is installed
✓ Ansible installed
✓ Collections installed
✓ Inventory created at: C:\Users\...\ansible\inventory\hosts.yml

========================================
Setup Complete!
========================================
```

**Optional Parameters**:
```powershell
# Skip specific setup steps
# SkipPython: Skip Python package installation
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1 -SkipPython

# SkipAnsible: Skip Ansible installation
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1 -SkipAnsible

# SkipGCP: Skip GCP credential setup
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1 -SkipGCP
```

---

### 3. deploy.sh (Original Bash Script)

**Location**: `scripts/deploy.sh`

**Status**: ⚠️ Deprecated - Use Ansible playbooks instead

**Note**: This original bash deployment script is replaced by the more robust Ansible playbooks. For migration information, see [BASH_VS_ANSIBLE.md](../BASH_VS_ANSIBLE.md).

**Why Ansible is better**:
- Idempotent (safe to run multiple times)
- Better error handling
- Multi-environment support
- Modular roles
- Built-in check mode

---

## Script Selection Guide

### "I'm on Linux/macOS"

Use `setup_ansible.sh`:
```bash
bash scripts/setup_ansible.sh
```

### "I'm on Windows"

Use `setup_ansible.ps1`:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1
```

### "I'm in Cloud Shell (GCP)"

Use either:
```bash
# Cloud Shell is Linux-based
bash scripts/setup_ansible.sh
```

### "I already have Ansible installed"

You can skip the installation:

**Linux/macOS**:
```bash
bash scripts/setup_ansible.sh
# When prompted: "Continue despite missing dependencies? y"
```

**Windows**:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1 -SkipPython
```

---

## Post-Setup

After running setup script:

### 1. Source Environment (Linux/macOS)

```bash
source .env.local
# Or
export $(cat .env.local | xargs)
```

### 2. Load Environment (Windows)

```powershell
& '.\.env.local.ps1'
```

### 3. Edit Inventory

Update GCP project ID and settings:

```bash
# Linux/macOS
nano ansible/inventory/hosts.yml

# Windows
notepad ansible/inventory/hosts.yml
```

### 4. Test Connectivity

```bash
ansible localhost -m ping
```

### 5. Deploy

```bash
# Development environment
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/deploy.yml -e "environment=dev"
```

---

## Troubleshooting Setup Scripts

### Problem: "Permission Denied" (Linux/macOS)

**Solution**:
```bash
# Make script executable
chmod +x scripts/setup_ansible.sh

# Then run
bash scripts/setup_ansible.sh
```

### Problem: "Python not found"

**Solution**:
```bash
# Install Python
apt-get install python3 python3-pip    # Ubuntu/Debian
brew install python3                   # macOS
choco install python                   # Windows (Chocolatey)

# Then run setup script again
bash scripts/setup_ansible.sh
```

### Problem: "gcloud not found"

**Solution**:
```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Then run setup script again
bash scripts/setup_ansible.sh
```

### Problem: "pip version too old" (Windows)

**Solution**:
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Then run setup script
powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1
```

### Problem: Script completed but inventory.yml is empty

**Solution**:
```bash
# Manually copy template
cp ansible/inventory/hosts.example.yml ansible/inventory/hosts.yml

# Then edit
nano ansible/inventory/hosts.yml
```

---

## Environment Files Created

### Linux/macOS: `.env.local`

```bash
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/application_default_credentials.json"
export ANSIBLE_CONFIG="./ansible.cfg"
export ANSIBLE_INVENTORY="./ansible/inventory/hosts.yml"
export ANSIBLE_HOST_KEY_CHECKING=False
```

**Load with**:
```bash
source .env.local
```

### Windows: `.env.local.ps1`

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "$env:USERPROFILE\.config\gcloud\application_default_credentials.json"
$env:ANSIBLE_CONFIG = ".\ansible.cfg"
$env:ANSIBLE_INVENTORY = ".\ansible\inventory\hosts.yml"
$env:ANSIBLE_HOST_KEY_CHECKING = "False"
```

**Load with**:
```powershell
& '.\.env.local.ps1'
```

---

## Next Steps After Setup

1. **Review Documentation**:
   - Quick start: `QUICK_START_ANSIBLE.md`
   - Full guide: `DEPLOYMENT_GUIDE.md`
   - Reference: `ANSIBLE_DEPLOY.md`

2. **Configure Inventory**:
   ```bash
   nano ansible/inventory/hosts.yml
   # Update: gcp_project_id, environment, etc.
   ```

3. **Test Connectivity**:
   ```bash
   ansible localhost -m ping
   ```

4. **Dry Run**:
   ```bash
   ansible-playbook ansible/playbooks/deploy.yml --check
   ```

5. **Deploy**:
   ```bash
   ansible-playbook -i ansible/inventory/hosts.yml \
     ansible/playbooks/deploy.yml -e "environment=dev"
   ```

---

## Script Customization

### Modify setup_ansible.sh

Edit the bash script if you need custom setup:

```bash
# Key sections to customize:
# Lines 80-90: Check prerequisites
# Lines 95-110: Install Ansible
# Lines 115-125: Configure GCP
# Lines 130-145: Create inventory
```

### Modify setup_ansible.ps1

Edit the PowerShell script if you need custom setup:

```powershell
# Key sections to customize:
# Lines 60-80: Check prerequisites
# Lines 85-105: Install Ansible
# Lines 110-130: Configure GCP
# Lines 135-155: Create inventory
```

---

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Run setup script
  run: bash scripts/setup_ansible.sh

- name: Deploy with Ansible
  run: |
    source .env.local
    ansible-playbook -i ansible/inventory/hosts.yml \
      ansible/playbooks/deploy.yml -e "environment=prod"
```

### GitLab CI

```yaml
setup-ansible:
  script:
    - bash scripts/setup_ansible.sh
    - source .env.local
    - ansible-playbook ansible/playbooks/deploy.yml -e "environment=prod"
```

### Jenkins

```groovy
stage('Setup Ansible') {
    steps {
        sh 'bash scripts/setup_ansible.sh'
    }
}

stage('Deploy') {
    steps {
        sh '''
            source .env.local
            ansible-playbook -i ansible/inventory/hosts.yml \
              ansible/playbooks/deploy.yml -e "environment=prod"
        '''
    }
}
```

---

## Script Maintenance

### Check for Updates

```bash
# View script version
head -n 5 scripts/setup_ansible.sh

# Check last modified
ls -l scripts/setup_ansible.sh
```

### Backup Script

```bash
# Create backup
cp scripts/setup_ansible.sh scripts/setup_ansible.sh.backup

# Before making changes
git commit -am "Backup setup script before modifications"
```

---

## Support

For issues with setup scripts:

1. Check [ANSIBLE_TROUBLESHOOTING.md](../ANSIBLE_TROUBLESHOOTING.md)
2. Review script output carefully
3. Verify prerequisites are installed
4. Check GCP credentials are valid

---

## Related Documentation

- **[QUICK_START_ANSIBLE.md](../QUICK_START_ANSIBLE.md)** - 30-minute quick start
- **[DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)** - Complete step-by-step guide
- **[ANSIBLE_DEPLOY.md](../ANSIBLE_DEPLOY.md)** - Full Ansible reference
- **[ANSIBLE_INDEX.md](../ANSIBLE_INDEX.md)** - Documentation index

---

**Last Updated**: February 28, 2026  
**Version**: 1.0.0  
**Maintained By**: Data Engineering Team

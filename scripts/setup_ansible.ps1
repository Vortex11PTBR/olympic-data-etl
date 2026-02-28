# Olympic Data ETL - Ansible Setup Script for Windows
# This script initializes Ansible for the Olympic Data ETL project on Windows

# Requires: PowerShell 5.0+
# Run with: powershell -ExecutionPolicy Bypass -File scripts/setup_ansible.ps1

param(
    [switch]$SkipPython = $false,
    [switch]$SkipGCP = $false,
    [switch]$SkipAnsible = $false
)

# ============================================
# Configuration
# ============================================
$ErrorActionPreference = "Stop"
$WarningPreference = "Continue"

$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent -Path $ScriptDir
$AnsibleDir = Join-Path -Path $ProjectRoot -ChildPath "ansible"
$LogDir = Join-Path -Path $AnsibleDir -ChildPath "logs"
$InventoryDir = Join-Path -Path $AnsibleDir -ChildPath "inventory"

# ============================================
# Functions
# ============================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Test-Command {
    param([string]$CommandName)
    
    try {
        if (Get-Command $CommandName -ErrorAction SilentlyContinue) {
            Write-Success "$CommandName is installed"
            return $true
        }
    } catch {
        Write-Error-Custom "$CommandName is not installed"
        return $false
    }
}

function Install-PythonModule {
    param([string]$ModuleName)
    
    Write-Host "Installing $ModuleName..."
    python -m pip install --upgrade $ModuleName
    
    if ($?) {
        Write-Success "$ModuleName installed"
    } else {
        Write-Error-Custom "Failed to install $ModuleName"
        exit 1
    }
}

# ============================================
# Main Script
# ============================================

Clear-Host
Write-Host "Olympic Data ETL - Ansible Setup (Windows)" -ForegroundColor Cyan -BackgroundColor Black

Write-Host "This script will:"
Write-Host "  1. Check prerequisites"
Write-Host "  2. Install/Update Ansible"
Write-Host "  3. Setup inventory files"
Write-Host "  4. Configure GCP credentials"
Write-Host "  5. Test connectivity"
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Warning-Custom "Setup cancelled"
    exit 0
}

# ============================================
# 1. Check Prerequisites
# ============================================
Write-Header "1. Checking Prerequisites"

$allOK = $true

if (-not (Test-Command "python")) {
    Write-Error-Custom "Python not found. Please install Python 3.8+"
    Write-Host "Download from: https://www.python.org/downloads/"
    $allOK = $false
} else {
    python --version
}

if (-not (Test-Command "pip")) {
    Write-Error-Custom "pip not found"
    $allOK = $false
} else {
    pip --version
}

if (-not (Test-Command "git")) {
    Write-Warning-Custom "git not found (optional but recommended)"
}

if (-not (Test-Command "gcloud")) {
    Write-Warning-Custom "gcloud not found. Download from: https://cloud.google.com/sdk/docs/install"
} else {
    gcloud version | Select-Object -First 1
}

if (-not (Test-Command "docker")) {
    Write-Warning-Custom "Docker not found (optional but recommended)"
}

if (-not $allOK) {
    $continue = Read-Host "Continue despite missing dependencies? (y/n)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        exit 1
    }
}

Write-Success "Prerequisites check complete"

# ============================================
# 2. Install/Update Python Packages
# ============================================
if (-not $SkipPython) {
    Write-Header "2. Installing Python Packages"
    
    Write-Host "Upgrading pip..."
    python -m pip install --upgrade pip setuptools wheel
    
    Install-PythonModule "ansible"
    
    Write-Host "Installing optional Ansible packages..."
    pip install 'ansible[google,azure]' -q
    
    ansible --version
}

# ============================================
# 3. Install Ansible Collections
# ============================================
if (-not $SkipAnsible) {
    Write-Header "3. Installing Ansible Collections"
    
    $requirementsFile = Join-Path -Path $AnsibleDir -ChildPath "requirements.yml"
    if (Test-Path $requirementsFile) {
        Write-Host "Installing from $requirementsFile..."
        ansible-galaxy install -r $requirementsFile -f
        Write-Success "Collections installed"
    } else {
        Write-Warning-Custom "requirements.yml not found"
    }
}

# ============================================
# 4. Create Inventory
# ============================================
Write-Header "4. Setting up Inventory"

$inventoryFile = Join-Path -Path $InventoryDir -ChildPath "hosts.yml"
$exampleFile = Join-Path -Path $InventoryDir -ChildPath "hosts.example.yml"

# Create inventory directory if not exists
if (-not (Test-Path $InventoryDir)) {
    New-Item -ItemType Directory -Path $InventoryDir | Out-Null
    Write-Success "Created directory: $InventoryDir"
}

if (-not (Test-Path $inventoryFile)) {
    if (Test-Path $exampleFile) {
        Write-Host "Creating inventory from template..."
        Copy-Item -Path $exampleFile -Destination $inventoryFile
        Write-Success "Inventory created at: $inventoryFile"
        Write-Warning-Custom "Please edit with your GCP project ID"
        Write-Host "Edit with: notepad $inventoryFile"
    } else {
        Write-Error-Custom "Template file not found: $exampleFile"
    }
} else {
    Write-Success "Inventory already exists: $inventoryFile"
}

# ============================================
# 5. Configure GCP Credentials
# ============================================
if (-not $SkipGCP) {
    Write-Header "5. Setting up GCP Credentials"
    
    Write-Host "Checking GCP authentication..."
    
    try {
        $projectId = & gcloud config get-value project 2>$null
        
        if ($projectId) {
            Write-Success "Current GCP Project: $projectId"
        } else {
            Write-Warning-Custom "No active GCP project"
            $projectId = Read-Host "Enter your GCP Project ID"
            gcloud config set project $projectId
        }
        
        Write-Host "Setting up Application Default Credentials..."
        gcloud auth application-default login
        
        Write-Success "GCP credentials configured"
    } catch {
        Write-Warning-Custom "GCP setup skipped"
    }
}

# ============================================
# 6. Create Environment Variables File
# ============================================
Write-Header "6. Creating Environment Configuration"

$envFilePath = Join-Path -Path $ProjectRoot -ChildPath ".env.local.ps1"

@"
# Environment Variables for Ansible (PowerShell)
`$env:GOOGLE_APPLICATION_CREDENTIALS = "`$env:USERPROFILE\.config\gcloud\application_default_credentials.json"
`$env:ANSIBLE_CONFIG = "$ProjectRoot\ansible.cfg"
`$env:ANSIBLE_INVENTORY = "$InventoryDir\hosts.yml"
`$env:ANSIBLE_HOST_KEY_CHECKING = "False"

Write-Host "Environment variables loaded" -ForegroundColor Green
"@ | Out-File -FilePath $envFilePath -Encoding UTF8

Write-Success "Environment file created: $envFilePath"
Write-Host "Run: & '$envFilePath'" -ForegroundColor Yellow

# ============================================
# 7. Create Log Directory
# ============================================
Write-Header "7. Preparing Log Directory"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}
Write-Success "Log directory ready: $LogDir"

# ============================================
# 8. Verify Setup
# ============================================
Write-Header "8. Verifying Setup"

$ansibleConfigPath = Join-Path -Path $ProjectRoot -ChildPath "ansible.cfg"
if (Test-Path $ansibleConfigPath) {
    Write-Success "Ansible configuration found"
} else {
    Write-Warning-Custom "ansible.cfg not found"
}

if (Test-Path $inventoryFile) {
    Write-Success "Inventory found"
} else {
    Write-Error-Custom "Inventory not found"
}

$playbookCount = (Get-ChildItem -Path (Join-Path -Path $AnsibleDir -ChildPath "playbooks") -Filter "*.yml" -ErrorAction SilentlyContinue | Measure-Object).Count
if ($playbookCount -gt 0) {
    Write-Success "Found $playbookCount playbook(s)"
} else {
    Write-Warning-Custom "No playbooks found"
}

$roleCount = (Get-ChildItem -Path (Join-Path -Path $AnsibleDir -ChildPath "roles") -Filter "main.yml" -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
if ($roleCount -gt 0) {
    Write-Success "Found $roleCount role(s)"
} else {
    Write-Warning-Custom "No roles found"
}

# ============================================
# Summary
# ============================================
Write-Header "Setup Complete!"

Write-Host "Next steps:"
Write-Host "  1. Load environment: & '.\\.env.local.ps1'" -ForegroundColor Yellow
Write-Host "  2. Edit inventory: notepad '$inventoryFile'" -ForegroundColor Yellow
Write-Host "  3. Test connectivity: ansible localhost -m ping" -ForegroundColor Yellow
Write-Host "  4. Verify setup: ansible-playbook -i '$inventoryFile' ansible/playbooks/verify.yml --check" -ForegroundColor Yellow
Write-Host "  5. Deploy: ansible-playbook -i '$inventoryFile' ansible/playbooks/deploy.yml -e `"environment=dev`"" -ForegroundColor Yellow
Write-Host ""

Write-Host "Documentation:"
Write-Host "  - Quick Start: Get-Content QUICK_START_ANSIBLE.md" -ForegroundColor Cyan
Write-Host "  - Full Guide: Get-Content ANSIBLE_DEPLOY.md" -ForegroundColor Cyan
Write-Host "  - Troubleshooting: Get-Content ANSIBLE_TROUBLESHOOTING.md" -ForegroundColor Cyan
Write-Host ""

Write-Success "Ansible setup ready!"
Write-Host ""

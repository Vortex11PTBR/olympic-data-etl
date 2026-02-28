#!/bin/bash

# Olympic Data ETL - Ansible Setup Script
# This script initializes Ansible for the Olympic Data ETL project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    fi
    print_success "$1 is installed"
    return 0
}

# Main script
main() {
    print_header "Olympic Data ETL - Ansible Setup"
    
    echo ""
    echo "This script will:"
    echo "  1. Check prerequisites"
    echo "  2. Create Ansible configuration"
    echo "  3. Setup inventory files"
    echo "  4. Install Python dependencies"
    echo "  5. Configure GCP credentials"
    echo ""
    
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Setup cancelled"
        exit 1
    fi
    
    # ============================================
    # 1. Check Prerequisites
    # ============================================
    print_header "1. Checking Prerequisites"
    
    MISSING_TOOLS=0
    
    check_command "python3" || MISSING_TOOLS=1
    check_command "pip" || MISSING_TOOLS=1
    check_command "git" || MISSING_TOOLS=1
    check_command "gcloud" || MISSING_TOOLS=1
    
    if [ $MISSING_TOOLS -eq 1 ]; then
        print_error "Please install missing tools and run again"
        exit 1
    fi
    
    print_success "All prerequisites found"
    
    # ============================================
    # 2. Install Ansible
    # ============================================
    print_header "2. Installing Ansible"
    
    echo "Installing Ansible and dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install 'ansible>=2.14.0' 'ansible[google,azure]'
    
    print_success "Ansible installed"
    ansible --version
    
    # ============================================
    # 3. Install Ansible Collections
    # ============================================
    print_header "3. Installing Ansible Collections"
    
    if [ -f "ansible/requirements.yml" ]; then
        echo "Installing from ansible/requirements.yml..."
        ansible-galaxy install -r ansible/requirements.yml -f
        print_success "Collections installed"
    else
        print_warning "ansible/requirements.yml not found, skipping"
    fi
    
    # ============================================
    # 4. Create Inventory File
    # ============================================
    print_header "4. Setting up Inventory"
    
    if [ ! -f "ansible/inventory/hosts.yml" ]; then
        if [ -f "ansible/inventory/hosts.example.yml" ]; then
            echo "Creating inventory from template..."
            cp ansible/inventory/hosts.example.yml ansible/inventory/hosts.yml
            print_success "Inventory template created at ansible/inventory/hosts.yml"
            print_warning "Please edit ansible/inventory/hosts.yml with your settings"
        else
            print_error "hosts.example.yml not found"
        fi
    else
        print_success "Inventory already exists at ansible/inventory/hosts.yml"
    fi
    
    # ============================================
    # 5. Configure GCP Credentials
    # ============================================
    print_header "5. Setting up GCP Credentials"
    
    echo "Checking GCP authentication..."
    
    if gcloud auth list | grep -q "ACTIVE"; then
        print_success "GCP authenticated"
        
        # Get current project
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            print_warning "No active GCP project set"
            read -p "Enter your GCP Project ID: " PROJECT_ID
            gcloud config set project "$PROJECT_ID"
        else
            print_success "Current GCP Project: $PROJECT_ID"
        fi
        
        # Setup credentials
        echo "Setting up application default credentials..."
        gcloud auth application-default login
        
        # Get credentials path
        CREDS_PATH="$HOME/.config/gcloud/application_default_credentials.json"
        if [ -f "$CREDS_PATH" ]; then
            print_success "Credentials saved to $CREDS_PATH"
            export GOOGLE_APPLICATION_CREDENTIALS="$CREDS_PATH"
        fi
    else
        print_warning "Not authenticated with GCP"
        echo "Run: gcloud auth login"
        read -p "Continue without GCP setup? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # ============================================
    # 6. Create Environment Variables File
    # ============================================
    print_header "6. Creating Environment File"
    
    ENV_FILE=".env.local"
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
# Environment Variables for Ansible
export GOOGLE_APPLICATION_CREDENTIALS="\$HOME/.config/gcloud/application_default_credentials.json"
export ANSIBLE_CONFIG="./ansible.cfg"
export ANSIBLE_INVENTORY="./ansible/inventory/hosts.yml"
export ANSIBLE_HOST_KEY_CHECKING=False
EOF
        print_success "Environment file created: $ENV_FILE"
        print_warning "Run: source .env.local"
    else
        print_success "Environment file already exists"
    fi
    
    # ============================================
    # 7. Create Log Directory
    # ============================================
    print_header "7. Preparing Log Directory"
    
    mkdir -p ansible/logs
    print_success "Log directory created: ansible/logs"
    
    # ============================================
    # 8. Verify Setup
    # ============================================
    print_header "8. Verifying Setup"
    
    echo "Checking Ansible configuration..."
    if [ -f "ansible.cfg" ]; then
        print_success "Ansible configuration found"
    else
        print_warning "ansible.cfg not found"
    fi
    
    echo ""
    echo "Checking inventory..."
    if [ -f "ansible/inventory/hosts.yml" ]; then
        print_success "Inventory found"
    else
        print_error "Inventory not found"
    fi
    
    echo ""
    echo "Checking playbooks..."
    count=$(find ansible/playbooks -name "*.yml" | wc -l)
    if [ $count -gt 0 ]; then
        print_success "Found $count playbook(s)"
    else
        print_warning "No playbooks found"
    fi
    
    echo ""
    echo "Checking roles..."
    count=$(find ansible/roles -name "main.yml" | wc -l)
    if [ $count -gt 0 ]; then
        print_success "Found $count role(s)"
    else
        print_warning "No roles found"
    fi
    
    # ============================================
    # Summary
    # ============================================
    print_header "Setup Complete!"
    
    echo ""
    echo "Next steps:"
    echo "  1. Source environment: source .env.local"
    echo "  2. Edit inventory: nano ansible/inventory/hosts.yml"
    echo "  3. Test connectivity: ansible localhost -m ping"
    echo "  4. Check setup: ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/verify.yml --check"
    echo "  5. Deploy: ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/deploy.yml -e \"environment=dev\""
    echo ""
    echo "Documentation:"
    echo "  - Quick Start: cat QUICK_START_ANSIBLE.md"
    echo "  - Full Guide: cat ANSIBLE_DEPLOY.md"
    echo "  - Troubleshooting: cat ANSIBLE_TROUBLESHOOTING.md"
    echo ""
    print_success "Setup ready!"
}

# Run main function
main

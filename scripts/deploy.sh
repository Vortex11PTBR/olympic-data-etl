#!/bin/bash
#
# Olympic Data ETL - Deployment Helper Script
# Automates common deployment tasks
#

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
GCP_PROJECT_ID="${1:-}"
ENVIRONMENT="${2:-dev}"
REGION="us-central1"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    command -v gcloud &> /dev/null || log_error "gcloud CLI not found. Install Google Cloud SDK."
    command -v python3 &> /dev/null || log_error "Python 3 not found."
    command -v docker &> /dev/null || log_warn "Docker not found. Skipping Docker steps."
    
    log_info "Prerequisites check passed!"
}

# Validate GCP project
validate_gcp_project() {
    if [ -z "$GCP_PROJECT_ID" ]; then
        log_error "Usage: $0 <GCP_PROJECT_ID> [environment]"
    fi
    
    log_info "Setting GCP project to: $GCP_PROJECT_ID"
    gcloud config set project $GCP_PROJECT_ID
    
    # Verify project exists
    gcloud projects describe $GCP_PROJECT_ID > /dev/null || \
        log_error "GCP project $GCP_PROJECT_ID not found"
    
    log_info "GCP project validated!"
}

# Setup GCP resources
setup_gcp_resources() {
    log_info "Setting up GCP resources for environment: $ENVIRONMENT..."
    
    # Enable APIs
    log_info "Enabling required APIs..."
    gcloud services enable \
        dataflow.googleapis.com \
        bigquery.googleapis.com \
        storage-api.googleapis.com \
        cloudlogging.googleapis.com \
        monitoring.googleapis.com \
        artifactregistry.googleapis.com
    
    # Create service account
    SA_NAME="olympic-etl-${ENVIRONMENT}-sa"
    SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
    
    log_info "Creating service account: $SA_NAME"
    
    if gcloud iam service-accounts describe $SA_EMAIL 2>/dev/null; then
        log_warn "Service account already exists: $SA_EMAIL"
    else
        gcloud iam service-accounts create $SA_NAME \
            --display-name="Olympic ETL Service Account ($ENVIRONMENT)"
        log_info "Service account created: $SA_EMAIL"
    fi
    
    # Grant roles
    log_info "Granting IAM roles..."
    roles=(
        "roles/dataflow.worker"
        "roles/bigquery.dataEditor"
        "roles/storage.objectAdmin"
        "roles/cloudlogging.logWriter"
        "roles/monitoring.metricWriter"
    )
    
    for role in "${roles[@]}"; do
        gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
            --member=serviceAccount:$SA_EMAIL \
            --role=$role \
            --condition=None \
            2>/dev/null || log_warn "Failed to grant $role"
    done
    
    log_info "IAM roles granted!"
    
    # Create service account key
    log_info "Creating service account key..."
    SA_KEY_FILE="olympic-etl-${ENVIRONMENT}-key.json"
    
    if [ -f "$SA_KEY_FILE" ]; then
        log_warn "Service account key already exists: $SA_KEY_FILE"
    else
        gcloud iam service-accounts keys create $SA_KEY_FILE \
            --iam-account=$SA_EMAIL
        log_info "Service account key created: $SA_KEY_FILE"
    fi
    
    # Export credentials
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/$SA_KEY_FILE"
    log_info "GOOGLE_APPLICATION_CREDENTIALS set to: $GOOGLE_APPLICATION_CREDENTIALS"
}

# Setup BigQuery resources
setup_bigquery_resources() {
    log_info "Setting up BigQuery resources..."
    
    DATASET="olympic_analytics_${ENVIRONMENT}"
    
    # Create dataset
    log_info "Creating BigQuery dataset: $DATASET"
    bq mk \
        --dataset \
        --location=us \
        --description="Olympic analytics dataset ($ENVIRONMENT)" \
        --default_table_expiration=7776000 \
        $DATASET 2>/dev/null || log_warn "Dataset might already exist"
    
    # Create medals table
    log_info "Creating medals table..."
    SCHEMA_FILE="src/gcp/bigquery/schemas/olympic_dataset_schema.sql"
    
    if [ -f "$SCHEMA_FILE" ]; then
        bq mk \
            --table \
            --description="Olympic medal records" \
            --time_partitioning_field=processed_at \
            --time_partitioning_type=DAY \
            --clustering_fields=country_code,year \
            $DATASET.medals \
            $SCHEMA_FILE 2>/dev/null || log_warn "Table might already exist"
    fi
    
    log_info "BigQuery resources created!"
}

# Setup Cloud Storage buckets
setup_storage_buckets() {
    log_info "Setting up Cloud Storage buckets..."
    
    BUCKETS=(
        "${GCP_PROJECT_ID}-beam-input"
        "${GCP_PROJECT_ID}-beam-temp"
        "${GCP_PROJECT_ID}-beam-dlq"
        "${GCP_PROJECT_ID}-beam-output"
    )
    
    for bucket in "${BUCKETS[@]}"; do
        if gsutil ls -b gs://$bucket 2>/dev/null; then
            log_warn "Bucket already exists: gs://$bucket"
        else
            log_info "Creating bucket: gs://$bucket"
            gsutil mb -l $REGION gs://$bucket
        fi
    done
    
    # Set lifecycle policies for DLQ
    log_info "Setting lifecycle policies..."
    cat > /tmp/lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 30}
      }
    ]
  }
}
EOF
    
    gsutil lifecycle set /tmp/lifecycle.json gs://${GCP_PROJECT_ID}-beam-dlq 2>/dev/null || \
        log_warn "Failed to set lifecycle policy"
    
    log_info "Cloud Storage buckets configured!"
}

# Build and push Docker image
build_and_push_docker() {
    if ! command -v docker &> /dev/null; then
        log_warn "Docker not available. Skipping Docker build."
        return
    fi
    
    log_info "Building Docker image..."
    
    REGISTRY="us-central1-docker.pkg.dev"
    IMAGE_TAG="${REGISTRY}/${GCP_PROJECT_ID}/olympic-docker/olympic-etl:${ENVIRONMENT}"
    
    # Authenticate Docker
    gcloud auth configure-docker $REGISTRY
    
    # Build image
    docker build \
        -f docker/Dockerfile \
        -t $IMAGE_TAG \
        .
    
    log_info "Docker image built: $IMAGE_TAG"
    
    # Push image
    log_info "Pushing Docker image to registry..."
    docker push $IMAGE_TAG
    
    log_info "Docker image pushed successfully!"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate || . venv/Scripts/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r src/beam/requirements.txt
    
    log_info "Dependencies installed!"
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    source venv/bin/activate || . venv/Scripts/activate
    
    pytest tests/unit/ \
        --cov=src/beam \
        --cov-report=term-missing \
        -v || log_error "Tests failed!"
    
    log_info "All tests passed!"
}

# Deploy pipeline
deploy_pipeline() {
    log_info "Deploying pipeline..."
    
    source venv/bin/activate || . venv/Scripts/activate
    
    DATASET="olympic_analytics_${ENVIRONMENT}"
    
    python -m src.beam.pipelines.olympic_etl_pipeline \
        --project=$GCP_PROJECT_ID \
        --region=$REGION \
        --dataset=$DATASET \
        --table=medals \
        --runner=DataflowRunner \
        --job_name=olympic-etl-${ENVIRONMENT}-$(date +%s)
    
    log_info "Pipeline deployed!"
}

# Print summary
print_summary() {
    log_info "Deployment completed successfully!"
    log_info ""
    log_info "Summary:"
    log_info "  - GCP Project: $GCP_PROJECT_ID"
    log_info "  - Environment: $ENVIRONMENT"
    log_info "  - Region: $REGION"
    log_info "  - Service Account: olympic-etl-${ENVIRONMENT}-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
    log_info "  - BigQuery Dataset: olympic_analytics_${ENVIRONMENT}"
    log_info "  - Storage Buckets: ${GCP_PROJECT_ID}-beam-{input,temp,dlq,output}"
    log_info ""
    log_info "Next steps:"
    log_info "  1. Export credentials: export GOOGLE_APPLICATION_CREDENTIALS=\"$(pwd)/olympic-etl-${ENVIRONMENT}-key.json\""
    log_info "  2. Run tests: pytest tests/"
    log_info "  3. Deploy: ./scripts/deploy.sh $GCP_PROJECT_ID $ENVIRONMENT"
    log_info ""
}

# Main execution
main() {
    check_prerequisites
    validate_gcp_project
    setup_gcp_resources
    setup_bigquery_resources
    setup_storage_buckets
    install_dependencies
    
    read -p "Build and push Docker image? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_and_push_docker
    fi
    
    read -p "Run tests? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    read -p "Deploy pipeline to Dataflow? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        deploy_pipeline
    fi
    
    print_summary
}

# Run main function
main

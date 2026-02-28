# Olympic Data ETL - Setup & Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [GCP Configuration](#gcp-configuration)
4. [Azure Configuration](#azure-configuration)
5. [Docker Setup](#docker-setup)
6. [Running the Pipeline](#running-the-pipeline)
7. [CI/CD Deployment](#cicd-deployment)
8. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (WSL2)
- **Python**: 3.11+
- **Docker**: 24.0+
- **Git**: 2.40+
- **RAM**: 8GB minimum
- **Disk Space**: 50GB for local data staging

### Cloud Accounts
- **Google Cloud Platform (GCP)**
  - Project with billing enabled
  - Service Account with roles: `Dataflow Worker`, `BigQuery Editor`, `Storage Admin`
  
- **Microsoft Azure** (optional)
  - Storage Account created
  - Data Factory service principal
  - Access to Databricks clusters

### API Keys & Credentials
- GCP Service Account JSON key
- Azure Service Principal credentials
- GitHub Personal Access Token (for CI/CD)

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/olympic-data-etl.git
cd olympic-data-etl
```

### 2. Create Python Virtual Environment

#### Using venv (recommended)
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Using conda
```bash
conda create -n olympic-etl python=3.11
conda activate olympic-etl
```

### 3. Install Dependencies

```bash
# Install root dependencies
pip install -r requirements.txt

# Install Beam pipeline dependencies
pip install -r src/beam/requirements.txt

# Install development & testing dependencies
pip install -e ".[dev]"
```

### 4. Configure Environment Variables

Create `.env` file in project root:

```bash
# GCP Configuration
export GCP_PROJECT_ID="your-gcp-project"
export GCP_REGION="us-central1"
export GCP_DATASET="olympic_analytics"
export GCP_TABLE="medals"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Azure Configuration (optional)
export AZURE_STORAGE_ACCOUNT="your-storage-account"
export AZURE_STORAGE_KEY="your-storage-key"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Pipeline Configuration
export ENVIRONMENT="development"
export LOG_LEVEL="INFO"
export BATCH_SIZE="1000"

# API Configuration
export OLYMPICS_API_URL="https://api.olym.dev"
export WIKIDATA_ENDPOINT="https://query.wikidata.org"
export REQUEST_TIMEOUT="30"
```

Load environment variables:
```bash
source .env
```

### 5. Verify Installation

```bash
# Check Python version
python --version

# Verify key packages
python -c "import apache_beam; print(f'Beam: {apache_beam.__version__}')"
python -c "import google.cloud.bigquery; print('BigQuery SDK: OK')"

# Run quick test
pytest tests/unit/test_pipeline.py::test_validate_record -v
```

---

## GCP Configuration

### 1. Create GCP Project & Enable APIs

```bash
# Set project ID
export GCP_PROJECT_ID="olympic-etl-prod"
gcloud config set project $GCP_PROJECT_ID

# Enable required APIs
gcloud services enable \
  dataflow.googleapis.com \
  bigquery.googleapis.com \
  storage-api.googleapis.com \
  cloudlogging.googleapis.com \
  monitoring.googleapis.com \
  artifactregistry.googleapis.com
```

### 2. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create olympic-etl-sa \
  --display-name="Olympic ETL Service Account"

export SA_EMAIL="olympic-etl-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

# Grant necessary roles
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member=serviceAccount:$SA_EMAIL \
  --role=roles/dataflow.worker

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member=serviceAccount:$SA_EMAIL \
  --role=roles/bigquery.dataEditor

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member=serviceAccount:$SA_EMAIL \
  --role=roles/storage.objectAdmin

# Create and download key
gcloud iam service-accounts keys create olympic-etl-key.json \
  --iam-account=$SA_EMAIL

export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/olympic-etl-key.json"
```

### 3. Create BigQuery Dataset & Tables

```bash
# Create dataset
bq mk \
  --dataset \
  --location=us \
  --description="Olympic analytics dataset" \
  olympic_analytics

# Create medals table
bq mk \
  --table \
  --description="Olympic medal records" \
  olympic_analytics.medals \
  src/gcp/bigquery/schemas/olympic_dataset_schema.sql

# Set table clustering & partitioning
bq update \
  --clustering_fields=country_code,year \
  --time_partitioning_field=processed_at \
  --time_partitioning_type=DAY \
  olympic_analytics.medals
```

### 4. Create Cloud Storage Buckets

```bash
# Create buckets for pipeline stages
gsutil mb -l us-central1 gs://${GCP_PROJECT_ID}-beam-input
gsutil mb -l us-central1 gs://${GCP_PROJECT_ID}-beam-temp
gsutil mb -l us-central1 gs://${GCP_PROJECT_ID}-beam-dlq

# Set lifecycle policies (auto-delete after 30 days)
gsutil lifecycle set - gs://${GCP_PROJECT_ID}-beam-dlq << EOF
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
```

---

## Azure Configuration

### 1. Create Resource Group & Storage Account

```bash
# Login to Azure
az login

# Create resource group
az group create \
  --name olympic-etl-rg \
  --location eastus

# Create storage account
az storage account create \
  --name olympicetlstorage \
  --resource-group olympic-etl-rg \
  --location eastus

export AZURE_STORAGE_ACCOUNT="olympicetlstorage"
```

### 2. Create Data Factory

```bash
# Create Data Factory
az datafactory create \
  --resource-group olympic-etl-rg \
  --factory-name olympic-etl-adf \
  --location eastus

# Deploy ADF pipeline
az deployment group create \
  --resource-group olympic-etl-rg \
  --template-file src/azure/deployment/adf_pipeline_template.json \
  --parameters \
    dataFactoryName=olympic-etl-adf \
    dataLakeStorageAccountName=$AZURE_STORAGE_ACCOUNT \
    googleBigQueryProjectId=$GCP_PROJECT_ID
```

### 3. Create Databricks Cluster

```bash
# Create Databricks workspace (if using Databricks)
az databricks workspace create \
  --resource-group olympic-etl-rg \
  --name olympic-etl-dbx \
  --location eastus
```

---

## Docker Setup

### 1. Build Docker Image

```bash
# Build locally
docker build \
  -f docker/Dockerfile \
  -t olympic-etl:local \
  .

# Test the image
docker run --rm olympic-etl:local python -m src.beam.pipelines.olympic_etl_pipeline --help
```

### 2. Push to Container Registry

```bash
# Authenticate to GCP
gcloud auth configure-docker us-central1-docker.pkg.dev

# Create Artifact Registry
gcloud artifacts repositories create olympic-docker \
  --repository-format=docker \
  --location=us-central1

# Tag image
docker tag olympic-etl:local \
  us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/olympic-docker/olympic-etl:latest

# Push to registry
docker push \
  us-central1-docker.pkg.dev/${GCP_PROJECT_ID}/olympic-docker/olympic-etl:latest
```

### 3. Run Locally with Docker Compose

```bash
# Start services (BigQuery Emulator, etc.)
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## Running the Pipeline

### 1. Local Testing (DirectRunner)

```bash
# Test with sample data
python -m src.beam.pipelines.olympic_etl_pipeline \
  --project=$GCP_PROJECT_ID \
  --dataset=olympic_analytics \
  --table=medals \
  --runner=DirectRunner \
  --input-file=data/sample/olympics_sample.json

# With verbose logging
python -m src.beam.pipelines.olympic_etl_pipeline \
  --project=$GCP_PROJECT_ID \
  --dataset=olympic_analytics \
  --table=medals \
  --runner=DirectRunner \
  --input-file=data/sample/olympics_sample.json \
  --log_level=DEBUG
```

### 2. Run on Google Cloud Dataflow

```bash
# Submit to Dataflow
python -m src.beam.pipelines.olympic_etl_pipeline \
  --project=$GCP_PROJECT_ID \
  --region=us-central1 \
  --dataset=olympic_analytics \
  --table=medals \
  --runner=DataflowRunner \
  --enable_streaming_engine

# Monitor in console
gcloud dataflow jobs list
gcloud dataflow jobs describe JOB_ID --region=us-central1
```

### 3. Schedule with Cloud Scheduler

```bash
# Create Cloud Scheduler job (daily at 6 AM UTC)
gcloud scheduler jobs create pubsub olympic-etl-daily \
  --location=us-central1 \
  --schedule="0 6 * * *" \
  --topic=olympic-etl-trigger \
  --message-body='{"environment":"production"}'

# Create Pub/Sub subscription to trigger Dataflow
gcloud pubsub subscriptions create olympic-etl-sub \
  --topic=olympic-etl-trigger \
  --push-endpoint=https://dataflow.googleapis.com/v1b3/projects/${GCP_PROJECT_ID}/jobs
```

---

## CI/CD Deployment

### 1. GitHub Secrets Setup

Add the following secrets to your GitHub repository:

```
GCP_PROJECT_ID              # GCP project ID
GCP_SA_KEY                  # Service account JSON (base64 encoded)
GCP_PROD_PROJECT_ID         # Production GCP project
GCP_PROD_SA_KEY             # Production service account key
SLACK_WEBHOOK               # Slack webhook for notifications
```

### 2. Deploy to Staging

```bash
# Push to develop branch triggers staging deployment
git push origin develop

# View workflow status
gh run list --workflow=deploy.yml

# View logs
gh run view RUN_ID --log
```

### 3. Deploy to Production

```bash
# Create release branch and push to main
git checkout -b release/v1.0.0
git push origin release/v1.0.0

# Create Pull Request → Merge to main
# Triggers production deployment pipeline
```

### 4. Manual Deployment

```bash
# Trigger workflow manually
gh workflow run deploy.yml \
  -f deploy_to_prod=true

# Wait for completion
gh run view RUN_ID --exit-status
```

---

## Monitoring & Troubleshooting

### 1. View Pipeline Logs

```bash
# Local logs
tail -f logs/pipeline.log

# Cloud Logging
gcloud logging read "resource.type=cloud_dataflow_step" \
  --limit=50 \
  --format=json

# Structured logs
gcloud logging read \
  'jsonPayload.pipeline="olympic_etl"' \
  --limit=100 \
  --format=table
```

### 2. Monitor BigQuery

```bash
# Check recent queries
bq ls -j

# View table statistics
bq show --schema oauth_analytics.medals

# Check data:
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM olympic_analytics.medals'
```

### 3. View Dataflow Metrics

```bash
# Get pipeline metrics
gcloud monitoring metrics-descriptors list \
  --filter="metric.type:dataflow*"

# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json
```

### 4. Common Issues & Solutions

**Issue: Authentication Failed**
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Verify credentials
gcloud auth list
```

**Issue: Pipeline Timeout**
```bash
# Increase worker timeout
python -m src.beam.pipelines.olympic_etl_pipeline \
  --project=$GCP_PROJECT_ID \
  --runner=DataflowRunner \
  --job_timeout=1800  # 30 minutes
```

**Issue: Insufficient Quota**
```bash
# Check quota usage
gcloud compute project-info describe \
  --project=$GCP_PROJECT_ID

# Request quota increase via Cloud Console
# IAM & Admin → Quotas → Select service → Edit quota
```

---

## Performance Tuning

### 1. Beam Pipeline Optimization

```bash
# Enable multiple workers
python -m src.beam.pipelines.olympic_etl_pipeline \
  --project=$GCP_PROJECT_ID \
  --runner=DataflowRunner \
  --num_workers=10 \
  --max_num_workers=20 \
  --machine_type=n1-standard-8 \
  --disk_size_gb=100

# Enable caching for repeated transforms
--enable_cache_service
```

### 2. BigQuery Optimization

```sql
-- Verify clustering is effective
SELECT
  total_bytes_processed,
  total_bytes_billed,
  total_slot_ms
FROM
  olympic_analytics.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE query LIKE '%olympic%'
ORDER BY creation_time DESC
LIMIT 5;
```

---

## Next Steps

1. Review [Architecture Documentation](ARCHITECTURE.md)
2. Check [API Integration Guide](API_INTEGRATION.md)
3. Explore [BigQuery Analytics Queries](../src/gcp/bigquery/queries/)
4. Set up [Monitoring & Alerting](../monitoring/)

---

## Support

For issues or questions:
- 📧 Email: olympic-etl@your-org.com
- 🐛 GitHub Issues: [olympic-data-etl/issues](https://github.com/your-org/olympic-data-etl/issues)
- 📚 Documentation: [docs/](.)

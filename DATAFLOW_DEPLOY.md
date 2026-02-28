# Deploy no Google Cloud Dataflow

## Pré-requisitos
- Billing Account configurada (com cartão de crédito)
- APIs habilitadas: Dataflow, Compute Engine, Cloud Storage
- Permissões: Editor role no projeto

## Step 1: Habilitar APIs

```powershell
gcloud services enable dataflow.googleapis.com compute.googleapis.com

# Criar bucket para staging
gsutil mb gs://my-olympic-etl-dataflow-staging
```

## Step 2: Deploy Pipeline

```powershell
python src/beam/pipelines/olympic_etl_pipeline.py \
  --runner=DataflowRunner \
  --project=my-olympic-etl \
  --region=us-central1 \
  --staging_location=gs://my-olympic-etl-dataflow-staging/staging \
  --temp_location=gs://my-olympic-etl-dataflow-staging/temp
```

## Step 3: Monitorar Job

```powershell
# Listar jobs
gcloud dataflow jobs list --region=us-central1

# Verificar status
gcloud dataflow jobs describe JOB_ID --region=us-central1

# Ver logs
gcloud dataflow jobs log JOB_ID --region=us-central1
```

## Custo Estimado
- Workers: $0.07/hr × N workers
- Storage: $0.02/GB/month
- **Exemplo**: 1 worker × 1 hour = ~$0.07

## Cancelar Job (se necessário)
```powershell
gcloud dataflow jobs cancel JOB_ID --region=us-central1
```

**Nota:** Dataflow roda na nuvem e pode levar 5-10 minutos para processar dados.

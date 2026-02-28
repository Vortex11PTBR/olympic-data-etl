#!/usr/bin/env python3
"""
Load Olympic Data to BigQuery
Carrega dados validados para o BigQuery do GCP via Cloud Storage
"""

import json
import logging
from pathlib import Path
from google.cloud import bigquery, storage
from google.api_core import exceptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BigQueryLoader:
    """Carrega dados para BigQuery via Cloud Storage"""
    
    def __init__(self, project_id: str, dataset_id: str = "olympics_dataset", bucket_name: str = None):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bucket_name = bucket_name or f"{project_id}-olympics-data"
        self.bq_client = bigquery.Client(project=project_id)
        self.storage_client = storage.Client(project=project_id)
        
    def create_dataset(self) -> None:
        """Cria dataset se não existir"""
        dataset_id_full = f"{self.project_id}.{self.dataset_id}"
        dataset = bigquery.Dataset(dataset_id_full)
        dataset.location = "US"
        
        try:
            dataset = self.bq_client.create_dataset(dataset, timeout=30)
            logger.info(f"✅ Dataset criado: {dataset_id_full}")
        except exceptions.Conflict:
            logger.info(f"✅ Dataset já existe: {dataset_id_full}")
    
    def create_table(self) -> None:
        """Cria tabela athletes"""
        table_id = f"{self.project_id}.{self.dataset_id}.athletes"
        
        schema = [
            bigquery.SchemaField("athlete_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("country", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("sport", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("medal", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("medal_rank", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("year", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("_processed_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("_pipeline_version", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("_environment", "STRING", mode="NULLABLE"),
        ]
        
        table = bigquery.Table(table_id, schema=schema)
        
        try:
            table = self.bq_client.create_table(table)
            logger.info(f"✅ Tabela criada: {table_id}")
        except exceptions.Conflict:
            logger.info(f"✅ Tabela já existe: {table_id}")
    
    def create_or_get_bucket(self) -> str:
        """Cria bucket de Cloud Storage se não existir"""
        bucket = None
        try:
            bucket = self.storage_client.get_bucket(self.bucket_name)
            logger.info(f"✅ Bucket já existe: {self.bucket_name}")
        except exceptions.NotFound:
            bucket = self.storage_client.create_bucket(
                self.bucket_name, 
                location="US"
            )
            logger.info(f"✅ Bucket criado: {self.bucket_name}")
        
        return self.bucket_name
    
    def upload_to_gcs(self, local_file: str, gcs_blob_name: str) -> str:
        """Upload arquivo local para Cloud Storage"""
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(gcs_blob_name)
        
        blob.upload_from_filename(local_file)
        logger.info(f"✅ Arquivo enviado: gs://{self.bucket_name}/{gcs_blob_name}")
        
        return f"gs://{self.bucket_name}/{gcs_blob_name}"
    
    def load_from_gcs_json(self, gcs_uri: str) -> int:
        """Carrega dados do Cloud Storage (NDJSON) para BigQuery"""
        table_id = f"{self.project_id}.{self.dataset_id}.athletes"
        
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=False,
            write_disposition="WRITE_APPEND",
            skip_leading_rows=0,
        )
        
        load_job = self.bq_client.load_table_from_uri(
            gcs_uri,
            table_id,
            job_config=job_config,
        )
        
        load_job.result()
        logger.info(f"✅ {load_job.output_rows} registros carregados de {gcs_uri}")
        
        return load_job.output_rows
    
    def prepare_ndjson(self, json_file: str) -> str:
        """Converte JSON array para NDJSON"""
        with open(json_file) as f:
            records = json.load(f)
        
        ndjson_file = json_file.replace(".json", ".ndjson")
        with open(ndjson_file, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
        
        logger.info(f"✅ NDJSON preparado: {ndjson_file}")
        return ndjson_file
    
    def query_athletes(self, limit: int = 10) -> list:
        """Consulta athletes da tabela"""
        query = f"""
        SELECT * FROM `{self.project_id}.{self.dataset_id}.athletes`
        ORDER BY year DESC, name
        LIMIT {limit}
        """
        
        query_job = self.bq_client.query(query)
        results = query_job.result()
        
        return [dict(row) for row in results]
    
    def query_medals_by_country(self) -> list:
        """Conta medalhas por país"""
        query = f"""
        SELECT 
            country,
            COUNT(*) as medal_count,
            COUNTIF(medal = 'Gold') as gold,
            COUNTIF(medal = 'Silver') as silver,
            COUNTIF(medal = 'Bronze') as bronze
        FROM `{self.project_id}.{self.dataset_id}.athletes`
        WHERE medal IS NOT NULL
        GROUP BY country
        ORDER BY medal_count DESC
        """
        
        query_job = self.bq_client.query(query)
        results = query_job.result()
        
        return [dict(row) for row in results]
    
    def get_table_stats(self) -> dict:
        """Obtém estatísticas da tabela"""
        table_id = f"{self.project_id}.{self.dataset_id}.athletes"
        table = self.bq_client.get_table(table_id)
        
        return {
            "total_rows": table.num_rows,
            "total_bytes": table.num_bytes,
            "created": table.created.isoformat() if table.created else None,
            "modified": table.modified.isoformat() if table.modified else None,
        }


def main():
    """Main entry point"""
    import sys
    
    project_id = sys.argv[1] if len(sys.argv) > 1 else "my-olympic-etl"
    
    logger.info("=" * 60)
    logger.info("BigQuery Data Loader (via Cloud Storage)")
    logger.info(f"Project: {project_id}")
    logger.info("=" * 60)
    
    try:
        loader = BigQueryLoader(project_id)
        
        # 1. Criar bucket
        logger.info("\n☁️ Criando bucket...")
        loader.create_or_get_bucket()
        
        # 2. Criar dataset
        logger.info("\n📁 Criando dataset...")
        loader.create_dataset()
        
        # 3. Criar tabela
        logger.info("\n📊 Criando tabela...")
        loader.create_table()
        
        # 4. Preparar dados
        logger.info("\n📝 Preparando dados...")
        valid_records_file = Path("output/valid_records.json")
        
        if not valid_records_file.exists():
            logger.warning(f"Arquivo não encontrado: {valid_records_file}")
            logger.info("Execute primeiro: python src/beam/pipelines/olympic_etl_simple.py my-olympic-etl")
            return 1
        
        # Converter JSON para NDJSON
        ndjson_file = loader.prepare_ndjson(str(valid_records_file))
        
        # 5. Upload para GCS
        logger.info("\n📤 Enviando para Cloud Storage...")
        gcs_uri = loader.upload_to_gcs(ndjson_file, "data/athletes.ndjson")
        
        # 6. Load para BigQuery
        logger.info("\n📥 Carregando para BigQuery...")
        rows_loaded = loader.load_from_gcs_json(gcs_uri)
        
        # 7. Estatísticas
        logger.info("\n📈 Estatísticas da tabela:")
        stats = loader.get_table_stats()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        # 8. Query de exemplo
        logger.info("\n🏆 Top 5 atletas:")
        athletes = loader.query_athletes(limit=5)
        for athlete in athletes:
            logger.info(f"  • {athlete['name']} ({athlete['country']}) - {athlete['medal']} - {athlete['year']}")
        
        # 9. Medalhas por país
        logger.info("\n🥇 Medalhas por país:")
        medals = loader.query_medals_by_country()
        for country_medals in medals:
            logger.info(
                f"  {country_medals['country']}: "
                f"{int(country_medals['gold'])}🥇 "
                f"{int(country_medals['silver'])}🥈 "
                f"{int(country_medals['bronze'])}🥉"
            )
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ BigQuery carregado com sucesso!")
        logger.info("=" * 60)
        
        logger.info("\n💡 Próximos passos:")
        logger.info(f"   1. Acesse BigQuery: https://console.cloud.google.com/bigquery?project={project_id}")
        logger.info(f"   2. Dataset: olympics_dataset")
        logger.info(f"   3. Tabela: athletes")
        logger.info(f"\n   Cloud Storage:")
        logger.info(f"   https://console.cloud.google.com/storage?project={project_id}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())


if __name__ == "__main__":
    import sys
    sys.exit(main())

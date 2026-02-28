"""
Olympic Data ETL Pipeline using Apache Beam.

Multi-source API ingestion with data validation, transformation, and BigQuery loading.
Supports both local execution and Google Cloud Dataflow deployment.
"""

import argparse
import logging
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Tuple
from collections import defaultdict

import apache_beam as beam
from apache_beam.options.pipeline_options import (
    PipelineOptions,
    GoogleCloudOptions,
    WorkerOptions,
    StandardOptions,
)
from apache_beam.io import ReadFromText, WriteToText
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.transforms import (
    Create,
    FlatMap,
    Map,
    ParDo,
    GroupByKey,
    Distinct,
    Filter,
    CombineGlobally,
)
import requests


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class APIClient:
    """Client for fetching data from multiple Olympic data sources."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def fetch_olympics_data(self, endpoint: str = "https://api.olym.dev/") -> List[Dict]:
        """Fetch data from Olympics API."""
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching Olympics API: {e}")
            return []

    def fetch_wikidata(self, sport: str = None) -> List[Dict]:
        """Fetch enrichment data from Wikidata."""
        try:
            query = f"""
            SELECT ?athlete ?name ?countryLabel ?sportLabel
            WHERE {{
              ?athlete wdt:P31 wd:Q5; rdfs:label ?name.
              ?athlete wdt:P27 ?country.
              FILTER(LANG(?name) = "en")
            }}
            LIMIT 1000
            """
            url = "https://query.wikidata.org/sparql"
            response = self.session.get(
                url,
                params={"query": query, "format": "json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            results = response.json().get("results", {}).get("bindings", [])
            return [
                {
                    "athlete": r.get("athlete", {}).get("value", ""),
                    "name": r.get("name", {}).get("value", ""),
                    "country": r.get("countryLabel", {}).get("value", ""),
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error fetching Wikidata: {e}")
            return []


# ============================================================================
# Transform Functions
# ============================================================================

class ValidateRecord(beam.DoFn):
    """Validate Olympic records against schema."""

    REQUIRED_FIELDS = {"athlete_id", "event_id", "country_code", "medal_type", "year"}
    MEDAL_TYPES = {"GOLD", "SILVER", "BRONZE"}

    def process(self, element: Dict) -> beam.pvalue.PDone:
        try:
            # Check required fields
            if not all(field in element for field in self.REQUIRED_FIELDS):
                yield beam.pvalue.TaggedOutput(
                    "invalid",
                    {
                        "record": element,
                        "reason": "missing_required_fields",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            # Validate medal type
            if element.get("medal_type") not in self.MEDAL_TYPES:
                yield beam.pvalue.TaggedOutput(
                    "invalid",
                    {
                        "record": element,
                        "reason": "invalid_medal_type",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            # Validate year range
            year = element.get("year")
            if not (1896 <= int(year) <= 2024):
                yield beam.pvalue.TaggedOutput(
                    "invalid",
                    {
                        "record": element,
                        "reason": "invalid_year",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )
                return

            yield beam.pvalue.TaggedOutput("valid", element)

        except Exception as e:
            logger.error(f"Validation error: {e}")
            yield beam.pvalue.TaggedOutput(
                "invalid",
                {
                    "record": element,
                    "reason": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )


class EnrichWithCountryData(beam.DoFn):
    """Enrich records with country metadata."""

    COUNTRY_DATA = {
        "USA": {"name": "United States", "region": "Americas"},
        "CHN": {"name": "China", "region": "Asia"},
        "GBR": {"name": "United Kingdom", "region": "Europe"},
        "RUS": {"name": "Russia", "region": "Europe"},
        "JPN": {"name": "Japan", "region": "Asia"},
        "AUS": {"name": "Australia", "region": "Oceania"},
        "CAN": {"name": "Canada", "region": "Americas"},
        "FRA": {"name": "France", "region": "Europe"},
        "GER": {"name": "Germany", "region": "Europe"},
        "IND": {"name": "India", "region": "Asia"},
    }

    def process(self, element: Dict) -> beam.pvalue.PDone:
        country_code = element.get("country_code")
        if country_code in self.COUNTRY_DATA:
            element.update(self.COUNTRY_DATA[country_code])
        else:
            element["name"] = f"Country_{country_code}"
            element["region"] = "Unknown"

        element["enriched_at"] = datetime.utcnow().isoformat()
        yield element


class DeduplicateRecords(beam.DoFn):
    """Remove duplicate records based on unique key."""

    def process(self, element: Tuple[str, List[Dict]]) -> beam.pvalue.PDone:
        unique_key, records = element
        if records:
            # Keep the most recent record
            deduplicated = sorted(
                records, 
                key=lambda x: x.get("processed_at", ""), 
                reverse=True
            )[0]
            yield deduplicated


class GenerateMetrics(beam.DoFn):
    """Generate metrics for monitoring."""

    def process(self, element: Tuple[str, int]) -> beam.pvalue.PDone:
        key, count = element
        metric = {
            "metric_name": key,
            "value": count,
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline": "olympic_etl"
        }
        logger.info(f"Metric: {metric}")
        yield metric


# ============================================================================
# Pipeline Functions
# ============================================================================

def generate_record_id(element: Dict) -> str:
    """Generate unique record ID for deduplication."""
    key_fields = f"{element.get('athlete_id')}_{element.get('event_id')}_{element.get('year')}"
    return hashlib.md5(key_fields.encode()).hexdigest()


def add_processing_metadata(element: Dict) -> Dict:
    """Add processing metadata to record."""
    element["record_id"] = generate_record_id(element)
    element["processed_at"] = datetime.utcnow().isoformat()
    return element


def emit_key_value(element: Dict) -> Tuple[str, Dict]:
    """Emit record as key-value pair for grouping."""
    key = element.get("record_id")
    return (key, element)


def flatten_enriched_data(element: Dict) -> List[Dict]:
    """Flatten nested enriched data."""
    medals = element.get("medals", [])
    results = []
    for medal in medals:
        record = element.copy()
        record.update(medal)
        results.append(record)
    return results


# ============================================================================
# BigQuery Schema
# ============================================================================

BIGQUERY_SCHEMA = """{
    "fields": [
        {"name": "record_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "athlete_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "athlete_name", "type": "STRING", "mode": "NULLABLE"},
        {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "event_name", "type": "STRING", "mode": "NULLABLE"},
        {"name": "country_code", "type": "STRING", "mode": "REQUIRED"},
        {"name": "country_name", "type": "STRING", "mode": "NULLABLE"},
        {"name": "region", "type": "STRING", "mode": "NULLABLE"},
        {"name": "medal_type", "type": "STRING", "mode": "REQUIRED"},
        {"name": "year", "type": "INTEGER", "mode": "REQUIRED"},
        {"name": "season", "type": "STRING", "mode": "NULLABLE"},
        {"name": "city", "type": "STRING", "mode": "NULLABLE"},
        {"name": "processed_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
        {"name": "enriched_at", "type": "TIMESTAMP", "mode": "NULLABLE"}
    ]
}"""


# ============================================================================
# Main Pipeline
# ============================================================================

def run_pipeline(
    project: str,
    region: str,
    dataset: str,
    table: str,
    runner: str = "DirectRunner",
    input_file: str = None,
    use_streaming: bool = False,
):
    """
    Run the Olympic ETL pipeline.

    Args:
        project: GCP project ID
        region: GCP region
        dataset: BigQuery dataset
        table: BigQuery table
        runner: Beam runner (DirectRunner, DataflowRunner)
        input_file: Optional input file for local testing
        use_streaming: Enable streaming mode
    """

    pipeline_options = PipelineOptions()
    pipeline_options.view_as(StandardOptions).runner = runner

    if runner == "DataflowRunner":
        options = pipeline_options.view_as(GoogleCloudOptions)
        options.project = project
        options.region = region
        options.temp_location = f"gs://{project}-beam-temp"
        
        worker_options = pipeline_options.view_as(WorkerOptions)
        worker_options.num_workers = 2
        worker_options.machine_type = "n1-standard-4"

    with beam.Pipeline(options=pipeline_options) as pipeline:
        # ====== Data Ingestion ======
        if input_file:
            # Load from local file (for testing)
            raw_data = (
                pipeline
                | "ReadJsonFile" >> beam.io.ReadFromText(input_file)
                | "ParseJson" >> beam.Map(json.loads)
            )
        else:
            # Fetch from APIs
            api_client = APIClient()
            olympics_data = api_client.fetch_olympics_data()
            raw_data = pipeline | "CreateOlympicsData" >> beam.Create(olympics_data)

        # ====== Add Metadata ======
        with_metadata = (
            raw_data
            | "AddMetadata" >> beam.Map(add_processing_metadata)
        )

        # ====== Data Validation ======
        validated = (
            with_metadata
            | "ValidateRecords" >> beam.ParDo(ValidateRecord()).with_outputs(
                "invalid", main="valid"
            )
        )

        valid_records = validated["valid"]
        invalid_records = validated["invalid"]

        # ====== Transform & Enrich ======
        enriched = (
            valid_records
            | "EnrichWithCountry" >> beam.ParDo(EnrichWithCountryData())
        )

        # ====== Deduplication ======
        deduplicated = (
            enriched
            | "CreateKeyValuePair" >> beam.Map(emit_key_value)
            | "GroupByKey" >> beam.GroupByKey()
            | "Deduplicate" >> beam.ParDo(DeduplicateRecords())
        )

        # ====== Output to BigQuery ======
        bigquery_output = (
            deduplicated
            | "WriteToBigQuery"
            >> WriteToBigQuery(
                table=f"{project}:{dataset}.{table}",
                schema=BIGQUERY_SCHEMA,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                custom_gcs_temp_location=f"gs://{project}-beam-temp/bq"
                if runner == "DataflowRunner"
                else None,
            )
        )

        # ====== Dead Letter Queue (DLQ) ======
        dlq_output = (
            invalid_records
            | "WriteDLQ"
            >> beam.io.WriteToText(
                "/tmp/olympic_dlq" if runner == "DirectRunner" 
                else f"gs://{project}-beam-dlq/records"
            )
        )

        # ====== Metrics ======
        metrics = (
            deduplicated
            | "CountRecords" >> beam.combiners.Count.Globally()
            | "CreateMetrics" >> beam.Map(
                lambda count: ("records_processed", count)
            )
            | "EmitMetrics" >> beam.ParDo(GenerateMetrics())
        )

        logger.info("Pipeline constructed successfully")


def main():
    parser = argparse.ArgumentParser(description="Olympic Data ETL Pipeline")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--region", default="us-central1", help="GCP Region")
    parser.add_argument("--dataset", default="olympic_analytics", help="BigQuery Dataset")
    parser.add_argument("--table", default="medals", help="BigQuery Table")
    parser.add_argument(
        "--runner",
        default="DirectRunner",
        choices=["DirectRunner", "DataflowRunner"],
        help="Beam Runner",
    )
    parser.add_argument("--input-file", help="Local input file for testing")
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Enable streaming mode",
    )

    args = parser.parse_args()

    run_pipeline(
        project=args.project,
        region=args.region,
        dataset=args.dataset,
        table=args.table,
        runner=args.runner,
        input_file=args.input_file,
        use_streaming=args.streaming,
    )


if __name__ == "__main__":
    main()

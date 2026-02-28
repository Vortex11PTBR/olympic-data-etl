# BigQuery Import Instructions

## Option 1: Import from CSV (Recommended)

1. Open BigQuery Console:
   https://console.cloud.google.com/bigquery

2. Create Dataset (if needed):
   - Click 'Create Dataset'
   - Name: `olympics_dataset`
   - Location: `US`

3. Upload CSV File:
   - File: `output\athletes.csv`
   - Destination Dataset: `olympics_dataset`
   - Destination Table: `athletes`
   - Table Type: `Native table`
           - Auto-detect schema: [X] Checked
   - Click 'Create table'

## Option 2: Import from NDJSON

   - Use same steps above with `output\athletes.ndjson`

## Command Line Option

```bash
# Load CSV
bq load --autodetect --source_format=CSV \
  olympics_dataset.athletes \
  output\athletes.csv

# Or load NDJSON
bq load --autodetect --source_format=NEWLINE_DELIMITED_JSON \
  olympics_dataset.athletes \
  output\athletes.ndjson
```

## Verify Data

```bash
# Check row count
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as total FROM olympics_dataset.athletes'

# View first 10 rows
bq query --use_legacy_sql=false \
  'SELECT * FROM olympics_dataset.athletes LIMIT 10'
```

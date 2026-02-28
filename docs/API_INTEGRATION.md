# API Integration Guide - Olympic Data ETL

## Overview

This guide covers integrating multiple data sources into the Olympic ETL pipeline:
- **Olympics API** - Primary data source for athletes, events, and medals
- **Wikidata SPARQL** - Enrichment data (country info, athlete metadata)
- **OpenOlympics API** - Venues, sports categories, and historical data

---

## 1. Olympics API Integration

### Endpoint Documentation

**Base URL**: `https://api.olym.dev`

#### Get Athletes
```bash
GET /athletes
GET /athletes?year=2020
GET /athletes?country=USA
```

**Response Schema**:
```json
{
  "data": [
    {
      "athlete_id": "ath_001",
      "athlete_name": "John Doe",
      "country_code": "USA",
      "birth_year": 1990,
      "height_cm": 180,
      "weight_kg": 75
    }
  ]
}
```

#### Get Events
```bash
GET /events
GET /events?year=2020&sport=Swimming
```

**Response Schema**:
```json
{
  "data": [
    {
      "event_id": "evt_001",
      "event_name": "100m Sprint",
      "sport": "Athletics",
      "gender": "M",
      "year": 2020,
      "city": "Tokyo"
    }
  ]
}
```

#### Get Medals
```bash
GET /medals
GET /medals?country=USA&year=2020
```

**Response Schema**:
```json
{
  "data": [
    {
      "athlete_id": "ath_001",
      "event_id": "evt_001",
      "medal_type": "GOLD",
      "year": 2020,
      "country_code": "USA"
    }
  ]
}
```

### Python Integration

#### Using the APIClient

```python
from src.beam.pipelines.api_clients import OlympicsAPIClient

# Initialize client
client = OlympicsAPIClient(base_url="https://api.olym.dev")

# Fetch athletes for specific year
athletes = client.get_athletes(year=2020, country="USA")

# Fetch events
events = client.get_events(sport="Swimming")

# Fetch medals
medals = client.get_medals(country="CHN")

# Process results
for medal in medals:
    print(f"{medal['athlete_name']} won {medal['medal_type']} in {medal['event_name']}")
```

#### Error Handling

```python
import logging
from src.beam.pipelines.api_clients import OlympicsAPIClient

logger = logging.getLogger(__name__)

try:
    client = OlympicsAPIClient(timeout=30)
    data = client.get_athletes(year=2020)
except requests.Timeout:
    logger.error("API request timed out")
except requests.HTTPError as e:
    logger.error(f"HTTP error: {e.response.status_code}")
finally:
    client.close()
```

---

## 2. Wikidata Integration

### SPARQL Query Examples

#### Get Athlete Information

```sparql
SELECT ?athlete ?name ?countryLabel ?birthDate ?occupationLabel
WHERE {
  ?athlete rdfs:label "Alexander Zhukov"@en.
  ?athlete wdt:P31 wd:Q5.
  ?athlete rdfs:label ?name.
  OPTIONAL { ?athlete wdt:P27 ?country. }
  OPTIONAL { ?athlete wdt:P569 ?birthDate. }
  OPTIONAL { ?athlete wdt:P106 ?occupation. }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en".
  }
}
LIMIT 10
```

#### Get Country Information

```sparql
SELECT ?country ?countryLabel ?population ?area ?continent
WHERE {
  ?country wdt:P297 "USA".
  OPTIONAL { ?country wdt:P1082 ?population. }
  OPTIONAL { ?country wdt:P2046 ?area. }
  OPTIONAL { ?country wdt:P30 ?continent. }
  SERVICE wikibase:label { 
    bd:serviceParam wikibase:language "en".
  }
}
```

### Python Integration

```python
from src.beam.pipelines.api_clients import WikidataClient

# Initialize client
wikidata = WikidataClient()

# Query Wikidata with SPARQL
query = """
SELECT ?athlete ?name ?countryLabel
WHERE {
  ?athlete wdt:P31 wd:Q5.
  ?athlete rdfs:label ?name.
  ?athlete wdt:P27 ?country.
  FILTER (LANG(?name) = "en")
}
LIMIT 100
"""

results = wikidata.query(query)

# Get specific athlete info
athlete_info = wikidata.get_athlete_info("Michael Phelps")

# Get country info
country_info = wikidata.get_country_info("CHN")

# Process enrichment data
for athlete_record in athlete_info:
    print(f"Athlete: {athlete_record['name'].get('value')}")
    print(f"Country: {athlete_record.get('countryLabel', {}).get('value')}")
```

---

## 3. OpenOlympics API Integration

### Endpoints

**Base URL**: `https://api.openolympics.org`

```bash
# Get venues
GET /venues
GET /venues?year=2020

# Get sports
GET /sports

# Get countries
GET /countries

# Get historical data
GET /history?start_year=1896&end_year=2024
```

### Python Integration

```python
from src.beam.pipelines.api_clients import OpenOlympicsClient

# Initialize client
client = OpenOlympicsClient()

# Fetch venues
venues = client.get_venues(year=2020)

# Fetch sports
sports = client.get_sports()

# Fetch participating countries
countries = client.get_countries()

for venue in venues:
    print(f"Venue: {venue['city']} - {venue['country']}")
```

---

## 4. Data Aggregation Pipeline

### Multi-Source Integration

```python
from src.beam.pipelines.api_clients import APIAggregator

# Initialize aggregator
aggregator = APIAggregator()

# Fetch data from all sources
data = aggregator.fetch_olympics_data(year=2020)

print(f"Athletes: {len(data['athletes'])}")
print(f"Events: {len(data['events'])}")
print(f"Medals: {len(data['medals'])}")
print(f"Venues: {len(data['venues'])}")

# Enrich with Wikidata
enriched_athletes = aggregator.enrich_athletes_with_wikidata(data['athletes'])

# Close connections
aggregator.close()
```

---

## 5. Rate Limiting & Best Practices

### Rate Limiting Strategy

```python
import time
from functools import wraps

def rate_limit(calls_per_second=5):
    """Decorator to rate limit API calls"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=5)
def fetch_data(endpoint):
    # Make API call
    pass
```

### Batch Processing

```python
from src.beam.pipelines.api_clients import APIAggregator

aggregator = APIAggregator()

years = [2000, 2004, 2008, 2012, 2016, 2020, 2024]

for year in years:
    print(f"Fetching data for {year}...")
    data = aggregator.fetch_olympics_data(year=year)
    
    # Process and load to BigQuery
    # ...
    
    # Respect rate limits
    time.sleep(2)

aggregator.close()
```

---

## 6. Error Handling & Retry Logic

### Robust Error Handling

```python
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def create_session_with_retries():
    """Create requests session with automatic retries"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Usage
session = create_session_with_retries()
response = session.get("https://api.olym.dev/athletes")
```

---

## 7. Testing API Integration

### Unit Tests

```python
import pytest
from unittest.mock import patch, MagicMock
from src.beam.pipelines.api_clients import OlympicsAPIClient

@patch('requests.Session.get')
def test_get_athletes(mock_get):
    # Mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "athlete_id": "ath_001",
                "athlete_name": "Test Athlete",
                "country_code": "USA"
            }
        ]
    }
    mock_get.return_value = mock_response
    
    # Test API client
    client = OlympicsAPIClient()
    athletes = client.get_athletes(year=2020)
    
    assert len(athletes) == 1
    assert athletes[0]["athlete_name"] == "Test Athlete"
```

### Integration Tests

```python
import pytest
from src.beam.pipelines.api_clients import APIAggregator

@pytest.mark.integration
def test_api_aggregator():
    """Test real API calls (requires network)"""
    aggregator = APIAggregator()
    
    data = aggregator.fetch_olympics_data(year=2020)
    
    assert "athletes" in data
    assert "medals" in data
    assert len(data["athletes"]) > 0
    
    aggregator.close()
```

---

## 8. Monitoring & Logging

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

# Log API calls
logger.info("api_call_started", 
    endpoint="/athletes",
    params={"year": 2020}
)

# Log results
logger.info("api_call_completed",
    endpoint="/athletes",
    record_count=150,
    duration_ms=245
)

# Log errors
logger.error("api_call_failed",
    endpoint="/athletes",
    error="timeout",
    retry_count=3
)
```

### Performance Monitoring

```python
import time
from contextlib import contextmanager

@contextmanager
def measure_api_performance(endpoint):
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info("api_performance",
            endpoint=endpoint,
            duration_seconds=duration,
            threshold_exceeded=(duration > 5.0)
        )

# Usage
with measure_api_performance("/athletes"):
    athletes = client.get_athletes()
```

---

## Support & References

- **Olympics API**: https://api.olym.dev/docs
- **Wikidata SPARQL**: https://query.wikidata.org
- **OpenOlympics**: https://api.openolympics.org
- **Requests Library**: https://docs.python-requests.org/

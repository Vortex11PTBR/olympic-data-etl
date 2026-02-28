"""
Pytest configuration and fixtures for Olympic ETL tests.
"""

import os
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def gcp_project_id():
    """Fixture for GCP project ID."""
    return "test-project-id"


@pytest.fixture
def bigquery_dataset():
    """Fixture for BigQuery dataset name."""
    return "olympic_analytics_test"


@pytest.fixture
def mock_bigquery_client():
    """Fixture for mocked BigQuery client."""
    return MagicMock()


@pytest.fixture
def mock_gcs_client():
    """Fixture for mocked GCS client."""
    return MagicMock()


@pytest.fixture
def sample_athlete_record():
    """Fixture for sample athlete record."""
    return {
        "record_id": "rec_001",
        "athlete_id": "ath_001",
        "athlete_name": "John Doe",
        "event_id": "evt_001",
        "country_code": "USA",
        "medal_type": "GOLD",
        "year": 2020,
        "processed_at": "2026-02-28T12:00:00Z",
    }


@pytest.fixture
def sample_invalid_record():
    """Fixture for sample invalid record."""
    return {
        "record_id": "rec_invalid_001",
        "athlete_id": "ath_inv_001",
        # Missing athlete_name
        "event_id": "evt_001",
        "country_code": "USA",
        "medal_type": "INVALID",  # Invalid medal type
        "year": 2050,  # Invalid year
    }


@pytest.fixture
def mock_api_client():
    """Fixture for mocked API client."""
    client = MagicMock()
    client.get_athletes.return_value = [
        {
            "athlete_id": "ath_001",
            "athlete_name": "Test Athlete",
            "country_code": "USA",
        }
    ]
    client.get_events.return_value = [
        {
            "event_id": "evt_001",
            "event_name": "100m Sprint",
            "sport": "Athletics",
        }
    ]
    return client


def pytest_configure(config):
    """Configure pytest."""
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires GCP credentials)"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "requires_gcp: mark test as requiring GCP access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

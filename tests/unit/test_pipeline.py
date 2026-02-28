"""
Unit tests for Olympic ETL Pipeline components.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.beam.pipelines.data_quality import DataValidator


class TestDataValidator:
    """Test DataValidator class."""

    def test_valid_record(self):
        """Test validation of a valid record."""
        validator = DataValidator()
        
        record = {
            "record_id": "rec_001",
            "athlete_id": "ath_123",
            "athlete_name": "John Doe",
            "event_id": "evt_001",
            "country_code": "USA",
            "medal_type": "GOLD",
            "year": 2020,
        }
        
        result = validator.validate_record(record)
        
        assert result["is_valid"]
        assert len(result["errors"]) == 0

    def test_missing_required_field(self):
        """Test validation of record with missing required field."""
        validator = DataValidator()
        
        record = {
            "record_id": "rec_002",
            "athlete_id": "ath_124",
            "athlete_name": "Jane Smith",
            # Missing event_id
            "country_code": "CHN",
            "medal_type": "SILVER",
            "year": 2020,
        }
        
        result = validator.validate_record(record)
        
        assert not result["is_valid"]
        assert len(result["errors"]) > 0

    def test_invalid_medal_type(self):
        """Test validation with invalid medal type."""
        validator = DataValidator()
        
        record = {
            "record_id": "rec_003",
            "athlete_id": "ath_125",
            "athlete_name": "Test Athlete",
            "event_id": "evt_003",
            "country_code": "GBR",
            "medal_type": "PLATINUM",  # Invalid
            "year": 2020,
        }
        
        result = validator.validate_record(record)
        
        assert not result["is_valid"]
        assert any("medal_type" in error for error in result["errors"])

    def test_invalid_year(self):
        """Test validation with invalid year."""
        validator = DataValidator()
        
        record = {
            "record_id": "rec_004",
            "athlete_id": "ath_126",
            "athlete_name": "Test Athlete",
            "event_id": "evt_004",
            "country_code": "JPN",
            "medal_type": "BRONZE",
            "year": 2050,  # Future year
        }
        
        result = validator.validate_record(record)
        
        assert not result["is_valid"]
        assert any("year" in error for error in result["errors"])

    def test_batch_validation(self):
        """Test batch validation of multiple records."""
        validator = DataValidator()
        
        records = [
            {
                "record_id": "rec_001",
                "athlete_id": "ath_001",
                "athlete_name": "Athlete 1",
                "event_id": "evt_001",
                "country_code": "USA",
                "medal_type": "GOLD",
                "year": 2020,
            },
            {
                "record_id": "rec_002",
                "athlete_id": "ath_002",
                "athlete_name": "Athlete 2",
                "event_id": "evt_002",
                "country_code": "CHN",
                "medal_type": "SILVER",
                "year": 2020,
            },
            {
                "record_id": "rec_003",
                "athlete_id": "ath_003",
                "athlete_name": "",  # Invalid
                "event_id": "evt_003",
                "country_code": "GBR",
                "medal_type": "BRONZE",
                "year": 2020,
            },
        ]
        
        summary = validator.validate_batch(records)
        
        assert summary["total_records"] == 3
        assert summary["valid_records"] == 2
        assert summary["invalid_records"] == 1
        assert summary["validity_percentage"] > 60

    def test_country_code_validation(self):
        """Test country code length validation."""
        validator = DataValidator()
        
        record = {
            "record_id": "rec_005",
            "athlete_id": "ath_127",
            "athlete_name": "Test Athlete",
            "event_id": "evt_005",
            "country_code": "INVALID",  # Should be 3 chars
            "medal_type": "GOLD",
            "year": 2020,
        }
        
        result = validator.validate_record(record)
        
        assert not result["is_valid"]
        assert any("country_code" in error for error in result["errors"])


class TestAPIClient:
    """Test API Client classes."""

    @patch('requests.Session.get')
    def test_olympics_api_get_athletes(self, mock_get):
        """Test OlympicsAPIClient.get_athletes()"""
        from src.beam.pipelines.api_clients import OlympicsAPIClient
        
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "athlete_id": "ath_001",
                    "athlete_name": "Test Athlete",
                    "country_code": "USA",
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Create client and fetch
        client = OlympicsAPIClient()
        athletes = client.get_athletes(year=2020)
        
        # Assertions
        assert len(athletes) == 1
        assert athletes[0]["athlete_name"] == "Test Athlete"

    @patch('requests.Session.get')
    def test_olympics_api_error_handling(self, mock_get):
        """Test OlympicsAPIClient error handling"""
        from src.beam.pipelines.api_clients import OlympicsAPIClient
        import requests
        
        # Mock error
        mock_get.side_effect = requests.RequestException("Connection error")
        
        # Create client
        client = OlympicsAPIClient()
        athletes = client.get_athletes()
        
        # Should return empty list on error
        assert athletes == []


class TestDataQualityExpectations:
    """Test Great Expectations patterns."""
    
    def test_athlete_expectations(self):
        """Test athlete data expectations."""
        from src.beam.pipelines.data_quality import ExpectationSuite
        
        expectations = ExpectationSuite.athlete_expectations()
        
        assert len(expectations) > 0
        assert any(
            e["expectation_type"] == "expect_column_to_exist"
            for e in expectations
        )

    def test_medal_expectations(self):
        """Test medal data expectations."""
        from src.beam.pipelines.data_quality import ExpectationSuite
        
        expectations = ExpectationSuite.medal_expectations()
        
        assert len(expectations) > 0
        medal_types = {}
        for e in expectations:
            if e["expectation_type"] == "expect_column_values_to_be_in_set":
                medal_types = e["kwargs"]["value_set"]
        
        assert "GOLD" in medal_types
        assert "SILVER" in medal_types
        assert "BRONZE" in medal_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

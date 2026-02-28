"""
Data Quality Validation using Great Expectations.

Provides validation rules and expectations for Olympic data quality.
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates Olympic data against quality rules."""

    def __init__(self, config_path: str = None):
        self.config_path = config_path
        self.validation_results = []
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Dict]:
        """Load validation rules from configuration."""
        return {
            "athlete_id": {
                "type": "string",
                "required": True,
                "min_length": 1,
                "max_length": 100,
            },
            "event_id": {
                "type": "string",
                "required": True,
            },
            "country_code": {
                "type": "string",
                "required": True,
                "length": 3,  # ISO 3166-1 alpha-3
            },
            "medal_type": {
                "type": "string",
                "required": True,
                "allowed_values": ["GOLD", "SILVER", "BRONZE"],
            },
            "year": {
                "type": "integer",
                "required": True,
                "min_value": 1896,
                "max_value": 2024,
            },
            "athlete_name": {
                "type": "string",
                "required": True,
                "min_length": 1,
            },
        }

    def validate_record(self, record: Dict) -> Dict[str, Any]:
        """
        Validate a single record against expectations.

        Returns:
            Dict with validation status and errors.
        """
        errors = []

        for field, rule in self.rules.items():
            if rule.get("required") and field not in record:
                errors.append(f"{field}: required field missing")
                continue

            if field not in record:
                continue

            value = record[field]

            # Type validation
            expected_type = rule.get("type")
            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"{field}: expected string, got {type(value).__name__}")
            elif expected_type == "integer" and not isinstance(value, int):
                errors.append(f"{field}: expected integer, got {type(value).__name__}")

            # String validations
            if isinstance(value, str):
                if "min_length" in rule and len(value) < rule["min_length"]:
                    errors.append(
                        f"{field}: length {len(value)} < {rule['min_length']}"
                    )
                if "max_length" in rule and len(value) > rule["max_length"]:
                    errors.append(
                        f"{field}: length {len(value)} > {rule['max_length']}"
                    )
                if "length" in rule and len(value) != rule["length"]:
                    errors.append(
                        f"{field}: length {len(value)} != {rule['length']}"
                    )
                if "allowed_values" in rule and value not in rule["allowed_values"]:
                    errors.append(
                        f"{field}: '{value}' not in {rule['allowed_values']}"
                    )

            # Integer validations
            if isinstance(value, int):
                if "min_value" in rule and value < rule["min_value"]:
                    errors.append(f"{field}: {value} < {rule['min_value']}")
                if "max_value" in rule and value > rule["max_value"]:
                    errors.append(f"{field}: {value} > {rule['max_value']}")

        result = {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "record_id": record.get("record_id", "unknown"),
            "validated_at": datetime.utcnow().isoformat(),
        }

        self.validation_results.append(result)
        return result

    def validate_batch(self, records: List[Dict]) -> Dict[str, Any]:
        """
        Validate a batch of records.

        Returns:
            Summary of validation results.
        """
        total = len(records)
        valid_count = 0
        invalid_records = []

        for record in records:
            result = self.validate_record(record)
            if result["is_valid"]:
                valid_count += 1
            else:
                invalid_records.append(
                    {
                        "record_id": record.get("record_id"),
                        "errors": result["errors"],
                    }
                )

        summary = {
            "total_records": total,
            "valid_records": valid_count,
            "invalid_records": len(invalid_records),
            "validity_percentage": (valid_count / total * 100) if total > 0 else 0,
            "invalid_details": invalid_records[:10],  # Top 10 errors
            "validated_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Batch validation: {summary}")
        return summary

    def get_expectations_json(self) -> str:
        """Export rules as Great Expectations JSON."""
        return json.dumps(self.rules, indent=2)


class ExpectationSuite:
    """Define expectations for Olympic data using Great Expectations patterns."""

    @staticmethod
    def athlete_expectations() -> List[Dict]:
        """Expectations for athlete data."""
        return [
            {
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {"min_value": 1, "max_value": 500000},
            },
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "athlete_id"},
            },
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "athlete_id"},
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": "athlete_id", "type_": "string"},
            },
            {
                "expectation_type": "expect_column_value_lengths_to_be_between",
                "kwargs": {
                    "column": "athlete_name",
                    "min_value": 1,
                    "max_value": 200,
                },
            },
        ]

    @staticmethod
    def medal_expectations() -> List[Dict]:
        """Expectations for medal data."""
        return [
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "medal_type"},
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "medal_type",
                    "value_set": ["GOLD", "SILVER", "BRONZE"],
                },
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "year", "min_value": 1896, "max_value": 2024},
            },
        ]

    @staticmethod
    def geography_expectations() -> List[Dict]:
        """Expectations for geographic data."""
        return [
            {
                "expectation_type": "expect_column_to_exist",
                "kwargs": {"column": "country_code"},
            },
            {
                "expectation_type": "expect_column_values_to_match_regex",
                "kwargs": {
                    "column": "country_code",
                    "regex": "^[A-Z]{3}$",  # ISO 3166-1 alpha-3
                },
            },
        ]


if __name__ == "__main__":
    # Test the validator
    logging.basicConfig(level=logging.INFO)

    validator = DataValidator()

    test_records = [
        {
            "record_id": "rec_001",
            "athlete_id": "ath_123",
            "athlete_name": "John Doe",
            "event_id": "evt_001",
            "country_code": "USA",
            "medal_type": "GOLD",
            "year": 2020,
        },
        {
            "record_id": "rec_002",
            "athlete_id": "ath_124",
            "athlete_name": "Jane Smith",
            "event_id": "evt_002",
            "country_code": "CHN",
            "medal_type": "SILVER",
            "year": 2020,
        },
        {
            "record_id": "rec_003",
            "athlete_id": "ath_125",
            "athlete_name": "",  # Invalid: empty name
            "event_id": "evt_003",
            "country_code": "GBR",
            "medal_type": "INVALID",  # Invalid: not GOLD/SILVER/BRONZE
            "year": 2025,  # Invalid: year > 2024
        },
    ]

    results = validator.validate_batch(test_records)
    print(json.dumps(results, indent=2))

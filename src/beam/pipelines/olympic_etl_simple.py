#!/usr/bin/env python3
"""
Olympic Data ETL Pipeline - Simplified Local Version (No Apache Beam)
Run locally for testing without cloud dependencies.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleOlympicsPipeline:
    """Simplified pipeline for local testing"""
    
    def __init__(self, project: str = "my-olympic-etl"):
        self.project = project
        self.data = []
        self.valid_records = []
        self.invalid_records = []
        
    def load_sample_data(self) -> List[Dict[str, Any]]:
        """Load sample Olympics data"""
        sample_file = Path("data/sample/olympics_sample.json")
        
        if sample_file.exists():
            logger.info(f"Loading sample data from {sample_file}")
            with open(sample_file) as f:
                self.data = json.load(f)
        else:
            logger.warning(f"Sample file not found: {sample_file}")
            # Create minimal test data
            self.data = [
                {
                    "athlete_id": "1",
                    "name": "Sample Athlete",
                    "country": "USA",
                    "sport": "Basketball",
                    "medal": "Gold",
                    "year": 2020
                }
            ]
        
        logger.info(f"Loaded {len(self.data)} records")
        return self.data
    
    def validate_records(self) -> Dict[str, int]:
        """Validate records"""
        logger.info("Starting validation...")
        
        required_fields = {"athlete_id", "name", "country", "sport", "year"}
        
        for record in self.data:
            # Check required fields
            if all(field in record for field in required_fields):
                # Check data types
                if isinstance(record["year"], int) and 1900 <= record["year"] <= 2100:
                    self.valid_records.append(record)
                else:
                    self.invalid_records.append({
                        **record,
                        "_error": "Invalid year"
                    })
            else:
                missing = required_fields - set(record.keys())
                self.invalid_records.append({
                    **record,
                    "_error": f"Missing fields: {missing}"
                })
        
        logger.info(f"Valid: {len(self.valid_records)}, Invalid: {len(self.invalid_records)}")
        return {
            "valid": len(self.valid_records),
            "invalid": len(self.invalid_records)
        }
    
    def add_metadata(self) -> None:
        """Add processing metadata"""
        logger.info("Adding metadata...")
        
        timestamp = datetime.utcnow().isoformat()
        
        for record in self.valid_records:
            record["_processed_at"] = timestamp
            record["_pipeline_version"] = "1.0.0"
            record["_environment"] = "local"
    
    def enrich_data(self) -> None:
        """Enrich with additional information"""
        logger.info("Enriching data...")
        
        # Simple enrichment example
        for record in self.valid_records:
            if "medal" in record:
                record["medal_rank"] = {
                    "Gold": 1,
                    "Silver": 2,
                    "Bronze": 3
                }.get(record["medal"], 0)
    
    def save_output(self, output_dir: str = "output") -> Dict[str, str]:
        """Save results to output files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save valid records
        valid_file = output_path / "valid_records.json"
        with open(valid_file, "w") as f:
            json.dump(self.valid_records, f, indent=2)
        logger.info(f"Saved valid records to {valid_file}")
        
        # Save invalid records
        invalid_file = output_path / "invalid_records.json"
        with open(invalid_file, "w") as f:
            json.dump(self.invalid_records, f, indent=2)
        logger.info(f"Saved invalid records to {invalid_file}")
        
        # Save summary
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "project": self.project,
            "total_records": len(self.data),
            "valid_records": len(self.valid_records),
            "invalid_records": len(self.invalid_records),
            "success_rate": f"{100 * len(self.valid_records) / len(self.data):.2f}%" if self.data else "0%"
        }
        
        summary_file = output_path / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary: {summary}")
        
        return {
            "valid": str(valid_file),
            "invalid": str(invalid_file),
            "summary": str(summary_file)
        }
    
    def run(self) -> bool:
        """Execute full pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("Olympic Data ETL Pipeline - Local Version")
            logger.info(f"Project: {self.project}")
            logger.info("=" * 60)
            
            # Execute pipeline steps
            self.load_sample_data()
            self.validate_records()
            self.add_metadata()
            self.enrich_data()
            results = self.save_output()
            
            logger.info("=" * 60)
            logger.info("Pipeline completed successfully! ✅")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    import sys
    
    # Get project from command line
    project = sys.argv[1] if len(sys.argv) > 1 else "my-olympic-etl"
    
    pipeline = SimpleOlympicsPipeline(project=project)
    success = pipeline.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

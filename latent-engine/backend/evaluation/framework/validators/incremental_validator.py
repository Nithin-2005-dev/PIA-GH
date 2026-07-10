from typing import Any
from app.adapters.database.sqlite_provider import get_provider
from app.adapters.database.models import MeasurementRecord

class IncrementalValidator:
    @classmethod
    def validate(cls, timestamp_between_syncs: str, full_count: int) -> tuple[bool, str]:
        provider = get_provider()
        
        # Get all measurements updated AFTER the timestamp_between_syncs
        # Since timestamp is ISO8601, we can do string comparison in python
        all_measurements = provider.query(MeasurementRecord, limit=10000)
        
        updated_measurements = [
            m for m in all_measurements 
            if (m.identity.updated_at and m.identity.updated_at > timestamp_between_syncs) or 
               (m.identity.created_at and m.identity.created_at > timestamp_between_syncs)
        ]
        
        updated_count = len(updated_measurements)
        
        report = "IncrementalSyncValidationReport\n\n"
        report += f"Total Measurements: {len(all_measurements)}\n"
        report += f"Updated/Inserted Measurements in Incremental Sync: {updated_count}\n\n"
        
        passed = True
        
        if updated_count == 0:
            report += "FAIL: No measurements were updated or inserted during the incremental sync.\n"
            passed = False
        elif updated_count >= full_count:
            report += f"FAIL: Full recompute detected! Expected a small fraction of {full_count}, but {updated_count} were updated.\n"
            passed = False
        else:
            report += f"PASS: Only {updated_count} measurements were updated, confirming incremental behavior.\n"
            
        return passed, report

import uuid
from datetime import datetime, UTC
from typing import Optional

from app.measurement.core.recompute import AppendOnlyRecomputeEngine
from app.measurement.core.audit import MeasurementAuditLog, RecomputeAuditRecord
from app.measurement.core.quality import RecomputeQualityGate
from app.measurement.domain import Measurement, MeasurementDefinition, MeasurementUnit, MeasurementUncertainty, NormalizationMethod, MeasurementProvenance, MeasurementTrace, MeasurementMethod

class MockStore:
    def __init__(self):
        self.saved_measurements = []
    def save(self, measurement):
        self.saved_measurements.append(measurement)

class MockMeasurementEngine:
    def __init__(self, override_value: float):
        self.override_value = override_value
        
    def measure_observation(self, observation, context) -> list[Measurement]:
        MOCK_DEF = MeasurementDefinition(id="code_churn", name="Code Churn", description="Mock Code Churn", unit=MeasurementUnit.COUNT, version="2.0")
        new_m = Measurement(
            id="temp_id",
            definition=MOCK_DEF,
            unit=MeasurementUnit.COUNT,
            value=self.override_value,
            confidence=0.9,
            uncertainty=MeasurementUncertainty(self.override_value, self.override_value, 0.0),
            quality_score=0.9,
            measurement_method=MeasurementMethod("mock_evaluator", "2.0", "code_churn"),
            normalization_method=NormalizationMethod("identity", "2.0", MeasurementUnit.COUNT, MeasurementUnit.COUNT),
            provenance=MeasurementProvenance("github", "test_adapter", "obs_1", "obs_1", ("target_dev",), ("facts",), "tenant_1", "target_dev", "user", "commit"),
            timestamp=datetime.now(UTC),
            version="2.0",
            traceability=MeasurementTrace("2.0", "mock_evaluator"),
            metadata={}
        )
        return [new_m]

def run_test():
    MOCK_DEF = MeasurementDefinition(id="code_churn", name="Code Churn", description="Mock Code Churn", unit=MeasurementUnit.COUNT, version="1.0")
    
    old_measurement = Measurement(
        id="old_m_123",
        definition=MOCK_DEF,
        unit=MeasurementUnit.COUNT,
        value=10.0,
        confidence=0.8,
        uncertainty=MeasurementUncertainty(10.0, 10.0, 0.0),
        quality_score=0.8,
        measurement_method=MeasurementMethod("mock_evaluator", "1.0", "code_churn"),
        normalization_method=NormalizationMethod("identity", "1.0", MeasurementUnit.COUNT, MeasurementUnit.COUNT),
        provenance=MeasurementProvenance("github", "test_adapter", "obs_1", "obs_1", ("target_dev",), ("facts",), "tenant_1", "target_dev", "user", "commit"),
        timestamp=datetime.now(UTC),
        version="1.0",
        traceability=MeasurementTrace("1.0", "mock_evaluator"),
        metadata={}
    )
    
    store = MockStore()
    audit_log = MeasurementAuditLog()
    gate = RecomputeQualityGate()
    
    print("--- Test 1: Safe Recompute (20% drift) ---")
    engine1 = MockMeasurementEngine(override_value=12.0)
    recomputer1 = AppendOnlyRecomputeEngine(engine1, store, audit_log, gate)
    
    new_m = recomputer1.recompute_historical_measurement(old_measurement, raw_observation="mock_obs", context="mock_ctx")
    
    assert new_m is not None, "Recompute should have succeeded"
    assert new_m.metadata["supersedes_id"] == "old_m_123", "Must have supersedes pointer"
    assert new_m.value == 12.0
    assert len(audit_log._records) == 1
    assert audit_log._records[0].old_value == 10.0
    assert audit_log._records[0].new_value == 12.0
    print("Test 1 Passed: Safe recompute successful, ledger appended.")
    
    print("\n--- Test 2: Unsafe Recompute (10,000% drift) ---")
    engine2 = MockMeasurementEngine(override_value=1000.0)
    recomputer2 = AppendOnlyRecomputeEngine(engine2, store, audit_log, gate)
    
    new_m2 = recomputer2.recompute_historical_measurement(old_measurement, raw_observation="mock_obs", context="mock_ctx")
    
    assert new_m2 is None, "Recompute should have been BLOCKED by quality gate"
    print("Test 2 Passed: Destructive recompute successfully blocked!")

if __name__ == "__main__":
    run_test()

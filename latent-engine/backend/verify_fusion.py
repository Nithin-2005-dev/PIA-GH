import asyncio
from dataclasses import dataclass
from datetime import datetime, UTC

from app.measurement.core.engine import MeasurementEngine
from app.measurement.domain.registry import MeasurementRegistry
from app.measurement.core.interfaces import MeasurementEvaluator
from app.measurement.domain import Measurement, MeasurementContext, MeasurementDefinition, MeasurementMethod, MeasurementUncertainty, NormalizationMethod, MeasurementProvenance, MeasurementTrace, MeasurementUnit
from app.observation.domain import Observation, CommitFacts, ObservationType, ObservationCategory, ObservationLifecycle, ObservationProvenance, ObservationContext
from app.domain.entity_ref import EntityRef
from app.measurement.core.confidence import DefaultConfidenceEstimator
from app.measurement.core.quality import DefaultQualityScorer
from app.measurement.core.normalization_pipeline import NormalizationPipeline

# Create a mock measurement definition
MOCK_CODE_CHURN = MeasurementDefinition(
    id="code_churn",
    name="Code Churn",
    description="Mock Code Churn",
    unit=MeasurementUnit.COUNT,
    version="1.0"
)

class MockGithubEvaluator(MeasurementEvaluator):
    @property
    def metric_name(self) -> str: return "mock_github_churn"
    @property
    def logic_version(self) -> str: return "1.0"

    def evaluate(self, observation: Observation, context: MeasurementContext) -> list[Measurement]:
        return [
            Measurement(
                id="github_churn_123",
                definition=MOCK_CODE_CHURN,
                unit=MeasurementUnit.COUNT,
                value=100.0,
                confidence=0.4, # Hardcoded confidence before fusion
                uncertainty=MeasurementUncertainty(100.0, 100.0, 0.0),
                quality_score=0.4,
                measurement_method=MeasurementMethod("github_evaluator", "1.0", "code_churn"),
                normalization_method=NormalizationMethod("identity", "1.0", MeasurementUnit.COUNT, MeasurementUnit.COUNT),
                provenance=MeasurementProvenance("github", "test_adapter", "obs_1", "obs_1", ("target_dev",), ("facts",), "tenant_1", "target_dev", "user", "commit"),
                timestamp=datetime.now(UTC),
                version="1.0",
                traceability=MeasurementTrace("1.0", "github_evaluator"),
                metadata={"confidence_override": 0.4} # In a real test, confidence estimator computes this
            )
        ]

class MockSonarEvaluator(MeasurementEvaluator):
    @property
    def metric_name(self) -> str: return "mock_sonar_churn"
    @property
    def logic_version(self) -> str: return "1.0"

    def evaluate(self, observation: Observation, context: MeasurementContext) -> list[Measurement]:
        return [
            Measurement(
                id="sonar_churn_123",
                definition=MOCK_CODE_CHURN,
                unit=MeasurementUnit.COUNT,
                value=95.0,
                confidence=0.9, # Higher confidence
                uncertainty=MeasurementUncertainty(95.0, 95.0, 0.0),
                quality_score=0.9,
                measurement_method=MeasurementMethod("sonar_evaluator", "1.0", "code_churn"),
                normalization_method=NormalizationMethod("identity", "1.0", MeasurementUnit.COUNT, MeasurementUnit.COUNT),
                provenance=MeasurementProvenance("sonarqube", "test_adapter", "obs_1", "obs_1", ("target_dev",), ("facts",), "tenant_1", "target_dev", "user", "commit"),
                timestamp=datetime.now(UTC),
                version="1.0",
                traceability=MeasurementTrace("1.0", "sonar_evaluator"),
                metadata={"confidence_override": 0.9} 
            )
        ]

class MockConfidenceEstimator(DefaultConfidenceEstimator):
    def estimate(self, measurement: Measurement, context: MeasurementContext) -> Measurement:
        from dataclasses import replace
        # Override the confidence for our test
        override = measurement.metadata.get("confidence_override")
        if override is not None:
            return replace(measurement, confidence=override)
        return super().estimate(measurement, context)


def run_test():
    registry = MeasurementRegistry()
    registry.register_evaluator(MockGithubEvaluator())
    registry.register_evaluator(MockSonarEvaluator())

    engine = MeasurementEngine(
        registry=registry,
        normalizers=[],
        validators=[],
        confidence_estimator=MockConfidenceEstimator(),
        quality_scorer=DefaultQualityScorer(),
        normalization_pipeline=NormalizationPipeline.default(),
    )

    # Mock Observation
    obs = Observation(
        observation_id="obs_1",
        trace_id="trace_1",
        correlation_id="corr_1",
        timestamp=datetime.now(UTC),
        observation_type=ObservationType.COMMIT,
        observation_category=ObservationCategory.SOURCE_CONTROL,
        source_platform="github",
        source_adapter="test_adapter",
        version="1.0",
        lifecycle=ObservationLifecycle.VALIDATED,
        actors=(EntityRef("target_dev", "user"),),
        targets=(EntityRef("target_repo", "repository"),),
        provenance=ObservationProvenance("github", "test_adapter", "rec_1"),
        context=ObservationContext(tenant_id="tenant_1"),
        facts=CommitFacts(
            commit_id="sha_1",
            message="test commit",
            author_name="dev",
            author_email="dev@dev.com",
            authored_at=datetime.now(UTC)
        ),
    )

    context = MeasurementContext(timestamp=datetime.now(UTC))

    fused_measurements = engine.measure_observation(obs, context)

    print(f"Number of measurements returned: {len(fused_measurements)}")
    if fused_measurements:
        m = fused_measurements[0]
        print(f"Fused Value: {m.value}")
        print(f"Fused Confidence: {m.confidence}")
        print(f"Fused Provenance: {m.provenance.transformations}")
        
        # Verify it's closer to 95 than 100
        assert len(fused_measurements) == 1, "Expected exactly one fused measurement"
        assert abs(m.value - 95.0) < abs(m.value - 100.0), f"Value {m.value} should be closer to 95"
        print("TEST PASSED: Fusion logic applied correctly!")

if __name__ == "__main__":
    run_test()

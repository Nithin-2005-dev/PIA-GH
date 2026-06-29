from datetime import UTC
from datetime import datetime
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    ),
)

from app.domain.entity_ref import EntityRef
from app.domain.entity_type import EntityType
from app.domain.event import Event
from app.domain.event_type import EventType
from app.measurement.domain import MeasurementContext
from app.measurement.domain import MeasurementDefinition
from app.measurement.domain import SoftwareSignal
from app.measurement.domain import MeasurementUnit
from app.measurement.domain import ValidationStatus
from app.measurement.benchmark import BenchmarkEngine
from app.measurement.benchmark_datasets import BenchmarkDataset
from app.measurement.benchmark_datasets import BenchmarkDatasetRegistry
from app.measurement.benchmark_datasets import BenchmarkScope
from app.measurement.catalog import DefaultMeasurementCatalog
from app.measurement.accuracy import EnterpriseAccuracyPipeline
from app.measurement.active import ActiveMeasurementService
from app.measurement.compression import ApproximateHistogramBuilder
from app.measurement.compression import ReservoirSampler
from app.measurement.contracts import MeasurementContract
from app.measurement.contracts import MeasurementContractValidator
from app.measurement.contracts import MeasurementLifecycle
from app.measurement.domain_packs import DefaultDomainPacks
from app.measurement.dsl import MeasurementDslParser
from app.measurement.engine import MeasurementEngine
from app.measurement.execution import CandidateMeasurementPath
from app.measurement.execution import CostBasedMeasurementOptimizer
from app.measurement.execution import MeasurementComputationNode
from app.measurement.execution import MeasurementExecutionPlanner
from app.measurement.execution import MeasurementExecutor
from app.measurement.formula import DerivedMeasurementEngine
from app.measurement.formula import FormulaDefinition
from app.measurement.fusion import MultiSourceFusionEngine
from app.measurement.fusion import ProbabilisticFusionEngine
from app.measurement.lineage import MeasurementExplainer
from app.measurement.lineage import MeasurementLineageService
from app.measurement.lineage_query import MeasurementLineageQueryEngine
from app.measurement.knowledge_api import MeasurementKnowledgeApi
from app.measurement.mapping import MappingCardinality
from app.measurement.mapping import SignalMeasurementMapping
from app.measurement.mapping import SignalMeasurementMappingRegistry
from app.measurement.mapping import SignalToMeasurementMapper
from app.measurement.measurement_knowledge import DefaultSoftwareMeasurementKnowledge
from app.measurement.ml import CalibrationResult
from app.measurement.ml import MeasurementCalibrationModel
from app.measurement.ml import MlCalibrationService
from app.measurement.mql import MqlEngine
from app.measurement.mql import MqlParser
from app.measurement.ontology import MeasurementOntology
from app.measurement.packs import MeasurementMarketplace
from app.measurement.packs import MeasurementPack
from app.measurement.recompute import MeasurementDependencyGraph
from app.measurement.semantic_graph import ConceptRelationship
from app.measurement.semantic_graph import SemanticMeasurementEdge
from app.measurement.semantic_graph import SemanticMeasurementGraph
from app.measurement.signal_classifier import SemanticSignalClassifier
from app.measurement.signal_ontology import SignalOntology
from app.measurement.signal_validation import SemanticMappingValidator
from app.measurement.signal_validation import SignalDefinitionValidator
from app.measurement.signals import DefaultSignalCatalog
from app.measurement.standards import StandardsCatalog
from app.measurement.statistical_pipeline import StatisticsPipeline
from app.measurement.store import MeasurementCache
from app.measurement.store import TemporalMeasurementStore
from app.measurement.streaming import StreamingMeasurementEngine


class DemoCalibrationModel(MeasurementCalibrationModel):

    def calibrate(
        self,
        measurement,
    ):
        return CalibrationResult(
            calibrated_value=measurement.value + 1.0,
            confidence_adjustment=0.01,
            model_name="demo-calibrator",
            model_version="1.0",
        )


def developer(
    name,
):
    return EntityRef(
        id=name,
        type=EntityType.DEVELOPER,
    )


def module(
    name,
):
    return EntityRef(
        id=name,
        type=EntityType.FILE,
    )


def event():
    event_id = uuid4()

    return Event(
        id=event_id,
        type=EventType.COMMIT,
        actor_ref=developer(
            "alice"
        ),
        target_refs=(
            module(
                "payments.py"
            ),
            module(
                "billing.py"
            ),
        ),
        occurred_at=datetime.now(
            UTC
        ),
        payload={
            "additions": 40,
            "deletions": 10,
            "total_changes": 50,
            "observation": {
                "behavioral": {
                    "commit": {
                        "files_changed": 2,
                        "total_additions": 40,
                        "total_deletions": 10,
                        "total_changes": 50,
                    }
                },
                "artifact": {
                    "files": [
                        {
                            "filename": "payments.py",
                            "changes": 35,
                            "patch": (
                                "+ if amount > 0:\n"
                                "+     for item in items:\n"
                                "- if old_amount:\n"
                            ),
                        },
                        {
                            "filename": "billing.py",
                            "changes": 15,
                            "patch": "+ while retry:\n",
                        },
                    ]
                },
            },
        },
        metadata={
            "source": "github",
            "gateway": "rest",
        },
    )


def main():
    engine = MeasurementEngine.default()

    context = MeasurementContext(
        timestamp=datetime.now(
            UTC
        ),
        tenant_id="tenant-a",
        source_reliability={
            "github": 0.95,
        },
        metadata={
            "benchmarks": {
                "code_churn": [
                    5,
                    10,
                    20,
                    50,
                    100,
                ]
            }
        },
    )

    measurements = engine.measure_event(
        event(),
        context,
    )

    assert len(
        measurements
    ) == 6

    by_definition = {
        measurement.definition.id: measurement
        for measurement in measurements
    }

    assert by_definition[
        "code_churn"
    ].value == 50

    assert by_definition[
        "files_changed"
    ].value == 2

    assert by_definition[
        "patch_complexity_delta"
    ].value == 2

    for measurement in measurements:
        assert measurement.validation_status in {
            ValidationStatus.PASSED,
            ValidationStatus.WARNING,
        }
        assert 0.0 <= measurement.confidence <= 1.0
        assert 0.0 <= measurement.quality_score <= 1.0
        assert measurement.provenance.source_event_id is not None

    derived = DerivedMeasurementEngine().derive(
        FormulaDefinition(
            definition=MeasurementDefinition(
                id="change_risk_index",
                name="Change Risk Index",
                description="Risk = churn * attention.",
                unit=MeasurementUnit.SCORE,
                version="1.0",
                minimum=0.0,
            ),
            expression="churn * attention",
            variable_measurement_ids={
                "churn": by_definition[
                    "code_churn"
                ].id,
                "attention": by_definition[
                    "review_attention_need"
                ].id,
            },
        ),
        measurements,
    )

    assert derived.dependencies
    assert derived.traceability.formula == "churn * attention"
    assert derived.uncertainty.variance > 0

    fused = MultiSourceFusionEngine().fuse(
        [
            by_definition[
                "change_surface_area"
            ],
            by_definition[
                "review_attention_need"
            ],
        ]
    )

    assert fused.dependencies
    assert fused.metadata[
        "source_count"
    ] == 2

    probabilistic = ProbabilisticFusionEngine().fuse(
        [
            by_definition[
                "change_surface_area"
            ],
            by_definition[
                "review_attention_need"
            ],
        ]
    )

    assert probabilistic.uncertainty.method == (
        "precision_weighted_bayesian_fusion"
    )

    ontology = MeasurementOntology.default()

    assert ontology.get(
        "maintainability"
    ).display_name == "Maintainability"

    registry = DefaultMeasurementCatalog.build()

    assert registry.get(
        "code_churn"
    ).concept_id == "change_impact"

    signal_registry = DefaultSignalCatalog.build()
    signal_definition = signal_registry.get(
        "git.total_additions"
    )

    software_signal = SoftwareSignal(
        id="git.total_additions",
        name="total_additions",
        source="github",
        value=40,
        unit=MeasurementUnit.LOC,
        source_event_id="event-1",
    )

    assert (
        SignalDefinitionValidator()
        .validate_value(
            software_signal,
            signal_definition,
        )
        .status
        == ValidationStatus.PASSED
    )

    signal_ontology = SignalOntology.default()
    classification = SemanticSignalClassifier(
        signal_registry,
        signal_ontology,
    ).classify(
        software_signal
    )

    assert classification.category == "source_control"

    mapping_registry = SignalMeasurementMappingRegistry()
    mapping_registry.register(
        SignalMeasurementMapping(
            id="git-additions-to-churn",
            version="1.0",
            signal_ids=(
                "git.total_additions",
                "git.total_deletions",
            ),
            concept_id="change_impact",
            measurement_definition_ids=(
                "code_churn",
            ),
            evaluator="change_complexity_evaluator",
            cardinality=MappingCardinality.MANY_TO_ONE,
            confidence=0.95,
            explanation=(
                "line additions and deletions compose code churn"
            ),
            trace=(
                "signal_registry",
                "measurement_registry",
            ),
        )
    )

    resolution = SignalToMeasurementMapper(
        registry,
        mapping_registry,
    ).resolve(
        software_signal,
        classification,
    )

    assert resolution.definitions[0].id == "code_churn"

    assert (
        SemanticMappingValidator()
        .validate(
            classification,
            resolution,
        )
        .status
        == ValidationStatus.PASSED
    )

    standards = StandardsCatalog.default()

    assert standards.get(
        "ISO-15939"
    ).organization == "ISO/IEC"

    domain_packs = DefaultDomainPacks.build()

    assert any(
        pack.id == "code-quality"
        for pack in domain_packs
    )

    measurement_knowledge = (
        DefaultSoftwareMeasurementKnowledge
        .build()
    )

    assert measurement_knowledge.get(
        "code_churn"
    ).business_definition

    benchmark_registry = BenchmarkDatasetRegistry()
    benchmark_registry.register(
        BenchmarkDataset(
            id="repo-code-churn",
            measurement_id="code_churn",
            scope=BenchmarkScope.REPOSITORY,
            values=(
                5,
                10,
                20,
                50,
            ),
            version="1.0",
            source="internal",
            metadata={
                "repository": "latent-engine",
            },
        )
    )

    knowledge_api = MeasurementKnowledgeApi(
        signal_registry=signal_registry,
        measurement_registry=registry,
        mapping_registry=mapping_registry,
        signal_ontology=signal_ontology,
        measurement_knowledge=measurement_knowledge,
        benchmark_registry=benchmark_registry,
        standards_catalog=standards,
    )

    assert knowledge_api.signal_definition(
        "git.total_additions"
    ).display_name == "Total Additions"
    assert knowledge_api.measurement_definition(
        "code_churn"
    ).name == "Code Churn"
    assert knowledge_api.mappings_for_signal(
        "git.total_additions"
    )
    assert knowledge_api.benchmark_metadata(
        "code_churn"
    )
    assert knowledge_api.standards_references()

    contract = MeasurementContract(
        definition=registry.get(
            "code_churn"
        ),
        input_signals=(
            "total_additions",
            "total_deletions",
        ),
        output_unit=MeasurementUnit.LOC,
        precision=0.05,
        confidence_model="default_factor_model",
        lifecycle=MeasurementLifecycle.PRODUCTION,
    )

    assert (
        MeasurementContractValidator()
        .validate(
            by_definition[
                "code_churn"
            ],
            contract,
        )
        .status
        == ValidationStatus.PASSED
    )

    parsed = MeasurementDslParser().parse(
        """
        measure Risk
        from Complexity
        from Ownership
        formula Complexity * Ownership
        confidence Bayesian
        validator Range
        normalizer Percentile
        """
    )

    definition = MeasurementDslParser().to_definition(
        parsed
    )

    assert definition.formula == "Complexity * Ownership"
    assert definition.confidence_model == "Bayesian"

    lineage = MeasurementLineageService().graph_for(
        derived
    )

    assert lineage.nodes
    assert lineage.edges

    first_node = lineage.nodes[0].id
    path = MeasurementLineageQueryEngine().show_path(
        lineage,
        first_node,
        derived.id,
    )

    assert path

    explanation = MeasurementExplainer().explain(
        derived
    )

    assert explanation[
        "formula"
    ] == "churn * attention"

    store = TemporalMeasurementStore()

    for measurement in measurements:
        store.append(
            measurement
        )

    assert store.history(
        "code_churn",
        tuple(
            by_definition[
                "code_churn"
            ].provenance.source_entity_ids
        ),
    )

    cache = MeasurementCache()
    cache.put_hot(
        by_definition[
            "code_churn"
        ]
    )

    assert cache.get(
        by_definition[
            "code_churn"
        ].id
    )

    graph = MeasurementDependencyGraph()
    graph.register(
        derived.id,
        derived.dependencies,
    )

    assert graph.affected_by(
        derived.dependencies[0]
    ) == {
        derived.id
    }

    semantic_graph = SemanticMeasurementGraph()
    semantic_graph.add(
        SemanticMeasurementEdge(
            source_concept_id="maintainability",
            target_concept_id="complexity",
            relationship=ConceptRelationship.DEPENDS_ON,
            confidence=0.95,
        )
    )

    assert semantic_graph.neighbors(
        "maintainability"
    )

    benchmark = BenchmarkEngine().compare(
        by_definition[
            "code_churn"
        ].value,
        [
            5,
            10,
            20,
            50,
            100,
        ],
        "repository",
    )

    assert benchmark.cohort == "repository"

    report = StatisticsPipeline().analyze(
        [
            measurement.value
            for measurement in measurements
        ]
    )

    assert report.distribution in {
        "approximately_symmetric",
        "left_skewed",
        "right_skewed",
    }

    accuracy_report = EnterpriseAccuracyPipeline().process(
        measurements,
        context,
    )

    assert accuracy_report.measurements
    assert all(
        validation.status == ValidationStatus.PASSED
        for validation in accuracy_report.validations
    )

    calibrated = MlCalibrationService(
        DemoCalibrationModel()
    ).calibrate(
        by_definition[
            "code_churn"
        ]
    )

    assert calibrated.metadata[
        "ml_calibration"
    ][
        "source_measurement_id"
    ] == by_definition[
        "code_churn"
    ].id

    mql = MqlParser().parse(
        """
        SELECT code_churn
        WHERE confidence > 0.9
        ORDER BY quality_score
        """
    )

    assert MqlEngine().query(
        measurements,
        mql,
    )

    cache = MeasurementCache()
    node = MeasurementComputationNode(
        id="code_churn_node",
        dependencies=(),
        cache_key=by_definition[
            "code_churn"
        ].id,
        cost=1.0,
        executor=lambda: by_definition[
            "code_churn"
        ],
    )
    plan = MeasurementExecutionPlanner().plan(
        requested_ids=(
            "code_churn_node",
        ),
        nodes=[
            node,
        ],
        cache=cache,
    )
    executed = MeasurementExecutor().execute(
        plan,
        cache,
    )

    assert executed[
        "code_churn_node"
    ].definition.id == "code_churn"

    chosen = CostBasedMeasurementOptimizer().choose(
        [
            CandidateMeasurementPath(
                id="ast",
                expected_confidence=0.96,
                expected_latency_ms=100,
                expected_cost=2.0,
            ),
            CandidateMeasurementPath(
                id="llm",
                expected_confidence=0.91,
                expected_latency_ms=900,
                expected_cost=20.0,
            ),
        ],
        minimum_confidence=0.9,
        maximum_latency_ms=500,
    )

    assert chosen.id == "ast"

    marketplace = MeasurementMarketplace()
    marketplace.publish(
        MeasurementPack(
            id="architecture-intelligence",
            name="Architecture Intelligence",
            domain="architecture",
            version="1.0",
            definitions=(
                registry.get(
                    "patch_complexity_delta"
                ),
            ),
        )
    )
    marketplace.install(
        "tenant-a",
        "architecture-intelligence",
    )

    assert marketplace.installed(
        "tenant-a"
    )

    active_requests = (
        ActiveMeasurementService()
        .requests_for_low_confidence(
            measurement_id="low-confidence",
            confidence=0.4,
            required_signals=(
                "runtime_coverage",
            ),
        )
    )

    assert active_requests

    updates = []
    streaming = StreamingMeasurementEngine(
        engine
    )
    streaming.subscribe(
        updates.append
    )
    streaming.ingest(
        event(),
        context,
    )

    assert updates

    sampler = ReservoirSampler(
        size=3
    )

    for value in range(10):
        sampler.add(
            value
        )

    assert len(
        sampler.sample()
    ) == 3

    histogram = ApproximateHistogramBuilder().build(
        [
            measurement.value
            for measurement in measurements
        ]
    )

    assert histogram.counts

    print(
        "\n=== MEASUREMENT ENGINE ===\n"
    )

    for measurement in measurements:
        print(
            f"{measurement.definition.id:<30}"
            f"value={measurement.value:<8.2f}"
            f"confidence={measurement.confidence:.2f} "
            f"quality={measurement.quality_score:.2f}"
        )

    print(
        "\nMeasurement science platform passed."
    )


if __name__ == "__main__":
    main()

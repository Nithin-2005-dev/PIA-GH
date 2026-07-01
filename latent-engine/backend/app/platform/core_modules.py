from __future__ import annotations

from app.platform.di import ServiceCollection
from app.platform.di import ServiceScope
from app.platform.module import BaseModule


class GitHubAdapterFactory:
    def create(
        self,
        token: str,
    ):
        from app.adapters.github.adapter import GitHubAdapter
        from app.adapters.github.rest_gateway import GitHubRestGateway

        return GitHubAdapter(
            gateway=GitHubRestGateway(token=token)
        )


class MeasurementPlatformModule(BaseModule):
    name = "measurement"
    version = "1.0"
    dependencies = ("observation",)
    capabilities = (
        "measurement.provider",
        "measurement.engine",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.measurement.core.engine import MeasurementEngine
        from app.measurement.scientific_engine import MeasurementAggregationEngine
        from app.measurement.scientific_engine import MeasurementBenchmarkRecorder
        from app.measurement.scientific_engine import MeasurementProviderRegistry
        from app.measurement.scientific_engine import ScientificMeasurementEngine
        from app.measurement.scientific_engine import ScientificMeasurementRegistry
        from app.measurement.scientific_engine import ScientificStatistics
        from app.measurement.scientific_engine import default_measurement_providers
        from app.measurement.scientific_engine import default_scientific_measurements
        from app.platform.storage import PlatformStorage

        services.add(
            MeasurementEngine,
            lambda _: MeasurementEngine.default(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScientificMeasurementRegistry,
            lambda _: ScientificMeasurementRegistry(
                default_scientific_measurements()
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            MeasurementProviderRegistry,
            lambda _: MeasurementProviderRegistry(
                default_measurement_providers()
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScientificMeasurementEngine,
            lambda provider: ScientificMeasurementEngine(
                providers=provider.resolve(MeasurementProviderRegistry),
                registry=provider.resolve(ScientificMeasurementRegistry),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            MeasurementAggregationEngine,
            MeasurementAggregationEngine,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScientificStatistics,
            ScientificStatistics,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            MeasurementBenchmarkRecorder,
            MeasurementBenchmarkRecorder,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            PlatformStorage,
            PlatformStorage,
            scope=ServiceScope.SINGLETON,
        )


class ObservationPlatformModule(BaseModule):
    name = "observation"
    version = "1.0"
    dependencies = ()
    capabilities = (
        "observation.ingestion",
        "observation.adapter",
        "observation.replay",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.observation.ingestion import AdapterRegistry
        from app.observation.ingestion import CheckpointStore
        from app.observation.ingestion import ObservationDeduplicator
        from app.observation.ingestion import ObservationIngestionEngine
        from app.observation.ingestion import ObservationIngestionStore
        from app.observation.ingestion import ObservationMetrics
        from app.observation.ingestion import ObservationNormalizer
        from app.observation.ingestion import RateLimiter
        from app.observation.ingestion import UnifiedIdentityResolver
        from app.observation.validation import ObservationValidationPipeline
        from app.observation.adapters import default_observation_adapters

        services.add(
            AdapterRegistry,
            lambda _: self._adapter_registry(
                AdapterRegistry(),
                default_observation_adapters(),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            UnifiedIdentityResolver,
            UnifiedIdentityResolver,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationNormalizer,
            lambda provider: ObservationNormalizer(
                provider.resolve(UnifiedIdentityResolver)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationValidationPipeline,
            ObservationValidationPipeline,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationIngestionStore,
            ObservationIngestionStore,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CheckpointStore,
            CheckpointStore,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationDeduplicator,
            ObservationDeduplicator,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            RateLimiter,
            RateLimiter,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationMetrics,
            ObservationMetrics,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ObservationIngestionEngine,
            lambda provider: ObservationIngestionEngine(
                adapters=provider.resolve(AdapterRegistry),
                normalizer=provider.resolve(ObservationNormalizer),
                validator=provider.resolve(ObservationValidationPipeline),
                store=provider.resolve(ObservationIngestionStore),
                checkpoints=provider.resolve(CheckpointStore),
                deduplicator=provider.resolve(ObservationDeduplicator),
                rate_limiter=provider.resolve(RateLimiter),
                metrics=provider.resolve(ObservationMetrics),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            GitHubAdapterFactory,
            lambda _: GitHubAdapterFactory(),
            scope=ServiceScope.SINGLETON,
        )

    def _adapter_registry(
        self,
        registry,
        adapters,
    ):
        for adapter in adapters:
            registry.register(adapter)
        return registry


class EvidencePlatformModule(BaseModule):
    name = "evidence"
    version = "1.0"
    dependencies = ("measurement",)
    capabilities = (
        "evidence.synthesis",
        "evidence.validation",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.evidence.synthesis.engine import EvidenceSynthesisEngine
        from app.evidence.semantic import SemanticEvidenceEngine

        services.add(
            EvidenceSynthesisEngine,
            EvidenceSynthesisEngine,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SemanticEvidenceEngine,
            SemanticEvidenceEngine,
            scope=ServiceScope.SINGLETON,
        )


class EstimationPlatformModule(BaseModule):
    name = "estimation"
    version = "1.0"
    dependencies = ("evidence",)
    capabilities = (
        "estimation.expertise",
        "estimation.ownership",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.estimator.policies.exponential_decay_policy import ExponentialDecayPolicy
        from app.estimator.policies.rule_expertise_scoring_policy import RuleExpertiseScoringPolicy
        from app.estimator.semantic_pipeline import SemanticEvidenceExpertiseBridge
        from app.estimator.semantic_pipeline import SemanticExpertiseProjectionPipeline

        services.add(
            ExponentialDecayPolicy,
            lambda _: ExponentialDecayPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            RuleExpertiseScoringPolicy,
            lambda _: RuleExpertiseScoringPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SemanticEvidenceExpertiseBridge,
            lambda _: SemanticEvidenceExpertiseBridge(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SemanticExpertiseProjectionPipeline,
            lambda provider: SemanticExpertiseProjectionPipeline(
                provider.resolve(SemanticEvidenceExpertiseBridge)
            ),
            scope=ServiceScope.SINGLETON,
        )


class GraphPlatformModule(BaseModule):
    name = "graph"
    version = "1.0"
    dependencies = ("knowledge",)
    capabilities = (
        "graph.organization",
        "graph.knowledge",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.graph.graph_service import GraphService
        from app.graph.builders import KnowledgeGraphBuilder
        from app.graph.organizational_graph import OrganizationalGraph

        services.add(
            KnowledgeGraphBuilder,
            lambda _: KnowledgeGraphBuilder(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OrganizationalGraph,
            lambda _: OrganizationalGraph(
                nodes=[],
                edges=[],
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            GraphService,
            lambda provider: GraphService(
                provider.resolve(OrganizationalGraph)
            ),
            scope=ServiceScope.SINGLETON,
        )


class TemporalPlatformModule(BaseModule):
    name = "temporal"
    version = "1.0"
    dependencies = ("graph",)
    capabilities = (
        "temporal.snapshot",
        "temporal.history",
        "temporal.trend",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from pathlib import Path
        from app.temporal.graph_diff import GraphDiffEngine
        from app.temporal.snapshot_repository import SnapshotRepository
        from app.temporal.temporal_engine import TemporalEngine

        services.add(
            SnapshotRepository,
            lambda _: SnapshotRepository(
                root=Path("outputs/showcase/history/snapshots")
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            GraphDiffEngine,
            lambda _: GraphDiffEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            TemporalEngine,
            lambda provider: TemporalEngine(
                repository=provider.resolve(SnapshotRepository),
                graph_diff=provider.resolve(GraphDiffEngine),
            ),
            scope=ServiceScope.SINGLETON,
        )


class KnowledgePlatformModule(BaseModule):
    name = "knowledge"
    version = "1.0"
    dependencies = ("estimation",)
    capabilities = (
        "knowledge.model",
        "knowledge.contract",
    )


class ForecastPlatformModule(BaseModule):
    name = "forecast"
    version = "1.0"
    dependencies = ("temporal",)
    capabilities = (
        "forecast.engine",
        "forecast.models",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.forecast.baseline_models import (
            ConstantBaselineModel,
            ExponentialSmoothingModel,
            LinearTrendModel,
            MomentumProjectionModel,
            MovingAverageModel,
        )
        from app.forecast.engine import ForecastEngine, ForecastRegistry
        from app.forecast.factory import TimeSeriesFactory

        # Register baseline models
        services.add(LinearTrendModel, lambda _: LinearTrendModel(), scope=ServiceScope.SINGLETON)
        services.add(ExponentialSmoothingModel, lambda _: ExponentialSmoothingModel(), scope=ServiceScope.SINGLETON)
        services.add(MovingAverageModel, lambda _: MovingAverageModel(), scope=ServiceScope.SINGLETON)
        services.add(MomentumProjectionModel, lambda _: MomentumProjectionModel(), scope=ServiceScope.SINGLETON)
        services.add(ConstantBaselineModel, lambda _: ConstantBaselineModel(), scope=ServiceScope.SINGLETON)

        # Register and populate the Registry
        def build_registry(provider):
            registry = ForecastRegistry()
            # Register in priority order
            registry.register(provider.resolve(LinearTrendModel))
            registry.register(provider.resolve(MomentumProjectionModel))
            registry.register(provider.resolve(MovingAverageModel))
            registry.register(provider.resolve(ExponentialSmoothingModel))
            registry.register(provider.resolve(ConstantBaselineModel))
            return registry

        services.add(
            ForecastRegistry,
            build_registry,
            scope=ServiceScope.SINGLETON,
        )

        services.add(
            ForecastEngine,
            lambda provider: ForecastEngine(
                registry=provider.resolve(ForecastRegistry),
                factory=TimeSeriesFactory,
            ),
            scope=ServiceScope.SINGLETON,
        )


class ForecastingPlatformModule(BaseModule):
    name = "forecasting"
    version = "1.0"
    dependencies = ("estimation",)
    capabilities = (
        "forecasting.model",
        "forecasting.pipeline",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.forecasting.forecast_service import ForecastService
        from app.forecasting.validation import ForecastValidationService
        from app.forecasting.linear_forecast_policy import LinearForecastPolicy

        services.add(
            LinearForecastPolicy,
            LinearForecastPolicy,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastService,
            lambda provider: ForecastService(
                provider.resolve(LinearForecastPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastValidationService,
            lambda _: ForecastValidationService(),
            scope=ServiceScope.SINGLETON,
        )


class SimulationPlatformModule(BaseModule):
    name = "simulation"
    version = "1.0"
    dependencies = (
        "forecast",
    )
    capabilities = (
        "simulation.engine",
        "simulation.registry",
        "simulation.comparison",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.simulation.engine import SimulationEngine, ScenarioComparisonEngine
        from app.simulation.registry import SimulationRegistry

        services.add(
            SimulationEngine,
            lambda _: SimulationEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ScenarioComparisonEngine,
            lambda _: ScenarioComparisonEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SimulationRegistry,
            lambda _: SimulationRegistry(),
            scope=ServiceScope.SINGLETON,
        )


class AgentPlatformModule(BaseModule):
    name = "agent"
    version = "1.0"
    dependencies = (
        "graph",
        "simulation",
        "intelligence",
    )
    capabilities = (
        "agent.reasoning",
        "agent.tool",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.agent.intent_classifier import IntentClassifier

        services.add(
            IntentClassifier,
            IntentClassifier,
            scope=ServiceScope.SINGLETON,
        )


class ExecutivePlatformModule(BaseModule):
    name = "executive"
    version = "1.0"
    dependencies = (
        "agent",
        "decision",
        "forecasting",
    )
    capabilities = (
        "executive.recommendation",
        "executive.roadmap",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.executive.executive_recommendation_service import ExecutiveRecommendationService
        from app.executive.roadmap_service import RoadmapService
        from app.platform.hardening import ProductionHardeningService

        services.add(
            ExecutiveRecommendationService,
            ExecutiveRecommendationService,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            RoadmapService,
            RoadmapService,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ProductionHardeningService,
            lambda _: ProductionHardeningService(),
            scope=ServiceScope.SINGLETON,
        )


class DecisionPlatformModule(BaseModule):
    name = "decision"
    version = "1.0"
    dependencies = (
        "agent",
        "forecasting",
        "simulation",
    )
    capabilities = (
        "decision.optimization",
        "decision.portfolio",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.decision.optimization import DecisionOptimizationEngine

        services.add(
            DecisionOptimizationEngine,
            lambda _: DecisionOptimizationEngine(),
            scope=ServiceScope.SINGLETON,
        )


class IntelligencePlatformModule(BaseModule):
    name = "intelligence"
    version = "1.0"
    dependencies = (
        "forecast",
        "forecasting",  # Legacy dependency kept for backwards compatibility
        "simulation",
    )
    capabilities = (
        "intelligence.context",
        "intelligence.ownership",
        "intelligence.organization",
    )

    def __init__(
        self,
        projection=None,
        context=None,
    ):
        self._projection = projection
        self._context = context

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.bootstrap.intelligence_context import IntelligenceContext
        from app.concentration.concentration_service import ConcentrationService
        from app.concentration.policies.expertise_concentration_policy import ExpertiseConcentrationPolicy
        from app.coverage.coverage_service import CoverageService
        from app.coverage.policies.expertise_coverage_policy import ExpertiseCoveragePolicy
        from app.estimator.expertise_projection import ExpertiseProjection
        from app.forecasting.forecast_pipeline_service import ForecastPipelineService
        from app.forecasting.forecast_service import ForecastService
        from app.forecasting.forecast_severity_service import ForecastSeverityService
        from app.forecasting.future_risk_pipeline_service import FutureRiskPipelineService
        from app.forecasting.linear_forecast_policy import LinearForecastPolicy
        from app.health.health_service import HealthService
        from app.health.policies.organizational_health_policy import OrganizationalHealthPolicy
        from app.history.health_projection import HealthProjection
        from app.history.history_service import HistoryService
        from app.knowledge_transfer.policies.simple_transfer_policy import SimpleTransferPolicy
        from app.knowledge_transfer.transfer_service import TransferService
        from app.organization.organization_dashboard_service import OrganizationDashboardService
        from app.organization.organization_health_service import OrganizationHealthService
        from app.organization.organization_readiness_service import OrganizationReadinessService
        from app.organization.organization_risk_service import OrganizationRiskService
        from app.organization.organization_transfer_service import OrganizationTransferService
        from app.ownership.ownership_service import OwnershipService
        from app.ownership.policies.expertise_ownership_policy import ExpertiseOwnershipPolicy
        from app.query.expertise_query_service import ExpertiseQueryService
        from app.risk.bus_factor_service import BusFactorService
        from app.risk.policies.ownership_bus_factor_policy import OwnershipBusFactorPolicy

        from app.successor.policies.expertise_successor_policy import ExpertiseSuccessorPolicy
        from app.successor.successor_service import SuccessorService

        if self._projection is not None:
            services.add_instance(
                ExpertiseProjection,
                self._projection,
            )
        if self._context is not None:
            services.add_instance(
                IntelligenceContext,
                self._context,
            )
        services.add(
            ExpertiseQueryService,
            lambda provider: ExpertiseQueryService(
                provider.resolve(ExpertiseProjection)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseOwnershipPolicy,
            lambda _: ExpertiseOwnershipPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OwnershipService,
            lambda provider: OwnershipService(
                provider.resolve(ExpertiseQueryService),
                provider.resolve(ExpertiseOwnershipPolicy),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseSuccessorPolicy,
            lambda _: ExpertiseSuccessorPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SuccessorService,
            lambda provider: SuccessorService(
                provider.resolve(OwnershipService),
                provider.resolve(ExpertiseSuccessorPolicy),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseCoveragePolicy,
            lambda _: ExpertiseCoveragePolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CoverageService,
            lambda provider: CoverageService(
                provider.resolve(ExpertiseCoveragePolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExpertiseConcentrationPolicy,
            lambda _: ExpertiseConcentrationPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ConcentrationService,
            lambda provider: ConcentrationService(
                provider.resolve(ExpertiseConcentrationPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OwnershipBusFactorPolicy,
            lambda _: OwnershipBusFactorPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            BusFactorService,
            lambda provider: BusFactorService(
                provider.resolve(OwnershipService),
                provider.resolve(OwnershipBusFactorPolicy),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            OrganizationalHealthPolicy,
            lambda _: OrganizationalHealthPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            HealthService,
            lambda provider: HealthService(
                provider.resolve(OrganizationalHealthPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            HealthProjection,
            HealthProjection,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            HistoryService,
            lambda provider: HistoryService(
                provider.resolve(HealthProjection)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            LinearForecastPolicy,
            lambda _: LinearForecastPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastService,
            lambda provider: ForecastService(
                provider.resolve(LinearForecastPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ForecastPipelineService,
            lambda provider: ForecastPipelineService(
                provider.resolve(HistoryService),
                provider.resolve(ForecastService),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            FutureRiskPipelineService,
            lambda provider: FutureRiskPipelineService(
                provider.resolve(ForecastPipelineService)
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            SimpleTransferPolicy,
            lambda _: SimpleTransferPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            TransferService,
            lambda provider: TransferService(
                provider.resolve(SimpleTransferPolicy)
            ),
            scope=ServiceScope.SINGLETON,
        )

        services.add(
            ForecastSeverityService,
            lambda _: ForecastSeverityService(),
            scope=ServiceScope.SINGLETON,
        )
        if self._context is not None:
            services.add(
                OrganizationRiskService,
                lambda provider: OrganizationRiskService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationHealthService,
                lambda provider: OrganizationHealthService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationReadinessService,
                lambda provider: OrganizationReadinessService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationTransferService,
                lambda provider: OrganizationTransferService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )
            services.add(
                OrganizationDashboardService,
                lambda provider: OrganizationDashboardService(
                    provider.resolve(IntelligenceContext)
                ),
                scope=ServiceScope.SINGLETON,
            )


def default_platform_modules(
) -> tuple[BaseModule, ...]:
    return (
        ObservationPlatformModule(),
        MeasurementPlatformModule(),
        EvidencePlatformModule(),
        EstimationPlatformModule(),
        KnowledgePlatformModule(),
        GraphPlatformModule(),
        TemporalPlatformModule(),
        ForecastPlatformModule(),
        IntelligencePlatformModule(),
        ForecastingPlatformModule(),
        SimulationPlatformModule(),
        AgentPlatformModule(),
        DecisionPlatformModule(),
        ExecutivePlatformModule(),
    )

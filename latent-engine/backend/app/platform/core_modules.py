from __future__ import annotations

from app.platform.di import ServiceCollection
from app.platform.di import ServiceScope
from app.platform.module import BaseModule


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
    dependencies = ("estimation",)
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
        "estimation",
        "forecasting",
    )
    capabilities = (
        "simulation.engine",
        "simulation.scenario",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.simulation.simulation_engine import SimulationEngine

        services.add(
            SimulationEngine,
            SimulationEngine,
            scope=ServiceScope.SINGLETON,
        )


class AgentPlatformModule(BaseModule):
    name = "agent"
    version = "1.0"
    dependencies = (
        "graph",
        "simulation",
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


class IntelligencePlatformModule(BaseModule):
    name = "intelligence"
    version = "1.0"
    dependencies = (
        "estimation",
        "forecasting",
    )
    capabilities = (
        "intelligence.context",
        "intelligence.ownership",
        "intelligence.organization",
    )

    def __init__(
        self,
        projection,
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
        from app.simulation.policies.expertise_readiness_policy import ExpertiseReadinessPolicy
        from app.simulation.readiness_service import ReadinessService
        from app.successor.policies.expertise_successor_policy import ExpertiseSuccessorPolicy
        from app.successor.successor_service import SuccessorService

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
            ExpertiseReadinessPolicy,
            lambda _: ExpertiseReadinessPolicy(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ReadinessService,
            lambda provider: ReadinessService(
                provider.resolve(SuccessorService),
                provider.resolve(ExpertiseQueryService),
                provider.resolve(ExpertiseReadinessPolicy),
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
        GraphPlatformModule(),
        ForecastingPlatformModule(),
        SimulationPlatformModule(),
        AgentPlatformModule(),
        ExecutivePlatformModule(),
    )

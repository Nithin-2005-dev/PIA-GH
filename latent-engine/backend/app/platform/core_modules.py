from __future__ import annotations

from app.platform.di import ServiceCollection
from app.platform.di import ServiceScope
from app.platform.module import BaseModule


class MeasurementPlatformModule(BaseModule):
    name = "measurement"
    version = "1.0"
    dependencies = ()
    capabilities = (
        "measurement.provider",
        "measurement.engine",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.measurement.core.engine import MeasurementEngine

        services.add(
            MeasurementEngine,
            lambda _: MeasurementEngine.default(),
            scope=ServiceScope.SINGLETON,
        )


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

        services.add(
            EvidenceSynthesisEngine,
            EvidenceSynthesisEngine,
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

        services.add(
            ExponentialDecayPolicy,
            ExponentialDecayPolicy,
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            RuleExpertiseScoringPolicy,
            RuleExpertiseScoringPolicy,
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

        services.add(
            GraphService,
            GraphService,
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


def default_platform_modules(
) -> tuple[BaseModule, ...]:
    return (
        MeasurementPlatformModule(),
        EvidencePlatformModule(),
        EstimationPlatformModule(),
        GraphPlatformModule(),
        ForecastingPlatformModule(),
        SimulationPlatformModule(),
        AgentPlatformModule(),
        ExecutivePlatformModule(),
    )


import sys

with open("app/platform/core_modules.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add CausalPlatformModule right before ExecutivePlatformModule
causal_code = """
class CausalPlatformModule(BaseModule):
    name = "causal"
    version = "1.0"
    dependencies = (
        "intelligence",
    )
    capabilities = (
        "causal.engine",
        "causal.explanation",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.causal.ontology import CausalOntology
        from app.causal.semantic_model import CausalSemanticModelBuilder
        from app.causal.rule_registry import CausalRuleRegistry, default_rule_registry
        from app.causal.rule_engine import CausalRuleEngine
        from app.causal.hypothesis_engine import CausalHypothesisEngine
        from app.causal.explanation_engine import ExplanationEngine
        from app.causal.causal_engine import CausalEngine

        services.add(
            CausalOntology,
            lambda _: CausalOntology(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalRuleRegistry,
            lambda _: default_rule_registry(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalRuleEngine,
            lambda provider: CausalRuleEngine(provider.resolve(CausalRuleRegistry)),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalSemanticModelBuilder,
            lambda provider: CausalSemanticModelBuilder(
                rule_engine=provider.resolve(CausalRuleEngine),
                ontology=provider.resolve(CausalOntology),
            ),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalHypothesisEngine,
            lambda provider: CausalHypothesisEngine(provider.resolve(CausalOntology)),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            ExplanationEngine,
            lambda _: ExplanationEngine(),
            scope=ServiceScope.SINGLETON,
        )
        services.add(
            CausalEngine,
            lambda provider: CausalEngine(
                ontology=provider.resolve(CausalOntology),
                rule_registry=provider.resolve(CausalRuleRegistry),
            ),
            scope=ServiceScope.SINGLETON,
        )


"""

content = content.replace("class ExecutivePlatformModule(BaseModule):", causal_code + "class ExecutivePlatformModule(BaseModule):")

# 2. Merge ForecastPlatformModule into ForecastingPlatformModule
# Since we just want to combine them, we can find ForecastPlatformModule and replace it with nothing,
# then replace ForecastingPlatformModule with the combined one.

# Remove ForecastPlatformModule entirely
import re
content = re.sub(r'class ForecastPlatformModule\(BaseModule\):.*?class ForecastingPlatformModule\(BaseModule\):', 'class ForecastingPlatformModule(BaseModule):', content, flags=re.DOTALL)

# Now update ForecastingPlatformModule
forecasting_code = """class ForecastingPlatformModule(BaseModule):
    name = "forecasting"
    version = "1.0"
    dependencies = ("temporal", "estimation",)
    capabilities = (
        "forecasting.model",
        "forecasting.pipeline",
        "forecast.engine",
        "forecast.models",
    )

    def configure_services(
        self,
        services: ServiceCollection,
    ) -> None:
        from app.forecasting.forecast_service import ForecastService
        from app.forecasting.validation import ForecastValidationService
        from app.forecasting.linear_forecast_policy import LinearForecastPolicy

        from app.forecast.baseline_models import (
            ConstantBaselineModel,
            ExponentialSmoothingModel,
            LinearTrendModel,
            MomentumProjectionModel,
            MovingAverageModel,
        )
        from app.forecast.engine import ForecastEngine, ForecastRegistry
        from app.forecast.factory import TimeSeriesFactory

        # Register forecasting services
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
        )"""

content = re.sub(r'class ForecastingPlatformModule\(BaseModule\):.*?class SimulationPlatformModule\(BaseModule\):', forecasting_code + '\n\n\nclass SimulationPlatformModule(BaseModule):', content, flags=re.DOTALL)

# 3. Fix dependencies in SimulationPlatformModule
content = content.replace('dependencies = (\n        "forecast",\n    )', 'dependencies = (\n        "forecasting",\n    )')
content = content.replace('dependencies = ("forecast",)', 'dependencies = ("forecasting",)')

# 4. Fix default_platform_modules order
default_modules = """def default_platform_modules() -> tuple[BaseModule, ...]:
    return (
        ObservationPlatformModule(),
        MeasurementPlatformModule(),
        EvidencePlatformModule(),
        EstimationPlatformModule(),
        KnowledgePlatformModule(),
        GraphPlatformModule(),
        TemporalPlatformModule(),
        ForecastingPlatformModule(),
        SimulationPlatformModule(),
        IntelligencePlatformModule(),
        CausalPlatformModule(),
        AgentPlatformModule(),
        DecisionPlatformModule(),
        ExecutivePlatformModule(),
    )"""

content = re.sub(r'def default_platform_modules\(.*?\) -> tuple\[BaseModule, \.\.\.\]:.*?    \)', default_modules, content, flags=re.DOTALL)

with open("app/platform/core_modules.py", "w", encoding="utf-8") as f:
    f.write(content)

from app.estimator.expertise_projection import (
    ExpertiseProjection,
)

from app.query.expertise_query_service import (
    ExpertiseQueryService,
)

from app.ownership.ownership_service import (
    OwnershipService,
)

from app.ownership.policies.expertise_ownership_policy import (
    ExpertiseOwnershipPolicy,
)

from app.successor.successor_service import (
    SuccessorService,
)

from app.successor.policies.expertise_successor_policy import (
    ExpertiseSuccessorPolicy,
)

from app.coverage.coverage_service import (
    CoverageService,
)

from app.coverage.policies.expertise_coverage_policy import (
    ExpertiseCoveragePolicy,
)

from app.concentration.concentration_service import (
    ConcentrationService,
)

from app.concentration.policies.expertise_concentration_policy import (
    ExpertiseConcentrationPolicy,
)

from app.risk.bus_factor_service import (
    BusFactorService,
)

from app.risk.policies.ownership_bus_factor_policy import (
    OwnershipBusFactorPolicy,
)

from app.health.health_service import (
    HealthService,
)

from app.health.policies.organizational_health_policy import (
    OrganizationalHealthPolicy,
)

from app.history.health_projection import (
    HealthProjection,
)

from app.history.history_service import (
    HistoryService,
)

from app.forecasting.forecast_service import (
    ForecastService,
)

from app.forecasting.linear_forecast_policy import (
    LinearForecastPolicy,
)

from app.forecasting.forecast_pipeline_service import (
    ForecastPipelineService,
)

from app.forecasting.future_risk_pipeline_service import (
    FutureRiskPipelineService,
)

from app.knowledge_transfer.transfer_service import (
    TransferService,
)

from app.knowledge_transfer.policies.simple_transfer_policy import (
    SimpleTransferPolicy,
)



from app.forecasting.forecast_severity_service import (
    ForecastSeverityService,
)

from app.organization.organization_risk_service import (
    OrganizationRiskService,
)

from app.organization.organization_health_service import (
    OrganizationHealthService,
)

from app.organization.organization_readiness_service import (
    OrganizationReadinessService,
)

from app.organization.organization_transfer_service import (
    OrganizationTransferService,
)

from app.organization.organization_dashboard_service import (
    OrganizationDashboardService,
)
from app.platform.core_modules import (
    IntelligencePlatformModule,
    default_platform_modules,
)
from app.platform.runtime import (
    PlatformRuntime,
)


class IntelligenceContext:

    def __init__(
        self,
        projection: ExpertiseProjection,
    ):

        self.projection = projection
        self.runtime = PlatformRuntime.create()
        for module in default_platform_modules():
            if module.name == "intelligence":
                continue
            self.runtime.register_module(module)
        self.runtime.register_module(
            IntelligencePlatformModule(
                projection=projection,
                context=self,
            )
        )
        self.platform = self.runtime.build()
        self.platform.initialize()
        provider = self.platform.provider

        self.query_service = provider.resolve(ExpertiseQueryService)
        self.ownership_service = provider.resolve(OwnershipService)
        self.successor_service = provider.resolve(SuccessorService)
        self.coverage_service = provider.resolve(CoverageService)
        self.concentration_service = provider.resolve(ConcentrationService)
        self.bus_factor_service = provider.resolve(BusFactorService)
        self.health_service = provider.resolve(HealthService)
        self.health_projection = provider.resolve(HealthProjection)
        self.history_service = provider.resolve(HistoryService)
        self.forecast_service = provider.resolve(ForecastService)
        self.forecast_pipeline_service = provider.resolve(ForecastPipelineService)
        self.future_risk_pipeline_service = provider.resolve(FutureRiskPipelineService)
        self.transfer_service = provider.resolve(TransferService)
        self.forecast_severity_service = provider.resolve(ForecastSeverityService)
        self.organization_risk_service = provider.resolve(OrganizationRiskService)
        self.organization_health_service = provider.resolve(OrganizationHealthService)
        self.organization_readiness_service = provider.resolve(OrganizationReadinessService)
        self.organization_transfer_service = provider.resolve(OrganizationTransferService)
        self.organization_dashboard_service = provider.resolve(OrganizationDashboardService)

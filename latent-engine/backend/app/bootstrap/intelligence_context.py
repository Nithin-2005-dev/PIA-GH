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

from app.simulation.readiness_service import (
    ReadinessService,
)

from app.simulation.policies.expertise_readiness_policy import (
    ExpertiseReadinessPolicy,
)

from app.forecasting.forecast_severity_service import (
    ForecastSeverityService,
)

class IntelligenceContext:

    def __init__(
        self,
        projection: ExpertiseProjection,
    ):

        self.projection = projection

        self.query_service = (
            ExpertiseQueryService(
                projection
            )
        )

        self.ownership_service = (
            OwnershipService(
                self.query_service,
                ExpertiseOwnershipPolicy(),
            )
        )

        self.successor_service = (
            SuccessorService(
                self.ownership_service,
                ExpertiseSuccessorPolicy(),
            )
        )

        self.coverage_service = (
            CoverageService(
                ExpertiseCoveragePolicy()
            )
        )

        self.concentration_service = (
            ConcentrationService(
                ExpertiseConcentrationPolicy()
            )
        )

        self.bus_factor_service = (
            BusFactorService(
                self.ownership_service,
                OwnershipBusFactorPolicy(),
            )
        )

        self.health_service = (
            HealthService(
                OrganizationalHealthPolicy()
            )
        )

        self.health_projection = (
            HealthProjection()
        )

        self.history_service = (
            HistoryService(
                self.health_projection
            )
        )

        self.forecast_service = (
            ForecastService(
                LinearForecastPolicy()
            )
        )

        self.forecast_pipeline_service = (
            ForecastPipelineService(
                self.history_service,
                self.forecast_service,
            )
        )

        self.future_risk_pipeline_service = (
            FutureRiskPipelineService(
                self.forecast_pipeline_service
            )
        )

        self.transfer_service = (
            TransferService(
                SimpleTransferPolicy()
            )
        )
        
        self.readiness_service = (
            ReadinessService(
                self.successor_service,
                self.query_service,
                ExpertiseReadinessPolicy(),
            )
        )
        
        self.forecast_severity_service = (
            ForecastSeverityService()
        )

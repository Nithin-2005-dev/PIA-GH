from app.domain.entity_ref import (
    EntityRef,
)

from app.domain.entity_type import (
    EntityType,
)

from app.forecasting.forecast import (
    Forecast,
)

from app.forecasting.future_risk_service import (
    FutureRiskService,
)


class ForecastAdapter:

    def __init__(
        self,
        intelligence_context=None,
    ):
        self._intelligence = (
            intelligence_context
        )

    def execute(
        self,
        context,
    ):

        #
        # Grounded path
        #
        if (
            self._intelligence
            is not None
        ):

            risks = (
                self._intelligence
                .future_risk_pipeline_service
                .ranking(
                    horizon=3,
                    limit=1,
                )
            )

            if not risks:

                return (
                    "No forecast data available."
                )

            risk = risks[0]

            return (
                f"Current Health: "
                f"{risk.current_health:.2f}\n"
                f"Predicted Health: "
                f"{risk.predicted_health:.2f}\n"
                f"Risk Score: "
                f"{risk.risk_score:.2f}"
            )

        #
        # Fixture fallback
        #
        module_ref = EntityRef(
            id="payments.py",
            type=EntityType.FILE,
        )

        forecast = Forecast(
            module_ref=module_ref,
            current_health=40,
            predicted_health=10,
            horizon=3,
            slope=-10,
            risk_level="CRITICAL",
        )

        risk = (
            FutureRiskService()
            .analyze(
                [forecast]
            )[0]
        )

        return (
            f"Current Health: "
            f"{risk.current_health:.2f}\n"
            f"Predicted Health: "
            f"{risk.predicted_health:.2f}\n"
            f"Risk Score: "
            f"{risk.risk_score:.2f}"
        )
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

    def execute(
        self,
        context,
    ):

        module_id = (
            context.module_id
            or
            "payments.py"
        )

        module = EntityRef(
            id=module_id,
            type=EntityType.FILE,
        )

        forecast = Forecast(
            module_ref=module,
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
            f"{forecast.current_health:.2f}\n"
            f"Predicted Health: "
            f"{forecast.predicted_health:.2f}\n"
            f"Risk Score: "
            f"{risk.risk_score:.2f}"
        )

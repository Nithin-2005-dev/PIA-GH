from app.history.health_trend import (
    HealthTrend,
)

from .forecast import (
    Forecast,
)

from .forecast_policy import (
    ForecastPolicy,
)


class LinearForecastPolicy(
    ForecastPolicy
):

    def forecast(
        self,
        trend: HealthTrend,
        horizon: int,
    ):

        predicted_health = (
            trend.current_score
            +
            (
                trend.slope
                * horizon
            )
        )

        predicted_health = max(
            0,
            min(
                100,
                predicted_health,
            ),
        )

        if predicted_health >= 75:

            risk = "SAFE"

        elif predicted_health >= 50:

            risk = "WARNING"

        else:

            risk = "CRITICAL"

        return Forecast(
            module_ref=(
                trend.module_ref
            ),
            current_health=(
                trend.current_score
            ),
            predicted_health=(
                predicted_health
            ),
            horizon=horizon,
            slope=trend.slope,
            risk_level=risk,
        )
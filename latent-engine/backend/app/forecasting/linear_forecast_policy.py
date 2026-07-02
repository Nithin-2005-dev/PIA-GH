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

        # Dynamically calculate confidence based on sample size and variance
        # Max confidence if sample_size > 30 and variance is low.
        base_confidence = min(1.0, trend.sample_size / 30.0)
        
        # Penalize confidence if variance is high (e.g. noisy data)
        # Assuming variance of health score is typically 0 to 1000 (since max diff is 100).
        variance_penalty = min(0.5, trend.variance / 1000.0)
        
        confidence = max(0.1, base_confidence - variance_penalty)

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
            confidence=confidence,
        )
from __future__ import annotations

from dataclasses import dataclass

from app.forecasting.forecast import Forecast
from app.history.health_history import HealthHistory
from app.history.health_snapshot import HealthSnapshot
from app.history.trend_analyzer import TrendAnalyzer


@dataclass(frozen=True)
class ForecastValidationResult:
    module_id: str
    predicted_health: float
    actual_health: float
    absolute_error: float
    squared_error: float
    within_tolerance: bool


@dataclass(frozen=True)
class ForecastBacktestReport:
    module_id: str
    sample_count: int
    mean_absolute_error: float
    root_mean_squared_error: float
    within_tolerance_rate: float
    results: tuple[ForecastValidationResult, ...]


class ForecastValidationService:
    def __init__(
        self,
        tolerance: float = 5.0,
    ):
        self._tolerance = tolerance
        self._trend_analyzer = TrendAnalyzer()

    def validate(
        self,
        forecast: Forecast,
        actual: HealthSnapshot,
        tolerance: float | None = None,
    ) -> ForecastValidationResult:
        threshold = (
            self._tolerance
            if tolerance is None
            else tolerance
        )
        absolute_error = abs(
            forecast.predicted_health
            - actual.health_score
        )
        return ForecastValidationResult(
            module_id=forecast.module_ref.id,
            predicted_health=forecast.predicted_health,
            actual_health=actual.health_score,
            absolute_error=absolute_error,
            squared_error=absolute_error * absolute_error,
            within_tolerance=absolute_error <= threshold,
        )

    def backtest(
        self,
        history: HealthHistory,
        policy,
        horizon: int = 1,
        tolerance: float | None = None,
    ) -> ForecastBacktestReport:
        snapshots = sorted(
            history.snapshots,
            key=lambda snapshot: snapshot.recorded_at,
        )
        results: list[ForecastValidationResult] = []
        for index in range(2, len(snapshots) - horizon + 1):
            training = HealthHistory(
                module_ref=history.module_ref,
                snapshots=list(snapshots[:index]),
            )
            trend = self._trend_analyzer.analyze(training)
            forecast = policy.forecast(
                trend,
                horizon,
            )
            actual = snapshots[index + horizon - 1]
            results.append(
                self.validate(
                    forecast,
                    actual,
                    tolerance,
                )
            )

        if not results:
            return ForecastBacktestReport(
                module_id=history.module_ref.id,
                sample_count=0,
                mean_absolute_error=0.0,
                root_mean_squared_error=0.0,
                within_tolerance_rate=0.0,
                results=(),
            )

        mean_absolute_error = sum(
            result.absolute_error
            for result in results
        ) / len(results)
        root_mean_squared_error = (
            sum(
                result.squared_error
                for result in results
            ) / len(results)
        ) ** 0.5
        within_tolerance_rate = sum(
            1
            for result in results
            if result.within_tolerance
        ) / len(results)
        return ForecastBacktestReport(
            module_id=history.module_ref.id,
            sample_count=len(results),
            mean_absolute_error=mean_absolute_error,
            root_mean_squared_error=root_mean_squared_error,
            within_tolerance_rate=within_tolerance_rate,
            results=tuple(results),
        )


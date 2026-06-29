from dataclasses import dataclass

from app.measurement.analytics.outliers import OutlierDetectionEngine
from app.measurement.analytics.statistical import StatisticalEngine


@dataclass(frozen=True)
class StatisticalReport:
    mean: float
    median: float
    variance: float
    outlier_indices: tuple[int, ...]
    confidence_interval: tuple[float, float]
    distribution: str


class StatisticsPipeline:

    def __init__(
        self,
    ):
        self._stats = StatisticalEngine()
        self._outliers = OutlierDetectionEngine()

    def analyze(
        self,
        values: list[float],
    ) -> StatisticalReport:
        average = self._stats.mean(
            values
        )
        variance = self._stats.variance(
            values
        )
        deviation = variance ** 0.5

        count = len(
            values
        )

        if count > 0:
            margin = 1.96 * deviation / (
                count ** 0.5
            )
        else:
            margin = 0.0

        return StatisticalReport(
            mean=average,
            median=self._stats.median(
                values
            ),
            variance=variance,
            outlier_indices=tuple(
                self._outliers.mad_outliers(
                    values
                )
            ),
            confidence_interval=(
                average - margin,
                average + margin,
            ),
            distribution=self._distribution(
                values,
            ),
        )

    def _distribution(
        self,
        values: list[float],
    ) -> str:
        if len(
            values
        ) < 3:
            return "unknown"

        average = self._stats.mean(
            values
        )
        median = self._stats.median(
            values
        )

        if abs(
            average - median
        ) <= max(
            1.0,
            abs(average),
        ) * 0.05:
            return "approximately_symmetric"

        if average > median:
            return "right_skewed"

        return "left_skewed"



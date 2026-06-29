from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkResult:
    value: float
    percentile: float
    label: str
    cohort: str


class BenchmarkEngine:

    def compare(
        self,
        value: float,
        cohort_values: list[float],
        cohort: str,
    ) -> BenchmarkResult:
        if not cohort_values:
            return BenchmarkResult(
                value=value,
                percentile=0.0,
                label="unknown",
                cohort=cohort,
            )

        below_or_equal = sum(
            1
            for cohort_value in cohort_values
            if cohort_value <= value
        )

        percentile = below_or_equal / len(
            cohort_values
        )

        label = "typical"

        if percentile >= 0.9:
            label = "high"
        elif percentile <= 0.1:
            label = "low"

        return BenchmarkResult(
            value=value,
            percentile=percentile,
            label=label,
            cohort=cohort,
        )

from dataclasses import dataclass


@dataclass(frozen=True)
class TrendEstimate:
    slope: float
    intercept: float
    direction: str


class TimeSeriesMeasurementEngine:

    def moving_average(
        self,
        values: list[float],
        window: int,
    ) -> list[float]:
        if window <= 0:
            raise ValueError(
                "window must be positive"
            )

        result = []

        for index in range(
            len(values)
        ):
            start = max(
                0,
                index - window + 1,
            )
            segment = values[
                start : index + 1
            ]
            result.append(
                sum(segment)
                / len(segment)
            )

        return result

    def ewma(
        self,
        values: list[float],
        alpha: float,
    ) -> list[float]:
        if not 0 < alpha <= 1:
            raise ValueError(
                "alpha must be in (0, 1]"
            )

        if not values:
            return []

        result = [
            values[0]
        ]

        for value in values[1:]:
            result.append(
                alpha * value
                + (1.0 - alpha)
                * result[-1]
            )

        return result

    def trend(
        self,
        values: list[float],
    ) -> TrendEstimate:
        count = len(
            values
        )

        if count < 2:
            return TrendEstimate(
                slope=0.0,
                intercept=values[0] if values else 0.0,
                direction="flat",
            )

        xs = list(
            range(count)
        )
        x_mean = sum(xs) / count
        y_mean = sum(values) / count

        denominator = sum(
            (
                x - x_mean
            )
            ** 2
            for x in xs
        )

        if denominator == 0:
            slope = 0.0
        else:
            slope = sum(
                (
                    xs[index]
                    - x_mean
                )
                * (
                    values[index]
                    - y_mean
                )
                for index in range(count)
            ) / denominator

        intercept = y_mean - slope * x_mean

        direction = "flat"

        if slope > 0:
            direction = "up"
        elif slope < 0:
            direction = "down"

        return TrendEstimate(
            slope=slope,
            intercept=intercept,
            direction=direction,
        )



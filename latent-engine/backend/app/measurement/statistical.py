from math import log2
from statistics import mean
from statistics import median


class StatisticalEngine:

    def mean(
        self,
        values: list[float],
    ) -> float:
        return mean(
            values
        ) if values else 0.0

    def median(
        self,
        values: list[float],
    ) -> float:
        return median(
            values
        ) if values else 0.0

    def variance(
        self,
        values: list[float],
    ) -> float:
        if len(
            values
        ) < 2:
            return 0.0

        average = mean(
            values
        )

        return sum(
            (
                value - average
            )
            ** 2
            for value in values
        ) / (
            len(
                values
            )
            - 1
        )

    def covariance(
        self,
        left: list[float],
        right: list[float],
    ) -> float:
        count = min(
            len(left),
            len(right),
        )

        if count < 2:
            return 0.0

        left_values = left[:count]
        right_values = right[:count]
        left_mean = mean(
            left_values
        )
        right_mean = mean(
            right_values
        )

        return sum(
            (
                left_values[index]
                - left_mean
            )
            * (
                right_values[index]
                - right_mean
            )
            for index in range(count)
        ) / (count - 1)

    def correlation(
        self,
        left: list[float],
        right: list[float],
    ) -> float:
        covariance = self.covariance(
            left,
            right,
        )

        left_variance = self.variance(
            left
        )

        right_variance = self.variance(
            right
        )

        denominator = (
            left_variance
            * right_variance
        ) ** 0.5

        if denominator == 0:
            return 0.0

        return covariance / denominator

    def percentile(
        self,
        values: list[float],
        percentile: float,
    ) -> float:
        if not values:
            return 0.0

        ordered = sorted(
            values
        )

        index = min(
            len(ordered) - 1,
            max(
                0,
                round(
                    percentile
                    * (len(ordered) - 1)
                ),
            ),
        )

        return ordered[index]

    def entropy(
        self,
        values: list[float],
    ) -> float:
        total = sum(
            value
            for value in values
            if value > 0
        )

        if total <= 0:
            return 0.0

        result = 0.0

        for value in values:
            if value <= 0:
                continue

            probability = value / total
            result -= probability * log2(
                probability
            )

        return result

    def kl_divergence(
        self,
        observed: list[float],
        expected: list[float],
    ) -> float:
        total_observed = sum(
            observed
        )
        total_expected = sum(
            expected
        )

        if (
            total_observed <= 0
            or total_expected <= 0
        ):
            return 0.0

        result = 0.0

        for observed_value, expected_value in zip(
            observed,
            expected,
        ):
            if (
                observed_value <= 0
                or expected_value <= 0
            ):
                continue

            p = observed_value / total_observed
            q = expected_value / total_expected
            result += p * log2(
                p / q
            )

        return result
